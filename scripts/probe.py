#!/usr/bin/env python3
"""Connect to every remote server in the directory and record what answered.

For each http/sse entry with an endpoint this sends an MCP `initialize`, and when the
server allows it without credentials, a `tools/list` (plus `resources/list` and
`prompts/list` where the server declares them). It records whether the server is live,
needs auth, or is down; which step failed and why; how long it took; how many tools it
exposes; roughly how many tokens those tool definitions cost a client; and a hash of
them so changes show up. Tool descriptions and input schemas are saved per server in
data/tools/ so the site can show them. For entries with a GitHub repository it also
records stars, last push and license.

Nothing here verifies that a server is safe. It records what was observed, nothing more.

usage: probe.py [--status data/status.json] [--only-new] [--only slug ...]
Set GITHUB_TOKEN to raise the GitHub API rate limit.
"""

import argparse
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

from lib import REPO_URL, ROOT, endpoint_problem, github_repo, load_servers

PROTOCOL_VERSION = "2025-06-18"
USER_AGENT = f"awesome-mcp-servers-probe/1.0 (+{REPO_URL})"
TIMEOUT = 20
MAX_BYTES = 2_000_000
HISTORY_DAYS = 30
MAX_TOOL_NAMES = 200
MAX_TOOLS_SAVED = 400
MAX_SCHEMA_CHARS = 20_000
TOOLS_DIR = ROOT / "data" / "tools"  # main() points this next to the status file


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def clip(value, limit: int = 120) -> str:
    return str(value)[:limit] if value is not None else ""


def request(url: str, body: dict | None, headers: dict, want_id: int | None = None):
    """One HTTP exchange. Returns (status, response headers, parsed JSON-RPC message or None)."""
    for _ in range(4):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
        try:
            resp = OPENER.open(req, timeout=TIMEOUT)
        except urllib.error.HTTPError as err:
            location = err.headers.get("Location")
            if err.code in (301, 302, 307, 308) and location:
                url = urljoin(url, location)
                if endpoint_problem(url):
                    return err.code, err.headers, None
                continue
            return err.code, err.headers, None
        with resp:
            ctype = resp.headers.get("Content-Type", "")
            if "text/event-stream" in ctype:
                if want_id is None:
                    return resp.status, resp.headers, None
                return resp.status, resp.headers, read_sse(resp, want_id)
            raw = resp.read(MAX_BYTES)
            try:
                message = json.loads(raw)
            except ValueError:
                message = None
            return resp.status, resp.headers, message if isinstance(message, dict) else None
    return 310, {}, None


def read_sse(resp, want_id: int):
    """Read an SSE stream until the JSON-RPC response with our id arrives."""
    read = 0
    deadline = time.monotonic() + TIMEOUT
    while read < MAX_BYTES and time.monotonic() < deadline:
        line = resp.readline()
        if not line:
            return None
        read += len(line)
        if not line.startswith(b"data:"):
            continue
        try:
            message = json.loads(line[5:].strip())
        except ValueError:
            continue
        if isinstance(message, dict) and message.get("id") == want_id:
            return message
    return None


def looks_like_auth(error: dict) -> bool:
    text = json.dumps(error).lower()
    return any(w in text for w in ("unauthor", "authenticat", "api key", "api_key", "token", "forbidden", "login"))


def probe_endpoint(url: str) -> dict:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "User-Agent": USER_AGENT,
    }
    init = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "awesome-mcp-servers-probe", "version": "1.0"},
        },
    }
    started = time.monotonic()
    try:
        status, resp_headers, message = request(url, init, headers, want_id=1)
    except Exception as err:  # DNS failure, TLS error, timeout, reset
        return {"status": "down", "reason": clip(type(err).__name__ + ": " + str(getattr(err, "reason", err)))}
    result = {"latency_ms": round((time.monotonic() - started) * 1000), "http": status}

    if status in (401, 403):
        challenge = resp_headers.get("WWW-Authenticate", "") or ""
        result |= {"status": "auth", "auth": "oauth" if "resource_metadata" in challenge else "credentials"}
        return result

    if message and isinstance(message.get("result"), dict):
        info = message["result"].get("serverInfo") or {}
        caps = message["result"].get("capabilities")
        caps = caps if isinstance(caps, dict) else {}
        result |= {
            "status": "live",
            "init": "ok",
            "transport_seen": "streamable-http",
            "server_name": clip(info.get("name")),
            "server_version": clip(info.get("version"), 40),
            "protocol": clip(message["result"].get("protocolVersion"), 20),
            "capabilities": sorted(clip(k, 30) for k in caps)[:12],
        }
        session = resp_headers.get("Mcp-Session-Id")
        try:
            result |= discover(url, headers, session, result["protocol"], caps)
        except Exception as err:
            result |= {"discovery": "failed", "discovery_reason": clip(type(err).__name__ + ": " + str(getattr(err, "reason", err)))}
        return result

    if message and isinstance(message.get("error"), dict) and looks_like_auth(message["error"]):
        return result | {"status": "auth", "auth": "credentials"}

    # Not Streamable HTTP. Older servers speak SSE: a GET that opens an event stream.
    try:
        sse_status, sse_headers, _ = request(url, None, {"Accept": "text/event-stream", "User-Agent": USER_AGENT})
        if sse_status in (401, 403):
            return result | {"status": "auth", "auth": "credentials", "http": sse_status}
        if sse_status == 200 and "text/event-stream" in (sse_headers.get("Content-Type", "") or ""):
            # The stream opened, which shows a legacy SSE server is there; no handshake is attempted over it.
            return result | {"status": "live", "protocol": "sse", "transport_seen": "sse", "http": 200}
    except Exception:
        pass
    return result | {"status": "down", "reason": f"HTTP {status}, no MCP response"}


def call(url: str, headers: dict, rid: int, method: str, params: dict | None = None):
    """One JSON-RPC call. Returns (outcome, result or reason): outcome is ok, auth or failed."""
    status, _, message = request(url, {"jsonrpc": "2.0", "id": rid, "method": method, "params": params or {}}, headers, want_id=rid)
    if message and isinstance(message.get("result"), dict):
        return "ok", message["result"]
    if status in (401, 403):
        return "auth", f"HTTP {status}"
    error = message.get("error") if message else None
    if isinstance(error, dict):
        return ("auth" if looks_like_auth(error) else "failed"), clip(error.get("message") or "JSON-RPC error")
    return "failed", f"HTTP {status}, no result"


def list_all(url: str, headers: dict, rid: int, method: str, key: str):
    """Follow pagination for a list method. Returns (outcome, items or reason)."""
    items, cursor = [], None
    for page in range(5):
        outcome, result = call(url, headers, rid + page, method, {"cursor": cursor} if cursor else None)
        if outcome != "ok":
            return (outcome, result) if page == 0 else ("ok", items)
        items += [x for x in result.get(key) or [] if isinstance(x, dict)]
        cursor = result.get("nextCursor")
        if not cursor:
            break
    return "ok", items


def tool_detail(tool: dict) -> dict:
    """What the site shows for one tool. Everything here is the server author's text."""
    out = {"name": clip(tool.get("name"), 80)}
    if tool.get("title"):
        out["title"] = clip(tool["title"], 120)
    if isinstance(tool.get("description"), str):
        out["description"] = tool["description"][:4000]
    schema = tool.get("inputSchema")
    if isinstance(schema, dict):
        out["inputSchema"] = schema if len(json.dumps(schema)) <= MAX_SCHEMA_CHARS else {"type": "object", "x-omitted": "schema too large to store"}
    hints = tool.get("annotations")
    if isinstance(hints, dict):
        kept = {k: hints[k] for k in ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint") if isinstance(hints.get(k), bool)}
        if kept:
            out["annotations"] = kept
    return out


def discover(url: str, headers: dict, session: str | None, protocol: str, caps: dict) -> dict:
    headers = headers | {"MCP-Protocol-Version": protocol or PROTOCOL_VERSION}
    if session:
        headers["Mcp-Session-Id"] = session
    request(url, {"jsonrpc": "2.0", "method": "notifications/initialized"}, headers)

    outcome, tools = list_all(url, headers, 2, "tools/list", "tools")
    if outcome != "ok":
        if outcome == "failed" and "tools" not in caps:
            return {"discovery": "none"}  # the server never said it has tools
        return {"discovery": outcome, "discovery_reason": tools}

    canonical = json.dumps(
        sorted(({"name": t.get("name"), "description": t.get("description"), "inputSchema": t.get("inputSchema")} for t in tools), key=lambda t: str(t["name"])),
        sort_keys=True,
        separators=(",", ":"),
    )
    found = {
        "discovery": "ok",
        "tools": len(tools),
        "tool_names": sorted(clip(t.get("name"), 80) for t in tools)[:MAX_TOOL_NAMES],
        "tool_tokens": round(len(canonical) / 4),  # rough: about four characters per token
        "tools_hash": hashlib.sha256(canonical.encode()).hexdigest()[:16],
    }
    detail = {"tools": sorted((tool_detail(t) for t in tools), key=lambda t: t["name"])[:MAX_TOOLS_SAVED]}

    # Resources and prompts are optional parts of MCP; only ask servers that declare them.
    for cap, method, key, label in (("resources", "resources/list", "resources", "name"), ("prompts", "prompts/list", "prompts", "name")):
        if cap not in caps:
            continue
        try:
            outcome, items = list_all(url, headers, 20 if cap == "resources" else 30, method, key)
        except Exception:
            continue
        if outcome == "ok":
            found[cap] = len(items)
            detail[cap] = [
                {k: (v[:500] if k == "description" else clip(v, 200)) for k, v in item.items() if k in ("name", "title", "uri", "description", "mimeType") and isinstance(v, str)}
                for item in items[:100]
            ]
    return found | {"_detail": detail}


def probe_with_retry(url: str) -> dict:
    result = probe_endpoint(url)
    if result["status"] == "down":
        time.sleep(3)
        result = probe_endpoint(url)
    return result


def github_info(repo: str) -> dict | None:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    try:
        with urllib.request.urlopen(urllib.request.Request(f"https://api.github.com/repos/{repo}", headers=headers), timeout=TIMEOUT) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as err:
        return {"missing": True} if err.code == 404 else None
    except Exception:
        return None
    return {
        "stars": data.get("stargazers_count", 0),
        "pushed": clip(data.get("pushed_at"), 10),
        "archived": bool(data.get("archived")),
        "license": clip((data.get("license") or {}).get("spdx_id"), 30),
    }


def check(entry: dict, previous: dict, today: str) -> dict:
    record = {k: previous[k] for k in ("first_seen", "tools_changed", "history", "repo") if k in previous}
    record.setdefault("first_seen", today)

    if repo := github_repo(entry):
        info = github_info(repo)
        if info is not None:
            record["repo"] = info | {"name": repo}

    if entry["transport"] not in ("http", "sse") or "endpoint" not in entry:
        return record | {"status": "unprobed"}

    result = probe_with_retry(entry["endpoint"])
    result.setdefault("init", {"live": "untested", "auth": "auth", "down": "failed"}[result["status"]])
    result.setdefault("discovery", "untested")
    if detail := result.pop("_detail", None):
        TOOLS_DIR.mkdir(parents=True, exist_ok=True)
        (TOOLS_DIR / f"{entry['slug']}.json").write_text(json.dumps({"server": entry["name"], "checked": today} | detail, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    old_hash, new_hash = previous.get("tools_hash"), result.get("tools_hash")
    if old_hash and new_hash and old_hash != new_hash:
        record["tools_changed"] = today
    if not new_hash and old_hash:  # keep the last tool list we saw while it is unreachable
        result |= {k: previous[k] for k in ("tools", "tool_names", "tool_tokens", "tools_hash") if k in previous}

    mark = {"live": "u", "auth": "a", "down": "d"}[result["status"]]
    history = record.get("history", "")
    latencies = list(previous.get("latency_history", []))
    if previous.get("checked", "")[:10] == today and history:
        history, latencies = history[:-1], latencies[:-1]  # one mark per day; a re-run replaces today's
    record["history"] = (history + mark)[-HISTORY_DAYS:]
    record["latency_history"] = (latencies + [None if mark == "d" else result.get("latency_ms")])[-HISTORY_DAYS:]
    return record | result | {"checked": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--status", type=Path, default=ROOT / "data" / "status.json")
    parser.add_argument("--only-new", action="store_true", help="only check servers with no record yet")
    parser.add_argument("--only", nargs="*", default=None, help="only check these slugs")
    args = parser.parse_args()

    global TOOLS_DIR
    TOOLS_DIR = args.status.parent / "tools"

    old = json.loads(args.status.read_text())["servers"] if args.status.exists() else {}
    servers = load_servers()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    todo = [e for e in servers if (not args.only_new or e["slug"] not in old) and (args.only is None or e["slug"] in args.only)]
    with ThreadPoolExecutor(max_workers=12) as pool:
        fresh = dict(zip((e["slug"] for e in todo), pool.map(lambda e: check(e, old.get(e["slug"], {}), today), todo)))

    # Entries removed from the directory drop out; everything else keeps its last record.
    merged = {e["slug"]: fresh.get(e["slug"]) or old.get(e["slug"]) for e in servers}
    merged = {slug: rec for slug, rec in merged.items() if rec}

    args.status.parent.mkdir(parents=True, exist_ok=True)
    args.status.write_text(json.dumps({"generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "servers": merged}, indent=1, sort_keys=True) + "\n")

    counts: dict[str, int] = {}
    for rec in merged.values():
        counts[rec["status"]] = counts.get(rec["status"], 0) + 1
    print(f"checked {len(todo)} of {len(servers)}: " + ", ".join(f"{n} {s}" for s, n in sorted(counts.items())))


if __name__ == "__main__":
    main()

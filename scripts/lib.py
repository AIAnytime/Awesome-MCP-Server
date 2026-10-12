"""Shared helpers: load the server files, validate them, render the README section."""

import ipaddress
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SERVERS_DIR = ROOT / "servers"
README = ROOT / "README.md"

REPO = "AIAnytime/Awesome-MCP-Servers"
REPO_URL = f"https://github.com/{REPO}"

CATEGORIES = {
    "developer-tools": "Agents, IDEs & developer tools",
    "search": "Search & discovery",
    "knowledge-memory": "Knowledge, memory & context",
    "media": "Media & generation",
    "security": "Security",
    "finance": "Finance & markets",
    "marketing": "Marketing, content & social",
    "cloud-data": "Cloud, ops & data",
    "commerce-travel": "Commerce, travel & logistics",
    "productivity": "Work & productivity",
}
TRANSPORTS = ("stdio", "http", "sse", "none")
REQUIRED = ("name", "url", "category", "transport", "description")
OPTIONAL = ("endpoint", "registry")
MAX_DESCRIPTION = 600

START_MARK = "<!-- directory:start (generated from servers/*.json by scripts/build.py; do not edit by hand) -->"
END_MARK = "<!-- directory:end -->"

SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")
GITHUB_REPO = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)")


def load_servers() -> list[dict]:
    servers = []
    for path in sorted(SERVERS_DIR.glob("*.json")):
        entry = json.loads(path.read_text(encoding="utf-8"))
        entry["slug"] = path.stem
        servers.append(entry)
    return sorted(servers, key=lambda e: str(e.get("name", "")).lower())


def github_repo(entry: dict) -> str | None:
    """owner/repo for the entry's source repository, if it has one."""
    for text in (entry.get("url", ""), entry.get("description", "")):
        match = GITHUB_REPO.search(text)
        if match:
            return f"{match[1]}/{match[2].removesuffix('.git')}"
    return None


def endpoint_problem(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        return "endpoint must be an https:// URL"
    host = parsed.hostname.lower()
    try:
        ipaddress.ip_address(host)
        return "endpoint must be a hostname, not an IP address"
    except ValueError:
        pass
    if host == "localhost" or "." not in host or host.endswith((".local", ".internal", ".localhost")):
        return "endpoint must be publicly reachable"
    return None


def validate(servers: list[dict]) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    names: dict[str, str] = {}
    urls: dict[str, str] = {}
    for entry in servers:
        where = f"servers/{entry['slug']}.json"
        if not SLUG.match(entry["slug"]):
            errors.append(f"{where}: file name must be lowercase letters, digits and hyphens")
        missing = [k for k in REQUIRED if not entry.get(k)]
        if missing:
            errors.append(f"{where}: missing {', '.join(missing)}")
            continue
        unknown = set(entry) - set(REQUIRED) - set(OPTIONAL) - {"slug"}
        if unknown:
            errors.append(f"{where}: unknown field(s) {', '.join(sorted(unknown))}")
        if any(not isinstance(v, str) for k, v in entry.items()):
            errors.append(f"{where}: every field must be a string")
            continue
        if entry["category"] not in CATEGORIES:
            errors.append(f"{where}: category must be one of {', '.join(CATEGORIES)}")
        if entry["transport"] not in TRANSPORTS:
            errors.append(f"{where}: transport must be stdio, http or sse")
        if entry["transport"] == "none" and "not a server" not in entry["description"]:
            errors.append(f"{where}: transport 'none' is only for entries that say they are not a server")
        if not entry["url"].startswith("https://"):
            errors.append(f"{where}: url must start with https://")
        if "\n" in entry["description"] or len(entry["description"]) > MAX_DESCRIPTION:
            errors.append(f"{where}: description must be one line of at most {MAX_DESCRIPTION} characters")
        if any("utm_" in v for v in entry.values()):
            errors.append(f"{where}: remove tracking parameters (utm_*)")
        if entry["transport"] in ("http", "sse"):
            if "endpoint" not in entry:
                warnings.append(f"{where}: no endpoint, so this remote server cannot be checked nightly")
            elif problem := endpoint_problem(entry["endpoint"]):
                errors.append(f"{where}: {problem}")
        elif "endpoint" in entry:
            errors.append(f"{where}: endpoint is only for http and sse servers")
        key = entry["name"].lower()
        if key in names:
            errors.append(f"{where}: duplicate name, already in {names[key]}")
        names[key] = where
        if entry["url"] in urls:
            errors.append(f"{where}: duplicate url, already in {urls[entry['url']]}")
        urls[entry["url"]] = where
    return errors, warnings


def readme_line(entry: dict) -> str:
    tag = "" if entry["transport"] == "none" else f" `{entry['transport']}`"
    return f"- **[{entry['name']}]({entry['url']})**{tag} — {entry['description']}"


def render_directory(servers: list[dict]) -> str:
    out = [START_MARK, ""]
    for slug, title in CATEGORIES.items():
        out += [f"### {title}", ""]
        out += [readme_line(e) for e in servers if e["category"] == slug]
        out += [""]
    out += [END_MARK]
    return "\n".join(out)


def splice_readme(text: str, section: str) -> str:
    start, end = text.index(START_MARK), text.index(END_MARK) + len(END_MARK)
    return text[:start] + section + text[end:]

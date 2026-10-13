"""Server-page sections built from the nightly check: health, client setup and the tool explorer.

Everything a server sent us (names, descriptions, schemas, error messages) is escaped before
it reaches a page. None of it is rendered as Markdown or HTML.
"""

import base64
import html
import json
from statistics import median
from urllib.parse import quote

STATE_LABEL = {"verified": "Verified", "failed": "Failed", "untested": "Untested"}
TRANSPORT_NAME = {"streamable-http": "Streamable HTTP", "sse": "SSE (legacy)"}


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def failure_label(reason: str) -> str:
    """A plain-language cause for a failed check."""
    r = (reason or "").lower()
    for needle, label in (
        ("timed out", "Timed out"),
        ("timeout", "Timed out"),
        ("nodename", "Domain does not resolve"),
        ("name or service", "Domain does not resolve"),
        ("getaddrinfo", "Domain does not resolve"),
        ("certificate", "TLS certificate problem"),
        ("ssl", "TLS problem"),
        ("refused", "Connection refused"),
        ("http 404", "Endpoint not found (HTTP 404)"),
        ("http 410", "Endpoint gone (HTTP 410)"),
        ("http 429", "Rate limited (HTTP 429)"),
        ("http 5", "Server error (HTTP 5xx)"),
    ):
        if needle in r:
            return label
    return "No valid MCP response"


def steps(entry: dict) -> tuple[str, str]:
    """(handshake, discovery) outcomes, filled in for records written before these were stored."""
    s = entry["status"]
    kind = s["status"]
    init = s.get("init") or {"live": "untested" if s.get("protocol") == "sse" else "ok", "auth": "auth", "down": "failed"}.get(kind, "untested")
    discovery = s.get("discovery") or ("ok" if kind == "live" and "tools" in s else "untested")
    return init, discovery


def health_checks(entry: dict) -> list[tuple[str, str, str]]:
    """Rows of (check, state, detail). State is verified, failed or untested."""
    s = entry["status"]
    kind = s["status"]
    if kind == "unprobed":
        why = "Runs on your own machine, so there is no endpoint to check." if entry["transport"] == "stdio" else "No endpoint is on file for this server."
        return [("Endpoint reachable", "untested", why)]

    init, discovery = steps(entry)
    how = "an OAuth sign-in" if s.get("auth") == "oauth" else "an API key or token"
    rows = []
    if kind == "down":
        rows.append(("Endpoint reachable", "failed", failure_label(s.get("reason", ""))))
    else:
        rows.append(("Endpoint reachable", "verified", f"Responded in {s['latency_ms']} ms" if "latency_ms" in s else "Responded"))

    if init == "ok":
        rows.append(("MCP handshake (initialize)", "verified", "Completed without credentials"))
    elif init == "auth":
        rows.append(("MCP handshake (initialize)", "untested", f"The server asks for {how} first"))
    elif init == "failed":
        rows.append(("MCP handshake (initialize)", "failed", failure_label(s.get("reason", ""))))
    else:
        rows.append(("MCP handshake (initialize)", "untested", "A legacy SSE stream opened; no handshake is attempted over it"))

    if discovery == "ok":
        rows.append(("Tool discovery (tools/list)", "verified", f"{s.get('tools', 0)} tool{'s' if s.get('tools') != 1 else ''} listed"))
    elif discovery == "auth":
        rows.append(("Tool discovery (tools/list)", "untested", "The handshake is open, but listing tools needs credentials"))
    elif discovery == "failed":
        rows.append(("Tool discovery (tools/list)", "failed", s.get("discovery_reason") or "No tool list returned"))
    elif discovery == "none":
        rows.append(("Tool discovery (tools/list)", "untested", "The server does not declare any tools"))
    else:
        rows.append(("Tool discovery (tools/list)", "untested", "Not attempted"))

    if kind == "live":
        rows.append(("Authentication", "verified", "None needed to connect" if discovery != "auth" else "None for the handshake; credentials needed to list tools"))
    elif kind == "auth":
        rows.append(("Authentication", "verified", f"Requires {how}"))
    else:
        rows.append(("Authentication", "untested", "Unknown while the server is not answering"))

    if s.get("protocol") and s["protocol"] != "sse":
        rows.append(("Protocol version", "verified", s["protocol"]))
    else:
        rows.append(("Protocol version", "untested", "Only known after a completed handshake"))

    if s.get("transport_seen") or s.get("protocol") == "sse":
        rows.append(("Transport", "verified", TRANSPORT_NAME.get(s.get("transport_seen") or "sse", "")))
    else:
        rows.append(("Transport", "untested", f"Listed as {entry['transport']}"))

    if s.get("capabilities"):
        rows.append(("Capabilities declared", "verified", ", ".join(s["capabilities"])))
    return rows


def state_pill(state: str) -> str:
    return f'<span class="state {state}">{STATE_LABEL[state]}</span>'


def uptime(history: str) -> int | None:
    return round(100 * sum(c != "d" for c in history) / len(history)) if len(history) >= 7 else None


def history_strip(history: str) -> str:
    return f'<div class="days">{"".join(f"<i class={c!r}></i>" for c in history)}</div>'


def health_section(entry: dict) -> str:
    s = entry["status"]
    rows = "".join(f"<tr><th scope='row'>{esc(name)}</th><td>{state_pill(state)}</td><td>{esc(detail)}</td></tr>" for name, state, detail in health_checks(entry))
    out = f'<h2 id="health">Health and compatibility</h2><div class="scroll"><table class="checks"><tbody>{rows}</tbody></table></div>'
    if s.get("checked"):
        out += f'<p class="note">Last checked <time datetime="{esc(s["checked"])}">{esc(s["checked"].replace("T", " ").replace("Z", " UTC"))}</time>. Verified means the check saw it happen; it says nothing about whether the server is safe.</p>'
    history = s.get("history", "")
    if history:
        up = uptime(history)
        times = [t for t in s.get("latency_history", []) if isinstance(t, (int, float))]
        bits = [f"{up}% of the last {len(history)} daily checks reachable" if up is not None else f"{len(history)} daily check{'s' if len(history) != 1 else ''} so far"]
        if len(times) >= 3:
            bits.append(f"median response {round(median(times))} ms")
        out += f'<h3>Recent history</h3><p class="note">{esc("; ".join(bits))}. Green answered, violet asked for auth, red did not answer.</p>{history_strip(history)}'
    return out


# ───────────────────────── client setup ─────────────────────────


def code_block(text: str) -> str:
    return f'<div class="cmd"><code>{esc(text)}</code><button class="copy" data-copy="{esc(text)}">Copy</button></div>'


def json_block(obj) -> str:
    text = json.dumps(obj, indent=2)
    return f'<div class="snippet"><button class="copy" data-copy="{esc(text)}">Copy</button><pre><code>{esc(text)}</code></pre></div>'


def setup_section(entry: dict) -> str:
    """Copy-ready configuration for the common MCP clients. Hosted servers only."""
    if "endpoint" not in entry:
        return ""
    s = entry["status"]
    name, url, kind = entry["slug"], entry["endpoint"], entry["transport"]
    needs_key = s["status"] == "auth" and s.get("auth") != "oauth"
    oauth = s.get("auth") == "oauth"
    header = {"Authorization": "Bearer YOUR_TOKEN"}

    claude_code = f"claude mcp add --transport {kind} {name} {url}" + (' --header "Authorization: Bearer YOUR_TOKEN"' if needs_key else "")
    remote_args = ["-y", "mcp-remote", url] + (["--header", "Authorization: Bearer YOUR_TOKEN"] if needs_key else [])
    desktop = {"mcpServers": {name: {"command": "npx", "args": remote_args}}}
    cursor_server = {"url": url} | ({"headers": header} if needs_key else {})
    cursor_link = f"cursor://anysphere.cursor-deeplink/mcp/install?name={quote(name)}&config={quote(base64.b64encode(json.dumps(cursor_server).encode()).decode())}"
    vscode_server = {"type": kind, "url": url} | ({"headers": header} if needs_key else {})
    vscode_link = "vscode:mcp/install?" + quote(json.dumps({"name": name} | vscode_server))
    windsurf_server = {"serverUrl": url} | ({"headers": header} if needs_key else {})

    panels = [
        ("claude-code", "Claude Code", f"<p>Run this in a terminal:</p>{code_block(claude_code)}" + ("<p>Then run <code>/mcp</code> inside Claude Code to sign in.</p>" if oauth else "")),
        (
            "claude-desktop",
            "Claude Desktop",
            f"<p>Open <b>Settings → Connectors → Add custom connector</b> and paste this URL:</p>{code_block(url)}"
            f"<p>Or bridge it through <code>mcp-remote</code> in <code>claude_desktop_config.json</code> (needs Node.js):</p>{json_block(desktop)}",
        ),
        (
            "cursor",
            "Cursor",
            f'<p><a class="btn" href="{esc(cursor_link)}">Add to Cursor</a></p><p>Or add it to <code>~/.cursor/mcp.json</code> (or <code>.cursor/mcp.json</code> in a project):</p>{json_block({"mcpServers": {name: cursor_server}})}',
        ),
        (
            "vscode",
            "VS Code",
            f'<p><a class="btn" href="{esc(vscode_link)}">Add to VS Code</a></p><p>Or add it to <code>.vscode/mcp.json</code>:</p>{json_block({"servers": {name: vscode_server}})}'
            f"<p>Or from a terminal:</p>{code_block('code --add-mcp ' + chr(39) + json.dumps({'name': name} | vscode_server) + chr(39))}",
        ),
        ("windsurf", "Windsurf", f"<p>Add it to <code>~/.codeium/windsurf/mcp_config.json</code>:</p>{json_block({'mcpServers': {name: windsurf_server}})}"),
        ("other", "Other clients", f"<p>Most clients accept this shape. The endpoint is:</p>{code_block(url)}{json_block({'mcpServers': {name: {'type': kind, 'url': url} | ({'headers': header} if needs_key else {})}})}"),
    ]
    tabs = "".join(f'<button type="button" role="tab" data-tab="{pid}"{" class=on" if i == 0 else ""}>{label}</button>' for i, (pid, label, _) in enumerate(panels))
    bodies = "".join(f'<div class="panel" data-panel="{pid}"><h3>{label}</h3>{body}</div>' for pid, label, body in panels)

    tips = []
    if s["status"] == "down":
        tips.append(f"Last night's check could not reach this server ({esc(failure_label(s.get('reason', '')))}), so it may not connect right now.")
    if oauth:
        tips.append("This server uses OAuth. Your client opens a browser window to sign in the first time it connects.")
    if needs_key:
        tips.append("This server asked for credentials. Replace <code>YOUR_TOKEN</code> with your own key. A bearer token is the usual form, but check the server's documentation for the exact header it expects.")
    if kind == "sse" or s.get("transport_seen") == "sse":
        tips.append("This is a legacy SSE server. Some newer clients only accept Streamable HTTP.")
    tips.append("Restart the client after editing a config file, and keep keys out of files you commit.")
    tips.append("If the tools do not appear, open the client's MCP log: a 401 means the credentials were not accepted, and a timeout means the server did not answer.")

    return (
        f'<h2 id="setup">Set up in your client</h2><div class="tabs"><div class="tablist" role="tablist">{tabs}</div>{bodies}</div>'
        f'<h3>If it does not connect</h3><ul class="tips">{"".join(f"<li>{t}</li>" for t in tips)}</ul>'
    )


# ───────────────────────── tool explorer ─────────────────────────


def type_of(schema) -> str:
    if not isinstance(schema, dict):
        return "any"
    t = schema.get("type")
    if isinstance(t, list):
        return " | ".join(str(x) for x in t)
    if t == "array":
        return f"{type_of(schema.get('items'))}[]" if schema.get("items") else "array"
    if t:
        return str(t)
    for key in ("anyOf", "oneOf"):
        if isinstance(schema.get(key), list):
            return " | ".join(dict.fromkeys(type_of(x) for x in schema[key]))
    return "enum" if "enum" in schema else "any"


def placeholder(schema):
    if not isinstance(schema, dict):
        return "..."
    if isinstance(schema.get("enum"), list) and schema["enum"]:
        return schema["enum"][0]
    if "default" in schema:
        return schema["default"]
    t = schema.get("type")
    t = next((x for x in t if x != "null"), "string") if isinstance(t, list) else t
    return {"integer": 0, "number": 0, "boolean": False, "array": [], "object": {}}.get(t, "...")


def clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + " …"


def hint_badges(tool: dict) -> str:
    a = tool.get("annotations") or {}
    out = []
    if a.get("readOnlyHint") is True:
        out.append(("read", "read-only"))
    if a.get("readOnlyHint") is False:
        out.append(("write", "can modify"))
    if a.get("destructiveHint") is True and a.get("readOnlyHint") is not True:
        out.append(("danger", "destructive"))
    if a.get("openWorldHint") is True:
        out.append(("world", "external access"))
    return "".join(f'<span class="hint {cls}">{label}</span>' for cls, label in out)


def tool_card(tool: dict, long_text: int) -> str:
    name = tool.get("name", "")
    description = tool.get("description", "")
    schema = tool.get("inputSchema") if isinstance(tool.get("inputSchema"), dict) else {}
    props = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
    required = [r for r in schema.get("required", []) if isinstance(r, str)] if isinstance(schema.get("required"), list) else []

    rows = ""
    for pname, pschema in list(props.items())[:40]:
        pschema = pschema if isinstance(pschema, dict) else {}
        notes = clip(str(pschema.get("description", "")), 260)
        if isinstance(pschema.get("enum"), list):
            notes += (" " if notes else "") + "One of: " + ", ".join(str(v) for v in pschema["enum"][:8]) + (" …" if len(pschema["enum"]) > 8 else "")
        rows += f"<tr><td><code>{esc(pname)}</code></td><td>{esc(type_of(pschema))}</td><td>{'required' if pname in required else 'optional'}</td><td>{esc(notes)}</td></tr>"
    params = (
        f'<div class="scroll"><table class="params"><thead><tr><th>Parameter</th><th>Type</th><th></th><th>Description</th></tr></thead><tbody>{rows}</tbody></table></div>'
        if rows
        else '<p class="note">Takes no parameters.</p>'
    )
    example = json.dumps({"method": "tools/call", "params": {"name": name, "arguments": {r: placeholder(props.get(r)) for r in required}}}, indent=2, ensure_ascii=False)
    first_line = clip(" ".join(description.split()), 110)
    return (
        f'<details class="tool" data-text="{esc((name + " " + description[:400]).lower())}">'
        f"<summary><code>{esc(name)}</code>{hint_badges(tool)}<span>{esc(first_line)}</span></summary>"
        + (f'<p class="desc">{esc(clip(description, long_text))}</p>' if description else "")
        + params
        + f'<p class="note">Example call (required arguments only, placeholder values):</p><pre><code>{esc(example)}</code></pre></details>'
    )


def tools_section(entry: dict, detail: dict | None) -> str:
    s = entry["status"]
    if not detail or not detail.get("tools"):
        if s.get("tool_names"):
            return f'<h2 id="tools">Tools</h2><ul class="tools">{"".join(f"<li><code>{esc(n)}</code></li>" for n in s["tool_names"])}</ul>'
        return ""
    tools = detail["tools"]
    long_text = 500 if len(tools) > 120 else 1500
    search = '<input id="toolq" type="search" placeholder="Filter tools" aria-label="Filter tools">' if len(tools) > 8 else ""
    hinted = any(t.get("annotations") for t in tools)
    out = (
        f'<h2 id="tools">Tools <span class="count">{len(tools)}</span></h2>'
        f'<p class="note">Names, descriptions and input schemas exactly as the server returned them on {esc(detail.get("checked", ""))}. '
        "This is the server author's own text. Nothing is run from this page."
        + (" Labels such as read-only are declared by the server and are not verified." if hinted else "")
        + f' <a href="../../api/tools/{entry["slug"]}.json">Raw JSON</a></p>{search}'
        f'<div id="toollist">{"".join(tool_card(t, long_text) for t in tools)}</div>'
    )
    for key, title in (("resources", "Resources"), ("prompts", "Prompts")):
        items = detail.get(key) or []
        if items:
            lis = "".join(
                f"<li><code>{esc(i.get('name') or i.get('uri') or '')}</code>{' ' + esc(clip(i.get('description', ''), 200)) if i.get('description') else ''}</li>" for i in items
            )
            out += f'<h3>{title} <span class="count">{len(items)}</span></h3><ul class="plain">{lis}</ul>'
    return out


SECTION_CSS = """
.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:.92rem}
th,td{text-align:left;padding:8px 12px 8px 0;border-bottom:1px solid var(--line);vertical-align:top}
table.checks th{font-weight:500}
table.checks td:last-child{min-width:150px}
table.params{min-width:560px}
thead th{color:var(--mute);font-weight:500;font-size:.8rem;white-space:nowrap}
.state{font-size:.78rem;font-weight:600;white-space:nowrap}
.state::before{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;background:currentColor}
.state.verified{color:var(--live)}.state.failed{color:var(--down)}.state.untested{color:var(--off)}
.state.untested::before{background:none;border:1.5px solid currentColor}
h3{font-size:1.02rem;margin:22px 0 6px}
.count{font:500 .8rem "Geist Mono",ui-monospace,monospace;color:var(--mute);margin-left:4px}
.tablist{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 0}
.tablist button{font:inherit;font-size:.88rem;cursor:pointer;color:var(--mute);background:none;border:1px solid var(--line);border-radius:999px;padding:5px 13px}
.tablist button.on{background:var(--accent);border-color:var(--accent);color:var(--bg);font-weight:600}
.tabs.js .panel{display:none}.tabs.js .panel.on{display:block}.tabs.js .panel h3{display:none}
.tabs:not(.js) .tablist{display:none}
.panel{margin-top:6px}
.snippet{position:relative}.snippet .copy{position:absolute;top:8px;right:8px;height:28px}
.snippet pre{margin:8px 0;padding-right:76px}
.btn{display:inline-block;background:var(--accent);color:var(--bg);font-weight:600;text-decoration:none;border-radius:999px;padding:7px 16px;font-size:.9rem}
.tips{padding-left:18px;color:var(--mute);font-size:.92rem}.tips li{margin:4px 0}
#toolq{font:inherit;width:100%;max-width:360px;color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 10px;margin:4px 0 10px}
.tool{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin-top:6px}
.tool summary{cursor:pointer;display:flex;flex-wrap:wrap;gap:6px 10px;align-items:baseline}
.tool summary span:last-child{color:var(--mute);font-size:.88rem;flex:1 1 260px;min-width:0}
.tool .desc{white-space:pre-wrap;overflow-wrap:anywhere;font-size:.92rem;margin:10px 0}
.tool pre{margin:6px 0 4px}
.hint{font:500 .68rem "Geist Mono",ui-monospace,monospace;border-radius:5px;padding:1px 6px;border:1px solid var(--line);color:var(--mute);white-space:nowrap}
.hint.read{color:var(--live);border-color:currentColor}.hint.danger{color:var(--down);border-color:currentColor}
ul.plain{padding-left:18px;font-size:.92rem;color:var(--mute)}
.status td,.status th{white-space:nowrap}.status .days i{width:5px;height:16px;border-radius:2px}.status .days{gap:2px;margin:0}
"""

SECTION_JS = """
document.querySelectorAll('.tabs').forEach(tabs=>{tabs.classList.add('js');
const show=id=>{tabs.querySelectorAll('[data-tab]').forEach(b=>b.classList.toggle('on',b.dataset.tab===id));
tabs.querySelectorAll('[data-panel]').forEach(p=>p.classList.toggle('on',p.dataset.panel===id));};
let saved=null;try{saved=localStorage.getItem('client')}catch(e){}
show(saved&&tabs.querySelector('[data-tab="'+saved+'"]')?saved:tabs.querySelector('[data-tab]').dataset.tab);
tabs.addEventListener('click',e=>{const b=e.target.closest('[data-tab]');if(!b)return;show(b.dataset.tab);try{localStorage.setItem('client',b.dataset.tab)}catch(e){}});});
const tq=document.getElementById('toolq');
if(tq)tq.addEventListener('input',()=>{const terms=tq.value.toLowerCase().split(/\\s+/).filter(Boolean);
document.querySelectorAll('#toollist .tool').forEach(t=>{t.hidden=!terms.every(x=>t.dataset.text.includes(x));});});
"""

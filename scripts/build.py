#!/usr/bin/env python3
"""Generate the README directory section and the static site from servers/*.json.

usage: build.py [--readme] [--site OUT_DIR] [--status data/status.json]

  --readme   rewrite the directory section of README.md
  --site     write the website (index, one page per server, badges, JSON API) to OUT_DIR

SITE_URL sets the absolute address used in badges, the sitemap and llms.txt.
"""

import argparse
import html
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from lib import CATEGORIES, README, REPO_URL, ROOT, load_servers, render_directory, splice_readme, validate

SITE_URL = os.environ.get("SITE_URL", "https://aianytime.github.io/Awesome-MCP-Servers").rstrip("/")
MCP_URL = os.environ.get("MCP_URL", "").rstrip("/")
YOUTUBE = "https://www.youtube.com/@AIAnytime"

STATUS_LABEL = {"live": "Live", "auth": "Needs auth", "down": "Down", "unprobed": "Not checked"}
BADGE_COLOR = {"live": "#1a7f37", "auth": "#0969da", "down": "#cf222e", "unprobed": "#6e7781"}

LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
CODE = re.compile(r"`([^`]+)`")
EMPH = re.compile(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])")


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def md(text: str) -> str:
    """The small subset of Markdown that entries use: links, code and emphasis."""
    out = esc(text)
    out = CODE.sub(r"<code>\1</code>", out)
    out = LINK.sub(r'<a href="\2" rel="nofollow noopener">\1</a>', out)
    return EMPH.sub(r"<em>\1</em>", out)


def plain(text: str) -> str:
    return EMPH.sub(r"\1", CODE.sub(r"\1", LINK.sub(r"\1", text)))


def fmt_tokens(n: int) -> str:
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


def uptime(history: str) -> int | None:
    return round(100 * sum(c != "d" for c in history) / len(history)) if len(history) >= 7 else None


def status_text(entry: dict) -> str:
    """One honest sentence about what the last check saw."""
    s = entry["status"]
    kind = s["status"]
    if kind == "live":
        if "tools" in s:
            return f"Answered an MCP handshake without credentials and listed {s['tools']} tool{'s' if s['tools'] != 1 else ''}."
        return "Answered an MCP handshake without credentials. It did not list its tools to an anonymous client."
    if kind == "auth":
        how = "an OAuth sign-in" if s.get("auth") == "oauth" else "credentials"
        return f"Reachable, and asks for {how} before it will talk. Tools were not inspected."
    if kind == "down":
        return f"Did not answer an MCP handshake ({s.get('reason', 'no response')})."
    if entry["transport"] == "stdio":
        return "Runs on your own machine, so there is no endpoint to check."
    if entry["transport"] == "none":
        return "Not a server, so there is nothing to check."
    return "No endpoint is on file for this server, so it is not checked."


def facts(entry: dict) -> list[str]:
    s, out = entry["status"], []
    if "tools" in s:
        out.append(f"<b>{s['tools']}</b> tools")
        out.append(f"<b>~{fmt_tokens(s['tool_tokens'])}</b> tokens of tool definitions")
    if s["status"] in ("live", "auth") and "latency_ms" in s:
        out.append(f"<b>{s['latency_ms']}</b> ms")
    repo = s.get("repo") or {}
    if repo.get("missing"):
        out.append("repository link is broken")
    elif repo:
        out.append(f"<b>{repo['stars']:,}</b> stars")
        if repo.get("pushed"):
            out.append(f"last push {repo['pushed']}")
        if repo.get("archived"):
            out.append("archived")
    return out


def install_command(entry: dict) -> str | None:
    if "endpoint" in entry:
        return f"claude mcp add --transport {entry['transport']} {entry['slug']} {entry['endpoint']}"
    return None


def badge_svg(entry: dict) -> str:
    s = entry["status"]
    kind = s["status"]
    right = {"live": "live", "auth": "reachable · needs auth", "down": "down", "unprobed": "listed"}[kind]
    if kind == "live" and "tools" in s:
        right = f"live · {s['tools']} tools"
    left = "MCP"
    lw, rw = 12 + round(len(left) * 7.2), 12 + round(len(right) * 6.3)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{lw + rw}" height="20" role="img" aria-label="{left}: {esc(right)}">'
        f"<title>{esc(entry['name'])}: {esc(right)}</title>"
        f'<clipPath id="r"><rect width="{lw + rw}" height="20" rx="3"/></clipPath>'
        f'<g clip-path="url(#r)"><rect width="{lw}" height="20" fill="#24292f"/>'
        f'<rect x="{lw}" width="{rw}" height="20" fill="{BADGE_COLOR[kind]}"/></g>'
        f'<g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">'
        f'<text x="{lw / 2}" y="14">{left}</text><text x="{lw + rw / 2}" y="14">{esc(right)}</text></g></svg>\n'
    )


CSS = """
:root{--bg:#fbfaf7;--card:#fff;--ink:#1c1b19;--mute:#6b675f;--line:#e4e0d6;--accent:#0b5e55;--accent-ink:#fff;
--live:#1a7f37;--auth:#0969da;--down:#cf222e;--off:#8a857b;--code:#f1eee6}
@media (prefers-color-scheme:dark){:root{--bg:#141412;--card:#1c1c19;--ink:#ecebe6;--mute:#a09c92;--line:#33322d;
--accent:#5fd3c3;--accent-ink:#0c1f1c;--live:#4ac26b;--auth:#58a6ff;--down:#ff7b72;--off:#8a857b;--code:#262521}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--accent)}
code{font:.86em ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:var(--code);padding:.1em .35em;border-radius:4px;overflow-wrap:anywhere}
.wrap{max-width:1040px;margin:0 auto;padding:0 16px}
header.top{border-bottom:1px solid var(--line)}
header.top .wrap{display:flex;gap:16px;align-items:center;justify-content:space-between;padding-top:14px;padding-bottom:14px;flex-wrap:wrap}
.brand{font-weight:700;color:var(--ink);text-decoration:none;letter-spacing:-.01em}
.brand span{color:var(--mute);font-weight:500}
nav a{margin-left:18px;color:var(--mute);text-decoration:none;font-size:.93rem}
nav a:first-child{margin-left:0}
nav a:hover{color:var(--ink)}
.hero{padding:44px 0 18px}
h1{font-size:clamp(1.9rem,5vw,2.9rem);line-height:1.1;letter-spacing:-.03em;margin:0 0 14px;text-wrap:balance}
.lede{font-size:1.1rem;color:var(--mute);max-width:64ch;margin:0}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:26px 0 8px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.stat b{display:block;font-size:1.6rem;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.stat span{color:var(--mute);font-size:.86rem}
.note{color:var(--mute);font-size:.86rem;margin:6px 0 0}
.controls{position:sticky;top:0;z-index:2;background:var(--bg);padding:12px 0;display:flex;gap:8px;flex-wrap:wrap;border-bottom:1px solid var(--line)}
.controls input,.controls select{font:inherit;color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 10px;min-width:0}
.controls input{flex:1 1 240px}
.controls select{flex:0 1 auto;max-width:100%}
#count{color:var(--mute);font-size:.88rem;margin:12px 0}
.list{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.card h3{margin:0;font-size:1.05rem;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.card h3 a{color:var(--ink);text-decoration:none}
.card h3 a:hover{text-decoration:underline}
.card p{margin:6px 0 0;color:var(--mute);font-size:.94rem;overflow-wrap:anywhere}
.tag{font:600 .7rem ui-monospace,Menlo,monospace;border:1px solid var(--line);border-radius:5px;padding:1px 6px;color:var(--mute)}
.pill{font-size:.76rem;font-weight:600;white-space:nowrap}
.pill::before{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px;background:currentColor}
.live{color:var(--live)}.auth{color:var(--auth)}.down{color:var(--down)}.unprobed{color:var(--off)}
.unprobed.pill::before{background:none;border:1.5px solid currentColor}
.facts{margin:8px 0 0;font-size:.84rem;color:var(--mute);display:flex;flex-wrap:wrap;gap:4px 14px}
.facts b{color:var(--ink);font-variant-numeric:tabular-nums}
.cmd{display:flex;gap:8px;align-items:stretch;margin-top:10px}
.cmd code{flex:1;padding:7px 10px;white-space:nowrap;overflow-x:auto;overflow-wrap:normal}
button.copy{font:inherit;font-size:.82rem;cursor:pointer;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:6px;padding:0 12px}
button.copy:hover{border-color:var(--accent)}
section{padding:34px 0 0}
h2{font-size:1.35rem;letter-spacing:-.02em;margin:0 0 10px}
.learn{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px;padding:0;list-style:none;margin:14px 0 0}
.learn li{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;font-size:.93rem;color:var(--mute)}
.learn a{font-weight:600}
footer{margin-top:48px;border-top:1px solid var(--line);padding:22px 0 40px;color:var(--mute);font-size:.88rem}
.crumbs{margin:26px 0 8px;font-size:.9rem}
dl{display:grid;grid-template-columns:max-content 1fr;gap:6px 18px;margin:16px 0}
dt{color:var(--mute)}dd{margin:0;overflow-wrap:anywhere}
.days{display:flex;gap:3px;margin-top:6px}
.days i{width:12px;height:22px;border-radius:3px;background:var(--off)}
.days .u{background:var(--live)}.days .a{background:var(--auth)}.days .d{background:var(--down)}
pre{background:var(--code);padding:12px 14px;border-radius:8px;overflow-x:auto;font-size:.86rem}
pre code{background:none;padding:0;overflow-wrap:normal}
.tools{columns:220px;padding-left:18px;font-size:.9rem}
[hidden]{display:none!important}
"""

JS = """
const q=document.getElementById('q'),cat=document.getElementById('cat'),st=document.getElementById('st'),
sort=document.getElementById('sort'),list=document.getElementById('list'),count=document.getElementById('count');
const cards=[...list.children];
function apply(){
  const terms=q.value.toLowerCase().split(/\\s+/).filter(Boolean);let n=0;
  for(const c of cards){
    const d=c.dataset;
    const ok=(!cat.value||d.cat===cat.value)&&(!st.value||d.status===st.value||(st.value==='remote'&&d.status!=='unprobed'))
      &&terms.every(t=>d.text.includes(t));
    c.hidden=!ok;if(ok)n++;
  }
  const by=sort.value,num=k=>(a,b)=>(+b.dataset[k])-(+a.dataset[k]);
  const order={name:(a,b)=>a.dataset.name.localeCompare(b.dataset.name),tools:num('tools'),stars:num('stars'),
    light:(a,b)=>((+a.dataset.tokens)||1e12)-((+b.dataset.tokens)||1e12)}[by];
  [...cards].sort(order).forEach(c=>list.appendChild(c));
  count.textContent=n+' of '+cards.length+' servers';
  const p=new URLSearchParams();if(q.value)p.set('q',q.value);if(cat.value)p.set('category',cat.value);
  if(st.value)p.set('status',st.value);if(by!=='name')p.set('sort',by);
  history.replaceState(null,'',p.toString()?'?'+p:location.pathname);
}
const p=new URLSearchParams(location.search);
q.value=p.get('q')||'';cat.value=p.get('category')||'';st.value=p.get('status')||'';sort.value=p.get('sort')||'name';
if(cat.selectedIndex<0)cat.value='';if(st.selectedIndex<0)st.value='';if(sort.selectedIndex<0)sort.value='name';
[q,cat,st,sort].forEach(e=>e.addEventListener('input',apply));apply();
"""

COPY_JS = """
document.addEventListener('click',e=>{const b=e.target.closest('button.copy');if(!b)return;
navigator.clipboard.writeText(b.dataset.copy).then(()=>{const t=b.textContent;b.textContent='Copied';setTimeout(()=>b.textContent=t,1200)});});
"""


def page(title: str, description: str, body: str, root: str, canonical: str, script: str = "") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{esc(canonical)}">
<style>{CSS}</style>
</head>
<body>
<header class="top"><div class="wrap">
<a class="brand" href="{root}">Awesome MCP Servers <span>by AI Anytime</span></a>
<nav><a href="{root}#directory">Directory</a><a href="{root}#learn">Learn</a><a href="{root}#agents">For agents</a><a href="{REPO_URL}">GitHub</a></nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer><div class="wrap">
Checks record what a server answered, not whether it is safe. A listing is not a security audit; read a server's source and permissions before you connect it.
<br>Maintained by <a href="{YOUTUBE}">AI Anytime</a> · <a href="{REPO_URL}/blob/main/CONTRIBUTING.md">Add a server</a> · <a href="{root}api/servers.json">JSON</a> · <a href="{root}llms.txt">llms.txt</a>
</div></footer>
<script>{COPY_JS}{script}</script>
</body>
</html>
"""


def pill(entry: dict) -> str:
    kind = entry["status"]["status"]
    label = "Local" if kind == "unprobed" and entry["transport"] == "stdio" else STATUS_LABEL[kind]
    return f'<span class="pill {kind}">{label}</span>'


def command_block(command: str) -> str:
    return f'<div class="cmd"><code>{esc(command)}</code><button class="copy" data-copy="{esc(command)}">Copy</button></div>'


def card(entry: dict) -> str:
    s = entry["status"]
    text = " ".join([entry["name"], plain(entry["description"]), CATEGORIES[entry["category"]], entry["transport"], *s.get("tool_names", [])]).lower()
    tag = "" if entry["transport"] == "none" else f'<span class="tag">{entry["transport"]}</span>'
    fact_html = "".join(f"<span>{f}</span>" for f in facts(entry))
    command = install_command(entry)
    return (
        f'<li class="card" data-name="{esc(entry["name"].lower())}" data-cat="{entry["category"]}" data-status="{s["status"]}" '
        f'data-tools="{s.get("tools", 0)}" data-tokens="{s.get("tool_tokens", 0)}" data-stars="{(s.get("repo") or {}).get("stars", 0)}" data-text="{esc(text)}">'
        f'<h3><a href="s/{entry["slug"]}/">{esc(entry["name"])}</a>{tag}{pill(entry)}</h3>'
        f"<p>{md(entry['description'])}</p>"
        + (f'<div class="facts">{fact_html}</div>' if fact_html else "")
        + (command_block(command) if command else "")
        + "</li>"
    )


def index_page(servers: list[dict], reference: list[dict], generated: str) -> str:
    counts = {k: sum(e["status"]["status"] == k for e in servers) for k in STATUS_LABEL}
    remote = counts["live"] + counts["auth"] + counts["down"]
    cat_options = "".join(
        f'<option value="{slug}">{esc(title)} ({sum(e["category"] == slug for e in servers)})</option>' for slug, title in CATEGORIES.items()
    )
    learn = "".join(
        f'<li><a href="{REPO_URL}/tree/main/{esc(r["folder"]).replace(" ", "%20")}">{esc(r["title"])}</a><br>{esc(r["summary"])}'
        + (f' <a href="{esc(r["video"])}">Watch the walkthrough</a>' if r.get("video") else "")
        + "</li>"
        for r in reference
    )
    agents = (
        f"<p>This directory is itself an MCP server, so an agent can look up servers on its own.</p>{command_block(f'claude mcp add --transport http mcp-directory {MCP_URL}')}"
        if MCP_URL
        else "<p>The whole directory, with the latest check results, is one JSON file.</p>"
    )
    body = f"""
<div class="hero">
<h1>MCP servers we actually connect to, every night.</h1>
<p class="lede">A community directory of Model Context Protocol servers. Each hosted server is sent a real MCP handshake nightly, so you can see which ones answer, which need a sign-in, how many tools they expose and how much of your context those tools cost.</p>
<div class="stats">
<div class="stat"><b>{len(servers)}</b><span>servers listed</span></div>
<div class="stat"><b class="live">{counts["live"]}</b><span>answer without credentials</span></div>
<div class="stat"><b class="auth">{counts["auth"]}</b><span>reachable, need auth</span></div>
<div class="stat"><b class="down">{counts["down"]}</b><span>did not answer</span></div>
</div>
<p class="note">{remote} hosted endpoints checked, last on {esc(generated[:10])} (UTC). Local stdio servers run on your machine and are not checked.</p>
</div>
<div id="directory" class="controls">
<input id="q" type="search" placeholder="Search servers, descriptions and tool names" aria-label="Search">
<select id="cat" aria-label="Category"><option value="">All categories</option>{cat_options}</select>
<select id="st" aria-label="Status"><option value="">Any status</option><option value="live">Live, no credentials</option><option value="auth">Needs auth</option><option value="down">Down</option><option value="remote">All hosted</option><option value="unprobed">Local or not checked</option></select>
<select id="sort" aria-label="Sort"><option value="name">Sort: name</option><option value="tools">Most tools</option><option value="light">Lightest context</option><option value="stars">Most stars</option></select>
</div>
<p id="count"></p>
<ul id="list" class="list">
{chr(10).join(card(e) for e in servers)}
</ul>
<section id="learn">
<h2>Learn to build one</h2>
<p>Small, readable reference servers in Python that live in the same repository. Start with the first and work down.</p>
<ul class="learn">{learn}</ul>
</section>
<section id="agents">
<h2>For agents and scripts</h2>
{agents}
<p><a href="api/servers.json"><code>api/servers.json</code></a> has every entry and its last check. <a href="llms.txt"><code>llms.txt</code></a> is a plain-text index. Each server also has a status badge its author can embed.</p>
</section>
"""
    return page(
        "Awesome MCP Servers: a directory that checks every server nightly",
        f"{len(servers)} Model Context Protocol servers, with hosted endpoints connected to nightly: status, auth, tool count and context cost.",
        body,
        "./",
        SITE_URL + "/",
        JS,
    )


def server_page(entry: dict) -> str:
    s = entry["status"]
    url = f"{SITE_URL}/s/{entry['slug']}/"
    rows = [("Category", f'<a href="../../?category={entry["category"]}#directory">{esc(CATEGORIES[entry["category"]])}</a>')]
    if entry["transport"] != "none":
        rows.append(("Transport", f"<code>{entry['transport']}</code>"))
    rows.append(("Source", f'<a href="{esc(entry["url"])}" rel="nofollow noopener">{esc(entry["url"])}</a>'))
    if "endpoint" in entry:
        rows.append(("Endpoint", f"<code>{esc(entry['endpoint'])}</code>"))
    if "registry" in entry:
        rows.append(("MCP Registry", f"<code>{esc(entry['registry'])}</code>"))
    if s.get("server_name"):
        version = f" {esc(s['server_version'])}" if s.get("server_version") else ""
        rows.append(("Reports itself as", f"{esc(s['server_name'])}{version}"))
    if s.get("protocol"):
        rows.append(("Protocol", esc(s["protocol"])))
    if "tools" in s:
        rows.append(("Tools", str(s["tools"])))
        rows.append(("Context cost", f"about {s['tool_tokens']:,} tokens for the tool definitions (estimated at four characters per token)"))
        rows.append(("Tool definitions last changed", esc(s.get("tools_changed", "no change seen since first check"))))
    if "latency_ms" in s and s["status"] != "down":
        rows.append(("Handshake time", f"{s['latency_ms']} ms"))
    repo = s.get("repo") or {}
    if repo.get("missing"):
        rows.append(("Repository", "The linked GitHub repository was not found."))
    elif repo:
        bits = [f"{repo['stars']:,} stars", f"last push {repo['pushed']}"] + ([repo["license"]] if repo.get("license") and repo["license"] != "NOASSERTION" else []) + (["archived"] if repo.get("archived") else [])
        rows.append(("Repository", esc(" · ".join(bits))))
    if s.get("checked"):
        rows.append(("Last checked", esc(s["checked"].replace("T", " ").replace("Z", " UTC"))))
    rows.append(("Listed since", esc(s.get("first_seen", ""))))

    history = s.get("history", "")
    days = ""
    if history:
        up = uptime(history)
        summary = f"{up}% of the last {len(history)} daily checks reachable" if up is not None else f"{len(history)} daily check{'s' if len(history) != 1 else ''} so far"
        days = f'<h2>Check history</h2><p class="note">{summary}. Green answered, blue asked for auth, red did not answer.</p><div class="days">{"".join(f"<i class={c!r}></i>" for c in history)}</div>'

    connect = ""
    if command := install_command(entry):
        config = json.dumps({"mcpServers": {entry["slug"]: {"type": entry["transport"], "url": entry["endpoint"]}}}, indent=2)
        connect = f"<h2>Connect</h2><p>Claude Code:</p>{command_block(command)}<p>Other clients, as JSON config:</p><pre><code>{esc(config)}</code></pre>"

    tools = ""
    if s.get("tool_names"):
        tools = f'<h2>Tools</h2><ul class="tools">{"".join(f"<li><code>{esc(n)}</code></li>" for n in s["tool_names"])}</ul>'

    badge_md = f"[![MCP status]({SITE_URL}/badge/{entry['slug']}.svg)]({url})"
    body = f"""
<p class="crumbs"><a href="../../#directory">Directory</a> / {esc(CATEGORIES[entry["category"]])}</p>
<h1>{esc(entry["name"])}</h1>
<p class="lede">{md(entry["description"])}</p>
<p style="margin-top:18px">{pill(entry)} &nbsp;{esc(status_text(entry))}</p>
<dl>{"".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows)}</dl>
{connect}
{days}
{tools}
<h2>Badge</h2>
<p>Maintain this server? Put its live status in your README:</p>
<p><img src="../../badge/{entry["slug"]}.svg" alt="MCP status badge" height="20"></p>
{command_block(badge_md)}
<p class="note" style="margin-top:22px"><a href="{REPO_URL}/blob/main/servers/{entry["slug"]}.json">Edit this entry</a> · <a href="{REPO_URL}/issues/new?template=report-entry.yml">Report a problem</a></p>
"""
    return page(f"{entry['name']} MCP server: status, tools and setup", plain(entry["description"])[:155], body, "../../", url)


def llms_txt(servers: list[dict]) -> str:
    out = [
        "# Awesome MCP Servers",
        "",
        "> A community directory of Model Context Protocol servers by AI Anytime. Hosted endpoints are sent an MCP handshake nightly; "
        "status values are live (answers without credentials), auth (reachable, needs credentials), down, or unprobed (local or no endpoint). "
        "A listing is not a security audit.",
        "",
        f"- [Full data as JSON]({SITE_URL}/api/servers.json)",
    ]
    if MCP_URL:
        out.append(f"- MCP endpoint for searching this directory: {MCP_URL}")
    for slug, title in CATEGORIES.items():
        out += ["", f"## {title}", ""]
        for e in servers:
            if e["category"] == slug:
                where = f" Endpoint: {e['endpoint']}." if "endpoint" in e else ""
                out.append(f"- [{e['name']}]({SITE_URL}/s/{e['slug']}/): [{e['transport']}, {e['status']['status']}] {plain(e['description'])[:220]}{where}")
    return "\n".join(out) + "\n"


def build_site(out: Path, servers: list[dict], generated: str) -> None:
    if out.exists():
        shutil.rmtree(out)
    (out / "api").mkdir(parents=True)
    (out / "badge").mkdir()
    reference = json.loads((ROOT / "data" / "reference.json").read_text(encoding="utf-8"))

    (out / "index.html").write_text(index_page(servers, reference, generated), encoding="utf-8")
    for entry in servers:
        folder = out / "s" / entry["slug"]
        folder.mkdir(parents=True)
        (folder / "index.html").write_text(server_page(entry), encoding="utf-8")
        (out / "badge" / f"{entry['slug']}.svg").write_text(badge_svg(entry), encoding="utf-8")

    api = {"generated": generated, "site": SITE_URL, "categories": CATEGORIES, "servers": [e | {"page": f"{SITE_URL}/s/{e['slug']}/"} for e in servers]}
    (out / "api" / "servers.json").write_text(json.dumps(api, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (out / "llms.txt").write_text(llms_txt(servers), encoding="utf-8")
    urls = [f"{SITE_URL}/"] + [f"{SITE_URL}/s/{e['slug']}/" for e in servers]
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{esc(u)}</loc></url>\n" for u in urls)
        + "</urlset>\n",
        encoding="utf-8",
    )
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    host = SITE_URL.split("//", 1)[-1].split("/", 1)[0]
    if not host.endswith(".github.io"):  # a custom domain on GitHub Pages needs this file
        (out / "CNAME").write_text(host + "\n", encoding="utf-8")
    (out / "404.html").write_text(
        page("Not found", "This page does not exist.", f'<div class="hero"><h1>Nothing here.</h1><p class="lede"><a href="{SITE_URL}/">Back to the directory</a></p></div>', f"{SITE_URL}/", SITE_URL + "/"),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--readme", action="store_true")
    parser.add_argument("--site", type=Path)
    parser.add_argument("--status", type=Path, default=ROOT / "data" / "status.json")
    args = parser.parse_args()

    servers = load_servers()
    errors, _ = validate(servers)
    if errors:
        print("\n".join(errors))
        return 1

    if args.readme:
        README.write_text(splice_readme(README.read_text(encoding="utf-8"), render_directory(servers)), encoding="utf-8")
        print(f"README.md: {len(servers)} servers")

    if args.site:
        status = json.loads(args.status.read_text()) if args.status.exists() else {"servers": {}}
        generated = status.get("generated") or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        for entry in servers:
            entry["status"] = status["servers"].get(entry["slug"]) or {"status": "unprobed"}
        build_site(args.site, servers, generated)
        print(f"{args.site}: {len(servers)} server pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

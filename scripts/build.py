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

import sections
from lib import CATEGORIES, README, REPO_URL, ROOT, load_servers, render_directory, splice_readme, validate

SITE_URL = os.environ.get("SITE_URL", "https://mcp.aianytime.net").rstrip("/")
MCP_URL = os.environ.get("MCP_URL", "").rstrip("/")
YOUTUBE = "https://www.youtube.com/@AIAnytime"
MAIN_SITE = "https://aianytime.net"
ACADEMY = "https://academy.aianytime.net"

SITE_NAME = "Awesome MCP Servers by AI Anytime"
KEYWORDS = "MCP servers, Model Context Protocol, MCP directory, remote MCP servers, MCP server list, awesome mcp servers, AI agents, Claude, Cursor, AI Anytime"
STATIC = Path(__file__).resolve().parent / "static"

# Hub pages besides the categories: (slug, title, intro, filter).
COLLECTIONS = [
    (
        "no-auth",
        "MCP servers you can connect to without an account",
        "Hosted Model Context Protocol servers that answered last night's MCP handshake with no credentials at all. Paste the command and they work.",
        lambda e: e["status"]["status"] == "live",
    ),
    (
        "local",
        "Local MCP servers that run on your machine",
        "Model Context Protocol servers that run locally over stdio. Nothing is hosted, so your data stays on your machine and there is no endpoint to check.",
        lambda e: e["transport"] == "stdio",
    ),
]

FAQ = [
    ("What is an MCP server?", "An MCP server exposes tools, data or prompts to an AI assistant through the Model Context Protocol, an open standard. A client such as Claude, Cursor or VS Code connects to the server and can then call its tools."),
    ("How is this directory different from other MCP server lists?", "Every hosted server here is sent a real MCP handshake each night. The directory shows which servers answered, which asked for credentials, how many tools each one exposes and roughly how many tokens those tool definitions take up in a model's context."),
    ("What do Live, Needs auth and Down mean?", "Live means the server answered an MCP initialize request without any credentials. Needs auth means it is reachable but asked for an OAuth sign-in or an API key first. Down means it did not return a valid MCP response. Local stdio servers run on your own machine and are not checked."),
    ("What is context cost?", "A client loads every tool definition a server exposes into the model's context. Context cost is an estimate of how many tokens those definitions take, at about four characters per token. A server with hundreds of tools can use tens of thousands of tokens before you ask anything."),
    ("Does a listing mean a server is safe?", "No. The nightly check records what a server answered, not whether it is safe. A listing is not a security audit. Read a server's source and the permissions it asks for before you connect it."),
    ("How do I add my MCP server?", "Open a pull request on GitHub that adds one small JSON file for your server. Once it merges, the server gets its own page, a nightly check and a status badge you can embed in your README."),
    ("Can an AI agent search this directory?", "Yes. The whole directory is available as a JSON file and as llms.txt and llms-full.txt, and the repository includes an MCP server that searches the directory by keyword, category and live status."),
]

STATUS_LABEL = {"live": "Live", "auth": "Needs auth", "down": "Down", "unprobed": "Not checked"}
BADGE_COLOR = {"live": "#1a7f37", "auth": "#5b3df5", "down": "#cf222e", "unprobed": "#6e7781"}

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
:root{--bg:#f6f4ee;--card:#fffdf8;--ink:#121118;--mute:#625f6d;--line:#dedad0;--accent:#5b3df5;--accent-soft:#ebe6ff;
--lime:#d4f75e;--night:#0d0c12;--night-2:#17151f;--night-line:#2b2935;
--live:#1a7f37;--auth:#5b3df5;--down:#c0262d;--off:#8a8794;--code:#efece3}
/* Dark: follows the system unless the visitor picked a theme with the header button. */
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#0d0c12;--card:#17151f;--ink:#f6f4ee;--mute:#a9a6b5;--line:#2b2935;
--accent:#a594ff;--accent-soft:#241d4d;--live:#d4f75e;--auth:#a594ff;--down:#ff8a80;--off:#7d7a89;--code:#211f2b}}
:root[data-theme=dark]{--bg:#0d0c12;--card:#17151f;--ink:#f6f4ee;--mute:#a9a6b5;--line:#2b2935;
--accent:#a594ff;--accent-soft:#241d4d;--live:#d4f75e;--auth:#a594ff;--down:#ff8a80;--off:#7d7a89;--code:#211f2b}
.icon .sun{display:none}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]) .icon .sun{display:block}:root:not([data-theme=light]) .icon .moon{display:none}}
:root[data-theme=dark] .icon .sun{display:block}:root[data-theme=dark] .icon .moon{display:none}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Geist,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
body{min-height:100vh;display:flex;flex-direction:column}
main{flex:1;width:100%}
a{color:var(--accent)}
code{font:.86em "Geist Mono",ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--code);padding:.1em .35em;border-radius:4px;overflow-wrap:anywhere}
.wrap{max-width:1040px;margin:0 auto;padding:0 16px}
header.top{border-bottom:1px solid var(--line)}
header.top .wrap{display:flex;gap:16px;align-items:center;justify-content:space-between;padding-top:14px;padding-bottom:14px;flex-wrap:wrap}
.brand{font-weight:700;color:var(--ink);text-decoration:none;letter-spacing:-.01em}
.brand span{color:var(--mute);font-weight:500}
nav a{margin-left:18px;color:var(--mute);text-decoration:none;font-size:.93rem}
nav a:first-child{margin-left:0;color:var(--accent);font-weight:600}
nav a:hover{color:var(--ink)}
nav{display:flex;align-items:center;flex-wrap:wrap;row-gap:8px}
.icon{display:inline-grid;place-items:center;width:34px;height:34px;margin-left:10px;padding:0;cursor:pointer;color:var(--mute);background:var(--card);border:1px solid var(--line);border-radius:999px}
nav a+.icon{margin-left:18px}
.icon:hover{color:var(--accent);border-color:var(--accent)}
.icon svg{width:17px;height:17px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.hero{padding:44px 0 18px}
h1{font:400 clamp(2.3rem,6vw,3.6rem)/1.05 "Instrument Serif",ui-serif,Georgia,serif;letter-spacing:-.01em;margin:0 0 14px;text-wrap:balance}
h1 em{font-style:italic;color:var(--accent)}
.lede{font-size:1.1rem;color:var(--mute);max-width:64ch;margin:0}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:26px 0 8px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.stat b{display:block;font-weight:600;font-size:1.6rem;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.stat span{color:var(--mute);font-size:.86rem}
.note{color:var(--mute);font-size:.86rem;margin:6px 0 0}
.controls{position:sticky;top:0;z-index:2;background:var(--bg);padding:12px 0;display:flex;gap:8px;flex-wrap:wrap;border-bottom:1px solid var(--line)}
.controls input,.controls select{font:inherit;color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 10px;min-width:0}
.controls input{flex:1 1 240px}
.controls select{flex:0 1 auto;max-width:100%}
#count{color:var(--mute);font-size:.88rem;margin:12px 0}
.list{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.card:hover{border-color:var(--accent)}
.card h3{margin:0;font-size:1.05rem;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.card h3 a{color:var(--ink);text-decoration:none}
.card h3 a:hover{text-decoration:underline}
.card p{margin:6px 0 0;color:var(--mute);font-size:.94rem;overflow-wrap:anywhere}
.tag{font:500 .7rem "Geist Mono",ui-monospace,Menlo,monospace;background:var(--accent-soft);color:var(--accent);border-radius:5px;padding:1px 6px}
.pill{font-size:.76rem;font-weight:600;white-space:nowrap}
.pill::before{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px;background:currentColor}
.live{color:var(--live)}.auth{color:var(--auth)}.down{color:var(--down)}.unprobed{color:var(--off)}
.unprobed.pill::before{background:none;border:1.5px solid currentColor}
.facts{margin:8px 0 0;font-size:.84rem;color:var(--mute);display:flex;flex-wrap:wrap;gap:4px 14px}
.facts b{color:var(--ink);font-variant-numeric:tabular-nums}
.cmd{display:flex;gap:8px;align-items:stretch;margin-top:10px}
.cmd code{flex:1;padding:7px 10px;white-space:nowrap;overflow-x:auto;overflow-wrap:normal}
button.copy{font:inherit;font-size:.82rem;cursor:pointer;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:6px;padding:0 12px}
button.copy:hover{border-color:var(--accent);color:var(--accent)}
.controls input:focus,.controls select:focus{outline:2px solid var(--accent);outline-offset:1px}
section{padding:34px 0 0}
h2{font-size:1.35rem;letter-spacing:-.02em;margin:0 0 10px}
.learn{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px;padding:0;list-style:none;margin:14px 0 0}
.learn li{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;font-size:.93rem;color:var(--mute)}
.learn a{font-weight:600}
.fineprint{margin-top:44px;color:var(--mute);font-size:.86rem}
footer{margin-top:22px;background:var(--night);color:#b9b6c6;font-size:.92rem;border-top:1px solid var(--night-line)}
footer .wrap{padding-top:36px;padding-bottom:36px}
footer a{color:#f6f4ee}
.foot{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:28px;align-items:start}
.foot h2{font:400 1.7rem/1.1 "Instrument Serif",ui-serif,Georgia,serif;color:#f6f4ee;margin:0 0 8px;letter-spacing:0}
.foot p{margin:0 0 12px;max-width:46ch}
.foot .links a{margin-right:16px;white-space:nowrap}
.academy{background:var(--night-2);border:1px solid var(--night-line);border-radius:16px;padding:20px 22px}
.academy .eyebrow{font:500 .72rem "Geist Mono",ui-monospace,monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--lime)}
.academy h3{font:400 1.5rem/1.15 "Instrument Serif",ui-serif,Georgia,serif;color:#f6f4ee;margin:6px 0 8px}
.academy a.cta{display:inline-block;background:var(--lime);color:#121118;font-weight:600;text-decoration:none;border-radius:999px;padding:9px 18px;margin-top:4px}
.academy a.cta:hover{filter:brightness(1.06)}
.crumbs{margin:26px 0 8px;font-size:.9rem}
dl{display:grid;grid-template-columns:max-content 1fr;gap:6px 18px;margin:16px 0}
dt{color:var(--mute)}dd{margin:0;overflow-wrap:anywhere}
.days{display:flex;gap:3px;margin-top:6px}
.days i{width:12px;height:22px;border-radius:3px;background:var(--off)}
.days .u{background:var(--live)}.days .a{background:var(--auth)}.days .d{background:var(--down)}
pre{background:var(--code);padding:12px 14px;border-radius:8px;overflow-x:auto;font-size:.86rem}
pre code{background:none;padding:0;overflow-wrap:normal}
.tools{columns:220px;padding-left:18px;font-size:.9rem}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 0;padding:0;list-style:none}
.chips a{display:inline-block;background:var(--card);border:1px solid var(--line);border-radius:999px;padding:5px 12px;font-size:.88rem;text-decoration:none;color:var(--ink)}
.chips a:hover{border-color:var(--accent);color:var(--accent)}
.chips a span{color:var(--mute)}
.faq details{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 16px;margin-top:8px}
.faq summary{cursor:pointer;font-weight:600}
.faq p{margin:8px 0 0;color:var(--mute)}
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
document.getElementById('theme').addEventListener('click',()=>{const r=document.documentElement;
const dark=r.dataset.theme?r.dataset.theme==='dark':matchMedia('(prefers-color-scheme:dark)').matches;
r.dataset.theme=dark?'light':'dark';try{localStorage.setItem('theme',r.dataset.theme)}catch(e){}});
document.getElementById('refresh').addEventListener('click',()=>location.reload());
"""


CSS += sections.SECTION_CSS


def jsonld(*items: dict) -> str:
    graph = {"@context": "https://schema.org", "@graph": list(items)}
    return '<script type="application/ld+json">' + json.dumps(graph, ensure_ascii=False).replace("</", "<\\/") + "</script>"


ORG = {
    "@type": "Organization",
    "@id": "https://aianytime.net/#organization",
    "name": "AI Anytime",
    "url": "https://aianytime.net",
    "sameAs": ["https://www.youtube.com/@AIAnytime", "https://github.com/AIAnytime", "https://academy.aianytime.net"],
}


def breadcrumbs(*trail: tuple[str, str]) -> dict:
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [{"@type": "ListItem", "position": i, "name": name, "item": url} for i, (name, url) in enumerate(trail, 1)],
    }


def item_list(entries: list[dict]) -> dict:
    return {
        "@type": "ItemList",
        "numberOfItems": len(entries),
        "itemListElement": [{"@type": "ListItem", "position": i, "name": e["name"], "url": f"{SITE_URL}/s/{e['slug']}/"} for i, e in enumerate(entries, 1)],
    }


def page(title: str, description: str, body: str, root: str, canonical: str, script: str = "", schema: str = "", index: bool = True) -> str:
    browse = " · ".join(f'<a href="{root}c/{slug}/">{esc(name)}</a>' for slug, name in CATEGORIES.items())
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="keywords" content="{esc(KEYWORDS)}">
<meta name="author" content="AI Anytime">
<meta name="robots" content="{'index,follow,max-image-preview:large,max-snippet:-1' if index else 'noindex,follow'}">
<meta name="theme-color" content="#f6f4ee">
<link rel="canonical" href="{esc(canonical)}">
<link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/json" title="Directory data" href="{root}api/servers.json">
<link rel="alternate" type="text/plain" title="llms.txt" href="{root}llms.txt">
<meta property="og:site_name" content="{esc(SITE_NAME)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:image" content="{SITE_URL}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Awesome MCP Servers by AI Anytime: MCP servers we actually connect to, every night.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{SITE_URL}/og.png">
{schema}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500&family=Instrument+Serif:ital@0;1&display=swap">
<script>try{{var t=localStorage.getItem('theme');if(t==='dark'||t==='light')document.documentElement.dataset.theme=t}}catch(e){{}}</script>
<style>{CSS}</style>
</head>
<body>
<header class="top"><div class="wrap">
<a class="brand" href="{root}">Awesome MCP Servers <span>by AI Anytime</span></a>
<nav><a href="{ACADEMY}">Academy</a><a href="{root}#directory">Directory</a><a href="{root}status/">Status</a><a href="{root}#learn">Learn</a><a href="{root}#agents">For agents</a><a href="{REPO_URL}">GitHub</a>
<button id="refresh" class="icon" type="button" title="Reload for the latest check results" aria-label="Reload page"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 11a8 8 0 1 0-2.3 5.7"/><path d="M20 4v7h-7"/></svg></button>
<button id="theme" class="icon" type="button" title="Switch between light and dark" aria-label="Switch theme"><svg class="moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg><svg class="sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg></button></nav>
</div></header>
<main class="wrap">
{body}
<p class="fineprint">Checks record what a server answered, not whether it is safe. A listing is not a security audit; read a server's source and permissions before you connect it.
<a href="{REPO_URL}/blob/main/CONTRIBUTING.md">Add a server</a> · <a href="{root}api/servers.json">JSON</a> · <a href="{root}llms.txt">llms.txt</a> · <a href="{root}llms-full.txt">llms-full.txt</a></p>
<p class="fineprint" style="margin-top:8px">Browse: {browse} · <a href="{root}c/no-auth/">No account needed</a> · <a href="{root}c/local/">Local servers</a></p>
</main>
<footer><div class="wrap foot">
<div>
<h2>AI Anytime</h2>
<p>Practical AI for all. AI education, research and enablement, rooted in open source. This directory is built and maintained by AI Anytime.</p>
<p class="links"><a href="{MAIN_SITE}">aianytime.net</a><a href="{YOUTUBE}">YouTube</a><a href="{REPO_URL}">GitHub</a></p>
</div>
<div class="academy">
<span class="eyebrow">AI Anytime Academy</span>
<h3>Become an AI engineer by building.</h3>
<p>Structured career tracks, browser coding labs, an AI mentor and AI-reviewed portfolio projects. Start for free.</p>
<a class="cta" href="{ACADEMY}">Explore the Academy</a>
</div>
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


def card(entry: dict, root: str = "") -> str:
    s = entry["status"]
    text = " ".join([entry["name"], plain(entry["description"]), CATEGORIES[entry["category"]], entry["transport"], *s.get("tool_names", [])]).lower()
    tag = "" if entry["transport"] == "none" else f'<span class="tag">{entry["transport"]}</span>'
    fact_html = "".join(f"<span>{f}</span>" for f in facts(entry))
    command = install_command(entry)
    return (
        f'<li class="card" data-name="{esc(entry["name"].lower())}" data-cat="{entry["category"]}" data-status="{s["status"]}" '
        f'data-tools="{s.get("tools", 0)}" data-tokens="{s.get("tool_tokens", 0)}" data-stars="{(s.get("repo") or {}).get("stars", 0)}" data-text="{esc(text)}">'
        f'<h3><a href="{root}s/{entry["slug"]}/">{esc(entry["name"])}</a>{tag}{pill(entry)}</h3>'
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
    chips = "".join(
        f'<li><a href="c/{slug}/">{esc(title)} <span>{sum(e["category"] == slug for e in servers)}</span></a></li>' for slug, title in CATEGORIES.items()
    ) + "".join(f'<li><a href="c/{slug}/">{esc(title)} <span>{sum(map(keep, servers))}</span></a></li>' for slug, title, _, keep in COLLECTIONS)
    faq = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in FAQ)
    schema = jsonld(
        ORG,
        {
            "@type": "WebSite",
            "@id": f"{SITE_URL}/#website",
            "url": f"{SITE_URL}/",
            "name": "Awesome MCP Servers",
            "alternateName": SITE_NAME,
            "description": "A community directory of Model Context Protocol servers whose hosted endpoints are checked every night.",
            "publisher": {"@id": ORG["@id"]},
            "potentialAction": {"@type": "SearchAction", "target": {"@type": "EntryPoint", "urlTemplate": f"{SITE_URL}/?q={{search_term_string}}"}, "query-input": "required name=search_term_string"},
        },
        {
            "@type": "CollectionPage",
            "@id": f"{SITE_URL}/#directory",
            "url": f"{SITE_URL}/",
            "name": "Awesome MCP Servers directory",
            "isPartOf": {"@id": f"{SITE_URL}/#website"},
            "dateModified": generated,
            "mainEntity": item_list(servers),
        },
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
    )
    body = f"""
<div class="hero">
<h1>MCP servers we actually connect to, <em>every night.</em></h1>
<p class="lede">A community directory of Model Context Protocol servers. Each hosted server is sent a real MCP handshake nightly, so you can see which ones answer, which need a sign-in, how many tools they expose and how much of your context those tools cost.</p>
<div class="stats">
<div class="stat"><b>{len(servers)}</b><span>servers listed</span></div>
<div class="stat"><b class="live">{counts["live"]}</b><span>answer without credentials</span></div>
<div class="stat"><b class="auth">{counts["auth"]}</b><span>reachable, need auth</span></div>
<div class="stat"><b class="down">{counts["down"]}</b><span>did not answer</span></div>
</div>
<p class="note">{remote} hosted endpoints checked, last on <time datetime="{esc(generated)}">{esc(generated[:10])}</time> (UTC). Local stdio servers run on your machine and are not checked.</p>
<ul class="chips">{chips}</ul>
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
<p><a href="api/servers.json"><code>api/servers.json</code></a> has every entry and its last check. <a href="llms.txt"><code>llms.txt</code></a> is a plain-text index and <a href="llms-full.txt"><code>llms-full.txt</code></a> has every server in full. Each server also has a status badge its author can embed.</p>
</section>
<section id="faq" class="faq">
<h2>Questions</h2>
{faq}
</section>
"""
    return page(
        "Awesome MCP Servers: a directory that checks every server nightly",
        f"{len(servers)} Model Context Protocol servers, with hosted endpoints connected to nightly: status, auth, tool count and context cost.",
        body,
        "./",
        SITE_URL + "/",
        JS,
        schema,
    )


def collection_page(slug: str, title: str, intro: str, entries: list[dict], generated: str) -> str:
    url = f"{SITE_URL}/c/{slug}/"
    counts = {k: sum(e["status"]["status"] == k for e in entries) for k in STATUS_LABEL}
    hosted = counts["live"] + counts["auth"] + counts["down"]
    summary = f"{len(entries)} server{'s' if len(entries) != 1 else ''} listed."
    if hosted:
        summary += f" Of the {hosted} hosted, {counts['live']} answered without credentials, {counts['auth']} need auth and {counts['down']} did not answer on {generated[:10]}."
    others = "".join(f'<li><a href="../{s}/">{esc(n)}</a></li>' for s, n in CATEGORIES.items() if s != slug)
    others += "".join(f'<li><a href="../{s}/">{esc(n)}</a></li>' for s, n, _, _ in COLLECTIONS if s != slug)
    body = f"""
<p class="crumbs"><a href="../../#directory">Directory</a> / {esc(title)}</p>
<h1>{esc(title)}</h1>
<p class="lede">{esc(intro)}</p>
<p class="note" style="margin:14px 0 22px">{esc(summary)}</p>
<ul class="list">
{chr(10).join(card(e, "../../") for e in entries)}
</ul>
<section>
<h2>More of the directory</h2>
<ul class="chips">{others}<li><a href="../../#directory">All servers</a></li></ul>
</section>
"""
    schema = jsonld(
        ORG,
        {"@type": "CollectionPage", "url": url, "name": title, "description": intro, "isPartOf": {"@id": f"{SITE_URL}/#website"}, "dateModified": generated, "mainEntity": item_list(entries)},
        breadcrumbs(("Directory", f"{SITE_URL}/"), (title, url)),
    )
    return page(f"{title} | Awesome MCP Servers", intro[:200], body, "../../", url, schema=schema)


def server_page(entry: dict, related: list[dict], detail: dict | None = None) -> str:
    s = entry["status"]
    url = f"{SITE_URL}/s/{entry['slug']}/"
    rows = [("Category", f'<a href="../../c/{entry["category"]}/">{esc(CATEGORIES[entry["category"]])}</a>')]
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

    health = sections.health_section(entry)
    connect = sections.setup_section(entry)
    tools = sections.tools_section(entry, detail)

    badge_md = f"[![MCP status]({SITE_URL}/badge/{entry['slug']}.svg)]({url})"
    body = f"""
<p class="crumbs"><a href="../../#directory">Directory</a> / <a href="../../c/{entry["category"]}/">{esc(CATEGORIES[entry["category"]])}</a></p>
<h1>{esc(entry["name"])}</h1>
<p class="lede">{md(entry["description"])}</p>
<p style="margin-top:18px">{pill(entry)} &nbsp;{esc(status_text(entry))}</p>
<dl>{"".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows)}</dl>
{health}
{connect}
{tools}
<h2>Badge</h2>
<p>Maintain this server? Put its live status in your README:</p>
<p><img src="../../badge/{entry["slug"]}.svg" alt="MCP status badge" height="20"></p>
{command_block(badge_md)}
<p class="note" style="margin-top:22px"><a href="{REPO_URL}/blob/main/servers/{entry["slug"]}.json">Edit this entry</a> · <a href="{REPO_URL}/issues/new?template=report-entry.yml">Report a problem</a></p>
<section>
<h2>More in {esc(CATEGORIES[entry["category"]])}</h2>
<ul class="chips">{"".join(f'<li><a href="../{r["slug"]}/">{esc(r["name"])}</a></li>' for r in related)}<li><a href="../../c/{entry["category"]}/">All of {esc(CATEGORIES[entry["category"]])}</a></li></ul>
</section>
"""
    description = f"{entry['name']} MCP server. {status_text(entry)} {plain(entry['description'])}"
    description = description if len(description) <= 200 else description[:197].rsplit(" ", 1)[0] + "..."
    app = {
        "@type": "SoftwareApplication",
        "name": entry["name"],
        "description": plain(entry["description"]),
        "url": url,
        "sameAs": entry["url"],
        "applicationCategory": "DeveloperApplication",
        "applicationSubCategory": f"MCP server ({CATEGORIES[entry['category']]})",
        "operatingSystem": "Any",
        "isPartOf": {"@id": f"{SITE_URL}/#website"},
    }
    if s.get("server_version"):
        app["softwareVersion"] = s["server_version"]
    if s.get("tool_names"):
        app["featureList"] = s["tool_names"][:50]
    if s.get("checked"):
        app["dateModified"] = s["checked"]
    schema = jsonld(ORG, app, breadcrumbs(("Directory", f"{SITE_URL}/"), (CATEGORIES[entry["category"]], f"{SITE_URL}/c/{entry['category']}/"), (entry["name"], url)))
    return page(f"{entry['name']} MCP server: status, tools and setup", description, body, "../../", url, sections.SECTION_JS, schema)


def status_page(servers: list[dict], generated: str) -> str:
    url = f"{SITE_URL}/status/"
    hosted = [e for e in servers if e["status"]["status"] != "unprobed"]
    order = {"down": 0, "auth": 1, "live": 2}
    hosted.sort(key=lambda e: (order[e["status"]["status"]], e["name"].lower()))
    counts = {k: sum(e["status"]["status"] == k for e in hosted) for k in ("live", "auth", "down")}
    discovered = sum(sections.steps(e)[1] == "ok" for e in hosted)

    reasons: dict[str, int] = {}
    for e in hosted:
        if e["status"]["status"] == "down":
            label = sections.failure_label(e["status"].get("reason", ""))
            reasons[label] = reasons.get(label, 0) + 1
    protocols: dict[str, int] = {}
    for e in hosted:
        if proto := e["status"].get("protocol"):
            protocols[proto] = protocols.get(proto, 0) + 1

    def mark(outcome: str, ok: str = "ok") -> str:
        return sections.state_pill("verified" if outcome == ok else "failed" if outcome == "failed" else "untested")

    rows = ""
    for e in hosted:
        s = e["status"]
        init, discovery = sections.steps(e)
        up = sections.uptime(s.get("history", ""))
        rows += (
            f'<tr><td><a href="../s/{e["slug"]}/#health">{esc(e["name"])}</a></td><td>{pill(e)}</td><td>{mark(init)}</td><td>{mark(discovery)}</td>'
            f'<td>{s.get("tools", "")}</td><td>{esc(s.get("protocol", ""))}</td><td>{str(s["latency_ms"]) + " ms" if "latency_ms" in s and s["status"] != "down" else ""}</td>'
            f'<td>{sections.history_strip(s.get("history", ""))}</td><td>{str(up) + "%" if up is not None else "new"}</td></tr>'
        )
    why = "".join(f"<li><b>{n}</b> {esc(label)}</li>" for label, n in sorted(reasons.items(), key=lambda kv: -kv[1])) or "<li>None today.</li>"
    protos = ", ".join(f"{esc(k)} ({v})" for k, v in sorted(protocols.items(), reverse=True))
    body = f"""
<p class="crumbs"><a href="../#directory">Directory</a> / Status</p>
<h1>MCP server status</h1>
<p class="lede">What every hosted server in the directory answered when it was last sent an MCP handshake. Checked nightly; last run <time datetime="{esc(generated)}">{esc(generated.replace("T", " ").replace("Z", " UTC"))}</time>.</p>
<div class="stats">
<div class="stat"><b>{len(hosted)}</b><span>hosted endpoints checked</span></div>
<div class="stat"><b class="live">{counts["live"]}</b><span>answer without credentials</span></div>
<div class="stat"><b class="auth">{counts["auth"]}</b><span>reachable, need auth</span></div>
<div class="stat"><b class="down">{counts["down"]}</b><span>did not answer</span></div>
</div>
<p class="note">{discovered} servers also returned their tool list. Protocol versions seen: {protos or "none"}. <b>Verified</b> means the check saw the step succeed, <b>Failed</b> means it was tried and did not work, and <b>Untested</b> means it could not be tried, usually because the server wants credentials first. None of this says a server is safe.</p>
<h2>Why servers failed</h2>
<ul class="tips">{why}</ul>
<h2>All hosted servers</h2>
<div class="scroll"><table class="status">
<thead><tr><th>Server</th><th>Status</th><th>Handshake</th><th>Tool discovery</th><th>Tools</th><th>Protocol</th><th>Response</th><th>Last 30 days</th><th>Reachable</th></tr></thead>
<tbody>{rows}</tbody></table></div>
"""
    schema = jsonld(ORG, {"@type": "WebPage", "url": url, "name": "MCP server status", "isPartOf": {"@id": f"{SITE_URL}/#website"}, "dateModified": generated}, breadcrumbs(("Directory", f"{SITE_URL}/"), ("Status", url)))
    return page(
        "MCP server status: which servers are live right now | Awesome MCP Servers",
        f"Live status of {len(hosted)} hosted MCP servers: handshake, tool discovery, protocol version, response time and 30-day history, checked nightly.",
        body,
        "../",
        url,
        schema=schema,
    )


def llms_txt(servers: list[dict]) -> str:
    out = [
        "# Awesome MCP Servers",
        "",
        "> A community directory of Model Context Protocol servers by AI Anytime. Hosted endpoints are sent an MCP handshake nightly; "
        "status values are live (answers without credentials), auth (reachable, needs credentials), down, or unprobed (local or no endpoint). "
        "A listing is not a security audit.",
        "",
        f"- [Every server in full, as plain text]({SITE_URL}/llms-full.txt)",
        f"- [Full data as JSON]({SITE_URL}/api/servers.json)",
        f"- [Live status of every hosted server]({SITE_URL}/status/)",
        f"- [Servers that need no account]({SITE_URL}/c/no-auth/)",
        f"- [Local stdio servers]({SITE_URL}/c/local/)",
        f"- [Source and how to add a server]({REPO_URL})",
    ]
    if MCP_URL:
        out.append(f"- MCP endpoint for searching this directory: {MCP_URL}")
    for slug, title in CATEGORIES.items():
        out += ["", f"## [{title}]({SITE_URL}/c/{slug}/)", ""]
        for e in servers:
            if e["category"] == slug:
                where = f" Endpoint: {e['endpoint']}." if "endpoint" in e else ""
                out.append(f"- [{e['name']}]({SITE_URL}/s/{e['slug']}/): [{e['transport']}, {e['status']['status']}] {plain(e['description'])[:220]}{where}")
    return "\n".join(out) + "\n"


def llms_full_txt(servers: list[dict], generated: str) -> str:
    counts = {k: sum(e["status"]["status"] == k for e in servers) for k in STATUS_LABEL}
    out = [
        "# Awesome MCP Servers: full directory",
        "",
        f"> {len(servers)} Model Context Protocol servers, maintained by AI Anytime ({MAIN_SITE}). Hosted endpoints were last checked on {generated[:10]} (UTC): "
        f"{counts['live']} answered without credentials, {counts['auth']} are reachable but need auth, {counts['down']} did not answer. "
        "A listing is not a security audit. Descriptions are written by each server's author.",
        "",
        f"Site: {SITE_URL}/",
        f"Data: {SITE_URL}/api/servers.json",
        f"Source: {REPO_URL}",
        "",
        "## How servers are checked",
        "",
        "Each night every hosted (http or sse) server with a known endpoint is sent an MCP `initialize` request and, if it answers without credentials, a `tools/list`. "
        "The check records the result (live, auth, down), the handshake time, the number of tools, an estimate of the tokens the tool definitions take (about four characters per token) "
        "and a hash of the definitions so that changes are noticed. Local stdio servers are listed but not checked.",
        "",
        "## Questions and answers",
        "",
    ]
    for q, a in FAQ:
        out += [f"### {q}", "", a, ""]
    for slug, title in CATEGORIES.items():
        out += [f"## {title}", ""]
        for e in servers:
            if e["category"] != slug:
                continue
            s = e["status"]
            out += [f"### {e['name']}", "", plain(e["description"]), ""]
            out.append(f"- Page: {SITE_URL}/s/{e['slug']}/")
            out.append(f"- Source: {e['url']}")
            out.append(f"- Transport: {e['transport']}")
            if "endpoint" in e:
                out.append(f"- Endpoint: {e['endpoint']}")
                out.append(f"- Connect with Claude Code: `{install_command(e)}`")
            if "registry" in e:
                out.append(f"- MCP Registry id: {e['registry']}")
            out.append(f"- Last check: {status_text(e)}")
            if "tools" in s:
                out.append(f"- Tools: {s['tools']} (about {s['tool_tokens']:,} tokens of definitions)")
                out.append(f"- Tool names: {', '.join(s.get('tool_names', []))}")
            repo = s.get("repo") or {}
            if repo and not repo.get("missing"):
                out.append(f"- Repository: {repo['stars']:,} stars, last push {repo['pushed']}")
            out.append("")
    return "\n".join(out)


def build_site(out: Path, servers: list[dict], generated: str, tools_dir: Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    (out / "api").mkdir(parents=True)
    (out / "api" / "tools").mkdir()
    (out / "badge").mkdir()
    (out / "status").mkdir()
    (out / "status" / "index.html").write_text(status_page(servers, generated), encoding="utf-8")
    reference = json.loads((ROOT / "data" / "reference.json").read_text(encoding="utf-8"))

    (out / "index.html").write_text(index_page(servers, reference, generated), encoding="utf-8")
    for asset in STATIC.iterdir():
        shutil.copy(asset, out / asset.name)

    hubs = [(slug, f"{title} MCP servers", f"Model Context Protocol servers for {title[0].lower() + title[1:]}, with nightly status, tool counts and install commands for the hosted ones.", [e for e in servers if e["category"] == slug]) for slug, title in CATEGORIES.items()]
    hubs += [(slug, title, intro, [e for e in servers if keep(e)]) for slug, title, intro, keep in COLLECTIONS]
    for slug, title, intro, entries in hubs:
        (out / "c" / slug).mkdir(parents=True)
        (out / "c" / slug / "index.html").write_text(collection_page(slug, title, intro, entries, generated), encoding="utf-8")

    for entry in servers:
        folder = out / "s" / entry["slug"]
        folder.mkdir(parents=True)
        # Link each server to the next few in its category, wrapping round, so every page is linked from several others.
        peers = [e for e in servers if e["category"] == entry["category"]]
        at = peers.index(entry)
        related = [p for p in (peers[at + 1 :] + peers[:at])[:6]]
        detail = None
        if (tools_dir / f"{entry['slug']}.json").exists():
            detail = json.loads((tools_dir / f"{entry['slug']}.json").read_text(encoding="utf-8"))
            (out / "api" / "tools" / f"{entry['slug']}.json").write_text(json.dumps(detail, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        (folder / "index.html").write_text(server_page(entry, related, detail), encoding="utf-8")
        (out / "badge" / f"{entry['slug']}.svg").write_text(badge_svg(entry), encoding="utf-8")

    api = {"generated": generated, "site": SITE_URL, "categories": CATEGORIES, "servers": [e | {"page": f"{SITE_URL}/s/{e['slug']}/"} for e in servers]}
    (out / "api" / "servers.json").write_text(json.dumps(api, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (out / "llms.txt").write_text(llms_txt(servers), encoding="utf-8")
    (out / "llms-full.txt").write_text(llms_full_txt(servers, generated), encoding="utf-8")
    urls = [f"{SITE_URL}/", f"{SITE_URL}/status/"] + [f"{SITE_URL}/c/{slug}/" for slug, *_ in hubs] + [f"{SITE_URL}/s/{e['slug']}/" for e in servers]
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{esc(u)}</loc><lastmod>{generated[:10]}</lastmod></url>\n" for u in urls)
        + "</urlset>\n",
        encoding="utf-8",
    )
    bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Google-Extended", "Applebot-Extended", "CCBot"]
    robots = "User-agent: *\nAllow: /\n\n# AI crawlers and assistants are welcome. See /llms.txt and /llms-full.txt.\n"
    robots += "".join(f"User-agent: {bot}\nAllow: /\n\n" for bot in bots) + f"Sitemap: {SITE_URL}/sitemap.xml\n"
    (out / "robots.txt").write_text(robots, encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    host = SITE_URL.split("//", 1)[-1].split("/", 1)[0]
    if not host.endswith(".github.io"):  # a custom domain on GitHub Pages needs this file
        (out / "CNAME").write_text(host + "\n", encoding="utf-8")
    (out / "404.html").write_text(
        page("Not found", "This page does not exist.", f'<div class="hero"><h1>Nothing here.</h1><p class="lede"><a href="{SITE_URL}/">Back to the directory</a></p></div>', f"{SITE_URL}/", SITE_URL + "/", index=False),
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
        build_site(args.site, servers, generated, args.status.parent / "tools")
        print(f"{args.site}: {len(servers)} server pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

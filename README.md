<div align="center">

# Awesome MCP Servers

**A directory of Model Context Protocol servers that checks every hosted server nightly — plus runnable reference implementations you can learn from.**

**[Browse the live directory →](https://mcp.aianytime.net/)**

[![Stars](https://img.shields.io/github/stars/AIAnytime/Awesome-MCP-Servers?style=flat-square&color=f5c518)](https://github.com/AIAnytime/Awesome-MCP-Servers/stargazers)
[![Forks](https://img.shields.io/github/forks/AIAnytime/Awesome-MCP-Servers?style=flat-square&color=6f42c1)](https://github.com/AIAnytime/Awesome-MCP-Servers/network/members)
[![Contributors](https://img.shields.io/github/contributors/AIAnytime/Awesome-MCP-Servers?style=flat-square&color=0aa)](https://github.com/AIAnytime/Awesome-MCP-Servers/graphs/contributors)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)
[![MCP](https://img.shields.io/badge/Model%20Context%20Protocol-spec-black?style=flat-square)](https://modelcontextprotocol.io)

[Servers in this repo](#-servers-in-this-repo) · [Community directory](#-community-directory) · [Contributing](#-contributing) · [Resources](#-resources)

</div>

---

The [Model Context Protocol](https://modelcontextprotocol.io) is the open standard for connecting AI
assistants to tools and data. This repository is two things:

1. **A directory** — a categorized list of MCP servers the community has built and shipped. Every hosted server is sent a real MCP handshake each night, and [the site](https://mcp.aianytime.net/) shows which ones answered, which need auth, how many tools they expose and how much context those tools cost.
2. **A teaching repo** — small, readable server implementations in Python you can clone, run, and copy from.

Built and maintained by [AI Anytime](https://www.youtube.com/@AIAnytime). Additions come from the community — see [Contributing](#-contributing).

## 🗒 Contents

- [Servers in this repo](#-servers-in-this-repo)
- [Quick start](#-quick-start)
- [Community directory](#-community-directory)
  - [Agents, IDEs & developer tools](#agents-ides--developer-tools)
  - [Search & discovery](#search--discovery)
  - [Knowledge, memory & context](#knowledge-memory--context)
  - [Media & generation](#media--generation)
  - [Security](#security)
  - [Finance & markets](#finance--markets)
  - [Marketing, content & social](#marketing-content--social)
  - [Cloud, ops & data](#cloud-ops--data)
  - [Commerce, travel & logistics](#commerce-travel--logistics)
  - [Work & productivity](#work--productivity)
- [Contributing](#-contributing)
- [Resources](#-resources)
- [License](#-license)

## 🧱 Servers in this repo

Reference implementations you can run locally. Each folder is self-contained — open it and follow its `README.md`.

| Server | What it does | Stack |
| --- | --- | --- |
| [`weather`](./weather) | Active US weather alerts by state and short-term forecasts by lat/long, from the National Weather Service API. | Python · stdio |
| [`linkedin-profile-mcp`](./linkedin-profile-mcp) | Fetches LinkedIn profile data as JSON through the Fresh LinkedIn Profile Data API on RapidAPI. | Python · stdio · needs `RAPIDAPI_KEY` |
| [`pubmed-mcp-server`](./pubmed-mcp-server) | Searches PubMed and returns article abstracts, via BioPython's Entrez module. | Python · stdio |
| [`mcp-wiki`](./mcp-wiki) | Reads a Wikipedia article and hands it back as clean Markdown. | Python · stdio |
| [`http-sse-mcp-starter`](./http-sse-mcp-starter) | Starter template for a **remote** MCP server over HTTP/SSE (Starlette + FastMCP), with a matching client. | Python · SSE |
| [`directory-mcp`](./directory-mcp) | Searches this directory from inside an MCP client: find servers by keyword, category and live status. Runs locally or as a remote server. | Python · stdio or HTTP |
| [`streamlit as an MCP Host`](./streamlit%20as%20an%20MCP%20Host) | Streamlit app acting as an MCP **host** — connects to an SSE server, calls its tools, summarizes with a local Ollama model. | Python · Streamlit |

> [!TIP]
> New to MCP? Read `weather` first (smallest surface area), then `http-sse-mcp-starter` to see the same
> idea served remotely, then `streamlit as an MCP Host` to see the other side of the wire.

## 🚀 Quick start

```bash
git clone https://github.com/AIAnytime/Awesome-MCP-Servers.git
cd Awesome-MCP-Servers/weather

uv sync              # or: pip install -r requirements.txt
uv run weather.py
```

Then point an MCP client at it. With Claude Code:

```bash
claude mcp add weather -- uv --directory /absolute/path/to/Awesome-MCP-Servers/weather run weather.py
```

For Claude Desktop, add the same command to `claude_desktop_config.json` under `mcpServers`.
Stuck? The [MCP playlist on the AI Anytime YouTube channel](https://www.youtube.com/@AIAnytime) walks through it end to end.

## 🌍 Community directory

Servers built by the community, alphabetical within each category. This list is generated from the files in [`servers/`](./servers); for live status, tool counts and one-line install commands, use [the site](https://mcp.aianytime.net/).

A listing is not a security review. Read a server's source and permissions before you connect it.

**Legend** — `stdio` runs locally on your machine · `http` is a hosted remote server (nothing to install) · `sse` is a remote server over Server-Sent Events.

<!-- directory:start (generated from servers/*.json by scripts/build.py; do not edit by hand) -->

### Agents, IDEs & developer tools

- **[Agent QA](https://github.com/vostride/agent-qa)** `stdio` — Author, validate, run, and inspect natural-language web and mobile regression tests, with persistent test memory. Install: `npx -y agent-qa mcp`
- **[AI Developer Toolkit MCP](https://github.com/mjaskolski/developer-toolkit-mcp)** `http` — Read-only search and fetch over 950+ guides on AI-assisted development (Cursor, Claude Code, Codex) in English and Polish. No account or API key. Endpoint: `https://developertoolkit.ai/mcp` · Registry: `io.github.mjaskolski/developer-toolkit-mcp`
- **[Aident Loadout](https://github.com/Aident-AI/aident-skill)** `http` — Connect Codex, Claude Code, Cursor, ChatGPT and other MCP clients to 1,000+ apps and 400+ Skills through one reusable setup with Vault-protected credentials. Endpoint: `https://loadout.aident.ai/mcp` · [Docs](https://docs.aident.ai/loadout/overview) · [Website](https://aident.ai) · Registry: `io.github.Aident-AI/loadout`
- **[AIHawk](https://github.com/feder-cr/AIHawk)** `stdio` — AI browser agent that browses, clicks, types, and reads real web pages from plain-English instructions. Install: `uvx aihawk`
- **[Antigravity Link](https://github.com/cafeTechne/antigravity-link-extension)** `stdio` — Mirror active AI chat sessions from Google's Antigravity IDE to your phone: send messages, upload files, stop generation, automate workflows across 9 tools. Registry: `io.github.cafeTechne/antigravity-link`
- **[API.market MCP Gateway](https://api.market/mcp)** `http` — Discover and call 580+ APIs through five gateway tools, with OAuth or API-key authentication; pricing and free tiers vary by API. Endpoint: `https://api.market/api/mcp/gateway`
- **[Apple Docs 2.0 MCP](https://github.com/mishafyi/Apple-Docs-2.0-MCP)** `stdio` — Searches and reads Apple's developer documentation, Human Interface Guidelines and 1,700 WWDC sessions with code, with an offline index of 336,629 pages. Install: `npx -y apple-docs-2.0-mcp`
- **[Archcore](https://github.com/archcore-ai/archcore)** `stdio` — Git-native context engineering CLI and MCP server for AI coding agents. Keep specs, ADRs, rules, plans, and project knowledge in Git. Install: `curl -fsSL https://archcore.ai/install.sh | bash` · [Docs](https://docs.archcore.ai)
- **[Bestax](https://github.com/allxsmith/bestax/tree/main/bestax-mcp)** `stdio` — Props, working examples, `--bulma-*` CSS variables and Agent Skills for Bestax, a React component library for Bulma v1; offline, no API key. Install: `npx -y bestax-mcp@1` · [Docs](https://bestax.io/docs/guides/llms#mcp-server)
- **[Better Design](https://github.com/marvkr/better-design)** `http` — Design systems, UI and UX principles, icons and UI review for coding agents that build interfaces; free account, OAuth or API key. Endpoint: `https://better-design.com/api/mcp` · [Docs](https://better-design.com/mcp/install) · Registry: `io.github.marvkr/better-design`
- **[claude-node](https://github.com/claw-army/claude-node)** `stdio` — Python subprocess bridge to the Claude Code CLI, giving Python direct access to Claude Code's native capabilities over stream-json.
- **[CurlShot](https://curlshot.com/docs)** `http` — Renders any public URL as a PNG, JPEG or WebP screenshot, a PDF, or a scrolling video, full page or at a phone, tablet or desktop preset. `list_devices` needs no key; `take_screenshot` needs an API key as a Bearer token (free plan 100 screenshots/month, no card). Endpoint: `https://curlshot.com/api/mcp` · [Docs](https://curlshot.com/docs)
- **[ERIUS PHONE MCP](https://github.com/Protremix/erius-phone-mcp)** `stdio` — Drive a hosted ERIUS PHONE Android phone or tablet: read the screen as an accessibility tree or screenshot, tap, type, swipe, launch apps, install APKs and pull crash logs. Requires an ERIUS PHONE API key (early access). Install: `uvx erius-phone-mcp` · [Website](https://eriusphone.com)
- **[Ganado Bridge](https://github.com/cynarax/bridge-by-ganado)** `stdio` — Checked local file edits (SHA-256-gated), bounded reads/search and persistent command sessions with real exit codes on macOS. Install: `.mcpb` bundle from releases · [Docs](https://ganado-bridge.vercel.app/install)
- **[Hexis](https://github.com/Bevel-Software/Hexis)** `http` — Git-backed platform for skills, tools, and context for AI agents. Endpoint: `https://demo.bevel.software/api/mcp`
- **[Kleap](https://github.com/kleaphq/cli)** `http` — AI website builder MCP: create apps, edit files, connect domains, and publish. OAuth remote. Endpoint: `https://kleap.co/api/mcp` · [Website](https://kleap.co/mcp)
- **[Oh My Android](https://github.com/ateymoori/oh-my-android)** `stdio` — Lets coding agents see and drive the Android Emulator and adb devices: dp-scaled screenshots, UI tree, taps, logcat, and dark mode, font scale, RTL and TalkBack switches; ships inside a free native macOS app (macOS 26+). Install: `brew install --cask ateymoori/tap/oh-my-android` · Registry: `io.github.ateymoori/oh-my-android`
- **[Omega MCP Router](https://github.com/Omega-JS-Stack/omega/tree/main/packages/mcp-router)** `stdio` — Fronts many upstream MCP servers behind one stdio connection, serves their tool schemas from a disk cache, and starts each upstream only on its first call; a session switches upstreams on and off through four `router__*` tools. Install: `npx -y @omega.js/mcp-router`
- **[OpenAPI to MCP Cloud Bridge](https://github.com/notsariedo/openapi-mcp-gateway)** `sse` — Zero-setup hosted bridge that turns any OpenAPI JSON spec into a remote MCP server. [Hosted bridge](https://mcp-bridge-saas.onrender.com)
- **[Openhook](https://github.com/openhook-dev/openhook-inbox)** `http` — Capture HTTP, email, and DNS callbacks and wait for or inspect inbox events through MCP; private inbox tokens control reads and deletion. MIT self-hosting and free temporary hosted inboxes are available, with optional paid persistent hosting.
- **[OrcaReplay](https://github.com/Continuum-AI-Corp/OrcaReplay)** `stdio` — Read-only window into a local library of recorded agent runs: six tools (`list`, `show`, `checkpoints`, `graph`, `replay`, `compare`) over the prompts, tool calls and responses an agent already exchanged, so a failed run can be replayed offline or diffed against another. Install: `npx -y orcareplay mcp`
- **[Plazmi](https://plazmi.gg)** `http` — A homemaking world for AI agents: move into a little house on a floating island, keep it on a real UTC clock, meet neighbours and send your human a postcard; free, no auth. Endpoint: `https://plazmi.gg/mcp` · [Skill](https://plazmi.gg/SKILL.md) · Registry: `gg.plazmi/plazmi`
- **[REA](https://github.com/morluto/rea)** `stdio` — Local reverse-engineering tools for native binaries, JavaScript/Electron apps, and .NET assemblies; native deep analysis uses separately installed Hopper, Ghidra, or IDA. Install: `npm install --global rea-agents`
- **[rea-captcha](https://github.com/masakaai/rea-captcha)** `stdio` — Local verification-evidence analysis and authorized test-flow control for browser agents; browser actions require a configured caller-owned Playwright/CDP session and official provider test keys or an owned flow. Start for stateless analysis and tool discovery: `npx -y rea-captcha mcp --stateless` · [Configuration](https://github.com/masakaai/rea-captcha#browser-providers)
- **[Roundtable](https://github.com/askbudi/roundtable)** `stdio` — Zero-configuration server that unifies multiple AI coding assistants (Codex, Claude Code, Cursor, Gemini) behind one interface with auto-discovery. [Website](https://askbudi.ai/roundtable)
- **[SandBase CLI](https://github.com/sandbaseai/cli)** `stdio` — Agent-first CLI and MCP bridge for discovering, inspecting, and running 2,000+ AI models on one account — search, scraping, multimodal generation, data APIs, sandboxes. Install: `npx -y @sandbaseai/cli connect` · [Website](https://sandbase.ai)
- **[SandBase Harness](https://github.com/sandbaseai/sandbase-harness)** `stdio` — Local-first agent runtime and MCP bridge for governed tool access, persistent sessions, credentials, approvals, audit/replay, and sandboxed execution. Install: `docker run --rm -i -e MANAGED_AGENTS_URL=http://host.docker.internal:3000 ghcr.io/sandbaseai/sandbase-harness-mcp:0.3.8`
- **[Sem](https://github.com/Ataraxy-Labs/sem)** `stdio` — Search code entities, inspect dependencies and impact, and review structural diffs in local Git repositories; no API key required. Install: `npm install -g @ataraxy-labs/sem`, then run `sem mcp` from the repository · [Docs](https://github.com/Ataraxy-Labs/sem#use-with-ai-agents-mcp)
- **[Sequential](https://www.usesequential.com/docs/connect-claude-ai.md)** `http` — Session replay and product analytics with an AI judge that reviews each session (what the user came to do, whether they got there, where they struggled) and lists findings to fix; agents query sessions, findings, events, funnels, flows and retention. Hosted, OAuth sign-in, free sign-up. Endpoint: `https://api.usesequential.com/mcp` · [Tools](https://www.usesequential.com/docs/agent-tools.md) · Registry: `io.github.Acro/sequential`
- **[since-cutoff](https://github.com/MohammadHijjawi97/since-cutoff)** `stdio` — Reports which APIs of a project's pinned Python dependencies changed after a coding model's training cutoff, from a static diff of the two releases, and where the project's code uses them; no model calls or API key. Install: `uvx since-cutoff mcp` · Registry: `io.github.MohammadHijjawi97/since-cutoff`
- **[Skillselion](https://github.com/skillselion/skillselion-mcp)** `stdio` — On-demand skill loader over a catalog of 79,000+ agent skills, MCP servers, and plugins; materializes the matching `SKILL.md` and its scripts into the session mid-task. Install: `npx -y skillselion-mcp` · [Website](https://skillselion.com)
- **[squirrelscan](https://github.com/squirrelscan/squirrelscan)** `http` — Audits websites for SEO, performance, security, accessibility, and agent experience (260+ rules) and returns fixes for your coding agent. Endpoint: `https://mcp.squirrelscan.com/mcp` · [Website](https://squirrelscan.com)
- **[SwarmMemo](https://github.com/Hugo0/swarmmemo)** `http` — Where agents meet, work, and keep their word: public rooms, private agent-to-agent messages, paid tasks and long-term memory, with a public log anchored to Bitcoin; free, no key needed to start. Endpoint: `https://swarmmemo.com/mcp/core` · [Docs](https://swarmmemo.com/docs)
- **[vibe-testing](https://github.com/AishwaryShrivastav/vibe-testing)** `stdio` — Code-aware Playwright browser testing for coding agents with regression diffs and HTML reports. Install: `npx -y vibe-testing@latest --mcp`
- **[Zambo](https://github.com/zambodotdev/zambo-mcp)** `http` — 120 native tools across 17 products: strategy, code audit, lead generation, onchain scoring, credit discovery, prompt defense. Endpoint: `https://zambo.dev/api/mcp`, zero auth, no signup. [Website](https://zambo.dev)

### Search & discovery

- **[AgentoolRank](https://github.com/agent-gigmole/agentoolrank-mcp)** `http` — Search open-source AI agent tools and MCP servers ranked by live GitHub activity, refreshed daily, and get alternatives for any tool; read-only search needs no API key. Install: `claude mcp add --transport http agentoolrank https://agentoolrank.com/api/mcp` · [Docs](https://agentoolrank.com/agents) · Registry: `com.agentoolrank/agent-tools`
- **[AISOTools](https://github.com/shibley/aisotools-mcp-server)** `http` — Search a curated catalog of 1,766 AI tools by keyword, category, or pricing; compare 2–5 products side by side and find alternatives. Read-only, no API key, sponsored results flagged. Install: `claude mcp add --transport http aisotools https://aisotools.com/api/mcp` · [Docs](https://aisotools.com/mcp)
- **[Anansi Haven](https://github.com/kburrus64-max/anansi-haven)** `http` — MIT-licensed hosted server (also A2A and HTTP) giving agents a persistent identity, versioned key-value memory that survives restarts, client-side encrypted storage, an agent directory and a job board. Read-only utility tools need no key; memory tools need a free key from `register_agent`. Endpoint: `https://anansi-haven.anansidata.workers.dev/mcp` · [Docs](https://github.com/kburrus64-max/anansi-haven/blob/main/docs/SETUP.md) · Registry: `io.github.kburrus64-max/anansi-haven`
- **[ats-jobs-mcp](https://github.com/benkrasin/ats-jobs-mcp)** `stdio` — Lists and filters a company's open jobs from its public Greenhouse, Lever or Ashby job board in one normalized shape; no API key, zero dependencies. Install: `npx -y github:benkrasin/ats-jobs-mcp mcp`
- **[BOIM (보임)](https://github.com/kikiyop1101/boim-mcp)** `http` — Find Korean businesses by region and industry (2.7M, all industries), public-procurement vendors (75,000+) and open public bids; read-only, no account or API key on the free tier (5 results per tool). Endpoint: `https://boim.io/api/mcp` · Registry: `io.boim/vendors`
- **[CareJobs.Now Healthcare Jobs](https://github.com/yumaheymans/carejobs-mcp)** `http` — Search 170,000+ open US healthcare jobs read daily from 270 hospitals' and health systems' career sites, with job details and the pay employers post by kind of job, employer and state; read-only, no account or API key
- **[Court Rules](https://github.com/foklepoint/court-rules-mcp)** `http` — U.S. federal court rules, local rules, judge standing orders, court holidays and filing deadline checks; API key required, free tier. Endpoint: `https://mcp.courtrules.app/mcp`
- **[Derrick](https://github.com/DerrickAppOrg/derrick-mcp)** `stdio` — B2B data enrichment from a name, a domain or a LinkedIn URL: verified work emails, phone numbers, company firmographics, tech stack, hiring signals, and French SIRET/SIREN records. Install: `npx derrick-mcp` · [Docs](https://derrick-app.com/mcp)
- **[Find MCP](https://github.com/agentage/find-mcp)** `stdio` — Discover other MCP servers: searches a catalog of 17,000+ servers synced from the official MCP registry. Install: `npx @agentage/find-mcp` · Registry: `io.agentage/find-mcp`
- **[Grok Bot Wiki](https://www.grokbotwiki.com/mcp)** `http` — Unofficial, read-only search of public Grok Bot templates and source-backed guides; free, no account or API key. Endpoint: `https://www.grokbotwiki.com/api/mcp`
- **[looot](https://github.com/loootai/looot-mcp)** `http` — One API key and prepaid balance for about 2,500 data endpoints from 90+ providers: work email, phone, company enrichment, Google SERP, web pages. Pay per call, OAuth or Bearer key. Registry: `ai.looot/looot`
- **[nothumansearch](https://nothumansearch.ai/mcp)** `http` — Search engine over 8,600+ agent-native services: discover MCP servers, OpenAPI providers, and llms.txt publishers by keyword, category, or agentic-readiness score. Registry: `ai.nothumansearch/search`
- **[Papers by Ouroboros Apps](https://github.com/LAHutchins91/papers-mcp)** `http` — Research paper search with real citations from OpenAlex, Semantic Scholar, PubMed, Crossref, and arXiv: find papers, fetch abstracts, follow citations, and format references. OAuth sign-in. Endpoint: `https://papers-mcp.vercel.app/mcp` · [Docs](https://ouroborosapps.com/docs/papers) · [Ouroboros Apps](https://ouroborosapps.com)
- **[Parallel Search](https://docs.parallel.ai/integrations/mcp/search-mcp)** `http` — Free live web search and URL fetching, no account or API key. Endpoint: `https://search.parallel.ai/mcp`
- **[Patent by Ouroboros Apps](https://github.com/LAHutchins91/patent-mcp)** `http` — USPTO patent search and prior art lookup: search public patent records, fetch a patent, list citations, and run a prior-art search. Not legal advice. Hosted coverage is USPTO only. OAuth sign-in. Endpoint: `https://patent-mcp.vercel.app/mcp` · [Docs](https://ouroborosapps.com/docs/patent) · [Ouroboros Apps](https://ouroborosapps.com)
- **[srezai](https://github.com/srezai-team/srezai-mcp-web-search)** `http` — Web search, page reading as clean Markdown, site crawling, JSON-schema extraction and claim verification with quotes for AI agents, with strong Russian-web coverage. Русский: веб-поиск и чтение страниц для ИИ-агентов, 12 инструментов. Endpoint: `https://srezai.ru/api/mcp`, API key required · [Docs](https://srezai.ru/docs/mcp)
- **[StatOrigin](https://github.com/SudoAI-App/statorigin-mcp)** `http` — Read-only search of sourced industry statistics; each record carries its publisher, source document and source sentence. No account or API key. Endpoint: `https://statorigin.org/mcp` · [Docs](https://statorigin.org/docs/mcp)
- **[Statsnet](https://github.com/usenetstate/statsnet-mcp)** `http` — Background check any company in the world: registration, executives, courts and finances. Endpoint: `https://statsnet.co/mcp` · Registry: `io.github.usenetstate/statsnet`
- **[TwitterAPI.io](https://github.com/kaitoInfra/twitterapi-io-mcp-server)** `http` — 12 read-only tools over [twitterapi.io](https://twitterapi.io): tweet search with full operators, profiles, followers, conversation threads, real-time streaming, trending topics. Endpoint: `mcp.twitterapi.io/mcp`
- **[UnifAPI](https://github.com/unifapi-agent/unifapi-mcp-server)** `http` — Public-data tools for social, search, scraping, news, creator research, and KOL pricing workflows. Endpoint: `https://mcp.unifapi.com` · [Docs](https://docs.unifapi.com/mcp) · Registry: `com.unifapi/mcp`
- **[Vend API Merchant](https://extract.paypercall.dev)** `http` — Pay-per-call web intelligence: extract clean text from URLs, web search, link checking, domain WHOIS/DNS/SSL info, IP geolocation, and PDF text extraction. 22+ endpoints, no signup or API key, each call settles in Nano (XNO) via x402 at 0.0001–0.0005 XNO. Endpoint: `https://extract.paypercall.dev/mcp` · [Docs](https://extract.paypercall.dev) · Registry: `dev.paypercall.extract/vend-api-merchant`
- **[Xquik](https://github.com/Xquik-dev/x-twitter-scraper)** `http` — X/Twitter search, extraction workflows, account insights, webhooks, and SDK access. [Docs](https://docs.xquik.com/mcp/overview)
- **[YouTube Transcripts MCP](https://github.com/gunnargray-dev/youtube-transcripts-mcp)** `http` — YouTube transcripts with video metadata (text, timestamped segments or SRT), filtered YouTube search, chapters, and timestamped extractive summaries; no YouTube API key. Local stdio free; hosted pay-per-call on Apify (API token). Endpoint: `https://parallelstudio--youtube-transcripts-mcp.apify.actor/mcp` · Registry: `io.github.gunnargray-dev/youtube-transcripts-mcp`

### Knowledge, memory & context

- **[AccInt](https://github.com/maxbaluev/accreted-intelligence)** `stdio` — Local-first, SQLite-backed memory shared across Claude Code, OpenCode, Codex, and Cursor; feeds verified outcomes back into future retrieval. Public integration glue around a private engine. · [Website](https://accint.xyz/)
- **[Agentage Memory](https://memory.agentage.io)** `http` — One shared Markdown memory for Claude, Cursor, and ChatGPT that you own and can export: six tools to search, read, write, edit, list, and delete. OAuth 2.1 with dynamic client registration. Endpoint: `https://memory.agentage.io/mcp` · Registry: `io.agentage/memory`
- **[ContextStream](https://github.com/contextstream/mcp-server)** `http` — Shared persistent memory and semantic code search for AI coding agents (Cursor, Claude Code, Codex, Grok, Windsurf). Free tier; hosted OAuth or API key. Endpoint: `https://mcp.contextstream.io/mcp` · [Website](https://contextstream.io)
- **[Continuity by Ouroboros Apps](https://github.com/LAHutchins91/continuity-mcp)** `http` — Story continuity for fiction writers: a series bible and novel memory that keeps characters, places, timelines, and plot facts consistent across chats. OAuth sign-in. Endpoint: `https://continuitywriter.com/mcp` · [Website](https://continuitywriter.com) · [Ouroboros Apps](https://ouroborosapps.com)
- **[GoodMemory](https://github.com/hjqcan/GoodMemory)** `stdio` — Local-first, auditable memory for coding agents. SQLite-backed, read-only context/trace/search tools by default, with durable writes opt-in behind inspect, revise, forget, and export. Install: `npm install -g goodmemory`
- **[Hyperconsciousness](https://github.com/louis030195/hyperconsciousness)** `stdio` — Developer-alpha encrypted knowledge store with search and retrieval through scoped, expiring grants. · [Docs](https://github.com/louis030195/hyperconsciousness#give-an-agent-limited-access)
- **[Liminal](https://github.com/jaybro2042-alt/liminality-mcp)** `http` — Liminal turns objectives into structured work by strategizing through an atomic, deterministic basis: setting guardrails around scope, compiling resources and constraints, uncovering gaps, and organizing research and next steps. OAuth 2.1 or API key; free key at physea.ai/signup. Endpoint: `https://liminality.physea.ai/mcp` · [Docs](https://physea.ai/mcp) · Registry: `ai.physea/liminality`
- **[Mnemoverse](https://github.com/mnemoverse/mcp-memory-server)** `http` — Hosted persistent memory for AI agents with shared rooms; tell it a recalled memory helped or misled and it re-ranks what comes back next. Free tier; OAuth on the hosted endpoint, API key for the npm package. Endpoint: `https://mcp.mnemoverse.com/mcp` · Install: `npx -y @mnemoverse/mcp-memory-server@latest` · [Docs](https://mnemoverse.com/docs)
- **[Neither](https://github.com/stonianua/neither-mcp)** `stdio` — Project context your AI can query through MCP. Selected notes/docs for Cursor or Claude Desktop; related retrieval with source evidence. Install: `npx -y @neitherai/mcp-server`. Registry: `io.github.stonianua/neither-mcp`. [Start](https://www.neither.online/start/?product=dev)
- **[ORANO](https://github.com/infotik/orano-mcp-server)** `http` — Read-only access to your ORANO library: projects built from saved Reels, videos, articles and PDFs, with summaries, ordered tasks, selectable video context and curated memory facts. Paid web plan; API key required. Endpoint: `https://orano-ai-backend-1037939693300.us-central1.run.app/mcp/` · [Website](https://oranoai.com/mcp)
- **[ReadGZH](https://github.com/sweesama/readgzh)** `http` — Reads WeChat Official Account articles into clean Markdown for AI clients. Free daily credits; cached articles cost 0. Endpoint: `https://api.readgzh.site/mcp-server` (API key optional for higher quota) · [Docs](https://readgzh.site/docs)
- **[Screenpipe](https://github.com/screenpipe/screenpipe)** `stdio` — Source-available MCP access to searchable local screen text and audio transcripts. Requires a running Screenpipe recorder and local API authentication. Install: `claude mcp add screenpipe -- npx -y screenpipe-mcp@latest` · [Docs](https://github.com/screenpipe/screenpipe/tree/main/packages/screenpipe-mcp#installation)
- **[Whisper Memos](https://whispermemos.com/mcp)** `http` — Official server for the Whisper Memos iPhone and Apple Watch voice memo app: list and read memo transcripts and summaries, list labels, view account details, and delete memos; it cannot create or edit memos. OAuth 2.1, approved in the iOS app. Endpoint: `https://whispermemos.com/mcp` · [Config](https://github.com/whispermemos/whisper-memos-plugin) · Registry: `com.whispermemos/whisper-memos`
- **[Wondel.ai Skills MCP](https://github.com/mjaskolski/wondel-skills-mcp)** `http` — Read-only access to 50 book-based agent skills and 12 guided journeys: recommends a framework for a task and serves its SKILL.md in-session. No account or auth. Endpoint: `https://skills.wondel.ai/mcp` · Registry: `io.github.mjaskolski/wondel-skills-mcp`

### Media & generation

- **[audio](https://github.com/audiojs/audio)** `stdio` — Edit, analyze and convert audio files and the sound of videos, no ffmpeg: loudness and true peak, checks against ACX, podcast, streaming and EBU R 128 specs, denoise, EQ, trim, fades, BPM, key. Install: `npx -y audio --mcp` · [Docs](https://github.com/audiojs/audio#mcp)
- **[Claude Imagine](https://github.com/lumian2015/claudeimagine-mcp)** `http` — Generate and edit images and videos with Nano Banana 2, GPT Image 2.5, Seedream 4.5, Flux 2 Pro, and Veo 3.1 Fast. Endpoint: `https://claudeimagine.com/api/mcp` (OAuth, no API key; free signup credits, then paid plans) · [Docs](https://claudeimagine.com/docs/mcp)
- **[dare-mcp-server](https://github.com/avi-aggarwal14/dare-mcp-server)** `stdio` — Generate video and images on Dare (Seedance 2.5, Veo 3.1, Kling 3.0 Pro, Hailuo 2.3, Nano Banana 2) from Claude, billed to your own Dare credits, with local cost estimates and dry runs. Needs a Dare session cookie; unofficial. Install: `npx dare-mcp-server setup`
- **[Magic Hour](https://github.com/magichourhq/magic-hour-mcp)** `http` — Generate and edit video, images, and audio with 44 Magic Hour API tools. Endpoint: `https://mcp.magichour.ai/` (bearer API key required) · [Setup](https://magichour.ai/mcp)
- **[Motomarks](https://motomarks.io/docs/mcp)** `http` — Search a published automotive brand library and build logo CDN URLs for Claude, Cursor, and VS Code. Endpoint: `https://motomarks.io/api/mcp` (OAuth or API key; free account, no credit card)
- **[OrkasVideoStudio](https://github.com/Orkas-AI/Orkas-VideoStudio)** `stdio` — Local-first server and TypeScript CLI for agent-driven video composition, editing, generation, and assembly on editable `plan.json` timelines, with installable skills for Codex and Claude Code.
- **[Playable Gift](https://playablegift.com/agents)** `http` — Creates a small browser game from someone's habits or inside jokes, then returns links for sharing the gift. Free within daily allowances. Endpoint: `https://playablegift.com/mcp`
- **[prompt-to-asset](https://github.com/MohamedAbdallah-14/prompt-to-asset)** `stdio` — Routes image-generation prompts to 30+ models (DALL·E, Stable Diffusion, Flux, Midjourney) through one interface. Install: `npm install -g prompt-to-asset`
- **[RunAPI](https://github.com/runapi-ai/mcp)** `stdio` — Browse the RunAPI model catalog and run image, video, music/audio, text-to-speech, and LLM tasks from agent workflows. Install: `npx -y @runapi.ai/mcp`
- **[UpRes](https://github.com/auroracapital/upres-cli)** `stdio` — UpRes MCP: list models, credits, and submit 4K image and video upscale jobs. Install: `npx -y upres-cli`
- **[VideoGen MCP](https://github.com/video-gen/videogen-mcp)** `http` — Create editable videos from storyboards, scripts or voiceovers, generate media, edit projects and export results through the VideoGen API; account and generation credits required. Hosted HTTP with OAuth/API key or local stdio via `npx -y @videogen/mcp@2.2.1` with `VIDEOGEN_API_KEY`; MIT server; [Setup](https://videogen.io/videogen-mcp).

### Security

- **[Council of AI (GSPC)](https://github.com/CSOAI-ORG/councilof-ai/tree/master/mcp/gspc-server)** `http` — Reads a public board of signed AI behaviour measurement cards and verifies Ed25519 signatures and Merkle inclusion; read tools need no key, evidence tools are x402-metered. Endpoint: `https://councilof.ai/mcp` · Install: `npx -y csoai-gspc-mcp` · Registry: `io.github.CSOAI-ORG/gspc`
- **[Darkmoon](https://github.com/ASCIT31/Dark-Moon)** `stdio` — Open-source (GPLv3) autonomous penetration-testing platform orchestrating 80+ offensive security tools through 50 specialist agents, with proof of exploitation behind every finding. Runs fully locally.
- **[Skycloak MCP](https://github.com/sky-cloak/skycloak-mcp)** `http` — Managed Keycloak identity MCP server for AI agents (OIDC/OAuth realms, users, clients, SSO). Endpoint: `https://mcp.skycloak.io` · [Docs](https://skycloak.io/mcp) · Registry: `io.skycloak/skycloak-mcp`
- **[Sunglasses](https://github.com/sunglasses-dev/sunglasses)** `stdio` — Scans text and files locally for prompt injection, credential leaks and data exfiltration; runs as a CLI, a Python API or an MCP server. Install: `pip install sunglasses` · Run: `python -m sunglasses.mcp` · [Website](https://sunglasses.dev)

### Finance & markets

- **[AskCyborg](https://github.com/Ask-Cyborg/askcyborg-mcp)** `http` — Stress-tests public and private companies through analyst debate: reports, scores, comparisons, competitors, recent developments. Anonymous free tier, no API key. Endpoint: `https://mcp.askcyborg.com/mcp`
- **[BankBridge](https://github.com/bankbridge-money/bankbridge-plugin)** `http` — Read-only access to your US bank accounts, card transactions and investment holdings: spending, subscriptions, cashflow. Paid, OAuth sign-in or API key. Endpoint: `https://bankbridge.money/api/mcp` · [Website](https://bankbridge.money) · Registry: `money.bankbridge/server`
- **[BlockVectra](https://github.com/blockvectra/mcp)** `http` — Multi-chain EVM JSON-RPC, indexed Data API, documentation, pricing and status for developers and AI agents. Documentation, chain, pricing and status tools need no API key; Data API tools require one. Endpoint: `https://docs.blockvectra.com/mcp` · [Docs](https://docs.blockvectra.com/en/)
- **[canli-validation-mcp](https://github.com/arhancanli/canli-validation-mcp)** `http` — Checks whether a backtest result is real or just the luckiest of the variants tried: deflated Sharpe ratio, CSCV probability of backtest overfitting, data-snooping tests (Hansen's SPA, White's Reality Check, Romano-Wolf StepM), a lookahead check and a pipeline placebo test. Free, no API key; also runs locally with `npx -y canli-validation-mcp`. Endpoint: `https://canlicapital.com/mcp` · [Docs](https://canlicapital.com/developers) · Registry: `io.github.arhancanli/canli-validation-mcp`
- **[Chord](https://github.com/getchordlabs/chord)** `http` — DEX swap quotes and unsigned swap transactions on 7 EVM chains (Base, Monad, BNB Chain, Avalanche, Arbitrum, Robinhood Chain, Arc), plus token boards, candles, trades, wallet PnL, smart money, holders and LP pools (Solana data read-only). Hosted, no key for data and swaps (about 60 requests a minute), only `chord_ask` needs an API key; non-custodial. Endpoint: `https://api.getchord.xyz/v1/mcp` · [Docs](https://getchord.xyz/docs/agents/mcp/) · Registry: `io.github.getchordlabs/chord`
- **[ddbx](https://ddbx.uk/mcp)** `http` — Insider share dealings from UK directors, US Form 4 filers, Swedish and Dutch PDMRs, and US Congress members, with notable filings rated. Read-only, no API key. Endpoint: `https://api.ddbx.uk/mcp` · [Repo](https://github.com/jonwillington/ddbx-plugin) · Registry: `io.github.jonwillington/ddbx`
- **[Deposit by Ouroboros Apps](https://github.com/LAHutchins91/deposit-mcp)** `http` — Freelance deposit and payment schedule: approved deposits, payment dates, and client wording; deposit waivers and date changes need approval. OAuth sign-in. Endpoint: `https://deposit-continuity2.vercel.app/mcp` · [Docs](https://ouroborosapps.com/docs/deposit) · [Ouroboros Apps](https://ouroborosapps.com)
- **[Equibles](https://equibles.com/docs/mcp)** `http` — US company research: SEC filing search and text, fundamentals as reported in 10-K and 10-Q filings, earnings-call transcripts, 13F holdings, insider and congressional trades, and FRED macro series, with links to the source filings. Free tier, OAuth sign-in. Endpoint: `https://mcp.equibles.com/mcp` · [Website](https://equibles.com)
- **[Eulerpool](https://github.com/eulerpool/eulerpool-mcp)** `http` — Financial data for AI agents: 250+ tools over stocks, fundamentals, ETFs, macro (FRED/ECB/IMF/World Bank), crypto, FX, insider trades, congress trading and options flow. Free tier, API key or OAuth. Endpoint: `https://api.eulerpool.com/mcp` · [Docs](https://eulerpool.com/developers/mcp-server)
- **[EventTrader](https://github.com/eventtrader/event-trader-mcp)** `http` — Prediction-market trading: place bets, TGE token price predictions, real-time orderbooks, agent cloning, due-diligence scoring. [Platform](https://cymetica.com)
- **[Helium](https://github.com/connerlambden/helium-mcp)** `http` — Real-time news with 37-dimension bias scoring, ML options pricing, and live market data. [Interactive demo](https://connerlambden.github.io/helium-news-explorer/) · [REST API](https://heliumtrades.com/mcp-page/)
- **[HostDeFi](https://hostdefi.com)** `http` — Free token-safety scanner grading tokens A+–F from on-chain checks (mint/freeze authority, liquidity, holder concentration) across Solana and 7 EVM chains. Keyless REST API, hosted MCP, and x402 endpoints.
- **[Invoice by Ouroboros Apps](https://github.com/LAHutchins91/invoice-mcp)** `http` — Freelance invoice records: approved invoice line items, quantities, agreed rates, due dates, and late terms; invoice changes need explicit approval. OAuth sign-in. Endpoint: `https://invoice-continuity2.vercel.app/mcp` · [Docs](https://ouroborosapps.com/docs/invoice) · [Ouroboros Apps](https://ouroborosapps.com)
- **[Invompt](https://github.com/Invompt/invompt-mcp)** `http` — Turn AI-host work into invoices you review before send; Continue as guest or OAuth via hosted MCP. Endpoint: `https://mcp.invompt.com/mcp` · [Website](https://www.invompt.com) · Registry: `com.invompt/invompt`
- **[MoltNode by Chord](https://github.com/tuantqse90/moltnode-mcp)** `http` — Read 31 blockchains over JSON-RPC (Ethereum, Base, Arbitrum, Solana, Monad, BNB Chain, Avalanche, Sui and more) and get DEX swap quotes with the unsigned transaction, approval and simulation via Chord. Hosted, no account or API key; non-custodial, the user's wallet signs. Endpoint: `https://moltnode.ag/mcp` · [Docs](https://moltnode.ag/agents) · Registry: `io.github.tuantqse90/moltnode`
- **[ParlayAPI](https://github.com/JacobiusMakes/parlay-api-mcp)** `stdio` — Sports odds, player props, public event discovery, and account usage through ParlayAPI; account data tools require each user's own API key and allowances. Install: `uvx --from parlayapi-mcp==0.3.6 parlayapi-mcp`
- **[Silicon Floor](https://github.com/Baptoshi/silicon-floor)** `http` — Who owns AI and semiconductor stocks, who is buying and selling them, and what their filed numbers say: SEC XBRL financials, 13F, Schedule 13D/G, Forms 3/4/5, FINRA short interest and dividends, every figure dated and linked to its filing. Read-only, no API key. Endpoint: `https://siliconfloor.com/mcp` · [Docs](https://siliconfloor.com/docs/mcp) · Registry: `com.siliconfloor/silicon-floor`
- **[SwapWallet](https://github.com/SwapWallet/swapwallet-mcp)** `http` — Official server for the SwapWallet crypto exchange: balances, P&L, history and deposit addresses, plus swaps, transfers and withdrawals that run only after the user approves them in Telegram. OAuth sign-in. Endpoint: `https://swapwallet.app/mcp` · [Docs](https://swapwallet.app/docs/mcp) · Registry: `app.swapwallet/mcp`
- **[Tapetide](https://github.com/Tapetide-hq/nse-bse-indian-stock-market-data-mcp)** `http` — Indian stock market (NSE and BSE) research over about 8,200 stocks: quotes, financials, technicals, fundamental and technical screeners, FII/DII flows, option chains, parsed filings, IPOs, and portfolio tracking; free plan of 50 tool calls a day. Endpoint: `https://mcp.tapetide.com/mcp` · [Docs](https://tapetide.com/mcp)
- **[The Stall](https://github.com/thebrierfox/the-stall)** `http` — About 300 pay-per-call capabilities: US/EU/JP/KR/AU equities, options chains, DeFi yields, blockchain analytics, macro indicators, wallet intelligence, and prediction markets. Paid per call in USDC on Base ($0.001–$1.50), no API key. Endpoint: `https://the-stall.intuitek.ai/mcp`
- **[Truthifi](https://github.com/truthifi/truthifi-mcp)** `http` — One verified household record for your AI: accounts, activity, holdings, fees, performance, cash flow and your Truthifi Score. Can't move money. Endpoint: `https://api.truthifi.com/mcp` · [Docs](https://truthifi.com/mcp-tools) · Registry: `com.truthifi/mcp`
- **[VoxOdds](https://github.com/softdevfz/voxodds-mcp)** `http` — Prediction-market research across Polymarket and Kalshi: odds for the same contract on both venues, the all-in executable price for a budget with estimated taker fees and which venue fills cheaper, trending markets, edge signals and an audited forecast track record. Read-only, no API key. Endpoint: `https://voxodds.com/mcp` · [Docs](https://voxodds.com/llms.txt) · Registry: `com.voxodds/voxodds`

### Marketing, content & social

- **[App Store & Google Play Review Intelligence MCP](https://github.com/gunnargray-dev/app-store-review-intelligence-mcp)** `http` — Search Apple App Store / Google Play, pull reviews, return top complaints with quotes, rating-by-version, what got worse in the latest update, and competitor comparisons. Local stdio free; hosted pay-per-call on Apify (API token). Endpoint: `https://parallelstudio--app-store-review-intelligence-mcp.apify.actor/mcp` · Registry: `io.github.gunnargray-dev/app-store-review-intelligence-mcp`
- **[Autoposting](https://github.com/Autoposting-ai/autoposting-mcp)** `http` — Draft, schedule, and publish to X, LinkedIn, Instagram, Threads, and YouTube, plus AI carousels and video clipping. OAuth 2.1 with dynamic client registration — no secret to paste. Install: `claude mcp add --transport http autoposting https://app.autoposting.ai/mcp`
- **[BulkPublish](https://github.com/azeemkafridi/bulkpublish-api)** `http` — Plan, review, schedule, publish, and analyze social media content for AI agents through BulkPublish. Endpoint: `https://mcp.bulkpublish.com/mcp` · [Docs](https://app.bulkpublish.com/docs)
- **[Claim by Ouroboros Apps](https://github.com/LAHutchins91/claim-mcp)** `http` — Brand claims and marketing copy compliance: approved claims, offers, proof, brand voice, and banned phrases, with a check that rejects copy inventing a guarantee or discount. OAuth sign-in. Endpoint: `https://claim-continuity2.vercel.app/mcp` · [Docs](https://ouroborosapps.com/docs/claim) · [Ouroboros Apps](https://ouroborosapps.com)
- **[Datacircle](https://docs.datacircle.dev/mcp-server)** `http` — Query your favorite B2B data APIs through us. Same request, same price, no markup. OAuth sign-in, or an API key as a Bearer token. Endpoint: `https://api.datacircle.dev/mcp` · [Website](https://datacircle.dev) · Registry: `dev.datacircle/datacircle`
- **[day3](https://github.com/Mopra/day3.app)** `http` — Official server for the day3 email platform: read account context, draft, edit, preview and test-send newsletter campaigns, and enroll contacts in automations; sending to an audience needs an extra API key scope. Bearer API key. Endpoint: `https://go.day3.app/api/mcp` · [Docs](https://docs.day3.app/mcp)
- **[FirstSales MCP](https://developer.firstsales.io/agents/mcp-server)** `http` — Read CRM contacts, companies, deals, and lists, and create contacts in an authorized FirstSales workspace; OAuth and an eligible paid FirstSales plan required. Endpoint: `https://api.app.firstsales.io/mcp` · [Website](https://firstsales.io)
- **[HarborRank](https://harborrank.com/features/mcp)** `http` — SEO data for agents: keyword metrics, live Google SERPs and Maps results, domain and backlink overviews, rank-tracker reads, site audits, and read-only Search Console performance and URL inspection. OAuth login, free plan, paid from $29/month. Endpoint: `https://app.harborrank.com/mcp` · Registry: `com.harborrank/harborrank`
- **[Liftli](https://github.com/liftli-ai/liftli-mcp)** `http` — Head-of-content for LinkedIn, X, and Substack: extracts your voice from your own posts, turns voice notes and transcripts into drafts, critiques them, then publishes through official platform APIs. 54 tools, no scraping.
- **[LigoSocial](https://ligosocial.com/integrations/claude)** `http` — LinkedIn MCP: draft posts in your voice, read post analytics, schedule and publish via LinkedIn's official API. Endpoint: `https://ligosocial.com/mcp` · [Docs](https://ligosocial.com/integrations/claude)
- **[LinkMCP](https://app.linkmcp.io)** `http` — Hosted LinkedIn MCP server on your own LinkedIn account: profiles, companies, people, job and Sales Navigator search, inbox, posts, comments, reactions, connection requests and work email finding; OAuth or access key, paid plans with a 7-day free trial. Endpoint: `https://app.linkmcp.io/api/mcp` · [Docs](https://github.com/linkmcp-io/linkmcp) · Registry: `io.linkmcp/linkmcp`
- **[LLM Pulse MCP](https://github.com/estevecastells/llmpulse-mcp)** `http` — AI search visibility analytics for brand mentions, citations, share of voice, and AI-referred traffic across ChatGPT, Perplexity, Gemini, and Google AI Overviews. Endpoint: `https://llmpulse.ai/api/v1/mcp` (Bearer authentication) · [Product](https://llmpulse.ai)
- **[LogNorm](https://github.com/lognorm/lognorm-mcp)** `http` — Site and GEO audits ranked into a backlog that Claude Code, Codex and Cursor can fix, write and track (including how AI assistants answer buyer prompts). OAuth 2.1 with dynamic client registration; free plan. Endpoint: `https://lognorm.com/api/mcp` · [Docs](https://lognorm.com/docs/agents)
- **[MentionsAPI](https://github.com/mukul-dutt/mentionsapi-mcp)** `http` — AI brand visibility: whether ChatGPT, Claude, Gemini, Perplexity, Google AI Overviews and Bing Copilot mention a brand, at what rank and sentiment, and which URLs they cite. OAuth 2.1 or Bearer key; free tier. Endpoint: `https://api.mentionsapi.com/mcp` · [Docs](https://mentionsapi.com/docs)
- **[Murkuz](https://murkuz.com/mcp-tools)** `http` — SEO MCP: your Search Console, GA4 and Bing Webmaster data across every site, with live SEO analyses. Endpoint: `https://murkuz.com/mcp` · [Docs](https://murkuz.com/mcp-tools)
- **[NotFair](https://notfair.co)** `http` — Google Ads diagnostics (CPA, ROAS, search-term waste, quality scores) and optimizations executed through the official Google Ads API behind a human-approval gate.
- **[NotFair Skills](https://github.com/nowork-studio/NotFair)** — *Skills, not a server.* Open-source Claude Code skills for SEO, GEO, Google Ads, and Meta Ads that pull live data through the Google Ads, Meta Ads, Search Console, and GA4 MCP servers.
- **[PostWire](https://github.com/Perufitlife/postwire-mcp)** `http` — Writes a separate native post per network from one idea and publishes or schedules it to TikTok, Instagram, YouTube, LinkedIn, Bluesky and more; free plan, OAuth sign-in. Endpoint: `https://postwire.io/api/mcp` · Local: `npx -y postwire-mcp` · Registry: `io.github.Perufitlife/postwire-mcp`
- **[Proofsource](https://proofsource.co/docs/chatgpt-and-claude)** `http` — AI visibility for a brand: which buyer questions name it in ChatGPT, Perplexity, Claude and Google AI Overviews, which competitors are named instead, which sources are cited, and whether shipped fixes changed the answers. OAuth sign-in; free trial. Endpoint: `https://app.proofsource.co/v1/mcp` · Registry: `co.proofsource/proofsource`
- **[Rank by Ouroboros Apps](https://github.com/LAHutchins91/rank-mcp)** `http` — SEO rankings from Google Search Console, read-only: top queries and pages, traffic trends, period comparisons, quick wins, dropped pages, and URL inspection. OAuth sign-in. Endpoint: `https://rank.ouroborosapps.com/mcp` · [Docs](https://ouroborosapps.com/docs/rank) · [Ouroboros Apps](https://ouroborosapps.com)
- **[Robot Speed](https://github.com/robot-speed/mcp)** `http` — AI SEO MCP: content calendar, keyword research, site audits, backlinks, and CMS publishing. OAuth remote. Endpoint: `https://www.robot-speed.com/api/mcp` · [Website](https://www.robot-speed.com/mcp)
- **[SaaSCity](https://github.com/nyyhao/saascity-mcp)** `http` — Launch toolkit: audits a homepage before launch, finds startup and SaaS directories by Ahrefs DR, dofollow and price, and submits the product to the SaaSCity launch directory as a draft the human claims. No API key. Endpoint: `https://saascity.io/api/mcp` · [Website](https://saascity.io) · Registry: `io.saascity/saascity`
- **[SearchLink Lite](https://github.com/GlobalMatchHub/searchlink-lite)** `stdio` — Google Search Console inside your MCP client: search performance by query, page, country or device, ranking opportunities, URL indexing, sitemaps and on-page checks. Eight read-only tools, runs locally with a service account or gcloud credentials. Install: `npx -y github:GlobalMatchHub/searchlink-lite`
- **[SemanticHub](https://semantichub.app/docs)** `http` — Monitors news sources, clusters articles by topic and generates texts from them. OAuth 2 or Bearer token, free plan with no card.
- **[Serpel](https://serpel.app/mcp)** `http` — SEO infrastructure for rankings, site audits, keyword research, and AI visibility. Endpoint: `https://serpel.app/mcp` · [Website](https://serpel.app)
- **[Site SEO & AI Crawler Audit](https://tools.openkrill.app/#site-check)** `http` — Checks a public page's SEO tags, its robots.txt rules for GPTBot and other AI crawlers, and the signals AI answer engines use to cite it; free, read-only, no API key. Endpoint: `https://sitecheck.openkrill.app/mcp`
- **[Testimonials.ltd](https://testimonials.ltd/integrations/claude)** `http` — Testimonials and wall of love widgets: import reviews, approve, tag and pin the best ones from chat. Endpoint: `https://testimonials.ltd/mcp` · [Docs](https://testimonials.ltd/integrations/claude)
- **[ThreadFox Lite](https://github.com/amflimited/threadfox-lite)** `stdio` — Read-only Reddit research through your own signed-in Chrome: a subreddit's rules with self-promotion rules flagged, communities for a topic, an account's standing, and whether a post is still live. No API keys.
- **[Unfetch](https://unfetch.com/plugin)** `http` — Google Ads MCP reporting for campaign spend, conversions, and search terms, plus Google Analytics, Search Console, keyword research, and web research with read-only account access; OAuth and a free plan. Endpoint: `https://unfetch.com/api/mcp` · [Website](https://unfetch.com)
- **[Unsora](https://github.com/Shipped-Studio/unsora)** `http` — Generates AI images, video, voiceovers, music and clips, then schedules and publishes them to connected social accounts; OAuth or API-key auth, open source (AGPL-3.0). Endpoint: `https://mcp.tryunsora.com/mcp` · [Docs](https://docs.tryunsora.com)
- **[Upload-Post](https://github.com/Upload-Post/upload-post-mcp)** `http` — Publish and schedule videos, photos, carousels, text and documents to TikTok, Instagram, YouTube, LinkedIn, Facebook, X, Threads, Pinterest, Reddit, Bluesky and Google Business Profile, and read post analytics and comments; OAuth or API key, free plan. Install: `npx -y @upload-post/mcp` (stdio) or endpoint `https://mcp.upload-post.com/mcp` · [Docs](https://docs.upload-post.com/guides/mcp-server-integration/)
- **[VoiceMoat](https://github.com/prateeks367/voicemoat-mcp)** `http` — Personal brand tools for Twitter/X and LinkedIn: score a draft against your own voice profile, improve it, read your analytics and top posts, and publish or schedule after a preview and a confirmed second call; OAuth, needs a VoiceMoat Pro or Enterprise plan. Endpoint: `https://app.voicemoat.com/api/mcp` · [Website](https://voicemoat.com/mcp) · Registry: `com.voicemoat/voicemoat`
- **[Warmerly](https://github.com/WarmerlyApp/mcp)** `http` — Email warmup and cold outreach: mailbox health and warmup, SPF/DKIM/DMARC checks, placement tests, lead search, email verification, draft campaigns and inbox reply triage; campaigns are launched by the person in the dashboard, never by the assistant. OAuth sign-in, free plan. Endpoint: `https://app.warmerly.com/api/mcp` · [Docs](https://docs.warmerly.com/ai)

### Cloud, ops & data

- **[Cohesivity](https://github.com/cohesivity-org/cohesivity-plugin)** `http` — Agent-native backend services for hosting, Postgres, email, storage, containers, LLMs, voice, and third-party APIs, with free tiers, $5/month in AI and Search credits, and x402 top-ups. This remote MCP requires OAuth sign-in; anonymous no-signup setup uses the local MCP. Endpoint: `https://cohesivity.ai/mcp/manage` · [Docs](https://github.com/cohesivity-org/cohesivity-plugin#local-bootstrap-and-remote-oauth-are-independent)
- **[DC Hub](https://github.com/azmartone67/dchub-mcp-server)** `http` — DC Hub is the live data layer for data-center site selection. Its Data Center Power Index (DCPI) is a daily score of where data centers can get grid power, across 300+ markets, with 94 tools keyless at free-tier depth via `claude mcp add --transport http dchub https://dchub.cloud/mcp`.
- **[Gemmein](https://docs.gemmein.com/r/dir)** `stdio` — Server-enforced access rules and server-defined AI tools on the owner's provider key, with an integration check that fails when anonymous people can read private data. · [Website](https://gemmein.com/r/dir)
- **[Invokely](https://invokely.ai/docs)** `http` — Hosted MCP and REST API for official statistics by indicator, place, and period, with a source citation on each figure. The Free plan includes 500 MCP calls/month with no card; REST data queries require Builder, Pro, or prepaid credits, while the separate no-account MCP trial allows 25 calls/day per IP. Endpoint: `https://invokely.ai/mcp` · Trial endpoint: `https://invokely.ai/mcp/trial`
- **[RowSafe](https://github.com/rowsafe/rowsafe)** `http` — Database health, backups, recovery workflows and managed database provisioning through Streamable HTTP or local `rowsafe mcp`; a RowSafe account with OAuth or API-key authentication is required. The agent, CLI and MCP server are Apache-2.0; the hosted service is separate · [Docs](https://rowsafe.sh/docs/reference/mcp)
- **[Shipvela](https://shipvela.com/integrations/assistants)** `http` — Publish React, Vite and static websites, and read project status, build logs and usage through OAuth; a Shipvela account is required, a Hobby tier is available, and uploads require owner confirmation. Endpoint: `https://shipvela.com/mcp`
- **[SolidPing](https://github.com/fclairamb/solidping)** `http` — Self-hostable uptime monitor whose MCP server creates, runs and diagnoses checks across 43 types, reads incidents, and manages status pages and maintenance windows. Free hosted tier, OAuth 2.1, also runs over stdio. Endpoint: `https://solidping.io/api/v1/mcp` · [Docs](https://docs.solidping.io/features/mcp)
- **[spinnaker-mcp](https://github.com/GeiserX/spinnaker-mcp)** `stdio` — Exposes a Spinnaker instance through its Gate API as 37 tools for applications, pipelines, executions, deployment strategies and infrastructure, with an optional read-only toolset. Install: `npx -y spinnaker-mcp` (set `GATE_URL`) · [Docs](https://geiserx.github.io/spinnaker-mcp/)
- **[ZopDev MCP](https://zop.dev/learn/mcp-server)** `http` — Cloud cost and infrastructure governance across AWS, Azure, GCP, Databricks, and Snowflake: 263 tools (155 read, 108 write) spanning cost, resources, schedules, recommendations, budgets, and diagnostics. Read-only by default, with optional scoped writes. Install: `claude mcp add zopdev https://api.zop.dev/mcp-server -t http` (OAuth 2.1 signs you in; add `--header "Authorization: Bearer zn_pat_YOUR_TOKEN"` for CI) · [Repo](https://github.com/zopdev/mcp) · [Claude setup](https://zop.dev/learn/how-to/set-up-zopnight-mcp-for-claude)

### Commerce, travel & logistics

- **[BirkinBagStock](https://birkinbagstock.com/llms.txt)** `http` — Independent Hermès resale index: inventory, market prices, auction calendar and results. Endpoint: `https://birkinbagstock.com/mcp` (no auth) · Registry: `com.birkinbagstock/mcp`
- **[Brainy Prices](https://prices.brainy.ae/developers.html)** `http` — UAE cost of living data: school fees (KHDA), registered rents (DLD), fuel, utilities, telecom plans and relocation costs, with source and date on every answer. Read-only; no auth. Endpoint: `https://prices.brainy.ae/mcp/v2`
- **[BuyWhere](https://github.com/BuyWhere/buywhere-mcp)** `http` — Cross-border product search and price comparison across 370M+ listings. No API key. Endpoint: `https://api.buywhere.ai/mcp` · Install: `npx -y @buywhere/mcp-server` · [Docs](https://docs.buywhere.ai)
- **[CardDeals](https://github.com/cello305/carddeals-mcp)** `http` — Query and compare real-time discounted digital gift cards across 700+ brands. Endpoint: `https://catalog.carddeals.co/mcp` · [Docs](https://carddeals.co/mcp)
- **[Clickwise](https://github.com/softdevfz/clickwise-api)** `http` — Affiliate network: find affiliate programs that fit a site or channel and browse deals without a key; a free publisher key adds tracked links, conversion reports and a product search endpoint (by text or GTIN). Endpoint: `https://partners.clickwise.net/api/v1/mcp` · [Docs](https://partners.clickwise.net/developers/) · Registry: `net.clickwise/mcp`
- **[Google Hotels](https://github.com/huynhtanan/google-hotels-mcp)** `stdio` — Live Google Hotels + Vacation Rentals search with per-OTA nightly rates (Booking.com, Expedia, Agoda, Vrbo, Airbnb, Hotels.com and 10+ other providers) and a 3-month daily price calendar. Install: `uvx --from "git+https://github.com/huynhtanan/google-hotels-mcp.git@v0.1.2" google-hotels-mcp` · [Docs](https://github.com/huynhtanan/google-hotels-mcp#readme)
- **[HOTLIKESHOP](https://github.com/tuanone123/hotlikeshop-mcp)** `http` — Search a catalog of social-media accounts, proxies, and digital services and buy them right inside the chat; free to connect, no key for lookup. Endpoint: `https://hotlikeshop.com/api/mcp` · [Docs](https://hotlikeshop.com/ai)
- **[MAQAMI Travel](https://github.com/negm17111995/mcp-server)** `http` — Official MCP server for MAQAMI, a hotel and flight booking platform with 3M+ hotels. Search live hotel rates and flights, look up airports and hotel details, then send the customer a secure checkout link on book.maqami.co. Endpoint: `https://mcp.maqami.co/`, no API key required · [Website](https://maqami.co)
- **[OctoTrip Rental Cars](https://github.com/octotrip/rental-cars)** `http` — Search and compare rental cars with real-time pricing across providers worldwide, grouped by SIPP category. Endpoint: `https://mcp.octotrip.app/rental-cars/mcp`, no API key required · [Website](https://octotrip.app)
- **[Packrift](https://github.com/Packrift/packrift-mcp)** `http` — Packaging procurement: exact-size SKU lookup, carton-fit recommendations, shipping estimates, and dimensional-weight calculations.
- **[Pocket Drives](https://github.com/RevList/pocket-drives-mcp)** `http` — Search peer-to-peer luxury, exotic, and EV rentals from independent hosts. Endpoint: `https://pocketdrives.ai/mcp`, no auth.
- **[pumperly-mcp](https://github.com/GeiserX/pumperly-mcp)** `stdio` — Queries fuel prices, finds nearby stations, plans routes and geocodes places through a Pumperly instance (the public pumperly.com or your own), read-only and with no API key. Install: `npx -y pumperly-mcp` (set `PUMPERLY_URL`) · [Docs](https://github.com/GeiserX/pumperly-mcp/blob/main/docs/getting-started.md)
- **[RoboHub](https://robohub.app)** `http` — Vendor-neutral catalog of 340+ commercial robots: search, compare specs and maker-verified prices. Endpoint: `https://robohub.app/api/mcp` (no auth) · Registry: `app.robohub/robohub`
- **[ScentVerdict](https://scentverdict.com/connect)** `http` — Fragrance verdicts, similarity scores, scent profiles, drydowns and local prices for a perfume catalogue. Read-only; no auth. Endpoint: `https://scentverdict.com/mcp` · Registry: `com.scentverdict/fragrances`
- **[SkyAccess](https://github.com/sky-access/skyaccess-mcp)** `http` — Search 5,000+ live empty leg flights, get charter price estimates and booking links. No account or API key. Endpoint: `https://mcp.skyaccess.com/mcp` · [Website](https://skyaccess.com) · Registry: `com.skyaccess/skyaccess`
- **[StayingAPI](https://github.com/stayingapi/hotel-mcp)** `http` — Accommodation data across Airbnb, Booking.com, Vrbo, and Google Hotels: search stays and read live listings, rates, availability and reviews. Endpoint: `https://mcp.stayingapi.com/mcp` · [Docs](https://stayingapi.com)
- **[Tenmomo](https://tenmomo.com/mcp)** `http` — Search US stores for cashback rates and coupon codes, and get a tracked activation link. Endpoint: `https://tenmomo.com/mcp`
- **[Wheremind](https://wheremind.ai/maps-mcp)** `http` — Hosted maps server: live place search, place details, nearby search, forward and reverse geocoding, and turn-by-turn directions, with no Maps API key to manage. Read-only tools; invite-only beta with OAuth or a stored Bearer header. Endpoint: `https://wheremind.ai/mcp` · [Docs](https://wheremind.ai/llms.txt) · Registry: `ai.wheremind/wheremind`

### Work & productivity

- **[AI Applyd](https://github.com/whateverneveranywhere/aiapplyd-mcp)** `http` — ATS resume scoring, job-description analysis, interview prep, cover letters, resume building, and auto-apply that submits on the employer's own hiring system. [Website](https://aiapplyd.com/mcps)
- **[atlassian-browser-mcp](https://github.com/GeiserX/atlassian-browser-mcp)** `stdio` — Wraps mcp-atlassian with a Playwright browser-cookie login, so its Jira and Confluence tools work on Atlassian Server/Data Center behind corporate SSO (Okta, SAML) where API tokens are not available. Install: clone and `uv pip install -e .`, then `./atlassian-cli login jira` once per service · [Docs](https://github.com/GeiserX/atlassian-browser-mcp/blob/main/docs/getting-started.md)
- **[call4me](https://github.com/skeptrunedev/call4me)** `http` — Places real phone calls to businesses for you (bookings, appointments, cancellations), works through phone menus, and returns the transcript and outcome. Endpoint: `https://call4.me/mcp` (OAuth) · [Docs](https://call4.me)
- **[CareClinic Health Tracker](https://cdn.careclinic.io/mcp/help/index.html)** `http` — Review personal medication schedules, symptoms, mood, and confirmed health check-ins through an authorized CareClinic account. Endpoint: `https://mcp.careclinic.io/mcp`
- **[Clera](https://github.com/getclera/mcp)** `http` — Search 210,000+ vetted startup candidates, review Clera's picks for your open roles and request intros; candidates search open startup roles. Endpoint: `https://mcp.getclera.com` (OAuth 2.1, no API key) · [Docs](https://www.getclera.com/mcp) · Registry: `com.getclera/clera`
- **[Communicate](https://developer.communicate.so/docs/mcp)** `http` — Read-only discovery of workspace AI support agents through `communicate_list_agents`, using OAuth client-credentials tokens with the `agents:read` scope. Endpoint: `https://app.communicate.so/mcp` · [Website](https://communicate.so) · Registry: `io.github.uditgoenka/communicate`
- **[Connections](https://studio.connections.icu/connect)** `http` — Contact book with follow-ups, event pages with ticketing, notes and email for a free Connections account, reached over OAuth sign-in. Endpoint: `https://studio.connections.icu/v1/mcp` · [Docs](https://studio.connections.icu/connect)
- **[Desk by Ouroboros Apps](https://github.com/LAHutchins91/desk-mcp)** `http` — Customer support policy for assistants: approved support answers, refund rules, and escalation limits read before replying; unapproved promises go to human review. OAuth sign-in. Endpoint: `https://desk-mcp-continuity2.vercel.app/mcp` · [Docs](https://ouroborosapps.com/docs/desk) · [Ouroboros Apps](https://ouroborosapps.com)
- **[Milestone by Ouroboros Apps](https://github.com/LAHutchins91/milestone-mcp)** `http` — Freelance project milestones: approved milestones, deliverables, and acceptance criteria; a milestone is only done when the saved criteria are met. OAuth sign-in. Endpoint: `https://milestone-continuity2.vercel.app/mcp` · [Docs](https://ouroborosapps.com/docs/milestone) · [Ouroboros Apps](https://ouroborosapps.com)
- **[Office Suite](https://github.com/theluckystrike/mcp-servers)** `stdio` — Bundle of MCP servers for freelance and back-office work: invoices, spreadsheets, PDFs, time tracking, expense tracking, resumes, and contracts. [Hosted](https://mcp.zovo.one)
- **[PDFtoMarkdown.ai](https://github.com/happywpco/pdftomarkdown-mcp)** `stdio` — Converts local PDF, DOCX, PPTX, XLSX, PNG/JPG, HTML and EPUB files into structured Markdown with headings, tables and OCR text, via the PDFtoMarkdown.ai API. API key required; free account includes 10 pages, then pay-per-page credits. Install: `npm install -g @happywp/pdftomarkdown-mcp` · [Docs](https://pdftomarkdown.ai/developers)
- **[Process Street](https://github.com/process-street/process-street-mcp)** `http` — Connect agents to Process Street workflows, tasks, runs, data sets, and operational records, with an interactive authorization flow. [Docs](https://www.process.st/help/docs/mcp-server/)
- **[Scope by Ouroboros Apps](https://github.com/LAHutchins91/scope-mcp)** `http` — Freelance scope of work: approved scope, rates, deadlines, and change orders, so an assistant cannot promise work or discounts that were not approved. OAuth sign-in. Endpoint: `https://scope-continuity2.vercel.app/mcp` · [Docs](https://ouroborosapps.com/docs/scope) · [Ouroboros Apps](https://ouroborosapps.com)

<!-- directory:end -->

## 🤝 Contributing

Contributions are very welcome — this list is only as good as the people adding to it.

**Adding a server?** Read **[CONTRIBUTING.md](CONTRIBUTING.md)** first. The short version:

- One server per pull request.
- Add one file, `servers/<your-server>.json`:
  ```json
  {
    "name": "Your Server",
    "url": "https://link-to-repo-or-docs",
    "category": "developer-tools",
    "transport": "http",
    "description": "One sentence on what it does. [Docs](https://…)",
    "endpoint": "https://your-server.example/mcp"
  }
  ```
- Run `python3 scripts/build.py --readme` to regenerate the list. Don't edit the list in this README by hand.
- Keep the description to one or two sentences. No marketing copy, no tracking parameters in URLs.
- The server must actually exist, speak MCP, and be reachable by someone who isn't you.

Once merged, your server gets its own page and a status badge you can embed:

```markdown
[![MCP status](https://mcp.aianytime.net/badge/your-server.svg)](https://mcp.aianytime.net/s/your-server/)
```

<a href="https://github.com/AIAnytime/Awesome-MCP-Servers/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=AIAnytime/Awesome-MCP-Servers" alt="Contributors" />
</a>

## 📚 Resources

- [Model Context Protocol — documentation](https://modelcontextprotocol.io)
- [MCP specification](https://modelcontextprotocol.io/specification)
- [Official MCP registry](https://registry.modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) · [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [AI Anytime on YouTube](https://www.youtube.com/@AIAnytime) — MCP tutorials and walkthroughs

## 📜 License

[MIT](LICENSE). Listed third-party servers carry their own licenses — check each project before using it.

---

<div align="center">

**Found this useful? Star the repo ⭐ — it's how other people find it.**

</div>

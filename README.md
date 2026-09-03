<div align="center">

# Awesome MCP Servers

**A curated directory of Model Context Protocol servers — plus runnable reference implementations you can learn from.**

[![Stars](https://img.shields.io/github/stars/AIAnytime/Awesome-MCP-Server?style=flat-square&color=f5c518)](https://github.com/AIAnytime/Awesome-MCP-Server/stargazers)
[![Forks](https://img.shields.io/github/forks/AIAnytime/Awesome-MCP-Server?style=flat-square&color=6f42c1)](https://github.com/AIAnytime/Awesome-MCP-Server/network/members)
[![Contributors](https://img.shields.io/github/contributors/AIAnytime/Awesome-MCP-Server?style=flat-square&color=0aa)](https://github.com/AIAnytime/Awesome-MCP-Server/graphs/contributors)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)
[![MCP](https://img.shields.io/badge/Model%20Context%20Protocol-spec-black?style=flat-square)](https://modelcontextprotocol.io)

[Servers in this repo](#-servers-in-this-repo) · [Community directory](#-community-directory) · [Contributing](#-contributing) · [Resources](#-resources)

</div>

---

The [Model Context Protocol](https://modelcontextprotocol.io) is the open standard for connecting AI
assistants to tools and data. This repository is two things:

1. **A directory** — a curated, categorized list of MCP servers the community has built and shipped.
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
| [`streamlit as an MCP Host`](./streamlit%20as%20an%20MCP%20Host) | Streamlit app acting as an MCP **host** — connects to an SSE server, calls its tools, summarizes with a local Ollama model. | Python · Streamlit |

> [!TIP]
> New to MCP? Read `weather` first (smallest surface area), then `http-sse-mcp-starter` to see the same
> idea served remotely, then `streamlit as an MCP Host` to see the other side of the wire.

## 🚀 Quick start

```bash
git clone https://github.com/AIAnytime/Awesome-MCP-Server.git
cd Awesome-MCP-Server/weather

uv sync              # or: pip install -r requirements.txt
uv run weather.py
```

Then point an MCP client at it. With Claude Code:

```bash
claude mcp add weather -- uv --directory /absolute/path/to/Awesome-MCP-Server/weather run weather.py
```

For Claude Desktop, add the same command to `claude_desktop_config.json` under `mcpServers`.
Stuck? The [MCP playlist on the AI Anytime YouTube channel](https://www.youtube.com/@AIAnytime) walks through it end to end.

## 🌍 Community directory

Servers built by the community. Entries are alphabetical within each category.

**Legend** — `stdio` runs locally on your machine · `http` is a hosted remote server (nothing to install) · `sse` is a remote server over Server-Sent Events.

### Agents, IDEs & developer tools

- **[Agent QA](https://github.com/vostride/agent-qa)** `stdio` — Author, validate, run, and inspect natural-language web and mobile regression tests, with persistent test memory. Install: `npx -y agent-qa mcp`
- **[Antigravity Link](https://github.com/cafeTechne/antigravity-link-extension)** `stdio` — Mirror active AI chat sessions from Google's Antigravity IDE to your phone: send messages, upload files, stop generation, automate workflows across 9 tools. Registry: `io.github.cafeTechne/antigravity-link`
- **[claude-node](https://github.com/claw-army/claude-node)** `stdio` — Python subprocess bridge to the Claude Code CLI, giving Python direct access to Claude Code's native capabilities over stream-json.
- **[OpenAPI to MCP Cloud Bridge](https://github.com/notsariedo/openapi-mcp-gateway)** `sse` — Zero-setup hosted bridge that turns any OpenAPI JSON spec into a remote MCP server. [Hosted bridge](https://mcp-bridge-saas.onrender.com)
- **[Roundtable](https://github.com/askbudi/roundtable)** `stdio` — Zero-configuration server that unifies multiple AI coding assistants (Codex, Claude Code, Cursor, Gemini) behind one interface with auto-discovery. [Website](https://askbudi.ai/roundtable)
- **[SandBase CLI](https://github.com/sandbaseai/cli)** `stdio` — Agent-first CLI and MCP bridge for discovering, inspecting, and running 2,000+ AI models on one account — search, scraping, multimodal generation, data APIs, sandboxes. Install: `npx -y @sandbaseai/cli connect` · [Website](https://sandbase.ai)
- **[Skillselion](https://github.com/skillselion/skillselion-mcp)** `stdio` — On-demand skill loader over a catalog of 79,000+ agent skills, MCP servers, and plugins; materializes the matching `SKILL.md` and its scripts into the session mid-task. Install: `npx -y skillselion-mcp` · [Website](https://skillselion.com)

### Search & discovery

- **[AISOTools](https://github.com/shibley/aisotools-mcp-server)** `http` — Search a curated catalog of 1,766 AI tools by keyword, category, or pricing; compare 2–5 products side by side and find alternatives. Read-only, no API key, sponsored results flagged. Install: `claude mcp add --transport http aisotools https://aisotools.com/api/mcp` · [Docs](https://aisotools.com/mcp)
- **[nothumansearch](https://nothumansearch.ai/mcp)** `http` — Search engine over 8,600+ agent-native services: discover MCP servers, OpenAPI providers, and llms.txt publishers by keyword, category, or agentic-readiness score. Registry: `ai.nothumansearch/search`
- **[Parallel Search](https://docs.parallel.ai/integrations/mcp/search-mcp)** `http` — Free live web search and URL fetching, no account or API key. Endpoint: `https://search.parallel.ai/mcp`
- **[TwitterAPI.io](https://github.com/kaitoInfra/twitterapi-io-mcp-server)** `http` — 12 read-only tools over [twitterapi.io](https://twitterapi.io): tweet search with full operators, profiles, followers, conversation threads, real-time streaming, trending topics. Endpoint: `mcp.twitterapi.io/mcp`
- **[Xquik](https://github.com/Xquik-dev/x-twitter-scraper)** `http` — X/Twitter search, extraction workflows, account insights, webhooks, and SDK access. [Docs](https://docs.xquik.com/mcp/overview)

### Knowledge, memory & context

- **[ContextStream](https://github.com/contextstream/mcp-server)** `http` — Shared persistent memory and semantic code search for AI coding agents (Cursor, Claude Code, Codex, Grok, Windsurf). Free tier; hosted OAuth or API key. Endpoint: `https://mcp.contextstream.io/mcp` · [Website](https://contextstream.io)
- **[GoodMemory](https://github.com/hjqcan/GoodMemory)** `stdio` — Local-first, auditable memory for coding agents. SQLite-backed, read-only context/trace/search tools by default, with durable writes opt-in behind inspect, revise, forget, and export. Install: `npm install -g goodmemory`
- **[Screenpipe](https://github.com/screenpipe/screenpipe)** `stdio` — Local-first 24/7 screen and microphone recording with OCR, accessibility-tree, and transcript indexing, so assistants can answer questions over everything you've seen and heard. Install: `claude mcp add screenpipe -- npx -y screenpipe-mcp@latest`

### Media & generation

- **[Magic Hour](https://github.com/magichourhq/magic-hour-mcp)** `http` — Generate and edit video, images, and audio with 44 Magic Hour API tools. Endpoint: `https://mcp.magichour.ai/` (bearer API key required) · [Setup](https://magichour.ai/mcp)
- **[prompt-to-asset](https://github.com/MohamedAbdallah-14/prompt-to-asset)** `stdio` — Routes image-generation prompts to 30+ models (DALL·E, Stable Diffusion, Flux, Midjourney) through one interface. Install: `npm install -g prompt-to-asset`
- **[RunAPI](https://github.com/runapi-ai/mcp)** `stdio` — Browse the RunAPI model catalog and run image, video, music/audio, text-to-speech, and LLM tasks from agent workflows. Install: `npx -y @runapi.ai/mcp`

### Security

- **[Darkmoon](https://github.com/ASCIT31/Dark-Moon)** `stdio` — Open-source (GPLv3) autonomous penetration-testing platform orchestrating 80+ offensive security tools through 50 specialist agents, with proof of exploitation behind every finding. Runs fully locally.

### Finance & markets

- **[AskCyborg](https://github.com/Ask-Cyborg/askcyborg-mcp)** `http` — Stress-tests public and private companies through analyst debate: reports, scores, comparisons, competitors, recent developments. Anonymous free tier, no API key. Endpoint: `https://mcp.askcyborg.com/mcp`
- **[EventTrader](https://github.com/eventtrader/event-trader-mcp)** `http` — Prediction-market trading: place bets, TGE token price predictions, real-time orderbooks, agent cloning, due-diligence scoring. [Platform](https://cymetica.com)
- **[Helium](https://github.com/connerlambden/helium-mcp)** `http` — Real-time news with 37-dimension bias scoring, ML options pricing, and live market data. [Interactive demo](https://connerlambden.github.io/helium-news-explorer/) · [REST API](https://heliumtrades.com/mcp-page/)

### Marketing, content & social

- **[BulkPublish](https://github.com/azeemkafridi/bulkpublish-api)** `http` — Plan, review, schedule, publish, and analyze social media content for AI agents through BulkPublish. Endpoint: `https://mcp.bulkpublish.com/mcp` · [Docs](https://app.bulkpublish.com/docs)
- **[Autoposting](https://github.com/Autoposting-ai/autoposting-mcp)** `http` — Draft, schedule, and publish to X, LinkedIn, Instagram, Threads, and YouTube, plus AI carousels and video clipping. OAuth 2.1 with dynamic client registration — no secret to paste. Install: `claude mcp add --transport http autoposting https://app.autoposting.ai/mcp`
- **[Liftli](https://github.com/liftli-ai/liftli-mcp)** `http` — Head-of-content for LinkedIn, X, and Substack: extracts your voice from your own posts, turns voice notes and transcripts into drafts, critiques them, then publishes through official platform APIs. 54 tools, no scraping.
- **[NotFair](https://notfair.co)** `http` — Google Ads diagnostics (CPA, ROAS, search-term waste, quality scores) and optimizations executed through the official Google Ads API behind a human-approval gate.
- **[NotFair Skills](https://github.com/nowork-studio/NotFair)** — *Skills, not a server.* Open-source Claude Code skills for SEO, GEO, Google Ads, and Meta Ads that pull live data through the Google Ads, Meta Ads, Search Console, and GA4 MCP servers.

### Cloud, ops & data

- **[Zopnight](https://zop.dev/learn/mcp-server)** `http` — Read-only cloud cost and infrastructure governance across AWS, Azure, and GCP: 85 tools spanning cost, resources, schedules, recommendations, budgets, and diagnostics. Install: `claude mcp add --transport http zopnight https://api.zop.dev/mcp-server --header "Authorization: Bearer zn_pat_YOUR_TOKEN"` · [Claude setup](https://zop.dev/learn/how-to/set-up-zopnight-mcp-for-claude)

### Commerce, travel & logistics

- **[BuyWhere](https://github.com/BuyWhere/buywhere-mcp)** `stdio` — Cross-border e-commerce product search across 150M+ products in Singapore, SEA, and US markets with real-time price comparison. Install: `npx @buywhere/mcp-server`
- **[Packrift](https://github.com/Packrift/packrift-mcp)** `http` — Packaging procurement: exact-size SKU lookup, carton-fit recommendations, shipping estimates, and dimensional-weight calculations.
- **[Pocket Drives](https://github.com/RevList/pocket-drives-mcp)** `http` — Search peer-to-peer luxury, exotic, and EV rentals from independent hosts. Endpoint: `https://pocketdrives.ai/mcp`, no auth.

### Work & productivity

- **[AI Applyd](https://github.com/whateverneveranywhere/aiapplyd-mcp)** `http` — ATS resume scoring, job-description analysis, interview prep, cover letters, resume building, and auto-apply that submits on the employer's own hiring system. [Website](https://aiapplyd.com/mcps)
- **[Process Street](https://github.com/process-street/process-street-mcp)** `http` — Connect agents to Process Street workflows, tasks, runs, data sets, and operational records, with an interactive authorization flow. [Docs](https://www.process.st/help/docs/mcp-server/)

## 🤝 Contributing

Contributions are very welcome — this list is only as good as the people adding to it.

**Adding a server?** Read **[CONTRIBUTING.md](CONTRIBUTING.md)** first. The short version:

- One server per pull request.
- Add it as a **bullet** in the right category, in alphabetical order. Please don't renumber anything or introduce numbered lists — that's what broke this file before.
- Use the exact entry format:
  ```markdown
  - **[Name](https://link-to-repo-or-docs)** `stdio|http|sse` — One sentence on what it does. Install: `command` · [Docs](https://…)
  ```
- Keep it to one or two sentences. No marketing copy, no tracking parameters in URLs.
- The server must actually exist, speak MCP, and be reachable by someone who isn't you.

<a href="https://github.com/AIAnytime/Awesome-MCP-Server/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=AIAnytime/Awesome-MCP-Server" alt="Contributors" />
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

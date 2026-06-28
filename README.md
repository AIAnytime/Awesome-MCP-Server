# Awesome-MCP-Server 🚀  

This repository contains **MCP (Model Context Protocol) servers** . Each folder represents a different MCP server implementation.  

## 📂 Server Implementations  

1. **Weather Server** 🌦️  
   - Fetches real-time weather details and forecasts.  
   - Can be integrated with MCP clients like **Claude for Desktop**.  

2. **LinkedIn Profile Server** 🔗  
   - Retrieves LinkedIn profile data via an external API from RapidAPI.  
   - Enables AI models to process professional profile insights.
  
3. **Fetch PubMed Article Server** 🔗
   - Retrieves articles from PubMed given a query.

4. **Roundtable** 🤖
   - Zero-configuration MCP server that unifies multiple AI coding assistants (Codex, Claude Code, Cursor, Gemini).
   - Provides intelligent auto-discovery and standardized interface across AI tools.
   - Repository: [askbudi/roundtable](https://github.com/askbudi/roundtable) | Website: [askbudi.ai/roundtable](https://askbudi.ai/roundtable)

5. **claude-node** 🐍
   - Python subprocess bridge for Claude Code CLI, giving Python code direct access to Claude Code native capabilities via stream-json.
   - Repository: [claw-army/claude-node](https://github.com/claw-army/claude-node)

6. **Antigravity Link** 📱

7. **prompt-to-asset** 🎨
   - Routes image-generation prompts to 30+ models — DALL-E, Stable Diffusion, Flux, Midjourney, and more — through a single MCP interface.
   - Install: `npm install -g prompt-to-asset`
   - Repository: [MohamedAbdallah-14/prompt-to-asset](https://github.com/MohamedAbdallah-14/prompt-to-asset)

   - MCP server and mobile companion for Google's Antigravity IDE. Mirror active AI chat sessions on your phone, send messages, upload files, stop AI generation, and automate workflows via 9 MCP tools or a local OpenAPI HTTP API.
   - Repository: [cafeTechne/antigravity-link-extension](https://github.com/cafeTechne/antigravity-link-extension) | MCP Registry: io.github.cafeTechne/antigravity-link

7. **nothumansearch** 🔎
   - MCP server and search engine indexing 8,600+ agent-native services. Lets LLMs discover MCP-compatible services, OpenAPI providers, and llms.txt publishers by keyword, category, or minimum agentic readiness score (0-100).
   - 6 tools: search_agents, get_site_details, get_stats, submit_site, register_monitor, verify_mcp.
   - Endpoint: [nothumansearch.ai/mcp](https://nothumansearch.ai/mcp) | MCP Registry: ai.nothumansearch/search

8. **Packrift MCP** 📦
   - Remote MCP server for packaging procurement, exact-size SKU lookup, carton-fit recommendations, shipping estimates, and dimensional-weight calculations.
   - Repository: [Packrift/packrift-mcp](https://github.com/Packrift/packrift-mcp)
- [Helium MCP](https://github.com/connerlambden/helium-mcp) — Real-time news with 37-dimension bias scoring, ML options pricing, and live market data. [Interactive demo](https://connerlambden.github.io/helium-news-explorer/) · [REST API](https://heliumtrades.com/mcp-page/)

9. **Screenpipe MCP** 🖥️
   - Local-first MCP server backed by 24/7 screen and microphone recording with OCR, accessibility-tree, and transcript indexing.
   - Lets AI assistants search and answer questions over everything you've seen, heard, and typed on your machine.
   - Install: `claude mcp add screenpipe -- npx -y screenpipe-mcp@latest`
   - Repository: [screenpipe/screenpipe](https://github.com/screenpipe/screenpipe)

## 🛠️ How to Use  

1. Clone the repository:  
   ```bash
   git clone https://github.com/AIAnytime/MCP-Servers.git
   cd MCP-Servers
   ```
2. Navigate to the desired server folder. Follow the respective README.md file for instructions.
3. Watch the MCP Playlist on AI Anytime YT Channel if you face any problem.

## 📢 Contribute  
Feel free to open issues, submit pull requests, or suggest improvements!  

## 📜 License  
This project is open-source under the **MIT License**.  

---

🔔 **Like this project?** Give it a ⭐ on GitHub!  

- [EventTrader MCP Server](https://github.com/eventtrader/event-trader-mcp) — AI prediction market trading: place bets, TGE token price predictions, real-time orderbooks, AI agent cloning, due diligence scoring. Remote endpoint at `cymetica.com/.well-known/mcp.json`. [Platform](https://cymetica.com?utm_source=github&utm_medium=pr&utm_campaign=mcp-outreach) | [TGE Markets](https://cymetica.com/tge-launch?utm_source=github&utm_medium=pr&utm_campaign=mcp-outreach)
- [NotFair MCP](https://notfair.co) — Hosted Google Ads MCP server. Lets Claude and other AI agents diagnose campaign performance (CPA, ROAS, search-term waste, quality scores), recommend optimizations (bids, budgets, negative keywords, ad copy), and execute approved changes via the official Google Ads API with a built-in human-approval gate. Free tier plus paid plans. [Product](https://notfair.co)
- [NotFair Skills](https://github.com/nowork-studio/NotFair) — Open-source Claude Code skills (~2.9k stars, MIT) for SEO, GEO, Google Ads, and Meta Ads. Connects to live data through Google Ads MCP, Meta Ads MCP, Google Search Console MCP, and Google Analytics (GA4) MCP. Covers site analysis, keyword research, meta tags, schema markup, ad audits, wasted-spend detection, and Meta ROAS / creative-fatigue analysis.
- [AskCyborg MCP](https://github.com/Ask-Cyborg/askcyborg-mcp) — Stress-tests every public and private company through intense analyst debate. 8 tools (search_companies, get_company_report, get_cyborg_score, compare_companies, find_competitors, search_by_industry, get_recent_developments, get_top_insights). Hosted at `https://mcp.askcyborg.com/mcp` — Streamable HTTP, anonymous free tier (20 req/min/IP), no API key. Source: MIT, TypeScript on Cloudflare Workers. Listed in the official MCP Registry as `io.github.Ask-Cyborg/askcyborg-mcp`.
- [Xquik](https://github.com/Xquik-dev/x-twitter-scraper) - Remote MCP server for X/Twitter search, extraction workflows, account insights, webhooks, and SDK access. Docs: [docs.xquik.com/mcp/overview](https://docs.xquik.com/mcp/overview).
- [TwitterAPI.io MCP Server](https://github.com/kaitoInfra/twitterapi-io-mcp-server) — Hosted MCP server for [twitterapi.io](https://twitterapi.io) (Twitter / X data API). 12 read-only tools: tweet search with full operators, profiles, followers, conversation threads, real-time WebSocket streaming, trending topics. Hosted endpoint at `mcp.twitterapi.io/mcp`, npm `@kaitoinfra/twitterapi-io-mcp-server`. Listed on MCP Registry as `io.github.kaitoInfra/twitterapi-io-mcp-server` (active since 2026-05-23).
- [FilingFirehose MCP](https://filingfirehose.com/mcp) — Hosted MCP server exposing SEC EDGAR filings (8-K, 10-K, 10-Q, S-3, 13D), forensic risk scores (LOW/MODERATE/ELEVATED/HIGH), and cyber-incident tracking on any US stock ticker. No install — point your MCP client at `https://filingfirehose.com/mcp`. Free tier plus paid plans from $9/mo.

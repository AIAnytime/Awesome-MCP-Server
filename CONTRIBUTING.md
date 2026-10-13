# Contributing

Thanks for adding to the list. The directory is built from one small file per server, so two
people adding servers at the same time never collide, and a script can check every hosted
server each night.

## Adding a server to the directory

### 1. One server per pull request

Two servers, two PRs. It keeps review fast and makes a bad entry easy to revert without
taking a good one with it.

### 2. Add one file: `servers/<your-server>.json`

Name the file after the server, in lowercase with hyphens (`parallel-search.json`).

```json
{
  "name": "Parallel Search",
  "url": "https://docs.parallel.ai/integrations/mcp/search-mcp",
  "category": "search",
  "transport": "http",
  "description": "Free live web search and URL fetching, no account or API key. Endpoint: `https://search.parallel.ai/mcp`",
  "endpoint": "https://search.parallel.ai/mcp"
}
```

| Field | Rule |
| --- | --- |
| `name` | The server's real name. |
| `url` | Its public repository, or its docs page if there is no public repo. |
| `category` | One of `developer-tools`, `search`, `knowledge-memory`, `media`, `security`, `finance`, `marketing`, `cloud-data`, `commerce-travel`, `productivity`. If nothing fits, use the closest and say so in the PR. |
| `transport` | `stdio` (runs locally), `http` (hosted remote) or `sse` (remote over SSE). |
| `description` | One sentence, two at the absolute most, on a single line. Markdown links and `code` are fine: `Install: \`command\` · [Docs](https://…)`. |
| `endpoint` | **Hosted servers only.** The `https://` URL an MCP client connects to. This is what gets checked every night. |
| `registry` | Optional. Your id in the official MCP Registry. |

### 3. Regenerate the README

```bash
python3 scripts/build.py --readme   # rewrites the list in README.md from servers/
python3 scripts/lint.py             # the same check CI runs
```

**Do not edit the list in `README.md` by hand.** It is generated, and the lint fails if it does
not match the files in `servers/`. Python 3.10 or newer is all you need; there is nothing to install.

### 4. What happens after it merges

Your server gets a page on the site and a status badge you can put in your own README. If it is
hosted, the nightly check sends it an MCP `initialize` and, when no credentials are needed, a
`tools/list`, from a client that identifies itself as `awesome-mcp-servers-probe`. The site then
shows whether it answered, whether it asked for auth, how many tools it has, and roughly how many
tokens its tool definitions cost. It shows what was observed; it does not claim your server was audited.

For servers that list their tools without credentials, the site also publishes each tool's name,
description and input schema as returned, along with any resources and prompts, so people can see
what the server does before connecting it. Nothing is ever called beyond those list requests.

### 5. Write like a directory, not an ad

- Say what it does, not how great it is. Cut "powerful", "seamless", "revolutionary", "the best".
- **No tracking parameters.** `?utm_source=…` and friends get stripped in review.
- No emoji inside entries. The category heading already carries one.
- If your server has a free tier, a required API key, or is read-only, that's genuinely useful — say it in a few words.

### 6. The server has to be real

Before opening the PR, confirm:

- [ ] It speaks MCP (stdio, Streamable HTTP, or SSE) — not just "an API an agent could call".
- [ ] Someone who isn't you can reach it: the repo is public, or the hosted endpoint responds, or the package installs.
- [ ] Every link in your entry resolves.
- [ ] It isn't already in the list. Search `servers/` and the README for the name **and** the domain first.
- [ ] You have the right to list it.

PRs that are pure link-drops for a dead endpoint, or that list the same product under three names, get closed.

## Contributing a reference server to this repo

The folders at the top level are teaching examples. If you want to add one:

- Keep it small and readable. It's here to be understood, not to be exhaustive.
- Python with `uv` matches the existing servers; another stack is fine if the README explains how to run it.
- **Include a `README.md`** in your folder: what it does, tools exposed, prerequisites, how to run it, how to wire it into a client.
- Never commit secrets. Use `.env` (already gitignored) and document the variable names.
- Add a row to the *Servers in this repo* table in the main README, and an entry in `data/reference.json` so it shows on the site.

## Maintaining the site

The `Check servers and publish site` workflow does this every night. To do it by hand:

```bash
git fetch origin status-data && git archive FETCH_HEAD | tar -x -C data              # previous results
GITHUB_TOKEN=$(gh auth token) python3 scripts/probe.py                               # check every server
python3 scripts/build.py --site _site                                                # build the site
mkdir -p _status && cp data/status.json _status/ && cp -R data/tools _status/tools && scripts/push_branch.sh _status status-data "Check results"
scripts/push_branch.sh _site gh-pages "Site"
```

Set the repository variables `SITE_URL` (the site's public address) and `MCP_URL` (the hosted
`directory-mcp` endpoint) to change what the workflow builds with.

## Reporting a problem

- **A listed server is dead, misleading, or malicious** → open an issue with the entry name and what you observed. Verified reports get the entry removed.
- **A security issue in a server in this repo** → open an issue describing the class of problem. Please don't post a working exploit.

## Style

Everything else is ordinary GitHub-flavored Markdown. Match what's already there, keep lines reasonably short, and you're fine.

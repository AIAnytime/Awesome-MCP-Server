# Contributing

Thanks for adding to the list. This file exists because the README grew fast and got messy —
duplicate numbers, entries landing below the license, the same server listed twice. These rules
keep that from happening again. They take two minutes to follow and make your PR mergeable on sight.

## Adding a server to the directory

### 1. One server per pull request

Two servers, two PRs. It keeps review fast and makes a bad entry easy to revert without
taking a good one with it.

### 2. Put it in the right place

Find the category in [`README.md`](README.md#-community-directory) that fits and insert your entry
**in alphabetical order** within that category. If nothing fits, use the closest category and say
so in the PR — don't invent a new one unless you have three or more servers for it.

### 3. Use bullets, never numbers

The list is deliberately unnumbered. Numbered lists collide on every concurrent PR — that's how
the file ended up with two `7.`s and two `12.`s. **Do not renumber anything. Do not add a numbered list.**

### 4. Use the exact entry format

```markdown
- **[Name](https://link-to-repo-or-docs)** `stdio` — One sentence on what it does. Install: `command` · [Docs](https://…)
```

| Field | Rule |
| --- | --- |
| **Name** | The server's real name. Bold, linked to its repo, or its docs if there's no public repo. |
| Transport tag | Exactly one of `` `stdio` `` (runs locally), `` `http` `` (hosted remote), `` `sse` `` (remote over SSE). Omit only if genuinely not a server. |
| Description | One sentence, two at the absolute most. What it does and what it's over. |
| Install / Endpoint | The literal command or URL, in backticks. Optional but appreciated. |
| Extra links | `· [Docs](…)`, `· [Website](…)`, `· Registry: \`id\``. Keep it short. |

A good entry:

```markdown
- **[Parallel Search](https://docs.parallel.ai/integrations/mcp/search-mcp)** `http` — Free live web search and URL fetching, no account or API key. Endpoint: `https://search.parallel.ai/mcp`
```

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
- [ ] It isn't already in the list. Search the README for the name **and** the domain first.
- [ ] You have the right to list it.

PRs that are pure link-drops for a dead endpoint, or that list the same product under three names, get closed.

## Contributing a reference server to this repo

The folders at the top level are teaching examples. If you want to add one:

- Keep it small and readable. It's here to be understood, not to be exhaustive.
- Python with `uv` matches the existing servers; another stack is fine if the README explains how to run it.
- **Include a `README.md`** in your folder: what it does, tools exposed, prerequisites, how to run it, how to wire it into a client.
- Never commit secrets. Use `.env` (already gitignored) and document the variable names.
- Add a row to the *Servers in this repo* table in the main README.

## Reporting a problem

- **A listed server is dead, misleading, or malicious** → open an issue with the entry name and what you observed. Verified reports get the entry removed.
- **A security issue in a server in this repo** → open an issue describing the class of problem. Please don't post a working exploit.

## Style

Everything else is ordinary GitHub-flavored Markdown. Match what's already there, keep lines reasonably short, and you're fine.

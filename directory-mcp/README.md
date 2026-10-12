# Directory MCP Server

Search the [Awesome MCP Servers](https://mcp.aianytime.net/) directory from inside an MCP client, so an agent can find a server for a job on its own.

It reads the directory's public JSON file. No account or API key.

## Tools

- **search_servers(query, category, transport, status, limit)**
  Find servers by keyword, matched against names, descriptions and tool names. Filter by category, by transport (`stdio`, `http`, `sse`), or by what the nightly check saw (`live`, `auth`, `down`, `unprobed`).

- **get_server(slug)**
  Everything known about one server: endpoint, tool names, tool-definition size, check history.

- **list_categories()**
  The categories and how many servers each holds.

`status` is what the nightly check observed. It is not a safety review, and descriptions are written by each server's author.

## Run it locally (stdio)

```bash
uv sync
uv run server.py
```

With Claude Code:

```bash
claude mcp add mcp-directory -- uv --directory /absolute/path/to/Awesome-MCP-Servers/directory-mcp run server.py
```

## Run it as a remote server (Streamable HTTP)

```bash
uv run uvicorn server:app --port 8000
claude mcp add --transport http mcp-directory http://127.0.0.1:8000/mcp
```

The same `app` deploys to any host that runs ASGI apps. It is stateless, so it suits serverless hosting.

## What to read in the code

- One `FastMCP` object serves both transports: `mcp.run()` for stdio, `mcp.streamable_http_app()` for HTTP.
- `stateless_http=True, json_response=True` makes every request stand alone, with no session to keep.
- The data is fetched once and cached for ten minutes, and a failed refresh falls back to the last good copy.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `SITE_URL` | the public site | Where `/` redirects, and the base for `DIRECTORY_URL`. |
| `DIRECTORY_URL` | `$SITE_URL/api/servers.json` | The data file to read. |

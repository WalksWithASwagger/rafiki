# Rafiki MCP

Rafiki ships a local MCP server at `mcp_server.py`. It exposes the common
image-generation functions directly and a constrained bridge to the canonical
`generate.py` CLI for everything else.

The server uses the official Python MCP SDK's `FastMCP` API and runs over
stdio by default, which is the right fit for local desktop tools.

Official SDK reference: https://py.sdk.modelcontextprotocol.io/

## Install For Local Clients

From this checkout:

```bash
./.venv/bin/python -m py_compile mcp_server.py
```

Codex:

```bash
codex mcp add rafiki -- /Users/kk/Code/notion-local/rafiki/.venv/bin/python /Users/kk/Code/notion-local/rafiki/mcp_server.py
```

Claude Code:

```bash
claude mcp add --scope user rafiki -- /Users/kk/Code/notion-local/rafiki/.venv/bin/python /Users/kk/Code/notion-local/rafiki/mcp_server.py
```

Generic MCP JSON:

```json
{
  "mcpServers": {
    "rafiki": {
      "command": "/Users/kk/Code/notion-local/rafiki/.venv/bin/python",
      "args": ["/Users/kk/Code/notion-local/rafiki/mcp_server.py"]
    }
  }
}
```

The server loads `.env` from the Rafiki repo root, so API keys do not need to
be duplicated into every client config.

## Exposed Tools

- `rafiki_status`: show repo paths, which env vars are present, and local
  install commands without exposing secret values.
- `rafiki_generate`: generate one image through the Python core.
- `rafiki_batch`: run an `image-prompts.md` batch with run isolation.
- `rafiki_list_styles`: list style presets and descriptions.
- `rafiki_usage`: return the local usage log.
- `rafiki_run`: run supported `generate.py` workflows without a shell.

## CLI Bridge Examples

`rafiki_run` accepts `generate.py` arguments only. Do not include `python`,
`rafiki`, or `generate.py`.

```json
{"args": ["--usage"]}
{"args": ["view", "rap-all-weeks", "--all-runs"]}
{"args": ["library"]}
{"args": ["registry", "search", "certification"]}
{"args": ["registry", "export", "--format", "json"]}
{"args": ["--render", "/absolute/path/to/card.html"]}
{"args": ["canva-export", "rap-all-weeks", "--no-zip"]}
{"args": ["notion-export", "rap-all-weeks", "--dry-run"]}
{"args": ["regen", "--dry-run"]}
```

`serve` is intentionally blocked in the MCP bridge because it is a long-running
portal process. Start it directly when needed:

```bash
./.venv/bin/python generate.py serve --open
```

## Safety Notes

The MCP server never invokes a shell. `rafiki_run` always executes:

```bash
<python> /Users/kk/Code/notion-local/rafiki/generate.py <args...>
```

Some Rafiki CLI workflows still mutate local state or external systems:
`approve`, `clean`, `canva-export`, `deploy`, `notion-export`, `regen`, and
`social-expand`. The returned JSON includes `mutating: true` for those calls so
MCP clients can surface approvals or logs clearly.


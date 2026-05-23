# Rafiki MCP

Rafiki ships a local MCP server at `mcp_server.py`. It exposes the common
image-generation functions directly, typed wrappers for stable local workflows,
and a constrained bridge to the canonical CLI for everything else.

The server uses the official Python MCP SDK's `FastMCP` API and runs over
stdio by default, which is the right fit for local desktop tools.

Official SDK reference: https://py.sdk.modelcontextprotocol.io/

## Install For Local Clients

From this checkout:

```bash
./.venv/bin/python -m py_compile mcp_server.py
```

Run the spend-free agent smoke before changing MCP or CLI bridge behavior:

```bash
npm run smoke:dry-run
```

The smoke uses a disposable prompt file and output root. It runs the Node CLI in
`--dry-run --json` mode, calls `rafiki_status`, lists MCP tools, runs the MCP
`rafiki_run` bridge in dry-run mode, and checks `archive-health --json` over
the resulting dry-run manifests. It clears provider-key environment variables
inside the smoke process so a passing run never proves live provider access.

Codex:

```bash
codex mcp add rafiki -- /path/to/rafiki/.venv/bin/python /path/to/rafiki/mcp_server.py
```

Claude Code:

```bash
claude mcp add --scope user rafiki -- /path/to/rafiki/.venv/bin/python /path/to/rafiki/mcp_server.py
```

Generic MCP JSON:

```json
{
  "mcpServers": {
    "rafiki": {
      "command": "/path/to/rafiki/.venv/bin/python",
      "args": ["/path/to/rafiki/mcp_server.py"]
    }
  }
}
```

The server loads `.env` from the Rafiki repo root, so API keys do not need to
be duplicated into every client config.

`rafiki_status` returns machine-specific install commands for the current
checkout when you need copy-paste commands for your own client.

## Exposed Tools

- `rafiki_status`: show repo paths, which env vars are present, and local
  install commands without exposing secret values.
- `rafiki_generate`: generate one image through the Python core.
- `rafiki_batch`: run an `image-prompts.md` batch with run isolation.
- `rafiki_list_styles`: list style presets and descriptions.
- `rafiki_usage`: return the local usage log.
- `rafiki_registry_search`: search the persisted asset registry by title,
  caption, and tags.
- `rafiki_registry_export`: export the registry to CSV or JSON.
- `rafiki_archive_health`: report missing images, malformed manifests,
  duplicate filenames, sidecar orphans, and cleanup guidance without writing
  files.
- `rafiki_viewer_rebuild`: rebuild project, run, or approved viewers without
  regenerating images.
- `rafiki_library_rebuild`: check or rebuild the master `library.html` archive
  viewer without regenerating images.
- `rafiki_render`: render one HTML file or a directory of HTML files to PNG.
- `rafiki_canva_export`: build a Canva bulk-upload bundle from approved or
  latest-run images.
- `rafiki_notion_export`: dry-run or export approved/latest-run images to a
  Notion gallery database.
- `rafiki_run`: run supported fallback CLI workflows without a shell.

Typed workflow tools return stable JSON with `success`, `ok`, `tool`,
`dry_run`, `mutating`, and `external` fields, plus workflow-specific paths,
URLs, counts, stdout/stderr, or error details. `success` is kept for existing
clients; new clients should read `ok`.

## Typed Workflow Examples

Asset registry:

`rafiki_registry_search`:

```json
{"query": "certification", "limit": 10}
```

`rafiki_registry_export`:

```json
{"format": "json", "dry_run": true}
```

Archive health:

`rafiki_archive_health`:

```json
{"output_root": "/absolute/path/to/output", "cleanup_report": true}
```

Viewers:

`rafiki_viewer_rebuild`:

```json
{"project": "rap-all-weeks", "all_runs": true, "dry_run": true}
```

`rafiki_viewer_rebuild`:

```json
{"project": "rap-all-weeks", "approved": true}
```

`rafiki_library_rebuild`:

```json
{"output_root": "/absolute/path/to/output", "dry_run": true}
```

`rafiki_library_rebuild`:

```json
{"output_root": "/absolute/path/to/output", "dry_run": false}
```

HTML rendering:

`rafiki_render`:

```json
{"html_path": "/absolute/path/to/card.html", "dry_run": true}
```

`rafiki_render`:

```json
{"html_dir": "/absolute/path/to/cards"}
```

Canva and Notion export:

`rafiki_canva_export`:

```json
{"project": "rap-all-weeks", "dry_run": true}
```

`rafiki_canva_export`:

```json
{"project": "rap-all-weeks", "no_zip": true}
```

`rafiki_notion_export`:

```json
{"project": "rap-all-weeks", "database_id": "notion-db-id", "dry_run": true}
```

`rafiki_notion_export`:

```json
{"project": "rap-all-weeks", "database_id": "notion-db-id", "dry_run": false}
```

## CLI Bridge Examples

`rafiki_run` is still available for less common workflows. It accepts Rafiki
CLI arguments only. Do not include `python`, `rafiki`, or `generate.py`.
Prefer the typed tools above for registry, viewer rebuild, render, Canva, and
Notion workflows.

```json
{"args": ["--usage"]}
{"args": ["library"]}
{"args": ["archive-health", "--json"]}
{"args": ["archive-health", "--cleanup-report"]}
{"args": ["approve", "rap-all-weeks", "--run", "20260507-100000"]}
{"args": ["clean", "rap-all-weeks", "--dry-run"]}
{"args": ["billing", "summary", "--json"]}
{"args": ["social-expand", "rap-all-weeks", "--dry-run"]}
{"args": ["regen", "--dry-run"]}
```

`serve` is intentionally blocked in the MCP bridge because it is a long-running
portal process. Start it directly when needed:

```bash
./.venv/bin/python generate.py serve --open
```

## Safety Notes

The MCP server never invokes a shell. `rafiki_run` Python workflows execute:

```bash
<python> /path/to/rafiki/generate.py <args...>
```

Render-only bridge calls execute:

```bash
node /path/to/rafiki/index.js <args...>
```

Typed tools mark local writes and external calls explicitly. `rafiki_archive_health`
is always read-only and returns `mutating: false`. Registry export, viewer
rebuild, library rebuild, render, and Canva export are local mutations when
`dry_run` is false. Notion export is external and only mutates remote Notion
state plus the local export log when `dry_run` is false.

Dry-run wrappers do not stamp archive metadata or write generated outputs.
They only report the paths, URLs, counts, commands, and errors a real run would
use when the underlying workflow exposes enough information to preview safely.

Some fallback CLI workflows still mutate local state or external systems:
`approve`, `billing import`, `clean`, `deploy`, `regen`, and `social-expand`.
The returned JSON includes `mutating: true` for those calls so MCP clients can
surface approvals or logs clearly. Use each workflow's own `--dry-run` flag
where available.

# Notion Export

Push approved Rafiki images to a Notion gallery database.

## One-time Notion setup

1. **Create an internal integration**
   Go to <https://www.notion.so/my-integrations> → *New integration* → name it
   "Rafiki Exporter" → *Submit*. Copy the **Internal Integration Secret**
   (`secret_…`).

2. **Create or pick a database** with these properties (exact names matter):

   | Property      | Type      | Required |
   |---------------|-----------|----------|
   | `Name`        | Title     | yes      |
   | `Caption`     | Rich text | yes      |
   | `Week`        | Select    | optional |
   | `Source Run`  | Rich text | yes      |
   | `Image`       | Files     | yes      |

3. **Share the database with the integration.** Open the database page,
   click *Share* (or `…` → *Connections*), invite the "Rafiki Exporter"
   integration. Without this step every API call returns 404.

4. **Copy the database id** from its URL:
   `https://www.notion.so/<workspace>/<DATABASE_ID>?v=…` — the 32-char hex
   chunk before `?v=`.

5. **Add to `.env`** (next to `generate.py`):

   ```
   NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

## Usage

```bash
# Dry run — print what would be uploaded, no API calls
python generate.py notion-export my-project --dry-run

# Real export (uses $NOTION_DATABASE_ID)
python generate.py notion-export my-project

# Override the database
python generate.py notion-export my-project --database <other-db-id>

# Re-export images already pushed
python generate.py notion-export my-project --force
```

Source preference: `output/<project>/approved/` if present, otherwise the
latest `run-*/`. Captions come from `index.json` / `run.json` (the `caption`
field, falling back to `prompt`). Week is derived from `week-NN` in the
filename when present.

## Idempotency

A local file `output/<project>/.notion-exported.json` records every
`(database_id, filename)` pair already pushed. Re-running skips them. This
file is git-ignored — it is a local cache, not part of the project.

# Asset Registry

A lightweight, cross-project searchable index of generated images. Built by
walking every project in `output/` (plus any extras from
`config/extra-outputs.json` and `config/extra-outputs.local.json`), preferring
an `approved/` subdir and falling back to the latest `run-*` dir.

The registry is a **local cache** — `data/asset-registry.json` and
`data/asset-registry.csv` are gitignored. Regenerate any time.

## Schema (`AssetEntry`)

| field | type | source |
|---|---|---|
| `id` | str | `<project>-<png-stem>` |
| `project` | str | dir name under `output/` or key in the extra-output config |
| `title` | str | `viewer-data.json` → `run.json` `name` → derived from filename |
| `caption` | str | `viewer-data.json` → `run.json` `prompt` |
| `tags` | list[str] | `viewer-data.json` + `run.json` tags + `aspect_ratio` |
| `approval_status` | str | `approved` when sourced from `approved/`, otherwise `unapproved` |
| `source_prompt` | str | approval index prompt → `run.json` image prompt |
| `style` | str | `run.json` |
| `model` | str | `run.json` |
| `aspect_ratio` | str | `run.json` |
| `source` | str | `approved` or `latest-run` |
| `source_run` | str | source run id when known |
| `indexed_at` | str (ISO) | timestamp of `index()` call |
| `path` | str | image path, repo-root-relative when possible |

## CLI

```bash
generate.py registry index                  # rebuild data/asset-registry.json
generate.py registry search "hallucination" # case-insensitive, title+caption+tags
generate.py registry search "bias" --json   # JSON output
generate.py registry export --format csv    # → data/asset-registry.csv
generate.py registry export --format json   # → data/asset-registry.json
```

## When to re-index

- After a batch run produces a new `run-*` dir
- After moving/curating images into a project's `approved/` dir
- Before exporting to Notion / Canva / a spreadsheet

## Library viewer

The master library viewer (`generate.py library`) uses the same registry
metadata loader as `generate.py registry index`. It does not require a prebuilt
`data/asset-registry.json`: when you build the library, Rafiki reads
`approved/` first and falls back to the latest `run-*` directory for output-only
projects.

Library cards show registry-grade title, caption, tags, approval status, source
prompt, model, style, and aspect ratio when those fields are available.

# Asset Registry

A lightweight, cross-project searchable index of generated images. Built by
walking every project in `output/` (plus any extras from
`config/extra-outputs.json` and `config/extra-outputs.local.json`), preferring
an `approved/` subdir and falling back to the latest `run-*` dir.

The registry also has an archive scope for the master library: `all-runs`
indexes every historical `run-*` image so Rafiki can show the full local
generation history without exporting every draft by default.

The registry is a **local cache** — `data/asset-registry.json` and
`data/asset-registry.csv` are gitignored. Regenerate any time.

## Schema (`AssetEntry`)

| field | type | source |
|---|---|---|
| `id` | str | `<project>-<png-stem>` in curated scope; `<project>-<run-id>-<png-stem>` in all-runs scope |
| `project` | str | dir name under `output/` or key in the extra-output config |
| `title` | str | `viewer-data.json` → `run.json` `name` → derived from filename |
| `caption` | str | `viewer-data.json` → `run.json` `prompt` |
| `tags` | list[str] | `viewer-data.json` + `run.json` tags + `aspect_ratio` |
| `approval_status` | str | `approved` when sourced from `approved/`, otherwise `unapproved` |
| `metadata_states` | list[str] | local `output/archive-metadata.json` states keyed by `project/run/file` or `project/approved/file` |
| `export_status` | str | comma-separated `canva`/`notion` states from `metadata_states` |
| `publish_status` | str | comma-separated `deployed`/`published` states from `metadata_states` |
| `superseded_by` | str | local `output/archive-metadata.json` supersession target |
| `source_use_case` | str | public-safe use case, talk, article, or campaign label from archive metadata |
| `source_url` | str | optional public source URL from archive metadata |
| `prompt_pack` | str | repo-relative prompt pack path or stable prompt-pack label from archive metadata |
| `prompt_pack_section` | str | prompt-pack section or slide/asset beat from archive metadata |
| `artifact_review_state` | str | `approved`, `rejected`, `regenerate`, or `manual-rebuild` from archive metadata |
| `export_targets` | list[str] | intended export destinations such as `canva`, `deck`, or `site` |
| `downstream_uses` | list[str] | artifact uses such as `slide`, `blog-post`, `guide`, or `speaker-kit` |
| `source_prompt` | str | approval index prompt → `run.json` image prompt |
| `style` | str | `run.json` |
| `model` | str | `run.json` |
| `aspect_ratio` | str | `run.json` |
| `source` | str | `approved`, `latest-run`, or `run` |
| `source_run` | str | source run id when known |
| `indexed_at` | str (ISO) | timestamp of `index()` call |
| `path` | str | image path, repo-root-relative when possible |

CSV exports use the same stable state columns: `approval_status`,
`metadata_states`, `export_status`, `publish_status`, `superseded_by`, and the
artifact-chain fields from `output/archive-metadata.json`. Registry export
reads archive metadata but does not stamp or mutate that sidecar.

## CLI

```bash
generate.py registry index                  # rebuild curated data/asset-registry.json
generate.py registry index --all-runs       # persist the complete local archive
generate.py registry search "hallucination" # case-insensitive, title+caption+tags
generate.py registry search "bias" --json   # JSON output
generate.py registry export --format csv    # → data/asset-registry.csv
generate.py registry export --format json   # → data/asset-registry.json
```

## Automatic vs manual refresh

The curated registry cache refreshes automatically after successful non-dry-run
local mutations that change the archive surface:

- Python CLI batch generation and portal Prompt Studio generation
- `generate.py approve` when it promotes at least one starred asset
- Portal curation/export actions that stamp approval, Canva, Notion, or deploy
  state back into `output/archive-metadata.json`
- Portal **Registry Export**, which refreshes before writing CSV or JSON

Dry-runs, failed generation runs, failed export actions, and no-op approvals do
not mutate `data/asset-registry.json`.

Run a manual refresh when files were changed outside Rafiki, when extra output
roots changed, or when you want the complete archive instead of the curated
approved/latest-run view:

```bash
generate.py registry index
generate.py registry index --all-runs
```

## Library viewer

The master library viewer (`generate.py library`) uses the registry's all-runs
metadata loader. It does not require a prebuilt `data/asset-registry.json`: when
you build the library, Rafiki scans every `run-*` directory under `output/` and
configured extra-output roots. The default `registry index` command stays
curated because CSV, Notion, and Canva exports usually want keepers, not every
draft.

Library cards show registry-grade title, caption, tags, approval status, source
prompt, model, style, and aspect ratio when those fields are available. The
library also merges local card metadata from `output/archive-metadata.json`,
which can override display titles, add review tags, show export/publish states,
and carry artifact-chain provenance without changing the generated run
manifests.

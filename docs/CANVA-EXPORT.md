# Canva Export

Bundle a project's images plus a metadata CSV for drag-and-drop bulk upload
into Canva. No Canva API or hosted viewer required.

## Usage

```bash
# Default: produces output/<project>/canva-export.zip
python generate.py canva-export rap-all-weeks

# Skip zipping — leave the dir for inspection
python generate.py canva-export rap-week-1 --no-zip

# Custom output location
python generate.py canva-export rap-week-1 --output /tmp/my-bundle
```

## Source preference

1. `output/<project>/approved/` — curated handoff set, if present.
2. Latest `output/<project>/run-*/` — fallback when no approval folder exists.

## Output layout

```
output/<project>/canva-export/
├── images/              # PNG copies, original filenames preserved
└── assets.csv           # one row per image, all fields quoted
output/<project>/canva-export.zip   # the same, zipped
```

`assets.csv` columns: `filename, title, caption, week, social_post,
aspect_ratio, source_run, prompt`.

## Metadata enrichment

- If a project ships an optional viewer-data metadata file, captions/social
  copy are pulled from it if present (see issue #18). A missing file is handled
  gracefully — the columns simply come back empty.
- For non-RAP projects, `title` falls back to a Title-Case version of the
  filename slug; `caption`, `week`, and `social_post` are empty.

## Phase 4 follow-on

Direct Canva-API upload via the `mcp__claude_ai_Canva__upload-asset-from-url`
tool requires the images to be reachable over HTTP — that work is gated on
the hosted viewer in Phase 4 and tracked separately.

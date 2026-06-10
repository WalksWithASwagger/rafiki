# Presentation Viewer

`generate-presentation-viewer.py` builds a polished, single-file HTML viewer for a
series of generated images. It produces a static `viewer.html` with:

- header (title + subtitle + style attribution)
- category filter tabs (e.g. "All", "Week 1", "Week 2", …)
- live search across titles and captions
- responsive card grid with optional square-aspect override
- lightbox with prev/next navigation, keyboard shortcuts, download link
- ready-to-post social copy with one-click clipboard copy, including
  platform tabs for LinkedIn, X, and Instagram when `social-posts.json`
  is present beside a run
- "Export social posts" button (controls bar) that downloads all flagged
  posts as a single `.txt` — appears only when at least one item has a
  non-null `social` field or platform variants
- companion `social-posts.md` written next to `viewer.html` with one
  section per flagged item — written only when the data has social items

The viewer logic is identical for every series — only the data changes.

## Usage

```bash
python generate-presentation-viewer.py \
    --data <path/to/data.json> \
    --output <path/to/output-dir> \
    [--title "Optional title override"] \
    [--self-contained] \
    [--max-width 1200]
```

The script writes `<output-dir>/viewer.html` and resolves image `src` paths
relative to that output directory.

### Flags

| Flag | Default | Description |
|---|---|---|
| `--data` | required | Path to the JSON data file. |
| `--output` | required | Output directory. `viewer.html` is written here. |
| `--title` | from data | Override the `title` field from the JSON. |
| `--self-contained` | off | Embed every image as a base64 `data:` URI so the rendered HTML is a single portable file with no companion image directory. |
| `--max-width N` | none | When used with `--self-contained`, resize each image to a max width of `N` pixels (preserving aspect ratio) before encoding. Has no effect without `--self-contained` and emits a warning in that case. |

### Portable single-file mode

By default, the viewer references images via relative paths
(`src="../../output/.../slug.png"`), which means the rendered HTML is only
useful next to its image directory. With `--self-contained`, every image is
read from disk, optionally resized, base64-encoded, and embedded directly in
the HTML — so a single `.html` file can be emailed, dropped into a Slack
channel, or hosted anywhere with no companion assets.

The trade-off is file size. Embedding 40 PNGs at full resolution (1536×1024)
produces a viewer in the ~120 MB range. Using `--max-width 1200` brings each
image down to roughly 1.5–2 MB after re-encoding, but PNG is a lossless
format and the totals add up quickly. If file size matters, prefer
`--max-width 800` or smaller. The script prints the final file size after
writing and emits a warning to stderr when the embedded payload exceeds 50 MB.

```bash
# Single portable file, images capped at 1200 px wide
python generate-presentation-viewer.py \
    --data prompts/<series>/viewer-data.json \
    --output /tmp/series-viewer \
    --self-contained \
    --max-width 1200
```

## Wrappers

No wrappers ship in this repo. A wrapper is just a four-line
`subprocess.run(...)` around `generate-presentation-viewer.py` that pins a data
file and output directory — keep series-specific wrappers in your own working
directory rather than in the public tool.

## JSON schema

```jsonc
{
  "title": "Series Title",                 // shown in header H1
  "subtitle": "Series subtitle",           // shown under H1
  "page_title": "Browser tab <title>",     // optional, defaults to title
  "header": {
    "logo": "🌲",                          // single glyph or emoji
    "style_label": "bcai",                 // bold gold word in header-right
    "style_meta": "style · gpt-image-2",   // muted text after style_label
    "style_description": "BC old-growth forest visual language"
  },

  "category_field": "week",                // informational; the JSON key that groups items
  "category_label_singular": "Week",       // used in CLI summary output
  "all_tab_label": "All Weeks",            // text on the "show everything" tab

  "categories": [
    {
      "id": 1,                             // integer, matches item.category
      "label": "Week 1 — Foundations",     // long form, shown in lightbox badge
      "short": "W1",                       // shown in card badge
      "tab_label": "Week 1 — Foundations"  // optional, defaults to label
    }
  ],

  "image_dirs": {
    "1": "output/<series>-1/run-20260502-204603"  // dir per category id
  },

  "items": [
    {
      "category": 1,                       // matches a category id
      "slug": "01-data-as-structured-observation",  // <slug>.png inside image_dir
      "title": "Card title",
      "caption": "One-line description shown on the card and lightbox.",
      "social": null,                      // or a string with the post text
      "socialPlatforms": {                 // optional; normally loaded from social-posts.json
        "linkedin": "LinkedIn-ready copy",
        "x": "X-ready copy",
        "instagram": "Instagram-ready copy"
      },
      "square": false                      // optional; render this card 1:1 instead of 16:9
    }
  ]
}
```

### Image path resolution

For each item, the viewer expects `<image_dir>/<slug>.png`. `image_dir` values
in the JSON are resolved relative to the repo root (where
`generate-presentation-viewer.py` lives), or used as-is when absolute. The
resulting `src` in the generated HTML is computed with `os.path.relpath`
against the output directory, so `--output` can point anywhere — to `/tmp`,
to a sibling project, etc.

### Platform social tabs

When an image directory contains `social-posts.json` from
`python generate.py social-expand <project>`, the presentation viewer loads
the matching entry by item `slug` and embeds its `platforms` map into the
viewer. The lightbox then shows tabs for LinkedIn, X, and Instagram. If the
item also has the legacy `social` string, that copy remains available as an
`Original` tab, so existing viewer data and exports keep working.

## Adding a new content series

1. **Drop your images in a known directory**, one per slug, named `<slug>.png`.
   Group them by category if you want the filter tabs.
2. **Write a JSON data file** following the schema above. Put it next to your
   prompts (e.g. `prompts/<series>/viewer-data.json`).
3. **Generate the viewer:**
   ```bash
   python generate-presentation-viewer.py \
       --data prompts/<series>/viewer-data.json \
       --output output/<series>-viewer
   ```
4. **(Optional) Add a wrapper** in your own working directory if you'll
   regenerate often — a four-line `subprocess.run([...])` around
   `generate-presentation-viewer.py` with the data file and output dir pinned.

## Worked example: podcast episode thumbnails

Imagine a podcast where each season's episode covers should be browsable as a
single viewer, with per-season filter tabs.

`prompts/pod/viewer-data.json`:

```json
{
  "title": "Old Growth Pod — Cover Library",
  "subtitle": "Three seasons · 36 episode covers",
  "header": {
    "logo": "🎙",
    "style_label": "old-growth",
    "style_meta": "style · midjourney v7",
    "style_description": "moss, fog, low gold light"
  },
  "category_field": "season",
  "category_label_singular": "Season",
  "all_tab_label": "All Seasons",
  "categories": [
    {"id": 1, "label": "Season 1 — Foundations", "short": "S1"},
    {"id": 2, "label": "Season 2 — The Field", "short": "S2"},
    {"id": 3, "label": "Season 3 — The Network", "short": "S3"}
  ],
  "image_dirs": {
    "1": "output/pod/season-1",
    "2": "output/pod/season-2",
    "3": "output/pod/season-3"
  },
  "items": [
    {"category": 1, "slug": "01-pilot",
     "title": "Episode 01 — The Pilot",
     "caption": "Why we're recording in a forest.",
     "social": "New podcast: Old Growth. Episode 01 is up.\n\n#podcast #oldgrowth"},
    {"category": 1, "slug": "02-the-canopy",
     "title": "Episode 02 — The Canopy",
     "caption": "What lives 60 metres up.",
     "social": null}
  ]
}
```

Build it:

```bash
python generate-presentation-viewer.py \
    --data prompts/pod/viewer-data.json \
    --output output/pod-viewer
open output/pod-viewer/viewer.html
```

The same tabs, lightbox, and social-copy UX as the RAP viewer — no template
changes required.

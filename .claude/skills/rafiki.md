---
name: rafiki
description: Generate images using Rafiki — Gemini Nano Banana or OpenAI gpt-image-2. Use when asked to generate, create, or make images for content, social posts, articles, or brand assets. Also triggered when a batch prompt file (image-prompts.md) needs processing.
---

# Rafiki Image Generator

Invoke Rafiki to generate AI images (single or batch) using Gemini or OpenAI models.

## When to use

- User asks to generate / create / make images
- A prompt file (`image-prompts.md`) exists and needs processing
- Social, article, or brand imagery is needed
- Another agent or skill needs images as output

## Quick reference

```bash
# Single image — Gemini (default, free tier)
rafiki --prompt "Describe the image..." --output image.png

# Single image — OpenAI gpt-image-2 (best text rendering)
rafiki --prompt "..." --model gpt-image-2 --quality high

# Batch from prompt file (auto-generates viewer.html)
rafiki path/to/image-prompts.md --output-dir ./images/

# With style
rafiki --prompt "..." --style kk         # BC+AI dark editorial
rafiki --prompt "..." --style hopecode   # solarpunk mycelial
rafiki --prompt "..." --style bcai       # BC AI Community Centre
rafiki --prompt "..." --style upgrade    # bold transformation

# JSON output (for agent/pipeline use)
rafiki --prompt "..." --json

# Dry run (preview without API call)
rafiki --prompt "..." --dry-run

# List styles
rafiki --list-styles
```

## Key flags

| Flag | Default | Notes |
|------|---------|-------|
| `--model` | `gemini-2.5-flash-image` | Also: `gpt-image-2`, `gemini-3-pro-image-preview`, `dall-e-3` |
| `--style` | `kk` | kk / hopecode / bcai / upgrade / none |
| `--aspect-ratio` | `16:9` | Also: `1:1`, `9:16`, `linkedin`, `instagram`, `story` |
| `--quality` | `high` | OpenAI only: `low` / `medium` / `high` |
| `--resolution` | `1K` | Gemini Pro only: `2K` / `4K` |
| `--json` | off | Machine-readable output, progress to stderr |
| `--no-viewer` | off | Skip viewer.html after batch |
| `--dry-run` | off | No API calls, shows what would happen |

## Prompt file format (`image-prompts.md`)

```markdown
## 1. Card Name

**For:** where this image will be used

**Prompt:**
> The actual image description here.
> Can span multiple lines.

## 2. Another Image
...
```

## Environment

- `GOOGLE_API_KEY` — required for Gemini models
- `OPENAI_API_KEY` — required for gpt-image-* / dall-e-* models

## Invocation from kk-kb

Rafiki lives at `../rafiki/` relative to kk-ai-ecosystem. Run from that directory
or use the `RAFIKI_HOME` env var:

```bash
cd /path/to/rafiki && npx rafiki --prompt "..." --style kk
# or
RAFIKI_HOME=/path/to/rafiki node tools/image-gen/launch.js --prompt "..."
```

## After a batch run

- Images land in `--output-dir` (default: `<prompt-file-dir>/images/`)
- `viewer.html` is auto-generated — open it in a browser: prompts on cards, lightbox with download + copy-prompt, grid resize slider, star/reject ratings
- JSON output (`--json`) returns paths to all images + viewer for pipeline use

## Viewer maintenance

```bash
# Rebuild comparison viewer from disk (no re-generation)
python generate.py view <project>
python generate.py view philadelphia --all-runs   # also rebuild per-run viewers

# Master library — all projects in one page with filter chips
python generate.py library
python generate.py library --open                 # build + open in browser
```

The library viewer lives at `output/library.html`. It scans all `output/*/run-*/run.json`, re-verifies which files exist on disk, and generates a filterable grid by project and model.

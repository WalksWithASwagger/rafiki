# Floyo Video Workflows

Rafiki can drive [Floyo](https://flowyo.ai) — a hosted ComfyUI service — to render short
video clips from a workflow template. This is the first slice of folding the
[alex-samuel](PERSONAL-MEDIA-SUITE.md) film pipeline into Rafiki.

**Dry-run-first.** Nothing uploads, submits, or downloads unless you pass `--execute`. The
only thing that spends FloTime is `--execute`.

## Setup

Add a key to `.env` (never commit it):

```bash
FLOYO_KEY=...   # from https://flowyo.ai
```

## Workflows

Templates live in `config/floyo_workflows/` as ComfyUI API-format graphs plus an
`inputmaps.json` that maps named input slots to nodes.

- **`wan22_endframe`** — morph a start image into an end image as a short (~3s), silent,
  RIFE-interpolated clip. Slots: `start_image`, `end_image`, `prompt`.

## CLI

```bash
# Dry-run (no network, no spend): plan the run and write a manifest
python generate.py floyo generate \
  --workflow wan22_endframe \
  --set start_image=plateA.jpg \
  --set end_image=plateB.jpg \
  --set prompt="slow push-in, glam space opera" \
  --project andromeda

# Real run: upload, submit, poll, and download the clip
python generate.py floyo generate --workflow wan22_endframe \
  --set start_image=plateA.jpg --set end_image=plateB.jpg \
  --set prompt="..." --project andromeda --execute
```

Add `--no-wait` to submit without polling/downloading, `--json` for machine output, and
`-d/--output-dir` to override the output root. Output clips land in
`output/<project>/floyo-run-<stamp>/` (gitignored).

## MCP

`rafiki_floyo_generate(workflow="wan22_endframe", start_image, end_image, prompt, project,
execute=False, output_root="")` plans the run and, on `execute`, **submits only** (it does
not block-poll). Use the CLI to wait for and download the clip. Output follows the
[MCP output contract](MCP-OUTPUT-CONTRACT.md).

## Billing

Floyo bills in FloTime hours; Rafiki does not estimate spend locally (cost `amount` is
`null` on execute). Use Floyo's billing for exact charges.

## Boundary

The workflow templates are tool config and live in git. Generated clips and any private
plates stay in gitignored local roots — never committed. See
[PROMPT-MEDIA-POLICY.md](PROMPT-MEDIA-POLICY.md).

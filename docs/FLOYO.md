# Floyo Video Workflows

Rafiki can drive [Floyo](https://flowyo.ai) — a hosted ComfyUI service — to render short
video clips from a workflow template. This is the first slice of folding the
[alex-samuel](PERSONAL-MEDIA-SUITE.md) film pipeline into Rafiki.

Need a full narrative / explainer / promo video from a prompt or script instead?
Use hosted **AgentOpus MCP** — see [`AGENT-OPUS-MCP.md`](./AGENT-OPUS-MCP.md).

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
- **`infinitetalk`** — audio-driven lip-sync from a single still (the singing shots). Slots:
  `image`, `audio` (an audio file), `prompt`, plus optional `max_frames`, `width`, `height`.
- **`multitalk`** — multi-person lip-sync. Slots: `image`, `audio`, `prompt`.

Audio slots upload the file and pass its `#inputs/` reference to the workflow's audio loader.

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

# Lip-sync (singing shot)
python generate.py floyo generate --workflow infinitetalk \
  --set image=singer.jpg --set audio=vocal.mp3 \
  --set prompt="singing to camera, glam space opera" --project andromeda --execute
```

Add `--no-wait` to submit without polling/downloading, `--json` for machine output, and
`-d/--output-dir` to override the output root. Output clips land in
`output/<project>/floyo-run-<stamp>/` (gitignored).

### Scoring silent clips

`wan22_endframe` clips come back silent. Lay the song over one with ffmpeg (dry-run first):

```bash
python generate.py floyo mux --video clip.mp4 --audio song.mp3 --audio-start 5 --execute
# -> writes clip_scored.mp4 (video copied, audio re-encoded, trimmed to the clip)
```

Local only — no provider spend. **Do not** mux over a lip-sync (`infinitetalk`/`multitalk`)
clip: its vocal is already embedded and drives the lips.

## Keyframes (stills) — Replicate, not Floyo

Floyo/FloTime is a **video** backend and **cannot load FLUX image LoRAs**, so the keyframe
*stills* that feed these workflows are generated on **Replicate** (FLUX + the trained
character image LoRA, e.g. `walkswithaswagger/alexandra-samuel`). Floyo then animates them.

```bash
# from a project dir with keyframes.json + REPLICATE_API_TOKEN in rafiki/.env
python generate.py keyframes generate --beat situ_02_backstage --num-outputs 4 --execute
# or by number:  --beat 02
```

`keyframes.json` holds `settings` (the LoRA model `version`, aspect ratio, steps, guidance,
`lora_scale`, output format) and `beats` (each with a `prompt`). Stills land in
`output/keyframes/<beat>/keyframe-run-<stamp>/` (gitignored). Replicate is the **backup**
provider generally — but it is the only engine for FLUX-image-LoRA stills.

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

---
name: real-sky-poster
description: Replace invented constellations in artwork with the real sky for a given date and place, then export a full sized asset kit. Auto-triggers on "the constellations are wrong/fake/bullshit", "make the stars accurate", "real constellations", "what did the sky actually look like on <date>", "fix the sky in this poster", "build an asset kit from this artwork".
---

# Real Sky Poster

Take artwork with a made-up night sky, give it the sky that was actually there, and ship every size the campaign needs.

## Success Criteria

Done when all of these hold:

- [ ] **The sky is real.** Every star is a catalogue star at its true magnitude; every figure has its true shape and its true rotation against the horizon for the stated date, time and location.
- [ ] **The astronomy gate passes.** `python3 tests/skills/real-sky-poster/test_sky.py` is green. Polaris altitude equals the observer's latitude, or the reduction is wrong.
- [ ] **Nothing below the horizon is drawn.** If a constellation had not risen, it is not in the picture. Say so rather than faking it.
- [ ] **The artwork is untouched.** `plate.disturbance()` returns a number in the low hundreds. Thousands means the wipe ate somebody's painting — stop and fix the geometry.
- [ ] **Stars are native at every size.** No output contains an upscaled star.
- [ ] **No crop discards constellations.** Tall formats extend the sky; they do not centre-crop.
- [ ] **Copy is verbatim.** Every word traces to a source file. Nothing drafted, nothing paraphrased.
- [ ] Every exported file hits its exact pixel dimensions.

## Why not just regenerate the image

Because it will not work. An image model asked for "accurate constellations" produces a *fresh set of hallucinated star patterns* — the same failure in a new arrangement. Star positions are exact data. Port the data; do not ask a model to imagine it.

This is the same lesson as optical illusions: when the output must be *correct*, compute it, don't generate it.

## Instructions

### Inputs

A **profile** (`profiles/<name>.json`) carrying:

| Field | What it is |
|---|---|
| `source` | path to the artwork (never committed — see [Boundary](#boundary)) |
| `observer` | `utc` (**UTC, not local** — the easiest way to draw the wrong sky), `lat`, `lon` |
| `protect` | boxes the wipe must never touch: type, figures, anything painted |
| `horizon` | the top edge of the painted mass; above it is open sky |
| `layout` | where each figure sits, and at what scale |
| `zenith` | figures for the extended sky in tall formats |
| `copy` | approved strings + palette |

`profiles/futureproof-salmon-starfield.json` is the worked example.

### Stages

Run in order. Each stage is independently inspectable — look at the output before moving on.

```
1. plate.py    wipe the invented sky, keep the aurora and the brushwork
               -> check disturbance(); should be low hundreds
2. upscale.py  4x the CLEAN PLATE with a local ESRGAN (free, on-device)
3. render.py   draw the real stars at target scale — natively, never upscaled
4. kit.py      extend the sky for tall formats, set type, export every size
```

**Stage order is the whole trick.** Upscale the *plate*, then redraw the stars. Upscaling a finished poster gives you 4x-blurry stars; this gives you 4x sharp ones. It also means the upscaler never sees a fabricated dot it might sharpen into an artifact.

### Placing figures

Shape and rotation are computed. **Placement is composed** — and you should say so out loud rather than overclaim. Honest framing: *"every figure has its true shape and orientation; where each sits on the canvas is arranged to fit the art, following the real bearings."*

Read `Sky.report()` first, then place west-bearing figures left, north low and central, east right. That arrangement is usually a gift: it gave the Futureproof poster "summer setting on one side, winter rising on the other."

### Growing the canvas, not cropping it

A 16:9 painting cropped to 1:1 loses its left and right edges — exactly where the constellations live. So tall formats **grow upward**. Upward is toward the zenith, which is where the figures that could not fit the wide frame actually were. The square gains real sky instead of losing it.

## Quality Check

- [ ] Did I check `Sky.report()` before placing anything, or did I assume?
- [ ] Is anything drawn that was below the horizon?
- [ ] Did `disturbance()` stay low, and did I *look* at a 100% crop of the artwork's fine detail?
- [ ] Did I A/B the upscale against plain Lanczos before trusting it? (Photo-trained models plasticize brushwork — use an illustration model, never `RealESRGAN_x4plus`.)
- [ ] Does any asset stack a second wordmark on artwork that already has one?
- [ ] Is every string traceable to a source file?

## HITL Checkpoint

**Type:** Two checkpoints, because the two halves fail differently.

**Checkpoint 1 — after the sky (stage 3).** Show the corrected artwork and an annotated key naming each constellation with its real bearing and altitude. The key is what lets a human *check the claim* instead of taking it on faith.

Human reviews:
- [ ] Does the sky look right, and does the key survive a fact-check?
- [ ] Is the artwork genuinely untouched at 100%?

**Checkpoint 2 — before publish.** The kit is a marketing artifact.

Human reviews:
- [ ] Is the copy the approved copy?
- [ ] Do the story safe areas hold?
- [ ] Any brand conflict surfaced rather than silently resolved?

**Surface conflicts, never resolve them silently.** The Futureproof run turned up two (an OG size that disagreed between code and spec; two competing wordmarks). Both went in the PR body for a human to rule on.

## Boundary

Rafiki's public repo is **tool-only**. Artwork, generated assets and campaign copy are gitignored and live in the private knowledge base. This skill ships **code and geometry**; profiles reference artwork by path and never embed it. The smoke test runs with no image, no GPU and no network — which is also why the astronomy is standard-library only.

## Setup

Two assets are fetched, not committed (both are binaries, and the repo is tool-only):

```bash
# Upscale weights — an ILLUSTRATION model. Never RealESRGAN_x4plus on painted art.
curl -L -o ~/Code/ComfyUI/models/upscale_models/4x-UltraSharp.pth \
  https://huggingface.co/Kim2091/UltraSharp/resolve/main/4x-UltraSharp.pth

# Type faces for stage 4 (swap for whatever the brand actually uses)
mkdir -p .claude/skills/real-sky-poster/scripts/fonts
curl -L -o .claude/skills/real-sky-poster/scripts/fonts/Inter.ttf \
  'https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf'
curl -L -o .claude/skills/real-sky-poster/scripts/fonts/Cormorant.ttf \
  'https://raw.githubusercontent.com/google/fonts/main/ofl/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf'
```

Stages 1–3 need only `opencv-python`, `pillow`, `numpy`. Stage 2 runs on ComfyUI's venv (torch + MPS + spandrel already there). **The smoke test needs none of this** — that is the point of keeping the astronomy in the standard library.

## Reference

- Worked example: the Futureproof salmon-starfield poster — [WalksWithASwagger/futureproof-festival#644](https://github.com/WalksWithASwagger/futureproof-festival/pull/644)
- Star data: Bright Star Catalogue, J2000.

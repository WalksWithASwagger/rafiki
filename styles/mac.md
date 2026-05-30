# Mind, AI & Consciousness (MAC) Style Guide

## Overview

The `mac` style is the **brand-identity tile system** for the Mind, AI & Consciousness (MAC)
subgroup of BC + AI. It renders consciousness-as-data: a single abstract generative-art form on a
near-black field, with the MAC wordmark and a colored topic kicker. The register is
scientific-sublime — contemplative, premium-editorial, mysterious — never literal brains or robots.

**`mac` vs `femme`:** `mac` is the *outer brand-identity system* (the social-tile look used for
episodes, deepdives, and announcements). `femme` is a *thematic art direction within MAC* — the
intimate, body-compute metaphor set. Use `mac` for identity/announcement tiles; use `femme` for
embodied/body-adjacent themes; compose `mac+femme` when you want MAC tile framing around
body-compute art.

## Color Modes

| Mode | Description |
|------|-------------|
| Moody monochrome | Near-black or deep indigo-navy base + ONE accent hue (acid/emerald green, crimson+cobalt, warm copper, or opalescent pastel). Quiet, atmospheric. |
| Bold kaleidoscope | High-saturation radial mirror symmetry — electric blue or crimson against black. Loud, hypnotic. |

## Key Motifs (pick ONE per image)

- **Particle/dot fields** — millions of points forming waves or fingerprint-like contour ridges
- **Contour topography** — concentric ridge-lines radiating from a center, like a data-driven topo map
- **Line-field portrait** — flowing wireframe lines that resolve into a face/head in profile
- **Radial kaleidoscope** — mirrored symmetric pattern filling the frame
- **Iridescent moiré mesh** — soft spectral gradient interference across a fine grid
- **Spectrogram wave** — a single glowing horizontal waveform across darkness

## Typography System (when text is requested)

- **`MAC`** — large bold white geometric sans (Montserrat/Gotham-like), top-left (or centered for
  bold kaleidoscope variants)
- **`Mind, AI & Consciousness`** — white bold sans, bottom-left
- **Kicker** — smaller ALL-CAPS line directly beneath the subhead, in the image's accent color:
  `MONTH YEAR | TOPIC` (e.g., `NOVEMBER 2025 | EMERGENT MIND IN INFORMATION SPACE`)

## Text Fidelity Caveat

The colored kicker is what makes the tiles feel like a *system* — and it is also the part AI image
models render least reliably (misspellings, dropped pipes, weight/position drift). For a perfectly
consistent series, generate **background-only** tiles with `mac` and overlay text in a Canva
template. **Text-baked** tiles (gpt-image-2 + a reference image) look finished in isolation but
expect a share to need regeneration before they hold as a set.

## When to Use

- MAC episode / deepdive / announcement social tiles
- Event headers, story covers, and slide backgrounds for MAC programming
- Any BC + AI asset that needs the contemplative consciousness-as-data register

## When NOT to Use

- General BC + AI corporate content (use `bcai` or `kk`)
- Body-compute / embodied themes specifically (use `femme`, or `mac+femme`)
- Loud activist / poster work (use `kk-*`, `zine`, or `cmvan`)

## Reference Exemplars

`styles/refs/mac/` holds six exemplars from the source tile set, one per motif. Pass one as a
style reference to lock wordmark placement + corner-text layout:

```bash
# Text-baked tile, reference-anchored (best for finished social posts)
python generate.py \
  -p 'Radial kaleidoscope of electric-blue energy on black. MAC wordmark top-left, "Mind, AI & Consciousness" bottom-left, kicker "JUNE 2026 | ATTENTION IS ALL YOU ARE" in electric blue.' \
  --style mac -m gpt-image-2 --aspect-ratio square \
  --reference-image styles/refs/mac/kaleidoscope-blue.jpg --reference-role style \
  -o output/mac-attention.png

# Background-only tile (reliable; overlay text later)
python generate.py \
  -p 'Dense particle dot-field forming a luminous wave across darkness, emerald accent. No text, no wordmark, leave clean negative space top-left and bottom-left.' \
  --style mac -m flash --aspect-ratio square \
  -o output/mac-emergence-bg.png
```

## Source Material

Original internal 50-tile reference set: MAC Mind, AI & Consciousness source tiles (not packaged).
First generated batch: `prompts/mac/launch-series.md` → `output/mac-launch/`.

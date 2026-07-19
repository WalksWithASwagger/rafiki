# Dark Crystal Style Guide

## Overview

`dark-crystal` and `dark-crystal-chaos` are the project-signature style pair for **Dark Crystal**, Kris's hackathon app. The brand is a neo-noir "obsidian + punk collage" identity built around a faceted black-glass crystal with blood-red light trapped inside, plus a deliberate **Order ↔ Chaos** duality that the product's own UI toggle enacts. The design practices what the product preaches: order is glossy and restrained, chaos is handmade and scarred, and both share one locked palette.

**`dark-crystal` vs `dark-crystal-chaos`:** `dark-crystal` is the Order pole: calm, aligned, film-grain only. `dark-crystal-chaos` is an *additive* Chaos layer: fractures, collage, and glitch on top of the same form and palette. Use `dark-crystal` alone for calm/high-end shots, `dark-crystal-chaos` alone for pure-chaos facets, or compose `dark-crystal+dark-crystal-chaos` for a single frame that shows the tension between both poles.

**Locked-palette signature, not general-purpose:** like `n5orange`/`nardwuar`/`china-creek` (VANCOUVER MADE), this is a project-specific style with a hard-locked color set. It isn't a substitute for `zine`, `cmvan`, or `kk-glitch` on other work, and those generic house styles shouldn't be substituted back in here. Their newsprint yellow, hot magenta, and CMYK palettes break the Dark Crystal lock.

## Color Palette

| Token | Hex | Role |
|---|---|---|
| `obsidian-0` | `#05060A` | page void: the deepest dark |
| `obsidian-1` | `#0C0E14` | panel layer (dark-on-dark) |
| `obsidian-2` | `#14171F` | raised surface (dark-on-dark) |
| `bone` | `#E8E4DA` | off-white text/highlight, never pure white |
| `ash` | `#8A8F9A` | muted secondary |
| `blood` | `#E10600` | the ONE accent: rare, violent, load-bearing |
| `blood-deep` | `#7A0A0A` | the crystal's inner glow |
| `steel` | `#B8C0CC` | cold reflective edge-highlight on facets |

Rule: red is punctuation, not paint. Layer the darks (obsidian-0/1/2) rather than using one flat black. No colors outside this table: no purple-blue gradients, no CMYK, no hot pink.

## Key Motifs

- **Faceted obsidian glass:** a polyhedron or plane of black glass facets, the recurring "object" across every asset
- **Trapped red light:** blood-red light held inside the core, or leaking along a seam/crack; never a full-frame red wash
- **Steel edge-reflections:** cold, precise highlights along facet edges, never warm
- **Order:** facets aligned, razor-straight seams, near-still, one restrained accent
- **Chaos (additive):** facets fracture/shard, red flares wider, xerox halftone grain, torn-paper collage edges, ransom-note type, RGB glitch/scanline tears

## Tone

Neo-noir. Restrained-until-violent. Order reads as "polished in the sense that cohesive and well thought out": gallery-grade calm. Chaos reads as handmade and scarred, "assembled at midnight," but deliberately, not sloppily. It's the same discipline turned inside out, and it's literally the project's anti-slop stance made visual.

## Avoid-Clauses (Critical)

| Concept | Avoid |
|---|---|
| Palette drift | Any color outside the locked table, pure white, CMYK, hot pink/magenta, generic zine/cmvan hues |
| Generic AI look | Purple-blue glassmorphism, AI-brochure gradients, generic dark-mode SaaS panels |
| Stock tech clichés | Glowing brains, circuit boards, humanoid robots, fake dashboards/UI |
| Illustration drift | Cartoon, flat-vector illustration, clip-art |
| Text/marks | Baked-in text or logo marks; these get composited after generation in a separate pass because image models don't render small text/logos reliably |
| People | Photo-realistic people/faces in the abstract crystal style; documentary-photo companion prompts are a separate, explicitly-real-not-fantasy track |

## When to Use

- Dark Crystal logo lockups (icon, wordmark, horizontal, stacked)
- Facet/section backgrounds for the app and hero art
- Album cover art (the companion concept album)
- Pitch-deck and social assets specific to this project

## When NOT to Use

- Any other client's dark-mode or noir work; use `kk`, `bcai`, or `mac` instead
- Public assets that have not been checked against the anti-slop discipline above

## Example CLI Commands

```bash
# Order pole: logo icon
python generate.py -p "faceted obsidian glass crystal, blood-red light trapped in the core, full-bleed pure black, minimal, film grain, centered in a square frame" --style dark-crystal -m flash

# Chaos pole alone: a fractured facet background
python generate.py -p "vast field of fractured obsidian black-glass facets, blood-red seam cracking wide open, landscape orientation, no text, no people" --style dark-crystal-chaos -m flash

# Composed: order giving way to chaos in one frame
python generate.py -p "obsidian black-glass facets, ordered and aligned on one side giving way to fractured chaos on the other, a blood-red seam running the full diagonal connecting both halves" --style dark-crystal+dark-crystal-chaos -m flash
```

## Source Material

This public preset is derived from Dark Crystal's brand spec and proven Rafiki recipes. It is self-contained: use the locked palette, motifs, anti-slop discipline, and Order/Chaos distinction documented here.

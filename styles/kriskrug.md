# KrisKrug / Aurora Editorial Style Guide

## Overview

`kriskrug` is the default Rafiki style for **kriskrug.co personal assets** — Aurora cream/ink chrome, burnt-orange signal, acid-yellow wildcard, and the punk-editorial kits already shipping on the site (Both Hands Full neon, acid riso, CMYK slab, datamosh, CMVan collage, clay satire).

It is a **locked-palette personal-site lane**, not a client brand and not BC + AI.

### Critical: `kk` ≠ KrisKrug

| Key | What it actually is | Use for kriskrug.co? |
|---|---|---|
| **`kk`** | **BC + AI** brand: dark `#0f0f1a`, teal `#00c8b4`, purple `#9333ea` | **NEVER** for personal kriskrug.co assets |
| **`kriskrug`** | Personal / Aurora editorial (this guide) | **YES — default** |
| `kk-blocks` / `kk-acid` / `kk-cmyk` / `kk-glitch` | Specialized type-forward poster kits | Compose on top: e.g. `kriskrug+kk-blocks` |
| `cmvan` | CreativeMornings Vancouver punk collage | Event/punk-specific; or compose with `kriskrug` |

**Agents: if you are making art for kriskrug.co and reach for `--style kk`, stop. That is the BC+AI teal/purple recipe and will look off-brand. Use `--style kriskrug` instead.**

## Color Palette

| Token | Hex | Role |
|---|---|---|
| `paper` | `#efe6d2` | cream newsprint ground (primary light) |
| `paper-deep` | `#e6dcc2` | aged newsprint / secondary paper |
| `ink` | `#171310` | warm black ground / body ink |
| `signal` | `#d94a1f` | burnt-orange accent (CTA, underline, spark) |
| `signal-deep` | `#9a2f14` | deeper burnt orange / rust |
| `wildcard` | `#e8b53a` | acid lime/yellow punch |

Rule: orange and acid yellow are punctuation, not a rainbow wash. When type-forward kits are composed in (`kk-blocks`, `kk-acid`, etc.), neon CMYK clash may enter — still forbid the BC+AI teal+purple pair.

## Key Motifs

- **Both-hands tension:** protest pole vs power cable; civic grit vs compute hunger
- **Type-as-image:** massive condensed gothic/slab when text is requested
- **Handmade print grit:** riso grain, halftone, xerox scars, chromatic edge
- **Punk-editorial satire:** clay/stop-motion wit, collage fragments — never greenwashed datacenter brochure
- **Face (thumbs only):** high-contrast / halftone Kris likeness from brand refs

## Tone

Punk-editorial. Dark humor. Civic, not corporate. Reads like a wheatpasted flyer that somehow got into a magazine — not a SaaS landing page.

## Avoid-Clauses (Critical)

| Concept | Avoid |
|---|---|
| Wrong brand | Rafiki `kk` teal (`#00c8b4`) + purple (`#9333ea`); purple→blue/pink gradients; BC+AI void backgrounds |
| Soft brochure | Pure `#fff`, Inter/system sans softness, stock “AI future” polish |
| Stock tech clichés | Glowing brains, robots, fake dashboards/UI, greenwashed server farms |
| Documentary fraud | Generated crowds presented as real protest evidence — use real WP media instead |
| Wrong face | Stewart Muir (bald, short grey beard, thin glasses, plaid) — Kris only when a face is requested |

## When to Use

- YouTube thumbs, social cards, and editorial illustrations for **kriskrug.co** posts
- Personal-site featured/inline generated art when documentary photos are unavailable
- Compose with kits: `kriskrug+kk-blocks`, `kriskrug+kk-acid`, `kriskrug+cmvan`

## When NOT to Use

- **BC + AI / ecosystem / partner assets** — use `kk`, `bcai`, `bcai-ecosystem`, etc.
- **Real protest or interview documentation** — use rights-cleared WP media (bridge photos, signs, stills)
- Substituting for Dark Crystal, MAC, or other locked project styles

## Example CLI Commands

```bash
# Default personal-site editorial
python generate.py -p "editorial illustration, both hands tension, cream paper grit" \
  --style kriskrug -m flash --aspect-ratio 16:9

# Type-forward neon blocks on the personal palette
python generate.py -p "WHO GETS THE POWER? protest poster" \
  --style kriskrug+kk-blocks -m flash --aspect-ratio 16:9

# Acid riso heat on the personal palette
python generate.py -p "WHO GETS THE POWER? hardcore flyer energy" \
  --style kriskrug+kk-acid -m flash --aspect-ratio 16:9
```

## Reference Anchors

Live under `styles/refs/kriskrug/`:

1. `02-both-hands-full.png` — neon Both Hands Full
2. `01-ruthlessly-optimistic-absolutely-terrified.png` — acid riso
3. `01-dumbest-timeline-the-keeper.png` — CMYK slab
4. `02-we-are-the-training-data.jpg` — datamosh
5. `kk-cmvan-keynote-header.png` — CMVan punk collage
6. `01-cheer-is-a-cap-table-marionette.png` — clay satire
7. `kris-krug-oja-judge-editorial-badge.png` — OJA cream+orange+lime badge
8. Face identity (thumbs): `kris-krug-creativemornings-portrait-close-2026-scaled.jpg`, `kris-krug-van-ai-portrait-2025.jpg` (+ optional `7717-kk-on-the-bridge.jpg`)

## Source Material

Derived from live kriskrug.co / Aurora tokens and the existing editorial art kits already on the site. Self-contained: use the locked palette, hard bans, and compose kits rather than inventing a new neon SaaS look.

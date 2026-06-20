# Number Five Orange / "Work Is Work" Style Guide

## Overview

The `n5orange` style is a **counterfeit-official FIFA-style protest kit** for the VANCOUVER
MADE · MADE ON collection. It dresses as a glam, broadcast-ready World Cup *away strip* —
the highlight-reel version that fills the hotel rooms — and resolves, up close, into a
labour manifest and an itemized cover charge. The target is nightlife capitalism, the
spectacle economy, and sex-work stigma. The method, on every image: **mimic the official
polish, invert the payload, bake in the receipt.**

## The two-distance trick (mandatory)

- **TV read (10 m):** premium limited-edition away strip — safety-cone orange, white
  sleeves, metallic-gold trim, official-drop gloss.
- **Street read (arm's length):** the gloss bends into a cover charge and a VIP rope —
  thermal-receipt microtype, cover-charge stamps, an itemized "tab."

## Palette (strict — no other colours)

| Colour | Hex | Role |
|--------|-----|------|
| Safety-cone orange | `#ff6a00` | The façade / body |
| Vinyl black | `#0a0a0a` | Ink, surcharge lines |
| Merch gold | `#d9a521` | Official-drop trim, foil |
| Neon marquee pink | `#ff2d6f` | The signal / nightlife glow |

## Key Motifs

- Vertical metallic "pole" stripe down the torso
- Orange stage marquee / buzzing neon door marquee (trophy-misuse mark)
- Velvet VIP rope, brass stanchion, tear-off paper wristband
- Repeating rubber-stamp "COVER CHARGE" marks
- Itemized thermal-receipt "tab" (cover, drink minimum, "service fee")
- Telecom/airline-style sponsor wordmark lockup (`WORK IS WORK`)

## Ethics (hard line)

Punch **up** at buyers, VIP culture and the bylaw — **never down**. Any human figure is an
abstract, **faceless** flat silhouette. No worker/dancer/staff caricature, no real-person
likeness. EVOKE the tournament system (host-city shield, sponsor-board language, trophy);
never reproduce real FIFA marks or actual trademarks.

## When to Use

- The "Number Five Orange" away/home/third kit flats, graphic elements, and mood plates
- Any MADE ON asset critiquing nightlife capitalism / the spectacle economy

## When NOT to Use

- The memorial kits (02 / 04 / 07) — those are restrained, no neon, no irony
- General BC + AI content (use `bcai`/`kk`); loud generic poster work (use `kk-acid`)

## Render modes

Render-mode-neutral: the style carries palette + motifs + ethics; **each prompt sets its
own background and composition.** Use full-bleed for mood plates; `white background` +
"technical flat-lay fashion illustration" for graphic-element and jersey-flat extraction.

```bash
# Mood plate (full-bleed)
python generate.py -p 'A buzzing neon door marquee glowing over a darkened wet street, no people.' \
  --style n5orange -m pro -r 1K --aspect-ratio 4:5 -o output/n5-marquee.png

# Jersey flat (white background, for extraction)
python generate.py -p 'Technical flat-lay of a soccer away jersey, safety-cone orange body, white sleeves, gold pole-stripe, marquee crest, "WORK IS WORK" sponsor bar. white background.' \
  --style n5orange -m pro -r 1K --aspect-ratio 3:4 -o output/n5-front.png
```

## Reference Exemplars

`styles/refs/n5orange/` holds curated mood plates from the first generation run. Pass one
as `--reference-image … --reference-role style` to lock palette + texture on the kit flats.

## Source Material

Concept brief: `vancouver-made/docs/design/clubs/number-five-orange.md` and
`vancouver-made/src/data/clubs.js` (source of truth for palette + receipts). Prompt packs:
`vancouver-made/docs/design/prompts/clubs/number-five-orange/`.

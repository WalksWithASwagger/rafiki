# China Creek / "Public Land" Style Guide

## Overview

The `china-creek` style is a **counterfeit-official FIFA-style protest kit** for the VANCOUVER
MADE / MADE ON collection, and the first ALLEY LEAGUE expansion club. It dresses as a clean
host-city home kit with broadcast polish and resolves, up close, into a defended-public-space
manifesto: a skatepark bowl, griptape grit, spray-stencil and the city's own "NO SKATEBOARDING"
bylaw sign turned into the front mark. It is East Van skate and DIY culture worn as evidence.
The method, on every image: **mimic the official polish, invert the payload, bake in the
receipt.** The wound: the city policed street skating as a nuisance, then branded itself a
skate-tourism destination and rode skateboarding into the Olympics. Criminalize the subculture,
then sell it back.

## The two-distance trick (mandatory)

- **TV read (10 m):** a premium, high-end city-pride home kit led by ONE hero element — an
  elegant tonal all-over pattern of nested skatepark bowl contours and coping curves
  (caution-yellow + creek-teal line-art on concrete grey). Refined, restrained, covetable.
- **Street read (arm's length):** the pattern resolves into the defended-public-space payload,
  carried by small restrained marks — a discreet bylaw patch, a hem line, a parks-permit tag.
  Keep stickers / spray-stencil / zine grit to quiet accents, never clutter.

## Palette (strict — no other colours)

| Colour | Hex | Role |
|--------|-----|------|
| Concrete grey | `#9aa0a3` | Body / raw skatepark concrete |
| Marker black | `#0a0a0a` | Toner ink, line work, away body |
| Caution yellow | `#f4c20d` | City-signage trim, the bylaw mark |
| Creek teal | `#1f9e8a` | Coping line, accent |

Plus **brochure cream + gold** for the "Skate Tourism" third kit only.

## Key Motifs

- Skatepark bowl cross-section and coping line (the crest device)
- All-over bowl-contour / coping-curve line art, a transition map
- Griptape texture and grid
- The city "NO SKATEBOARDING" bylaw pictogram, set like a kit-maker brand mark
- Spray-stencil arrows and lettering on raw concrete
- Skate-zine cut-and-paste, xerox grain, DIY screenprint
- Parks-permit / closure-notice swing tag
- Trophy-misuse: the trophy silhouette becomes a skateboard deck (or a spray can, or a bowl coping curve)

## Ethics (hard line)

Punch **up** at the bylaw, redevelopment pressure, and the tourism / Olympic monetization of a
policed subculture. The skaters, the DIY builders and East Van youth are the **home team, never
the joke.** Any human figure appears ONLY as a faceless flat silhouette — never a caricature,
never a recognizable likeness. EVOKE the tournament and Olympic systems (host-city shield,
broadcast / credential language, the trophy) but NEVER reproduce real FIFA marks, Olympic rings,
real sponsor logos, or any actual trademark.

## When to Use

- The "China Creek" club home / away / third kit flats, graphic elements, and mood plates
- Any MADE ON asset about public space, the criminalize-then-monetize playbook, or skate / DIY culture

## When NOT to Use

- The memorial kits (02 / 04 / 07) — restrained, no irony
- General skate / streetwear work unrelated to the kit (use `zine` or `cmvan`)

## Render modes

Render-mode-neutral: the style carries palette + motifs + ethics; **each prompt sets its own
background and composition.** Full-bleed for mood plates; `white background` + "technical
flat-lay fashion illustration" for graphic-element and jersey-flat extraction.

```bash
# Mood plate (full-bleed)
python generate.py -p 'Extreme close-up of a weathered concrete skatepark bowl, coping lip and transition curve, wax and scuff marks, caution-yellow paint flecks. Full-bleed.' \
  --style china-creek -m pro -r 1K --aspect-ratio 4:5 -o output/cc-bowl.png

# Jersey flat (white background, for extraction)
python generate.py -p 'Technical flat-lay of a concrete-grey host-city home soccer jersey, a creek-teal coping line across the torso, bowl-and-skateboard crest, "NO SKATEBOARDING" bylaw-pictogram sponsor bar. white background.' \
  --style china-creek -m pro -r 1K --aspect-ratio 3:4 -o output/cc-front.png
```

## Reference Exemplars

`styles/refs/china-creek/` holds curated mood plates from the first generation run. Pass one as
`--reference-image … --reference-role style` to lock palette + texture on the kit flats.

## Source Material

Concept brief: `vancouver-made/docs/design/clubs/china-creek.md` and
`vancouver-made/src/data/clubs.js#china-creek` (source of truth for palette + receipts). Prompt
packs: `vancouver-made/docs/design/prompts/clubs/china-creek/`.

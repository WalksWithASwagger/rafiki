# Nardwuar FC / "Deep Cut" Style Guide

## Overview

The `nardwuar` style is a **counterfeit-official FIFA-style protest kit** for the VANCOUVER
MADE · MADE ON collection. It dresses as a bold, classic tartan *host-nation home kit* with
broadcast polish, and resolves, up close, into a riso-printed cut-and-paste fanzine of a
city's underground — records, flyers, interview microtext. It is the project's thesis worn
on the body: **research is the protest; the receipt is the weapon.** The method, on every
image: **mimic the official polish, invert the payload, bake in the receipt.**

## The two-distance trick (mandatory)

- **TV read (10 m):** bold tartan host-nation home kit — classic striping, crest, broadcast
  polish.
- **Street read (arm's length):** riso-zine walking archive — ghosted tartan check, 7"
  labels, photocopied flyers, ransom-note type, microtext quotes.

## Palette (strict — no other colours)

| Colour | Hex | Role |
|--------|-----|------|
| Tartan red | `#c8102e` | Body / the tam |
| Vinyl ink | `#0a0a0a` | Toner ink, line work |
| Tartan green | `#1d7a46` | Check / trim |
| Tartan yellow | `#e8c531` | Overcheck accent |

Plus **bone newsprint** for the away variant.

## Key Motifs

- Ghosted woven tartan check printed faint into the fabric
- Ultra-faint all-over collage: 7" record labels, cassette J-card spines, VHS labels,
  photocopied punk show flyers
- Cut-and-paste ransom-note lettering (the `NARDWUAR!!` nameplate)
- Numbers built from tiny record-sleeve / zine-panel rectangles
- Tam-o'-shanter hat silhouette
- Vintage microphone on a chrome stand fused with a vinyl spindle (trophy-misuse mark)
- Press-accreditation laminate on a lanyard ("Unsanctioned Press" third kit)

## Ethics (hard line)

This is an **homage to a living person — never his likeness.** NO human face, NO portrait,
NO recognizable likeness of any real person anywhere. The homage is carried entirely through
**objects** (tam silhouette, records, zines, mic stand). EVOKE the tournament system
(host-city shield, broadcast/credential language, trophy); never reproduce real FIFA marks
or actual trademarks. If this moves past exhibition toward merch, get Nardwuar's blessing first.

## When to Use

- The "Nardwuar FC" home/away/third kit flats, graphic elements, and mood plates
- Any MADE ON asset about research-as-protest / who tells the city's story

## When NOT to Use

- The memorial kits (02 / 04 / 07) — restrained, no irony
- General punk/zine work unrelated to the kit (use `zine` or `cmvan`)

## Render modes

Render-mode-neutral: the style carries palette + motifs + ethics; **each prompt sets its
own background and composition.** Full-bleed for mood plates; `white background` +
"technical flat-lay fashion illustration" for graphic-element and jersey-flat extraction.

```bash
# Mood plate (full-bleed)
python generate.py -p 'Layered wall of photocopied punk show flyers, stapled and torn, riso red and green ink, microtype gig listings. No faces.' \
  --style nardwuar -m pro -r 1K --aspect-ratio 4:5 -o output/nw-flyers.png

# Jersey flat (white background, for extraction)
python generate.py -p 'Technical flat-lay of a tartan-red host-nation home soccer jersey, ghosted check, collage crest (records + tam silhouette, no face), "WHO BENEFITS? WHO PAYS?" sponsor bar. white background.' \
  --style nardwuar -m pro -r 1K --aspect-ratio 3:4 -o output/nw-front.png
```

## Reference Exemplars

`styles/refs/nardwuar/` holds curated mood plates from the first generation run. Pass one as
`--reference-image … --reference-role style` to lock palette + texture on the kit flats.

## Source Material

Concept brief: `vancouver-made/docs/design/clubs/nardwuar-fc.md` and
`vancouver-made/src/data/clubs.js` (source of truth for palette + receipts). Prompt packs:
`vancouver-made/docs/design/prompts/clubs/nardwuar-fc/`.

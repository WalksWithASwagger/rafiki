# Slingsby / Haute Peinture Editorial

Draft style for Slingsby Advisors proposal plates and, later, authorized
portraits of Tanya Slingsby. The language comes from her public artist
statement and series names, not from private photos.

Use-case: [Slingsby Advisors proposal visuals](../docs/use-cases/slingsby-advisors-proposal-visuals.md).

## Overview

Tanya's studio practice is abstract: colour, form, line, and surface. She
calls site-specific commissions **Haute Peinture** — "The Completion of
Space." Proposal images should feel like that room, not like a bank brochure.

Public series that lock the suffix (from tanyaslingsby.com/portfolio, not
committed here):

- **Meridians (2012)** — matte black, one metallic-gold nested sweep, vertical
  impasto ridges
- **Mutual (2017)** — two stacked complementary fields on white (terracotta
  over turquoise)
- **Shoru (2011)** — one impasto crimson circle on bronze-gold, etched grid
- **Arcana (2010)** — imperfect off-white ring, cracked plaster greys
- **Art In Situ** — the painting finishes a real quiet room

## When To Use

- Abstract section plates for a family-office / legacy proposal
- Rooms, tables, and landscapes that should share a wall with her paintings
- Authorized portraits **only** when likeness refs or a subject LoRA are
  attached — this style does not invent a face

## When Not To Use

- Generic UHNW marble, gold serif, or yacht photography
- Tech-bro navy, dashboards, glowing brains, robots
- Mystical crystal / chakra pastiche
- Invented letterhead, logos, or fake Sanskrit/Latin/Arabic titles
- Any likeness job without an authorized reference set

## Palette

- Grounds: warm titanium-white, bone, quiet dusk
- Load-bearing colour: one or two jewel tones, used as fields
- Light: slow, spatial, the subject as much as the object
- Avoid: pure #ffffff, SaaS charcoal, rainbow accents

## Geometry And Surface

- A few arcs, ellipses, meridians, or iconic forms
- Sanded resin depth; pigment revealed, not airbrushed
- Generous open space (Salt Spring / "purity of open space")
- Never a dense sacred-geometry poster

## Example

```bash
npx rafiki examples/slingsby-advisors-style-plates.md \
  --style slingsby \
  --output-dir output/slingsby-advisors \
  --dry-run --no-viewer
```

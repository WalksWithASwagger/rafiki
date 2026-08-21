# Slingsby Advisors Editorial

Locked from the operator mood board (`SLA Images 2`): candid high-end
advisory photography. Not a painting LoRA. Not generic UHNW marble.

Use-case: [Slingsby Advisors proposal visuals](../docs/use-cases/slingsby-advisors-proposal-visuals.md).

## Overview

Proposal images should feel like a fly-on-the-wall in a luminous modern
office: through-glass frames, soft reflections, golden-hour haze, shallow
depth of field. People, when requested, are mid-conversation — not posed
catalogue portraits. Tanya's likeness only when authorized refs are
attached with `--reference-role likeness`.

## When To Use

- Counsel, stewardship, and bio stills for the family-office proposal
- Empty rooms and urban plates that share the same light
- Authorized portraits of Tanya placed into this register

## When Not To Use

- Generic UHNW marble, gold serif, or yacht photography
- Tech-bro navy, dashboards, glowing brains, robots
- Mystical crystal / chakra pastiche
- Invented letterhead, logos, or fake Sanskrit/Latin/Arabic titles
- Copying stock faces from the mood-board tiles
- Any likeness job without an authorized reference set

## Palette And Light

- Warm neutrals: oak, cream, bone, soft grey
- Cool glass and distant city blue
- Natural window light, backlight, occasional lens flare
- Avoid: pure #ffffff, SaaS charcoal, rainbow accents

## Camera

- Shoot through glass, doorways, or a blurred foreground shoulder
- Shallow depth of field; subjects rarely look at camera
- Floor-to-ceiling windows, long tables, quiet architecture
- Page-5 register: cinematic urban canyon, high contrast, golden distance

## Example

```bash
bash scripts/slingsby-proposal-generate.sh --status
npx rafiki examples/slingsby-advisors-style-plates.md \
  --style slingsby \
  --output-dir output/slingsby-advisors \
  --dry-run --no-viewer
```

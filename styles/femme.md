# Femme / Body-Compute Style Guide

## Overview

The `femme` style is the abstract body-compute *art direction* within the Mind, AI & Consciousness (MAC) subgroup of BC+AI. It renders biological processes — hormonal cycles, cellular membranes, neural routing, ancestry — as computational metaphors. Quiet, intimate, embodied intelligence. Never representational, never clinical.

**`femme` vs `mac`:** `femme` is the body-compute *theme*; `mac` (see `mac.md`) is the broader MAC *brand-identity tile system* (wordmark + colored topic kicker on near-black generative art). Use `mac` for episode/announcement tiles, `femme` for embodied themes, and compose `mac+femme` to frame body-compute art inside MAC tile branding.

**Community use note:** These prompts use abstract body metaphors. Review outputs before publishing in community contexts. The avoid-clauses in the prompts below are load-bearing — enforce them. Do not use literal clinical, anatomical, or objectifying framing in public assets without community sign-off from MAC.

## Color Families

| Role | Colors |
|------|--------|
| Foundation | Deep indigo, obsidian, near-black |
| Biologic warmth | Blush-magenta, warm amber, muted coral, peach |
| Tech-cool | Faint teal, cold blue, cyan highlights |
| Accent life | Hot pink microflares, jade glints, oil-slick iridescence (green/purple/blue) |
| Transformation | Rust red, arterial red, pale blue interference |

Night blues → rust reds → pearly whites → spring greens is the full cycle palette for rhythm-based imagery.

## Key Motifs

- **Membrane boundaries** — selective permeability, semi-transparent veils, gradients that suggest negotiation rather than walls
- **Contour fields** — concentric rings or rippling contours that imply shape without drawing the body part
- **Network routing** — pathways that detour around stress, stabilize fragile nodes, route for gentleness rather than efficiency
- **Gradient pulses** — hormonal rhythms, feedback loops, cycles visualized as asymmetry and texture, not labels
- **Nested containers** — organelles, membranes within membranes, concentric scaffolding
- **Accumulated micro-marks** — pressure ridges, soft grids, biometric-noise-as-texture

## Tone

Quiet. Intimate. Non-literal. Embodied intelligence rather than mechanical process. Should feel *found*, not diagrammed. The best images look like something you'd see under a microscope or in a dream — not a medical textbook.

## Avoid-Clauses (Critical)

These are standard across the MAC corpus — enforce them in every prompt:

| Concept | Avoid |
|---------|-------|
| Reproductive imagery | Goddess iconography, hearts, obvious pregnancy silhouettes, embryos, babies |
| Cycle imagery | Moons, period-blood clichés, calendars, text-heavy labels |
| Egg/cell | Literal cell diagrams, medical illustration look |
| Interface/exchange | Umbilical-cord literalism, medical anatomy |
| Touch/fingerprint | Biometric UI clichés, literal fingerprint patterns |
| Ancestry | DNA double helix front-and-center, textbook organelles |
| Network/routing | Brain silhouettes, circuit-board motifs |
| Identity | Chakras, sacred geometry, crystals, faces |

## When to Use

- MAC event visuals, zine pages, and immersive art contexts
- BC+AI community assets that center embodied / non-binary / femme perspectives
- Abstract scientific imagery with intimate emotional register
- Slides or prints where you need body-adjacent imagery without literal anatomy

## When NOT to Use

- General BC+AI corporate content (use `bcai` or `kk`)
- Anything requiring institutional credibility without community context
- Public assets without MAC review (the community sign-off requirement stands)

## Example CLI Commands

```bash
# Membrane boundary — abstract exchange
python generate.py -p "Two interpenetrating networks, warm and cool, braiding without merging. Boundary behaves like selective permeability — slow gradients, semi-transparent veils, capillary-like filaments reading as negotiation. Avoid: medical-illustration look, umbilical literalism." --style femme -m flash

# Care-based routing
python generate.py -p "Network that routes for gentleness over efficiency. Thicker pathways stabilize fragile nodes. Detours form around stress zones. Intelligence reads as relational, not optimized. Avoid: brain silhouettes, circuit-board motifs." --style femme -m flash

# Cycle rhythm — no labels
python generate.py -p "Ring-buffer phase diagram — thresholds and feedback loops as gradients and micro-textures. The cycle felt through asymmetry, not labels. Avoid: moons, calendars, period-blood clichés, text." --style femme -m flash
```

## Source Material

Full polished prompt set, short variants, alternate aesthetic phrasing, and batch-export one-liners: `prompts/kk-kb/femme-prompts-mac-image-repository.md`

The prompt file also contains a neuro/bio/substrate set (neural cartography, protein fold consciousness, chromosomal memory palace, etc.) that pairs well with this style.

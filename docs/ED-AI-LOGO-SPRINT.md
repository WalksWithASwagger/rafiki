# ED + AI Logo Sprint

This document records the May 2026 `ED + AI` / `AI Education Meetup` logo
exploration under the BC + AI ecosystem.

## Objective

Create a distinct education-focused meetup identity that can live under the
BC + AI parent brand without becoming a generic AI conference mark.

The sprint explored:

- `ED + AI` as the primary identity.
- `AI Education Meetup` as an optional subtitle.
- `BC + AI` as a small parent-brand or presenter credit.
- Abstract Ethos Lab influence through Ubuntu/community framing, culture-based
  STEAM, youth agency, relational infrastructure, and Afrofuturist storytelling.
- Futureproof Festival influence through luminous dot-matrix signal, aurora,
  bioluminescent accents, handmade artifact energy, portals, talismans, seed
  vaults, and local mythic atmosphere.

## Source Prompt Packs

| Round | Prompt pack | Direction | Local output |
| --- | --- | --- | --- |
| R1 | `prompts/bcai/ed-ai-logo-variations.md` | Original BC + AI parent/child logo lockups | `output/ed-ai-logo/` |
| R2 | `prompts/bcai/ed-ai-logo-brainstorm-round-2.md` | Broad education + BC + AI logo brainstorm | `output/ed-ai-logo-r2/` |
| R3 | `prompts/bcai/ed-ai-logo-pedagogy-underground-r3.md` | Pedagogy Underground: care, commons, consent, repair | `output/ed-ai-logo-r3-pedagogy/` |
| R4 | `prompts/bcai/ed-ai-logo-afrofuturist-geometry-r4.md` | Afrofuturist geometry, Aurora, bioluminescence | `output/ed-ai-logo-r4-afrofuturist-geometry/` |
| R5 | `prompts/bcai/ed-ai-logo-art-director-rebrief-r5.md` | Anti-corporate art-director rebrief | `output/ed-ai-logo-r5-art-director-rebrief/` |
| R6 | `prompts/bcai/ed-ai-logo-aurora-biolum-r6.md` | Pop Afrofuturism, Aurora, bioluminescent sub-brand lockups | `output/ed-ai-logo-r6-aurora-biolum/` |
| R7 | `prompts/bcai/ed-ai-logo-education-remix-r7.md` | Remix from user-starred taste references | `output/ed-ai-logo-r7-education-remix/` |
| R8 | `prompts/bcai/ed-ai-logo-futureproof-mythic-r8.md` | Futureproof-mythic education concepts | `output/ed-ai-logo-r8-futureproof-mythic/` |

## Review Artifacts

Generated images are intentionally not committed. They are local review output.

- Combined gallery: `http://127.0.0.1:8765/output/ed-ai-logo-all-review/index.html`
- R8 side-by-side viewer:
  `http://127.0.0.1:8765/output/ed-ai-logo-r8-futureproof-mythic/compare/side-by-side.html`
- Desktop export:
  `/Users/athena/Desktop/ED-AI-logo-images-20260529-173412.zip`

The combined gallery contained 176 PNG images when exported:

- R1: 16 images.
- R2: 30 images.
- R3: 30 images.
- R4: 20 images.
- R5: 20 images.
- R6: 20 images.
- R7: 20 images.
- R8: 20 images.

## Generation Pattern

Start the local viewer:

```bash
./.venv/bin/python generate.py serve --port 8765
```

Run a prompt pack through Gemini Pro 1K:

```bash
./.venv/bin/python generate.py \
  -f prompts/bcai/ed-ai-logo-futureproof-mythic-r8.md \
  -d output/ed-ai-logo-r8-futureproof-mythic/gemini-pro-1k \
  --style futureproof-mythic -m pro -a square -r 1K \
  --global-reference-images /Users/athena/code/RAP/web/public/brand/bcai/bcai-logo-official.png,prompts/futureproof/reference/futureproof-bcai-logo-reference-board.png,prompts/futureproof/reference/futureproof-dot-matrix-style.png \
  --reference-role style -w 1 --json
```

Run the same prompt pack through GPT Image 2:

```bash
./.venv/bin/python generate.py \
  -f prompts/bcai/ed-ai-logo-futureproof-mythic-r8.md \
  -d output/ed-ai-logo-r8-futureproof-mythic/openai-gpt-image-2 \
  --style futureproof-mythic -m gpt-image-2 -a square -q high \
  --global-reference-images /Users/athena/code/RAP/web/public/brand/bcai/bcai-logo-official.png,prompts/futureproof/reference/futureproof-bcai-logo-reference-board.png,prompts/futureproof/reference/futureproof-dot-matrix-style.png \
  --reference-role style -w 1 --json
```

## Creative Findings

- BC + AI works best as parent context, not as the main visual engine.
- The strongest concepts came from education-specific metaphors: syllabus,
  bell schedule, threshold, commons, repair, archive, table, and field-note
  systems.
- Hope Code texture was useful, but too much grit made the mark feel heavy.
- Futureproof Festival language helped unlock more memorable forms: portals,
  talismans, dot-matrix light, aurora, and mythic local artifacts.
- Generated type should be treated as concept evidence only. Production marks
  need deterministic typography and manual cleanup.
- The most reusable next step is to shortlist starred concepts, redraw the
  best marks in vector, and test real `ED + AI` / `AI Education Meetup` /
  `BC + AI` lockups.

## Hard Bans Used Across Later Rounds

- Corporate tech logo.
- Generic AI/startup identity.
- Robots, brains, dashboards, generic node networks, hex-grid wallpaper.
- Graduation caps, apples, school buses, lightbulbs.
- Fake institutional seals or sponsor badges.
- Copied Ethos marks, Futureproof marks, or borrowed cultural symbols.
- Faces, masks, flags, kente, adinkra, and other unlicensed cultural shorthand.

## Handoff

The committed prompt packs are the reproducible source. The local PNG outputs
and Desktop zip are delivery artifacts for human review, not source assets.

Recommended next pass:

1. Use the all-review gallery stars to pick 5-8 finalists.
2. Extract common motifs from the finalists into a deterministic reference set.
3. Redraw 2-3 logo systems manually as vector lockups.
4. Test lockups at favicon, avatar, poster, slide, and web-header sizes.
5. Keep BC + AI as a small parent mark unless the asset is explicitly a
   co-brand lockup.

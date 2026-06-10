# AI Animation Accelerator — Cohort 2, Week 3 YouTube Thumbnail (generative only)

**Program:** AI Animation Accelerator (BC+AI Ecosystem × Tiny Ghost Studios)
**Cohort:** Cohort 2
**Week:** Week 3
**Format:** YouTube thumbnail (16:9 landscape)
**Mode:** Generative only — all typography and brand marks baked into the clay scene. No overlays, no post-production logo plates, no flat pasted badges.

**Starting point:** Week 1 generative plaque (`generated-text-plaque-source.png`) — studio desk, pink program banner, purple wavy plaque. Circular BC+AI badge must be part of the set like reference #1, not composited afterward.

**Run:**
```
python generate.py \
  -f prompts/bcai/animation-accelerator-cohort-2-week-3-youtube-thumbnail.md \
  -d output/animation-accelerator-youtube-thumbnails/cohort-2-week-3-2026-06-09-v3 \
  --no-style -m gpt \
  --reference-role brand \
  --global-reference-images "/Users/kk/Code/rafiki/data/refs/animation-accelerator-source.jpg,/Users/kk/Code/animation-accelerator/assets/public/youtube-thumbnails/cohort-2-week-1-2026-05-31/background-blank-plaque.png,/Users/kk/Code/animation-accelerator/assets/public/youtube-thumbnails/cohort-2-week-1-2026-05-31/generated-text-plaque-source.png" \
  -a 16:9 -q high -w 2
```

**Reference key:**
- Reference #1: Luma hero — integrated circular BC+AI ecosystem badge in the lower-left of the set, plus palette, Tiny Ghost, wing-creature.
- Reference #2: Blank plaque studio scene — composition anchor.
- Reference #3: Approved Week 1 generative plaque — match this quality, lighting, and generative clay lettering.

**Required readable copy (all generative clay lettering in-scene):**
- Pink banner above plaque: `AI ANIMATION ACCELERATOR`
- On plaque: `COHORT 2`, `WEEK 3`, `RECORDING`

**Hard constraints:**
- Generative only. Every word and logo must be physically part of the stop-motion set.
- BC+AI ecosystem badge: circular sculpted studio maker's mark in the lower-left, matching reference #1 — navy circle, mint `BC+AI`, chartreuse `ecosystem`, green waveform motif inside the circle.
- No flat overlay rectangles. No pasted PNG logos. No post-production typography plates.

---

## 1. Week 3 Generative Plaque — Pass A

**Aspect Ratio:** 16:9
**Prompt:**
> YouTube thumbnail, 16:9 landscape, stop-motion claymation artist attic studio. Match the exact composition, lighting, and generative clay lettering quality of reference #3 and the blank plaque layout of reference #2. Center: large purple clay plaque with thick wavy scalloped edges. Pink clay banner across the top reads exactly "AI ANIMATION ACCELERATOR" in clean white handmade lettering sculpted into the set. On the plaque face, large readable sculpted clay typography: "COHORT 2" in bright yellow, "WEEK 3" with "WEEK" in teal-blue and "3" in yellow, and "RECORDING" in orange-red at the bottom. The white Tiny Ghost mascot from reference #1 peeks over the top edge of the plaque. The colorful winged creature from reference #1 stands on old books at the right. Small cheerful clay humanoid figure on the wooden desk at lower left under warm lamp light. Desk: open sketchbook with monster sketches, pencil jars, paint pots. Background: dark purple walls, shelves of sculpted busts, pinned sketches, circular porthole window with starry night at upper right, magenta and teal sparkle particles. Lower-left corner of the physical set: a circular sculpted BC+AI ecosystem maker's mark built into the scene exactly like reference #1 — dimensional clay/navy circular badge with mint "BC+AI", chartreuse "ecosystem", and green waveform motif inside the circle, sitting on the desk or wall as part of the set. Generative only: no overlays, no flat pasted logos, no rectangular logo plates. Rich tactile clay texture, cinematic depth, sharp legible lettering.

---

## 2. Week 3 Generative Plaque — Pass B

**Aspect Ratio:** 16:9
**Prompt:**
> YouTube thumbnail, 16:9 landscape claymation studio scene copied faithfully from reference #3. Same camera angle, plaque scale, desk props, ghost pose, winged creature placement, lamp glow, and handmade texture as the approved Week 1 generative plaque. All title text is generative clay lettering sculpted into the set: pink top banner "AI ANIMATION ACCELERATOR", plaque reads "COHORT 2", "WEEK 3", and "RECORDING" with the same letter colors and clay styling as Week 1. Lower-left: a circular BC+AI ecosystem badge physically part of the stop-motion set, matching reference #1 — a round dimensional maker's mark with navy field, mint "BC+AI", chartreuse "ecosystem", green waveform icon, integrated into the desk corner or wall trim. Not a flat overlay. Not a square logo plate. Not post-composited. No screening-room composition. Keep the attic studio plaque from reference #2. Subtle premiere hint allowed through one small dangling clay film strip above the plaque only. Stop-motion clay texture, dark whimsy, premium detail, legible typography, fully generative.

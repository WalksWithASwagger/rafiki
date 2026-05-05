# ED + AI v2 — Biolum aurora lane (4 prompts)

**Research notes baked in:** Pacific deep-water **siphonophore** light trails (string-of-pearls biolum, not “tech neural clipart”); **macro studio** mushroom lamellae as *sculpture* (raking light, subsurface scattering) not stock “AI brain”; **print craft**: simulated process separations, visible grain, one illegal fluorescent accent; **banned**: hexagon grids, floating holographic UI, robots, lightbulbs, generic “nodes and edges” SaaS diagrams, purple-gradient-on-navy startup slop.

**Tooling:** The CLI prints *“Running Nano Banana…”* — that is **this repo’s nickname** for the Gemini image generator in `tools/image-gen/generate.py`. It is **not** a product called “Nano Pro.” The **high-quality image model** wired in the CLI is **`gemini-3-pro-image-preview`** (Google’s Pro image preview); the fast default is `gemini-2.5-flash-image`. Use **`gemini-3-pro-image-preview`** + **2K or 4K** for meetup finals.

**Batch — no reference images** (forces originality; refs were homogenizing earlier):

```bash
cd /path/to/kk-ai-ecosystem/tools/image-gen
npx image-gen ../../content/projects/ed-ai-education-meetup/image-prompts-ed-ai-meetup-v2-biolum-4.md \
  --model gemini-3-pro-image-preview \
  --resolution 2K \
  --aspect-ratio square \
  --output-dir ../../content/projects/ed-ai-education-meetup/outputs/v2-biolum-4 \
  --no-style
```

---

## 1. Siphonophore syllabus — vertical biolum trails

**For:** Poster; tall type stack allowed in square with upper negative space

**Prompt:**
> Square editorial illustration, NOT a logo grid. Concept: a **colonial hydrozoan chain** (siphonophore) interpreted as a **vertical syllabus** — repeating luminous nodules along a drifting thread, each nodule a soft-edged “lesson bead” with no readable fake text. Deep navy-black water column; biolum cyan, acid yellow, and rare magenta accents only where light would actually scatter. Hand-caption energy: **ED + AI** large, custom wedge sans with slight warp; **AI IN EDUCATION** as a second line in narrow monospace; **BC + AI** tiny in margin like a museum accession number. Paper flecks and aquarium glass micro-scratches. **Hard ban:** neural-net graphs, hexagons, robots, stock icons, purple gradient orbs.

---

## 2. Lamellae eclipse — annular print plate

**For:** Screen-print hero; reads at distance

**Prompt:**
> One bold **annulus** (ring) of **macro mushroom lamellae** treated like a **copper photogravure plate**: extreme raking light, oxidized bronze valleys, razor-thin ridges catching **aurora iridescence** (teal, violet, not rainbow unicorn). True circular **central void** (pure black, no lens flare). Typography sits in the **lower third outside the void**: **ED + AI** in wide sans with letterpress bite; **AI IN EDUCATION** small caps tracking wide; **BC + AI** as a single quiet line. Visible ink grain and **misregistration** hint (1–2 px shift on one plate color). Must feel like **one photograph of a fabricated art object**, not an AI mush texture. **Ban:** symmetric “mandala AI,” glowing particles on every line, circuit traces.

---

## 3. Tide chart + biolum — data viz as coastal field note

**For:** Slide; intellectually specific

**Prompt:**
> **Salish Sea–adjacent abstract**: not a map of any real nation—just **tidal curves** as faint graphite, interleaved with **bioluminescent spark lines** that spike where curves cross (night water disturbed). Muted kelp ink greens, cold blue-grey paper, sparks in electric teal. Small boxed callouts with **single words only** (e.g. “PRAXIS”, “CONSENT”, “CARE”) — no sentences. Primary meetup text in a **stencil / maritime instrument** hybrid: **ED + AI** dominant; **AI IN EDUCATION** on a tilted brass plate rectangle; **BC + AI** in tiny stamped letters. Aesthetic: **hybrid of field notebook and hydrography**, not corporate infographic. **Ban:** isometric cubes, arrow-of-progress, graduation caps, brain icons.

---

## 4. Darkroom test strip — biolum as chemistry

**For:** Zine / experimental social card

**Prompt:**
> **Photographic darkroom** metaphor: horizontal **exposure test strips** across lower half, each strip stepping through under/over exposure; in the densest strip, **cyanotype-blue** lifts into **biolum teal glow** as if emulsion failed beautifully. Upper half: deep black with subtle **silver gelatin sparkle** noise. Typography: **ED + AI** like tape labels on enlarger easel — slightly crooked, **AI IN EDUCATION** on a smaller tape strip; **BC + AI** on corner **china marker** scrawl. Mood: **art school + marine bio lab**. Must look **intentionally imperfect**. **Ban:** lens flares, outer-space starfields, neon city, “futuristic font.”

---

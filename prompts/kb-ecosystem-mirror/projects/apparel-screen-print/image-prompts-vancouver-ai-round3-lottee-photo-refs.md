# Vancouver AI lot-tee — round 3 (real shirt refs + anti–clip-art)

Use **one reference photo per prompt** (order matches sections below). Refs live in `refs/`:

- `ref-lottee-bone-triangle-sunburst-dye.png` — sunburst tie-dye + dense emblem energy  
- `ref-lottee-lightning-path-purple-dye.png` — spiral purple/blue dye + framed scene  
- `ref-lottee-circular-skeleton-navy-dye.png` — navy / magenta target dye + circular chest print  
- `ref-vancouver-ai-poster-flat-white-bg.png` — your Vancouver AI poster density (lettering + drips), flat mock  

**Batch command** (from `tools/image-gen`; comma-separated `--reference-images` must be **5 paths in section order**):

```bash
cd tools/image-gen
npx image-gen ../../content/projects/apparel-screen-print/image-prompts-vancouver-ai-round3-lottee-photo-refs.md \
  --reference-images "../../content/projects/apparel-screen-print/refs/ref-lottee-bone-triangle-sunburst-dye.png,../../content/projects/apparel-screen-print/refs/ref-lottee-lightning-path-purple-dye.png,../../content/projects/apparel-screen-print/refs/ref-lottee-circular-skeleton-navy-dye.png,../../content/projects/apparel-screen-print/refs/ref-vancouver-ai-poster-flat-white-bg.png,../../content/projects/apparel-screen-print/refs/ref-lottee-bone-triangle-sunburst-dye.png" \
  --model gemini-3-pro-image-preview \
  --resolution 2K \
  --aspect-ratio square \
  --output-dir ../../content/projects/apparel-screen-print/outputs/round-3-lottee-photo-refs \
  --no-style
```

---

## 1. Variation — Bone portal Vancouver (sunburst dye read)

**For:** Chest print over dark sunburst blue/red/yellow dye

**Prompt:**
> Original Vancouver AI Community shirt graphic — NOT a copy of any band artwork. Use the reference photo only to match **physical vibe**: real cotton, tie-dye mottling, and **heavy vintage screen ink** sitting on fabric (slight grain, imperfect registration, chunky pigment), plus **hand-drawn wobbly linework** like a parking-lot poster. Absolutely avoid: corporate flat vector, stock illustration, clean Adobe-gradient plastic, mascot clip art, perfect symmetry, glossy 3D icons. Typography: custom warped arched letters reading VANCOUVER and large AI (add COMMUNITY smaller if it stays legible) — **extra drippy**, melting, uneven stroke width, black outer outline like old lot tees. Center: **your own** bone-triangle or portal motif with roses and a small cosmic scene inside — inspired by classic counterculture layout but **new shapes**. High contrast so it reads on **chaotic tie-dye**. Weird, human, wrong in the right ways.

---

## 2. Variation — Lightning road robot parade (spiral dye read)

**For:** Purple/blue spiral tie-dye long-sleeve

**Prompt:**
> Original illustration for Vancouver AI Community merch. Reference photo is for **texture and energy only** (fabric dye spirals, ink on shirt, analog imperfection) — do **not** recreate any trademarked character or band scene. Forbidden look: corporate infographic, vector clip art, smooth gradients without grain, emoji-simple shapes, sterile tech branding. Required look: **hand-inked** poster lines, slightly crooked composition, **visible halftone/stipple**, fat black outlines, colors that feel **screen-printed** not digital. Scene: jagged banner top, dense rose frame, central path or ribbon shape; friendly **original** robot or skeleton-adjacent figure (generic, not a copy) marching with roses and a retro synth prop. Big drippy warped VANCOUVER AI lettering. Dripping ink puddles, playful chaos, readable on **dark psychedelic dye**.

---

## 3. Variation — Circular starfield crest (navy target dye read)

**For:** Navy / magenta / cyan target tie-dye chest circle

**Prompt:**
> Design a **new** circular chest emblem for Vancouver AI Community. Learn from the reference **only** how ink behaves on **real tie-dye** (contrast, halation, rough edges) and how a **circular lot print** sits on the body — do not copy the reference’s character, pose, or band text. Style guardrails: **no** slick corporate logo packs, **no** flat vector polish, **no** sterile minimal tech — must feel like **1970s hand-drawn rock poster** scanned from paper: wobbly ellipses, uneven line weight, ink specks, slight color misregistration. Outer rings slightly imperfect. Inside: cosmic purple starfield with **original** figure (robot with top hat OR abstract cosmic jester — your invention) holding a **glowing orb** that reads AI-ish. VANCOUVER arched top, **VANCOUVER AI** split across top/bottom arcs like classic circular lot prints; COMMUNITY tiny along inner rim if needed. Typography ultra drippy with thick white inner stroke and black outer stroke like vintage prints. **Weird, collectible**, not clipart.

---

## 4. Variation — White-bg poster parity (then imagine on dark dye)

**For:** Master art on neutral ground, print-ready for dark blue/red blanks

**Prompt:**
> Create an original **Vancouver AI** psychedelic poster graphic on a **clean white rectangle** (print separation style), matching the **density and drippy hand-lettering energy** of classic lot-poster art — reference is for **layout complexity and ink texture**, not to duplicate its exact skeleton pose or composition. Hard reject anything that looks like **stock vector**, Canva template, corporate tech slide art, or smooth gradient clipart. Must have: crowded rose borders, cosmic void, mushroom and tech motifs **recomposed** uniquely, rainbow-gradient drippy letters with black outlines, stippled shading, melting bottom edge. Text: **VANCOUVER** arched, **AI** huge center, **COMMUNITY** on a melting ribbon. Lines should look **drawn with a brush and ink**, slightly uneven. This is the **anti-corporate** version: gritty, obsessive detail, slight ugliness, iconic.

---

## 5. Variation — Sunburst chaos shield (back to fabric ref)

**For:** Same dye class as ref 1 — emblem must “float” on sunburst

**Prompt:**
> Original Vancouver AI Community **shield or crest** graphic tuned for **bright sunburst tie-dye** behind it (deep blues, magentas, hot center). Use reference for **how professional bootleg ink fights busy dye** — thick outlines, high contrast, occasional intentional **misprint/double-hit** look — not for copying any specific trademarked imagery. Ban: clean corporate icon systems, flat duotone tech logos, vector-perfect curves, generic AI chip clipart. Require: hand-drawn jitter, rose clusters, lightning, cosmic nebula, **maximum drip** typography (VANCOUVER AI COMMUNITY words arranged for impact). Center motif: **new** hybrid of organic + circuit (e.g. rose made of traces) — surreal, wrong, memorable. Should feel like a **rare lot shirt**, not a startup hoodie.

# ED + AI — AI IN EDUCATION meetup (BC + AI) — 12 graphic variations

> **Note:** If results felt samey, use **v2** instead: three lane-specific files with stronger art-direction and **`--style hopecode` / `--style bcai`** where appropriate — see [`README.md`](README.md). v1 used **`--no-style`** (no YAML style suffix) + **cycled refs on every prompt**, which often converges on generic “biolum neural” tropes.

Flat artwork for slides, posters, and screen print. Use reference images for color and texture only; all wording must come from the prompt.

**Batch (from `tools/image-gen`):**

```bash
cd tools/image-gen
npx image-gen ../../content/projects/ed-ai-education-meetup/image-prompts-ed-ai-meetup-12-variations.md \
  --reference-images "../../content/projects/ed-ai-education-meetup/refs/ref-biolum-mushroom-gills-bc-ai-circle.png,../../content/projects/ed-ai-education-meetup/refs/ref-biolum-iridescent-gills-aurora.png,../../content/projects/ed-ai-education-meetup/refs/ref-biolum-mycelial-neural-glow.png,../../content/projects/ed-ai-education-meetup/refs/ref-bc-ai-ecosystem-wordmark-dark.png,../../content/projects/ed-ai-education-meetup/refs/ref-biolum-mushroom-gills-bc-ai-circle.png,../../content/projects/ed-ai-education-meetup/refs/ref-biolum-mycelial-neural-glow.png,../../content/projects/ed-ai-education-meetup/refs/ref-biolum-iridescent-gills-aurora.png,../../content/projects/ed-ai-education-meetup/refs/ref-bc-ai-ecosystem-wordmark-dark.png,../../content/projects/ed-ai-education-meetup/refs/ref-bc-ai-ecosystem-wordmark-dark.png,../../content/projects/ed-ai-education-meetup/refs/ref-biolum-mycelial-neural-glow.png,../../content/projects/ed-ai-education-meetup/refs/ref-biolum-iridescent-gills-aurora.png,../../content/projects/ed-ai-education-meetup/refs/ref-biolum-mushroom-gills-bc-ai-circle.png" \
  --model gemini-3-pro-image-preview \
  --resolution 2K \
  --aspect-ratio square \
  --output-dir ../../content/projects/ed-ai-education-meetup/outputs/batch-12 \
  --no-style
```

---

## 1. Biolum aurora — circular crest on gill mandala

**For:** Poster / slide hero; dark shirt print

**Prompt:**
> Original graphic for the BC + AI meetup series ED + AI — AI IN EDUCATION. Lane: BIOLUM AURORA. Large circular composition: radial mushroom-gill texture filling the ring, deep black center void, bioluminescent cyan and violet nodes on thin glowing filaments like a neural map. Small clean line text at bottom: ED + AI in pale mint; arc above: AI IN EDUCATION in smaller caps; tiny BC + AI credit line. High contrast dark-on-dark with aurora shimmer on ridges. No stock icons, no robots. Hand-finished macro look suitable for screen print.

---

## 2. Biolum aurora — iridescent gill eclipse

**For:** Square social card

**Prompt:**
> Original ED + AI meetup artwork, AI IN EDUCATION subtitle, presented by BC + AI. BIOLUM AURORA lane. Donut of iridescent gill ridges: bronze base with electric blue, magenta, and teal sheen like oil-on-water. Black circular core. Typography carved into lower arc: ED + AI with soft yellow-green glow; AI IN EDUCATION as thin orbital ring text. Cosmic dust halo. Cinematic macro, gritty not glossy.

---

## 3. Biolum aurora — neural mycelium plate

**For:** Back print or large slide

**Prompt:**
> Original square poster for ED + AI — AI IN EDUCATION (BC + AI). BIOLUM AURORA plus subtle neural metaphor. Organic root-mycelium radial plate on black; cyan and lavender pulses at junctions like synapses. Fine brown tan branches. Center title stack: top line AI IN EDUCATION small caps; middle ED + AI large custom sans with glow; footer BC + AI ecosystem in small lime accent. Atmospheric, dark-on-dark, print-ready halftone suggestion in shadows.

---

## 4. Biolum aurora — wordmark constellation

**For:** Lockup with brand colors from ref

**Prompt:**
> Original lockup graphic. Use reference for BC + AI palette: deep navy field, pale mint and chartreuse accents. BIOLUM AURORA twist: behind the type, faint circular gill-nebula texture barely visible like aurora through fog. Primary words: ED + AI bold; AI IN EDUCATION on second line; BC + AI small. Add sparse glowing nodes connected by hairline filaments. Minimal but still biolum; corporate logo grid forbidden.

---

## 5. Hopecode — mycelial field map

**For:** Community meetup poster

**Prompt:**
> Original ED + AI — AI IN EDUCATION meetup graphic. HOPECODE lane: solarpunk mycelial mapping. Jittered hand-drawn paths, ochre ash rust moss earth tones, iridescent oil-slick interference on edges. Nodes labeled abstractly as small circles (no readable fake words except ED + AI and AI IN EDUCATION and BC + AI once each). Paper grain, photocopy scars, marginalia ticks. Irreverent embodied tone. No neat corporate diagrams.

---

## 6. Hopecode — parchment zones glyph

**For:** Vertical story slide

**Prompt:**
> Original HOPECODE-style poster for BC + AI ED + AI meetup. Torn paper texture, archival rot stains. Zones as irregular blobs connected by meandering ink lines; layered glyphs (abstract symbols only). Typography: monospace crossed with hand-lettered field notes feel — ED + AI dominant; AI IN EDUCATION as stamped ribbon; BC + AI in margin. Spectral fungi glow accents. Anti-colonial solarpunk energy.

---

## 7. Hopecode — network night soil

**For:** Dark background variant

**Prompt:**
> Original square graphic. HOPECODE lane on near-black soil background. Mycelial branches in warm rust and deep green; electric fungi glow in teal and violet specks. Title treatment: ED + AI in rough white chalk-like letters; AI IN EDUCATION curved along a branch; BC + AI in tiny orange ink. Dense but readable; analog bleed; found-not-made aesthetic.

---

## 8. Hopecode — spectral ribbon agenda

**For:** Wide banner feel in square crop

**Prompt:**
> Original meetup art ED + AI / AI IN EDUCATION / BC + AI. HOPECODE: horizontal spectral ribbon (rainbow oil interference) cuts across composition; above and below, mycelial tangles in earth tones. Type locks to ribbon with slight misalignment. Hand-drawn non-Euclidean curves. Texture heavy. No photoreal people; no robots.

---

## 9. BC + AI brand — coast forest radial network

**For:** Professional community centre vibe

**Prompt:**
> Original BC AI Community Centre lane graphic for ED + AI — AI IN EDUCATION meetup. Deep forest green and coast blue palette, birch white highlights, sunrise orange accents, twilight purple nodes. Interconnected organic network: soft circular nodes, irregular glowing paths, radial layout from lower center. Modern sans typography: ED + AI headline; AI IN EDUCATION sub; BC + AI lockup small. Rainforest meets innovation; minimum fifteen percent breathing room; professional not sterile.

---

## 10. BC + AI brand — wordmark mycelial frame

**For:** Clean hero with organic frame

**Prompt:**
> Original graphic: central BC + AI ecosystem wordmark treatment reinterpreted fresh (do not copy exact pixels) — mint and lime on dark navy. Surround with subtle mycelial frame in forest green and coast blue lines with growth green glow nodes. Top banner: ED + AI; beneath wordmark: AI IN EDUCATION in open sans caps. Balanced, legible at distance, still organic edges on frame.

---

## 11. BC + AI brand — STEM growth burst

**For:** Energetic event graphic

**Prompt:**
> Original ED + AI meetup square. BC + AI brand colors: navy base, orange callout sparks at network nodes, purple secondary glow. Abstract growth burst from center like opening bud made of circuit-organic hybrid lines (not literal circuit board clipart). ED + AI large; AI IN EDUCATION ring; BC + AI footer. Empowering collaborative learning mood; no dystopian robots.

---

## 12. Fusion — biolum core hopecode rim BC palette

**For:** Flagship blended concept

**Prompt:**
> Original fusion graphic for BC + AI ED + AI — AI IN EDUCATION. Center: biolum aurora circular gill vortex with cyan violet glow on black. Middle ring: hopecode jittered mycelial ink in earth tones. Outer margin: BC + AI community centre palette accents (forest green coast blue orange nodes) as small orbital dots. Typography hierarchy: ED + AI largest; AI IN EDUCATION; BC + AI credit. Cohesive not collage chaos; still dark-on-dark with disciplined contrast.

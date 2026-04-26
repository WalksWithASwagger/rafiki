# Mockups: Vancouver AI print on YOUR dyed long-sleeves

Reference photos (in order with sections below):

- `refs/ref-blank-dyed-shirt-01-comfort-colors-spiral-cyan-maroon.png`
- `refs/ref-blank-dyed-shirt-02-symmetric-inkblot-teal-magenta.png`
- `refs/ref-blank-dyed-shirt-03-spiral-magenta-cyan-navy.png`

Use **`--reference-role mockup`** so the tool keeps the shirt photo and adds ink.

```bash
cd tools/image-gen
npx image-gen ../../content/projects/apparel-screen-print/image-prompts-mockups-on-real-dyed-shirts.md \
  --reference-images "../../content/projects/apparel-screen-print/refs/ref-blank-dyed-shirt-01-comfort-colors-spiral-cyan-maroon.png,../../content/projects/apparel-screen-print/refs/ref-blank-dyed-shirt-02-symmetric-inkblot-teal-magenta.png,../../content/projects/apparel-screen-print/refs/ref-blank-dyed-shirt-03-spiral-magenta-cyan-navy.png" \
  --reference-role mockup \
  --model gemini-3-pro-image-preview \
  --resolution 2K \
  --aspect-ratio 3:4 \
  --output-dir ../../content/projects/apparel-screen-print/outputs/mockups-on-real-shirts \
  --no-style
```

---

## 1. Idea — Bone portal + rose wreath (matches spiral energy)

**For:** Shirt 01 — off-center spiral, cyan + maroon on dark navy

**Prompt:**
> Center-chest graphic only (do not cover the whole shirt). Large equilateral triangle built from three thick cartoon bones with stippled shading; inside the triangle a starfield with two planets (ringed + striped), bold black outlines. Wrap the triangle in a heart-shaped wreath of red roses, buds, thorns, and green leaves. Above: arched drippy psychedelic bubble letters spelling VANCOUVER AI with thick black outer stroke and lavender-to-maroon gradient in the fills; small ribbon with COMMUNITY if it stays readable. Slightly crooked, hand-inked, halftone texture — anti-corporate lot-tee poster. Size the emblem to fit the upper chest, respecting the spiral so the print reads clearly on both dark and bright dye areas.

---

## 2. Idea — Circular cosmic crest (matches symmetric inkblot)

**For:** Shirt 02 — vertical symmetry, teal/magenta Rorschach on dark body

**Prompt:**
> Center-chest circular emblem aligned with the shirt’s vertical symmetry. Concentric imperfect rings (cream, black) framing a deep purple cosmic interior with stars. Original figure in the middle: skeleton or friendly robot in a tall hat tipping the hat, holding a glowing galaxy orb — your own pose, not a copy of any band mascot. Red roses clustered at left and right inside the circle. Typography bent along the circle: VANCOUVER AI in rainbow-gradient drippy letters with heavy black outline; COMMUNITY arched smaller along the bottom inner arc if it fits. Vintage heavy screen-ink look with grain and slight misregistration. Keep the print scale appropriate for long-sleeve chest; do not obscure collar tag area unnecessarily.

---

## 3. Idea — Finalist blend: vortex circle + bone shield (matches magenta/cyan spiral)

**For:** Shirt 03 — spiral magenta/cyan/teal on black

**Prompt:**
> Center-chest print only. Synthesize ONE original graphic blending **circular cosmic vortex / portal** energy (drippy display type, skeleton hand, roses, stars) with **bone-frame shield** language (central rose with subtle circuit-in-petals, side rose stacks, lightning bolts, heavy black outlines, drippy lettering). **No robot, keyboard, synth, or lightning-bolt path landscape.** Typography: **VANCOUVER AI COMMUNITY** legible and warped. Vintage screen ink, halftone grain, hand-drawn 70s lot-tee. Size for upper chest; work with this shirt’s spiral dye for contrast.

**Note:** When regenerating this slot, pass your saved finalist PNGs as `--composition-references` (see `image-prompt-mockup-shirt03-finalist-blend.md`).

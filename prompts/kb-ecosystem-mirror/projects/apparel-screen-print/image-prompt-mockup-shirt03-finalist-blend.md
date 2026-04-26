# Single regen: shirt 03 mockup using your finalist art (no robot)

```bash
cd tools/image-gen
npx image-gen ../../content/projects/apparel-screen-print/image-prompt-mockup-shirt03-finalist-blend.md \
  --reference-images "../../content/projects/apparel-screen-print/refs/ref-blank-dyed-shirt-03-spiral-magenta-cyan-navy.png" \
  --reference-role mockup \
  --composition-references "../../content/projects/apparel-screen-print/refs/ref-user-finalist-circular-vortex-vancouver-ai.png,../../content/projects/apparel-screen-print/refs/ref-user-finalist-bone-shield-sunburst-vancouver-ai.png" \
  --model gemini-3-pro-image-preview \
  --resolution 2K \
  --aspect-ratio 3:4 \
  --output-dir ../../content/projects/apparel-screen-print/outputs/mockups-on-real-shirts \
  --no-style
```

---

## 1. Mockup — Finalist blend (vortex + bone shield, no robot)

**For:** Dyed long-sleeve 03 — magenta/cyan spiral on dark navy

**Prompt:**
> Center-chest print only. Synthesize ONE original graphic that **blends** the two reference artworks’ strengths: the **circular vortex / cosmic portal** energy with drippy yellow-orange VANCOUVER AI COMMUNITY type, skeleton hand reaching, roses, stars — AND the **bone-frame shield** with central cosmic rose (tech/petal circuit detail OK), side rose columns, lightning bolts, drippy black-outlined lettering, sunburst dye interaction. **Do not** include any robot, keyboard, synthesizer, or marching character. **Do not** use a lightning-bolt *path* landscape scene. Typography must stay drippy, melting, hand-drawn lot-tee poster. Heavy black outlines, halftone/stipple, slight misregistration. Words on the print: **VANCOUVER AI COMMUNITY** arranged legibly (arched top/bottom or similar). Scale for upper chest; respect this shirt’s real spiral dye so the art reads on both dark and bright dye areas.

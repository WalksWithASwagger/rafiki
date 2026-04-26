# Apparel / screen print — image prompts

Batch-generate from this repo’s image tool after you drop reference art in `refs/` and edit the prompts below.

**Batch command** (from `tools/image-gen`, adjust paths and `--ref` when you add a moodboard):

```bash
cd tools/image-gen
npx image-gen ../../content/projects/apparel-screen-print/image-prompts.md \
  --ref ../../content/projects/apparel-screen-print/refs/your-reference.png \
  --model gemini-3-pro-image-preview \
  --resolution 2K \
  --aspect-ratio square \
  --output-dir ../../content/projects/apparel-screen-print/outputs \
  --no-style
```

Use `--style kk`, `bcai`, `hopecode`, or `upgrade` instead of `--no-style` when the brief matches a preset. Omit `--ref` if you are not using a reference image yet.

---

## 1. Concept A — Placeholder title

**For:** Front chest print, 1–3 ink colors, high contrast for screen separation

**Prompt:**
> Replace this with your full brief: subject, composition, typography (if any), mood, and constraints (e.g. no photorealistic shading, bold outlines, print-safe). Mention spot-color look and large flat areas for screens.

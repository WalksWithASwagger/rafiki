# Handoff — YouTube Thumbnails (Animation Accelerator + RAP)

**Date:** 2026-06-09  
**Branch:** `codex/god-skills-agentic-loop-graphics`  
**Viewer:** `youtube-thumbnails-viewer.html` (open locally in browser)

## What shipped

### Animation Accelerator — Cohort 2, Week 3

**Winner (generative only, Week 1 plaque recipe):**
`output/animation-accelerator-youtube-thumbnails/cohort-2-week-3-2026-06-09-v3/run-20260609-060607/02-week-3-generative-plaque-pass-b.png`

- Model: `gpt-image-2` (`-m gpt`), 16:9, `--reference-role brand`, `--no-style`
- Prompt: `prompts/bcai/animation-accelerator-cohort-2-week-3-youtube-thumbnail.md`
- References: Luma source, blank plaque, Week 1 generative plaque (no flat BC+AI PNG — badge is generative in-scene)
- Copy baked in: `AI ANIMATION ACCELERATOR`, `COHORT 2`, `WEEK 3`, `RECORDING`
- BC+AI circular ecosystem badge integrated into the clay set

**Recipe reference (Week 1 north star):**
`prompts/bcai/animation-accelerator-cohort-2-week-1-youtube-thumbnail.md`  
Committed assets: `animation-accelerator/assets/public/youtube-thumbnails/cohort-2-week-1-2026-05-31/`

**Failed path (do not reuse):** Gemini Pro screening-room pass (`cohort-2-week-3-2026-06-09/`) — different look/quality from Week 1.

### Responsible AI Professional — Cohort 2, Week 3

**Winner (generative only, bioluminescent forest):**
`output/rap-youtube-thumbnails/cohort-2-week-3-2026-06-09-v2/run-20260609-061636/02-cohort-2-week-3-bioluminescent-pass-b.png`

- Model: `gpt-image-2`, 16:9, `--reference-role brand`, `--no-style`
- Prompt: `prompts/bcai/rap-cohort-2-week-3-youtube-thumbnail.md`
- References:
  1. Bioluminescent plate — `output/rap-youtube-thumbnails/cohort-1-week-3-2026-06-08/.../01-week-3-thumbnail-full-design.png`
  2. **RAP Certification shield** — `/Users/kk/Code/RAP/web/public/images/rap-cert.png` (NOT `rap-shield.png`)
  3. BC+AI logo — `/Users/kk/Code/RAP/web/public/brand/bcai/bcai-logo-official.png`
- Copy baked in: `RESPONSIBLE AI PROFESSIONAL`, `COHORT 2`, `WEEK 3`, `RECORDING`

**Critical asset note:** `rap-shield.png` is the hex badge used for Luma feature graphics. YouTube thumbnails need `rap-cert.png` (green shield, gold ribbon `CERTIFICATION`, star burst, BC+AI at base). Same pattern as `rap-sarah-images-v2` and completion-certificate v3/v4 prompts.

## Regenerate commands

```bash
# Animation Accelerator Week 3 (recommended recipe)
python generate.py \
  -f prompts/bcai/animation-accelerator-cohort-2-week-3-youtube-thumbnail.md \
  -d output/animation-accelerator-youtube-thumbnails/cohort-2-week-3-REFRESH \
  --no-style -m gpt --reference-role brand \
  --global-reference-images "/Users/kk/Code/rafiki/data/refs/animation-accelerator-source.jpg,/Users/kk/Code/animation-accelerator/assets/public/youtube-thumbnails/cohort-2-week-1-2026-05-31/background-blank-plaque.png,/Users/kk/Code/animation-accelerator/assets/public/youtube-thumbnails/cohort-2-week-1-2026-05-31/generated-text-plaque-source.png" \
  -a 16:9 -q high -w 2

# RAP Cohort 2 Week 3 (recommended recipe)
python generate.py \
  -f prompts/bcai/rap-cohort-2-week-3-youtube-thumbnail.md \
  -d output/rap-youtube-thumbnails/cohort-2-week-3-REFRESH \
  --no-style -m gpt --reference-role brand \
  --global-reference-images "/Users/kk/Code/rafiki/output/rap-youtube-thumbnails/cohort-1-week-3-2026-06-08/run-20260608-133031/01-week-3-thumbnail-full-design.png,/Users/kk/Code/RAP/web/public/images/rap-cert.png,/Users/kk/Code/RAP/web/public/brand/bcai/bcai-logo-official.png" \
  -a 16:9 -q high -w 2
```

## Desktop deliverables

- `~/Desktop/animation-accelerator-youtube-thumbnails-2026-06-09.zip` — committed animation assets + Rafiki runs
- `~/Desktop/youtube-thumbnails-raw-2026-06-09.zip` — all raw PNG/JPG from this session (both programs)

## Local gallery setup

The main viewer (`youtube-thumbnails-viewer.html`) now includes **future cohort promo graphics** in addition to session YouTube thumbnails.

**Symlink required for Animation Accelerator paths:**

```bash
ln -sf /Users/kk/Code/animation-accelerator /Users/kk/Code/rafiki/animation-accelerator
```

Without this symlink, AA Cohort 2–4 image cards will 404 locally. RAP promo graphics load from `output/` inside Rafiki and do not need the symlink.

## Animation Accelerator — Cohorts 3 & 4 promo graphics

Committed in the animation-accelerator repo (no new generation needed). Asset index: `animation-accelerator/content/campaigns/2026-animation-accelerator-cohorts-3-4/asset-index.md`

| Asset | Path |
| --- | --- |
| Cohort 3 Luma cover | `animation-accelerator/assets/public/campaign-graphics/luma-covers/2026-07-27-ai-animation-accelerator-luma-cover.png` |
| Cohort 4 Luma cover | `animation-accelerator/assets/public/campaign-graphics/luma-covers/2026-09-21-ai-animation-accelerator-luma-cover.png` |
| C3 social crops (4) | `animation-accelerator/assets/public/campaign-graphics/social-crops/cohorts-3-4/cohort-3-*.png` |
| C4 social crops (4) | `animation-accelerator/assets/public/campaign-graphics/social-crops/cohorts-3-4/cohort-4-*.png` |
| C3 web refresh | `animation-accelerator/assets/public/creative-site/cohorts/cohort-3-refresh-1600x900.webp` |
| C4 web refresh | `animation-accelerator/assets/public/creative-site/cohorts/cohort-4-refresh-1600x900.webp` |

## RAP — Future cohort enrollment promo graphics

**Not session thumbnails.** These are native Luma feature graphics for future enrollment dates:

- **01–10:** RAP Cohort 2 enrollment promo — starts August 7, 2026
- **11–20:** RAP Cohort 3 enrollment promo — starts September 18, 2026

**Batch location:**
`output/rap-cohort-feature-graphics-2026-native/raw-gpt-image-2/run-20260605-194358/`

**Batch viewer:**
`output/rap-cohort-feature-graphics-2026-native/raw-gpt-image-2/run-20260605-194358/viewer.html`

**Prompt:** `prompts/bcai/rap-cohort-feature-graphics-2026-native-2026-06-06.md`

**Regenerate command:**

```bash
python generate.py \
  -f prompts/bcai/rap-cohort-feature-graphics-2026-native-2026-06-06.md \
  -d output/rap-cohort-feature-graphics-2026-native/REFRESH \
  --no-style -m gpt --reference-role brand \
  --global-reference-images "/Users/kk/Code/RAP/web/public/brand/rap/rap-shield.png,/Users/kk/Code/RAP/web/public/brand/bcai/bcai-logo-official.png" \
  -a 16:9 -q high -w 2
```

Note: enrollment promos use `rap-shield.png` (hex badge for Luma covers). Session recording thumbnails use `rap-cert.png` (certification shield).

## Verify

```bash
open youtube-thumbnails-viewer.html
open output/animation-accelerator-youtube-thumbnails/cohort-2-week-3-2026-06-09-v3/viewer.html
open output/rap-youtube-thumbnails/cohort-2-week-3-2026-06-09-v2/viewer.html
open output/rap-cohort-feature-graphics-2026-native/raw-gpt-image-2/run-20260605-194358/viewer.html
```

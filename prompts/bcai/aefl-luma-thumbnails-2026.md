# AI Ethical Futures Lab Luma Thumbnails 2026

Purpose: create a six-image Rafiki review batch for the existing AI Ethical Futures Lab #5-#10 Luma events from July through December 2026. These are square Luma thumbnails with baked-in generated text.

Production rule: no overlays, compositing, or post-generation typography. The only readable generated text requested in this pass is:

- `AI ETHICAL FUTURES LAB`
- the event number
- the event date

Reject or rerun any candidate with malformed text, extra words, fake logos, real brand marks, sponsor marks, venue claims, incorrect dates, or public claims not in the prompt.

Run from Rafiki:

```bash
./.venv/bin/python generate.py \
  -f /Users/kk/Code/rafiki/prompts/bcai/aefl-luma-thumbnails-2026.md \
  -d /Users/kk/Code/rafiki/output/aefl-luma-thumbnails-2026 \
  --model gpt-image-2 \
  --style bcai \
  --aspect-ratio 1:1 \
  --workers 2
```

Global visual direction: abstract editorial posters for a BC civic policy lab, not literal room scenes and not corporate AI stock. Use deep cedar greens, coastal blues, muted gold, civic-map contours, subtle mycelial network lines, soft public-room light, and small unlabeled data nodes. Avoid people, faces, laptops, devices, paper, icons, logos, device brand marks, sponsor marks, venue signs, keynote-stage spectacle, and any small readable text. Keep the series visually related while allowing seasonal light and colour shifts.

## 1. AEFL #5 July Thumbnail

**For:** Luma event thumbnail, AI Ethical Futures Lab #5
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail as an abstract editorial poster, not a scene. Deep cedar green and coastal blue background with subtle mycelial network lines, civic-map contours, soft warm light, and small unlabeled data nodes. No people, no faces, no laptops, no devices, no paper, no icons, no logos, no symbols, no small text. Bake in only these readable words as native poster typography: `AI ETHICAL FUTURES LAB`, `#5`, `JULY 1, 2026`. The typography must be clean, correctly spelled, and large. No other words anywhere.

## 2. AEFL #6 August Thumbnail

**For:** Luma event thumbnail, AI Ethical Futures Lab #6
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail as an abstract editorial poster, not a scene. Warm late-summer cedar green, coastal blue, and muted gold background with subtle mycelial network lines, civic-map contours, soft public-room light, and small unlabeled data nodes. No people, no faces, no laptops, no devices, no paper, no icons, no logos, no symbols, no small text. Bake in only these readable words as native poster typography: `AI ETHICAL FUTURES LAB`, `#6`, `AUGUST 5, 2026`. The typography must be clean, correctly spelled, and large. No other words anywhere.

## 3. AEFL #7 September Thumbnail

**For:** Luma event thumbnail, AI Ethical Futures Lab #7
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail as an abstract editorial poster, not a scene. Early-fall BC palette with cedar green, coastal blue, first gold leaves as abstract texture, subtle mycelial network lines, civic-map contours, soft warm light, and small unlabeled data nodes. No people, no faces, no laptops, no devices, no paper, no icons, no logos, no symbols, no small text. Bake in only these readable words as native poster typography: `AI ETHICAL FUTURES LAB`, `#7`, `SEPTEMBER 2, 2026`. The typography must be clean, correctly spelled, and large. No other words anywhere.

## 4. AEFL #8 October Thumbnail

**For:** Luma event thumbnail, AI Ethical Futures Lab #8
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail as an abstract editorial poster, not a scene. Darker October forest palette with cedar green, coastal blue signal light, ember-gold highlights, subtle mycelial network lines, civic-map contours, soft warm glow, and small unlabeled data nodes. No people, no faces, no laptops, no devices, no paper, no icons, no logos, no symbols, no small text. Bake in only these readable words as native poster typography: `AI ETHICAL FUTURES LAB`, `#8`, `OCTOBER 7, 2026`. The typography must be clean, correctly spelled, and large. No other words anywhere.

## 5. AEFL #9 November Thumbnail

**For:** Luma event thumbnail, AI Ethical Futures Lab #9
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail as an abstract editorial poster, not a scene. Rain-season BC palette with wet cedar green, deep teal, warm table-light gold, subtle mycelial network lines, civic-map contours, mist, and small unlabeled data nodes. No people, no faces, no laptops, no devices, no paper, no icons, no logos, no symbols, no small text. Bake in only these readable words as native poster typography: `AI ETHICAL FUTURES LAB`, `#9`, `NOVEMBER 4, 2026`. The typography must be clean, correctly spelled, and large. No other words anywhere.

## 6. AEFL #10 December Thumbnail

**For:** Luma event thumbnail, AI Ethical Futures Lab #10
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail as an abstract editorial poster, not a scene. Winter teal, evergreen, soft gold room light, subtle crystalline data points, mycelial network lines, civic-map contours, and a calm year-end public-interest mood. No people, no faces, no laptops, no devices, no paper, no icons, no logos, no symbols, no small text, no holiday-card look. Bake in only these readable words as native poster typography: `AI ETHICAL FUTURES LAB`, `#10`, `DECEMBER 2, 2026`. The typography must be clean, correctly spelled, and large. No other words anywhere.

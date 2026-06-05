# Life Sciences Luma Meetups 2026

Purpose: create a six-image, generative-only Luma thumbnail review batch for AI + Life Sciences meetups between July and December 2026. The canonical visual anchor is the Healing Futures no-text art plate, especially the calm mountain-headed figure, cedar lungs, river/circulation system, salmon, ravens, microscopes, DNA, crystal data points, and civic science gathering details.

Production rule: no overlays, compositing, or post-generation typography. The only readable generated text requested in this pass is `AI + LIFE SCIENCES` plus the date. If the generated text is wrong, malformed, or ugly, reject or rerun the whole candidate.

Primary reference:

- `/Users/kk/Code/futureproof-festival/docs/internal/branding/outputs/life-sciences-generative-canonical-pass/run-20260603-233323/02-healing-futures-no-text-art-plate.png`

Secondary style anchor:

- `/Users/kk/Code/futureproof-festival/docs/internal/branding/outputs/r4a-03-life-sciences.png`

Explicitly exclude:

- `07-living-systems-badge-poster.png`
- badge/mandala drift
- Data Whale imagery
- fake sponsor marks
- venue claims
- hospital-blue clinical stock imagery
- generic scientist stock
- excessive generated text

Run from Rafiki:

```bash
./.venv/bin/python generate.py \
  -f /Users/kk/Code/rafiki/prompts/bcai/life-sciences-luma-meetups-2026.md \
  -d /Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026 \
  --model pro \
  --resolution 1K \
  --style futureproof-mythic+bcai-ecosystem \
  --reference-role style \
  --global-reference-images /Users/kk/Code/futureproof-festival/docs/internal/branding/outputs/life-sciences-generative-canonical-pass/run-20260603-233323/02-healing-futures-no-text-art-plate.png,/Users/kk/Code/futureproof-festival/docs/internal/branding/outputs/r4a-03-life-sciences.png \
  --workers 2
```

Global visual direction: stay very close to the Healing Futures no-text art plate. Use gentle monthly variation through atmosphere, seasonal plant details, light quality, and small civic-science details, not a new concept. Every image should read as one coherent series of Luma event thumbnails. Keep the same central mountain-headed figure and cedar lungs as the visual heart. Use a square `1:1` composition for Luma cover review.

## 1. July 7 Zoom Thumbnail

**For:** Luma event thumbnail, July Zoom meetup
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `JULY 7, 2026`. Stay very close to the Healing Futures no-text reference: a calm mountain-headed figure with cedar lungs, river circulation, salmon, ravens, microscopes, DNA, crystal data points, and small civic science gatherings. This July meeting is on Zoom, but keep the same visual system; show the Zoom clue subtly as one glowing portal, window, or tablet-like light surface inside the forest-lab world, not as corporate video-call UI. Bake in only the readable generated text `AI + LIFE SCIENCES` and `JULY 7, 2026` as native painted or printed poster text. No other words, no logos, no sponsors, no venue, no whale, no badge/mandala layout.

## 2. August 11 Thumbnail

**For:** Luma event thumbnail, August meetup
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `AUGUST 11, 2026`. Use the canonical Healing Futures figure: mountain head, calm face, cedar lungs, river/circulation system, salmon, ravens, microscopes, DNA, crystal data points, mycelium, and civic science gathering details. Gentle late-summer mood: warm dusk light, cedar green, coral lungs, cyan data-light, clear river motion. Keep the composition recognizably part of the same series as July. Bake in only `AI + LIFE SCIENCES` and `AUGUST 11, 2026` as native generated poster text. No other words, no logos, no sponsors, no venue, no whale, no badge/mandala layout.

## 3. September 8 Thumbnail

**For:** Luma event thumbnail, September meetup
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `SEPTEMBER 8, 2026`. Stay anchored in the Healing Futures world: the same calm mountain-headed figure and cedar lungs, with river circulation, salmon, ravens, microscopes, DNA, crystal data points, mycelium threads, and small public research groups. Gentle early-fall mood: deeper teal forest, first gold leaves, warm lab light, cyan signal details. Keep the figure central and iconic; vary only the atmosphere and small seasonal details. Bake in only `AI + LIFE SCIENCES` and `SEPTEMBER 8, 2026` as native generated poster text. No other words, no logos, no sponsors, no venue, no whale, no badge/mandala layout.

## 4. October 13 Thumbnail

**For:** Luma event thumbnail, October meetup
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `OCTOBER 13, 2026`. Keep the Healing Futures figure close to the reference: mountain head, calm face, cedar lungs, river/circulation system, salmon, ravens, microscopes, DNA, crystal data points, mycelium, and civic science gatherings. Gentle October mood: darker forest night, ember-gold leaves, coral lungs glowing warmly, cyan data-light moving through river and roots. This should feel like a direct sibling of the July, August, and September thumbnails, not a new direction. Bake in only `AI + LIFE SCIENCES` and `OCTOBER 13, 2026` as native generated poster text. No other words, no logos, no sponsors, no venue, no whale, no badge/mandala layout.

## 5. November 10 Thumbnail

**For:** Luma event thumbnail, November meetup
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `NOVEMBER 10, 2026`. Stay close to the Healing Futures no-text art plate: mountain-headed figure, cedar lungs, river circulation, salmon, ravens, microscopes, DNA, crystal data points, mycelium, and public science gatherings. Gentle November mood: rain-dark cedar forest, mist, wet bark, bright warm lungs, cyan data-light reflected in water, quiet lab glow. Keep the composition iconic and consistent with the series. Bake in only `AI + LIFE SCIENCES` and `NOVEMBER 10, 2026` as native generated poster text. No other words, no logos, no sponsors, no venue, no whale, no badge/mandala layout.

## 6. December 8 Thumbnail

**For:** Luma event thumbnail, December meetup
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `DECEMBER 8, 2026`. Use the canonical Healing Futures figure and cedar lungs as the central anchor, with river/circulation, salmon, ravens, microscopes, DNA, crystal data points, mycelium, and small civic science gathering details. Gentle December mood: deep winter teal, cool mist, evergreen density, soft gold lab warmth, coral lungs, cyan data-light, crystalline frost details on branches and mountains. Keep the same series language; do not turn it into a holiday card. Bake in only `AI + LIFE SCIENCES` and `DECEMBER 8, 2026` as native generated poster text. No other words, no logos, no sponsors, no venue, no whale, no badge/mandala layout.

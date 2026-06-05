# Life Sciences Luma Meetups 2026 — Monthly Variations v2

Purpose: create a 15-image, generative-only review batch for AI + Life Sciences Luma thumbnails. July is locked and not regenerated; use it as the visual anchor for the series. Generate 3 new candidates each for August through December, gradually evolving the ecology motifs while preserving one coherent Healing Futures look.

Production rule: no overlays, compositing, or post-generation typography. All required text and the BC+AI ecosystem logo must be generated natively into the artwork. Reject or rerun candidates with garbled event text, bad dates, fake sponsor/venue claims, fake URLs, Data Whale drift, badge/mandala drift, or a badly malformed BC+AI mark.

Reference key passed as globals:

- Reference #1: locked July thumbnail and series anchor — `/Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026/run-20260604-084403/01-july-7-zoom-thumbnail.png`
- Reference #2: canonical Healing Futures no-text art plate — `/Users/kk/Code/agent-worktrees/futureproof-competitive-intel-323-fix-20260604/docs/internal/branding/outputs/life-sciences-generative-canonical-pass/run-20260603-233323/02-healing-futures-no-text-art-plate.png`
- Reference #3: official BC+AI ecosystem logo — `/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png`

Run from Rafiki:

```bash
./.venv/bin/python generate.py \
  -f /Users/kk/Code/rafiki/prompts/bcai/life-sciences-luma-meetups-2026-variations-v2.md \
  -d /Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026-variations-v2 \
  --model pro \
  --resolution 1K \
  --style futureproof-mythic+bcai-ecosystem \
  --reference-role brand \
  --global-reference-images /Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026/run-20260604-084403/01-july-7-zoom-thumbnail.png,/Users/kk/Code/agent-worktrees/futureproof-competitive-intel-323-fix-20260604/docs/internal/branding/outputs/life-sciences-generative-canonical-pass/run-20260603-233323/02-healing-futures-no-text-art-plate.png,/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png \
  --workers 2
```

Global visual direction: keep the same square poster system as the locked July thumbnail. The central Healing Futures figure remains primary in every candidate: calm mountain head, cedar lungs, river/circulation, salmon, ravens, microscopes, DNA/data-light, crystal data points, cedar forest, and civic science gatherings. Monthly ecology motifs support the figure; they do not replace her. The only readable typography should be `AI + LIFE SCIENCES`, the correct date, and a small full official `BC+AI ecosystem` lockup based on reference #3. Integrate the logo as a lower-corner field tag, lab card, notebook mark, poster imprint, or small ecosystem maker's mark; no pasted-on overlay, no black sponsor box, no fake alternate BC+AI mark.

## 1. August 11 — Salmon Return River

**For:** Luma event thumbnail, August wild salmon return candidate A
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `AUGUST 11, 2026`. Stay tightly in the locked July / Healing Futures visual system: central calm mountain-headed figure, cedar lungs, river circulation, ravens, microscopes, DNA/data-light, crystal points, civic science gathering details. Make August about wild salmon returns: a luminous salmon run moving upstream through the figure's river-circulation path, coral gills and teal data currents echoing the lungs. Add a small official `BC+AI ecosystem` logo lockup from reference #3 as a generated lower-corner field tag or lab-card imprint, integrated into the illustration. Bake in only `AI + LIFE SCIENCES`, `AUGUST 11, 2026`, and the BC+AI ecosystem lockup. No other words, no sponsors, no venue, no URL, no whale, no badge/mandala layout.

## 2. August 11 — Estuary Life Cycle

**For:** Luma event thumbnail, August wild salmon return candidate B
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `AUGUST 11, 2026`. Preserve the same central Healing Futures figure and poster language from the July reference: mountain head, cedar lungs, river/circulation, ravens, microscopes, DNA, cyan data-light, coral/teal on deep forest night. Focus August on the salmon life cycle: estuary, river mouth, returning adult salmon, tiny eggs, and circular biological timing woven into the river, all supporting the central figure. Add the official `BC+AI ecosystem` logo from reference #3 as a small generated mark on a field notebook or lower-corner science tag. Bake in only `AI + LIFE SCIENCES`, `AUGUST 11, 2026`, and the BC+AI ecosystem lockup. No other text, logos, sponsors, venue claims, URL, whale imagery, or badge/mandala composition.

## 3. August 11 — Cedar Spawning Ground

**For:** Luma event thumbnail, August wild salmon return candidate C
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `AUGUST 11, 2026`. Keep the July thumbnail as the composition anchor: central mountain-headed woman, cedar lungs, river-circulation, ravens, microscopes, DNA/data-light, civic science gatherings, handmade PNW mythic science poster style. Make August feel like a cedar-shaded spawning ground: salmon redds, gravel, clear water, cedar roots, warm late-summer light, and biological data crystals flowing through the river. Include a small generated official `BC+AI ecosystem` logo lockup from reference #3 on a lower-corner poster imprint or lab card, native to the art. Only readable text: `AI + LIFE SCIENCES`, `AUGUST 11, 2026`, and BC+AI ecosystem. No sponsors, venue, URL, whale, generic scientist stock, or badge/mandala drift.

## 4. September 8 — Salmon And Bear River Edge

**For:** Luma event thumbnail, September salmon plus bear candidate A
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `SEPTEMBER 8, 2026`. Stay close to the locked July / Healing Futures system: the central mountain-headed figure with cedar lungs remains primary, with river circulation, salmon, ravens, microscopes, DNA/data-light, crystal points, and small civic science gathering details. Add September's ecology motif as a respectful coastal bear at the river edge watching the salmon return, supporting the living-systems story without becoming the main subject. Early fall gold leaves, teal forest, coral lungs, cyan water signals. Add the official `BC+AI ecosystem` logo from reference #3 as a small generated lower-corner lab tag or notebook mark. Only readable text: `AI + LIFE SCIENCES`, `SEPTEMBER 8, 2026`, and BC+AI ecosystem. No other words, fake sponsors, venue, URL, whale, or badge/mandala layout.

## 5. September 8 — Bear Tracks Field Notes

**For:** Luma event thumbnail, September salmon plus bear candidate B
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `SEPTEMBER 8, 2026`. Keep the same iconic central Healing Futures figure, mountain head, cedar lungs, river-circulation, ravens, microscopes, DNA/data-light, salmon, civic science groups, and dense handmade poster texture. Make September about field notes from a salmon-bearing river: bear tracks in wet sand, returning salmon in the water, small researchers observing respectfully, and golden early-fall cedar light. The bear should be present but secondary, nested into the ecosystem. Include the official `BC+AI ecosystem` logo from reference #3 as a small generated full lockup printed on a field notebook or lower-corner science card. Only readable text: `AI + LIFE SCIENCES`, `SEPTEMBER 8, 2026`, and BC+AI ecosystem. No venue, sponsors, URLs, whale imagery, or badge/mandala drift.

## 6. September 8 — Bear Constellation Over Salmon

**For:** Luma event thumbnail, September salmon plus bear candidate C
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `SEPTEMBER 8, 2026`. Use the July thumbnail and Healing Futures art plate as strict style anchors: central mountain-headed woman, cedar lungs, river circulation, salmon, ravens, microscopes, DNA/data-light, crystal points, civic science gatherings. For September, add a subtle bear-shaped constellation or aurora silhouette above the salmon river, plus a small real bear shape at the forest edge; make it ecological, not mascot-like. Keep the figure dominant and the set cohesive. Include the official `BC+AI ecosystem` logo lockup from reference #3 as a small generated lower-corner poster imprint. Only readable text: `AI + LIFE SCIENCES`, `SEPTEMBER 8, 2026`, and BC+AI ecosystem. No extra words, fake sponsor marks, venue claims, URL, whale, or badge layout.

## 7. October 13 — Mycelium Salmon Memory

**For:** Luma event thumbnail, October mycelium/rainforest candidate A
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `OCTOBER 13, 2026`. Preserve the locked July / Healing Futures look: central mountain-headed figure, cedar lungs, river-circulation, salmon, ravens, microscopes, DNA/data-light, crystal points, civic science gathering details. Make October about mycelium and salmon memory: fungal threads under cedar roots carrying data-light from decomposing salmon nutrients into forest, lungs, and river. Ember-gold leaves, darker rainforest night, teal/coral glow. Add the official `BC+AI ecosystem` logo from reference #3 as a small generated lower-corner field tag or lab-card imprint. Only readable text: `AI + LIFE SCIENCES`, `OCTOBER 13, 2026`, and BC+AI ecosystem. No sponsors, venue, URL, whale, fake logos, or badge/mandala composition.

## 8. October 13 — Rainforest Network Lab

**For:** Luma event thumbnail, October mycelium/rainforest candidate B
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `OCTOBER 13, 2026`. Stay very close to the July and Healing Futures references: calm mountain-headed figure, cedar lungs, river/circulation, salmon, ravens, microscopes, DNA, crystal data points, and civic science gatherings in a dense PNW folk-surreal poster. Make October a rainforest network lab: mushrooms, cedar roots, wet leaves, microscopes on tiny forest platforms, and cyan mycelium/data threads connecting salmon, soil, lungs, and forest. Include a small generated official `BC+AI ecosystem` logo lockup from reference #3 on a notebook, field tag, or lower-corner poster imprint. Only readable text: `AI + LIFE SCIENCES`, `OCTOBER 13, 2026`, and BC+AI ecosystem. No extra text, fake sponsors, venue, URL, whale, or badge drift.

## 9. October 13 — Salmon Nutrient Loop

**For:** Luma event thumbnail, October mycelium/rainforest candidate C
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `OCTOBER 13, 2026`. Keep the central Healing Futures figure as the visual heart: mountain head, calm face, cedar lungs, coral/teal river circulation, salmon, ravens, microscopes, DNA/data-light, crystal points, civic science gathering details. Make October about the salmon nutrient loop: salmon, cedar roots, fungi, soil, lungs, and river arranged as one living system. Darker autumn forest, amber leaves, cyan signal threads, warm coral lungs. Add the official `BC+AI ecosystem` logo from reference #3 as a small generated lower-corner ecosystem maker's mark. Only readable text: `AI + LIFE SCIENCES`, `OCTOBER 13, 2026`, and BC+AI ecosystem. No other words, sponsor claims, venue, URL, whale, or badge/mandala layout.

## 10. November 10 — Rain Cedar Field Station

**For:** Luma event thumbnail, November rain/cedar field lab candidate A
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `NOVEMBER 10, 2026`. Stay anchored to the July / Healing Futures visual system: central mountain-headed figure, cedar lungs, river circulation, salmon, ravens, microscopes, DNA/data-light, crystal points, small civic science gatherings. Make November a rain-soaked cedar field station: wet bark, mist, rain lines, portable microscopes under cedar shelter, field notebooks, salmon in the river, cyan reflections in water, warm lungs in the rain. Add the official `BC+AI ecosystem` logo from reference #3 as a small generated full lockup on a waterproof lower-corner field tag or notebook label. Only readable text: `AI + LIFE SCIENCES`, `NOVEMBER 10, 2026`, and BC+AI ecosystem. No fake sponsors, venue, URL, whale, generic hospital imagery, or badge/mandala drift.

## 11. November 10 — Cedar Data Shelter

**For:** Luma event thumbnail, November rain/cedar field lab candidate B
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `NOVEMBER 10, 2026`. Use the locked July thumbnail and Healing Futures art plate as strict anchors: central mountain-headed woman, cedar lungs, river/circulation, salmon, ravens, microscopes, DNA/data-light, crystals, civic science groups, handmade PNW mythic science style. Make November about a cedar data shelter: researchers and community members gathered under living cedar branches, rain-dark forest, river measurements, salmon moving through the water, cyan data-light reflected in puddles. Include the official `BC+AI ecosystem` logo lockup from reference #3 as a small generated lower-corner lab card. Only readable text: `AI + LIFE SCIENCES`, `NOVEMBER 10, 2026`, and BC+AI ecosystem. No other text, sponsors, venue, URL, whale, or badge/mandala layout.

## 12. November 10 — Night River Field Lab

**For:** Luma event thumbnail, November rain/cedar field lab candidate C
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `NOVEMBER 10, 2026`. Preserve the same Healing Futures figure and series layout: mountain head, cedar lungs, river circulation, salmon, ravens, microscopes, DNA/data-light, crystal points, civic science gatherings, deep forest poster texture. Make November a night river field lab in rain: lantern-warm research circles, wet cedar, mist, test tubes, field scopes, salmon silhouettes, cyan circuitry in water and roots. Add the official `BC+AI ecosystem` logo from reference #3 as a small generated lower-corner field-station mark or notebook imprint. Only readable text: `AI + LIFE SCIENCES`, `NOVEMBER 10, 2026`, and BC+AI ecosystem. No sponsors, venues, URLs, whale imagery, clinical stock, or badge/mandala drift.

## 13. December 8 — Frost Lungs Healing System

**For:** Luma event thumbnail, December frost/mountain healing candidate A
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `DECEMBER 8, 2026`. Stay in the locked July / Healing Futures visual system: central mountain-headed figure, cedar lungs, river circulation, salmon, ravens, microscopes, DNA/data-light, crystal points, civic science gathering details. Make December about frost and healing systems: crystalline frost on cedar lungs and mountain branches, cool mist, evergreen density, winter river data-light, salmon moving through cold water, warm coral lungs glowing gently. Include the official `BC+AI ecosystem` logo from reference #3 as a small generated lower-corner poster imprint or lab card. Only readable text: `AI + LIFE SCIENCES`, `DECEMBER 8, 2026`, and BC+AI ecosystem. No holiday-card treatment, sponsors, venue, URL, whale, or badge/mandala layout.

## 14. December 8 — Mountain Systems Winter

**For:** Luma event thumbnail, December frost/mountain healing candidate B
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `DECEMBER 8, 2026`. Keep the central Healing Futures figure dominant: mountain head, calm face, cedar lungs, river/circulation, salmon, ravens, microscopes, DNA/data-light, crystals, civic science gatherings, coral/teal handmade poster style. Make December about mountain healing systems: snow-dusted mountains in the figure's crown, crystalline data points, frost tracing river and roots, salmon and cedar held in one winter life-support network. Add the official `BC+AI ecosystem` logo lockup from reference #3 as a small generated lower-corner field tag or notebook mark. Only readable text: `AI + LIFE SCIENCES`, `DECEMBER 8, 2026`, and BC+AI ecosystem. No sponsors, venue, URL, whale, generic hospital imagery, holiday card, or badge drift.

## 15. December 8 — Winter River Commons

**For:** Luma event thumbnail, December frost/mountain healing candidate C
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `DECEMBER 8, 2026`. Use the July and Healing Futures references as strict continuity anchors: central mountain-headed woman, cedar lungs, river circulation, salmon, ravens, microscopes, DNA/data-light, crystal points, and small civic science gatherings. Make December a winter river commons: soft snow on cedar branches, cold mist, crystalline roots, warm field-lab circles, salmon passing through teal water, lungs glowing coral under frost. Include the official `BC+AI ecosystem` logo from reference #3 as a small generated lower-corner poster imprint, integrated into the illustration. Only readable text: `AI + LIFE SCIENCES`, `DECEMBER 8, 2026`, and BC+AI ecosystem. No extra words, sponsors, venue claims, URLs, whale, holiday card styling, or badge/mandala layout.

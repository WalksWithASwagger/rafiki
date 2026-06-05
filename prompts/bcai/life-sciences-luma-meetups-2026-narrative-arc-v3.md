# Life Sciences Luma Meetups 2026 - Narrative Ecology Arc v3

Purpose: create a 15-image, generative-only review batch for AI + Life Sciences Luma thumbnails. July is locked and not regenerated; use it as the visual anchor. This pass should read as a visible ecology story arc, not a set of seasonal swaps: salmon returns, salmon plus bear, ravens as intelligence/messenger thread, rain/cedar field labs, and winter healing systems.

Production rule: no overlays, compositing, or post-generation typography. All required text and the BC+AI ecosystem logo must be generated natively into the artwork. Reject or rerun candidates with garbled event text, bad dates, fake sponsor/venue claims, fake URLs, Data Whale drift, badge/mandala drift, extra readable text, or a badly malformed BC+AI mark.

Reference key passed as globals:

- Reference #1: locked July thumbnail and series anchor - `/Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026/run-20260604-084403/01-july-7-zoom-thumbnail.png`
- Reference #2: canonical Healing Futures no-text art plate - `/Users/kk/Desktop/futureproof-life-sciences-generations-2026-06-04/futureproof-festival/docs/internal/branding/outputs/life-sciences-generative-canonical-pass/run-20260603-233323/02-healing-futures-no-text-art-plate.png`
- Reference #3: official BC+AI ecosystem logo - `/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png`

Per-prompt references:

- August: v2 keepers `01`, `02`, `03`
- September: v2 keepers `04`, `06`, `04`
- October: v2 keepers `07`, `09`, `09`
- November: v2 keepers `10`, `11`, `12`
- December: v2 keepers `13`, `14`, `15`

Run from Rafiki:

```bash
./.venv/bin/python generate.py \
  -f /Users/kk/Code/rafiki/prompts/bcai/life-sciences-luma-meetups-2026-narrative-arc-v3.md \
  -d /Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026-narrative-arc-v3 \
  --model pro \
  --resolution 1K \
  --style futureproof-mythic+bcai-ecosystem \
  --reference-role brand \
  --global-reference-images /Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026/run-20260604-084403/01-july-7-zoom-thumbnail.png,/Users/kk/Desktop/futureproof-life-sciences-generations-2026-06-04/futureproof-festival/docs/internal/branding/outputs/life-sciences-generative-canonical-pass/run-20260603-233323/02-healing-futures-no-text-art-plate.png,/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png \
  --reference-images /Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026-variations-v2/run-20260604-093718/01-august-11-salmon-return-river.png,/Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026-variations-v2/run-20260604-093718/02-august-11-estuary-life-cycle.png,/Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026-variations-v2/run-20260604-093718/03-august-11-cedar-spawning-ground.png,/Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026-variations-v2/run-20260604-093718/04-september-8-salmon-and-bear-river-edge.png,/Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026-variations-v2/run-20260604-093718/06-september-8-bear-constellation-over-salmon.png,/Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026-variations-v2/run-20260604-093718/04-september-8-salmon-and-bear-river-edge.png,/Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026-variations-v2/run-20260604-093718/07-october-13-mycelium-salmon-memory.png,/Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026-variations-v2/run-20260604-093718/09-october-13-salmon-nutrient-loop.png,/Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026-variations-v2/run-20260604-093718/09-october-13-salmon-nutrient-loop.png,/Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026-variations-v2/run-20260604-093718/10-november-10-rain-cedar-field-station.png,/Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026-variations-v2/run-20260604-093718/11-november-10-cedar-data-shelter.png,/Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026-variations-v2/run-20260604-093718/12-november-10-night-river-field-lab.png,/Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026-variations-v2/run-20260604-093718/13-december-8-frost-lungs-healing-system.png,/Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026-variations-v2/run-20260604-093718/14-december-8-mountain-systems-winter.png,/Users/kk/Code/rafiki/output/life-sciences-luma-meetups-2026-variations-v2/run-20260604-093718/15-december-8-winter-river-commons.png \
  --workers 2
```

Global visual direction: keep the same square poster system as the locked July thumbnail. The central Healing Futures figure remains primary in every candidate: calm mountain head, cedar lungs, river/circulation, salmon, ravens, microscopes, DNA/data-light, crystal data points, cedar forest, and civic science gatherings. This pass should show narrative shift: each month changes what the ecology is doing in the story, not merely the weather. Wildlife and ecology motifs support the figure; they do not replace her. The only readable typography should be `AI + LIFE SCIENCES`, the correct date, and a small full official `BC+AI ecosystem` lockup based on reference #3. Integrate the logo as a lower-corner field tag, lab card, notebook mark, poster imprint, or small ecosystem maker's mark; no pasted-on overlay, no black sponsor box, no fake alternate BC+AI mark.

## 1. August 11 - Salmon Data Return

**For:** Luma event thumbnail, August narrative candidate A
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `AUGUST 11, 2026`. Start the narrative arc with the salmon return as living data: bright salmon move upstream through the central Healing Futures figure's river-circulation path, carrying coral and teal signal-light through her cedar lungs, into civic science circles, microscopes, DNA strands, and crystal data points. Stay close to the locked July composition and the August v2 reference: calm mountain-headed figure remains dominant, cedar forest, ravens present but quiet observers. Add a small generated official `BC+AI ecosystem` logo lockup from reference #3 as an integrated lower-corner field tag or lab-card imprint. Bake in only `AI + LIFE SCIENCES`, `AUGUST 11, 2026`, and the BC+AI ecosystem lockup. No other words, no sponsors, no venue, no URL, no whale, no badge/mandala layout.

## 2. August 11 - Estuary To Lungs

**For:** Luma event thumbnail, August narrative candidate B
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `AUGUST 11, 2026`. Make August the first chapter: salmon enter from estuary and river mouth into the figure's body-world, and their route becomes a visible bridge from water to cedar lungs to community knowledge. Keep the central mountain-headed Healing Futures figure primary, calm and close to the canonical references; include salmon, river circulation, ravens in the trees, microscopes, DNA/data-light, crystal points, and small civic science gathering details. Use late-summer teal, coral, cedar green, and warm river light. Add a small generated official `BC+AI ecosystem` logo from reference #3 on a field notebook or lower-corner science tag. Only readable text: `AI + LIFE SCIENCES`, `AUGUST 11, 2026`, and BC+AI ecosystem. No extra text, sponsors, venue claims, URL, whale imagery, or badge/mandala composition.

## 3. August 11 - Spawning Ground Signal

**For:** Luma event thumbnail, August narrative candidate C
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `AUGUST 11, 2026`. Show the salmon return becoming a biological signal system: spawning-ground gravel, cedar roots, eggs, clear river water, and glowing data crystals are woven through the central Healing Futures figure's lungs and circulation. This is chapter one of a longer ecology story, so the bear and raven motifs should be only hinted in the background, waiting for later months. Preserve the July thumbnail's square poster language: central mountain-headed woman, cedar lungs, river-circulation, ravens, microscopes, DNA/data-light, civic science gatherings, handmade PNW mythic science texture. Include a small generated official `BC+AI ecosystem` logo from reference #3 on a lower-corner poster imprint or lab card. Only readable text: `AI + LIFE SCIENCES`, `AUGUST 11, 2026`, and BC+AI ecosystem. No sponsors, venue, URL, whale, generic scientist stock, or badge/mandala drift.

## 4. September 8 - Bear At The River Edge

**For:** Luma event thumbnail, September narrative candidate A
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `SEPTEMBER 8, 2026`. Continue the narrative arc: the salmon return now brings a respectful coastal bear to the river edge, turning August's living data into embodied field knowledge and careful observation. The central Healing Futures figure with mountain head and cedar lungs stays primary, with river circulation, salmon, ravens, microscopes, DNA/data-light, crystal points, and civic science details. The bear should be powerful but secondary, watching rather than posing; salmon, river, and the figure still carry the composition. Add the official `BC+AI ecosystem` logo from reference #3 as a small generated lower-corner lab tag or notebook mark. Only readable text: `AI + LIFE SCIENCES`, `SEPTEMBER 8, 2026`, and BC+AI ecosystem. No other words, fake sponsors, venue, URL, whale, or badge/mandala layout.

## 5. September 8 - Tracks As Field Knowledge

**For:** Luma event thumbnail, September narrative candidate B
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `SEPTEMBER 8, 2026`. Make September a chapter about field knowledge: bear tracks in wet sand, salmon in the river, cedar roots, and respectful researchers/community members reading the ecosystem without extracting from it. Keep the iconic central Healing Futures figure dominant, mountain head, cedar lungs, river-circulation, ravens, microscopes, DNA/data-light, salmon, civic science groups, and dense handmade poster texture. Avoid notebook pages with fake writing; field-note objects may appear but must not contain readable words except the event title/date/logo. Include the official `BC+AI ecosystem` logo from reference #3 as a small generated full lockup printed on a lower-corner science card. Only readable text: `AI + LIFE SCIENCES`, `SEPTEMBER 8, 2026`, and BC+AI ecosystem. No venue, sponsors, URLs, whale imagery, or badge/mandala drift.

## 6. September 8 - Bear And Salmon Constellation

**For:** Luma event thumbnail, September narrative candidate C
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `SEPTEMBER 8, 2026`. Continue from August by making the salmon return visible in the sky as a subtle bear-and-salmon constellation, while a small real bear remains at the forest river edge. The story should feel like field observation becoming pattern recognition. Use the July thumbnail and Healing Futures art plate as strict anchors: central mountain-headed woman, cedar lungs, river circulation, salmon, ravens, microscopes, DNA/data-light, crystal points, civic science gatherings. Keep the figure dominant and the set cohesive. Include the official `BC+AI ecosystem` logo lockup from reference #3 as a small generated lower-corner poster imprint. Only readable text: `AI + LIFE SCIENCES`, `SEPTEMBER 8, 2026`, and BC+AI ecosystem. No extra words, fake sponsor marks, venue claims, URL, whale, or badge layout.

## 7. October 13 - Ravens Carry Salmon Memory

**For:** Luma event thumbnail, October narrative candidate A
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `OCTOBER 13, 2026`. This is the chapter where ravens become the visible intelligence and messenger thread. Keep the central Healing Futures figure primary: mountain head, calm face, cedar lungs, river-circulation, salmon, microscopes, DNA/data-light, crystal points, civic science details. Show ravens carrying small cyan/coral data-light between salmon, cedar roots, mycelium, and the figure's lungs, as if the ecosystem is remembering and passing knowledge onward. Darker rainforest night, ember-gold leaves, teal/coral glow. Add the official `BC+AI ecosystem` logo from reference #3 as a small generated lower-corner field tag or lab-card imprint. Only readable text: `AI + LIFE SCIENCES`, `OCTOBER 13, 2026`, and BC+AI ecosystem. No sponsors, venue, URL, whale, fake logos, or badge/mandala composition.

## 8. October 13 - Mycelium Messenger Lab

**For:** Luma event thumbnail, October narrative candidate B
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `OCTOBER 13, 2026`. Make October a messenger-system chapter: ravens, mycelium threads, salmon nutrients, cedar roots, microscopes, and cyan data-light all carry information through the forest-lab world. Stay very close to the July and Healing Futures references, especially the central calm mountain-headed figure with cedar lungs and river/circulation; do not let generic scientists or lab gear replace her. Place ravens around the figure as watchful messengers, not a separate bird poster. Include a small generated official `BC+AI ecosystem` logo lockup from reference #3 on a lower-corner field tag or poster imprint. Only readable text: `AI + LIFE SCIENCES`, `OCTOBER 13, 2026`, and BC+AI ecosystem. No extra text, fake sponsors, venue, URL, whale, or badge drift.

## 9. October 13 - Nutrient Loop Intelligence

**For:** Luma event thumbnail, October narrative candidate C
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `OCTOBER 13, 2026`. Show the story arc deepening from salmon and bear into ecosystem intelligence: salmon nutrients feed cedar roots and fungi, mycelium glows like a living network, and ravens carry tiny signal lights through the composition. Keep the central Healing Futures figure as the visual heart: mountain head, calm face, cedar lungs, coral/teal river circulation, salmon, ravens, microscopes, DNA/data-light, crystal points, civic science gathering details. Dark autumn forest, amber leaves, cyan signal threads, warm coral lungs. Add the official `BC+AI ecosystem` logo from reference #3 as a small generated lower-corner ecosystem maker's mark. Only readable text: `AI + LIFE SCIENCES`, `OCTOBER 13, 2026`, and BC+AI ecosystem. No other words, sponsor claims, venue, URL, whale, or badge/mandala layout.

## 10. November 10 - Rain Cedar Field Practice

**For:** Luma event thumbnail, November narrative candidate A
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `NOVEMBER 10, 2026`. Turn the October intelligence thread into civic science practice: rain-soaked cedar shelter, portable microscopes, community field-lab circles, ravens watching from wet branches, salmon still moving through the river, and cyan data-light reflected in rain and roots. Stay anchored to the July / Healing Futures visual system: central mountain-headed figure, cedar lungs, river circulation, salmon, ravens, microscopes, DNA/data-light, crystal points, small civic science gatherings. The figure remains primary; the field lab gathers around her living system. Add the official `BC+AI ecosystem` logo from reference #3 as a small generated full lockup on a waterproof lower-corner field tag. Only readable text: `AI + LIFE SCIENCES`, `NOVEMBER 10, 2026`, and BC+AI ecosystem. No fake sponsors, venue, URL, whale, generic hospital imagery, or badge/mandala drift.

## 11. November 10 - Cedar Shelter Commons

**For:** Luma event thumbnail, November narrative candidate B
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `NOVEMBER 10, 2026`. Make November the commons chapter: community members and researchers gather under living cedar branches, reading salmon, rain, ravens, and mycelium together as one field-lab practice. Use the locked July thumbnail and Healing Futures art plate as strict anchors: central mountain-headed woman, cedar lungs, river/circulation, salmon, ravens, microscopes, DNA/data-light, crystals, civic science groups, handmade PNW mythic science style. Rain should connect everything, not hide the figure. Include the official `BC+AI ecosystem` logo lockup from reference #3 as a small generated lower-corner lab card. Only readable text: `AI + LIFE SCIENCES`, `NOVEMBER 10, 2026`, and BC+AI ecosystem. No other text, sponsors, venue, URL, whale, or badge/mandala layout.

## 12. November 10 - Night River Methods

**For:** Luma event thumbnail, November narrative candidate C
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `NOVEMBER 10, 2026`. This chapter turns ecology into method: night river field lab, lantern-warm research circles, wet cedar, ravens above, salmon silhouettes, cyan circuitry in water and roots, microscopes and test tubes integrated into the living system. Preserve the same Healing Futures figure and series layout: mountain head, cedar lungs, river circulation, salmon, ravens, microscopes, DNA/data-light, crystal points, civic science gatherings, deep forest poster texture. Keep field-lab objects secondary and avoid fake labels. Add the official `BC+AI ecosystem` logo from reference #3 as a small generated lower-corner field-station mark or notebook imprint. Only readable text: `AI + LIFE SCIENCES`, `NOVEMBER 10, 2026`, and BC+AI ecosystem. No sponsors, venues, URLs, whale imagery, clinical stock, or badge/mandala drift.

## 13. December 8 - Frost Memory System

**For:** Luma event thumbnail, December narrative candidate A
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `DECEMBER 8, 2026`. Resolve the arc into deep-time healing systems: salmon memory, raven signals, cedar lungs, frost crystals, mountain snow, mycelium, and river data-light all held inside the central Healing Futures figure. Stay in the locked July / Healing Futures visual system: central mountain-headed figure, cedar lungs, river circulation, salmon, ravens, microscopes, DNA/data-light, crystal points, civic science gathering details. Frost should clarify the living system like a map, not turn it into a holiday card. Include the official `BC+AI ecosystem` logo from reference #3 as a small generated lower-corner poster imprint or lab card. Only readable text: `AI + LIFE SCIENCES`, `DECEMBER 8, 2026`, and BC+AI ecosystem. No holiday-card treatment, sponsors, venue, URL, whale, or badge/mandala layout.

## 14. December 8 - Mountain Healing Constellation

**For:** Luma event thumbnail, December narrative candidate B
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `DECEMBER 8, 2026`. Make December the long-view chapter: raven constellations, salmon memory, mountain snow, crystalline data points, frost-traced river and roots, and cedar lungs resolving into one healing system. Keep the central Healing Futures figure dominant: mountain head, calm face, cedar lungs, river/circulation, salmon, ravens, microscopes, DNA/data-light, crystals, civic science gatherings, coral/teal handmade poster style. The image should feel like the narrative has accumulated, not like a new winter poster. Add the official `BC+AI ecosystem` logo lockup from reference #3 as a small generated lower-corner field tag or notebook mark. Only readable text: `AI + LIFE SCIENCES`, `DECEMBER 8, 2026`, and BC+AI ecosystem. No sponsors, venue, URL, whale, generic hospital imagery, holiday card, or badge drift.

## 15. December 8 - Winter River Deep Time

**For:** Luma event thumbnail, December narrative candidate C
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for an AI + Life Sciences meetup on `DECEMBER 8, 2026`. Complete the ecology arc as winter river deep time: salmon passing through cold teal water, ravens carrying the last signal lights, cedar roots and mycelium under frost, warm field-lab circles, and the mountain-headed Healing Futures figure holding the whole system in her lungs and circulation. Use the July and Healing Futures references as strict continuity anchors: central mountain-headed woman, cedar lungs, river circulation, salmon, ravens, microscopes, DNA/data-light, crystal points, and small civic science gatherings. Include the official `BC+AI ecosystem` logo from reference #3 as a small generated lower-corner poster imprint, integrated into the illustration. Only readable text: `AI + LIFE SCIENCES`, `DECEMBER 8, 2026`, and BC+AI ecosystem. No extra words, sponsors, venue claims, URLs, whale, holiday card styling, or badge/mandala layout.

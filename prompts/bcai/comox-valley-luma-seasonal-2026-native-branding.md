# Comox Valley AI Seasonal Luma Graphics 2026 - Native Branding

Purpose: create a 12-image native-branding review batch for Comox Valley AI Luma square graphics. Each month has two candidates: one faithful "badge over cinematic Comox forest" version and one more progressive seasonal fusion. The series should feel like the established Comox Valley style: lush Pacific Northwest / Comox Valley atmosphere, central drippy sticker-badge energy, hand-inked eagle mark, moss, cedar, estuary, tidepool, and civic AI community signal.

Production rule: no overlays, compositing, or post-generation typography in this pass. All requested branding and date text must be generated natively into the artwork. Reject or rerun candidates with garbled `COMOX VALLEY AI`, malformed `BC+AI ecosystem`, fake venue text, fake sponsor marks, URLs, extra slogans, bad dates, or generic AI-conference stock imagery.

Reference key passed as globals:

- Reference #1: wide Comox Valley style anchor - `/Users/kk/Pictures/Photos Library.photoslibrary/originals/4/4825E103-3390-469E-A1D3-F5C3034A03AA.png`
- Reference #2: canonical drippy eagle badge - `/Users/kk/Desktop/Comox Valley AI Image Set/01-comox-valley-style-core/02-comox-valley-ai-eagle-redux-text-fix.png`
- Reference #3: compact Comox Valley AI logo reference - `/Users/kk/Desktop/Comox Valley AI Image Set/02-cv-ai-logos-canva/cv-ai-logo.jpeg`
- Reference #4: official BC+AI ecosystem logo - `/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png`

Run from Rafiki:

```bash
./.venv/bin/python generate.py \
  -f /Users/kk/Code/rafiki/prompts/bcai/comox-valley-luma-seasonal-2026-native-branding.md \
  -d /Users/kk/Code/rafiki/output/comox-valley-luma-seasonal-2026-openai \
  --model gpt-image-2 \
  --resolution 1K \
  --reference-role brand \
  --global-reference-images /Users/kk/Pictures/Photos\ Library.photoslibrary/originals/4/4825E103-3390-469E-A1D3-F5C3034A03AA.png,/Users/kk/Desktop/Comox\ Valley\ AI\ Image\ Set/01-comox-valley-style-core/02-comox-valley-ai-eagle-redux-text-fix.png,/Users/kk/Desktop/Comox\ Valley\ AI\ Image\ Set/02-cv-ai-logos-canva/cv-ai-logo.jpeg,/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png \
  --workers 2
```

```bash
./.venv/bin/python generate.py \
  -f /Users/kk/Code/rafiki/prompts/bcai/comox-valley-luma-seasonal-2026-native-branding.md \
  -d /Users/kk/Code/rafiki/output/comox-valley-luma-seasonal-2026-google-pro \
  --model pro \
  --resolution 1K \
  --reference-role brand \
  --global-reference-images /Users/kk/Pictures/Photos\ Library.photoslibrary/originals/4/4825E103-3390-469E-A1D3-F5C3034A03AA.png,/Users/kk/Desktop/Comox\ Valley\ AI\ Image\ Set/01-comox-valley-style-core/02-comox-valley-ai-eagle-redux-text-fix.png,/Users/kk/Desktop/Comox\ Valley\ AI\ Image\ Set/02-cv-ai-logos-canva/cv-ai-logo.jpeg,/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png \
  --workers 2
```

Global visual direction: make every candidate a square Luma thumbnail, not a flyer. Keep the central Comox Valley AI badge dominant and legible, with a black outer ring, white badge field, drippy hand-lettered `COMOX VALLEY AI`, bold `AI`, an eagle or eagle-like ink emblem, and organic Comox Valley plant/water details. Place a small generated `BC+AI ecosystem` mark in a lower corner as a field tag, maker's mark, notebook imprint, or sticker; it must stay secondary to Comox Valley AI. Only readable text allowed: `COMOX VALLEY AI`, `CV + AI COMMUNITY MEETUP`, the exact date, and `BC+AI ecosystem`.

## 1. July 8 - High Summer Cedar Badge

**For:** Luma square graphic, July faithful badge candidate
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for `CV + AI COMMUNITY MEETUP` on `JULY 8, 2026`. Use references #1 and #2 as strict style anchors: a cinematic Comox Valley old-growth forest, moss floor, cedar trunks, fern understory, warm high-summer light, and a large centered circular sticker badge. The badge should have a black outer ring, white field, drippy hand-lettered `COMOX VALLEY AI` around the top, bold `AI` in the center, and a hand-inked eagle emblem with small cosmic/data sparks. Add a small generated official `BC+AI ecosystem` mark from reference #4 as a lower-corner field tag, secondary and integrated. Keep the composition clean enough for Luma cropping. Only readable text: `COMOX VALLEY AI`, `CV + AI COMMUNITY MEETUP`, `JULY 8, 2026`, and `BC+AI ecosystem`. No venue, sponsor, URL, fake extra logos, city list, or generic tech conference imagery.

## 2. July 8 - Harbour Heat Signal

**For:** Luma square graphic, July progressive seasonal candidate
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for `CV + AI COMMUNITY MEETUP` on `JULY 8, 2026`. Keep the Comox Valley drippy eagle badge as the hero, but make July feel like a post-holiday restart: cedar shade opening toward warm Comox Harbour light, glassy water, eelgrass shimmer, salal leaves, and subtle cyan data-light moving from the shoreline into the badge. The circular badge remains centered and legible with `COMOX VALLEY AI`, bold `AI`, an inked eagle, and small punk-sticker drips. Add the official `BC+AI ecosystem` logo from reference #4 as a tiny generated maker's mark on a lower-corner sticker or field notebook. Only readable text: `COMOX VALLEY AI`, `CV + AI COMMUNITY MEETUP`, `JULY 8, 2026`, and `BC+AI ecosystem`. No other words, no venue, no sponsors, no URL, no fake calendar UI, no stock laptop crowd.

## 3. August 6 - Tidepool Badge

**For:** Luma square graphic, August faithful badge candidate
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for `CV + AI COMMUNITY MEETUP` on `AUGUST 6, 2026`. Preserve the reference Comox Valley style: cinematic Pacific Northwest realism behind a crisp central drippy sticker badge. Set the background at a late-summer Comox tidepool edge with sandstone, kelp, eelgrass, sea foam, blackberry and salal along the shore, golden sea haze, and cedar forest rising behind it. Center a circular `COMOX VALLEY AI` badge with black border, white field, hand-drawn eagle, bold `AI`, ink splatter, and subtle cyan data-sparks. Include a small generated official `BC+AI ecosystem` lower-corner mark from reference #4. Only readable text: `COMOX VALLEY AI`, `CV + AI COMMUNITY MEETUP`, `AUGUST 6, 2026`, and `BC+AI ecosystem`. No venue, fake sponsors, URL, extra taglines, or generic AI icons.

## 4. August 6 - Eelgrass Data Current

**For:** Luma square graphic, August progressive seasonal candidate
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for `CV + AI COMMUNITY MEETUP` on `AUGUST 6, 2026`. Build a progressive Comox Valley style image: the central drippy eagle badge is partly nested into a tidepool ecology system, with eelgrass strands, kelp ribbons, sea foam cells, blackberry canes, salal leaves, and tiny cyan data currents flowing like bioluminescence through shallow water. Keep the badge readable and badge-first: `COMOX VALLEY AI` in drippy hand lettering, bold `AI`, black ring, white field, eagle inkwork. Add the official `BC+AI ecosystem` mark from reference #4 as a small generated corner field tag. Only readable text: `COMOX VALLEY AI`, `CV + AI COMMUNITY MEETUP`, `AUGUST 6, 2026`, and `BC+AI ecosystem`. No extra words, no venue, no sponsor, no URL, no fake interface overlay.

## 5. September 3 - First Rain Estuary Badge

**For:** Luma square graphic, September faithful badge candidate
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for `CV + AI COMMUNITY MEETUP` on `SEPTEMBER 3, 2026`. Stay close to references #1 and #2: a photoreal-cinematic Comox Valley landscape with the large circular drippy eagle badge centered over it. Make September about first rain and the estuary: soft rain on cedar boughs, Komoks estuary water, eelgrass, early fall green-gold light, salmon beginning to move through the river mouth. The badge must read as `COMOX VALLEY AI`, with bold `AI`, a hand-inked eagle, black outer ring, white center, ink splatter, and slight sticker texture. Add a small generated official `BC+AI ecosystem` lower-corner mark from reference #4. Only readable text: `COMOX VALLEY AI`, `CV + AI COMMUNITY MEETUP`, `SEPTEMBER 3, 2026`, and `BC+AI ecosystem`. No venue, sponsor, URL, fake extra copy, or generic tech imagery.

## 6. September 3 - Salmon Return Signal

**For:** Luma square graphic, September progressive seasonal candidate
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for `CV + AI COMMUNITY MEETUP` on `SEPTEMBER 3, 2026`. Make a more progressive seasonal fusion of the Comox Valley style: the circular drippy eagle badge floats above a rain-bright estuary, while salmon, eelgrass, cedar roots, and cyan data-light form a living signal network that flows into the eagle emblem. Keep the badge graphic crisp and readable: `COMOX VALLEY AI`, bold `AI`, black ring, white badge field, punk sticker drips, ink texture. Use early fall green-gold, rain silver, salmon coral, cedar green, and small cosmic sparks. Add the official `BC+AI ecosystem` logo from reference #4 as a tiny generated field tag in the lower corner. Only readable text: `COMOX VALLEY AI`, `CV + AI COMMUNITY MEETUP`, `SEPTEMBER 3, 2026`, and `BC+AI ecosystem`. No other words, no fake sponsor marks, no URL, no venue.

## 7. October 1 - Mycelium Cedar Badge

**For:** Luma square graphic, October faithful badge candidate
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for `CV + AI COMMUNITY MEETUP` on `OCTOBER 1, 2026`. Preserve the established Comox Valley composition: cinematic wet cedar forest background, mossy old-growth floor, and a large centered circular drippy sticker badge. Make October about mycelium and storm season: mushrooms, wet cedar bark, copper leaves, lichen, rain-dark moss, and faint cyan network lines under the forest floor. The badge should be high contrast and legible with `COMOX VALLEY AI`, bold `AI`, hand-inked eagle, black border, white field, ink splatter, and punk sticker drips. Add a small generated official `BC+AI ecosystem` logo from reference #4 as a lower-corner maker's mark. Only readable text: `COMOX VALLEY AI`, `CV + AI COMMUNITY MEETUP`, `OCTOBER 1, 2026`, and `BC+AI ecosystem`. No venue, sponsors, URL, fake extra words, or generic AI imagery.

## 8. October 1 - Fungal Network Badge

**For:** Luma square graphic, October progressive seasonal candidate
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for `CV + AI COMMUNITY MEETUP` on `OCTOBER 1, 2026`. Make a progressive Comox Valley style image where the central drippy eagle badge is interwoven with a living rainforest network: glowing mycelium threads, mushroom caps, cedar roots, wet bark texture, lichen maps, storm rain, and cyan data-signal lines connecting the forest floor to the eagle emblem. Keep the badge dominant and readable: `COMOX VALLEY AI`, bold `AI`, black ring, white field, inked eagle, subtle drips, hand-made sticker texture. Add the official `BC+AI ecosystem` mark from reference #4 as a small generated lower-corner field tag. Only readable text: `COMOX VALLEY AI`, `CV + AI COMMUNITY MEETUP`, `OCTOBER 1, 2026`, and `BC+AI ecosystem`. No extra labels, fake venue, sponsor, URL, or corporate AI interface.

## 9. November 5 - Rain Shelter Badge

**For:** Luma square graphic, November faithful badge candidate
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for `CV + AI COMMUNITY MEETUP` on `NOVEMBER 5, 2026`. Stay faithful to the Comox Valley style: a cinematic rain-soaked cedar forest and moss floor, with a crisp central circular drippy eagle badge like a punk community sticker. November mood: cedar shelter, rain lines, mist, dark wet bark, warm lantern glow, tiny community field-station hints in the background without faces becoming the subject. Badge text must be legible: `COMOX VALLEY AI`, bold `AI`, eagle inkwork, black ring, white field, ink splatter. Add a small generated official `BC+AI ecosystem` mark from reference #4 in the lower corner as a waterproof field label. Only readable text: `COMOX VALLEY AI`, `CV + AI COMMUNITY MEETUP`, `NOVEMBER 5, 2026`, and `BC+AI ecosystem`. No venue, sponsor, URL, fake extra text, or generic conference crowd.

## 10. November 5 - Lantern Field Station

**For:** Luma square graphic, November progressive seasonal candidate
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for `CV + AI COMMUNITY MEETUP` on `NOVEMBER 5, 2026`. Build a progressive seasonal fusion in the Comox Valley style: the central drippy eagle badge sits inside a rain-dark cedar field-station scene, with warm lantern circles, wet notebooks, tiny microscopes, cedar boughs, mist, puddle reflections, and cyan data-light running through roots and rainwater. Keep the badge graphic clean and readable: `COMOX VALLEY AI`, bold `AI`, black ring, white field, hand-inked eagle, ink splatter, sticker drips. Add the official `BC+AI ecosystem` logo from reference #4 as a small generated lower-corner notebook imprint. Only readable text: `COMOX VALLEY AI`, `CV + AI COMMUNITY MEETUP`, `NOVEMBER 5, 2026`, and `BC+AI ecosystem`. No extra words, no venue, no sponsor, no URL, no generic tech expo stage.

## 11. December 3 - Glacier Frost Badge

**For:** Luma square graphic, December faithful badge candidate
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for `CV + AI COMMUNITY MEETUP` on `DECEMBER 3, 2026`. Preserve the reference composition: photoreal-cinematic Comox Valley old-growth scene, a large centered circular drippy eagle badge, black ring, white field, bold `AI`, and hand-lettered `COMOX VALLEY AI`. Make December seasonal without becoming a holiday card: frost on cedar needles, moss under cold mist, distant Comox Glacier light, evergreen density, subtle winter blue data-glow, warm community signal from inside the badge. Add the official `BC+AI ecosystem` mark from reference #4 as a small generated lower-corner field tag. Only readable text: `COMOX VALLEY AI`, `CV + AI COMMUNITY MEETUP`, `DECEMBER 3, 2026`, and `BC+AI ecosystem`. No venue, sponsor, URL, fake extra logos, holiday greetings, or generic AI conference visuals.

## 12. December 3 - Winter Data-Glow Commons

**For:** Luma square graphic, December progressive seasonal candidate
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Luma event thumbnail for `CV + AI COMMUNITY MEETUP` on `DECEMBER 3, 2026`. Make a progressive winter version of the Comox Valley style: the central drippy eagle badge is surrounded by frost crystals, cedar silhouettes, distant Comox Glacier geometry, moss, evergreen boughs, and soft cyan data-glow that feels like winter light moving through the forest. Keep it grounded and local, not sci-fi: tactile bark, wet moss, cold mist, warm human-community glow inside the badge. The badge must remain readable with `COMOX VALLEY AI`, bold `AI`, black ring, white field, inked eagle, sticker drips. Add the official `BC+AI ecosystem` logo from reference #4 as a tiny generated corner mark. Only readable text: `COMOX VALLEY AI`, `CV + AI COMMUNITY MEETUP`, `DECEMBER 3, 2026`, and `BC+AI ecosystem`. No extra words, no venue, no sponsor, no URL, no holiday-card treatment.

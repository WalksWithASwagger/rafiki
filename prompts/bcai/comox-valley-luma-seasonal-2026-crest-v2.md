# Comox Valley AI Seasonal Crest 2026 - v2

Purpose: create a 12-image native-generation review batch for Comox Valley AI seasonal Luma squares. This v2 corrects the previous native-branding batch, which technically used native generation but invited poster-style lower-third typography. This pass is crest-first: the crest, badge, patch, or heraldic sticker is the complete artifact.

Production rule: no overlays, no compositing, no post-generation typography, and no separate flyer layout. All text must be native to the generated crest itself. Reject or rerun any candidate with lower-third typography, detached logo boxes, corner labels, big event-title blocks, fake UI, extra readable text, malformed crest text, or a date outside the crest.

Reference key passed as globals:

- Reference #1: canonical drippy eagle badge - `/Users/kk/Desktop/Comox Valley AI Image Set/01-comox-valley-style-core/02-comox-valley-ai-eagle-redux-text-fix.png`
- Reference #2: island chapter badge structure - `/Users/kk/Desktop/Comox Valley AI Image Set/01-comox-valley-style-core/05-comox-valley-ai-island-chapter-badge-a.png`
- Reference #3: old-growth eagle crest texture - `/Users/kk/Desktop/Comox Valley AI Image Set/01-comox-valley-style-core/09-comox-valley-ai-eagle-and-old-growth.png`
- Reference #4: official BC+AI ecosystem mark for tiny native maker-mark treatment only - `/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png`

Run from Rafiki:

```bash
./.venv/bin/python generate.py \
  -f /Users/kk/Code/rafiki/prompts/bcai/comox-valley-luma-seasonal-2026-crest-v2.md \
  -d /Users/kk/Code/rafiki/output/comox-valley-luma-seasonal-2026-crest-v2-openai \
  --model gpt-image-2 \
  --resolution 1K \
  --style none \
  --reference-role brand \
  --global-reference-images /Users/kk/Desktop/Comox\ Valley\ AI\ Image\ Set/01-comox-valley-style-core/02-comox-valley-ai-eagle-redux-text-fix.png,/Users/kk/Desktop/Comox\ Valley\ AI\ Image\ Set/01-comox-valley-style-core/05-comox-valley-ai-island-chapter-badge-a.png,/Users/kk/Desktop/Comox\ Valley\ AI\ Image\ Set/01-comox-valley-style-core/09-comox-valley-ai-eagle-and-old-growth.png,/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png \
  --workers 1
```

```bash
./.venv/bin/python generate.py \
  -f /Users/kk/Code/rafiki/prompts/bcai/comox-valley-luma-seasonal-2026-crest-v2.md \
  -d /Users/kk/Code/rafiki/output/comox-valley-luma-seasonal-2026-crest-v2-google-pro \
  --model pro \
  --resolution 1K \
  --style none \
  --reference-role brand \
  --global-reference-images /Users/kk/Desktop/Comox\ Valley\ AI\ Image\ Set/01-comox-valley-style-core/02-comox-valley-ai-eagle-redux-text-fix.png,/Users/kk/Desktop/Comox\ Valley\ AI\ Image\ Set/01-comox-valley-style-core/05-comox-valley-ai-island-chapter-badge-a.png,/Users/kk/Desktop/Comox\ Valley\ AI\ Image\ Set/01-comox-valley-style-core/09-comox-valley-ai-eagle-and-old-growth.png,/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png \
  --workers 1
```

Global visual direction: create one square crest/emblem/patch per prompt. The crest fills most of the square and is the whole design, not a badge placed on a poster. Keep `COMOX VALLEY AI` as curved or wrapped crest lettering, preserve a bold central `AI`, and place the date only on a small internal ribbon or rim segment. A tiny native `BC+AI ecosystem` maker mark may appear only if it is embedded into the rim, ribbon end, seal notch, or inner maker stamp; omit it rather than making a detached corner label. No text outside the crest. No `CV + AI COMMUNITY MEETUP`.

## 1. July 8 - Classic Cedar Harbour Crest

**For:** Luma square crest, July classic round eagle variant
**Aspect Ratio:** 1:1

**Prompt:**
> Generate a square native crest emblem for Comox Valley AI, not a poster. The whole image is one classic round drippy eagle badge filling most of the square, close to references #1 and #2: black outer ring, cream-white badge field, hand-inked eagle, bold central `AI`, curved drippy crest lettering `COMOX VALLEY AI`. July seasonality is built inside the crest only: cedar shade, warm Comox Harbour gold, salal, moss, and subtle summer cyan data sparks in the eagle field. Add a small integrated ribbon inside the lower crest reading `JULY 8, 2026`. If possible, embed a tiny native `BC+AI ecosystem` maker mark into the ribbon end or inner rim; omit it if it cannot stay integrated. No text outside the crest, no lower-third typography, no corner logo, no flyer layout, no detached labels, no `CV + AI COMMUNITY MEETUP`.

## 2. July 8 - Harbour Restart Heraldic Patch

**For:** Luma square crest, July seasonal system variant
**Aspect Ratio:** 1:1

**Prompt:**
> Generate a square heraldic sticker-patch crest for Comox Valley AI. The image is a single integrated emblem, centered and large, with a slightly irregular punk-sticker edge and no separate background poster. Keep the reference eagle-badge language: drippy `COMOX VALLEY AI` lettering around the rim, bold `AI`, black ink eagle, cream field, old-growth texture. Make July feel like a high-summer restart by replacing the wreath with cedar tips, harbour ripples, salal leaves, and small gold sun flecks woven into the rim. Add one internal date ribbon reading `JULY 8, 2026`. Tiny `BC+AI ecosystem` may be stamped into the crest rim only, never as a corner box. No text outside the crest, no big title block, no event flyer typography, no fake UI.

## 3. August 6 - Tidepool Round Crest

**For:** Luma square crest, August classic round eagle variant
**Aspect Ratio:** 1:1

**Prompt:**
> Generate a square native crest emblem for Comox Valley AI, one round badge filling most of the square. Follow references #1 and #2 for structure: black outer ring, cream center, drippy curved `COMOX VALLEY AI`, bold `AI`, hand-drawn eagle, ink splatter, sticker texture. August seasonality must be inside the crest design: tidepool sandstone, kelp ribbons, eelgrass, sea foam bubbles, blackberry and salal woven into the wreath. Add a small internal ribbon reading `AUGUST 6, 2026`. A tiny `BC+AI ecosystem` maker mark may be integrated into a ribbon end or rim stamp only. No lower thirds, no detached corner logo, no separate typography, no poster background, no `CV + AI COMMUNITY MEETUP`.

## 4. August 6 - Kelp And Eelgrass Shield

**For:** Luma square crest, August seasonal system variant
**Aspect Ratio:** 1:1

**Prompt:**
> Generate a square Comox Valley AI crest as a single shield-and-roundel hybrid patch, not a poster. The emblem should feel hand-inked, coastal, drippy, and print-sticker ready. Use `COMOX VALLEY AI` as native crest lettering wrapped along the top rim, bold `AI` in the inner field, and an eagle silhouette diving through an eelgrass current. Build the August theme into the crest: kelp, tidepool foam, barnacle dots, blackberry canes, salal leaves, and cyan bioluminescent data lines in the border. Include one small built-in date ribbon reading `AUGUST 6, 2026`. Tiny `BC+AI ecosystem` only as an integrated seal notch or rim stamp. No external text, no logo box, no flyer layout, no lower-third event title.

## 5. September 3 - Estuary Rain Crest

**For:** Luma square crest, September classic round eagle variant
**Aspect Ratio:** 1:1

**Prompt:**
> Generate a square native crest emblem for Comox Valley AI. The whole image is one centered round drippy eagle badge, close to references #1 and #3. Keep `COMOX VALLEY AI` curved around the crest, bold `AI` in the center, black ink eagle, cream badge field, and old-growth sticker texture. September seasonality appears only in crest elements: first rain, Komoks estuary eelgrass, salmon returning through the inner field, early fall green-gold leaves, and silver rain marks in the rim. Add a small internal ribbon reading `SEPTEMBER 3, 2026`. Tiny native `BC+AI ecosystem` may be embedded in the rim or ribbon end only. No words outside the crest, no corner label, no big typography block, no poster layout, no `CV + AI COMMUNITY MEETUP`.

## 6. September 3 - Salmon Return Seal

**For:** Luma square crest, September seasonal system variant
**Aspect Ratio:** 1:1

**Prompt:**
> Generate a square seasonal seal for Comox Valley AI, fully native and crest-first. Make the badge a living estuary crest: eagle wings, salmon, eelgrass, cedar roots, rain rings, and cyan data-light all woven into one circular emblem. Use drippy hand-lettered `COMOX VALLEY AI` as rim lettering and keep bold `AI` in the inner field. The date appears only on a small integrated banner across the lower inner crest: `SEPTEMBER 3, 2026`. A tiny `BC+AI ecosystem` maker mark may be pressed into the crest rim if it stays subtle and native. No lower-third title, no detached logo, no external type, no flyer scene, no separate background poster.

## 7. October 1 - Mycelium Cedar Crest

**For:** Luma square crest, October classic round eagle variant
**Aspect Ratio:** 1:1

**Prompt:**
> Generate a square native crest emblem for Comox Valley AI. The design is one round drippy eagle badge filling most of the square, with no poster typography. Follow the reference badge system: black outer ring, cream field, curved `COMOX VALLEY AI`, bold `AI`, hand-inked eagle, organic ink splatter and sticker edge. October seasonality is integrated into the crest rim and wreath: wet cedar bark, lichen, mushrooms, copper leaves, mycelium threads, rain-dark moss, and small cyan signal nodes. Add a small internal ribbon reading `OCTOBER 1, 2026`. Tiny `BC+AI ecosystem` may be integrated into the ribbon end or rim only. No text outside crest, no corner box, no flyer layout, no `CV + AI COMMUNITY MEETUP`.

## 8. October 1 - Fungal Network Heraldry

**For:** Luma square crest, October seasonal system variant
**Aspect Ratio:** 1:1

**Prompt:**
> Generate a square Comox Valley AI heraldic crest as one complete emblem. Make the seasonal system more experimental while staying badge-first: an eagle nested in a circular mycelium network, mushroom caps replacing laurel leaves, lichen-map textures in the rim, wet cedar bark as the outer border, and cyan data threads feeding into the bold central `AI`. Use native drippy `COMOX VALLEY AI` rim lettering. Include only one internal date ribbon: `OCTOBER 1, 2026`. Tiny `BC+AI ecosystem` may appear as an integrated maker stamp inside the crest rim. No detached text, no lower third, no logo box, no poster scene, no extra slogans.

## 9. November 5 - Rain Shelter Crest

**For:** Luma square crest, November classic round eagle variant
**Aspect Ratio:** 1:1

**Prompt:**
> Generate a square native crest emblem for Comox Valley AI, one round badge filling the square. Keep the classic drippy eagle crest structure from references #1 and #2: black ring, cream center, hand-inked eagle, bold `AI`, curved `COMOX VALLEY AI`, ink splatter, sticker texture. November seasonality is built into the crest only: rain lines, cedar shelter boughs, dark wet bark, lantern glow, mist, and small field-station details as tiny symbolic marks in the wreath, not as a scene. Add a small internal ribbon reading `NOVEMBER 5, 2026`. Tiny native `BC+AI ecosystem` may be integrated into the ribbon end or inner rim. No words outside the crest, no lower-third title, no detached logo, no flyer layout.

## 10. November 5 - Lantern Field Station Seal

**For:** Luma square crest, November seasonal system variant
**Aspect Ratio:** 1:1

**Prompt:**
> Generate a square seasonal field-station seal for Comox Valley AI. The whole image is one emblem/patch, not a poster. Combine the drippy eagle badge language with November cedar rain: a lantern-warm inner field, eagle wings sheltering the bold `AI`, cedar bough rim, rain beads, wet notebook texture, small microscope glyphs hidden as non-readable ornament, and cyan data-light through roots. Use native `COMOX VALLEY AI` lettering around the crest. Add a small integrated date ribbon reading `NOVEMBER 5, 2026`. Tiny `BC+AI ecosystem` may be stamped into the rim only. No separate text block, no corner label, no lower thirds, no fake UI, no event title.

## 11. December 3 - Glacier Frost Crest

**For:** Luma square crest, December classic round eagle variant
**Aspect Ratio:** 1:1

**Prompt:**
> Generate a square native crest emblem for Comox Valley AI. The image is one classic round drippy eagle badge, close to references #1 and #3, filling most of the square. Preserve native curved `COMOX VALLEY AI`, bold central `AI`, black ink eagle, cream badge field, black ring, and sticker texture. December seasonality belongs inside the crest: frost on cedar, evergreen needles, distant Comox Glacier geometry in the inner field, cold mist, winter blue data-glow, and a few warm gold community sparks. Add one small internal date ribbon reading `DECEMBER 3, 2026`. Tiny `BC+AI ecosystem` may be embedded into the rim or ribbon end only. No holiday greeting, no text outside crest, no lower third, no logo box, no poster layout.

## 12. December 3 - Winter Data-Glow Patch

**For:** Luma square crest, December seasonal system variant
**Aspect Ratio:** 1:1

**Prompt:**
> Generate a square winter heraldic patch for Comox Valley AI as one complete native crest. Keep it grounded, tactile, and local: frosted cedar rim, Comox Glacier facets, evergreen boughs, moss texture, cold mist, and soft cyan data-glow woven through the eagle and bold central `AI`. Use drippy hand-lettered `COMOX VALLEY AI` as crest lettering, not a separate title. Add a small integrated date ribbon reading `DECEMBER 3, 2026`. If included, `BC+AI ecosystem` must be a tiny native maker stamp in the rim or ribbon, never a detached logo. No extra words, no event title, no lower-third typography, no poster background, no corner mark.

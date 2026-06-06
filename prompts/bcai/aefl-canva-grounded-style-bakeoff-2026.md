# AI Ethical Futures Lab - Canva-Grounded Style Bakeoff 2026

Purpose: create a new 10-direction Rafiki style bakeoff for AI Ethical Futures Lab, grounded in the Canva reference file Kris assembled from earlier AEFL work. This is a style lock pass, not the final dated July-December cover series.

Reference rule: use the Canva reference board for typography, hierarchy, color energy, polish, and overall vibe only. Do not copy exact page elements, layouts, background images, or decorative shapes. Use the official BC+AI logo reference for the requested `BC+AI ecosystem` mark.

Production rule: no overlays, compositing, or post-generation typography. All poster text and the BC+AI ecosystem logo must be generated natively into the artwork. Reject or rerun candidates with malformed AEFL text, malformed BC+AI logo, copied Canva elements, fake sponsor marks, fake venue claims, fake dates, fake URLs, dirty texture, fake cultural motifs, campfire/canoe symbolism, circuit boards, PCB traces, dense dot-and-line networks, generic AI stock, robots, dashboards, or cluttered tech-interface graphics.

Required readable text in every candidate:

- `the bc + ai ecosystem association invites you to join our`
- `AI ETHICAL FUTURES LAB`
- `BC+AI ecosystem`
- `multi-modal, multi-cultural, radically local, and future-facing.`

Reference key passed as globals:

- Canva AEFL reference board - `/Users/kk/Code/rafiki/prompts/bcai/reference/aefl-canva-grounded-style-bakeoff-2026/aefl-canva-reference-board.png`
- Official BC+AI ecosystem logo - `/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png`

Run OpenAI / Image Gen 2 from Rafiki:

```bash
REFS="/Users/kk/Code/rafiki/prompts/bcai/reference/aefl-canva-grounded-style-bakeoff-2026/aefl-canva-reference-board.png,/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png"
./.venv/bin/python generate.py \
  -f /Users/kk/Code/rafiki/prompts/bcai/aefl-canva-grounded-style-bakeoff-2026.md \
  -d /Users/kk/Code/rafiki/output/aefl-canva-grounded-style-bakeoff-2026 \
  --model gpt-image-2 \
  --quality high \
  --aspect-ratio 1:1 \
  --style bcai-ecosystem \
  --reference-role brand \
  --global-reference-images "$REFS" \
  --workers 1
```

Run Gemini Pro / "Nano Pro" from Rafiki:

```bash
REFS="/Users/kk/Code/rafiki/prompts/bcai/reference/aefl-canva-grounded-style-bakeoff-2026/aefl-canva-reference-board.png,/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png"
./.venv/bin/python generate.py \
  -f /Users/kk/Code/rafiki/prompts/bcai/aefl-canva-grounded-style-bakeoff-2026.md \
  -d /Users/kk/Code/rafiki/output/aefl-canva-grounded-style-bakeoff-2026 \
  --model pro \
  --resolution 1K \
  --aspect-ratio 1:1 \
  --style bcai-ecosystem \
  --reference-role brand \
  --global-reference-images "$REFS" \
  --workers 2
```

Global visual direction: square AEFL poster art with crisp, clean, luminous editorial typography. Strong protected title zone, small invitation line, integrated BC+AI ecosystem mark, and acid-lime bottom tagline. The look should be Futureproof-adjacent through color and energy, but not mythic or folkloric: deep black-green, violet, coral, teal, mint, acid lime, polished gradients, sharp poster hierarchy, premium print finish, and new abstract visual fields. Keep backgrounds beautiful and restrained enough for Luma covers.

## 1. Luminous Type Field

**For:** AEFL Canva-grounded bakeoff, luminous type field
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square AI Ethical Futures Lab poster using the Canva reference board only for typography hierarchy, spacing, color energy, and polished vibe. Make a new original luminous type field: deep black-green and violet ground, coral glow behind the main title, subtle teal edge light, premium matte finish, and generous negative space. The large title should dominate with crisp editorial sans-serif confidence. Generate only these readable words: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` Integrate the official BC+AI ecosystem mark from the logo reference as a native lower poster element. Do not copy exact Canva elements. No dates, no venue, no sponsors, no URLs, no circuit boards, no dense node maps, no dirty texture, no campfire, no canoe, no fake cultural motifs.

## 2. Clean Coral Masthead

**For:** AEFL Canva-grounded bakeoff, clean coral masthead
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square AEFL poster with a crisp coral masthead system. Use the Canva reference board for the feeling of strong stacked typography and confident spacing, but create a new composition. Deep teal-black background, broad violet and mint light bands, coral headline glow, high contrast, clean lower logo zone, and acid-lime tagline. Required text only: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` The BC+AI ecosystem mark should match the supplied logo reference as faithfully as native generation allows. No copied Canva graphics, no extra readable words, no fake event details, no circuits, no clutter, no symbolic wilderness scenes.

## 3. Editorial Aurora Plane

**For:** AEFL Canva-grounded bakeoff, editorial aurora plane
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square AI Ethical Futures Lab poster as a clean editorial aurora plane, not a landscape scene. Use a deep black-green field with a few broad luminous sweeps of teal, violet, coral, and acid lime. Let the typography carry the poster: huge clean `AI ETHICAL FUTURES LAB`, small invitation line at the top, official `BC+AI ecosystem` mark integrated low, tagline along the bottom. Use the Canva reference board only for typographic confidence, spacing, and vibe; do not copy any exact elements. Only the four required text elements may be readable. No road, canoe, fire, forest ritual, circuit board, dashboard, robot, fake sponsor, fake venue, or URL.

## 4. Futureproof-Adjacent Badge Poster

**For:** AEFL Canva-grounded bakeoff, Futureproof-adjacent badge poster
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square AEFL poster that feels like a polished Futureproof-adjacent badge poster without copying previous badges. Use a new abstract circular field or soft geometric badge behind the title, with clean edges, luminous violet-teal depth, coral headline, and acid-lime accent. Typography should feel like the Canva reference: bold, crisp, intentional, and readable. Required text only: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` The BC+AI ecosystem mark must be native and based on the supplied logo reference. No extra labels, no dates, no venue, no sponsors, no copied Canva shapes, no folk motifs, no circuits, no dense dots and lines.

## 5. Civic Light Room Abstract

**For:** AEFL Canva-grounded bakeoff, civic light room abstract
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square AI Ethical Futures Lab poster that suggests a practical civic working room through abstract light only, not literal people or laptops. Use broad dark planes, a warm coral center glow, teal wall-light, violet shadow, and clean poster grain. The title and logo hierarchy should follow the Canva reference vibe: confident type, strong breathing room, polished social-poster finish. Generate only: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` Use the official BC+AI logo reference for the mark. No screens, no desks, no venue, no fake text, no copied Canva elements, no dirty grunge, no circuits, no dense data maps.

## 6. Minimal Signal Glow

**For:** AEFL Canva-grounded bakeoff, minimal signal glow
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square AEFL poster with a minimal signal glow: one or two soft luminous points, broad black-violet depth, a clean coral title zone, teal and acid-lime accents, and premium editorial polish. It should feel smart and future-facing without looking like generic AI. Use the Canva reference board for typography, layout discipline, and color vibe only. Required generated text only: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` Integrate the official BC+AI ecosystem mark natively. No node web, no circuit traces, no PCB, no fake sponsors, no venue, no dates, no URLs, no robots, no stock AI icons.

## 7. Policy Prism

**For:** AEFL Canva-grounded bakeoff, policy prism
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square AI Ethical Futures Lab poster built around a clean policy prism: abstract transparent planes of teal, violet, coral, and mint light crossing a dark field. The composition should be elegant, crisp, and graphic, with a large readable title and stable lower logo/tagline zone. Use the Canva reference board only for typography hierarchy and overall vibe. Generate only the four required readable text elements: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` Preserve the BC+AI logo reference as a native generated mark. No copied Canva art, no fake claims, no labels on the prism, no circuits, no dashboards, no dirty texture.

## 8. Public Trust Gradient

**For:** AEFL Canva-grounded bakeoff, public trust gradient
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square AEFL poster with a clean public-trust gradient: black-green base, smooth teal-to-violet depth, coral title glow, acid-lime bottom line, and one quiet abstract civic shape in the center. It should feel like a premium community event graphic, not a tech conference template. Use the Canva reference board for type scale, spacing, and vibe only. Required text only: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` Use the supplied BC+AI logo as the mark reference. No dates, no venue, no sponsors, no copied elements, no faux cultural iconography, no campfires, no canoes, no circuits, no dense visual noise.

## 9. Series System Prototype

**For:** AEFL Canva-grounded bakeoff, series system prototype
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square poster prototype for the year-round AI Ethical Futures Lab series. Make it reusable: protected top invitation line, huge clean title, new abstract center field, official BC+AI ecosystem mark, and stable bottom tagline. The visual language should echo the Canva reference board's typography and polish without copying exact elements. Use deep violet-black, teal, coral, mint, and acid lime in a crisp editorial system. Generate only: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` No dates yet, no sponsor or venue claims, no URLs, no circuits, no clutter, no literal scenes.

## 10. Clean Civic Threshold

**For:** AEFL Canva-grounded bakeoff, clean civic threshold
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square AI Ethical Futures Lab poster with a clean civic threshold: an abstract luminous opening or edge of light made from simple geometric color fields, not a doorway scene. Use polished black-green, violet, coral, teal, and acid-lime color. Typography should be crisp, strong, and Canva-reference-adjacent, with the main title as the hero. Generate only the required text: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` The BC+AI ecosystem mark should follow the supplied official logo reference. No copied Canva elements, no roads, no canoes, no campfires, no fake cultural symbols, no circuits, no dense dots, no extra text.

# AI Ethical Futures Lab - Futureproof Brand Bakeoff 2026

Purpose: create a 10-direction Rafiki style bakeoff for AI Ethical Futures Lab graphics inside the Futureproof + BC+AI visual system. This is a style lock pass, not the final dated July-December production series.

Production rule: no overlays, compositing, or post-generation typography for this pass. All poster text and the BC+AI ecosystem logo must be generated natively into the artwork. Reject or rerun candidates with malformed AEFL text, malformed BC+AI mark, fake sponsor marks, fake venue claims, fake URLs, extra readable words, generic AI stock, sterile SaaS gradients, or a composition that does not feel like the supplied Futureproof/BC+AI poster samples.

Required readable text in every candidate:

- `the bc + ai ecosystem association invites you to join our`
- `AI ETHICAL FUTURES LAB`
- `BC+AI ecosystem`
- `multi-modal, multi-cultural, radically local, and future-facing.`

Reference key passed as globals:

- Reference #1: overgrown civic lab wall / mint title - `/Users/kk/Desktop/Screenshot 2026-06-04 at 13.42.27.png`
- Reference #2: lake/council dream / coral title - `/Users/kk/Desktop/Screenshot 2026-06-04 at 13.42.36.png`
- Reference #3: radial road portal / teal-magenta tunnel - `/Users/kk/Desktop/Screenshot 2026-06-04 at 13.42.43.png`
- Reference #4: signal-field network / purple-coral nodes - `/Users/kk/Desktop/Screenshot 2026-06-04 at 13.42.58.png`
- Reference #5: official BC+AI ecosystem logo - `/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png`
- Reference #6: Futureproof + BC+AI logo reference board - `/Users/kk/Code/rafiki/prompts/futureproof/reference/futureproof-bcai-logo-reference-board.png`

Run OpenAI / Image Gen 2 from Rafiki:

```bash
REFS="/Users/kk/Desktop/Screenshot 2026-06-04 at 13.42.27.png,/Users/kk/Desktop/Screenshot 2026-06-04 at 13.42.36.png,/Users/kk/Desktop/Screenshot 2026-06-04 at 13.42.43.png,/Users/kk/Desktop/Screenshot 2026-06-04 at 13.42.58.png,/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png,/Users/kk/Code/rafiki/prompts/futureproof/reference/futureproof-bcai-logo-reference-board.png"
./.venv/bin/python generate.py \
  -f /Users/kk/Code/rafiki/prompts/bcai/aefl-futureproof-brand-bakeoff-2026.md \
  -d /Users/kk/Code/rafiki/output/aefl-futureproof-brand-bakeoff-2026 \
  --model gpt-image-2 \
  --quality high \
  --aspect-ratio 1:1 \
  --style futureproof-mythic+bcai-ecosystem \
  --reference-role brand \
  --global-reference-images "$REFS" \
  --workers 1
```

Run Gemini Pro / "Nano Pro" from Rafiki:

```bash
REFS="/Users/kk/Desktop/Screenshot 2026-06-04 at 13.42.27.png,/Users/kk/Desktop/Screenshot 2026-06-04 at 13.42.36.png,/Users/kk/Desktop/Screenshot 2026-06-04 at 13.42.43.png,/Users/kk/Desktop/Screenshot 2026-06-04 at 13.42.58.png,/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png,/Users/kk/Code/rafiki/prompts/futureproof/reference/futureproof-bcai-logo-reference-board.png"
./.venv/bin/python generate.py \
  -f /Users/kk/Code/rafiki/prompts/bcai/aefl-futureproof-brand-bakeoff-2026.md \
  -d /Users/kk/Code/rafiki/output/aefl-futureproof-brand-bakeoff-2026 \
  --model pro \
  --resolution 1K \
  --aspect-ratio 1:1 \
  --style futureproof-mythic+bcai-ecosystem \
  --reference-role brand \
  --global-reference-images "$REFS" \
  --workers 2
```

Global visual direction: square Futureproof x BC+AI poster art. Large glowing AEFL title, small invitation line at top, official BC+AI ecosystem lockup integrated as a lower field mark, acid-lime tagline along the bottom, deep forest/teal/purple fields, coral or mint title glow, hand-made poster grain, luminous nodes, civic policy lab symbolism, BC place, and enough clean hierarchy to work as a Luma cover. The family should feel radically local, policy-lab serious, and mythic without becoming fantasy or generic AI.

## 1. Signal-Field Network

**For:** AEFL Futureproof brand bakeoff, signal-field network direction
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Futureproof x BC+AI poster for AI Ethical Futures Lab. Use the supplied signal-field reference as the main anchor: deep purple night field, glowing coral-orange nodes, violet connection lines, faint civic-map contours, analog grain, and one strong luminous center. Layout like a public-interest signal map: the title is large, glowing coral, and left-weighted; the official `BC+AI ecosystem` lockup is small and clean in the lower right. Bake in only these readable words: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` Preserve the BC+AI logo from the reference as a generated brand mark, not a fake alternate. No other text, no dates, no sponsors, no venue, no URLs, no robots, no generic AI icons.

## 2. Radial Road Portal

**For:** AEFL Futureproof brand bakeoff, radial road/portal direction
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Futureproof x BC+AI poster for AI Ethical Futures Lab. Use the radial road portal sample as the main anchor: a dark BC forest road disappearing into a magenta and teal circular light tunnel, hand-made long-exposure texture, black tree silhouettes, and a precise poster frame. Keep the title huge and glowing coral inside a thin purple field box; place the invitation line small across the top, acid-lime tagline along the bottom, and a small official `BC+AI ecosystem` logo lockup as an integrated lower field mark. Bake in only: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` No other text, no fake sponsor/venue claims, no URLs, no stock tech conference look.

## 3. Overgrown Civic Lab Wall

**For:** AEFL Futureproof brand bakeoff, overgrown civic lab wall direction
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Futureproof x BC+AI poster for AI Ethical Futures Lab. Use the overgrown lab wall reference as the main anchor: dark teal chalkboard or concrete lab wall covered in faint equations, civic-policy marks, tiny stars, creeping ivy, and a vintage projector or observatory instrument in the lower scene. The AEFL title should be enormous mint-green luminous type, centered and clean; the small invitation line sits at the top; the official `BC+AI ecosystem` lockup is centered below the title, native to the poster; the acid-lime tagline anchors the bottom edge. Bake in only the required four text elements, spelled exactly. No other chalk words, no fake math labels, no sponsors, no venue, no URLs, no generic classroom stock.

## 4. Lake Council Dream

**For:** AEFL Futureproof brand bakeoff, lake/council dream direction
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Futureproof x BC+AI poster for AI Ethical Futures Lab. Use the lake/council dream reference as the main anchor: deep teal mountain lake, coral title glow, a small canoe or floating civic circle, quiet symbolic faces or masks in the sky, and analog screenprint grain. The tone is governance as a shared dream, not fantasy cosplay. Title: huge glowing coral `AI ETHICAL FUTURES LAB` near the top third. Add the invitation line at the top, official `BC+AI ecosystem` lockup near the lower center, and acid-lime tagline along the bottom. Bake in only the required four readable text elements. No extra names, no sponsors, no venue, no URLs, no distorted or uncanny face closeups, no generic AI symbols.

## 5. Civic Policy Weather Room

**For:** AEFL Futureproof brand bakeoff, civic policy weather room direction
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Futureproof x BC+AI poster for AI Ethical Futures Lab. Imagine a mythic civic policy weather room in the Futureproof visual language: a dark teal public room with a glowing circular weather map of risks, rights, data flows, and public trust; contour lines, storm arcs, signal nodes, cedar shadows, and warm table light. Make it a serious civic lab, not a disaster movie. Use large glowing coral or mint AEFL title, top invitation line, exact official `BC+AI ecosystem` lockup integrated as a lower map legend, and acid-lime tagline. Only readable text: the four required phrases. No fake labels on maps, no sponsor marks, no venue, no URL, no dashboards, no stock boardroom.

## 6. Laptops-Open Commons

**For:** AEFL Futureproof brand bakeoff, laptops-open commons direction
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Futureproof x BC+AI poster for AI Ethical Futures Lab. Show the AEFL room as an archetypal laptops-open commons without readable screens: a dark community worktable, soft public-room light, laptops as quiet silhouettes, cedar and mycelial signal lines growing through the table, civic map contours overhead, and a warm center glow. The poster should feel practical and participatory, with Futureproof mythic texture. Put the large glowing `AI ETHICAL FUTURES LAB` title in the upper half, invitation line at top, official `BC+AI ecosystem` lockup lower center or lower right, and acid-lime tagline along the bottom. Only the required four text elements may be readable. No screen text, no venue claims, no sponsor marks, no fake app UI, no generic startup scene.

## 7. Evidence Constellation

**For:** AEFL Futureproof brand bakeoff, evidence constellation direction
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Futureproof x BC+AI poster for AI Ethical Futures Lab. Build an evidence constellation: dark forest-sky background, tiny warm evidence lights connected by teal and violet lines, paper-like civic artifacts reduced to abstract shapes with no readable text, cedar silhouettes, public-interest signal routes, and a central luminous gravity point. The composition should echo the signal-field sample but feel more policy-lab and less abstract. Large glowing coral AEFL title, small invitation line at top, official `BC+AI ecosystem` logo lockup as a clean lower-corner field mark, acid-lime tagline at bottom. Bake in only the required four text elements. No fake document text, no extra labels, no sponsors, no venue, no URLs.

## 8. Social-License Threshold

**For:** AEFL Futureproof brand bakeoff, social-license threshold direction
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Futureproof x BC+AI poster for AI Ethical Futures Lab. Make a social-license threshold scene: a luminous doorway or ferry-crossing threshold between a dark BC forest and a civic lab glow, with people implied as small respectful silhouettes or signal points, not portraits. The threshold carries teal, magenta, coral, and acid-lime light like the sample posters. Use strong poster hierarchy: top invitation line, huge glowing `AI ETHICAL FUTURES LAB`, official `BC+AI ecosystem` lockup embedded as a lower field sign, and bottom acid-lime tagline. Only the required four readable text elements. No fake signs, no venue, no sponsors, no URLs, no corporate event stage, no robots.

## 9. Governance Garden

**For:** AEFL Futureproof brand bakeoff, governance garden direction
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Futureproof x BC+AI poster for AI Ethical Futures Lab. Make governance feel like a living garden: dark cedar and moss, luminous roots shaped like policy pathways, small coral and cyan nodes as public input, hand-drawn contour lines, a quiet council circle implied in the undergrowth, and a large clean title layer. Use mint or coral glowing AEFL title, top invitation line, official `BC+AI ecosystem` lockup as a lower poster imprint, and acid-lime tagline at the bottom. Bake in only the required four readable text elements. No botanical labels, no fake sponsor marks, no venue, no URL, no stock sustainability graphics, no generic AI brain.

## 10. Year-Round Series Template

**For:** AEFL Futureproof brand bakeoff, reusable series template direction
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square Futureproof x BC+AI poster template for the AI Ethical Futures Lab year-round series. It must feel reusable for six monthly Luma covers: strong protected title zone, clear lower logo/tagline zone, and a central visual field that can shift by month. Combine the sample language: purple signal nodes, teal forest depth, magenta/coral glow, civic-map contours, analog grain, and a clean official `BC+AI ecosystem` mark. Large glowing `AI ETHICAL FUTURES LAB` title, invitation line at top, official logo lockup lower right or lower center, acid-lime tagline bottom. Only the required four readable text elements; no dates yet, no sponsors, no venue, no URLs, no extra labels. Prioritize legibility and repeatable brand system over novelty.

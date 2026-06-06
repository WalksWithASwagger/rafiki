# AI Ethical Futures Lab - Civic Lab Style Bakeoff 2026

Purpose: create a Pro-only Rafiki bakeoff for a reusable AI Ethical Futures Lab style. This pass replaces the old `bcai-ecosystem` generation direction with the dedicated `aefl` style preset: civic policy lab, human synthesis, room trust, public-interest practice, and polished BC+AI typography.

Grounding sources reviewed:

- AEFL Notion hub: community-driven responsible AI through collaborative research, policy engagement, ethical framework development, public education, community engagement, Indigenous data sovereignty, and public-interest practice.
- AEFL design brief: the core visual idea is "the working room where policy becomes practice"; the lab should feel human, rigorous, accountable, visually alive, and credible to policy partners.
- Live AEFL page: a civic policy lab for public-interest AI in BC, facilitated rooms, human-synthesized community input, public outputs, practical civic tools, and careful room boundaries.
- Supplied AEFL graphics folder: active references are only the woven thread grid, cropped care/trust loop, cropped shared-understanding circle, and BC+AI logo reference.

Reference rule: use the curated AEFL civic-lab board for materiality, care, trust, and simple civic-lab metaphors. Use the Canva typography board only for type hierarchy, spacing, glow, and polish. Use the BC+AI logo references for a native generative `BC+AI ecosystem` mark. Do not copy source elements, source text, or any reference composition exactly.

Production rule: no overlays, compositing, or post-generation typography. All poster text and the BC+AI ecosystem logo must be generated natively into the image.

Required readable text in every candidate:

- `the bc + ai ecosystem association invites you to join our`
- `AI ETHICAL FUTURES LAB`
- `BC+AI ecosystem`
- `multi-modal, multi-cultural, radically local, and future-facing.`

Style rule: use `--style aefl`. Do not use `bcai-ecosystem` for AEFL anymore.

Review rule: reject any candidate that reintroduces anything from the `aefl` style hard-ban list, adds fake event details, copies reference text, mangles the AEFL title beyond public use, or turns the lab into generic technology art.

Reference key passed as globals:

- Curated AEFL civic-lab style board - `/Users/kk/Code/rafiki/prompts/bcai/reference/aefl-civic-lab-style-bakeoff-2026/aefl-civic-lab-reference-board.png`
- Canva typography-only reference board - `/Users/kk/Code/rafiki/prompts/bcai/reference/aefl-canva-typography-reset-2026/aefl-canva-typography-reference-board.png`
- Supplied AEFL BC+AI logo source - `/Users/kk/Code/rafiki/prompts/bcai/reference/aefl-civic-lab-style-bakeoff-2026/assets/004-bcai-logo-source.png`
- Official BC+AI ecosystem logo - `/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png`

Run Rafiki Pro / "Nano Pro" from Rafiki:

```bash
REFS="/Users/kk/Code/rafiki/prompts/bcai/reference/aefl-civic-lab-style-bakeoff-2026/aefl-civic-lab-reference-board.png,/Users/kk/Code/rafiki/prompts/bcai/reference/aefl-canva-typography-reset-2026/aefl-canva-typography-reference-board.png,/Users/kk/Code/rafiki/prompts/bcai/reference/aefl-civic-lab-style-bakeoff-2026/assets/004-bcai-logo-source.png,/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png"
./.venv/bin/python generate.py \
  -f /Users/kk/Code/rafiki/prompts/bcai/aefl-civic-lab-style-bakeoff-2026.md \
  -d /Users/kk/Code/rafiki/output/aefl-civic-lab-style-bakeoff-2026 \
  --model pro \
  --resolution 1K \
  --aspect-ratio 1:1 \
  --style aefl \
  --reference-role brand \
  --global-reference-images "$REFS" \
  --workers 2
```

## 1. Working Table Light

**For:** AEFL civic lab style, working table light
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square AI Ethical Futures Lab poster that feels like a policy working room seen through light and paper, not a literal office. Use a matte dark editorial surface, a warm pool of table light, a few quiet worksheet planes, one restrained thread accent, and generous negative space for crisp typography. The mood is practical, human, calm, and partner-credible: public-interest AI becoming usable civic practice. Generate only these readable text elements: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` Make the BC+AI ecosystem mark native and generative from the logo references. Follow the `aefl` style hard-ban list strictly.

## 2. Civic Field Notes

**For:** AEFL civic lab style, civic field notes
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square AEFL poster built around a clean civic field-notes image: dark green-black ground, soft paper-gold annotation surfaces without readable writing, a coral title glow, teal shadow, and one careful margin line that implies synthesis work. It should feel like public consultation notes becoming a useful artifact, but with no literal documents that contain extra words. Use the typography reference for hierarchy and polish only. Generate only: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` Integrate the BC+AI ecosystem mark natively. Follow the `aefl` style hard-ban list strictly.

## 3. Woven Accountability

**For:** AEFL civic lab style, woven accountability
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square AI Ethical Futures Lab poster with a single tactile woven-thread gesture as the conceptual image: a sparse, beautiful crossing of fibres holding tension on a matte dark surface. Keep it material, calm, and handmade rather than technical. The image should suggest accountability, care, and multiple perspectives held together in a facilitated room. Use restrained BC+AI color: coral title glow, coast teal, mint, paper-gold, deep violet, and acid-lime accents. Generate only the required text: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` Make the BC+AI ecosystem mark native from the logo references. Follow the `aefl` style hard-ban list strictly.

## 4. Care Loop

**For:** AEFL civic lab style, care loop
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square AEFL poster with one warm care-loop form: a simple luminous loop and a few soft connected arcs on a dark editorial field, with lots of open space and no small labels. The idea is room trust, attention, and human synthesis, not technology spectacle. Keep the image beautiful, minimal, and premium enough for a policy partner to share. Generate only these readable words: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` Use the BC+AI logo references for a native generative mark. Follow the `aefl` style hard-ban list strictly.

## 5. Shared Circle Light

**For:** AEFL civic lab style, shared circle light
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square AI Ethical Futures Lab poster with a quiet shared-circle light motif: a soft incomplete ring of warm points and blue-violet shadow, held in a clean editorial composition. The circle should feel like facilitated attention and respectful room boundaries, not an emblem or badge. Leave protected space for a large crisp title and stable lower BC+AI logo zone. Generate only the four required text elements: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` Integrate the BC+AI ecosystem mark natively. Follow the `aefl` style hard-ban list strictly.

## 6. Synthesis Stack

**For:** AEFL civic lab style, synthesis stack
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square AEFL poster around a refined synthesis stack: overlapping blank paper cards, translucent color tabs, soft thread shadows, and warm table light on a matte dark surface. It should suggest facilitated prompts, public-safe recaps, reading paths, and useful civic tools without showing any readable notes or fake UI. Keep it crisp, quiet, and grounded in practice. Generate only: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` Make the BC+AI ecosystem mark native from the logo references. Follow the `aefl` style hard-ban list strictly.

## 7. Room Boundary

**For:** AEFL civic lab style, room boundary
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square AI Ethical Futures Lab poster with a clean room-boundary concept: a matte dark field divided by one soft threshold of coral and teal light, like public and private knowledge being handled carefully. No literal doorway, no stage, no event venue. The image should communicate consent, care, and accountability through simple geometry and light. Use strong Canva-adjacent typography and a faithful native BC+AI ecosystem mark. Generate only: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` Follow the `aefl` style hard-ban list strictly.

## 8. Public Question Held

**For:** AEFL civic lab style, public question held
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square AEFL poster that implies a public question being held with care: one clean blank question-card shape, a soft halo of coral light, teal-green depth, and a few restrained pencil-like marks that are not readable words. The composition should feel like a serious civic workshop with hands-on materials, not a tech conference. Generate only these readable text elements: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` Make the BC+AI ecosystem mark native from the logo references. Follow the `aefl` style hard-ban list strictly.

## 9. Facilitated Signal

**For:** AEFL civic lab style, facilitated signal
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square AI Ethical Futures Lab poster with a restrained facilitated-signal image: a few broad bands of warm and cool light converging on a calm blank working surface, with no tiny technical marks. It should suggest lived experience becoming human-edited themes and public outputs. Keep the visual idea simple, luminous, editorial, and free of clutter. Generate only: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` Integrate the native BC+AI ecosystem mark from the logo references. Follow the `aefl` style hard-ban list strictly.

## 10. Year-Round Civic Lab System

**For:** AEFL civic lab style, year-round series system
**Aspect Ratio:** 1:1

**Prompt:**
> Create a square reusable series-cover system for AI Ethical Futures Lab. Use one calm original image field: dark editorial surface, sparse thread material, soft paper light, coral title glow, teal-violet depth, and acid-lime tagline energy. It should be strong enough to repeat for future monthly covers while leaving space for dates later, but do not add dates now. The feeling is a practical public-interest lab with people at tables, careful synthesis, and accountable civic AI work. Generate only the required readable text: `the bc + ai ecosystem association invites you to join our`, `AI ETHICAL FUTURES LAB`, `BC+AI ecosystem`, and `multi-modal, multi-cultural, radically local, and future-facing.` Make the BC+AI ecosystem mark native and generative from the logo references. Follow the `aefl` style hard-ban list strictly.

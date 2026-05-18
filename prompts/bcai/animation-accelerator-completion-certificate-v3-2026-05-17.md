# AI Animation Accelerator — Completion Certificate v3 (Gemini Pro, brand-role refs)

**Program:** AI Animation Accelerator (BC+AI Ecosystem × Tiny Ghost Studios)
**Purpose:** Print-ready completion certificate. Pick a winner, lock it.
**Why this version is different:**
- **Gemini 3 Pro Image** (not OpenAI) — composes multiple references properly.
- **`--reference-role brand`** — preserves the actual Tiny Ghost mascot and the BC+AI ecosystem logo when prompted, instead of inventing approximations.
- **Three brand assets passed as globals:** the canonical Tiny Ghost portrait from the original "cool" generations, the original attic studio cohort scene (style anchor for the claymation aesthetic), and the official BC+AI ecosystem logo lockup.
- **No style preset** — bcai conflicts with claymation. The aesthetic is described in detail in every prompt + locked in by the cohort reference image.
- **2K resolution, 4:3 landscape** — print-ready at letter or A4.
- **3 focused variations**, not 6.

**Run:**
```
python generate.py \
  -f prompts/bcai/animation-accelerator-completion-certificate-v3-2026-05-17.md \
  -d output/animation-accelerator-completion-certificate-v3-2026-05-17 \
  --no-style -m pro \
  --reference-role brand \
  --global-reference-images "/Users/kk/Code/rafiki/assets/kb-import/mirror/kk-ai-ecosystem/articles/bc-ai-website/ai-animation-accelerator/generated/09-social-square-ghost-portrait.png,/Users/kk/Code/rafiki/assets/kb-import/mirror/kk-ai-ecosystem/articles/bc-ai-website/ai-animation-accelerator/generated/01-hero-recap-cohort-wide.png,/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png" \
  -r 2K -w 2
```

**Reference key (passed to model as globals on every prompt):**
- Reference #1: canonical Tiny Ghost mascot (white friendly cartoon ghost, big black eyes, simple smile, light pink blush cheeks, claymation/sculpted texture, on purple sparkle background)
- Reference #2: original attic studio cohort scene — defines the claymation aesthetic (dark purple walls, shelves of clay character busts, warm desk lamp, sculpted clay creature characters, magenta/teal sparkle, hand-crafted stop-motion texture)
- Reference #3: official BC+AI ecosystem logo (navy background, light mint "BC+AI" letters with chartreuse "+", chartreuse "ecosystem" wordmark)

**Common elements across all three (preserve verbatim):**
- 4:3 landscape, print-ready certificate format
- The whole certificate rendered in the **claymation / stop-motion aesthetic of reference #2** (purple/magenta/teal/orange palette, warm practical lamp light, hand-crafted clay texture throughout, dark whimsy mood)
- **The exact Tiny Ghost mascot from reference #1** present in the composition — same proportions, same face, same blush
- Body copy on the certificate:
  - "AI ANIMATION ACCELERATOR" set in bespoke 3D puffy multi-color claymation type (gradient through purple, pink, green, teal, yellow, orange — hand-carved clay feel)
  - "Certificate of Completion" in clay-textured serif beneath
  - "awarded to"
  - Large magenta hand-sculpted cursive "[STUDENT NAME]"
  - "for the successful completion of the AI Animation Accelerator program"
  - "Issued [MONTH DAY, YEAR]"
- Base: two signature lines side by side — "Kris Krüg, Co-founder, BC+AI Ecosystem" (left) and "Tiny Ghost Studios" (right)
- **The exact BC+AI ecosystem logo from reference #3** rendered as a small lockup at the bottom corner of the certificate (placement specified per variation)
- "Tiny Ghost Studios" wordmark in the opposite bottom corner
- Sharp, legible typography. No lorem ipsum.

---

## 1. Attic Studio Scroll

**Aspect Ratio:** 4:3
**Prompt:**
> A landscape certificate of completion rendered as a single frame of claymation / stop-motion animation in the attic studio aesthetic of reference image #2. The certificate itself is a sculpted clay scroll laid out flat, occupying most of the frame, held open at its lower corners by two small sculpted clay hands. Background behind the scroll: the artist's attic studio — shelves of clay character busts, framed sketches on dark purple walls, warm golden desk lamp glow from the upper-right corner, soft magenta/teal sparkle particles in the air. On the scroll's surface, large 3D puffy claymation typography at the top: "AI ANIMATION ACCELERATOR" — bespoke multi-color clay letters gradient through purple, pink, green, teal, yellow, orange. Below in clean clay-textured serif: "Certificate of Completion". Below: "awarded to". Below: a large flowing magenta hand-sculpted cursive script "[STUDENT NAME]". Below: "for the successful completion of the AI Animation Accelerator program". A small teal clay flourish. "Issued [MONTH DAY, YEAR]". At the lower edge of the scroll, two signature lines: "Kris Krüg — Co-founder, BC+AI Ecosystem" (left) and "Tiny Ghost Studios" (right). The exact Tiny Ghost mascot from reference image #1 (white friendly cartoon ghost, big black eyes, simple smile, light pink blush cheeks, sculpted clay texture) peeks up from the lower-left edge of the scroll — same proportions and face as the reference. The exact BC+AI ecosystem logo from reference image #3 (navy, mint "BC+AI" with chartreuse "+", chartreuse "ecosystem") rendered as a small clean lockup in the lower-left of the certificate. "Tiny Ghost Studios" wordmark in the lower-right of the certificate in matching clay typography. Purple/magenta/teal palette, warm practical lamp light. Hand-crafted textured claymation throughout.

---

## 2. Framed on the Studio Wall

**Aspect Ratio:** 4:3
**Prompt:**
> A landscape composition rendered in the claymation aesthetic of reference image #2: a chunky sculpted clay picture frame mounted on a dark purple attic studio wall, photographed in stop-motion style with warm desk-lamp light catching its top edge from upper-right. The frame is deep purple clay with gold accents and tiny sculpted creature faces in each of the four corners. Inside the frame, the certificate proper: at the top, large 3D puffy multi-color claymation type "AI ANIMATION ACCELERATOR" gradient through purple, pink, green, teal, yellow, orange. Below in clay-textured serif: "Certificate of Completion". Below: "awarded to". Below: a large magenta hand-sculpted cursive "[STUDENT NAME]". Below: "for the successful completion of the AI Animation Accelerator program". A small clay flourish. "Issued [MONTH DAY, YEAR]". Near the base of the certificate, two signature lines: "Kris Krüg — Co-founder, BC+AI Ecosystem" (left) and "Tiny Ghost Studios" (right). The exact BC+AI ecosystem logo from reference image #3 (navy, mint, chartreuse) rendered as a small clean lockup in the lower-left of the certificate inside the frame. "Tiny Ghost Studios" wordmark in the lower-right of the certificate. Outside the frame at the lower-left of the overall image: the exact Tiny Ghost mascot from reference image #1 (white friendly cartoon ghost, big black eyes, simple smile, light pink blush cheeks) — peeking up admiringly at the framed certificate, same proportions and face as the reference. Background: blurred shelves of clay busts on a dark purple wall. Purple/magenta/teal palette. Tactile clay throughout. Dark whimsy.

---

## 3. Spotlight Stage Ceremony

**Aspect Ratio:** 4:3
**Prompt:**
> A landscape certificate composition rendered as a claymation theatre/stage scene in the aesthetic of reference image #2. Center-stage on a small sculpted clay podium: a tall vertical certificate scroll lit from above by a hanging clay bulb casting a warm golden cone of spotlight. The certificate fills most of the central frame. At the top of the certificate, large 3D puffy multi-color claymation type: "AI ANIMATION ACCELERATOR" gradient through purple, pink, green, teal, yellow, orange. Below in clay-textured serif: "Certificate of Completion". Below: "presented to". Below: a large magenta hand-sculpted cursive "[STUDENT NAME]". Below: "for the successful completion of the AI Animation Accelerator program". A small teal clay flourish. "Issued [MONTH DAY, YEAR]". Near the base of the scroll, two signature lines: "Kris Krüg — Co-founder, BC+AI Ecosystem" (left) and "Tiny Ghost Studios" (right). The exact BC+AI ecosystem logo from reference image #3 (navy, mint, chartreuse) rendered as a small clean lockup in the lower-left of the scroll. "Tiny Ghost Studios" wordmark in the lower-right of the scroll. On either side of the podium, small clay-sculpted creature characters (a friendly dragon, a goblin, a robot — matching the supporting cast aesthetic of reference image #2) gathered as a tiny audience watching the certificate proudly. In the front-left foreground: the exact Tiny Ghost mascot from reference image #1 (white friendly cartoon ghost, big black eyes, simple smile, light pink blush cheeks), facing the certificate, same proportions and face as the reference. Background fades into deep purple velvet curtain. Purple/magenta/teal palette with bright warm golden spotlight. Textured claymation throughout. Ceremonial yet whimsical. Sharp legible typography on the scroll.

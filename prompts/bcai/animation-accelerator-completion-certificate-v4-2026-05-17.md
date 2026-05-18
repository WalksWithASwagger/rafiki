# AI Animation Accelerator — Completion Certificate v4 (Luma source as primary ref)

**Program:** AI Animation Accelerator (BC+AI Ecosystem × Tiny Ghost Studios)
**Why v4 over v3:** v3 used the cohort scene as the style anchor; the **actual** north-star source is the Luma hero artwork at `data/refs/animation-accelerator-source.jpg` — it has the exact puffy multi-color "ANIMATION ACCELERATOR" wordmark, the canonical Tiny Ghost mascot, the wing-creature, the attic studio backdrop, AND both logos (BC+AI ecosystem lower-left, Tiny Ghost Studios lower-right). Using THAT as the primary brand reference instead.

**Run:**
```
python generate.py \
  -f prompts/bcai/animation-accelerator-completion-certificate-v4-2026-05-17.md \
  -d output/animation-accelerator-completion-certificate-v4-2026-05-17 \
  --no-style -m pro \
  --reference-role brand \
  --global-reference-images "/Users/kk/Code/rafiki/data/refs/animation-accelerator-source.jpg,/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png" \
  -r 2K -w 2
```

**Reference key:**
- Reference #1: The original Luma hero artwork. THE source of truth for the program's visual identity — wordmark, mascot, wing-creature, attic studio setting, palette, and both logo lockups.
- Reference #2: The official BC+AI ecosystem logo (navy / mint / chartreuse) for the lower-left brand mark.

**Common elements across all three (preserve verbatim):**
- 4:3 landscape, print-ready
- The cert MUST use the exact "ANIMATION ACCELERATOR" wordmark style from reference #1 — bespoke 3D puffy hand-carved clay letters, multi-color gradient (purple, pink, green, teal, yellow, orange)
- The exact Tiny Ghost mascot from reference #1 — white friendly cartoon ghost, big black eyes, simple smile, light blush, sculpted clay texture. Same proportions and face as the reference.
- Aesthetic of reference #1 throughout: deep purple walls, claymation/stop-motion texture, magenta + teal sparkle particles, warm desk lamp light, dark whimsy
- Body copy:
  - "AI ANIMATION ACCELERATOR" in the puffy multi-color claymation wordmark from reference #1
  - "Certificate of Completion" in clay-textured serif beneath
  - "awarded to"
  - Large magenta hand-sculpted cursive "[STUDENT NAME]"
  - "for the successful completion of the AI Animation Accelerator program"
  - "Issued [MONTH DAY, YEAR]"
- Base: two signature lines side by side — "Kris Krüg, Co-founder, BC+AI Ecosystem" (left) and "Tiny Ghost Studios" (right)
- The exact BC+AI ecosystem logo from reference #2 rendered as a clean lockup in the lower-left of the certificate
- "Tiny Ghost Studios" wordmark in the lower-right of the certificate, matching the lockup style shown in reference #1
- Sharp, legible typography. No lorem ipsum.

---

## 1. Direct Translation — Luma Aesthetic, Landscape

**Aspect Ratio:** 4:3
**Prompt:**
> A landscape certificate of completion that translates the EXACT visual aesthetic of reference image #1 (the Luma hero artwork) into a print-ready cert layout. Same attic studio backdrop (dark purple walls, shelves of clay character busts, framed sculpted portraits, an open sketchbook with character sketches on a wooden desk, warm desk lamp glow from the upper-left, magenta and teal sparkle particles). Center of the frame: the bespoke 3D puffy multi-color hand-carved clay "AI ANIMATION ACCELERATOR" wordmark from reference image #1 — letters gradient through purple, pink, green, teal, yellow, orange, hand-carved clay feel, dimensional. Below the wordmark in clay-textured serif: "Certificate of Completion". Below: "awarded to". Below: a large magenta hand-sculpted cursive script "[STUDENT NAME]". Below in clay serif: "for the successful completion of the AI Animation Accelerator program". A small teal clay flourish. "Issued [MONTH DAY, YEAR]". Near the base, two signature lines: "Kris Krüg — Co-founder, BC+AI Ecosystem" (left) and "Tiny Ghost Studios" (right). The exact Tiny Ghost mascot from reference image #1 (white friendly cartoon ghost, big black eyes, simple smile, sculpted clay texture) on the right side of the composition, mid-air, exactly as he appears in the reference. The clay wing-creature from reference image #1 on the left side, exactly as he appears in the reference. The exact BC+AI ecosystem logo from reference image #2 (navy with mint "BC+AI", chartreuse "+", chartreuse "ecosystem") rendered as a clean lockup in the lower-left corner. "Tiny Ghost Studios" wordmark in the matching circular badge style shown in reference image #1, in the lower-right corner. Purple/magenta/teal/orange palette. Stop-motion claymation texture throughout. Dark whimsy. Sharp legible typography.

---

## 2. Clay Scroll Held Open in the Studio

**Aspect Ratio:** 4:3
**Prompt:**
> A landscape claymation scene matching the aesthetic of reference image #1. Center of the frame: a parchment-textured clay scroll laid out horizontally, held open at its lower corners by two small sculpted clay hands. The scroll surface contains the certificate. At the top of the scroll: the exact bespoke 3D puffy multi-color hand-carved clay "AI ANIMATION ACCELERATOR" wordmark from reference image #1 — gradient through purple, pink, green, teal, yellow, orange, dimensional clay. Below in clay-textured serif: "Certificate of Completion". Below: "awarded to". Below: a large magenta hand-sculpted cursive script "[STUDENT NAME]". Below in clay serif: "for the successful completion of the AI Animation Accelerator program". A small teal clay flourish. "Issued [MONTH DAY, YEAR]". Near the base of the scroll, two signature lines: "Kris Krüg — Co-founder, BC+AI Ecosystem" (left) and "Tiny Ghost Studios" (right). The exact BC+AI ecosystem logo from reference image #2 (navy / mint / chartreuse) as a clean lockup in the lower-left of the scroll. "Tiny Ghost Studios" circular badge wordmark from reference image #1 in the lower-right of the scroll. Behind the scroll: the attic studio from reference image #1 — dark purple walls, shelves of clay character busts, framed sculpted portraits, warm desk lamp glow from upper-left, magenta and teal sparkle particles. The exact Tiny Ghost mascot from reference image #1 (white friendly cartoon ghost, big black eyes, simple smile) peeking up from the lower-left edge of the scroll. The clay wing-creature from reference image #1 peeking from the lower-right edge of the scroll. Purple/magenta/teal/orange palette. Stop-motion claymation texture throughout.

---

## 3. Framed on the Studio Wall, Ghost & Creature Admiring

**Aspect Ratio:** 4:3
**Prompt:**
> A landscape composition in the claymation aesthetic of reference image #1: a chunky sculpted clay picture frame mounted on a dark purple attic studio wall, with the certificate displayed inside the frame. The frame is deep purple clay with gold accents and small sculpted creature faces in each of the four corners. Inside the frame, the certificate: at the top, the exact bespoke 3D puffy multi-color hand-carved clay "AI ANIMATION ACCELERATOR" wordmark from reference image #1 (gradient through purple, pink, green, teal, yellow, orange, dimensional). Below in clay-textured serif: "Certificate of Completion". Below: "awarded to". Below: a large magenta hand-sculpted cursive "[STUDENT NAME]". Below: "for the successful completion of the AI Animation Accelerator program". A small clay flourish. "Issued [MONTH DAY, YEAR]". Near the base of the certificate inside the frame, two signature lines: "Kris Krüg — Co-founder, BC+AI Ecosystem" (left) and "Tiny Ghost Studios" (right). The exact BC+AI ecosystem logo from reference image #2 (navy / mint / chartreuse) as a clean lockup in the lower-left of the certificate. "Tiny Ghost Studios" circular badge wordmark from reference image #1 in the lower-right of the certificate. OUTSIDE the frame, in the foreground: at lower-left, the exact Tiny Ghost mascot from reference image #1 (white friendly cartoon ghost, big black eyes, simple smile) admiring the framed certificate. At lower-right, the clay wing-creature from reference image #1 also looking up at the frame proudly. Background behind the frame: dark purple wall with blurred shelves of clay character busts and framed sketches, warm desk-lamp glow from upper-right catching the top of the frame. Magenta and teal sparkle particles in the air. Purple/magenta/teal/orange palette. Stop-motion claymation texture throughout. Dark whimsy.

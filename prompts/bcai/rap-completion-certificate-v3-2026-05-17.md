# RAP — Completion Certificate v3 (Gemini Pro, brand-role refs)

**Program:** Responsible AI Professional Certification
**Purpose:** Print-ready completion certificate. Pick a winner, lock it.
**Why this version is different:**
- **Gemini 3 Pro Image** (not OpenAI) — handles multi-reference compositions properly; previous OpenAI run was using the shield as an *edit base canvas* instead of compositing it INTO the cert layout.
- **`--reference-role brand`** — preserves the actual referenced marks (RAP shield + BC+AI logo) when prompted, instead of inventing approximations.
- **Two brand assets passed as globals**, reused every prompt: the official RAP shield and the official BC+AI ecosystem logo.
- **2K resolution, 4:3 landscape** — print-ready at letter or A4.
- **3 focused variations**, not 6.

**Run:**
```
python generate.py \
  -f prompts/bcai/rap-completion-certificate-v3-2026-05-17.md \
  -d output/rap-completion-certificate-v3-2026-05-17 \
  --style bcai -m pro \
  --reference-role brand \
  --global-reference-images "/Users/kk/projects/BC + AI/rap-cert.png,/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png" \
  -r 2K -w 2
```

**Common elements across all three (preserve verbatim):**
- 4:3 landscape, print-ready cream parchment background
- Top: the **exact RAP Certification shield** from reference #1 — deep forest green, gold double-border, bold "RAP" cream, "CERTIFICATION" on gold ribbon banner, "Responsible AI Professional" small, "BC+AI ecosystem" wordmark at the base of the shield, gold star burst at apex. Render the shield as-shown in the reference.
- Body copy:
  - "CERTIFICATE OF COMPLETION" in small caps, deep forest green
  - "is hereby awarded to"
  - Large elegant cursive script "[STUDENT NAME]" in warm gold
  - "for the successful completion of the Responsible AI Professional Certification program"
  - "Issued [MONTH DAY, YEAR]"
- Base: two signature lines side-by-side — "Kris Krüg, Co-founder, BC+AI Ecosystem" (left) and "Program Director, Responsible AI Professional" (right)
- **BC+AI ecosystem logo** from reference #2 rendered as the official navy/mint/chartreuse logo lockup in the lower-left or lower-right of the cert (specified per variation). Render the logo as-shown in the reference.
- Sharp, legible typography. No lorem ipsum.

---

## 1. Classic Centered Shield

**Aspect Ratio:** 4:3
**Style:** bcai
**Prompt:**
> A formal landscape certificate of completion on warm cream parchment with a thin deep forest green border framing the entire page. Centered at the top of the page: the exact RAP Certification shield from reference image #1 (deep forest green with gold double-border, bold cream "RAP", "CERTIFICATION" gold ribbon banner, "Responsible AI Professional" small below, "BC+AI ecosystem" wordmark at the shield's base, gold star burst at apex) — rendered at moderate size with breathing room around it. Below the shield, centered: "CERTIFICATE OF COMPLETION" in small-caps deep forest green. Below: "is hereby awarded to" in serif. Below: a large elegant cursive script placeholder "[STUDENT NAME]" in warm gold, spanning most of the width. Below: "for the successful completion of the Responsible AI Professional Certification program" in elegant serif. A delicate horizontal gold flourish divider. "Issued [MONTH DAY, YEAR]" in serif. At the base of the page, two signature lines side by side with printed names beneath: "Kris Krüg — Co-founder, BC+AI Ecosystem" (left) and "Program Director, Responsible AI Professional" (right). In the lower-right corner of the page: the exact BC+AI ecosystem logo from reference image #2 (navy background, light mint "BC+AI" with chartreuse "+", chartreuse "ecosystem" wordmark), rendered as a small clean lockup. Symmetric, formal, deeply legible. Sharp typography.

---

## 2. Forest-Frame Botanical Border

**Aspect Ratio:** 4:3
**Style:** bcai
**Prompt:**
> A landscape completion certificate on cream parchment, with an ornate but tasteful botanical border running the full perimeter — fine line-drawn BC forest motifs in deep forest green and warm gold: cedar boughs along the top and bottom, douglas fir needles down the sides, small pine cones at the four corners. Inside the frame, centered at the top: the exact RAP Certification shield from reference image #1 (deep forest green, gold double-border, bold cream "RAP", "CERTIFICATION" gold ribbon, "Responsible AI Professional", "BC+AI ecosystem" wordmark at base, gold star burst at apex) — small enough to leave breathing room. Below the shield, centered: "CERTIFICATE OF COMPLETION" in small-caps forest green. Then: "is hereby awarded to". Then large cursive warm-gold "[STUDENT NAME]". Then: "for the successful completion of the Responsible AI Professional Certification program". A small gold flourish. "Issued [MONTH DAY, YEAR]". Two signature lines at the base — "Kris Krüg, Co-founder, BC+AI Ecosystem" (left) and "Program Director, Responsible AI Professional" (right). In the lower-left corner, just inside the botanical border: the exact BC+AI ecosystem logo from reference image #2 (navy, mint "BC+AI", chartreuse "+", chartreuse "ecosystem"), rendered as a small clean lockup. Reverent, rooted, place-specific. Sharp legible typography.

---

## 3. Modern Asymmetric — Shield Left, Logo Right

**Aspect Ratio:** 4:3
**Style:** bcai
**Prompt:**
> A landscape completion certificate, contemporary and confident. Cream parchment background, no border. Left third of the page: a vertical band of deep forest green with a soft gold inner edge, with the exact RAP Certification shield from reference image #1 centered in that band (deep forest green shield, gold double-border, bold cream "RAP", "CERTIFICATION" gold ribbon, "Responsible AI Professional", "BC+AI ecosystem" wordmark at base, gold star burst at apex). Right two-thirds: clean typographic block on parchment. Top line in small-caps forest green: "CERTIFICATE OF COMPLETION". Below in elegant large serif: "is hereby awarded to". Below in large warm-gold cursive script: "[STUDENT NAME]" spanning the width of the right column. Below in serif: "for the successful completion of the Responsible AI Professional Certification program". A thin horizontal gold rule. "Issued [MONTH DAY, YEAR]". At the base of the right column, two signature lines side by side: "Kris Krüg, Co-founder, BC+AI Ecosystem" and "Program Director, Responsible AI Professional". In the lower-right corner of the page: the exact BC+AI ecosystem logo from reference image #2 (navy, mint, chartreuse), rendered as a small clean lockup. Asymmetric, modern, formal. The kind of certificate a designer would frame.

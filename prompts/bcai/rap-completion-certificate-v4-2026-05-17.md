# RAP — Completion Certificate v4 (8.5×11 landscape print-ready, 4K)

**Program:** Responsible AI Professional Certification
**Why v4 over v3:** Bumped to 4K resolution for crisp print output, and refined prompts to push the design from "clean" to "amazing." Same Gemini Pro + brand-role reference setup that worked in v3 — keeps the real RAP shield and real BC+AI ecosystem logo composed properly into the layout.

**Aspect ratio note:** US Letter landscape is 11:8.5 (1.294). Gemini's closest supported ratio is 4:3 (1.333) — ~3% wider. Generated 4:3; trim ~3% off the long edge in post for exact letter-landscape fit, OR print as-is letting margins absorb it.

**Run:**
```
python generate.py \
  -f prompts/bcai/rap-completion-certificate-v4-2026-05-17.md \
  -d output/rap-completion-certificate-v4-2026-05-17 \
  --style bcai -m pro \
  --reference-role brand \
  --global-reference-images "/Users/kk/projects/BC + AI/rap-cert.png,/Users/kk/Code/rafiki/prompts/futureproof/reference/bcai-logo-light-official.png" \
  -a "4:3" -r 4K -w 2
```

**Reference key:**
- Reference #1: The official RAP Certification shield — deep forest green, gold double-border, bold cream "RAP", "CERTIFICATION" gold ribbon banner, "Responsible AI Professional" small below, "BC+AI ecosystem" wordmark at base of shield, gold star burst at apex. Use as-shown.
- Reference #2: The official BC+AI ecosystem logo — navy background, light mint "BC+AI" letters with chartreuse "+", chartreuse "ecosystem" wordmark. Use as-shown.

**Common elements across all three (preserve verbatim):**
- 11:8.5 landscape, print-ready at US Letter (11×8.5") or close-crop to A4 landscape
- Warm cream parchment background, deeply textured but not noisy
- The exact RAP Certification shield from reference #1 prominently placed (positioned per variation). Render with crisp gold edges and the bold cream "RAP" letters perfectly legible. The shield is the visual centerpiece — give it presence.
- Body copy (perfect spelling, sharp serif):
  - "CERTIFICATE OF COMPLETION" — small-caps deep forest green, letter-spaced
  - "is hereby awarded to" — elegant italic serif
  - **[STUDENT NAME]** — large flowing cursive script in rich warm gold, the visual anchor of the cert, spanning the central width
  - "for the successful completion of the Responsible AI Professional Certification program" — refined serif
  - "Issued [MONTH DAY, YEAR]" — small serif
- Base of certificate: two signature lines side-by-side with handwritten-style signatures and printed names beneath — "Kris Krüg, Co-founder, BC+AI Ecosystem" (left) and "Program Director, Responsible AI Professional" (right)
- The exact BC+AI ecosystem logo from reference #2 (navy block, mint "BC+AI" with chartreuse "+", chartreuse "ecosystem") rendered cleanly as a small lockup, placement specified per variation. Render the logo as-shown — do not redraw or restyle.
- Sharp legible typography. No lorem ipsum. No spelling errors.

---

## 1. Classic Centered Shield — Refined

**Aspect Ratio:** 4:3
**Style:** bcai
**Prompt:**
> A formal landscape Certificate of Completion on warm cream parchment with deep texture but no noise. A double inset border in deep forest green with a fine warm-gold inner rule frames the entire page, leaving generous margins. Centered at the top: the exact RAP Certification shield from reference image #1 — deep forest green with gold double-border, bold cream "RAP" letters perfectly crisp, "CERTIFICATION" on the gold ribbon banner, "Responsible AI Professional" small text below, "BC+AI ecosystem" wordmark at the shield's base, gold star burst at the apex — rendered at substantial presence size, with subtle gold glow radiating gently behind it. Below the shield, generous breathing space, then centered: "CERTIFICATE OF COMPLETION" in small-caps deep forest green, letter-spaced with elegance. Below: "is hereby awarded to" in italic serif. Below: a large flowing cursive script placeholder "[STUDENT NAME]" in rich warm gold, spanning the central width — this is the visual anchor. Below: "for the successful completion of the Responsible AI Professional Certification program" in refined serif. A delicate horizontal gold flourish — laurel-leaf motif, finely detailed. "Issued [MONTH DAY, YEAR]" in small serif. Near the base, two signature lines side by side with handwritten-style ink signatures and printed names beneath: "Kris Krüg — Co-founder, BC+AI Ecosystem" (left) and "Program Director, Responsible AI Professional" (right). In the lower-right corner of the page, sitting just inside the inset border: the exact BC+AI ecosystem logo from reference image #2 (navy block with light mint "BC+AI" letters, chartreuse "+", chartreuse "ecosystem" wordmark) rendered cleanly as a small lockup. Symmetric, formal, ceremonial. Print-grade typography throughout. Cream / deep forest green / warm gold palette.

---

## 2. Modern Asymmetric — Shield Band Left, Type Block Right

**Aspect Ratio:** 4:3
**Style:** bcai
**Prompt:**
> A contemporary landscape Certificate of Completion. Cream parchment background. The left third of the page is a clean vertical band of deep forest green with a soft warm-gold inner edge running its full height. Centered in that band: the exact RAP Certification shield from reference image #1 (deep forest green shield, gold double-border, bold cream "RAP", "CERTIFICATION" gold ribbon, "Responsible AI Professional", "BC+AI ecosystem" wordmark at base, gold star burst at apex) — rendered with crisp detail, subtle gold glow behind it, the band framing it like a banner. The right two-thirds of the page is a clean typographic block on cream. Top-aligned, in small-caps deep forest green: "CERTIFICATE OF COMPLETION", letter-spaced confidently. Below in italic serif: "is hereby awarded to". Below: a large flowing cursive script "[STUDENT NAME]" in rich warm gold, spanning the width of the right column — the visual anchor. Below in serif: "for the successful completion of the Responsible AI Professional Certification program". A thin horizontal warm-gold rule. "Issued [MONTH DAY, YEAR]" in small serif. Near the base of the right column, two signature lines side by side with handwritten-style ink signatures and printed names beneath: "Kris Krüg, Co-founder, BC+AI Ecosystem" and "Program Director, Responsible AI Professional". In the lower-right corner of the page: the exact BC+AI ecosystem logo from reference image #2 rendered cleanly as a small lockup. Asymmetric, modern, confident, formal. Print-grade typography throughout.

---

## 3. Botanical Forest Border — Heritage Edition

**Aspect Ratio:** 4:3
**Style:** bcai
**Prompt:**
> A landscape Certificate of Completion on warm cream parchment with an ornate but tasteful botanical border running the full perimeter — fine line-drawn BC forest motifs in deep forest green with warm-gold highlights: cedar boughs along the top and bottom edges, douglas fir needles down the left and right sides, small pine cones at the four corners, a subtle salal-leaf motif anchoring the upper-center. Inside the botanical frame, centered at the top: the exact RAP Certification shield from reference image #1 (deep forest green, gold double-border, bold cream "RAP", "CERTIFICATION" gold ribbon, "Responsible AI Professional", "BC+AI ecosystem" wordmark at base, gold star burst at apex) — rendered with crisp detail, subtle gold glow. Below the shield, generous breathing space, then centered: "CERTIFICATE OF COMPLETION" in small-caps deep forest green, letter-spaced. Below: "is hereby awarded to" in italic serif. Below: a large flowing cursive script "[STUDENT NAME]" in rich warm gold spanning the central width — the visual anchor. Below: "for the successful completion of the Responsible AI Professional Certification program" in refined serif. A finely-drawn gold laurel flourish. "Issued [MONTH DAY, YEAR]" in small serif. Near the base, two signature lines side by side with handwritten-style ink signatures and printed names beneath: "Kris Krüg, Co-founder, BC+AI Ecosystem" (left) and "Program Director, Responsible AI Professional" (right). In the lower-left corner, just inside the botanical border: the exact BC+AI ecosystem logo from reference image #2 rendered cleanly as a small lockup. Reverent, place-rooted, heritage-grade. Print-quality typography throughout. The kind of certificate someone hangs on their wall for a decade.

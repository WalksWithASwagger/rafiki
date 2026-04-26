# ED + AI v2 — HOPECODE lane (4 prompts)

Uses the repo’s **HOPECODE style suffix** (`--style hopecode`) so jittered mycelial mapping, paper grain, and anti-corporate tone are enforced consistently—on top of these **education-specific** narrative prompts (systems-diagram clarity *without* SaaS clipart).

**Model:** `gemini-3-pro-image-preview` (Gemini **Pro** image in API terms; the CLI prints “Nano Banana” as the tool nickname—there is no separate “Nano Pro” product name here.)

**Batch — no reference images** (let style suffix + text drive the look):

```bash
cd /Users/kk/Code/notion-local/kk-ai-ecosystem/tools/image-gen
npx image-gen ../../content/projects/ed-ai-education-meetup/image-prompts-ed-ai-meetup-v2-hopecode-4.md \
  --model gemini-3-pro-image-preview \
  --resolution 2K \
  --aspect-ratio square \
  --output-dir ../../content/projects/ed-ai-education-meetup/outputs/v2-hopecode-4 \
  --style hopecode
```

---

## 5. Pedagogy underground — what metrics miss

**For:** Critical keynotes; hopeful systems view

**Prompt:**
> **Systems poster:** Above ground, a tidy **“ENGAGEMENT / SCALE / SCORES”** dashboard sketched as faint cold-blue wireframe (no readable numbers). **Below ground**, thick **mycelial roots** carry what schools actually run on: **care labor, consent, repair, co-created rubrics, land-based learning, mutual aid between staff**. Roots in warm earth, ash, rust, moss; **spectral oil-slick** edges where root meets wireframe (interference, not rainbow gradient). Marginalia in tiny handwriting calls out contrasts (e.g. “attendance ≠ presence”). Typography: **ED + AI** as stamped title; **AI IN EDUCATION** on torn tape; **BC + AI** in margin. **Ban:** cute robots, apples, stock schoolbus icons.

---

## 6. Classroom as commons — metabolic sketch

**For:** Community meetup; solarpunk pragmatism

**Prompt:**
> **Metabolic diagram** (not isometric): flows between **library ↔ garden ↔ kitchen ↔ gym ↔ street ↔ home** as irregular **zones** connected by meandering paths. Energy/care shown as **loops**, not one-way arrows to a “platform.” Small glyphs for **wifi mesh, seed library, shared childcare block** — abstract icons only. Color: earth + moss + photocopy grey; **electric fungi** teal highlights on **three** junctions only (restraint). Title: **ED + AI** in monospace crossed with brush-letter warmth; **AI IN EDUCATION** on a diagonal ribbon; **BC + AI** small. **Ban:** holographic UI, floating tablets, perfect hub-and-spoke.

---

## 7. Ungrading constellation — marginal resistance

**For:** Square social; dense but legible

**Prompt:**
> **Field sheet** on stained paper: a **constellation** of hand-drawn dots (students? projects?) with **non-Euclidean** connections—some thick trust lines, some dashed experiments. One zone labeled only with **“?”** in circle. Red-pen energy: a few **cross-outs** on invisible fake policy text (suggest only, no readable paragraphs). **Spectral rot** at paper edge. **ED + AI** large in rough black ink; **AI IN EDUCATION** as sideways margin note; **BC + AI** as tiny circled footnote. Feels like **organizer’s notebook photographed on kitchen table**. **Ban:** neat network graphs, corporate rounded rectangles, glassmorphism.

---

## 8. Speculative timetable — spiral time vs bell schedule

**For:** Story slide; temporal critique + hope

**Prompt:**
> **Two time models** in one composition: left, a **rigid bell grid** drawn in pale pencil (fading); right, a **spiral / seasonal calendar** in ink with **growth rings** suggesting revisiting topics. Mycelial threads **bridge** the two—showing migration of one lesson from “slot” to “returning practice.” Ochre, ink black, muted purple twilight; **iridescent interference** only along the spiral. Typography: **ED + AI** on the spiral band; **AI IN EDUCATION** interrupting the grid like a sticker; **BC + AI** on the gutter. **Ban:** clocks with robot arms, futuristic alarm icons, neon countdown.

---

# Round 2 — Sporeprint + biolum (fav direction), typography fixed

Reference image = your favorite moodboard: **teal biolum fungi**, **ochre gnarled branches**, **violet spore-mist**. The model must **not** copy its lettering; use the ref for **palette, grain, lighting, and organic layout energy** only.

**Typography rules (every image):** Words on the image are **exactly** these three strings (correct spelling): **ED + AI** (primary), **AI IN EDUCATION** (secondary), **BC + AI** (small credit). Set in **crisp professional type** — neo-grotesque, geometric sans, or restrained high-contrast serif — with **optical kerning**, **even stroke weight**, **clean counters**, **no faux chalk**, **no crayon**, **no paint-drip letters**, **no warped illegible display**. **Forbidden on canvas:** the words “lane”, “HOPECODE”, “prompt”, “variant”, “biolum”, or any meta label; no lorem; no extra slogans.

**Batch** (from `tools/image-gen`; Pro model, 2K square):

```bash
cd tools/image-gen
REF="../../content/projects/ed-ai-education-meetup/refs/ref-user-fav-sporeprint-biolum.png"
OUT="../../content/projects/ed-ai-education-meetup/outputs/round2-sporeprint-type"
npx image-gen ../../content/projects/ed-ai-education-meetup/image-prompts-round2-sporeprint-typography.md \
  --reference-images "${REF},${REF},${REF},${REF},${REF},${REF},${REF},${REF},${REF},${REF}" \
  --model gemini-3-pro-image-preview \
  --resolution 2K \
  --aspect-ratio square \
  --output-dir "$OUT" \
  --no-style
```

---

## 1. Spore disk + exterior type

**For:** Hero where type does not fight the print

**Prompt:**
> Square poster. **Lower two-thirds:** near-black field with a **fungal spore-print** morphology: radial **violet and magenta stipple** fading to void at center, subtle asymmetry like a real spore deposit. **Upper third:** generous negative space; **ED + AI** in large **clean geometric sans** (inspired by Neue Haas Grotesk or similar), **birch white**, razor-sharp edges; **AI IN EDUCATION** one line smaller, tracked caps, same family; **BC + AI** tiny, **sunrise orange**, bottom corner of type block only. Organic spore zone **must not** cover the type. Teal biolum glow only as a **thin rim** under the spore disk edge. Reference image for **color and spore density** only.

---

## 2. Branches + biolum, Swiss lockup

**For:** Same organic subject as fav, readable at distance

**Prompt:**
> Illustration: **interlaced ochre and burnt-sienna branches** with **teal-cyan glowing mushroom clusters** and **violet spore specks** (reference mood). Background deep soil black with fine grain. Typography **centered in the upper half** on an implied **matte charcoal panel** (very subtle, not a corporate card): **ED + AI** in **bold neo-grotesque**, white; **AI IN EDUCATION** below in **medium weight**, +15% letterspacing; **BC + AI** small orange, **baseline-aligned**. Letters **vector-sharp** — if any texture, **micro halftone on fill only**, not outline wobble. No branch crossing through the cap-height of **ED + AI**.

---

## 3. Letterpress bite on dark

**For:** Print craft + premium type

**Prompt:**
> **Letterpress / deboss simulation:** **ED + AI** appears **deeply impressed** into **dense charcoal stock**, ink **warm white**, slight **ink squeeze** on counters only (physically believable). **AI IN EDUCATION** blind-deboss line beneath. **BC + AI** in **small burnt-orange** foil dot. Surrounding the type block, **organic vignette**: gnarled roots and **teal biolum pinpoints** emerging from edges only; **violet spore haze** in corners. Type remains **legible and horizontal**. Reference for **palette and biolum temperature** only.

---

## 4. Spore field + tabular micro-grid

**For:** Data-dense but type-clean

**Prompt:**
> **Composition:** faint **graphite grid** (5% opacity) suggesting measurement; overlaid **spore scatter field** in **violet** with higher density in **two lobes** (spore-print echo, abstract). **No fake numbers.** Three text lines only, **left-aligned** in **lower fifth**: **ED + AI** heavy sans; **AI IN EDUCATION** regular; **BC + AI** small. **Monospace allowed only for the two smaller lines** if it improves clarity — still **crisp**, not handwritten. **Teal** accents as **three** small glowing nodes on the grid intersections only. Reference for **spore grain and teal** only.

---

## 5. Night soil + edge-lit sign

**For:** Crisp type over painterly ground

**Prompt:**
> **Background:** painterly **night soil** texture, roots, **purple spore drift**, **teal** fungal glow (reference mood), full-bleed. **Foreground plane:** a **slightly inset matte panel** (dark olive-black) occupying **center 55%**; on it, **ED + AI** in **large white geometric sans** with **subtle outer glow** (single 2px equivalent, not blobby); **AI IN EDUCATION** caps smaller; **BC + AI** orange, corner. Panel edges **soft** — not glassmorphism, not neon frame. Type **absolutely sharp**. Reference for **background painting style** only.

---

## 6. Radial spore mandala, type outside ring

**For:** Sporeprint-forward

**Prompt:**
> **Central medallion:** circular **spore-print radial** stipple, **violet to magenta**, imperfect circle, **black pit** at true center (small). **Outside** the medallion, **circular text path** optional for **AI IN EDUCATION** only if perfectly readable; otherwise keep **AI IN EDUCATION** straight horizontal **below** the disk. **ED + AI** sits **above** the disk in **wide sans**. **BC + AI** at **6 o’clock** outside ring, small. **Teal biolum** as **short arc highlights** on **two** quadrants of the ring only. Reference for **spore rhythm and color** only.

---

## 7. Split layout — nature below, type above

**For:** Zero overlap ambiguity

**Prompt:**
> **Horizontal split at 42% from top.** **Upper zone:** flat **deep forest black** with **only typography**: **ED + AI** huge geometric sans white; **AI IN EDUCATION**; **BC + AI** orange — all **centered**, **maximum clarity**. **Lower zone:** full **organic illustration** — branches, **teal mushrooms**, **violet spores**, grain (reference mood). **Hard edge** between zones (no soft blend through text). **Ban:** text in lower zone.

---

## 8. Mycelial constellation, minimal words

**For:** Atmosphere first, type secondary but sharp

**Prompt:**
> **Sparse** composition: black ground; **delicate root lines** in umber; **seven to twelve** **teal** glowing nodes with **hairline connections**; **violet spore** particles **sparse** like distant stars. **Lower left:** compact type stack — **ED + AI** white sans **small caps** style but readable size; **AI IN EDUCATION** one line; **BC + AI** tiny. **Upper right** stays **empty** for breathing room. Type **no texture warp**. Reference for **node glow color and spore color** only.

---

## 9. Poster margin + specimen center

**For:** Museum label aesthetic

**Prompt:**
> **Center:** “specimen” circle — **spore print** on **warm grey paper** tone, **violet stipple**, **slight coffee stain** at one edge (subtle). **Margins:** **wide black margin** like a framed study; in **bottom margin**, **left-aligned** professional sans: **ED + AI**, **AI IN EDUCATION**, **BC + AI** in **three lines**, white and orange accent on credit only. **Outside** the specimen circle in the **side margins**, faint **teal biolum** spores only. Type **never** on the spore disk itself. Reference for **spore and paper texture** only.

---

## 10. Bold wordmark + spore aura

**For:** Type-forward social card

**Prompt:**
> **ED + AI** dominates: **extra-bold geometric sans**, **white**, **slightly tightened** tracking, **no outline** except optional **1px** subtle **teal** outer keyline. **AI IN EDUCATION** directly under, **regular weight**, **smaller**. **BC + AI** in **orange**, **lower right**. Behind the wordmark, **soft radial spore aura** — **violet and magenta** particles **falling off by 70% opacity** by mid-frame; **no** busy branches **behind** the main word (keep **dark soft vignette** there). **Tiny** teal glow dots **only** in the aura. Reference for **aura color and particle feel** only.

---

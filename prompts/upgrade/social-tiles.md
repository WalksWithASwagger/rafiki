# The Upgrade — Social Tiles (upgrade style)

**Program:** The Upgrade (Newsletter + Podcast)
**Style:** upgrade
**Reference:** none — relies on style suffix

Visual language: square 1:1 format optimized for Instagram, LinkedIn, and X. Deep-purple backgrounds with bright-orange and light-blue accents. Each tile leaves deliberate composition zones for overlaid text — title, quote, name, or stat — that the design team will add in post. No baked-in copy. Prompts target backdrop and atmosphere, not finished social posts.

Run: `python generate.py -f prompts/upgrade/social-tiles.md -d output/upgrade-social --style upgrade -m gpt-image-2 -w 2`

---

## 1. Quote Card — Background for Overlaid Text

**For:** quote cards from the newsletter or podcast — the prompt produces a background, the team overlays the quote
**Aspect Ratio:** 1:1
**Style:** upgrade
**Prompt:**
> Square composition: a soft deep-purple gradient background with a single subtle bright-orange light source in the lower-right quadrant, falling off gently across the canvas. A few faint light-blue prismatic streaks drift diagonally at low opacity. The center of the frame is intentionally calm and uncluttered — a clear plate of color where bold quote text will be overlaid in post. No literal subjects, no people, no objects competing for attention. Mood is contemplative and confident, an empty stage waiting for the words.

---

## 2. Article Summary Card

**For:** "issue at a glance" cards summarizing the week's newsletter on social
**Aspect Ratio:** 1:1
**Style:** upgrade
**Prompt:**
> Square editorial composition: a clean deep-purple field divided gently into a top hero zone and a lower content zone by a soft bright-orange horizon line. In the top zone, a single bold abstract motif — an upward arrow built from light-blue prismatic shards — anchors the eye. The lower zone is intentionally calm with light texture, designed for three short bullet lines of overlaid text. Composition feels modular and editorial, the kind of layout a magazine art director would approve. Energetic but legible.

---

## 3. Episode Announcement Card

**For:** "new episode out now" announcement tiles for podcast episodes
**Aspect Ratio:** 1:1
**Style:** upgrade
**Prompt:**
> Square composition with strong diagonal energy: a deep-purple field crossed by a single sweeping bright-orange diagonal band running from lower-left to upper-right, with light-blue glow trails feathered along its edges. Small prismatic spark accents punctuate the band. Center-left is left intentionally clean for an episode number and title overlay; the right edge carries the visual energy. The whole thing reads as forward momentum — something just dropped, you should listen now. Bold, urgent, welcoming.

---

## 4. Speaker / Guest Spotlight

**For:** "this week's guest" cards introducing a podcast or newsletter contributor
**Aspect Ratio:** 1:1
**Style:** upgrade
**Prompt:**
> Square portrait-style composition: a deep-purple frame with a bright-orange spotlight glow concentrated in the upper-center, falling across an empty oval portrait area where a guest photo will be composited in post. Around the portrait area, light-blue prismatic ribbons curl gently, suggesting introduction and arrival. The lower third of the frame is calm purple, ready for a name and one-line credential overlay. Warm, welcoming, professional — the visual equivalent of "please welcome."

---

## 5. Big Idea / Single-Concept Tile

**For:** standalone tiles featuring one big idea, framework, or principle from the newsletter
**Aspect Ratio:** 1:1
**Style:** upgrade
**Prompt:**
> Square composition centered on a single bold abstract icon: a bright-orange geometric shape — a stylized key, a prism, an unlocked padlock, or an upward chevron — rendered with depth and a soft light-blue rim glow, floating against a clean deep-purple field. The icon owns the center; everything else is generous breathing room. Subtle radial gradient draws the eye inward. Designed to support a 2-4 word concept name overlay below the icon. Memorable, iconic, framework-friendly.

---

## 6. Stats / Data Callout Backdrop

**For:** data drops — "73% of professionals say…" — backdrops for big-number stat callouts
**Aspect Ratio:** 1:1
**Style:** upgrade
**Prompt:**
> Square composition: a deep-purple field with a faint light-blue grid of dotted lines and tick marks running across the lower half, evoking measurement without literally drawing a chart. A single bright-orange accent — a thick underline or a small upward marker — sits in the lower-right, ready to anchor a percentage or stat overlay. The upper half of the frame is calm and open for a bold stat number, with room beneath for a one-line caption. The mood is data-grounded but not corporate — clean, curious, energetic.

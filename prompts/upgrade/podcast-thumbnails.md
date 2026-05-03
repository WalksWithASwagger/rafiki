# The Upgrade — Podcast Thumbnails (upgrade style)

**Program:** The Upgrade (Podcast)
**Style:** upgrade
**Reference:** none — relies on style suffix

Visual language: square 1:1 thumbnails optimized for podcast apps (Apple Podcasts, Spotify, Overcast). Deep purple base with bright-orange and light-blue accents. Each thumbnail is differentiated by episode format — guest, solo, series-opener, live — so listeners can scan the feed and immediately recognize the kind of episode. Designed to read clearly at small sizes; bold focal element, generous contrast, calm space for an episode number overlay.

Run: `python generate.py -f prompts/upgrade/podcast-thumbnails.md -d output/upgrade-podcast --style upgrade -m gpt-image-2 -w 2`

---

## 1. Guest Episode (Interview Format)

**For:** standard interview episodes featuring one guest
**Aspect Ratio:** 1:1
**Style:** upgrade
**Prompt:**
> Square thumbnail: a deep-purple field with two soft circular spotlights — one bright orange on the left, one light blue on the right — overlapping gently in the center where their colors blend into a warm prismatic intersection. The two spotlights represent host and guest in conversation; the overlap is the dialogue itself. No literal faces or microphones — the geometry carries the meaning. A small clean zone in the upper-left corner is reserved for an episode number overlay. Bold, immediately legible at thumbnail size, intellectually warm.

---

## 2. Solo Episode (KK Alone)

**For:** solo episodes — KK riffing, recapping, or essaying on one topic
**Aspect Ratio:** 1:1
**Style:** upgrade
**Prompt:**
> Square thumbnail: a deep-purple field anchored by a single bold bright-orange circular focal point in the dead center, surrounded by concentric light-blue rings expanding outward like a signal broadcast. The composition is symmetrical and meditative — one voice, radiating outward. Subtle prismatic shimmer at the outer edges. The upper-left corner has a small clean zone for an episode number overlay. Reads instantly at thumbnail size as "single voice, focused thought."

---

## 3. Series-Opener (Bigger, More Dramatic)

**For:** the launch episode of a new podcast series or season — needs to feel like an event
**Aspect Ratio:** 1:1
**Style:** upgrade
**Prompt:**
> Square thumbnail: a deep-purple field dramatically split by a vertical column of bright-orange light rising from the lower edge to the top of the frame, with prismatic light-blue rays fanning outward from its base like a sunrise. The column is bold and confident — a flag planted, a series begun. The corners of the frame are darker purple, focusing the eye inward toward the column. Upper-left corner reserved for an episode number or "Series One" overlay. Cinematic, ceremonial, unmistakably a launch.

---

## 4. Live Recording / Event

**For:** live-recorded episodes from events, conferences, on-stage interviews
**Aspect Ratio:** 1:1
**Style:** upgrade
**Prompt:**
> Square thumbnail: a deep-purple field rendered as a low-angle stage view, with a bright-orange stage-edge glow running along the lower third of the frame and warm light-blue spotlight beams angling down from the upper corners. Above the stage line, suggested silhouetted heads of an audience appear as soft purple shapes — implied crowd, not detailed. The focal point is the stage zone itself: open, lit, ready. Upper-left corner reserved for an episode number overlay. Energetic, communal, distinctly "in the room."

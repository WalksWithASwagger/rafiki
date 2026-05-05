# Image Generation Prompts: What Would Chat Do?
**Project:** WiT Regatta 2026 Panel Prep
**Date:** January 24, 2026
**Brand Style:** KK (dark #0f0f1a-#1a1a2e, teal #00c8b4, purple #9333ea)
**Output Sizes:** 1200x630px (LinkedIn/social), 1080x1080px (Instagram)

---

## 1. Hero Image — Article Featured

**For:** Blog header, LinkedIn post, Twitter card
**Aspect:** landscape (1200x630px)
**File name:** `what-would-chat-do-hero.png`

**Prompt:**
```
A creative professional standing at the intersection of technology and humanity, with one hand reaching toward flowing digital patterns (representing AI possibilities) and the other hand grounded on natural elements (representing human wisdom). The composition is split between a dark technological space with glowing teal circuits and a warmer space with purple earth tones. Seven translucent layers extend into the distance, symbolizing seven-generation thinking. The person's reflection appears in a mirror-like surface, but the reflection shows data streams and algorithmic patterns, visualizing "AI as mirror." Professional, thought-provoking, slightly surreal. Dark background with teal and purple accents matching KK brand. No text overlay. Cinematic lighting. High quality digital art.
```

---

## 2. CASK Framework — Visual Diagram

**For:** Educational content, slide deck, Instagram carousel
**Aspect:** square (1080x1080px)
**File name:** `cask-framework-diagram.png`

**Prompt:**
```
A clean, modern 2x2 grid visualization of the CASK Framework. Four quadrants on dark background (#0f0f1a):

Top-left: "CURIOSITY" with icon of wonder/exploration (warm glow)
Top-right: "AWARENESS" with icon of open eye/perception (teal accent #00c8b4)
Bottom-left: "SKEPTICISM" with icon of question mark/critical thinking (purple accent #9333ea)
Bottom-right: "CAUTION" with icon of thoughtful pause/deliberation (balanced tone)

Each quadrant has a one-line description below the title. Center shows subtle connection lines between all four elements. Typography: clean sans-serif (Inter or Helvetica), excellent hierarchy. Style: technical but accessible, not corporate. Modern, educational design. KK brand colors: dark backgrounds, teal and purple accents, white text.
```

---

## 3. Five Questions — Bias Assessment Card

**For:** Educational resource, social share, presentation slide
**Aspect:** landscape (1200x630px)
**File name:** `five-questions-bias-assessment.png`

**Prompt:**
```
A stacked list of five critical questions against a dark gradient background (#0f0f1a to #1a1a2e). Each question appears on a subtle card with progressive teal-to-purple gradient borders. Typography treatment makes each question scannable:

1. What data trained this?
2. Who is MISSING?
3. What proxy variables?
4. Who defined success?
5. Who benefits, who risks?

Title at top: "5 Questions to Reveal AI Bias" in bold white text. Minimal icons beside each question (magnifying glass, person outline, network nodes, target, scales). Clean, modern, educational tone. Dark background with KK brand accent colors (teal #00c8b4, purple #9333ea). Professional typography, excellent readability.
```

---

## 4. Mirror Concept — Core Visual

**For:** Conceptual illustration, social media, article illustration
**Aspect:** square (1080x1080px)
**File name:** `ai-as-mirror-concept.png`

**Prompt:**
```
Abstract visualization of AI as mirror concept. A figure stands before a large, semi-transparent mirror. The mirror doesn't show the person's reflection - instead it shows amplified patterns: data streams, biases made visible as geometric distortions, historical patterns emerging as layered shadows. The person's silhouette is grounded and human, while the mirror reveals the algorithmic interpretation - both beautiful and concerning. Split lighting: warm human side, cool digital reflection. Teal (#00c8b4) and purple (#9333ea) light playing on the mirror surface. Philosophical, slightly unsettling, thought-provoking. Dark background (#0f0f1a). KK brand aesthetic. No text overlay. High quality digital art.
```

---

## 5. Quote Card — "Write for the Bot"

**For:** Instagram, LinkedIn, Twitter
**Aspect:** square (1080x1080px)
**File name:** `quote-write-for-the-bot.png`

**Prompt:**
```
Large, bold typography on dark background (#0f0f1a). Central quote in white:

"If your values aren't in text, they don't exist to AI. And that's dangerously close to won't exist."

Attribution: "— Kris Krug" in smaller text at bottom.

Visual element: subtle transparent letters/text flowing into an AI-like neural pattern in the background. Teal accent line (#00c8b4) at top, purple accent (#9333ea) at bottom. Professional, urgent, memorable. Clean sans-serif font (Inter), excellent hierarchy. Typography-first design with subtle visual support. High contrast for social media readability.
```

---

## 6. Quote Card — "Bias Laundering"

**For:** Twitter, Instagram stories, quick shares
**Aspect:** square (1080x1080px)
**File name:** `quote-bias-laundering.png`

**Prompt:**
```
Bold statement design on dark background (#0f0f1a). Large quote text in white:

"Algorithmic bias launders discrimination - it makes prejudice look like math."

Small visual metaphor: abstract representation of messy human bias (organic, chaotic forms) going through a "clean" algorithmic filter (geometric, precise forms), coming out looking precise but still containing the original bias. Teal (#00c8b4) and purple (#9333ea) accents frame the composition. Typography-first design, high contrast, instantly shareable. Attribution: "— Kris Krug" at bottom. KK brand style. Professional, impactful.
```

---

## 7. Panel Event Promo

**For:** Social promotion, event marketing, email header
**Aspect:** landscape (1200x630px)
**File name:** `wit-regatta-2026-panel-promo.png`

**Prompt:**
```
Event promotional graphic for WiT Regatta 2026 panel.

Title: "What Would Chat Do? Navigating AI's Hidden Currents"
Date: February 5, 2026, 12pm-1:30pm
Venue: Amazon YVR26, Vancouver

Visual: abstract representation of hidden currents beneath a calm surface - data flows, algorithmic patterns, bias vectors shown as underwater currents in teal (#00c8b4) and purple (#9333ea). A small boat/compass at the surface representing human navigation and steering.

Panel details section with text:
"Featuring: Kris Krug, Fernanda Ave (moderator), Sonali Sharma, Adina Gray"

Clean layout, professional event aesthetic. Dark background (#0f0f1a to #1a1a2e) with teal/purple accents. Space for WiT Regatta logo. Include hashtag: #Regatta2026

Modern, sophisticated design. Typography: clean sans-serif. High quality promotional material.
```

---

## Generation Instructions

### Using Nano Banana Tool:

```bash
cd /path/to/kk-ai-ecosystem/tools/image-gen
python generate.py --prompt-file prompts/2026-01-24-what-would-chat-do.md --output-dir ./output/wit-regatta-2026/
```

### Brand Style Parameters:
- Primary background: #0f0f1a to #1a1a2e (dark gradient)
- Accent 1: #00c8b4 (teal)
- Accent 2: #9333ea (purple)
- Text: #ffffff (white) and #a0a0b0 (gray)
- Typography: Clean sans-serif (Inter, Helvetica, Arial)
- Style: Technical but accessible, not corporate
- Mood: Professional, thought-provoking, grounded

### Output Requirements:
- High resolution (300dpi for print-quality)
- Optimized file size for web (<500KB per image)
- PNG format with transparency support where applicable
- Consistent branding across all images
- Accessible design (high contrast, readable text)

---

## Post-Generation Checklist:

- [ ] Verify all images match KK brand colors
- [ ] Check text readability on all backgrounds
- [ ] Ensure consistent typography across all cards
- [ ] Optimize file sizes for web without quality loss
- [ ] Test display on various social media platforms
- [ ] Create alternate versions if needed (light/dark, different aspect ratios)
- [ ] Archive source files and prompts for future use

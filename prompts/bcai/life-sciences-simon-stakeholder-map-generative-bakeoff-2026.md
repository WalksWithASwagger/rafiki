# Life Sciences Simon Stakeholder Map — Generative Bakeoff 2026

Purpose: rerun Simon's AI Life Sciences stakeholder graphic as a fully generative Rafiki bakeoff in the BC+AI Life Sciences / Healing Futures style. This is a correction pass: no overlays, no compositing, and no post-generation typography.

Source interpretation: Simon's original graphic is a central `AI LIFE SCIENCES` hub connected to ten stakeholder and discipline groups. The information architecture is good; the mismatch is style. Replace the red clip-art wheel with a native Life Sciences research commons that feels like the existing Healing Futures system.

Production rule: no overlays, no compositing, no deterministic label layer, and no post-generation typography. Every accepted candidate must generate the title, tagline, and all labels natively in the artwork. Reject or rerun candidates with malformed text, missing labels, extra labels, fake sponsor marks, fake venue claims, fake URLs, hospital-blue stock styling, generic doctor stock, Data Whale imagery, whales, orcas, or any marine mammal icon drift.

Required readable text in every candidate:

- `AI LIFE SCIENCES`
- `Diversity driving innovation and impact`
- `Patients & Patient Groups`
- `Counsellors & Mental Health Practitioners`
- `Doctors & Surgeons`
- `AI Drug Discovery`
- `Biotech & Pharma`
- `Health Systems`
- `Engineering`
- `Biology`
- `Computational Science / AI`
- `Clinical Medicine`

Reference key passed as globals:

- Healing Futures no-text art plate - `/Users/kk/Code/rafiki/output/life-sciences-master-viewer-2026/assets/002-02-healing-futures-no-text-art-plate.png`
- Existing Life Sciences poster with native text - `/Users/kk/Code/rafiki/output/life-sciences-master-viewer-2026/assets/077-07-ai-plus-life-sciences.png`
- Life Sciences ecosystem map language - `/Users/kk/Code/rafiki/output/life-sciences-master-viewer-2026/assets/070-01-life-sciences-ai-membrane-discovery-map.png`

Run OpenAI / Image Gen 2 from Rafiki:

```bash
REFS="/Users/kk/Code/rafiki/output/life-sciences-master-viewer-2026/assets/002-02-healing-futures-no-text-art-plate.png,/Users/kk/Code/rafiki/output/life-sciences-master-viewer-2026/assets/077-07-ai-plus-life-sciences.png,/Users/kk/Code/rafiki/output/life-sciences-master-viewer-2026/assets/070-01-life-sciences-ai-membrane-discovery-map.png"
./.venv/bin/python generate.py \
  -f /Users/kk/Code/rafiki/prompts/bcai/life-sciences-simon-stakeholder-map-generative-bakeoff-2026.md \
  -d /Users/kk/Code/rafiki/output/life-sciences-simon-stakeholder-map-generative-bakeoff-2026-gpt \
  --model gpt-image-2 \
  --quality high \
  --aspect-ratio 16:9 \
  --style futureproof-mythic+bcai-ecosystem \
  --reference-role style \
  --global-reference-images "$REFS" \
  --workers 1
```

Run Gemini Pro from Rafiki:

```bash
REFS="/Users/kk/Code/rafiki/output/life-sciences-master-viewer-2026/assets/002-02-healing-futures-no-text-art-plate.png,/Users/kk/Code/rafiki/output/life-sciences-master-viewer-2026/assets/077-07-ai-plus-life-sciences.png,/Users/kk/Code/rafiki/output/life-sciences-master-viewer-2026/assets/070-01-life-sciences-ai-membrane-discovery-map.png"
./.venv/bin/python generate.py \
  -f /Users/kk/Code/rafiki/prompts/bcai/life-sciences-simon-stakeholder-map-generative-bakeoff-2026.md \
  -d /Users/kk/Code/rafiki/output/life-sciences-simon-stakeholder-map-generative-bakeoff-2026-pro \
  --model pro \
  --resolution 1K \
  --aspect-ratio 16:9 \
  --style futureproof-mythic+bcai-ecosystem \
  --reference-role style \
  --global-reference-images "$REFS" \
  --workers 2
```

Global visual direction: preserve the original ten-node hub-and-spoke meaning, but make it feel like the Life Sciences canon: deep evergreen and obsidian, coast teal river currents, cyan data-light, coral biological branching, birch-white native label fields, warm gold connectors, cedar forest, mountain forms, salmon river, mycelium/circuit roots, cellular membranes, protein folds, lab glass, microscopes, responsible discovery, and civic-science credibility. The output should be a finished native infographic/poster, not a background awaiting typesetting. Salmon are acceptable; whales, orcas, and marine mammal silhouettes are not.

## 1. Faithful Healing Futures Stakeholder Map

**For:** Simon stakeholder map remix, native typography fidelity pass
**Aspect Ratio:** 16:9

**Prompt:**
> Create a 16:9 AI Life Sciences stakeholder map in the BC+AI Life Sciences / Healing Futures style. Preserve Simon's structure: a central hub labeled exactly `AI LIFE SCIENCES`, the tagline exactly `Diversity driving innovation and impact`, and ten connected outer label nodes. Generate all labels natively inside the artwork, with crisp readable poster typography. Use this exact outer label set and no others: `Patients & Patient Groups`, `Counsellors & Mental Health Practitioners`, `Doctors & Surgeons`, `AI Drug Discovery`, `Biotech & Pharma`, `Health Systems`, `Engineering`, `Biology`, `Computational Science / AI`, `Clinical Medicine`. Make the map feel like a living research commons: deep forest night, coast teal river/circulation currents, coral biological branching, cyan data-light, birch-white label fields, warm gold connectors, cedar silhouettes, mountains, salmon, mycelium/circuit roots, lab glass, microscope hints, protein folds, and cellular membranes. No overlays, no blank placeholders, no post-production label zones, no extra readable words, no fake sponsors, no URLs, no red background, no hospital-blue stock style, no generic stock doctors, no whale imagery, no orcas, no marine mammals.

## 2. Clean Research Commons Wheel

**For:** Simon stakeholder map remix, cleaner institutional diagram
**Aspect Ratio:** 16:9

**Prompt:**
> Create a polished 16:9 BC+AI Life Sciences research commons wheel. The finished graphic must contain native readable text, not placeholders: center title `AI LIFE SCIENCES`, smaller subtitle `Diversity driving innovation and impact`, and exactly ten outer nodes labeled `Patients & Patient Groups`, `Counsellors & Mental Health Practitioners`, `Doctors & Surgeons`, `AI Drug Discovery`, `Biotech & Pharma`, `Health Systems`, `Engineering`, `Biology`, `Computational Science / AI`, `Clinical Medicine`. Use clean birch-white circular label medallions connected by warm gold and teal living-system pathways. Surround the map with responsible discovery imagery: membranes, protein folds, dataset constellations, mycelial/circuit networks, lab glass, microscopes, cedar, mountains, salmon river, cyan signal light, coral branching. Make it credible and calm, suitable to send back to a Life Sciences working group. No post-generation text, no overlays, no unlabeled circles, no malformed labels, no extra categories, no red field, no clinical stock image look, no fake logos or sponsor marks, no whales, no orcas, no marine mammals.

## 3. Poster-Map With Native Label Plaques

**For:** Simon stakeholder map remix, poster hierarchy variant
**Aspect Ratio:** 16:9

**Prompt:**
> Create a finished 16:9 illustrated poster-map for `AI LIFE SCIENCES` in the established Healing Futures style. The map should have a central dark-green native title plaque reading exactly `AI LIFE SCIENCES` with `Diversity driving innovation and impact` below it, surrounded by ten native label plaques. Required plaques: `Patients & Patient Groups`, `Counsellors & Mental Health Practitioners`, `Doctors & Surgeons`, `AI Drug Discovery`, `Biotech & Pharma`, `Health Systems`, `Engineering`, `Biology`, `Computational Science / AI`, `Clinical Medicine`. Connect each plaque with organic teal/gold pathways like river currents, mycelium, roots, and data circuits. Use PNW life-sciences motifs from the references: mountain-headed healing futures energy without making a portrait dominate, cedar lungs, salmon stream, cellular membranes, protein-like folds, lab glass, microscope silhouettes, cyan data-light, coral biological trees. No overlays, no post typesetting, no placeholder spaces, no extra words, no misspelled labels, no red background, no whale, no orca, no marine mammal, no hospital ad style.

## 4. Living Systems Atlas

**For:** Simon stakeholder map remix, richest ecosystem atlas variant
**Aspect Ratio:** 16:9

**Prompt:**
> Create a 16:9 finished Life Sciences living-systems atlas with native text. The central hub must read exactly `AI LIFE SCIENCES`; the subtitle must read exactly `Diversity driving innovation and impact`; the ten connected atlas regions must be labeled exactly `Patients & Patient Groups`, `Counsellors & Mental Health Practitioners`, `Doctors & Surgeons`, `AI Drug Discovery`, `Biotech & Pharma`, `Health Systems`, `Engineering`, `Biology`, `Computational Science / AI`, and `Clinical Medicine`. Build the atlas as one connected ecosystem, not a corporate icon wheel: cedar forest and mountain horizon, salmon river carrying cyan data-light, coral capillary branches, mycelium/circuit roots, protein folds, cell membranes, glassware, microscopes, small civic-science gathering details, warm gold connection points, deep evergreen/teal/obsidian palette. Make the text large, clean, and legible. No overlays, no compositing, no later labels, no extra readable words, no fake dates, no fake sponsors, no red background, no clinical stock imagery, no Data Whale, no whales, no orcas, no marine mammals.

## Local Run Notes

GPT Image 2 run from Rafiki:

- Output folder: `/Users/kk/Code/rafiki/output/life-sciences-simon-stakeholder-map-generative-bakeoff-2026-gpt/run-20260605-184219`
- Winner: `01-faithful-healing-futures-stakeholder-map.png`
- Why: all required labels were generated natively and the style is closest to the Life Sciences canon while preserving Simon's map structure.
- Rejected: `02-clean-research-commons-wheel.png`, `03-poster-map-with-native-label-plaques.png`, and `04-living-systems-atlas.png` because they drifted into whale/orca imagery and/or extra generated text.

# Image Pipeline Operator Guide

Scenario decision guide for Rafiki CLI and the gpt-image-1 Streamlit UI.
New contributor? Find your scenario in §1, copy the command, run it.

Cross-references: `styles/` for full style specs, `docs/SCOPE.md` for architecture.

---

## 1. Quick-start decision table

| Scenario | Tool | Style flag | Model | Example command |
|---|---|---|---|---|
| **KK editorial / social** — article headers, LinkedIn banners, social variants (16:9, 1:1, 9:16) | Rafiki CLI | `--style kk` | `flash` | `python generate.py -f prompts/kk/2026-01-24-what-would-chat-do.md -d output/kk --style kk` |
| **BC+AI ecosystem assets** — RAP marketing, logos, ecosystem diagrams | Rafiki CLI | `--style bcai` (diagrams) or `--no-style` (RAP, carries own styling) | `gpt` (RAP) / `flash` (diagrams) | `python generate.py -f prompts/bcai/rap-marketing.md -d output/rap --no-style -m gpt --quality high` |
| **HOPECODE community diagrams** — BC+AI community theory, solarpunk mapping | Rafiki CLI | `--style hopecode` | `flash` | `python generate.py -f prompts/bcai/bcai-hopecode-visual-prompts.md -d output/hopecode --style hopecode` |
| **WAIFF punk zine slide deck** — BWR, xerox grain, ransom-note type; needs reference image | Rafiki CLI (single-prompt; file needs reformat for batch — see §5) | `--style none` (prompts carry zine aesthetic) | `pro` | `python generate.py -p "Chaotic punk zine cover..." --no-style -m pro --reference-image prompts/kk-kb/reference-collage-v2.png` |
| **GNI cosmic editorial diagrams** — space-blue, orbital, orbit maps | Rafiki CLI | `--style gni` | `flash` / `pro` | `python generate.py -p "AI journalism toolkit — four orbiting quadrants: GenAI, NLP, ML, Predictive — radial nodes on deep space-blue" --style gni -m pro` |
| **GNI sovereignty diagrams (gpt-image-1)** — 44-line .txt, HOPECODE prefix | gpt-image-1 Streamlit UI | HOPECODE prefix file | `gpt-image-1` | `cd tools/gpt-image-batch-ui && streamlit run diagram_gen_ui.py` (see §4) |
| **MAC femme / body-compute** — abstract body-compute metaphors | Rafiki CLI | `--style femme` | `flash` | `python generate.py -p "Two braiding networks, warm and cool, selective membrane boundary..." --style femme -m flash` — enforce avoid-clauses; MAC community review before publishing |
| **Indigenomics diagrams** — sovereignty-forward, ancestral wisdom + tech | Rafiki CLI | `--style indigenomics` | `flash` / `pro` | `python generate.py -p "Circular reciprocity flow diagram, braided organic-tech, navy and cedar and cyan..." --style indigenomics -m flash` — abstract motifs only; nation-specific symbols need governance review |
| **Upgrade AI brand** — transformation/empowerment imagery | Rafiki CLI | `--style upgrade` | `flash` | `python generate.py -f prompts/upgrade/training-marketing.md -d output/upgrade --style upgrade` |
| **KK personal / thought-leadership** — name-the-bias series, what-would-chat-do | Rafiki CLI | `--style hopecode` (name-the-bias) or `--style kk` (wwcd) | `flash` | `python generate.py -f prompts/kk/name-the-bias-hopecode.md -d output/ntb --style hopecode` |

**Model alias reference:** `flash` = gemini-2.5-flash-image · `nano` = flash alias · `pro` = gemini-3-pro-image-preview · `gpt` = gpt-image-2 · `gpt1` = gpt-image-1 · `dalle3` = dall-e-3

---

## 2. Prompt file inventory

| File path | Scenario | Format | Rafiki-batch-ready | Notes |
|---|---|---|---|---|
| `prompts/kk/2026-01-24-what-would-chat-do.md` | KK editorial / social | `## N.` sections + `**Prompt:**` blockquotes | Yes | 7 prompts; WiT Regatta 2026 social/article images |
| `prompts/kk/name-the-bias-hopecode.md` | KK personal / thought-leadership | `## N.` sections + `**Prompt:**` blockquotes | Yes | 9 HOPECODE-style images for "Name the Bias" article series |
| `prompts/kk/name-the-bias-social-variants.md` | KK personal / thought-leadership | `## N.` sections + `**Prompt:**` blockquotes | Yes | 6 square/vertical social variants for name-the-bias |
| `prompts/bcai/rap-marketing.md` | BC+AI ecosystem — RAP certification | `## N.` sections + `**Prompt:**` blockquotes | Yes | RAP brand colors embedded; use `--no-style` |
| `prompts/bcai/rap-logo-variations.md` | BC+AI ecosystem — RAP logos | `## N.` sections + `**Prompt:**` blockquotes | Yes | Logo variants; use `--no-style` |
| `prompts/bcai/rap-martin-revisions.md` | BC+AI ecosystem — RAP lecture revisions | `## N.` sections + `**Prompt:**` blockquotes | Yes | Martin revision pass for RAP Weeks 1-3; optional local reference via `--reference-images` |
| `prompts/bcai/ecosystem-diagrams.md` | BC+AI ecosystem assets | `## N.` sections + `**Prompt:**` blockquotes | Yes | Mycelial network ecosystem diagrams |
| `prompts/bcai/bcai-hopecode-visual-prompts.md` | BC+AI / HOPECODE community | `## N.` sections + `**Prompt:**` blockquotes | Yes | Also contains HOPECODE style preface block for single-prompt overrides |
| `prompts/bcai/context-creator-field-journals.md` | BC+AI ecosystem | `## N.` sections + `**Prompt:**` blockquotes | Yes | Field journal visual series |
| `prompts/hopecode/personal-blog-examples.md` | HOPECODE style examples | `## N.` sections + `**Prompt:**` blockquotes | Yes | Journey maps, story diagrams |
| `prompts/hopecode/thought-leadership-examples.md` | HOPECODE style examples | `## N.` sections + `**Prompt:**` blockquotes | Yes | Framework diagrams, systems maps |
| `prompts/hopecode/concept-mapping-examples.md` | HOPECODE style examples | `## N.` sections + `**Prompt:**` blockquotes | Yes | Relationship networks, knowledge webs |
| `prompts/upgrade/training-marketing.md` | Upgrade AI brand | `## N.` sections + `**Prompt:**` blockquotes | Yes | Course marketing, transformation imagery |
| `prompts/kk-kb/hopecode-creative-big-ideas-prompts.md` | HOPECODE community / GNI | `## N.` sections; image + diagram pairs per concept | Yes | 7 big-idea sets; quick-export one-liners at bottom for Streamlit UI |
| `prompts/kk-kb/websummit-vancouver-kk-zine-image-prompts.md` | KK zine / resistance | `## N.` sections + `**Prompt:**` blockquotes | Yes | Web Summit Vancouver adjacent; HOPECODE/zine tone |
| `prompts/kk-kb/ai-diagram-pipeline-teaching-kit.md` | Teaching / educational | `## N.` sections + `**Prompt:**` blockquotes | Yes | Pipeline diagrams for AI teaching contexts |
| `prompts/kk-kb/custom-gpt-diagram-gardener-and-weaver.md` | BC+AI / HOPECODE | `## N.` sections + `**Prompt:**` blockquotes | Yes | Custom GPT workflow diagrams |
| `prompts/kk-kb/femme-prompts-mac-image-repository.md` | MAC femme / body-compute | `### Subhead` (not `## N.`) — not parseable | No | Polished + short-variant format; paste prompts individually. **Review avoid-clauses before generating.** |
| `prompts/kk-kb/gni-cosmic-diagram-style-guide.md` | GNI cosmic editorial | Style guide / reference snippets | No | Style reference, not a batch file; extract prompts individually |
| `prompts/kk-kb/indigenomics-diagram-style-guide.md` | Indigenomics diagrams | Style guide reference | No | Style/context reference only |
| `prompts/kk-kb/waiff-brazil-2026-keynote-image-prompts.md` | WAIFF punk zine | `## N.` sections + `**Prompt:**` blockquotes | Yes — 21 prompts | `--style zine -m pro`. Reference image: `reference-collage-v2.png` (not in repo — provide locally via `--reference-image`). |
| `prompts/kk-kb/gni-journalism-sovereignty/gpt-image-1-prompts-one-per-line.txt` | GNI sovereignty diagrams | One prompt per line (.txt) | No (Streamlit UI) | 44 lines; feeds gpt-image-1 Streamlit UI with HOPECODE prefix — see §4 |
| `prompts/kk-kb/wikipedia-five-futures-image-prompts-archive.md` | Wikipedia Five Futures | Midjourney `/imagine` syntax | No — archival | **Do not batch.** Dark themes require care review. See §7. |

---

## 3. Style reference

Eleven styles are registered in `styles/styles.yaml` and available via `--list-styles`: `kk`, `hopecode`, `bcai`, `futureproof-mythic`, `bcai-ecosystem`, `upgrade`, `zine`, `gni`, `femme`, `indigenomics`, `cmvan`.

### kk

**Description:** Professional, dark editorial. Dark background (#0f0f1a → #1a1a2e), teal (#00c8b4) and purple (#9333ea) accents. The default style.

**When to use:** Corporate ecosystem content, thought-leadership articles, LinkedIn graphics, event promotions, technical diagrams.

**Example prompt fragment:**
```
A creative professional at the intersection of technology and humanity,
dark gradient background, teal circuit patterns, purple earth tones.
```

**Composition:** Stacks well with `bcai` for ecosystem content (`--style kk+bcai`). Use alone for clean editorial.

---

### hopecode

**Description:** Solarpunk mycelial mapping. Jittered hand-drawn linework, earth tones (ochre, ash, rust, moss) with spectral interference (iridescent oil slick, electric fungi glow), analog grain, photocopy texture. Diagrams look found, not made.

**When to use:** Personal blog, radical thought-leadership, community mapping, grassroots organizing diagrams, anti-colonial framing, speculative futures.

**Example prompt fragment:**
```
Mycelial network spreading from center — organic root system, jittered
hand-drawn lines, ochre + iridescent glow, heavy photocopy grain,
found-not-made quality, anti-corporate resistance energy.
```

**Composition:** Can overlay with `bcai` for professional-organic hybrid. Avoid mixing with `kk` — tonal mismatch.

---

### bcai

**Description:** BC AI Community Centre mycelial network. Organic branching, BC natural color palette (Deep Forest Green #1E3A2B, Coast Blue #175E7C, Earth Brown #78552B), nodes with radial gradients. Professional yet rooted — "rainforest meets innovation."

**When to use:** Ecosystem diagrams, stakeholder maps, RAP-adjacent community content, BC AI branded materials, network visualizations.

**Example prompt fragment:**
```
Interconnected mycelial network, organic branching nodes, deep forest
green and coast blue, varying node sizes, irregular natural growth,
radial from center, minimum 15% white space.
```

**Composition:** Pairs well with `hopecode` for grassroots-organic feel. Sits between `kk` (polished) and `hopecode` (radical).

---

### futureproof-mythic

**Description:** Surrealist Pacific Northwest folk-myth language for Futureproof Festival worlds, rituals, creatures, posters, and invitation scenes.

**When to use:** Mythic event posters, track worlds, surreal social cards, portal scenes, archetypal portraits, and civic-imagination campaign imagery.

**Example prompt fragment:**
```
Surrealist Pacific Northwest folk-art poster, one strong mythic focal point,
living technology woven through cedar forest and river motifs, aurora teal,
coral, ember gold, analog grain, handmade symbolic density.
```

**Composition:** Use alone when the image needs a storybook or talismanic register. Keep one focal symbol readable even when adding dense supporting details.

---

### bcai-ecosystem

**Description:** BC + AI logo-forward ecosystem language for polished community assets, credentials, badges, schedules, partner-facing cards, and reusable campaign templates.

**When to use:** BC + AI event credentials, speaker cards, sponsor thank-yous, stickers, network maps, track badges, and partner-facing social assets.

**Example prompt fragment:**
```
BC + AI mark embedded inside a living ecosystem map, circular badge grammar,
mycelial/circuit network structure, deep forest green, coast teal, warm gold,
generous hierarchy, clear space for title and date.
```

**Composition:** Cleaner and more production-ready than `futureproof-mythic`; pair with `bcai` only when the BC natural network layer should be stronger than the logo system.

---

### upgrade

**Description:** Bold transformation and empowerment. Deep purple (primary), bright orange (accent), light blue (secondary). Dynamic layouts, upward arrows, human + AI partnership framing.

**When to use:** Upgrade AI course marketing, training module headers, skill development pathways, member success stories.

**Example prompt fragment:**
```
Professional in three-quarter profile engaging holographic AI interfaces,
before/after progression from muted to bright, upward momentum, deep
purple + orange accent, empowered transformation energy.
```

**Composition:** Use alone for brand fidelity. Does not compose well with `kk` or `hopecode` — different tonal register.

---

### zine

**Description:** Black/white/blood-red punk zine collage. Xerox grain, halftone dots, ransom-note typography, torn paper edges, staple holes, tape marks. Assembled-at-midnight energy.

**When to use:** WAIFF keynote slides, punk/resistance editorial, Web Summit zine drops.

**Example prompt fragment:**
```
Black white and blood red only. Xerox grain everywhere. Halftone dots.
Ransom-note typography at chaotic angles. Torn paper edges, visible tape,
staple holes. Raw handmade zine energy, anti-corporate.
```

**Composition:** `--style zine` is strict — BWR only. Composing with other styles will dilute the color discipline. Use alone.

---

### gni

**Description:** Cosmic editorial. Deep space-blue gradients, orbital lines, radial nodes, constellation metaphors. Editorial-meets-engineering — science-fiction journalism.

**When to use:** GNI AI Lab slides, journalism-sovereignty diagrams, editorial tech explainers.

**Example prompt fragment:**
```
Deep blue space gradient, soft glow, orbit trails between nodes,
constellation-style connections, editorial meets engineering tone.
```

**Composition:** Pairs well with `kk` (`--style gni+kk`) for extra professional polish. Keep away from `hopecode` — opposite aesthetic registers.

---

### femme

**Description:** Abstract body-compute metaphors for the Mind, AI & Consciousness (MAC) subgroup of BC+AI. Deep indigo/obsidian backgrounds with blush-magenta, teal, and opalescent pastels. Contour fields, membrane boundaries, network routing, nested containers. Quiet, intimate, embodied intelligence — never representational.

**Community note:** Review outputs before publishing. The avoid-clauses in the style suffix are load-bearing (no goddess iconography, no literal anatomy, no medical illustration). MAC community sign-off required for public assets.

**When to use:** MAC event visuals, BC+AI content centering femme/embodied perspectives, abstract scientific imagery with intimate register.

**Example prompt fragment:**
```
Two interpenetrating networks — warm and cool — braiding without merging.
Boundary behaves like selective permeability: slow gradients, semi-transparent
veils, capillary-like filaments reading as negotiation.
```

**Composition:** Use alone. Does not compose cleanly with `zine` or `gni` — distinct tonal register.

**Source:** `prompts/kk-kb/femme-prompts-mac-image-repository.md`, `styles/femme.md`

---

### indigenomics

**Description:** Indigenomics Institute visual language — ancestral wisdom + emergent technology. Deep navy/indigo/ochre palette, braided organic-tech motifs, circular and radial flows (sovereignty-first, not catch-up framing). Mythic realism meets cyberpunk.

**Governance note:** Abstract motifs (braided materials, circular flows, geo-mapping nodes) are safe. Nation-specific cultural symbols (specific regalia, drums, ceremonies) require Indigenous governance and consent before use. When in doubt, ask an Indigenomics Institute contact.

**When to use:** Indigenomics Institute presentations, BC+AI content centering Indigenous economic sovereignty, AI-and-governance educational diagrams.

**Example prompt fragment:**
```
Traditional longhouse structure fused with smart city grid. Fiber-optic
threads weave through cedar beams connecting circular community nodes.
Deep navy background, cedar brown and electric cyan accents.
Abstract — no specific nation's architectural details.
```

**Composition:** Pairs with `gni` for tech-heavy contexts. Keep away from `hopecode` — similar land-based language but different governance and community context.

**Source:** `prompts/kk-kb/indigenomics-diagram-style-guide.md`, `styles/indigenomics.md`

---

### cmvan

**Description:** Creative Mornings Vancouver / Punk Rock AI collage. Black/white halftone plus blood red and hot pink, dripping paint type, distressed physical objects, fire, torn paper, tape, and dense live-event chaos.

**When to use:** Creative Mornings Vancouver keynote slides, Punk Rock AI social cards, Release Day templates, loud event announcements, and poster-like campaign assets.

**Example prompt fragment:**
```
Maximalist punk zine collage in black, white, blood red, and hot pink only.
Distressed halftone photography, dripping paint typography, torn paper,
tape, staple holes, spray bleed, fire energy, dense overlapping layers.
```

**Composition:** More chaotic and color-saturated than `zine`; use when hot pink, photographic objects, and loud live-event energy are intentional parts of the brief.

**Source:** `prompts/creative-mornings-vancouver-may-2026/`, `styles/cmvan.md`

---

## 4. gpt-image-1 Streamlit UI workflow

### When to use Streamlit UI vs Rafiki CLI

| Use Rafiki CLI | Use Streamlit UI |
|---|---|
| Gemini or gpt-image-2 models | gpt-image-1 specifically |
| Batch from `## N.`-formatted .md files | Batch from one-prompt-per-line .txt files |
| Parallel workers (`--workers N`) | Sequential generation with live preview |
| Scripted / CI pipelines | Interactive review as images generate |

### How to invoke

```bash
cd tools/gpt-image-batch-ui
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
streamlit run diagram_gen_ui.py
```

The UI runs at `http://localhost:8501`. Upload your .txt prompt file, optionally upload a style prefix file, select size and quality, then run.

### HOPECODE prefix pattern

To apply HOPECODE style to the GNI sovereignty batch:
1. Load the prefix file: `prompts/kk-kb/gni-journalism-sovereignty/hopecode-style-guide.txt`
2. Load the prompt file: `prompts/kk-kb/gni-journalism-sovereignty/gpt-image-1-prompts-one-per-line.txt` (44 lines)
3. The UI prepends the style guide to each prompt before calling the API.

### Input format

One prompt per line in a `.txt` file. No headers, no blockquotes — plain text. Blank lines are skipped.

### Notes

- Requires OpenAI org verification for `gpt-image-1` if not yet enabled on your account.
- Long prompts: up to ~2 minutes per image.
- On failure the UI stops at the failing line. Fix the prompt and re-run (already-generated files are not automatically skipped).

---

## 5. Reference image workflow

### When reference images matter

The WAIFF zine deck was generated with a `reference-collage-v2.png` style anchor that enforces the BWR (black/white/red) palette and xerographic texture across all slides. Without it, individual slide prompts drift toward cleaner or more colorful outputs.

Reference images are most useful when:
- You need strict palette lock across a multi-slide batch
- A previous output defines the "look" and you're generating variations
- Mockup mode: preserve garment/background, apply new graphic print

### CLI flags

```bash
# Single image — apply reference style
python generate.py -p "Prompt here" --reference-image path/to/reference.png

# Batch — same reference for all prompts
python generate.py -f batch.md -d output/ --reference-image path/to/reference.png

# Batch — different reference per prompt (comma-separated, one per prompt in order)
python generate.py -f batch.md -d output/ --reference-images ref1.png,ref2.png,ref3.png

# Mockup mode (preserve garment, add print)
python generate.py -p "..." --reference-image garment.png --reference-role mockup
```

`--reference-role` choices: `style` (default — look and feel guidance), `brand` (preserve referenced marks/logos when the prompt explicitly asks for them), or `mockup` (preserve the reference image structure, apply design element).

### Documenting references in prompt files

Add a comment in the prompt file header so future operators know what reference was used:

```markdown
<!-- Reference: prompts/kk-kb/reference-collage-v2.png -->
```

### Storage convention

Store reference images alongside the prompt files they anchor:

```
prompts/kk-kb/reference-collage-v2.png
prompts/<folder>/reference-<descriptor>.png
```

---

## 6. Viewer and library commands

### Rebuild viewers without re-generating images

```bash
# Rebuild comparison viewer for a project (re-verifies files on disk)
python generate.py view philadelphia
python generate.py view cmvan-keynote --all-runs   # also rebuild per-run viewers

# Master library — all projects in one filterable page
python generate.py library
python generate.py library --open                  # build + open in browser
python generate.py library --output-dir /custom/output/
```

The library at `output/library.html` shows every image across all projects with:
- Project and model filter chips (click to narrow; click again to clear)
- Rating filters (All / ★ Starred / ✕ Rejected / Unreviewed)
- Grid resize slider (persisted in `localStorage`)

### Per-project viewer features

Open any `output/<project>/viewer.html` to:
- Switch between runs (tabs) or compare all runs side-by-side (**⊞ Compare all**)
- See the generating prompt on each card (3-line clamp)
- Click to open fullscreen lightbox → download button + ⎘ Copy prompt
- Drag the **Grid** slider to resize cards

---

## 7. Common CLI recipes

```bash
# Single image — KK editorial
python generate.py -p "A creative professional at the intersection of technology and humanity..." \
  --style kk -m flash

# Batch from file — HOPECODE community diagrams
python generate.py -f prompts/bcai/bcai-hopecode-visual-prompts.md \
  -d output/hopecode --style hopecode

# RAP certification marketing — model carries its own styling
python generate.py -f prompts/bcai/rap-marketing.md \
  -d output/rap --no-style -m gpt --quality high

# WAIFF punk zine — single slide with reference image (file needs ## N. reformat for batch)
python generate.py \
  -p "Chaotic punk zine cover, dense overlapping collage... Black white and blood red only." \
  --no-style -m pro \
  --reference-image prompts/kk-kb/reference-collage-v2.png

# Parallel batch — 4 workers
python generate.py -f prompts/bcai/rap-marketing.md \
  -d output/rap --workers 4

# Style composition — kk + bcai stacked
python generate.py -p "BC AI ecosystem network diagram..." --style kk+bcai

# Name-the-bias article series — HOPECODE
python generate.py -f prompts/kk/name-the-bias-hopecode.md \
  -d output/name-the-bias --style hopecode

# Social variants — square for Instagram
python generate.py -f prompts/kk/name-the-bias-social-variants.md \
  -d output/ntb-social --style hopecode -a 1:1

# Upgrade AI — transformation imagery
python generate.py -f prompts/upgrade/training-marketing.md \
  -d output/upgrade --style upgrade

# Dry run — preview without API calls
python generate.py -f prompts/bcai/ecosystem-diagrams.md \
  -d output/eco --style bcai --dry-run

# List all registered styles
python generate.py --list-styles

# GNI cosmic — proxy with kk until gni style is registered
python generate.py -p "Minimalist Venn diagram ML NLP GenAI, deep blue space gradient..." \
  --style kk -m flash
```

---

## 8. Archival warning

> **Archival-only files — do not batch-generate without a prompt rewrite:**
>
> - `prompts/kk-kb/wikipedia-five-futures-image-prompts-archive.md` — Midjourney `/imagine` syntax, incompatible with Rafiki batch parser. Dark themes (Resource Squeeze, Contributor Drought) use satirical/dystopian metaphors by design. Require care review before any regeneration or publication.
>
> - `prompts/kk-kb/gni-journalism-sovereignty/gpt-image-1-prompts-one-per-line.txt` — One-per-line format feeds the gpt-image-1 Streamlit UI, not the Rafiki batch parser. Do not pass to `generate.py -f`.

---

## Appendix: aspect ratio presets

| Alias | Ratio | Use |
|---|---|---|
| `linkedin` | 16:9 | LinkedIn posts, banners |
| `instagram` | 1:1 | Instagram feed |
| `twitter` | 16:9 | Twitter/X cards |
| `story` | 9:16 | Instagram/TikTok stories |
| `square` | 1:1 | General square |

Pass as `--aspect-ratio linkedin` or explicit `--aspect-ratio 16:9`.

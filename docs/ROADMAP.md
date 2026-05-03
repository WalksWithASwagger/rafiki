# Rafiki — Master Roadmap

**Purpose:** Rafiki is the content pipeline for all KK / BC + AI visual production. This document defines the direction, priorities, and backlog.

**Guiding principle:** Default to `gpt-image-2` via OpenAI — best output quality and most cost-effective for this workflow. Gemini remains available for style-transfer experiments.

---

## Current State (May 2026)

### What works today
- `generate.py` — batch generation from Markdown prompt files, multi-provider (OpenAI/Gemini), run isolation, usage tracking
- Per-run viewers with lightbox, ratings, compare mode
- Master library viewer spanning all projects
- Local portal server (`generate.py serve`) with persistent ratings API
- Project registry (`config/extra-outputs.json`) to pull in images from other repos
- 4 style packs: `bcai`, `kk`, `hopecode`, `upgrade` (+ cmvan, zine, gni)
- Full RAP certification visual curriculum — 40 images across 4 weeks
- Combined presentation viewer (`generate-rap-viewer.py`) with captions + social post copy

### Known gaps
- No automated social post export (have to copy manually from viewer)
- No image metadata embedding (EXIF/XMP) for archival provenance
- Viewer images reference by relative path — not portable as a single file
- No prompt versioning / diff tracking across regenerations
- No per-image cost tracking (tokens/API cost per generation)

---

## Phase 1 — Polish & Stability (now → near term)

**Goal:** Make the current pipeline bulletproof for daily use.

| Item | Why | Effort |
|------|-----|--------|
| Fix concurrent write race condition in `data/usage-log.json` | Batches with ≥2 workers can corrupt the log | S — file lock or atomic write |
| Add `--model` default to `gpt-image-2` in all docs + prompt file headers | Explicit > implicit; removes ambiguity for new prompt files | XS |
| `generate-rap-viewer.py` → generalize to `generate-presentation-viewer.py` | Pattern is reusable for any content series; RAP is the first instance | M |
| Add `--self-contained` flag to presentation viewer | Embed images as base64 for a truly portable single-file share | M |
| Expand `.gitignore` entries for common output artifacts | Avoid accidentally committing large PNGs into prompts dirs | XS |

---

## Phase 2 — Content Pipeline Expansion (next)

**Goal:** Rafiki covers all recurring content needs, not just one-off batches.

### 2a. Social Post Export
- Add "Export social posts" button to presentation viewer — downloads a `.txt` with all flagged post copy, one per section
- Or: generate a `social-posts.md` file alongside `viewer.html` when running `generate-rap-viewer.py`

### 2b. Prompt Library System
Formalize the prompt library as a structured content asset:
- `prompts/bcai/` — BC + AI curriculum, ecosystem, RAP cert
- `prompts/kk/` — personal brand, KK content series
- `prompts/upgrade/` — The Upgrade newsletter/podcast visual library
- `prompts/gni/` — Google News Initiative / journalism AI visuals
- Each folder gets a `README.md` with run commands, visual system description, and image index

### 2c. Archive Strategy
Define a clear archival flow:
- Approved images → `output/<project>/approved/` (hand-curated, never auto-deleted)
- All runs → `output/<project>/run-*/` (retained by default, purgeable via `generate.py clean --keep-approved`)
- Presentation viewers → `output/<project>-viewer/` (regenerable from approved set)

### 2d. The Upgrade Visual Library
Systematically generate visual assets for all Upgrade newsletter + podcast content:
- Article hero images (16:9)
- Social tiles (1:1 square)
- Email header banners
- Run command pattern already established; just needs prompt files

---

## Phase 3 — Workflow Integration (medium term)

**Goal:** Rafiki fits into the broader content production workflow without manual steps.

### 3a. Notion Integration
- Export approved images + captions to Notion pages automatically
- `generate-rap-viewer.py` output → Notion gallery block (via API)

### 3b. Canva Integration
- Export images + captions as Canva-ready assets (PNG + metadata CSV)
- The Canva MCP is already available — hook it into the presentation viewer export

### 3c. Prompt → Social Post LLM Pass
- After a batch generates, optionally run a second pass: feed the image + caption to an LLM and generate platform-specific social post variants (LinkedIn long-form, X short, Instagram)
- Store variants in `<run-dir>/social-posts.json`

### 3d. Scheduled Regeneration
- Some prompt sets need periodic refresh (new visual treatments of evergreen content)
- Use Claude Code scheduled tasks to trigger regeneration runs and post a summary of what was generated

---

## Phase 4 — Scale & Sharing (longer term)

**Goal:** Rafiki outputs are shareable beyond the local machine.

### 4a. Hosted Viewer
- Deploy `output/rap-all-weeks/viewer.html` to a static host (Vercel, Netlify, or Cloudflare Pages)
- Team can review and pull from a URL, no file sharing needed

### 4b. Password-Protected Team Portal
- Wrap the local portal in basic auth for team sharing
- Or: use Vercel + environment variable for lightweight access control

### 4c. Image CDN / Asset Registry
- Track all approved images in a lightweight registry (JSON or SQLite)
- Enables searching across all content by concept, week, style, date
- Foundation for a searchable asset library across all projects

---

## Prompt Backlog (content to generate)

| Project | Prompt file needed | Priority |
|---------|-------------------|----------|
| The Upgrade — newsletter hero images | `prompts/upgrade/newsletter-heroes.md` | High |
| RAP certification — logo/badge variations | `prompts/bcai/rap-logo-variations.md` ✓ (exists, may need rerun) | Medium |
| RAP marketing — recruitment/social | `prompts/bcai/rap-marketing.md` ✓ (exists) | Medium |
| KK personal brand — speaker/profile images | `prompts/kk/speaker-series.md` | Medium |
| GNI coaching sessions — workshop visuals | `prompts/gni/coaching-sessions.md` | Low |
| BC AI ecosystem — org/stakeholder maps | `prompts/bcai/ecosystem-diagrams.md` ✓ (exists) | Low |
| The Upgrade — podcast episode thumbnails | `prompts/upgrade/podcast-thumbnails.md` | Low |

---

## Technical Debt

| Item | Risk | Fix |
|------|------|-----|
| `data/usage-log.json` concurrent write corruption | Medium — already bit us once | Atomic write via temp file + rename |
| Viewer image paths are relative, not absolute | Low — works fine for local use | `--self-contained` flag for portable exports |
| No test coverage on `lib/` modules | Low — easy to verify manually | Add `tests/test_usage.py`, `tests/test_providers.py` |
| `generate-rap-viewer.py` has hardcoded run dir timestamps | Low — only matters if you rerun and want the viewer to update | Accept `--week-dirs` overrides or auto-detect latest run |

---

## Conventions

- **Default model:** `gpt-image-2` (OpenAI) — best quality/cost ratio for this workflow
- **Default style:** `bcai` for BC + AI content, `kk` for personal brand
- **Reference image:** always pass `--reference-images` for style consistency within a content series
- **Workers:** `-w 2` is the sweet spot — parallel without hammering rate limits
- **Naming:** prompt files in `prompts/<brand>/<project>.md`, outputs in `output/<project>/`

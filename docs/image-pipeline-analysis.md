# Rafiki image pipeline — corpus analysis & operator outline

*Scope: read-only analysis of `prompts/` + `styles/`. No prompt files modified. Review before Phase 2.*  
*Written: 2026-04-25*

---

## 1. Scenario matrix

Eight distinct production scenarios found across the corpus.  
"✓ Rafiki-ready" = can run through `parse_image_prompts_md()` today (uses `## N.` section format).

| Scenario | Prompt source | Tool chain | Style flag | Format | Notes |
|---|---|---|---|---|---|
| **KK editorial / social** | `prompts/kk/` | Rafiki → Gemini flash | `--style kk` | ✓ Rafiki-ready | Article headers, social variants; 16:9 + 1:1 + 9:16 per-prompt |
| **HOPECODE community diagrams** | `prompts/bcai/bcai-hopecode-visual-prompts.md`, `prompts/kk-kb/hopecode-creative-big-ideas-prompts.md` | Rafiki → Gemini flash / gpt-image-1 | `--style hopecode` | Freeform blocks (not `## N.`) | Two files, complementary themes (see §3) |
| **BC+AI ecosystem** | `prompts/bcai/rap-marketing.md`, `ecosystem-diagrams.md`, `rap-logo-variations.md` | Rafiki → Gemini flash | `--style bcai` | ✓ Rafiki-ready (`rap-marketing.md`) | rap-marketing.md already has per-prompt `**Aspect Ratio:**` |
| **WAIFF punk zine (BWR)** | `prompts/kk-kb/waiff-brazil-2026-keynote-image-prompts.md` | Rafiki → `gemini-3-pro-image-preview` + `--reference reference-collage-v2.png` | No matching style flag | Freeform (## N. titles but not standard batch format) | Reference image is load-bearing; MUST-appear text constraints; **no `styles/zine.md` exists** |
| **GNI cosmic / editorial** | `prompts/kk-kb/gni-cosmic-diagram-style-guide.md` | gpt-image-1 via Streamlit batch UI OR Rafiki | No matching style flag | Style-guide narrative + sample snippets | **No `styles/gni.md` exists**; Streamlit app: `tools/gpt-image-batch-ui/` |
| **GNI sovereignty diagrams** | `prompts/kk-kb/gni-journalism-sovereignty/gpt-image-1-prompts-one-per-line.txt` | gpt-image-1 via Streamlit + HOPECODE prefix | `--style hopecode` as closest | 44-line `.txt` (one prompt per line) | HOPECODE prefix is `hopecode-style-guide.txt`; doesn't use Rafiki batch format |
| **MAC femme / body-compute** | `prompts/kk-kb/femme-prompts-mac-image-repository.md` | Unspecified (gpt-image-1 or Gemini) | No matching style flag | Freeform | Intentional "avoid" clauses need human review before batch; **no `styles/femme.md`** |
| **Wikipedia Five Futures** | `prompts/kk-kb/wikipedia-five-futures-image-prompts-archive.md` | **Archival only** — Midjourney `/imagine` syntax | n/a | Midjourney `/imagine` + freeform master prompts | **Do not batch through Rafiki without prompt rewrite.** Dark themes (resource squeeze, contributor drought) need care flag before any regeneration. |

Additional files:  
- `prompts/kk-kb/websummit-vancouver-kk-zine-image-prompts.md` — HOPECODE/solarpunk; freeform; closest to HOPECODE scenario but Vancouver-specific framing  
- `prompts/kk-kb/indigenomics-diagram-style-guide.md` — distinct Indigenous econographics aesthetic; **no `styles/indigenomics.md`**; small file, review before any generation  
- `prompts/hopecode/` — three example files (concept-mapping, personal-blog, thought-leadership) in Rafiki-batch format; ready to run with `--style hopecode`  
- `prompts/upgrade/training-marketing.md` — Upgrade AI; freeform but small; `--style upgrade`  

---

## 2. Style system gaps

Four production aesthetics used heavily in prompts with no first-class `styles/<name>.md` or CLI flag:

| Gap | Candidate suffix source | Priority |
|---|---|---|
| `styles/zine.md` (WAIFF punk BWR) | Extract from `waiff-brazil-2026-keynote-image-prompts.md` — "Black/white/blood-red, halftone, xerox grain, ransom-note ransom-note type; MUST appear text" pattern | High — large active batch |
| `styles/gni.md` (cosmic editorial) | Extract from `gni-cosmic-diagram-style-guide.md` Principles + Micro-moves sections | Medium — active GNI work |
| `styles/femme.md` (MAC body-compute) | Extract palette/avoid-clause framework from `femme-prompts-mac-image-repository.md` §1 | Medium — needs community review |
| `styles/indigenomics.md` | Extract from `indigenomics-diagram-style-guide.md` | Low — small corpus, community sign-off needed |

Existing styles (`kk`, `hopecode`, `bcai`, `upgrade`) already cover the majority of day-to-day generation.

---

## 3. Overlap & dedupe assessment

**`bcai/bcai-hopecode-visual-prompts.md` (485 lines) vs `kk-kb/hopecode-creative-big-ideas-prompts.md` (241 lines):**  
Not duplicates. Different themes, same HOPECODE visual language:
- `bcai/` = BC+AI ecosystem diagrams: researcher/subject duality, situated knowledge maps, quantum observer, watershed, spore genesis — community *theory* images
- `kk-kb/` = KK personal creative practice: new creative stack, cognitive exoskeleton, daily rhythm, field journals — *personal* and *teaching* images

Recommendation: keep separate, cross-link READMEs more explicitly.

**KB `content/reference/` stale mirrors:**  
`kk-ai-ecosystem/content/reference/` contains old copies of `gni-cosmic-diagram-style-guide.md`, `hopecode-creative-big-ideas-prompts.md`, and the `gni-journalism-sovereignty/` folder. These are stale (per `kk-kb` CLAUDE.md policy). No edits should land there — they should stub-link to Rafiki.

---

## 4. Format heterogeneity

| Format | Files | Rafiki batch? |
|---|---|---|
| `## N. Title` sections with `**Prompt:**` blockquote | `prompts/kk/`, `prompts/bcai/rap-marketing.md`, `prompts/hopecode/*.md`, `prompts/upgrade/training-marketing.md` | ✓ Yes — `parse_image_prompts_md()` |
| Freeform narrative with embedded code blocks | `bcai/bcai-hopecode-visual-prompts.md`, `kk-kb/hopecode-creative-big-ideas-prompts.md`, `kk-kb/websummit-*.md`, `kk-kb/femme-*.md`, `kk-kb/waiff-*.md` | ✗ No — manual copy/paste or reformat needed |
| Style-guide narrative + snippet excerpts | `kk-kb/gni-cosmic-diagram-style-guide.md`, `kk-kb/indigenomics-diagram-style-guide.md` | ✗ No — teaching docs, not batch files |
| One-prompt-per-line `.txt` | `gni-journalism-sovereignty/gpt-image-1-prompts-one-per-line.txt` | ✗ No — feeds gpt-image-1 Streamlit UI |
| Midjourney `/imagine` syntax | `kk-kb/wikipedia-five-futures-image-prompts-archive.md` | ✗ No — archival |

Only ~30% of the corpus is immediately runnable through Rafiki's batch parser today.

---

## 5. Reference image workflow gap

The WAIFF punk zine scenario is the only place a **reference image** (`reference-collage-v2.png`) is mentioned as load-bearing. Rafiki supports `--reference` but:
- No prompt file documents which `--reference` flag to pass
- `reference-collage-v2.png` location is unknown (not in repo)
- The reference image is what keeps BWR discipline across slides

**Action needed:** locate the reference collage, document its path, add a `**Reference:**` metadata field to the WAIFF prompt file.

---

## 6. Proposed phases (pending user sign-off)

**Phase A — fill the style gaps (small, reviewable)**  
Write `styles/zine.md` and `styles/gni.md` by extracting from existing style-guide docs. No prompt files touched. One PR each.

**Phase B — convert high-priority freeform files to Rafiki batch format**  
Start with `waiff-brazil-2026-keynote-image-prompts.md` (slides are already numbered, conversion is mostly mechanical). Preserve originals with `-v1` suffix or a dated archive header.

**Phase C — operator README**  
`docs/image-pipeline-operator.md`: decision tree (what scenario? → which tool? → which flag? → example command). References this analysis and all `styles/` files.

**Phase D — dedupe HOPECODE (optional)**  
After A–C, evaluate whether `bcai/` and `kk-kb/` HOPECODE content should cross-link more explicitly or be partially consolidated. Current recommendation: keep separate, add cross-links.

---

*Next step: review this outline. Approve phases individually; Phase A (style gap files) can start immediately with no risk to existing prompts.*

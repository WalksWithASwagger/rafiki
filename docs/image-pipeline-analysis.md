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

## 2. Style system

Eleven production aesthetics are now registered in `styles/styles.yaml` with markdown guides in `styles/`:

| Style | File | Status | Notes |
|---|---|---|---|
| `zine` | `styles/zine.md` | ✓ Done | BWR xerox-grain; WAIFF batch-ready |
| `gni` | `styles/gni.md` | ✓ Done | Cosmic editorial; GNI coaching sessions |
| `femme` | `styles/femme.md` | ✓ Done — community review required | Abstract body-compute (MAC); enforce avoid-clauses |
| `indigenomics` | `styles/indigenomics.md` | ✓ Done — governance review required | Nation-specific symbols need consent before use |
| `kk` | `styles/kk.md` | ✓ Done | Default; day-to-day editorial |
| `hopecode` | `styles/hopecode.md` | ✓ Done | Solarpunk mycelial |
| `bcai` | `styles/bcai.md` | ✓ Done | BC ecosystem |
| `futureproof-mythic` | `styles/futureproof-mythic.md` | ✓ Done | Surrealist PNW folk-myth; Futureproof worlds and posters |
| `bcai-ecosystem` | `styles/bcai-ecosystem.md` | ✓ Done | BC + AI logo-forward ecosystem assets, credentials, and badges |
| `upgrade` | `styles/upgrade.md` | ✓ Done | Upgrade AI brand |
| `cmvan` | `styles/cmvan.md` | ✓ Done | Creative Mornings Vancouver / Punk Rock AI live-event collage |

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

## 6. Phase completion status

**Phase A — fill the style gaps** ✓ Complete  
All eleven styles registered: `kk`, `hopecode`, `bcai`, `futureproof-mythic`, `bcai-ecosystem`, `upgrade`, `zine`, `gni`, `femme`, `indigenomics`, `cmvan`. Markdown guides in `styles/`. `femme` and `indigenomics` carry community-review caveats.

**Phase B — convert high-priority freeform files to batch format** ✓ Complete  
`prompts/kk-kb/waiff-brazil-2026-keynote-image-prompts.md` is in `## N.` batch format with per-prompt `**Model:**`, `**Style:**`, `**Aspect Ratio:**` metadata. Run with: `python generate.py -f prompts/kk-kb/waiff-brazil-2026-keynote-image-prompts.md -d output/waiff --style zine -m pro`

**Phase C — operator guide** ✓ Complete  
`docs/image-pipeline-operator.md` covers all scenarios, all styles, viewer/library commands, reference image workflow, Streamlit UI, and archival warnings.

**Phase D — dedupe HOPECODE** Open  
`bcai/bcai-hopecode-visual-prompts.md` and `kk-kb/hopecode-creative-big-ideas-prompts.md` remain separate (different themes). Cross-linking via README notes is sufficient for now.

---

*Analysis last updated: 2026-04-25. All critical gaps closed.*

# Alex Samuel ⇄ Rafiki Consolidation Audit (2026-06-28)

Dated snapshot of where the Rafiki ⇄ `alex-samuel` consolidation stands, and the
retirement-readiness gaps that must close before the standalone studio can be retired.
Goal (KK): eventually retire `/Users/kk/Desktop/alex-samuel` and have all Floyo/flowyo.ai
video + audio-production work live in Rafiki.

## What is true today

- **Two repos by design.** `/Users/kk/Desktop/alex-samuel` is the live studio (own GitHub
  repo, ~14 GB, very active — 29 commits in the 2 days before this audit). Rafiki is the
  catalog/ops layer that **indexes it in place** (metadata only) and has its own dry-run
  Replicate pipelines. The combine happened June 3–4 2026 (issues #169–#197, commit
  `846c0c7`); see [PERSONAL-MEDIA-SUITE.md](../../docs/PERSONAL-MEDIA-SUITE.md).

- **Re-sync (2026-06-28).** Re-indexed the live studio (metadata only, no spend). Drift
  since the June-3 cache:

  | Metric | 2026-06-03 | 2026-06-28 |
  |---|---|---|
  | entries | 6,284 | 6,642 |
  | subjects | 2 | 6 |
  | video edits | — | 52 |
  | warnings | 0 | 9 (all "remote-only prediction outputs", benign) |

  The 9 warnings are predictions whose outputs live on Replicate URLs and were never
  downloaded locally — informational, not errors.

## Gap-check: what Rafiki sees vs misses in `andromeda_project/`

Rafiki **does** index andromeda media: 472 entries (448 image, 17 video, 7 audio). What it
**misses**:

1. **Production knowledge (not indexed).** The `.md` production docs that hold the project's
   actual state and creative direction — `HANDOFF.md`, `PROJECT_STATE.md`, `TREATMENT.md`,
   `SHOTLIST.md`, `CHARACTERS.md`, `KEYFRAME_PROMPTS.md`, `MIDJOURNEY_PROMPTS.md`,
   `LYRICS.md`, `FLOYO_GUIDE.md`, `PRODUCTION_LOG.md`, etc. — are invisible to the importer,
   which only ingests media + a fixed manifest set
   (`predictions/trainings/storyboard/scenes/shot_list/*_edl` + style anchors). New manifest
   shapes like `keyframes.json` and `style_lora.json` are also unrecognized as structured
   data.

2. **The active generation tooling (absent from Rafiki).** The Floyo/FloTime pipeline — the
   thing KK is actively building with — is **code that lives only in the studio**:
   `floyo_video.py`, `floyo_run.py`, `floyo_workflows/`, `litegraph_to_api.py`,
   `ingest_clips.py`, plus lip-sync, `faceswap/`, the clip manager, and the
   cast/clips/keyframes viewers. Rafiki has **Replicate** LoRA + `wan-video` generation, but
   **not the Floyo/ComfyUI backend**. This is the core retirement blocker.

## Retirement-readiness map

| Studio capability / content | Rafiki today | Gap to retire |
|---|---|---|
| Portrait → FLUX LoRA training | ✅ `lib/training.py` (Replicate, dry-run) | Parity check vs studio's experiment-suite/tournament flow |
| Replicate video (wan-video) | ✅ `lib/video_jobs.py` | — |
| **Floyo/FloTime video pipeline** | ❌ none | **Port Floyo/ComfyUI backend** (biggest item) |
| **Lip-sync engine** | ❌ none | Port |
| **Faceswap / plates** | ❌ none | Port |
| **Clip manager + ingest** | ❌ none | Port |
| **Audio production** | partial (indexed only) | Define an audio-production surface |
| Cast/clips/keyframes viewers | ❌ (Rafiki has its own portal) | Decide: fold into portal or drop |
| Media corpus (14 GB) | ✅ indexed in place | Decide canonical gitignored home |
| Production `.md` knowledge | ❌ not indexed | Importer extension or knowledge-base route |

## Recommended phased path (gated on KK + proof at each step; nothing deleted now)

1. **Stay synced** — keep re-indexing the studio so Rafiki's catalog stays current
   (recurring, cheap).
2. **Port Floyo/FloTime video** into Rafiki as a first-class provider/pipeline alongside the
   Replicate one — the largest phase; covers lip-sync, faceswap, clip manager incrementally.
3. **Audio-production surface** in Rafiki.
4. **Media home** — settle the canonical gitignored local media root the studio's corpus
   moves to (never into git).
5. **Retirement cutover** — once 2–4 are proven on a real project (e.g. Andromeda),
   archive the standalone repo. Requires explicit KK sign-off + verification; preserve a
   backup.

Tracked as GitHub issues: epic **#268**, with phases **#263** (Floyo/FloTime video pipeline —
core, incl. lip-sync/faceswap/clip-manager), **#264** (audio-production surface), **#265**
(index production knowledge), **#266** (canonical gitignored media home), and **#267**
(retirement cutover + verification, blocked on the rest). The standalone studio remains the
source of truth until the cutover.

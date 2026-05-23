# Rafiki Library And Archive Roadmap

Last reviewed: 2026-05-23

## Goal

Build one local-first place to see, search, review, approve, and reuse every
image Rafiki has generated.

The library should answer four practical questions fast:

- What did Rafiki make?
- Where did it come from?
- Which versions are keepers?
- What can be safely exported, deployed, or deleted?

This is not a hosted gallery or shared cloud asset manager. Generated images,
ratings, registry caches, and approvals stay on the operator's machine unless a
separate export/deploy action is explicitly run.

## Current Foundation

Rafiki already has most of the pieces:

| Area | Files | State |
|---|---|---|
| Run manifests | `output/<project>/run-*/run.json` | Canonical source for generated image file, prompt, model, style, aspect ratio, and run metadata. |
| Project viewers | `lib/renderers/viewer.py`, `generate.py view` | Per-project and per-run review pages. |
| Master library | `lib/renderers/library.py`, `generate.py library`, `generate.py serve` | Cross-project portal with search, filters, ratings, Prompt Studio, and curation/export actions. |
| Ratings | `output/ratings.json`, `lib/server.py` | Star/reject state keyed by `project/run-id/file`. |
| Evaluations | `output/evaluations.json`, `lib/evaluations.py`, `lib/server.py` | Decision, score, use case, rationale, next-step state keyed by `project/run-id/file`. |
| Archive health | `lib/archive_health.py`, `generate.py archive-health` | Read-only report for missing images, malformed manifests, duplicate filenames, sidecar orphans, disk usage, cleanup risk, and advisory cleanup candidates. |
| Approved archive | `lib/archive.py`, `generate.py approve`, `generate.py clean` | Promotes starred assets into `approved/` and supports conservative cleanup. |
| Registry cache | `lib/registry.py`, `generate.py registry` | Local searchable/exportable metadata cache. |
| External roots | `config/extra-outputs*.json` | Lets the portal include generated outputs outside the repo. |
| Curriculum context | `config/curriculum-atlas.json`, `lib/renderers/library_atlas.py` | Teach mode maps archive assets into programs/modules, facilitator notes, critique criteria, concept links, evaluation summaries, and a Cohort Story Mode rail. |

The missing product-level behavior was archive completeness: the registry and
library leaned toward curated/latest assets, not every historical `run-*`.

## Phase 1: Complete Local Archive View

Status: shipped on `main`.

Success criteria:

- `generate.py library` indexes every `run-*` image, not just approved/latest.
- `generate.py serve` shows the same all-runs archive on the portal home page.
- Cards still show prompt, model, style, aspect ratio, project, source run, and
  approval state when available.
- Approved images are recognized from `approved/index.json` by
  `(source_run, original_file)` while keeping the original run image as the
  archive card.
- `generate.py registry index --all-runs` can persist the complete archive
  metadata to `data/asset-registry.json`.
- The default `generate.py registry index` remains curated for downstream CSV,
  Notion, and Canva workflows that should not export every draft.

## Phase 2: Make Review Fast

Status: complete. Source/run/approval filters, keyboard card review, the run
detail panel, and filename warnings are implemented.

Build on the current library UI.

Success criteria:

- Add source/run filters alongside project/model/style/aspect filters. Done.
- Add approval-state filters for `approved`, `unapproved`, `starred`,
  `rejected`, and `unreviewed`. Done.
- Add a run drawer or detail panel with full `run.json` metadata, prompt file,
  generation source, and direct links to the run viewer. Done.
- Add keyboard shortcuts for star/reject/next/previous. Done.
- Add duplicate/similar filename warnings so reruns do not hide prior work.
  Done.

## Phase 3: Make Curation Durable

Turn review decisions into durable archive state.

Success criteria:

- Promote starred images from any historical run into `approved/` from the
  portal, not only the CLI.
- Record human notes, title overrides, tags, and publish/export status in a
  stable sidecar, not only browser local storage. Title overrides, tags,
  export/publish states, and superseded links are now in
  `output/archive-metadata.json`; notes and change requests remain in
  `output/feedback.json`.
- Show whether each archive card has been approved, exported to Canva, exported
  to Notion, deployed, or superseded. Export/publish/superseded badges are now
  visible from archive metadata; successful portal Canva, Notion, and static
  deploy actions now stamp matching source cards automatically. Static deploy
  mapping covers approved viewers, run viewers, and project-root comparison
  viewers; custom viewer directories report why they are unmapped.
- Add a "needs decision" queue for high-value projects where many images remain
  unreviewed. Done as **Review Queue**, which combines unreviewed cards,
  feedback attention, missing evaluation, missing export state, and
  Atlas-unmapped assets.
- Add card-level evaluation and a run-level decision summary. Done in Run
  Detail with decision, score, use case, rationale, next step, badges, and
  per-run counts.
- Add a first prompt/run comparison for reruns and superseded assets. Done in
  Run Detail from local manifests plus `output/archive-metadata.json`
  `superseded_by`; missing targets render as a calm no-data state.

## Phase 4: Make Cleanup Safe

Let Rafiki manage disk growth without losing source-of-truth assets.

Status: read-only health and advisory cleanup reporting are shipped.

Success criteria:

- Add a dry-run cleanup report with image counts, total size, approved coverage,
  and risky deletions. Done as `archive-health --cleanup-report`.
- Keep cleanup conservative: never delete `approved/`, never delete runs with
  unapproved-only images unless explicitly requested.
- Add an archive health command that reports missing files, malformed
  `run.json`, orphaned ratings/feedback/evaluations/metadata, duplicate
  filenames, disk usage, and cleanup risk. Done as
  `python generate.py archive-health`.
- Add optional thumbnail/cache generation so huge archives stay fast without
  mutating originals.

## Phase 5: Make The Archive Useful To Agents

Expose stable, machine-readable archive contracts.

Success criteria:

- Add direct MCP wrappers for archive search, image lookup, approval-state
  updates, and export prep. Next active slice: typed wrappers for registry
  search/export, archive health, viewer rebuild checks, and dry-run-safe export
  helpers.
- Return stable JSON with absolute image paths, source prompts, run metadata,
  approval state, and safe mutation flags.
- Add recipe prompts for common agent jobs: "find unused good assets",
  "compare these runs", "prepare a web gallery shortlist", and "audit stale
  generated assets".

## Build Order

1. Ship the all-runs archive scope in registry and library. Done.
2. Add archive filters/detail panels to the portal. Done.
3. Add duplicate/similar filename warnings. Done.
4. Move review notes/title/tags into durable metadata. Partly done:
   feedback notes live in `output/feedback.json`, and card metadata lives in
   `output/archive-metadata.json`.
5. Add archive health and cleanup reports. Done.
6. Add registry export state from `output/archive-metadata.json`.
7. Add MCP wrappers once the local contracts are stable.

## Non-Goals

- No automatic deletion of generated work.
- No publishing images to a remote service without an explicit export/deploy
  action.
- No committing generated `output/` images to the repo by default.
- No replacing project-specific viewers; the master library should link into
  them.

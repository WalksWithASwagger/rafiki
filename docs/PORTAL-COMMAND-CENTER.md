# Portal Command Center

`python generate.py serve` now serves the TypeScript frontend shell documented
in [Frontend Shell](FRONTEND.md) as the primary `/` and `/library` experience.
Python still runs on the operator's machine, reads the same `output/` archive,
owns `/api/*`, `/output/*`, `/media/*`, and uses the same generation path as
the CLI.

The mode-heavy HTML command center described below is retained as a rollback and
static-rendering surface during the migration. Use `/legacy-suite` for the old
media-suite command center and `/legacy-library` for the old image-only library.
Static generated run/project viewers are still supported for file-open/export
workflows.

## Surfaces

- **Current frontend shell** owns the live `/`, `/library`, `/viewer/*`,
  `/export`, `/registry`, `/health`, and `/spend` routes through the Python
  proxy. It reads normalized archive data from `/api/library-state` and writes
  review state through the existing sidecar APIs.
- **Legacy Review** is the image-first default mode in `/legacy-library`. It
  contains archive filters,
  Review Queue, lineage chips, copy-prompt actions, search, ratings, metadata
  badges, feedback badges, evaluation badges, keyboard review, and the run
  detail panel.
- **Legacy Workflow** stages repeatable artifact chains before generation. The first
  template stages the public keynote visual workflow prompt pack as a dry-run
  batch, then sends the operator into Prompt Studio to inspect the prompt file,
  style, aspect ratio, and project before running.
- **Legacy Generate** contains Prompt Studio and launches single-prompt or Markdown
  batch runs through `/api/regen`. It keeps the latest submitted payload in the
  browser so failed or reset runs can be retried directly or restored into the
  form for review before another attempt.
- **Legacy Curate** exposes local action helpers such as approve starred, Canva export,
  Notion dry run, registry export, and static deploy helper.
- **Legacy Spend** contains local spend, billing imports, usage, and deploy readiness.
- **Legacy Teach** renders the Curriculum Atlas from `config/curriculum-atlas.json`,
  including facilitator notes, discussion prompts, critique rubrics, concept
  links, a compact concept graph, and links from programs/modules back to
  matching archive cards.
- **Spend & Review Ops** summarizes local usage and run manifests:
  - provider-billing imports from `data/billing-imports.json`
  - estimated spend from local manifest amounts plus `config/pricing.json`
  - unpriced image count when manifests and the pricing profile cannot estimate
    a local amount
  - archive image, run, project, model, provider, failed-image, and duration
    totals
  - recent runs with project, run id, state, image count, and local/profile cost
    amounts
  - manual one-off billing entry form for exact charges
  - deployment readiness for local public sharing and static Vercel deploys
- **Run Detail** shows manifest metadata, direct viewer links, filename
  warnings, prompt/run comparisons for superseded assets, durable card
  metadata, per-card feedback, card evaluation, and a run-level decision
  summary.

## Local State

| File | Writer | Purpose |
|---|---|---|
| `output/ratings.json` | `/api/ratings` | Star/reject review state keyed by `project/run/file`. |
| `output/feedback.json` | `/api/feedback` | Per-card notes, change requests, and review statuses. |
| `output/evaluations.json` | `/api/evaluations` | Per-card decision, score, use case, rationale, and next step. |
| `output/archive-metadata.json` | `/api/archive-metadata` | Title overrides, tags, export/publish markers, superseded links, and artifact-chain metadata. |
| `data/usage-log.json` | `lib.usage.log_generation` | Local generation event log. |
| `data/billing-imports.json` | `generate.py billing` and `/api/billing-imports` | Local provider billing ledger. |
| `config/curriculum-atlas.json` | Maintainers | Local program/module/objective/competency scaffold for Teach mode. |
| `config/pricing.json` | Maintainers | Public pricing profile used for local spend estimates. |
| `output/<project>/run-*/run.json` | `lib.batch.run_batch` | Run metadata, prompt details, timings, state, and local cost estimates. |

`output/`, `data/usage-log.json`, and `data/billing-imports.json` are
gitignored. Feedback, ratings, evaluations, archive metadata, and imported
billing stay local unless an operator intentionally exports or deploys them.

## Spend Semantics

The spend tile combines two local signals:

- provider-billing imports when available
- exact local manifest amounts when `cost_estimate.amount` is present
- pricing-profile estimates from `config/pricing.json` when Rafiki can estimate
  the image output price

Images that cannot be estimated locally remain counted as unpriced. Provider
billing exports remain the source of truth for invoices and account-level
spend. See [Spend Accounting](SPEND-ACCOUNTING.md).

## Online Readiness

The portal readiness panel is read-only. It checks:

- whether a static viewer exists when a project/viewer is selected
- whether the Vercel CLI is on `$PATH`
- whether `PORTAL_USERNAME` and `PORTAL_PASSWORD` are set before public binding
- whether Gemini/OpenAI provider keys are present, without echoing secrets

It does not deploy, call provider APIs, or expose secret values.

## Feedback To Rerun Flow

1. Open a card's **Info** panel.
2. Save a status, note, and change request.
3. Use **Stage Rerun** to prefill Prompt Studio from the source prompt plus the
   change request.
4. Use **Dry Run** to validate the revision payload without provider spend.
5. Run the staged prompt when ready; the new output lands in the same
   `output/<project>/run-*` archive.

## Prompt Studio Run Status

Workflow mode can prefill Prompt Studio from a known prompt-pack template. The
staged keynote visual workflow starts as a dry run with `style=hopecode`,
`aspect_ratio=16:9`, and
`prompt_file=examples/keynote-visual-workflow-prompt-pack.md`; operators still
review the payload before spend.

Prompt Studio distinguishes pending, success, failure, and reset states in the
status line. Server and provider errors stay visible as sanitized text so the
operator can retry with the useful failure reason still on screen. **Retry
Last** resubmits the last payload exactly as sent, while **Restage Last** puts
that payload back into the form for edits before a new run.

**Stop Waiting** only aborts the current browser request. It does not claim to
cancel provider work that may already have been handed off, so operators should
check the run folder before spending on a retry.

## Card Evaluation

The **Evaluation** section in the run detail panel writes to
`output/evaluations.json`. It records the card decision (`approve`, `revise`,
`reject`, or `reference`), a 1-5 score, intended use case, rationale, and next
step. Cards show the decision as an evaluation badge, Review Queue treats
missing evaluations as attention-worthy, and Run Detail summarizes decisions
across the current run. When a card matches the Curriculum Atlas, Run Detail
also shows the matched module, objective, matching terms, critique criteria,
and discussion prompts beside the evaluation form.

## Durable Card Metadata

The **Card Metadata** section in the run detail panel writes to
`output/archive-metadata.json`. It can override the display title, add durable
review tags, mark local export/publish states (`canva`, `notion`, `deployed`,
`published`, `superseded`), record a `superseded_by` card key, and carry
artifact-chain fields such as source use case, public source URL, prompt-pack
section, artifact review state, export targets, and downstream uses. The master
library and registry merge that sidecar so provenance stays searchable and
exportable instead of being trapped in browser-local storage.
Successful non-dry-run Canva, Notion, and static deploy portal actions stamp
the matching source cards with `canva`, `notion`, or `deployed` automatically
when Rafiki can map the exported source back to run images. Static deploys map
`approved/` viewers through `approved/index.json`, `run-*` viewers through
their run manifest, and project-root viewers through every `run-*` manifest in
that project. Custom viewer directories that do not map to local run images
return an explicit `unmapped` reason instead of silently stamping nothing.
When a portal action changes archive metadata, Rafiki also refreshes the
curated `data/asset-registry.json` cache so search and registry exports reflect
the new approval/export state without a manual re-index. Dry-runs and failed
actions leave the registry cache untouched.

## Prompt And Run Comparison

When a card's metadata has `superseded_by`, Run Detail renders a read-only
comparison against that local archive card. The first slice compares title,
prompt, model, style, aspect ratio, run id, and archive metadata state from the
already-indexed `output/<project>/run-*/run.json` manifests plus
`output/archive-metadata.json`. If the target key is not present in the current
archive, the panel keeps the original card readable and shows a clear missing
target state instead of guessing. Cards without a linked target show an empty
state that points operators back to the `superseded_by` metadata field.

## Curriculum Atlas

The **Teach** mode reads `config/curriculum-atlas.json`, matches archive cards
against program and module patterns, and shows linked asset counts plus an
unmapped queue. Selecting an atlas module switches back to **Review** mode with
the matching image cards filtered. Module cards can also show facilitator notes,
discussion prompts, critique rubric items, concept links, and evaluation
summaries by decision/score. The current concept graph is static SVG generated
from `concept_links`; it is intentionally lightweight until the Atlas schema
has been used in real review sessions. See [Curriculum Atlas](CURRICULUM-ATLAS.md).

## Review Queue And Lineage

The **Review Queue** filter surfaces cards that are still likely to need human
attention: unrated cards, cards with feedback that requests attention, cards
without evaluation state, cards without export/publish metadata, and cards not
yet mapped into the Curriculum Atlas. Each card also shows compact lineage chips
for source run, archive source/approval state, and next action. **Copy Prompt**
copies the source prompt for quick reuse or review notes.

## HTTP Endpoints

| Endpoint | Method | Behavior |
|---|---|---|
| `/api/library-state` | `GET` | Read-only normalized state for the TypeScript frontend: projects, runs, images, ratings, health, and registry summary. |
| `/api/usage` | `GET` | Read-only local usage and manifest summary. |
| `/api/billing-imports` | `GET` | Read-only imported provider billing summary. |
| `/api/billing-imports` | `POST` | Add one or more local billing rows with `provider`, `model`, `amount`, `currency`, and `note`. |
| `/api/deploy-readiness` | `GET` | Secret-safe readiness checks for static deploy and public portal sharing. |
| `/api/feedback` | `GET` | Return `output/feedback.json` as `{version, items}`. |
| `/api/feedback` | `POST` | Upsert one feedback item using `key`, `status`, `note`, and `change_request`. |
| `/api/evaluations` | `GET` | Return `output/evaluations.json` as `{version, items}`. |
| `/api/evaluations` | `POST` | Upsert one evaluation item using `key`, `decision`, `score`, `use_case`, `rationale`, and `next_step`. |
| `/api/archive-metadata` | `GET` | Return `output/archive-metadata.json` as `{version, items}`. |
| `/api/archive-metadata` | `POST` | Upsert one metadata item using `key`, `title`, `tags`, `states`, `superseded_by`, `source_use_case`, `source_url`, `prompt_pack`, `prompt_pack_section`, `artifact_review_state`, `export_targets`, and `downstream_uses`. |
| `/api/regen` | `POST` | Run Prompt Studio generation or dry run through `lib.batch.run_batch`. |
| `/legacy-suite` | `GET` | Render the old media-suite command center rollback surface. |
| `/legacy-library` | `GET` | Render the old image-only library rollback surface. |

Supported feedback statuses are `needs-change`, `keep`, `maybe`, `blocked`, and
`done`.

Supported evaluation decisions are `approve`, `revise`, `reject`, and
`reference`. Scores are optional integers from 1 to 5.

Supported archive metadata states are `canva`, `notion`, `deployed`,
`published`, and `superseded`.

## Browser Smoke

Run the committed portal smoke before declaring portal/library UX changes done:

```bash
npm run e2e:portal
```

The smoke uses a temporary output root, creates a dry-run archive from
`examples/quickstart-image-prompts.md`, writes local fixture images without
calling a provider, starts `generate.py serve` on a random localhost port, then
checks the new frontend in Chromium. It verifies `/api/library-state`, live
library/run/viewer/export/registry/health/spend routes, rating persistence
through `/api/ratings`, present image loading from `/output/*`, missing-image
placeholders, desktop and mobile overflow, nonblank desktop/mobile screenshot
metrics, and a clean browser console.

The smoke runs its fixture subprocesses with `RAFIKI_DISABLE_EXTRA_OUTPUTS=1`,
so machine-local `config/extra-outputs.local.json` mappings do not affect the
strict archive-count assertions.

Use the explicit visual baseline modes only when reviewing portal layout drift.
They capture named desktop/mobile screenshots and record coarse metrics:
dimensions, luminance, contrast distribution, color variety, and saturation. The
manifest at
`docs/portal-visual-baselines.json` stores reviewed metric ranges, not
pixel-perfect image fixtures.

For human visual review, opt into saved screenshots:

```bash
RAFIKI_E2E_ARTIFACT_DIR=/tmp/rafiki-portal-visuals \
  node scripts/portal-e2e-smoke.mjs --visual-baseline=review
```

The run keeps the existing named PNGs for compatibility:
`portal-desktop-review.png`, `portal-desktop-teach.png`, and
`portal-mobile-review.png`. The JSON output includes
`visual_artifacts.directory`, `visual_artifacts.files`, and `screenshots` with
the metric inputs used by the review. These files are scratch review artifacts;
compare them across runs, but do not commit generated screenshots.

After the screenshots are visually reviewed, refresh the coarse manifest:

```bash
RAFIKI_E2E_ARTIFACT_DIR=/tmp/rafiki-portal-visuals \
  node scripts/portal-e2e-smoke.mjs --visual-baseline=refresh
```

Commit only the reviewed `docs/portal-visual-baselines.json` changes. Then run
the check mode before handing off:

```bash
RAFIKI_E2E_ARTIFACT_DIR=/tmp/rafiki-portal-visuals \
  node scripts/portal-e2e-smoke.mjs --visual-baseline=check
```

Check mode fails with the capture name, metric drift reason, and screenshot
artifact path. Use `node scripts/portal-e2e-smoke.mjs --self-test-baselines` to
exercise baseline parsing and drift failure messaging without launching the
browser.

`RAFIKI_E2E_KEEP_TMP=1 npm run e2e:portal` still keeps the entire disposable
workspace for debugging. For visual modes without `RAFIKI_E2E_ARTIFACT_DIR`,
the named visual artifacts are copied under the kept temp directory at
`visual-artifacts/`; default smoke runs still stay screenshot-free.

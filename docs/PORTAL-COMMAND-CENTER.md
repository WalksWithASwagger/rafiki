# Portal Command Center

`python generate.py serve` turns the master library into Rafiki's local command
center. It still runs on the operator's machine, reads the same `output/`
archive, and uses the same generation path as the CLI.

## Surfaces

- **Review** is the image-first default mode. It contains archive filters,
  Review Queue, lineage chips, copy-prompt actions, search, ratings, metadata
  badges, feedback badges, evaluation badges, keyboard review, and the run
  detail panel.
- **Generate** contains Prompt Studio and launches single-prompt or Markdown
  batch runs through `/api/regen`.
- **Curate** exposes local action helpers such as approve starred, Canva export,
  Notion dry run, registry export, and static deploy helper.
- **Spend** contains local spend, billing imports, usage, and deploy readiness.
- **Teach** renders the Curriculum Atlas from `config/curriculum-atlas.json`,
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
  warnings, durable card metadata, per-card feedback, card evaluation, and a
  run-level decision summary.

## Local State

| File | Writer | Purpose |
|---|---|---|
| `output/ratings.json` | `/api/ratings` | Star/reject review state keyed by `project/run/file`. |
| `output/feedback.json` | `/api/feedback` | Per-card notes, change requests, and review statuses. |
| `output/evaluations.json` | `/api/evaluations` | Per-card decision, score, use case, rationale, and next step. |
| `output/archive-metadata.json` | `/api/archive-metadata` | Title overrides, tags, export/publish markers, and superseded links. |
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

## Card Evaluation

The **Evaluation** section in the run detail panel writes to
`output/evaluations.json`. It records the card decision (`approve`, `revise`,
`reject`, or `reference`), a 1-5 score, intended use case, rationale, and next
step. Cards show the decision as an evaluation badge, Review Queue treats
missing evaluations as attention-worthy, and Run Detail summarizes decisions
across the current run.

## Durable Card Metadata

The **Card Metadata** section in the run detail panel writes to
`output/archive-metadata.json`. It can override the display title, add durable
review tags, mark local export/publish states (`canva`, `notion`, `deployed`,
`published`, `superseded`), and record a `superseded_by` card key. The master
library merges that sidecar when it renders, so the state is visible as card
badges and searchable tags instead of being trapped in browser-local storage.
Successful non-dry-run Canva, Notion, and static deploy portal actions stamp
the matching source cards with `canva`, `notion`, or `deployed` automatically
when Rafiki can map the exported source back to run images.

## Curriculum Atlas

The **Teach** mode reads `config/curriculum-atlas.json`, matches archive cards
against program and module patterns, and shows linked asset counts plus an
unmapped queue. Selecting an atlas module switches back to **Review** mode with
the matching image cards filtered. Module cards can also show facilitator notes,
discussion prompts, critique rubric items, and concept links. The current
concept graph is static SVG generated from `concept_links`; it is intentionally
lightweight until the Atlas schema has been used in real review sessions. See
[Curriculum Atlas](CURRICULUM-ATLAS.md).

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
| `/api/usage` | `GET` | Read-only local usage and manifest summary. |
| `/api/billing-imports` | `GET` | Read-only imported provider billing summary. |
| `/api/billing-imports` | `POST` | Add one or more local billing rows with `provider`, `model`, `amount`, `currency`, and `note`. |
| `/api/deploy-readiness` | `GET` | Secret-safe readiness checks for static deploy and public portal sharing. |
| `/api/feedback` | `GET` | Return `output/feedback.json` as `{version, items}`. |
| `/api/feedback` | `POST` | Upsert one feedback item using `key`, `status`, `note`, and `change_request`. |
| `/api/evaluations` | `GET` | Return `output/evaluations.json` as `{version, items}`. |
| `/api/evaluations` | `POST` | Upsert one evaluation item using `key`, `decision`, `score`, `use_case`, `rationale`, and `next_step`. |
| `/api/archive-metadata` | `GET` | Return `output/archive-metadata.json` as `{version, items}`. |
| `/api/archive-metadata` | `POST` | Upsert one metadata item using `key`, `title`, `tags`, `states`, and `superseded_by`. |
| `/api/regen` | `POST` | Run Prompt Studio generation or dry run through `lib.batch.run_batch`. |

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
checks the portal in Chromium. It verifies the home page, mode navigation,
Teach/Curriculum Atlas rendering, usage and readiness APIs, search, run detail,
metadata save, feedback save, evaluation save, run decision summary, rating
filters, desktop and mobile overflow, and mobile lazy image loading after
scroll. The quality lane also checks concept
graph rendering, Review Queue behavior, lineage/copy affordances, focusable
mode controls, reduced-motion CSS, absence of `transition: all`, and a clean
browser console. Screenshots are not pixel-snapshotted, but the smoke now
records visual baseline metrics for desktop Review, desktop Teach, and mobile
captures, including dimensions, luminance, contrast distribution, color variety,
and saturation, so blank pages and major layout/theme regressions fail without
creating brittle image fixtures.

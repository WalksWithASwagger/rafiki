# Portal Command Center

`python generate.py serve` turns the master library into Rafiki's local command
center. It still runs on the operator's machine, reads the same `output/`
archive, and uses the same generation path as the CLI.

## Surfaces

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
- **Prompt Studio** launches single-prompt or Markdown batch runs through
  `/api/regen`.
- **Curation & Export** exposes local action helpers such as approve starred,
  Canva export, Notion dry run, registry export, and static deploy helper.
- **Run Detail** shows manifest metadata, direct viewer links, filename
  warnings, durable card metadata, and per-card feedback.

## Local State

| File | Writer | Purpose |
|---|---|---|
| `output/ratings.json` | `/api/ratings` | Star/reject review state keyed by `project/run/file`. |
| `output/feedback.json` | `/api/feedback` | Per-card notes, change requests, and review statuses. |
| `output/archive-metadata.json` | `/api/archive-metadata` | Title overrides, tags, export/publish markers, and superseded links. |
| `data/usage-log.json` | `lib.usage.log_generation` | Local generation event log. |
| `data/billing-imports.json` | `generate.py billing` and `/api/billing-imports` | Local provider billing ledger. |
| `config/pricing.json` | Maintainers | Public pricing profile used for local spend estimates. |
| `output/<project>/run-*/run.json` | `lib.batch.run_batch` | Run metadata, prompt details, timings, state, and local cost estimates. |

`output/`, `data/usage-log.json`, and `data/billing-imports.json` are
gitignored. Feedback, ratings, archive metadata, and imported billing stay
local unless an operator intentionally exports or deploys them.

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

## Durable Card Metadata

The **Card Metadata** section in the run detail panel writes to
`output/archive-metadata.json`. It can override the display title, add durable
review tags, mark local export/publish states (`canva`, `notion`, `deployed`,
`published`, `superseded`), and record a `superseded_by` card key. The master
library merges that sidecar when it renders, so the state is visible as card
badges and searchable tags instead of being trapped in browser-local storage.

## HTTP Endpoints

| Endpoint | Method | Behavior |
|---|---|---|
| `/api/usage` | `GET` | Read-only local usage and manifest summary. |
| `/api/billing-imports` | `GET` | Read-only imported provider billing summary. |
| `/api/billing-imports` | `POST` | Add one or more local billing rows with `provider`, `model`, `amount`, `currency`, and `note`. |
| `/api/deploy-readiness` | `GET` | Secret-safe readiness checks for static deploy and public portal sharing. |
| `/api/feedback` | `GET` | Return `output/feedback.json` as `{version, items}`. |
| `/api/feedback` | `POST` | Upsert one feedback item using `key`, `status`, `note`, and `change_request`. |
| `/api/archive-metadata` | `GET` | Return `output/archive-metadata.json` as `{version, items}`. |
| `/api/archive-metadata` | `POST` | Upsert one metadata item using `key`, `title`, `tags`, `states`, and `superseded_by`. |
| `/api/regen` | `POST` | Run Prompt Studio generation or dry run through `lib.batch.run_batch`. |

Supported feedback statuses are `needs-change`, `keep`, `maybe`, `blocked`, and
`done`.

Supported archive metadata states are `canva`, `notion`, `deployed`,
`published`, and `superseded`.

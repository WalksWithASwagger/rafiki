# Portal Command Center

`python generate.py serve` turns the master library into Rafiki's local command
center. It still runs on the operator's machine, reads the same `output/`
archive, and uses the same generation path as the CLI.

## Surfaces

- **Spend & Review Ops** summarizes local usage and run manifests:
  - known spend from `cost_estimate.amount` values already written to run
    manifests
  - unestimated image count when manifests do not contain local amounts
  - archive image, run, project, model, provider, failed-image, and duration
    totals
  - recent runs with project, run id, state, image count, and local cost amount
- **Prompt Studio** launches single-prompt or Markdown batch runs through
  `/api/regen`.
- **Curation & Export** exposes local action helpers such as approve starred,
  Canva export, Notion dry run, registry export, and static deploy helper.
- **Run Detail** shows manifest metadata, direct viewer links, filename
  warnings, and per-card feedback.

## Local State

| File | Writer | Purpose |
|---|---|---|
| `output/ratings.json` | `/api/ratings` | Star/reject review state keyed by `project/run/file`. |
| `output/feedback.json` | `/api/feedback` | Per-card notes, change requests, and review statuses. |
| `data/usage-log.json` | `lib.usage.log_generation` | Local generation event log. |
| `output/<project>/run-*/run.json` | `lib.batch.run_batch` | Run metadata, prompt details, timings, state, and local cost estimates. |

`output/` and `data/usage-log.json` are gitignored. Feedback and ratings stay
local unless an operator intentionally exports or deploys them.

## Spend Semantics

The portal does not bundle provider pricing. The spend tile only totals local
manifest amounts when `cost_estimate.amount` is present. Images without a local
amount remain counted as unestimated. Provider billing exports remain the
source of truth for invoices and account-level spend.

## Feedback To Rerun Flow

1. Open a card's **Info** panel.
2. Save a status, note, and change request.
3. Use **Stage Rerun** to prefill Prompt Studio from the source prompt plus the
   change request.
4. Use **Dry Run** to validate the revision payload without provider spend.
5. Run the staged prompt when ready; the new output lands in the same
   `output/<project>/run-*` archive.

## HTTP Endpoints

| Endpoint | Method | Behavior |
|---|---|---|
| `/api/usage` | `GET` | Read-only local usage and manifest summary. |
| `/api/feedback` | `GET` | Return `output/feedback.json` as `{version, items}`. |
| `/api/feedback` | `POST` | Upsert one feedback item using `key`, `status`, `note`, and `change_request`. |
| `/api/regen` | `POST` | Run Prompt Studio generation or dry run through `lib.batch.run_batch`. |

Supported feedback statuses are `needs-change`, `keep`, `maybe`, `blocked`, and
`done`.

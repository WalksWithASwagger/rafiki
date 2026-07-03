# Generate UI Next Work Plan - July 2026

## Summary

Generate UI V1 gives Rafiki a first-class React `/generate` route backed by
Python's existing `run_batch` path. The first stabilization pass shipped on
July 3, 2026; the next milestone should deepen prompt/reference workflows before
adding video, uploads, LoRA training, or a background job system.

## Current Baseline

- `/generate` supports single prompt, inline batch, and Markdown prompt-file
  preview modes.
- Runs default to `dry_run=true`; real provider execution requires an explicit
  confirmation checkbox plus a matching dry-run manifest for the current draft.
- Recent dry-runs and provider attempts are recorded in browser-local history
  with links back to the run viewer, project viewer, library run, and manifest.
- Library-picked references submit `/output/*` URLs, media references submit
  `/media/*` URLs, and Python resolves those through the existing local safety
  boundaries.
- Backend support is intentionally small: `GET /api/generate-options`,
  `POST /api/prompt-preview`, and backward-compatible `POST /api/regen`.
- Generate execution is synchronous in V1/V1.5: the React submit action waits on
  one `/api/regen` request, and Python handles that request by running
  `run_batch` directly before returning success, partial success, or an error.

## Shipped: Generation Workflow Stabilization

- PR #290 added an operator-friendly run history panel for recent `/generate`
  attempts, with links to the run viewer, project viewer, library project, and
  manifest.
- PR #290 made real-run execution more explicit by showing estimated provider,
  model, prompt count, reference count, and dry-run manifest path before
  enabling `dry_run=false`.
- PR #291 added the July 3 issue-crush audit and recommended the next issue
  order.

## Next Milestone: Prompt And Reference Depth

- Add per-row inline batch overrides for model, style, aspect ratio, and
  quality, matching the existing Markdown prompt-file override contract.
- Improve reference selection with filters for starred images, current project,
  latest runs, and media kind; keep v2 picker state local and do not add binary
  upload storage yet.
- Add empty, loading, and error states for `/generate` that clearly separate UI
  validation failures from provider or filesystem failures.

## Follow-On Milestone: Jobs And Cancellation Clarity

Keep provider work synchronous in V1/V1.5. The `/generate` screen may let an
operator stop waiting in the browser, but that action only aborts the active
browser request and unlocks the UI. It does not cancel Python work already
running inside `/api/regen`, revoke provider work already handed off, or prove
that no files will still be written to the local run folder. Operators should
check the run folder or library state before spending on a retry after stopping
the wait.

Future background execution requires a Python-owned local job ledger before the
UI can honestly present durable job state. The ledger direction is:

- Python is the sole writer for job records, provider identifiers, status
  transitions, terminal states, timestamps, errors, and output paths.
- React remains a reader/operator shell that displays job state and submits
  explicit operator intents, such as retry or cancel request.
- Browser-local Generate history stays a convenience history, not the
  authoritative job record.
- True cancellation, provider polling, resumable runs, and provider-state
  persistence remain follow-up implementation work for a maintainer-approved
  design.

## Verification Targets

- Extend unit tests for per-row inline overrides and reference-role handling.
- Extend `npm run e2e:portal` to cover real-run confirmation and matching
  dry-run refusal paths without calling providers.
- Keep desktop and mobile checks for `/generate` horizontal overflow and
  nonblank screenshots.
- Continue running `npm --prefix frontend ci`, `npm run frontend:verify`,
  `python3 -m pytest tests/test_server_endpoints.py tests/test_server_auth.py -q`,
  `npm run e2e:portal`, `npm run verify`, and `git diff --check` for Generate
  UI changes.

## Deferred

- Upload storage, video generation, LoRA training, Floyo orchestration, and
  provider job queues remain out of scope until image generation workflows are
  stable.
- Packaging `frontend/` into the npm tarball remains a separate release-track
  follow-up.

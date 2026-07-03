# Generate UI Next Work Plan - July 2026

## Summary

Generate UI V1 gives Rafiki a first-class React `/generate` route backed by
Python's existing `run_batch` path. The next milestone should stabilize real
operator use before adding video, uploads, LoRA training, or a background job
system.

## Current Baseline

- `/generate` supports single prompt, inline batch, and Markdown prompt-file
  preview modes.
- Runs default to `dry_run=true`; real provider execution requires an explicit
  confirmation checkbox.
- Library-picked references submit `/output/*` URLs, media references submit
  `/media/*` URLs, and Python resolves those through the existing local safety
  boundaries.
- Backend support is intentionally small: `GET /api/generate-options`,
  `POST /api/prompt-preview`, and backward-compatible `POST /api/regen`.

## Next Milestone: Generation Workflow Stabilization

- In progress: add an operator-friendly run history panel for recent `/generate` attempts,
  with links to the run viewer, project viewer, library project, and manifest.
- In progress: make real-run execution more explicit by showing estimated provider, model,
  prompt count, reference count, and dry-run manifest path before enabling
  `dry_run=false`.
- Add per-row inline batch overrides for model, style, aspect ratio, and
  quality, matching the existing Markdown prompt-file override contract.
- Improve reference selection with filters for starred images, current project,
  latest runs, and media kind; keep v2 picker state local and do not add binary
  upload storage yet.
- Add empty, loading, and error states for `/generate` that clearly separate UI
  validation failures from provider or filesystem failures.

## Follow-On Milestone: Jobs And Cancellation Clarity

- Keep provider work synchronous in V1/V1.5; document that "Stop waiting" only
  aborts the browser wait.
- Design a local job ledger before adding true background cancellation,
  resumable runs, or provider polling.
- If a job ledger is introduced, make Python the only writer and keep React as
  a reader/operator shell.

## Verification Targets

- Extend unit tests for per-row inline overrides and reference-role handling.
- Extend `npm run e2e:portal` to cover a real-run confirmation refusal path
  without calling providers.
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

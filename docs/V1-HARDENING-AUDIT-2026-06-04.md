# Rafiki V1 Hardening Audit And Workplan - 2026-06-04

This audit covers the personal media suite after the foundation commit
`846c0c7 Add personal media suite foundation` and the first V1 hardening slice.
Rafiki remains the product home. `/Users/kk/Desktop/alex-samuel` remains an
external indexed media root, not copied content.

## Verified State

- The local Alex registry cache currently has 6,284 entries, 2 subjects,
  1 style profile, and 49 video edits.
- Indexed media kinds include images, videos, audio, prediction manifests,
  prompt suites, model versions, training manifests, evaluations, datasets,
  storyboards, and shot lists.
- The suite route `/` loads the multimedia portal. `/library` remains the
  legacy image-only route.
- The Library now defaults to reviewable media and exposes an All mode for the
  full registry.
- MP4 serving supports byte ranges for scrubbing.
- Video selections persist in ignored local state.
- Replicate image, training, and video job paths are dry-run safe by default.
- Local root config, registry cache, jobs, selections, and generated state stay
  ignored by git.

## Audit Findings

### Registry And Importer

What is solid:

- The multimedia registry keeps normalized metadata in Rafiki while preserving
  external file references.
- The Alex importer covers portrait predictions, trainings, prompt suites,
  benchmark/evaluation outputs, video storyboards, shot lists, clip predictions,
  rendered edits, and style anchors.
- The importer now emits aggregate warnings for malformed prediction rows,
  missing local prediction outputs, remote-only outputs, malformed training
  runs, and training manifests without subject profiles.
- Incremental indexing now has root fingerprints and cache-reuse behavior.

Gaps:

- Existing ignored local caches created before this hardening pass need one
  non-dry index refresh before `root_fingerprints` are persisted.
- The current root fingerprint is intentionally cheap. It avoids full rescans
  for unchanged roots, but it is not yet a deep content hash of every nested
  manifest.
- Importer warnings are returned by API/CLI, but the portal does not yet show a
  clear warning drawer or stale-reference report.
- Real-shape fixture coverage should be expanded for Alexandra benchmark and
  cross-version outputs, Kris wave counts, song1/song2/time-airport manifests,
  and style-anchor extraction.

### Portal And Library

What is solid:

- The suite is still a simple localhost Python server with modular static
  HTML/CSS/JS.
- Library, Subjects, Studio, Jobs, Styles, and Video Lab all exist in one local
  command center.
- Reviewable Library mode prevents datasets and training archives from crowding
  out useful image/video cards.
- All mode still exposes the complete indexed library.

Gaps:

- Filters are not durable across reloads or shareable in the URL.
- Subject pages are still summary cards, not real subject workspaces.
- Library filters do not yet cover root, review state, provider/model, or video
  selection state.
- Portal warnings are not prominent enough for stale docs, missing references,
  or malformed imported metadata.
- The portal smoke coverage is still lighter than the server/unit coverage.

### Jobs And Providers

What is solid:

- Provider execution defaults to dry-run.
- Dry-run LoRA training and video generation write manifests and job records.
- Tests prove dry-runs do not require provider tokens.
- Job records capture failed provider responses.

Gaps:

- Job records are not yet resumable provider workflows with polling, provider
  URLs, downloads, and failure recovery.
- The portal does not yet require explicit spend confirmation before execute
  calls.
- Cost/count previews are still basic and should be surfaced before training or
  video generation.
- Execute-mode behavior should stay opt-in until job lifecycle coverage is much
  stronger.

### Video Lab

What is solid:

- External MP4 playback works through range-capable local routes.
- Clip selections persist locally.
- Video generation and assembly commands write local manifests.
- Video edits from Alex are indexed and searchable.

Gaps:

- EDL import/export is not yet connected to indexed selections.
- Edit validation needs clearer missing-clip, missing-audio, and duration
  mismatch reporting.
- Assembly tests currently validate dry-run behavior. Tiny ffmpeg fixture tests
  should cover optional render success and failure paths.
- The editor is still a curation lab, not a full timeline tool.

### CLI, MCP, And Ops

What is solid:

- CLI surfaces exist for media index/search/export, Alex import, subjects,
  LoRA training, video generation, video assembly, and style anchors.
- MCP exposes the useful read and job surfaces from the suite foundation.
- `npm run verify` is a good broad gate for this codebase.

Gaps:

- MCP should mirror the hardened search/filter and job status semantics after
  the CLI stabilizes.
- The local acceptance script should include portal browser/API sanity and MP4
  `206` verification as a named command.
- The workplan should continue to avoid paid provider execution until dry-run,
  cost preview, confirmation, and failure-state tests are boring.

## Workplan

### P0 - Importer And Registry Confidence

Goal: make indexing reliable enough that the suite can trust its own library.

- Add fixtures for Alexandra benchmark/cross-version outputs.
- Add fixtures for Kris wave counts and expected prediction collections.
- Add fixtures for song1, song2, and time-airport video manifests.
- Add style-anchor extraction fixtures for the Hollywood style shape.
- Add a warning report endpoint and a portal warning drawer.
- Run one non-dry local index after merge to persist `root_fingerprints` in the
  ignored local cache.

Acceptance:

- Fixture tests fail on malformed or missing real-shape metadata.
- `python generate.py media index --incremental` reuses unchanged roots after
  the first refreshed cache.
- Portal shows warnings without leaking secrets or copying external media.

### P1 - Library And Subject Workflows

Goal: make the portal useful for repeated review sessions, not just indexing.

- Persist Library filters in the URL and local storage.
- Add filters for root, subject, project, kind, collection, review state,
  provider/model, and video selection state.
- Upgrade Subject pages with prompt suites, model versions, album/training
  roots, top outputs, and quick links into Library and Video Lab.
- Keep `/library` as image-only legacy and `/` as the suite command center.

Acceptance:

- Browser smoke tests cover Reviewable versus All, durable filters, Subject
  detail, and quick links.
- Dataset-heavy records remain available but never dominate default review.

### P2 - Job Lifecycle And Spend Controls

Goal: make provider jobs safe, resumable, and inspectable before execute mode is
  encouraged.

- Expand job records with provider URLs, polling status, output download state,
  retry/failure details, and last-checked timestamps.
- Add explicit portal confirmations before any execute provider call.
- Add cost/count previews for LoRA training and video generation.
- Add provider-polling tests and failure-capture tests around mocked Replicate
  responses.

Acceptance:

- Dry-run never calls the network.
- Execute is impossible from the portal without an explicit confirmation.
- Failed provider responses are visible in Jobs and stored in ignored job state.

### P3 - Video Lab And Assembly

Goal: turn Video Lab from clip review into reliable edit preparation.

- Add EDL import/export from indexed selections.
- Validate edit manifests for missing clips, missing audio, and duration
  mismatches.
- Add tiny fixture-based ffmpeg success/failure tests, with full rendering
  optional.
- Keep the richer timeline/editor UI out of scope until curation and assembly
  are dependable.

Acceptance:

- Selected clips can round-trip through an edit manifest.
- Missing media blocks render with clear local paths.
- Optional ffmpeg tests prove both success and failure reporting.

### P4 - MCP And Acceptance Automation

Goal: make the suite easy for agents to operate without touching private media.

- Mirror hardened media search/filter, subject lookup, style lookup, job list,
  and warning report through MCP.
- Add a named local acceptance command that checks registry counts, portal API,
  byte-range media response, dry-run jobs, and no copied Alex media.
- Keep generated/private assets and provider state ignored.

Acceptance:

- `npm run verify` remains green.
- The acceptance command proves representative media render through local
  routes and external files stay in place.
- Agents can inspect and report suite state without reading secrets or copying
  private media.

## Verification Cadence

- Run focused tests before each hardening change.
- Run `npm run verify` before every commit.
- After portal changes, open `http://localhost:7433/` and verify Library counts,
  Subject cards, Styles, Jobs, Video Lab playback, and MP4 `206` range response.
- Keep provider execute testing mocked unless the user explicitly approves paid
  execution with destination and count.

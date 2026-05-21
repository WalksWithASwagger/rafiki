# Rafiki Product Audit (2026-05-18)

## Scope

This audit is grounded in `main` at `ed10505` after the portal archive,
feedback, spend, billing-import, deploy-readiness, and archive-metadata slices
were merged.

Checked:

- tracked README and docs
- local portal/server/rendering code
- CLI, MCP, packaging, and verification scripts
- GitHub issue and PR queue
- repo hygiene signals from the active checkouts

Excluded:

- generated `output/` images and local billing/usage state
- provider API calls, because no provider keys are set in this shell
- destructive cleanup of the nested `/Users/kk/Code/rafiki/rafiki` scratch clone

## Verification Snapshot

Commands run during this audit:

- `npm run docs:check` - passed; 24 Markdown files checked
- `npm run pack:check` - passed; 81 files in the package dry run
- `PATH=/Users/kk/Code/rafiki/.venv/bin:$PATH node index.js --doctor` - passed with 0 critical issues and expected provider-key warnings after temporarily linking the existing `node_modules`
- `/Users/kk/Code/rafiki/.venv/bin/python generate.py --list-styles` - passed; 11 registered styles
- `PATH=/Users/kk/Code/rafiki/.venv/bin:$PATH npm test` - passed; 193 tests, 1 dependency deprecation warning

## Current Read

Rafiki is now a coherent local-first creative operations system, not just an
image-generation script. The current product has four reinforcing surfaces:

- CLI generation, batch runs, viewers, exports, deploy helpers, billing imports,
  and scheduled regeneration through `generate.py`.
- Node package entrypoints through `index.js`, with packaging controlled by the
  `package.json` file allowlist.
- MCP access through typed wrappers plus a constrained `generate.py` bridge.
- A local portal that now supports all-runs archive browsing, keyboard review,
  run detail, feedback, rerun staging, spend summaries, provider billing import,
  deploy readiness, and durable card metadata.

The core docs are mostly current. The one tracked stale agent doc found in this
audit was `.claude/skills/rafiki.md`, which still referenced an old model
nickname and a removed launcher path. This audit fixes that skill so future
agents use the current `npx rafiki` path and live style registry.

## Findings

### 1. Portal Product Surface Is Now The Center Of Gravity

The portal is where review, spend, feedback, rerun staging, and durable
metadata come together. The next product work should deepen that surface rather
than creating more one-off viewers or side workflows.

Impact:

- Operators can now see and curate the full archive.
- Remaining gaps are about lifecycle state, health, and action feedback, not
  basic browsing.

### 2. Export State Exists, But Export Actions Do Not Stamp It Yet

`output/archive-metadata.json` can represent `canva`, `notion`, `deployed`,
`published`, and `superseded` states. Portal actions can run Canva, Notion,
registry export, and deploy helpers. Those two systems are adjacent but not yet
connected.

Recommended next slice:

- When a portal export/deploy action succeeds, stamp matching card keys into
  archive metadata.
- Rebuild the library or refresh visible card badges after the stamp.
- Add tests around the action result -> metadata write contract.

### 3. Archive Health And Cleanup Need A Report Before More Automation

The archive is now broad enough that cleanup should start with reports, not
deletion. The repo already has conservative `clean`, filename warnings, ratings,
feedback, approved indexes, and all-runs registry collection.

Recommended next slice:

- Add `generate.py archive-health` or `generate.py clean --report`.
- Report missing files, malformed `run.json`, orphaned ratings/feedback/
  evaluations/metadata, approved entries whose source run is gone, duplicate
  filenames, disk usage, and deletion risk.
- Keep actual deletion opt-in and separate from the report.

### 4. Agent And CLI Smoke Coverage Is The Main Reliability Gap

The test suite is strong and currently at 193 tests, but the roadmap still calls
out cross-surface smoke coverage. This matters because the same user workflow
can enter through Python CLI, Node CLI, portal HTTP, MCP, or a local agent.

Recommended next slice:

- Add a no-provider-cost smoke path for `generate.py --dry-run --json`.
- Add a Node CLI dry-run smoke.
- Add an MCP stdio smoke that lists tools and calls `rafiki_status`.
- Add a portal dry-run request test for `/api/regen`.

### 5. `generate.py` Is Carrying Too Much Dispatcher Weight

The codebase already has good library modules, but `generate.py` remains the
large command dispatcher. The roadmap says to split subcommands when touched.
The newest billing/deploy/archive additions make that more important.

Recommended approach:

- Do not rewrite the dispatcher in one sweep.
- Move the next touched command into a `lib/commands/` module with focused
  parser and handler tests.
- Use billing or archive-health as the first extraction candidate because those
  commands are self-contained.

### 6. GitHub Queue Is Ready, But Sequencing Matters

Current open queue:

- PR #93, `Add communities graphics prompt kit`, is mergeable and
  review-ready but was created before the portal-product merge wave.
- PR #92 remains `needs-human`.
- Issues #81 through #88 are review-ready BC+AI communities content issues.
- Issue #69 remains the correct human-gated Notion signed-upload verification
  blocker.

Recommended sequence:

1. Rebase or refresh PR #93 against current `main`, rerun CI, then merge if it
   remains clean.
2. Let PR #93 close #81 if the prompt kit acceptance criteria are still met.
3. Generate the #82 through #88 community images in bounded batches after the
   prompt kit lands.
4. Keep #69 open until a real Notion workspace verifies the signed upload path.
5. Review #92 separately because it is marked `needs-human`.

### 7. Workspace Hygiene Is Mostly Good, With One Local Scratch Clone To Preserve

The clean audit worktree is synced with `origin/main`. The separate
`/Users/kk/Code/rafiki` checkout still has a nested untracked `rafiki/` clone,
plus local agent skill files and the older documentation-audit note. That nested
clone can confuse broad searches, but it should not be deleted without explicit
confirmation.

This audit adds `/rafiki/` to `.gitignore` so that scratch clone stops showing
up as repo work when this cleanup lands.

## Roadmap From Here

### Immediate Closeout

1. Merge or refresh PR #93.
2. Decide whether PR #92 is still useful or should be closed/reworked.
3. Run the BC+AI communities generation queue (#82 through #88) after the prompt
   kit is on `main`.

### Next Product Sprint

1. Stamp successful portal exports/deploys into `output/archive-metadata.json`.
2. Add archive health and cleanup reports.
3. Add direct MCP wrappers for archive search, metadata update, and export prep.
4. Add no-cost smoke tests across Python CLI, Node CLI, portal, and MCP.

### Reliability And Maintainability

1. Extract touched `generate.py` subcommands into command modules.
2. Strengthen `run.json` manifest schema and tests for provider, model, style,
   prompt file, references, timings, errors, and cost estimate fields.
3. Make registry exports include archive metadata state.
4. Expand `doctor` so missing local `node_modules` in worktrees is diagnosed
   with the same clarity as missing provider keys.

### Later Bets

1. Add prompt diffing between runs.
2. Improve long-running portal generation progress, cancellation, and retry.
3. Add self-contained export presets for small review files versus full-quality
   archives.
4. Consider SQLite only after JSON registry and metadata limits become concrete.

## Bottom Line

The roadmap should shift from "build the portal" to "make the portal the
trusted operating console." The highest-leverage next work is lifecycle state:
export stamping, archive health, and no-cost cross-surface verification.

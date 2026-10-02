# Agent Operating Guide

This file defines how coding agents should work in this repository.

## Engineering Loop

Follow this loop:

Audit → Prioritize → Plan → Implement → Verify → Report

Do not skip directly from a vague request to implementation.

## Core Principles

* Evidence over guesses
* Simplicity over ceremony
* Small changes over heroic rewrites
* Existing primitives over new abstractions
* Tests and evals over confidence theater
* Preservation before cleanup
* Clear ownership and handoffs
* Documentation must describe reality

## Repository Entry

When beginning work:

* Inspect the current branch
* Inspect the working tree
* Check the upstream relationship
* Identify uncommitted and untracked work
* Review relevant issues and PRs
* Locate project entry points
* Locate tests, evals, CI, and documentation
* Identify the relevant source of truth

Do not modify files during initial orientation unless the task is trivial and explicitly authorized.

## Planning

Before non-trivial implementation, create a focused work packet containing:

* Goal
* Why it matters
* Evidence
* Scope
* Non-goals
* Likely files
* Proposed approach
* Behavior to preserve
* Tests and evals
* Risks
* Validation commands
* Definition of done

Ask for approval before implementation when the work is risky, broad, ambiguous, destructive, or architecture-changing.

## Implementation

* Make the smallest useful change.
* Keep the diff focused.
* Do not fix unrelated issues.
* Do not silently expand scope.
* Preserve public behavior unless change is explicitly required.
* Add tests for important behavior.
* Add regression tests for bugs.
* Add evals when AI or agent behavior changes.
* Update docs when user or developer behavior changes.

## Git And Worktree Safety

Do not perform destructive Git operations without explicit approval.

Never assume a branch, worktree, stash, or untracked file is disposable.

Before deleting or consolidating work:

* Inventory it
* Determine its purpose
* Compare it with `main`
* Identify duplicate or superseding work
* Preserve anything uncertain
* Verify tests and CI
* Require human approval

## Issue And PR Discipline

* Reuse existing issues when possible.
* Do not create duplicate issues.
* One focused issue should usually map to one focused PR.
* Split broad or unrelated work.
* Use research or decision issues when requirements are unresolved.
* Do not open a PR until implementation and validation are complete.

Every implementation issue should contain:

* Summary
* Why it matters
* Scope
* Non-goals
* Acceptance criteria
* Tests
* Evals, when relevant
* Dependencies
* Risks
* Definition of done

## Code Quality

Look for:

* Duplicate logic
* Dead code
* Unused imports and dependencies
* Debug output
* Temporary files
* Commented-out code
* Stale feature flags
* Misleading names
* Oversized modules
* Fragile scripts
* Unnecessary abstraction layers

Do not declare code dead based only on appearance.

Check imports, dynamic registration, configuration, tests, builds, scripts, and runtime entry points first.

Refactoring must unlock something concrete.

## Skills, Workflows, And Automations

Use this model:

* Skills define reusable capabilities.
* Workflows coordinate skills.
* Automations trigger workflows.
* Issues define approved work.
* PRs deliver focused implementation.

Every active skill, workflow, or automation should have:

* A clear purpose
* A clear trigger
* Clear inputs
* Clear outputs
* A clear owner
* A safety boundary
* A validation method
* A known consumer

Anything lacking these should be fixed, merged, paused, archived, replaced, or removed after approval.

## Configuration And Secrets

When Varlock is present:

* Treat its schema as the configuration contract.
* Prefer Varlock-based runtime and validation paths.
* Identify legacy configuration paths that bypass it.
* Never reveal resolved secrets.
* Never commit secret-bearing files.
* Report suspected leaks without reproducing values.

## Documentation

Documentation is part of the implementation.

Keep accurate:

* README files
* Setup instructions
* Architecture docs
* Changelogs
* Configuration docs
* Skill and workflow docs
* Automation docs
* Testing and eval instructions

Do not invent changelog history.

## Verification

Run relevant checks after changes.

Report:

* Commands run
* Results
* Commands not run
* Reason they were not run
* Remaining uncertainty

A task is not complete merely because code was written.

## End Of Session

Leave the repository easier to resume.

Report:

* Current branch and working state
* Work completed
* Files changed
* Validation results
* Remaining risks
* Follow-up work
* Exact recommended next step


## Secrets (Varlock)

- Local secrets for agent/tool use live in gitignored plaintext `.env` / `.env.local` (mode `0600`). Varlock owns `.env.schema` + `load`/`run` injection — not macOS Keychain or Touch ID.
- Agents inspect with `varlock load --agent` and run tools with `varlock run --inject vars -- <command>`.
- Never `cat` `.env` / `.env.local`, never `printenv` secrets, never `varlock reveal` in agent sessions.
- Canonical contract docs: `/Users/kk/Code/kk-kb/docs/AGENT-SECRETS-VARLOCK.md`.

---

## This repository (rafiki)

Rafiki is a local-first image-generation and review tool. One checkout. Node
CLI (`index.js`, bins `rafiki` / `image-gen`), Python engine (`generate.py`),
TypeScript portal under `frontend/`, MCP server (`mcp_server.py`). No hosted
service.

There is no `pyproject.toml`. Python install and test config live in
`requirements.txt` (runtime), `requirements-dev.txt` (local/dev),
`requirements-ci.txt` (hashed CPython 3.11 Linux lock for CI), `pytest.ini`,
and `ruff.toml`.

### Layout

Verified against the tree on 2026-09-28. Longer map: `docs/FOLDER-LAYOUT.md`
(known stale in places — it still omits `frontend/` and several `lib/`
modules). Trust the tree and this section over that file until #459 lands.

- `index.js` — Node CLI and HTML-to-PNG renderer
- `generate.py` — Python dispatcher (generate, view, library, serve, archive,
  registry, media, video, floyo, and the other subcommands listed below)
- `generate-presentation-viewer.py` — JSON-driven deck viewer
- `mcp_server.py` — MCP tools
- `lib/` — Python library (providers, portal, archive, exporters, jobs)
- `frontend/` — TypeScript portal shell. Not in the public npm package.
- `styles/` — `styles.yaml` plus markdown guides. Live list:
  `npx rafiki --list-styles`
- `examples/` — public prompt fixtures
- `docs/` — operating docs. Start at `docs/INDEX.md`
- `tests/` — pytest, including `tests/agentic/`
- `scripts/` — verify helpers and the agentic pipeline
- `.github/workflows/` — CI and agentic gates
- `agentic/contract.json` — delivery contract (labels, limits, verify cmds)
- `.env.schema` / `.env.example` — env contract. Values stay untracked.
- `CHANGELOG.md` — merged-PR history since the last GitHub release

### Commands

From root `package.json`. Do not invent extras.

- `npm ci` and `npm --prefix frontend ci` — install
- `npm run doctor` — local readiness (`npx rafiki --doctor`)
- `npm test` / `npm run test:python` — pytest via `scripts/run-pytest.js`
- `npm run lint` — `ruff check .`
- `npm run verify` — lint, tests, `frontend:verify`, `e2e:portal`,
  `docs:check`, `public:check`, `smoke:dry-run`, `pack:check`, doctor
- `npm run verify:security` — npm audit + `pip_audit` on the CI lock
  (needs network)
- `npm run frontend:dev|build|typecheck|lint|test|verify`
- `npm run env:validate|audit|scan|smoke` — Varlock. No 1Password.
- `npm run lock:python-ci` — refresh the hashed Python CI lock
- `npm run e2e:portal`, `smoke:dry-run`, `accept:video-lab`
- `npm run pack:check`, `docs:check`, `public:check`, `workspace:hygiene`

`generate.py` subcommands (from the dispatcher in `generate.py`): `view`,
`library`, `serve`, `link-projects`, `approve`, `canva-export`, `clean`,
`deploy`, `notion-export`, `regen`, `registry`, `billing`, `archive-health`,
`archive-repair`, `archive-thumbnails`, `social-expand`, `media`, `import`,
`subjects`, `train`, `video`, `floyo`, `keyframes`, `style`.

App runtime: Node 22.13+ and npm 10+. Python 3.11+ locally. CI pins Node
22.13 and Python 3.11.

Default agent verification from `agentic/contract.json`: `npm test`,
`npm run pack:check`, `npm run doctor`.

### CI

Workflows under `.github/workflows/`. Do not edit them from a docs PR.

- `ci.yml` — job `test` (Node 22.13, Python 3.11, hashed
  `requirements-ci.txt`, lock drift check, `npm run verify:security`,
  `npm run verify`) and job `secret-scan` (gitleaks). Runs on `main`
  pushes and every PR.
- `codeql.yml` — CodeQL for `javascript-typescript` and `python`
- `dependency-review.yml` — PR dependency review, fails on high severity
- `agentic-issue-quality.yml` — lints issues labeled `agent:ready`
- `agentic-dev-loop.yml` — dispatched agent loop
- `agentic-traceability.yml` — `policy` check for `codex/issue-*` PRs
- `agentic-pr-review.yml` — advisory acceptance review for those PRs

Recommended required checks in `.github/branch-protection.md`: `test`,
`secret-scan`, `policy`. Applying GitHub protection settings is a
maintainer action, not an agent task. CodeQL and Dependency Review start
as reporting checks. `policy` only runs for `codex/issue-*` head branches.

### Secrets

- Env contract: `.env.schema`, `.env.example`, committed docs, code refs, sanitized fixtures only.
- Never read/print `.env*` value files (including `~/.agents/env/values/`).
- Use `varlock load --agent` (add `--show-all` for full redacted report). Run secret-dependent commands via `varlock run --inject vars -- <command>`.
- Never `env`/`printenv`, `varlock encrypt`/`reveal`, raw `varlock load`, or dumps of `process.env`.
- Prefer `npm run env:audit` and staged-only `npm run env:scan` without `--include-ignored`.
- Do not introduce `op://`, `op read`, or 1Password vault steps. Varlock owns this repo's secret path.
- App runtime: Node 22.13+ unless a maintainer approves otherwise.
- Do not rotate credentials, change provider/platform values, deploy, or cross a `needs-human` gate without approval. Stop and report if validation needs a real unlock.

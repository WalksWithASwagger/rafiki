# Rafiki Docs Audit — 2026-09-04

Last reviewed: 2026-09-04

Read-only audit of every tracked Markdown file, run after the repo-skill
cleanup in #456. It is a dated snapshot. The follow-up work is tracked in
GitHub issues, listed at the end; this record is not authorization for any
of them.

## Why This Exists

Kris asked for a docs audit after the skills audit. `npm run docs:check`
was green, but it only scans `README.md` and `docs/**` (37 of 95 tracked
Markdown files), so link health said nothing about drift, duplication, or
contradictions. This sweep cross-referenced doc claims against the tree,
`package.json`, CI workflows, `lib/models.py`, and recent PRs.

## Baseline

- Branch `chore/skill-cruft-cleanup` at `fddcfd1` (PR #456), one ahead of
  `origin/main` `bf04778`.
- Checks run: `git ls-files '*.md'` with line counts and last-commit dates;
  `npm run docs:check` (0 broken links, 37 files); `npm run public:check`
  (pass); `npm run doctor` (8 ok, 0 warnings); `pytest tests/test_slingsby_*.py`
  (4 failed, 21 passed, see Gaps); `gh pr list`, `gh pr checks 456`,
  `gh pr checks 449`.
- Not run: `npm run verify`, full `npm test`, `pack:check`. Live GitHub
  branch-protection settings were inferred from the 2026-09-03 audit and
  check runs, not read from the settings API.

## Counts

| Signal | Count |
|---|---|
| Tracked Markdown files | 95 |
| Files scanned by `docs:check` | 37 |
| Broken Markdown links | 0 |
| Path or claim drifts | 6 |
| Duplicate topic clusters | 6 |
| Contradictions | 7 |
| Orphaned docs | 6 |
| Files untouched more than 6 months | 0 |
| `CHANGELOG.md` | none |

## Contradictions

- Auto-merge: `docs/DELIVERY-PIPELINE.md` lines 6 and 143 say the pipeline
  never auto-merges; `meta/routines/auto-merge-gate.prompt.md` lines 57-68
  describe a squash-merge policy.
- Required checks: `.github/branch-protection.md:6` says `test`,
  `secret-scan`, `policy`; `meta/routines/SETUP.md:37` says the `CI / test`
  check; the 2026-09-03 audit says `test` + `secret-scan`. The `policy` job
  runs only for `codex/issue-*` head branches and skipped on #449, #456.
- Branch naming: `docs/DELIVERY-PIPELINE.md:29` gives `codex/issue-<n>-<slug>`
  as the branch shape; the last 15 PRs used `cursor/`, `chore/`, `docs/`,
  `fix/`, `dependabot/`.
- Model aliases: `docs/MODEL-POLICY.md:39-40` and `README.md:324-325` still
  advertised `gpt1`/`dalle3` and the retired OpenAI models. Fixed in #457.
- Python invocation: `README.md:99,240,430`, `CONTRIBUTING.md:100`,
  `docs/FRONTEND.md:123`, `docs/DELIVERY-PIPELINE.md:148-152` use bare
  `python3`; `README.md:214-215` and `docs/MCP.md:22,352` use
  `./.venv/bin/python`. `scripts/run-pytest.js` already prefers `.venv`, so
  `npm test` is the safe form.
- Packaged fixtures: `docs/FOLDER-LAYOUT.md:75-76` says one prompt ships in
  the npm package; `docs/PROMPT-MEDIA-POLICY.md:20-23` and `README.md` say two.
- Consistent, no action: Node 22.13+ everywhere; default model
  `gemini-2.5-flash-image` everywhere; `docs/MCP.md` tool list matches
  `mcp_server.py` (25 of 25).

## Drift

- `docs/FOLDER-LAYOUT.md` omits `frontend/`, `llms.txt`, `docs/use-cases/`,
  `meta/plans/`, `tests/skills/`, most of `config/`, 12 of 23 `scripts/`,
  and roughly 20 `lib/` modules. Line 34 describes `meta/audits/` as holding
  only `dev-loop-log.csv`. Line 72 omits the tracked public exception
  `prompts/bcai/ed-ai-logo-variations.md`.
- `docs/PROMPT-MEDIA-POLICY.md:60-61` cites tracked examples in `assets/`;
  `git ls-files assets` is empty.
- `docs/MCP.md:242` names `config/media-roots.json`; the documented user file
  is `config/media-roots.local.json` (code accepts both).
- `frontend/docs/HANDOFF.md:6` says "Version: 0.8.2"; `frontend/package.json`
  has no version field.
- `SECURITY.md:19` hardcodes `/Users/kk/Code/rafiki` in a public repo.
- `.gitignore` comment near line 98 calls `config/keyframes*.json` private;
  all four are tracked public fixtures.

## Duplicate Clusters

| Topic | Files | Canonical |
|---|---|---|
| Install/setup | `README.md:37-60`, `CONTRIBUTING.md:6-27`, `run-rafiki/SKILL.md:32-40`, `docs/DOCTOR.md:46-59` | README |
| Env/Varlock rules | `README.md:62-116`, `AGENTS.md:207-227`, `SECURITY.md:6-24`, `CONTRIBUTING.md:23-27`, `docs/MCP.md:36-40` | AGENTS.md (agents), README (humans) |
| Verification gates | `README.md:150-161`, `CONTRIBUTING.md:40-53`, `docs/DELIVERY-PIPELINE.md:121-127`, `agentic/contract.json` | DELIVERY-PIPELINE as the contract subset of `npm run verify` |
| Portal/command center | `docs/COMMAND-CENTER.md`, `docs/PORTAL-COMMAND-CENTER.md`, `docs/FRONTEND.md`, `docs/LIBRARY-VIEWER-DESIGNER-HANDOFF-2026-07.md`, `README.md:234-288` | FRONTEND + PORTAL-COMMAND-CENTER |
| Roadmaps | `docs/ROADMAP.md`, `docs/LIBRARY-ARCHIVE-ROADMAP.md`, `docs/GENERATE-UI-NEXT-WORK-PLAN-2026-07.md`, `meta/plans/2026-07-01-week-plan.md` | ROADMAP |
| Public/private boundary | `README.md:336-349`, `docs/PROMPT-MEDIA-POLICY.md`, `docs/SCOPE.md`, `docs/FOLDER-LAYOUT.md:72-78`, `CONTRIBUTING.md:88-91` | PROMPT-MEDIA-POLICY |

## Misfiled And Orphaned

- Dated records living in `docs/` as if they were guidance:
  `GENERATE-UI-NEXT-WORK-PLAN-2026-07.md`,
  `LIBRARY-VIEWER-DESIGNER-HANDOFF-2026-07.md`,
  `BCAI-FELLOWSHIP-READING-ROOM-HANDOFF-2026-07.md`,
  `CDN-PUBLISHING-RESEARCH.md`, `LIBRARY-ARCHIVE-ROADMAP.md` (Phase 1
  shipped), and `RAP-CAPSTONE-THUMBNAILS-YOUTUBE-HANDOFF-2026-07-01.md`.
  The RAP file names real cohort participants and YouTube IDs.
- Linked from nowhere: `meta/audits/2026-05-18-rafiki-docs-cleanup.md`,
  `meta/audits/2026-05-18-rafiki-product-audit.md`,
  `meta/audits/2026-05-21-workplan.md`,
  `meta/audits/2026-06-05-public-release-checklist.md`,
  `meta/plans/2026-07-01-week-plan.md`, and the 20 non-Slingsby
  `styles/*.md` guides (not read by code; `lib/styles.py` reads `styles.yaml`).
- `docs/INDEX.md:48-54` files three audit records under "Runtime Surfaces".

## Gaps

- No `CHANGELOG.md`. Last tag `v1.1.0` (2026-05-03, `e72c3ef`),
  `package.json` still 1.1.0, roughly 100 PRs since. `AGENTS.md` lines 173
  and 179 require changelogs be kept accurate.
- `tests/test_slingsby_runner.py` fails 4 of 25 on a machine with a real
  `.env` because `scripts/slingsby-proposal-generate.sh:49-50` sources
  `$ROOT/.env` and `.env.local`; tests only override via
  `SLINGSBY_ENV_FILE`. Green in CI. Undocumented.
- npm 10 / Node 22.13 lockfile rule only implied by `engines`.
- `.claude/skills/*` are symlinks; `docs/DELIVERY-PIPELINE.md:164-168` says
  "relative adapters" without saying so.
- `docs:check` scope (README + docs only) is not stated anywhere.

## Disposition

Done this session:

- #456 dropped the stale `.claude/skills/rafiki.md` and folded
  `agentic-intake` into the issue-writer skill.
- #457 removed the `gpt1` and `dalle3` aliases from code, help text,
  README, and MODEL-POLICY, with a regression test.

Opened as issues:

- #458 reconcile auto-merge, required-check, and branch-naming claims
  (`agent:ready`, refs #327).
- #459 rewrite FOLDER-LAYOUT from the tracked tree (`agent:ready`).
- #460 decision on the RAP capstone handoff with participant names
  (`needs-human`).
- #461 move dated records to `meta/`, add `meta/README.md`, regroup INDEX
  (`agent:ready`, skips the RAP file pending #460).
- #462 contributor gaps in CONTRIBUTING, drop duplicated install block,
  remove machine path from SECURITY (`agent:ready`; changelog policy is a
  human checkpoint inside it).

Not opened, polish only: trim `docs/PORTAL-COMMAND-CENTER.md` legacy modes,
merge or rename `docs/COMMAND-CENTER.md`, fix the `docs/MCP.md:242`
filename, fix `docs/PROMPT-MEDIA-POLICY.md:60-61`, drop the
`frontend/docs/HANDOFF.md` version line.

# Rafiki Docs Cleanup Audit (2026-05-18)

## Summary

This cleanup records the state after the library/archive work and the BC + AI
Communities graphics closeout. The goal is to prevent future agents from
following stale local checkout state or missing the Codex skill mirror.

## Sync State

- Clean working branch for this cleanup: `codex/issue-116-rafiki-docs-cleanup`
  from `origin/main`.
- Canonical current checkout state: `origin/main` includes the BC-169
  Communities prompt kit as commit `2044a99`.
- Stale local checkout observed at `/Users/kk/Code/rafiki`: branch
  `codex/BC-169-communities-prompt-kit` tracks a deleted remote branch and has
  duplicate local work relative to `origin/main`.
- Nested scratch checkout observed at `/Users/kk/Code/rafiki/rafiki`: separate
  git repository, stale relative to `origin/main`, and not part of the canonical
  repo layout. It was moved, not deleted, to
  `/Users/kk/.codex/cleanup-archive/rafiki-2026-05-18/nested-rafiki`.
- Stale untracked audit `meta/audits/documentation-audit-2026-05-17.md` from
  the old checkout was moved to the same cleanup archive.

## Documentation Updates

- Added `.agents/skills/github-issue-writer/SKILL.md` and
  `.agents/skills/github-pr-reviewer/SKILL.md` as Codex mirrors of the tracked
  `.claude/skills/` routines.
- Updated `docs/FOLDER-LAYOUT.md` so the repository map includes the `.agents/`
  skill surface.
- Updated `docs/DELIVERY-PIPELINE.md` to tell maintainers to keep Claude Code
  and Codex skill guidance equivalent.
- Updated `docs/ROADMAP.md` to point future agents at this cleanup audit and to
  include both agent-facing skill surfaces in the system map.

## Current Queue

Rafiki:

- Open PR #92: `Add image prompts for dontsurveil.me Bill C-22 page`;
  merge state is clean, checks are green/skipped, and it remains labeled
  `needs-human`.
- Open issue #69: Notion signed upload verification remains blocked on a real
  workspace check and is still `needs-human`.
- Closed issue range #82-#88: the BC + AI Communities graphic prompts were
  handled through the downstream website installation path.

BC + AI website:

- Merged PR #181: `Install approved Rafiki Communities graphics`; issue #59 is
  closed after live install verification.
- Open PR #180: draft reconciliation for `feat/per-photo-photographer-credit`;
  still dirty/draft work.
- Next actionable follow-ups are the production snippet and partners/Yoast
  issues before the more content-judgment-heavy tickets.

## Next Round

1. Review and merge Rafiki PR #92 if the `needs-human` content checkpoint is
   satisfied.
2. Resolve Rafiki issue #69 only when a real Notion workspace credential path is
   available.
3. Triage BC + AI website production issues #172, #173, and #107 before the
   content-decision issues #174-#177.
4. Reconcile or close BC + AI website draft PR #180.
5. Continue Rafiki product work from `docs/ROADMAP.md` near-term order:
   export-action metadata stamping, archive health reports, MCP/CLI dry-run
   smoke tests, then doctor remediation.

## Verification Results

- `npm run docs:check` - passed; checked 24 Markdown files.
- `npm run pack:check` - passed; dry-run package remained at 81 files.
- `PATH=/Users/kk/Code/rafiki/.venv/bin:$PATH npm test` - passed;
  193 tests passed with one upstream Python 3.14 deprecation warning.
- `PATH=/Users/kk/Code/rafiki/.venv/bin:$PATH npm run doctor` - passed with
  0 critical issues and 2 expected provider/env warnings.
- `git diff --check` - passed.

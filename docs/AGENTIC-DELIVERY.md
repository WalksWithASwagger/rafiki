# Agentic Delivery Contract

This repo uses GitHub as execution truth and Linear as planning and status truth. v2 keeps the automation non-blocking: it can lint issues, open branches and PRs, review acceptance shape, and sync Linear, but humans still own merge decisions and sensitive actions.

## Repo Identity

- GitHub repo: `WalksWithASwagger/rafiki`
- Linear team: `Bc-ai` (`BC`)
- Linear project: `Rafiki Roadmap Delivery`
- Canonical local root: the current Rafiki checkout

## Active-Delivery Mirror Rule

Only active delivery work should be mirrored into the `Rafiki Roadmap Delivery` Linear project. Backlog, exploration, or intentionally GitHub-only follow-ups may stay in GitHub without a Linear mirror.

## Labels

- Ready: `agent:ready`
- Ready aliases accepted for migration: `auto-implement`, `autonomous`
- Review: `review-ready`
- Stop labels: `needs-human`, `blocked`, `in-progress`

New work should use `agent:ready`. The issue quality workflow normalizes aliases to `agent:ready`.

## Required Issue Shape

An issue can only keep a ready label when it includes:

- `## Context`
- `## Acceptance Criteria`
- `## Tests/Evals`
- `## Verification`
- `## Agent Instructions`
- `## Out of Scope`

Acceptance criteria must include Markdown checkboxes.

## PR Traceability Contract

If work has a Linear mirror:

- Branch must be `codex/BC-<number>-<slug>`
- PR title must start with `BC-<number>:`
- PR body must include `Closes #<github-issue>` or `Refs #<github-issue>`
- PR body must include `Linear: BC-<number>`

If work is intentionally GitHub-only and outside the active delivery lane:

- Branch may use `codex/issue-<github-issue>-<slug>`
- A Linear key is not required
- The PR still needs `Closes #<github-issue>` or `Refs #<github-issue>`

## Runner Flow

1. `.github/workflows/agentic-issue-quality.yml` validates issue shape before ready work can proceed.
2. `.github/workflows/agentic-dev-loop.yml` checks pause controls, stop labels, clean worktree state, provider output, verification commands, and diff limits.
3. `.github/workflows/agentic-traceability-sync.yml` checks branch, title, and body metadata for every PR and syncs Linear status.
4. `.github/workflows/agentic-pr-review.yml` comments an acceptance verdict and applies `review-ready` or `needs-human`.
5. Humans review and merge. v2 still never auto-merges.

## Linear Sync Rules

- `in-progress` on a GitHub issue maps to Linear `In Progress`
- Any linked PR open or draft state maps to Linear `In Review`
- A merged linked PR maps to Linear `Done`
- If Linear misses the PR attachment, the sync helper leaves a comment with the PR URL
- If the metadata does not resolve to exactly one Linear key, the workflow leaves a handoff note instead of forcing status changes

The workflow reads the token from `LINEAR_API_KEY`.

## Verification Commands

- `npm test`
- `npm run pack:check`
- `npm run doctor`

## Drafts, Blockers, And Human Gates

- Draft PRs still count as `In Review` in Linear; draft status remains the GitHub readiness signal.
- `needs-human` and `blocked` stop autonomous progress and should remain sticky until the blocker is cleared.
- Human review is required for credentials, production writes, destructive cleanup, billing or paid-service changes, policy-sensitive prompts, merge approval, and any proof that cannot be produced locally.

## Pause Controls

Use either control to stop new dev-loop work:

- Add `.dev-loop-pause` at the repo root
- Set the Actions variable `LOOP_PAUSED` to a truthy value

## Local Commands

```bash
python3 scripts/agentic/issue_lint.py --issue-file issue.md --labels agent:ready
python3 scripts/agentic/dev_loop.py --issue-number 1 --issue-title "Example" --issue-file issue.md --labels agent:ready --provider noop
python3 scripts/agentic/pr_traceability.py --pr-title "BC-1: Example" --pr-body-file pr.md --head-ref "codex/BC-1-example" --issue-file issue.md --json-output /tmp/pr-traceability.json
python3 scripts/agentic/linear_sync.py --event pr-open --pr-title "BC-1: Example" --pr-body-file pr.md --head-ref "codex/BC-1-example" --json-output /tmp/linear-sync.json
python3 scripts/agentic/ensure_labels.py --dry-run
python3 -m pytest tests/agentic
```

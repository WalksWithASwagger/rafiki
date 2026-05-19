# Rafiki Delivery Pipeline

Rafiki uses GitHub as execution truth and Linear as planning and status truth.
The pipeline is intentionally conservative: it lints issues, opens branches and
PRs, reviews acceptance shape, and syncs Linear status — but humans still own
merge decisions and sensitive actions. There is no auto-merge.

Linear project: <https://linear.app/bc-ai/project/rafiki-roadmap-delivery-faf493aca4ce>

Repo-local contract: `agentic/contract.json` (canonical source if this doc
drifts).

## Repo Identity

- GitHub repo: `WalksWithASwagger/rafiki`
- Linear team: `Bc-ai` (`BC`)
- Linear project: `Rafiki Roadmap Delivery`
- Canonical local root: the current Rafiki checkout

## Operating Model

| Surface | Purpose |
|---|---|
| GitHub issues | Acceptance criteria, execution scope, and closure semantics |
| GitHub PRs | Review, CI, diff discussion, and merge history |
| Linear project | Priority, sequencing, milestone status, and cross-repo planning |
| `agentic/contract.json` | Repo-local automation contract (labels, limits, sync rules) |

## Active-Delivery Mirror Rule

Mirror only active delivery work into the `Rafiki Roadmap Delivery` Linear
project. Backlog, exploration, or intentionally GitHub-only follow-ups stay in
GitHub without a Linear mirror and use the `codex/issue-<number>-<slug>`
fallback branch shape.

## Labels

- Ready: `agent:ready`
- Ready aliases accepted for migration: `auto-implement`, `autonomous`
- Active: `in-progress`
- Review: `review-ready`
- Stop: `needs-human`, `blocked`

New work should use `agent:ready`. The issue-quality workflow normalizes
aliases back to `agent:ready`.

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

Branch templates come from `agentic/contract.json`
(`codex/{linear_key_or_issue}-{slug}`).

If work has a Linear mirror:

- Branch: `codex/BC-<number>-<slug>`
- PR title: starts with `BC-<number>:`
- PR body: `Closes #<github-issue>` or `Refs #<github-issue>`
- PR body: `Linear: BC-<number>`

If work is intentionally GitHub-only and outside the active delivery lane:

- Branch: `codex/issue-<github-issue>-<slug>`
- A Linear key is not required
- PR body still includes `Closes #<github-issue>` or `Refs #<github-issue>`

## Status Mapping

| GitHub event | Linear result |
|---|---|
| Issue labeled `in-progress` | `In Progress` |
| Any linked PR open or draft | `In Review` |
| Linked PR merged | `Done` |

If Linear does not auto-attach the PR, the sync helper leaves a comment with
the PR URL so the breadcrumb is still durable. If metadata does not resolve to
exactly one Linear key, the workflow leaves a handoff note instead of forcing
status changes. Draft PRs still count as `In Review`; draft status is the
GitHub readiness signal.

The sync workflow reads the token from `LINEAR_API_KEY`.

## Human Gates

Automation must stop and leave `needs-human` when the next step depends on:

- credentials or private services
- production writes or destructive cleanup
- policy-sensitive prompt or content decisions
- billing or paid-service configuration
- merge approval
- proof that cannot be produced locally

`needs-human` and `blocked` are sticky. `blocked` is for external dependencies;
`needs-human` is for judgment or access.

## Pause Controls

Either control stops new dev-loop work:

- `.dev-loop-pause` at the repo root
- GitHub Actions variable `LOOP_PAUSED` set to a truthy value

## Verification Gates

Default repo gates:

- `npm test`
- `npm run pack:check`
- `npm run doctor`

Use the smallest meaningful subset for a manual PR. Agent-created PRs are
expected to report all configured checks or clearly explain what could not run.

## Runner Flow

1. `.github/workflows/agentic-issue-quality.yml` validates issue shape and
   normalizes ready-label aliases before ready work can proceed.
2. `.github/workflows/agentic-dev-loop.yml` checks pause controls, stop labels,
   clean worktree state, provider output, verification commands, and diff
   limits.
3. `.github/workflows/agentic-traceability-sync.yml` checks branch, title, and
   body metadata for every PR and syncs Linear status.
4. `.github/workflows/agentic-pr-review.yml` comments an acceptance verdict and
   applies `review-ready` or `needs-human`.
5. Humans review and merge. The pipeline never auto-merges.

## Local Commands

```bash
python3 scripts/agentic/issue_lint.py --issue-file issue.md --labels agent:ready
python3 scripts/agentic/dev_loop.py --issue-number 1 --issue-title "Example" --issue-file issue.md --labels agent:ready --provider noop
python3 scripts/agentic/pr_traceability.py --pr-title "BC-1: Example" --pr-body-file pr.md --head-ref "codex/BC-1-example" --issue-file issue.md --json-output /tmp/pr-traceability.json
python3 scripts/agentic/linear_sync.py --event pr-open --pr-title "BC-1: Example" --pr-body-file pr.md --head-ref "codex/BC-1-example" --json-output /tmp/linear-sync.json
python3 scripts/agentic/ensure_labels.py --dry-run
python3 -m pytest tests/agentic
```

## Agent-Facing Routines

For agents running the loop end to end:

- `meta/routines/SETUP.md` — label setup and first-batch policy
- `meta/routines/dev-loop-runner.prompt.md` — issue → PR runner
- `meta/routines/auto-merge-gate.prompt.md` — guarded review/repair/merge
- `.claude/skills/github-issue-writer/SKILL.md`
- `.claude/skills/github-pr-reviewer/SKILL.md`
- `.agents/skills/github-issue-writer/SKILL.md`
- `.agents/skills/github-pr-reviewer/SKILL.md`
- `.claude/commands/agentic-intake.md`

Keep `.claude/skills/` as the Claude Code surface and `.agents/skills/` as the
Codex surface. The issue-writer and PR-reviewer routines should stay equivalent
across both directories so agents do not receive different delivery guidance.

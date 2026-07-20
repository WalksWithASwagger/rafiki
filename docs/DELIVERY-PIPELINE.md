# Rafiki Delivery Pipeline

Rafiki uses GitHub as the sole planning, execution, review, and delivery source
of truth. The pipeline is intentionally conservative: it lints issues, opens
branches and PRs, and reviews acceptance shape, but humans still own merge
decisions and sensitive actions. There is no auto-merge.

Repo-local contract: `agentic/contract.json` (canonical source if this doc
drifts).

## Repo Identity

- GitHub repo: `WalksWithASwagger/rafiki`
- Canonical local root: the current Rafiki checkout

## Operating Model

| Surface | Purpose |
|---|---|
| GitHub issues | Priority, dependencies, acceptance criteria, execution scope, and closure semantics |
| GitHub PRs | Review, CI, diff discussion, and merge history |
| GitHub labels and milestones | Queue state, sequencing, and roadmap grouping |
| `agentic/contract.json` | Repo-local automation contract (labels, limits, and traceability rules) |

## Active Delivery Rule

Every implementation starts from one GitHub issue. Use issue relationships,
labels, and milestones for dependencies and sequencing. Branches use the
`codex/issue-<number>-<slug>` shape.

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

Branch templates come from `agentic/contract.json`:

- Branch: `codex/issue-<github-issue>-<slug>`
- PR title: describes the issue outcome
- PR body: `Closes #<github-issue>` or `Refs #<github-issue>`

## Status Mapping

| GitHub event | Repository result |
|---|---|
| Issue labeled `in-progress` | Work is claimed |
| Linked PR opened | Diff, CI, and review become the durable handoff |
| PR labeled `review-ready` | Advisory acceptance review may begin |
| PR has traceability drift, `needs-human`, or `blocked` | The stable `policy` check fails |
| Linked PR merged with `Closes #N` | GitHub closes the issue |

## Retired Integration Cleanup

The former external-planner integration is retired and must not be invoked or
restored. A maintainer may remove the retired `LINEAR_API_KEY` repository
Actions secret in GitHub settings without reading or revealing its value. That
manual settings cleanup is not an agent task and is not required for local or
CI verification.

## Human Gates

Automation must stop and leave `needs-human` when the next step depends on:

- credentials or private services
- production writes or destructive cleanup
- policy-sensitive prompt or content decisions
- billing or paid-service configuration
- merge approval
- proof that cannot be produced locally

`needs-human` and `blocked` are sticky: automation may add them but never remove
them. `blocked` is for external dependencies; `needs-human` is for judgment or
access. Labels and comments remain advisory; only the `policy` check conclusion
is suitable for branch-protection enforcement.

## Workspace Hygiene Report

Run the workspace hygiene report before pruning branches or worktrees in a busy
Rafiki checkout:

```bash
npm run workspace:hygiene -- --repo .
python3 scripts/workspace_hygiene.py --repo /path/to/rafiki
```

The report is read-only. It lists dirty versus clean worktrees, gone upstreams,
branches that are attached to active worktrees, dependency/cache bulk hints, and
cleanup risk labels. `safe-to-review` means "worth human inspection"; it is not
approval to delete. Dirty worktrees, checked-out branches, local-only branches,
branches ahead of upstream, locked worktrees, and gone upstreams remain
human-gated until a maintainer explicitly approves the cleanup.

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
3. `.github/workflows/agentic-traceability.yml` checks branch, title, and body
   metadata for every PR.
4. `.github/workflows/agentic-pr-review.yml` comments an acceptance verdict and
   applies `review-ready` or `needs-human`.
5. Humans review and merge. The pipeline never auto-merges.

## Local Commands

```bash
python3 scripts/agentic/issue_lint.py --issue-file issue.md --labels agent:ready
python3 scripts/agentic/dev_loop.py --issue-number 1 --issue-title "Example" --issue-file issue.md --labels agent:ready --provider noop
python3 scripts/agentic/pr_traceability.py --pr-title "Example" --pr-body-file pr.md --head-ref "codex/issue-1-example" --issue-file issue.md --json-output /tmp/pr-traceability.json
python3 scripts/agentic/ensure_labels.py --dry-run
python3 -m pytest tests/agentic
```

## Agent-Facing Routines

For agents running the loop end to end:

- `meta/routines/SETUP.md` — label setup and first-batch policy
- `meta/routines/dev-loop-runner.prompt.md` — issue → PR runner
- `meta/routines/auto-merge-gate.prompt.md` — guarded review/repair/merge
- `.agents/skills/rafiki-github-issue-writer/SKILL.md`
- `.agents/skills/rafiki-github-pr-reviewer/SKILL.md`
- `.claude/skills/rafiki-github-issue-writer/SKILL.md` (relative adapter)
- `.claude/skills/rafiki-github-pr-reviewer/SKILL.md` (relative adapter)
- `.claude/commands/agentic-intake.md`

Keep physical project skill packages under `.agents/skills/`. Claude Code uses
relative adapters under `.claude/skills/` so every client reads the same package.

# Rafiki Delivery Pipeline

Rafiki uses GitHub for concrete execution and Linear for cross-repo planning. The pipeline is intentionally conservative: it automates the boring bookkeeping and traceability work, but it does not auto-merge or override human gates.

Linear project: <https://linear.app/bc-ai/project/rafiki-roadmap-delivery-faf493aca4ce>

## Operating Model

| Surface | Purpose |
|---|---|
| GitHub issues | Acceptance criteria, execution scope, and closure semantics |
| GitHub PRs | Review, CI, diff discussion, and merge history |
| Linear project | Priority, sequencing, milestone status, and cross-repo planning |
| `agentic/contract.json` | Repo-local automation contract |
| `docs/AGENTIC-DELIVERY.md` | Ready-issue, PR, and sync rules |

## Active-Delivery Rule

Mirror only active delivery work into the `Rafiki Roadmap Delivery` project. If a GitHub issue is backlog-only, exploratory, or intentionally local, keep it GitHub-only and use the `codex/issue-<number>-<slug>` fallback branch shape.

## Required PR Metadata

If a Linear issue exists:

- Branch: `codex/BC-<number>-<slug>`
- Title: `BC-<number>: ...`
- Body: `Closes #<github-issue>` or `Refs #<github-issue>`
- Body: `Linear: BC-<number>`

If the work stays GitHub-only:

- Branch: `codex/issue-<github-issue>-<slug>`
- Body still includes `Closes #...` or `Refs #...`

## Status Mapping

| GitHub event | Linear result |
|---|---|
| Issue labeled `in-progress` | `In Progress` |
| Draft or open PR linked to the work | `In Review` |
| Linked PR merged | `Done` |

If Linear does not auto-attach the PR, the sync helper adds a comment with the PR URL so the breadcrumb is still durable.

## Labels

- `agent:ready`
- `in-progress`
- `review-ready`
- `needs-human`
- `blocked`

Legacy ready aliases `auto-implement` and `autonomous` are accepted only for migration and are normalized back to `agent:ready`.

## Human Gates

Automation must stop and leave `needs-human` when the next step depends on:

- credentials or private services
- production writes or destructive cleanup
- policy-sensitive prompt or content decisions
- billing or paid-service configuration
- merge approval
- proof that cannot be produced locally

The current repo-level blocker model is the same one used elsewhere: `blocked` is for external dependencies, `needs-human` is for judgment or access.

## Verification Gates

Default repo gates:

- `npm test`
- `npm run pack:check`
- `npm run doctor`

Use the smallest meaningful subset for a manual PR, but agent-created PRs are expected to report all configured checks or clearly explain what could not run.

## Workflow Files

- `.github/workflows/agentic-issue-quality.yml`
- `.github/workflows/agentic-dev-loop.yml`
- `.github/workflows/agentic-traceability-sync.yml`
- `.github/workflows/agentic-pr-review.yml`

`LINEAR_API_KEY` should be configured in GitHub Actions before expecting live status sync.

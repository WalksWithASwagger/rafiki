# Rafiki Delivery Pipeline

Rafiki uses the same operating loop as the kk-kb delivery pipeline: write
agent-ready GitHub issues, mirror the roadmap in Linear, let agents work from
bounded issue contracts, and review pull requests against the issue acceptance
criteria before merge.

Linear project: https://linear.app/bc-ai/project/rafiki-roadmap-delivery-faf493aca4ce

## Surfaces

| Surface | Purpose |
|---|---|
| GitHub issues | Source of truth for implementation scope, acceptance criteria, and PR closure. |
| Linear project | Prioritization, milestones, project status, and cross-repo planning. |
| `.claude/skills/github-issue-writer/` | Local issue-writing contract for agent-ready GitHub issues. |
| `.claude/skills/github-pr-reviewer/` | Local PR-review contract for checking implementation against the linked issue. |
| `meta/routines/dev-loop-runner.prompt.md` | Repeatable prompt for the issue-to-PR implementation loop. |
| `meta/routines/auto-merge-gate.prompt.md` | Legacy prompt for guarded PR review decisions. |
| `meta/audits/dev-loop-log.csv` | Lightweight audit trail for autonomous PR attempts. |

## GitHub Label Contract

These labels drive the agent loop:

| Label | Meaning |
|---|---|
| `agent:ready` | Issue has enough context, acceptance criteria, and test expectations for an agent to attempt. |
| `in-progress` | An agent or maintainer is actively working the issue. |
| `review-ready` | A PR exists and needs CI, review, or acceptance-criteria verification. |
| `needs-human` | The next step requires maintainer judgment, credentials, content policy, or merge approval. |
| `blocked` | Work cannot continue until an external blocker clears. |

Existing labels such as `phase-1`, `phase-2`, `phase-3`, `pipeline`,
`documentation`, `enhancement`, `bug`, and `tech-debt` still describe roadmap
area and work type.

## Linear Contract

Every roadmap issue should live in the `Rafiki Roadmap Delivery` Linear project
when it is part of the active plan.

Use these milestones:

- `Phase 0: Pipeline + Stabilization`
- `Phase 1: Public Release Hygiene`
- `Phase 2: Workflow Reliability`
- `Phase 3: Registry + Portal + Automation`

Linear issues should link to the corresponding GitHub issue. GitHub issues may
link back to Linear when useful, but GitHub remains the merge-closing source of
truth.

## Issue Intake

Use `.github/ISSUE_TEMPLATE/agent-task.md` or the
`github-issue-writer` skill. A ready issue includes:

- user-facing problem or opportunity
- current repo context with exact files when known
- non-goals and boundaries
- implementation phases small enough for one PR
- acceptance criteria
- required tests or smoke checks
- docs/package impact
- human checkpoints

Do not apply `agent:ready` until the issue is specific enough for a worker to
act without rereading the whole repo.

## Agent Implementation Loop

The implementation loop is:

1. Select one open issue labeled `agent:ready` and not labeled `in-progress`,
   `needs-human`, or `blocked`.
2. Re-read the issue, `docs/ROADMAP.md`, this pipeline doc, and relevant code.
3. Create a branch named `codex/<linear-key-or-issue>-<slug>`.
4. Make the smallest change that satisfies the issue.
5. Run the gates listed in the issue. Default gates are `npm test`,
   `npm run pack:check`, and `npm run doctor` when the change can affect runtime
   behavior, packaging, or docs.
6. Open a PR with `Closes #<issue>`, a criteria checklist, test output, and any
   Linear issue identifier.
7. Replace `in-progress` with `review-ready`.

The loop must stop and add `needs-human` when it touches credentials, public vs
private content boundaries, destructive cleanup, model-default policy, or any
change that cannot be verified locally.

## Review And Merge Loop

The PR gate checks:

- linked GitHub issue exists and is open
- PR scope matches the issue, or the PR uses `Refs` plus a clear follow-up
- acceptance criteria are satisfied
- tests and smoke checks are credible
- docs/package impacts are handled
- private paths, generated assets, and local-only config are not leaked
- diff is small enough to review safely

For the first 10 agent-created Rafiki PRs, keep a human spot check before merge
and record the result in `meta/audits/dev-loop-log.csv`. Real provider execution
should stay disabled until the prior PRs show clean scope control, passing CI,
and useful self-checks. v1 does not auto-merge.

## Pause Controls

Any maintainer can pause the loop by adding either:

- a root `.dev-loop-pause` file
- a GitHub Actions variable named `LOOP_PAUSED` with value `true`

Agents must check for pause signals before starting new work and before PR review.

## Default Verification Gates

Run the smallest meaningful set for the change:

- `npm test`
- `npm run pack:check`
- `npm run doctor`
- MCP smoke: list tools and call `rafiki_status`
- CLI dry run: `python generate.py --prompt "..." --dry-run --json`
- docs check: search for stale local paths or broken links when touching docs
- scheduled regen docs: `python generate.py regen --config config/scheduled-regen.json.example --dry-run`

If a gate cannot run locally, the PR must say why and mark the missing proof.

For local automation recipes, see [SCHEDULED-REGEN.md](SCHEDULED-REGEN.md).

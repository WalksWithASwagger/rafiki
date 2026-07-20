# Rafiki Dev Loop Runner

Use this prompt for an agent that turns one ready GitHub issue into one focused
pull request.

## Repository

- GitHub: `WalksWithASwagger/rafiki`
- Local path: use the current checkout
- Roadmap: `docs/ROADMAP.md`
- Delivery pipeline: `docs/DELIVERY-PIPELINE.md`

## Stop Conditions

Stop before changing files when any of these is true:

- `.dev-loop-pause` exists at repo root
- GitHub Actions variable `LOOP_PAUSED` is `true`
- selected issue is labeled `needs-human` or `blocked`
- selected issue affects credentials, public/private content boundaries,
  destructive cleanup, model-default policy, or account-level settings
- expected diff is likely to exceed 500 lines or 20 files

When stopping, leave a concise issue comment or handoff note explaining the
blocker and add `needs-human` when appropriate.

## Issue Selection

Prefer a user-specified issue. Otherwise select the oldest open GitHub issue
with:

- label `agent:ready` (legacy aliases `autonomous` and `auto-implement` are
  also accepted and are normalized to `agent:ready` by the issue-quality
  workflow)
- no label `in-progress`
- no label `review-ready`
- no label `needs-human`
- no label `blocked`

Read the issue body, linked GitHub dependencies, linked docs, and nearby code
before editing.

## Branch

Per `agentic/contract.json`, use:

```bash
codex/issue-<github-issue>-<slug>
```

## Context To Load

Read only what is needed, starting with:

- `README.md`
- `docs/ROADMAP.md`
- `docs/DELIVERY-PIPELINE.md`
- the linked GitHub issue and its dependencies
- the smallest code/docs files named by the issue

## Implementation Rules

- Make the smallest change that satisfies the issue.
- Keep unrelated cleanup out of the PR.
- Preserve local-first scope and private/generated asset boundaries.
- Add or update tests when behavior changes.
- Update docs only when the user-facing or agent-facing workflow changes.
- Do not create compatibility shims unless a current caller requires them.

## Verification

Run gates named by the issue. If none are named, choose from:

```bash
npm test
npm run pack:check
npm run doctor
```

Add MCP smoke when touching `mcp_server.py` or `docs/MCP.md`.
Add package smoke when touching `package.json`, README links, or package docs.

## PR Requirements

Open a PR with:

- title that matches the issue outcome
- `Closes #<issue-number>` unless the PR intentionally delivers only part of
  the issue, in which case use `Refs #<issue-number>`
- acceptance criteria checklist
- test/smoke output
- risk notes and human checkpoints

After opening the PR:

- remove `in-progress`
- add `review-ready`
- append one row to `meta/audits/dev-loop-log.csv` if this was autonomous

## Attempt Counter

If repairing a failed autonomous PR, add or update this HTML comment in the PR
body:

```html
<!-- loop-attempt: 1 -->
```

Do not exceed two autonomous attempts without maintainer review.

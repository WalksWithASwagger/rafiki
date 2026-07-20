---
name: rafiki-github-issue-writer
description: Write agent-ready GitHub issues for Rafiki with acceptance criteria, tests, dependencies, and human checkpoints.
---

# GitHub Issue Writer

Use this skill when creating or rewriting Rafiki GitHub issues for the
GitHub-only delivery pipeline.

## Goal

Produce issues that a coding agent can implement without rediscovering the
whole repository. The issue should also be useful to a human reviewer scanning
the GitHub queue.

## Required Structure

```markdown
## Summary

What should change, in user-facing terms.

## Context

- Roadmap phase:
- GitHub dependencies:
- Relevant files:
- Current behavior:
- Desired behavior:

## Implementation Notes

Suggested phases or constraints. Keep this bounded to one PR unless the issue
explicitly says otherwise.

## Acceptance Criteria

- [ ] Concrete observable outcome
- [ ] Tests or smoke checks pass
- [ ] Docs/package impact handled, if relevant

## Tests/Evals

Regression tests, smoke checks, evals, or fixtures that prove the change.

## Verification

Commands or manual checks the PR must report.

## Agent Instructions

Scope constraints, branch name, safety boundaries, and implementation notes.

## Out of Scope

Explicit non-goals and likely overreach.

## Human Checkpoints

Anything requiring maintainer judgment before implementation or merge.
```

## Defaults For Rafiki

Use these repo references when relevant:

- `README.md`
- `docs/ROADMAP.md`
- `docs/DELIVERY-PIPELINE.md`
- `docs/MCP.md`
- `docs/SCOPE.md`
- `agentic/contract.json`
- `generate.py`
- `index.js`
- `mcp_server.py`
- `lib/`
- `tests/`

Default verification choices:

- `npm test`
- `npm run pack:check`
- `npm run doctor`
- MCP smoke: list tools and call `rafiki_status`

## Label Guidance

Add `agent:ready` only when scope, files, criteria, and verification are clear.
`autonomous` and `auto-implement` are accepted as legacy aliases and are
normalized back to `agent:ready` by the issue-quality workflow — prefer
`agent:ready` on new issues.

Add `needs-human` when the issue depends on release policy, credentials,
private content, destructive cleanup, or the default model decision.

Use phase and type labels to help planning:

- `phase-1`, `phase-2`, `phase-3`
- `pipeline`, `documentation`, `enhancement`, `bug`, `tech-debt`

## Quality Bar

An agent-ready issue is specific, testable, and small. It should name what is
out of scope as clearly as what is in scope and link blocking GitHub issues.

---
name: github-pr-reviewer
description: Review Rafiki pull requests against linked GitHub issue acceptance criteria, tests, docs, and local-first safety boundaries.
---

# GitHub PR Reviewer

Use this skill to review Rafiki pull requests before merge.

## Review Inputs

Load:

- PR title, body, files, and diff
- linked GitHub issue and acceptance criteria
- linked Linear issue, when present
- relevant docs or tests named by the issue
- CI status and reported local smoke checks

## Review Checklist

Check:

- the PR closes or references the correct issue
- scope matches the issue
- acceptance criteria are met
- tests cover changed behavior
- docs and package allowlist are updated when README/package links change
- private local paths, generated outputs, credentials, and local config are not
  accidentally committed
- local-first product boundary remains intact
- failure modes are reported clearly enough for a user or agent

## Autonomous Verdict

When called by an automation gate, return this machine-readable block at the end
of the review:

```json
{
  "verdict": "pass | fail | needs_human",
  "linked_issue": "#0",
  "acceptance_criteria": "pass | fail | partial",
  "tests": "pass | fail | missing | not_applicable",
  "docs": "pass | fail | missing | not_applicable",
  "risk": "low | medium | high",
  "required_action": "merge | repair | human_review"
}
```

Use `needs_human` for release policy, security, credentials, public/private
content boundaries, default model policy, or ambiguous product decisions.

## Findings Format

Lead with bugs and risks, ordered by severity. Include file and line references
when possible. If there are no blocking issues, say that clearly and mention
remaining test gaps or residual risk.

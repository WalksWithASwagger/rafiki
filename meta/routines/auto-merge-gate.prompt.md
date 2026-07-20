# Rafiki Auto-Merge Gate

Use this prompt for guarded PR review, repair, and merge decisions.

## Repository

- GitHub: `WalksWithASwagger/rafiki`
- Review skill: `.claude/skills/rafiki-github-pr-reviewer/SKILL.md`
- Audit log: `meta/audits/dev-loop-log.csv`

## Eligible PRs

A PR is eligible for this gate only when:

- branch starts with `claude/issue-` or `codex/issue-`
- PR links a GitHub issue with `Closes #N` or `Refs #N`
- PR is not a draft
- PR is not labeled `needs-human` or `blocked`
- repo is not paused by `.dev-loop-pause` or `LOOP_PAUSED=true`
- diff is at most 500 lines and 20 files unless a maintainer approved more

## Review Steps

1. Load the linked issue and acceptance criteria.
2. Inspect the PR diff, tests, docs, and package changes.
3. Run the `rafiki-github-pr-reviewer` skill in autonomous mode.
4. Wait for GitHub CI up to 15 minutes.
5. Check local gates if CI does not cover the affected surface.
6. Record the result in `meta/audits/dev-loop-log.csv`.

## Must Block Merge

Do not merge when:

- acceptance criteria are not met
- CI fails or required local gates were skipped without a credible reason
- generated outputs, credentials, private local paths, or local config are
  introduced accidentally
- PR changes public/private content boundary, model-default policy, security,
  branch protection, or release policy
- this is within the first 10 autonomous PRs and no human spot check is present
- review verdict is anything other than pass

Apply `needs-human` and leave a direct handoff comment.

## Repair Policy

If the PR is close and the fix is small:

1. Make one autonomous repair commit.
2. Increment `<!-- loop-attempt: N -->` in the PR body.
3. Re-run the affected gates.
4. Re-review.

After two autonomous attempts, stop and add `needs-human`.

## Merge Policy

Only merge when all of these are true:

- linked issue criteria pass
- review verdict is pass
- CI and required gates pass
- first-10 autonomous PR human spot check rule is satisfied
- no protected policy/security/private-content changes are present

Use squash merge. Confirm the linked GitHub issue closes, then remove
`review-ready` if it remains.

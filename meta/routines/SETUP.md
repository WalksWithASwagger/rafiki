# Rafiki Pipeline Setup

This repo ports the kk-kb GitHub issue and PR workflow into Rafiki. The local
files live in the repo so future agents can restart from the same rules.

## Required GitHub Labels

Create or update these labels:

```bash
gh label create autonomous --color 0E8A16 --description "Issue is ready for an autonomous agent attempt." --force
gh label create in-progress --color FBCA04 --description "An agent or maintainer is actively working this issue." --force
gh label create review-ready --color 1D76DB --description "A PR exists and needs CI or acceptance-criteria review." --force
gh label create needs-human --color D93F0B --description "Maintainer judgment, credentials, policy, or merge approval is needed." --force
gh label create blocked --color 000000 --description "Work is blocked by an external dependency." --force
```

Keep the existing roadmap labels for phase and work type.

## Linear

Project:

- `Rafiki Roadmap Delivery`
- URL: https://linear.app/bc-ai/project/rafiki-roadmap-delivery-faf493aca4ce

Milestones:

- `Phase 0: Pipeline + Stabilization`
- `Phase 1: Public Release Hygiene`
- `Phase 2: Workflow Reliability`
- `Phase 3: Registry + Portal + Automation`

Each active roadmap GitHub issue should have a matching Linear issue or a
Linear link attached to the project.

## Branch Protection

See `.github/branch-protection.md`. At minimum, protect `main`, require PRs,
and require the `CI / test` check before merge.

## Agent Runner

Use these prompt files as routine inputs:

- `meta/routines/dev-loop-runner.prompt.md`
- `meta/routines/auto-merge-gate.prompt.md`

The runner must check pause controls before starting work or merging:

- root `.dev-loop-pause`
- GitHub Actions variable `LOOP_PAUSED=true`

## First Batch Policy

For the first 10 autonomous PRs in this repo:

- require a human spot check before merge
- record every attempt in `meta/audits/dev-loop-log.csv`
- prefer small docs/tests/pipeline issues before larger product changes

After the first 10, revisit whether auto-merge can be enabled.

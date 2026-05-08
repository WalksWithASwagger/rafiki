# Rafiki Agentic Workflow

Rafiki uses a Linear-backed GitHub issue-to-PR loop:

1. Write an agent-ready GitHub issue with `.claude/skills/github-issue-writer/`.
2. Link or mirror it in the Linear project `Rafiki Roadmap Delivery`.
3. Label it `autonomous` only when scope and verification are clear.
4. Run `meta/routines/dev-loop-runner.prompt.md` to produce one focused PR.
5. Review with `.claude/skills/github-pr-reviewer/`.
6. Use `meta/routines/auto-merge-gate.prompt.md` for guarded repair and merge.

Pause the loop with `.dev-loop-pause` or `LOOP_PAUSED=true`.

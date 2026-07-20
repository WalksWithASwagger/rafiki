# Agent Instructions

## Environment Safety

- Treat `.env.schema`, `.env.example`, committed documentation, and code
  references and sanitized fixtures as the only agent-readable environment
  contract.
- Never read, open, copy, search, or print `.env*` value files, including the
  user-managed files under `~/.agents/env/values/`.
- Never run `env`, `printenv`, `varlock encrypt`, `varlock reveal`, raw
  `varlock load`, or code that dumps `process.env` or `os.environ`.
- Every Varlock load must use `varlock load --agent`; add `--show-all` when a
  complete redacted validation report is needed.
- Run secret-dependent child commands through
  `varlock run --inject vars -- <command>`.
- Use `npm run env:audit` so generated and non-source paths stay excluded, and
  use staged-only `npm run env:scan` without `--include-ignored`.
- Keep Rafiki's application runtime at Node 22.12+ unless a maintainer
  explicitly approves another change. Run Varlock 1.10 with the same runtime
  or the standalone CLI.
- Do not change provider or platform values, rotate credentials, deploy, or
  cross a `needs-human` gate.

Stop and report a blocker if validation requires a real value or human unlock.

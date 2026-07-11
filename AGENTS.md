# Agent Instructions

## Environment Safety

- Treat `.env.schema`, `.env.example`, committed documentation, and code
  references as the only agent-readable environment contract.
- Never read, open, copy, search, or print `.env`, `.env.local`, or other
  ignored environment value files.
- Never run `env`, `printenv`, `varlock encrypt`, `varlock reveal`, raw
  `varlock load`, or code that dumps `process.env` or `os.environ`.
- Every Varlock load must use `varlock load --agent`; add `--show-all` when a
  complete redacted validation report is needed.
- Run provider-capable child commands through
  `varlock run --inject vars -- <command>`.
- Do not change provider or platform values, rotate credentials, deploy, or
  cross a `needs-human` gate.

Stop and report a blocker if validation requires a real value or human unlock.

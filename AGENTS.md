# Agent Instructions

- Treat `.env.schema` as the agent-readable environment contract.
- Do not read `.env`, `.env.local`, ignored env files, or local credential stores.
- Do not run commands that reveal raw secret values, including `varlock reveal`,
  `varlock printenv`, `varlock encrypt`, `env`, or `printenv`.
- Do not print `process.env`, `os.environ`, full Varlock load output, or provider
  settings. Report only redacted status such as "set" or "not set".
- Use `varlock load --agent --show-all` for redacted validation.
- Use `varlock run --inject vars -- ...` when a command needs provider-capable
  environment variables injected into a child process.

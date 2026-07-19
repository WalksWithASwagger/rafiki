# Security

Rafiki is a local-first tool. It does not run a hosted backend or shared
control plane. Provider API keys stay on the operator's machine.

## Secrets

- Keep keys in the user-managed `~/.agents/env/values/` convention or an
  untracked repo-local value file.
- `.env`, `.env.local`, and `.env.*.local` are intentionally gitignored. Agents
  must not inspect any of those value files.
- If a key was ever committed, rotate it immediately even if it has since been
  removed from the working tree.

Before changing repository visibility or publishing a release, run:

```bash
gitleaks detect --source . --redact --no-banner --verbose
trufflehog git file:///Users/kk/Code/rafiki --only-verified --no-update --json
git check-ignore -v .env .env.local .env.rafiki.local node_modules output .venv
```

Known false positives should be documented in the dated release checklist and
allowlisted by fingerprint in `.gitleaksignore`, not ignored silently.

## Local Portal

`python generate.py serve` binds to `127.0.0.1` by default.

If you expose the portal beyond localhost:

- use `--public` intentionally
- set both `PORTAL_USERNAME` and `PORTAL_PASSWORD` (`--public` refuses to start
  without them)
- prefer a strong generated password
- avoid exposing the portal directly to the public internet

See [docs/SCOPE.md](docs/SCOPE.md) for the supported deployment model.

## Reporting Issues

If you discover a security problem:

- do not include live secrets in a public issue
- prefer private disclosure through GitHub security reporting if available
- otherwise contact the repository owner directly before publishing details

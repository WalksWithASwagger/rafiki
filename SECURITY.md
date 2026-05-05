# Security

Rafiki is a local-first tool. It does not run a hosted backend or shared
control plane. Provider API keys stay on the operator's machine.

## Secrets

- Keep keys in environment variables or an untracked `.env`.
- `.env` is intentionally gitignored.
- If a key was ever committed, rotate it immediately even if it has since been
  removed from the working tree.

## Local Portal

`python generate.py serve` binds to `127.0.0.1` by default.

If you expose the portal beyond localhost:

- use `--public` intentionally
- set both `PORTAL_USERNAME` and `PORTAL_PASSWORD`
- prefer a strong generated password
- avoid exposing the portal directly to the public internet

See [docs/SCOPE.md](docs/SCOPE.md) for the supported deployment model.

## Reporting Issues

If you discover a security problem:

- do not include live secrets in a public issue
- prefer private disclosure through GitHub security reporting if available
- otherwise contact the repository owner directly before publishing details


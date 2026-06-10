# Contributing

Rafiki is a local-first tool. Keep changes easy to run from a checkout, easy
to review, and safe for users who store API keys on their own machines.

## Development Setup

```bash
git clone https://github.com/WalksWithASwagger/rafiki.git
cd rafiki

npm install

python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/pip install -r requirements-dev.txt
```

Create a local `.env` only if you need to hit real provider APIs:

```bash
cp .env.example .env
```

## Common Commands

```bash
npm run doctor
npm test
npm audit --omit=dev --audit-level=moderate
./.venv/bin/python -m pip_audit -r requirements.txt
npm run pack:check
python generate.py --help
python generate.py serve --open
```

## Deterministic Local Verification

The committed test and portal smoke gates should pass from a stateful checkout:

```bash
npm test
npm run e2e:portal
```

For deterministic tooling contexts outside the committed smoke script, set
`RAFIKI_DISABLE_EXTRA_OUTPUTS=1` to ignore
`config/extra-outputs.json` and `config/extra-outputs.local.json` for that
process. Normal runtime commands include configured extra outputs by default.

## Contribution Guidelines

- Do not commit secrets, tokens, or private local paths.
- Keep local machine configuration in untracked files where possible.
- Prefer generic examples in top-level docs; keep highly specific or content-
  specific workflow notes in a private knowledge base, not the public tool repo.
- Add or update tests when changing Python behavior.
- Keep the local-first product scope intact unless the change explicitly expands
  it.

## Release-Focused Checks

Before merging public-release work:

- `python3 -m pytest -q`
- `python3 -m pip_audit -r requirements.txt`
- `npm pack --dry-run`
- sanity-check `README.md`, `SECURITY.md`, and `docs/SCOPE.md`

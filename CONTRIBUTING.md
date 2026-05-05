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
npm run pack:check
python generate.py --help
python generate.py serve --open
```

## Contribution Guidelines

- Do not commit secrets, tokens, or private local paths.
- Keep local machine configuration in untracked files where possible.
- Prefer generic examples in top-level docs; move highly specific workflow notes
  into `docs/` or `prompts/`.
- Add or update tests when changing Python behavior.
- Keep the local-first product scope intact unless the change explicitly expands
  it.

## Release-Focused Checks

Before merging public-release work:

- `python3 -m pytest -q`
- `npm pack --dry-run`
- sanity-check `README.md`, `SECURITY.md`, and `docs/SCOPE.md`


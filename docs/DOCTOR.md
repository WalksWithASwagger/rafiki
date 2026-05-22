# Rafiki Doctor

`rafiki doctor` is a local readiness check for the Node CLI, Python generation
stack, MCP server, provider keys, and HTML rendering path.

Run it from the repo root:

```bash
npm run doctor
```

or through the CLI:

```bash
npx rafiki --doctor
```

## What It Checks

- Node.js version.
- Core Node dependencies for the CLI: `commander`, `dotenv`, and `chalk`.
- Python executable, preferring `.venv` unless `RAFIKI_DOCTOR_PYTHON` is set.
- Core Python dependencies for generation: `python-dotenv`, `google-genai`,
  `openai`, `pillow`, `pyyaml`, and `tenacity`.
- `.env` presence. This is useful but optional because shell environment
  variables work too.
- Provider keys without printing secret values: `GOOGLE_API_KEY` for Gemini and
  `OPENAI_API_KEY` for OpenAI image generation.
- MCP availability: `mcp_server.py` exists, compiles, and the `FastMCP` SDK can
  import.
- Browser rendering readiness: `puppeteer` and `sharp` can load, and Rafiki can
  find either a configured Chrome/Chromium path or Puppeteer's managed browser.

## Exit Codes

Doctor prints `[ok]`, `[warn]`, and `[fail]` lines.

Warnings do not fail the command. Missing provider keys, a missing `.env`, MCP
setup gaps, or browser-rendering gaps are actionable warnings because dry-run,
review, and other local workflows may still be usable.

Failures exit non-zero. Today those are reserved for the critical local runtime:
core Node CLI dependencies, Python itself, or core Python generation
dependencies.

## Common Fixes

Install Node dependencies:

```bash
npm install
```

Install Python dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Optional `.env` setup:

```bash
cp .env.example .env
```

Then edit `.env`, or skip the file and export provider keys in your shell.
Provider keys are warnings, not critical failures, because dry-run, render, and
review workflows can still run without them.

```bash
GOOGLE_API_KEY=...
OPENAI_API_KEY=...
```

Repair browser rendering:

```bash
npm install
```

If `doctor` says `puppeteer` or `sharp` is missing or cannot load, fix Node
packages first. If those packages load but no browser is found, install
Chrome/Chromium, set `PUPPETEER_EXECUTABLE_PATH=/path/to/chrome`, or run:

```bash
npx puppeteer browsers install chrome
```

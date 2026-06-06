---
name: run-rafiki
description: Build, run, screenshot, and smoke-test Rafiki — the local-first image-gen CLI, the browser review portal, the run viewer, and the HTML-to-PNG renderer. Use to launch Rafiki, take a screenshot of the portal/viewer, or confirm a change works without spending on image generation.
---

# Run Rafiki

Rafiki is a **local-first** image-generation + review workflow. It is a single
checkout exposing four surfaces:

- **CLI** — `node index.js` (installed as `rafiki` / `image-gen`): generate, batch, render, view, doctor.
- **Python engine** — `generate.py`: same generation path plus `serve` (the portal) and `library`.
- **Portal** — a local web server (`generate.py serve`) for browsing/rating runs.
- **MCP server** — `mcp_server.py` (FastMCP), exposing the above as tools.

It is built to run from a checkout on the user's machine. **All commands below
were run on macOS** (this is a Mac-targeted local tool — there is no Linux
container path and no `apt-get`). Paths are relative to the repo root.

The agent path that needs *no API keys and spends no money*: `--doctor`,
`npm run smoke:dry-run`, the portal, the run viewer, and `--render`. Only
actual image generation needs a provider key.

## Prerequisites

- Node.js ≥ 20.17 (verified on v24.15.0) + npm ≥ 10.
- Python ≥ 3.11 (verified on 3.12.13).
- Google Chrome (Puppeteer/headless). `--doctor` reports the path it found.

## Build

From a clean checkout (idempotent against the committed lockfile — ~5s for npm):

```bash
npm ci
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/pip install -r requirements-dev.txt
```

Optionally add provider keys for real generation (not needed for any of the
no-spend paths below):

```bash
cp .env.example .env   # then add GOOGLE_API_KEY and/or OPENAI_API_KEY
```

Confirm the install:

```bash
node index.js --doctor
```

Expected: a list of `[ok]` lines (Node, Python, deps, .env, provider keys,
MCP, browser rendering) and "Doctor found 0 critical issue(s)".

## Run (agent path) — screenshot the GUI

The existing repo smokes (below) verify logic but throw their screenshots
away. To get PNGs you can actually open, use the driver. It picks a free
port, builds the library index, launches the portal, screenshots it, builds a
run viewer and screenshots that, exercises the Studio Dry Run, renders an
HTML card to PNG, exports a Video Lab EDL, then runs Canva and Notion export
dry-runs. No keys, no spend.

```bash
bash .claude/skills/run-rafiki/driver.sh
```

It prints a temp dir holding `portal.png`, `viewer.png`, `studio.json`,
`card.png`, `video-edl.json`, `canva-export.json`, and `notion-export.json`.
Open the PNGs, or `Read` them. `viewer.png`
shows the real image grid for the first project under `output/`; `portal.png`
shows the Rafiki Suite shell (Library / Subjects / Studio / Jobs / Styles /
Video Lab tabs); `card.png` is the Puppeteer HTML→PNG renderer output. The
Studio step POSTs `{"mode":"single","dry_run":true,...}` to `/api/regen` — the
exact call the Studio "Dry Run" button makes — and asserts `generated == total`
(prints `ok: generated 1/1, run <id>`). It targets a throwaway project
`_driver-studio-smoke` and removes it afterward (dry-run still writes a run
dir; `output/` is gitignored). The Video Lab step GETs
`/api/media/selections/edl` (the "Export EDL" button) and asserts a valid
`rafiki-video-edl` payload — `clip_count` is 0 on a fresh checkout (no
selections yet), but the EDL structure is still emitted. The Canva step POSTs
`{"action":"canva-export","dry_run":true,...}` to `/api/actions` (a mutating
action, so dry-run skips the confirm guard) and asserts `dry_run:true`,
`mutating:false`, and a `.zip` `result_path` — it counts source images and
reports the would-be zip path **without writing it**. The Notion step POSTs
`{"action":"notion-export","dry_run":true,...}` (an `external` action) and
asserts `external:false` + empty `errors` — it reports what *would* be exported
with **no Notion token and no network call**.

Override Chrome if the auto-detect misses: `CHROME=/path/to/chrome bash .claude/skills/run-rafiki/driver.sh`.

### Build + screenshot a viewer by hand

The viewer is the most reliable content-rich GUI on a fresh checkout (see
Gotchas re: the portal Library tab):

```bash
./.venv/bin/python generate.py library          # index every run-* under output/
./.venv/bin/python generate.py view ed-ai-logo  # writes output/ed-ai-logo/viewer.html
```

Then screenshot the produced `viewer.html` with headless Chrome (this is what
the driver does internally):

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --hide-scrollbars --window-size=1440,1400 \
  --virtual-time-budget=5000 \
  --screenshot=/tmp/rafiki-viewer.png \
  "file://$PWD/output/ed-ai-logo/viewer.html"
```

### Launch the portal manually

```bash
./.venv/bin/python generate.py serve --port 7433 --output-dir output
# -> Rafiki portal → http://localhost:7433/   (Ctrl-C to stop)
curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://localhost:7433/   # HTTP 200
```

`/api/runs` returns the indexed runs as JSON — handy for asserting content
without a browser.

## No-spend smokes (logic coverage)

These already ship in the repo and are the right check for CLI / MCP / portal
changes:

```bash
npm run smoke:dry-run   # CLI + MCP-bridge dry-run; prints {"ok": true, ...}
npm run e2e:portal      # launches portal, validates DOM/layout metrics
```

Single-surface spot checks that spend nothing:

```bash
node index.js examples/quickstart-image-prompts.md --dry-run --no-viewer
# HTML -> PNG (writes alongside the .html as <name>.png):
printf '<!doctype html><body>card</body>' > /tmp/card.html && node index.js --render /tmp/card.html
```

## Run (human path)

`npm run generate -- ...` / `npx rafiki ...` is the same CLI without the
`node index.js` prefix. `python generate.py serve --open` opens the portal in
a browser — useless headless, fine on a desktop.

## Test

```bash
npm test    # node scripts/run-pytest.js — 328 passed in ~27s
```

## Gotchas

- **Portal Library / Subjects / Styles / Jobs tabs are empty on a fresh
  checkout, even with runs present.** They are all backed by the *media-archive
  registry* (`/api/media`, `/api/media/subjects`, `/api/media/styles`), which
  is empty until you populate it — Library shows "0 shown · 0 indexed",
  Subjects shows "No subjects indexed", Styles is blank. The actual run content
  lives under `/api/runs` and is surfaced by `generate.py view <project>`. Use
  the **viewer**, not the portal Library tab, to see images out of the box.
  Note: the portal Styles tab reads the media registry, which is *not* the same
  as the 14 generation style packs in `styles/*.md` used by `--style`.
- **Studio and Video Lab are the content-rich tabs that work standalone.**
  Studio has Image Studio / LoRA Training / Video Generation forms (each with a
  Dry Run button and an "Execute provider call" + "Confirm execute spend"
  double-guard before any spend); Video Lab has the Selection EDL export/import.
  Neither depends on the media registry.
- **`--dry-run` still writes a run directory** (e.g. `examples/images/run-<ts>/`
  with the manifest) even though it generates no images. Clean these up if you
  don't want them.
- **`generate.py library` must run before the portal will report indexed media**
  for a given `--output-dir`; the driver does this for you.
- **`--output-dir` matters.** The portal/library default to `output/`. Point
  them elsewhere and you'll see an empty index — not a bug.
- Provider keys are only needed for real generation. `--doctor` will report
  keys as set/unset but every path in this skill works with them blank.

## Troubleshooting

- **`zsh: command not found: timeout`** — macOS has no `timeout`. Drop it or
  use `gtimeout` (coreutils).
- **Driver: "no Chrome/Chromium found"** — set `CHROME=/path/to/chrome`. On a
  Mac the default is `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`.
- **Portal screenshot is blank/empty grid** — you screenshotted the Library
  tab before populating the media registry. Expected; use the viewer instead.
- **`portal exited early`** from the driver — read the printed `portal.log`;
  usually a port already in use (the driver auto-picks a free one, so this
  means the chosen port raced) — just re-run.

## The driver

`.claude/skills/run-rafiki/driver.sh` — Bash. Detects Chrome, picks a free
port, builds the index, launches `generate.py serve`, screenshots the portal
and a run viewer, runs a Studio Dry Run via `/api/regen`, renders an HTML card
to PNG, exports a Video Lab EDL via `/api/media/selections/edl`, runs Canva and
Notion export dry-runs via `/api/actions`, then tears the server down on exit.
Scoped to the GUI screenshot + portal-action + renderer flow the repo's own
`smoke:dry-run` / `e2e:portal` scripts don't cover.

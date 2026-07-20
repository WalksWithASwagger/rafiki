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

- Node.js ≥ 22.12 (verified on v22.22.3) + npm ≥ 10.
- Python ≥ 3.11 (verified on 3.12.13).
- Google Chrome (Puppeteer/headless). `--doctor` reports the path it found.

## Build

From a clean checkout (idempotent against the committed lockfile — ~5s for npm):

```bash
npm ci
npm --prefix frontend ci
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
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
HTML card to PNG, exports a Video Lab EDL, runs dry-runs of all five portal
`/api/actions` (Canva, Notion, registry, static-deploy, approve-starred), plans
LoRA training and video generation jobs, reads the usage/spend summary, then
calls the `rafiki_status` MCP tool. No keys, no spend.

```bash
bash .agents/skills/run-rafiki/driver.sh
```

It prints a temp dir holding the artifacts below. Open the PNGs, or `Read`
them. Each step drives the exact endpoint the matching portal button calls;
every write path is a `dry_run`/plan, so nothing spends or mutates.

| # | Artifact | Step (endpoint) | Asserts |
|---|---|---|---|
| 1 | `portal.png` | Portal screenshot | Rafiki Suite shell (Library/Subjects/Studio/Jobs/Styles/Video Lab) |
| 2 | `viewer.png` | Run-viewer screenshot | real image grid for the first project under `output/` |
| 3 | `studio.json` | Studio Dry Run — `POST /api/regen` (`dry_run:true`) | `generated == total` |
| 4 | `card.png` | `node index.js --render` (Puppeteer HTML→PNG) | non-empty PNG |
| 5 | `video-edl.json` | "Export EDL" — `GET /api/media/selections/edl` | valid `rafiki-video-edl` (0 clips on a fresh checkout) |
| 6 | `canva-export.json` | `POST /api/actions` canva-export dry-run (mutating) | `mutating:false`, `.zip` `result_path`, **no zip written** |
| 7 | `notion-export.json` | `POST /api/actions` notion-export dry-run (external) | `external:false`, empty `errors`, **no token/network** |
| 8 | `static-deploy.json` | `POST /api/actions` static-deploy dry-run (external) | `external:false`, empty `url`, `vercel` `command`, **no deploy** |
| 9 | `approve-starred.json` | `POST /api/actions` approve-starred dry-run (mutating) | `mutating:false`, int `approved_count`, **nothing copied to `approved/`** |
| 10 | `registry-export.json` | `POST /api/actions` registry-export dry-run | int `count`, `.csv` `path`, **file not rewritten** |
| 11 | `train-lora.json` | `POST /api/jobs/train-lora` (no `execute`) | `status:"dry-run"`, `$0.0` cost, `0` network calls |
| 12 | `video-generate.json` | `POST /api/jobs/video-generate` (no `execute`) | `status:"dry-run"`, `$0.0` cost, `0` network calls |
| 13 | `usage.json` | `GET /api/usage` (read-only, from local manifests) | int `usage_log.entries` and `archive.projects/runs/images` |
| 14 | `mcp-status.json` | `mcp_server.rafiki_status()` (MCP tool, no HTTP) | `repo_root` set; `rafiki_status`/`rafiki_run` registered |

Steps that write a manifest (Studio, LoRA, video) use throwaway projects
(`_driver-studio-smoke`, `_driver-lora-smoke`, `driver-video-smoke`) and remove
them on the way out; `output/` is gitignored regardless. The server is torn
down on exit.

Override Chrome if the auto-detect misses: `CHROME=/path/to/chrome bash .agents/skills/run-rafiki/driver.sh`.

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

`.agents/skills/run-rafiki/driver.sh` — Bash. Detects Chrome, picks a free
port, builds the index, launches `generate.py serve`, screenshots the portal
and a run viewer, runs a Studio Dry Run via `/api/regen`, renders an HTML card
to PNG, exports a Video Lab EDL via `/api/media/selections/edl`, dry-runs all
five portal `/api/actions` (Canva, Notion, registry, static-deploy,
approve-starred), plans LoRA training and video generation jobs via
`/api/jobs/*`, reads `/api/usage`, calls the `rafiki_status` MCP tool, then
tears the server down on exit. Scoped to the GUI screenshot + portal-action +
renderer + MCP flow the repo's own `smoke:dry-run` / `e2e:portal` scripts don't
cover.

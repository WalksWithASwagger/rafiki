# Rafiki

**Rafiki** is the standalone CLI for **AI image generation** (Google Gemini + OpenAI) and **HTML → PNG** rendering (Puppeteer). It grew out of the KK / BC + AI knowledge base image pipeline; this repository is the **canonical** home.

**One folder = all of Rafiki.** Clone this repo into a directory named `rafiki` (recommended). Everything you need to run and extend the tool — Node CLI, Python generator, styles, prompts, docs — lives **only** inside that checkout. See [docs/FOLDER-LAYOUT.md](docs/FOLDER-LAYOUT.md).

The npm package is **`rafiki`**. The **`image-gen`** command remains available as a **backward-compatible alias** (same `index.js`).

**Repository:** [github.com/WalksWithASwagger/rafiki](https://github.com/WalksWithASwagger/rafiki)

**Scope:** CLI + local portal. See [docs/SCOPE.md](docs/SCOPE.md).

## Features

- **Multi-provider AI generation**: Gemini (`gemini-2.5-flash-image`, `gemini-3-pro-image-preview`) and OpenAI (`gpt-image-2`, `dall-e-3`) via a unified CLI
- **Run isolation**: Each batch creates a timestamped `run-YYYYMMDD-HHMMSS/` directory — generations are never overwritten
- **Comparison viewer**: HTML gallery with tabs to switch runs, side-by-side compare mode, and lightbox with keyboard nav
- **Prompts on cards**: Every card shows the prompt that generated it (3-line clamp, full text in lightbox)
- **Lightbox**: Full-screen image with one-click download and copy-prompt button
- **Grid resize slider**: Drag to scale cards from thumbnail to large — preference saved in `localStorage`
- **Star / Reject ratings**: Rate images from the viewer; ratings persist in `output/ratings.json` (server mode) or `localStorage` (file://)
- **Filter bar**: All / ★ Starred / ✕ Rejected / Unreviewed with live counts; plus aspect-ratio and style chips in the library
- **Search + sort**: Live text search across prompts; sort by newest / oldest / project / model
- **Master library viewer**: `generate.py library` — single page spanning all projects, with project + model + AR + style filter chips
- **Local portal**: `generate.py serve` — starts a localhost server with persistent ratings API, cross-project search, and live viewer rebuild on page load
- **Project registry**: `config/extra-outputs.json` — register image directories from other repos so the portal and library find them without copying files
- **Lightbox metadata**: Lightbox panel shows model, style, aspect ratio, run ID, timestamp, prompt file
- **Viewer rebuild**: `generate.py view <project> [--all-runs]` — regenerate viewers from disk without re-generating images
- **HTML rendering**: Puppeteer for diagrams, charts, quote cards
- **Batch processing**: Parse `image-prompts.md` files (numbered sections + blockquote prompts)
- **Style packs**: KK / HOPECODE / BCAI / Upgrade / Zine / GNI (YAML + markdown guides)
- **Usage tracking**: Local `data/usage-log.json` (gitignored) — logs every API call (success and failure) with full prompt, model, style

## Setup

### 1. Install dependencies

```bash
git clone https://github.com/WalksWithASwagger/rafiki.git rafiki
cd rafiki

npm install

# Python: local venv (recommended on macOS / Homebrew Python — PEP 668)
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

`generate.py` uses the **`google-genai`** SDK (`pip install google-genai`), not the legacy `google-generativeai` package.

The CLI uses `rafiki/.venv/bin/python3` when that venv exists; otherwise it falls back to `python3` on your `PATH`.

### 2. API keys

```bash
cp .env.example .env
# Edit .env:
#   GOOGLE_API_KEY=...    (required for Gemini — https://aistudio.google.com/app/apikey)
#   OPENAI_API_KEY=...    (required for gpt-image-2, dall-e-3)
```

Run commands from the **repository root** (this directory) so `dotenv` loads `.env`, or export `GOOGLE_API_KEY` in your shell.

## Usage

Paths below are **examples**. Point at any checkout: your KB clone, a temp folder, etc.

Use **`npx rafiki`** (or globally: `rafiki`). You can still run **`npx image-gen`** where that bin is installed — it is the same program.

### AI image generation

```bash
# Single prompt
npx rafiki --prompt "A creative professional at a mixing console" --output hero.png

# From image-prompts.md (path to your file)
npx rafiki /path/to/your/article/image-prompts.md

# With style and output directory
npx rafiki /path/to/prompts/hopecode/personal-blog-examples.md \
  --style hopecode \
  --output-dir /path/to/images/

npx rafiki /path/to/image-prompts.md \
  --model gemini-3-pro-image-preview \
  --aspect-ratio 16:9 \
  --resolution 2K \
  --style kk \
  --output-dir /path/to/images/

npx rafiki /path/to/image-prompts.md --style hopecode --dry-run
npx rafiki --usage
npx rafiki --list-styles
```

### HTML rendering (Puppeteer)

Chrome resolution is documented in [docs/CHROME-PUPPETEER.md](docs/CHROME-PUPPETEER.md).

```bash
npx rafiki --render /path/to/graphics/hero.html
npx rafiki --render-dir /path/to/graphics/
```

### Python directly

```bash
./.venv/bin/python generate.py --prompt "Your prompt" --output image.png
./.venv/bin/python generate.py --prompt-file image-prompts.md --output-dir ./images/
```

### Reference images

```bash
npx rafiki \
  --prompt "Add certification text below this logo, same style" \
  --reference-image /path/to/logo.png \
  --model gemini-3-pro-image-preview \
  --output /path/to/out.png

npx rafiki /path/to/logo-variations.md \
  --reference-image /path/to/brand-logo.png \
  --model gemini-3-pro-image-preview \
  --resolution 2K \
  --output-dir /path/to/outputs/

npx rafiki /path/to/prompts.md \
  --reference-images "/path/a.png,/path/b.png,/path/c.png" \
  --output-dir /path/to/outputs/
```

**Mockup mode** (keep garment photo, add print): `--reference-role mockup`.

## Models

| Model | Provider | Speed | Resolution | Best for |
|-------|----------|-------|------------|----------|
| `gemini-2.5-flash-image` | Gemini | Fast | 1K | Quick iterations |
| `gemini-3-pro-image-preview` | Gemini | Slower | up to 4K | Final assets, text |
| `gpt-image-2` | OpenAI | Medium | up to 1536px | Photorealistic, text |
| `gpt-image-1` | OpenAI | Medium | up to 1024px | Balanced |
| `dall-e-3` | OpenAI | Medium | up to 1792px | Artistic, precise |

Pass model ID directly: `-m gpt-image-2` or `-m gemini-2.5-flash-image`.

## Styles

| Style | Notes |
|-------|--------|
| `kk` (default) | Dark editorial, teal / purple |
| `hopecode` | Solarpunk, organic, earth tones |
| `bcai` | Mycelial / community diagrams |
| `upgrade` | Bold training / transformation marketing |
| `zine` | Punk BWR — xerox grain, ransom-note type (WAIFF decks) |
| `gni` | Cosmic editorial — space-blue orbital diagrams (GNI journalism) |
| `femme` | Abstract body-compute metaphors (MAC community; review outputs) |
| `indigenomics` | Ancestral-wisdom + tech sovereignty diagrams (community review for nation-specific symbols) |

```bash
npx rafiki --prompt "..." --style hopecode
npx rafiki --prompt "..." --no-style
npx rafiki --list-styles
```

Guides: [styles/kk.md](styles/kk.md), [styles/hopecode.md](styles/hopecode.md), [styles/bcai.md](styles/bcai.md), [styles/upgrade.md](styles/upgrade.md).

Example prompt libraries live under [prompts/](prompts/). The **KK knowledge base** diagram + image prompt bundle (HOPECODE, GNI, Web Summit zine, WAIFF keynote, MAC femme, Wikipedia Five Futures, `gpt-image-1` batch spec + HOPECODE `.txt`) is consolidated in **[`prompts/kk-kb/`](prompts/kk-kb/README.md)**; the Streamlit `gpt-image-1` batch UI is under [`tools/gpt-image-batch-ui/`](tools/gpt-image-batch-ui/README.md).

## Aspect ratio presets

`linkedin` (16:9), `instagram` (1:1), `twitter` (16:9), `story` (9:16), `square` (1:1) — pass as `--aspect-ratio`.

## `image-prompts.md` format

```markdown
## 1. Hero Image — Title
**For:** Article header, LinkedIn
**Prompt:**
> A creative professional standing at a mixing console...

## 2. Quote Card — Key Message
**For:** Social media, pull quote
**Prompt:**
> Clean typography on dark background...
```

After `**Prompt:**`, lines starting with `>` form the prompt (multi-line blockquotes supported).

You can also add per-prompt metadata fields — they override the batch CLI defaults:
```markdown
## 1. Hero Banner
**For:** LinkedIn header
**Aspect Ratio:** 16:9
**Model:** gpt-image-2
**Style:** kk
**Quality:** high
**Prompt:**
> ...
```

## Run isolation and the viewer

Every batch run saves to a timestamped subdirectory:
```
output/<project>/
  run-20260425-093605/
    01-hero.png
    02-card.png
    run.json          ← metadata: model, style, timestamps, image list
    viewer.html       ← single-run gallery (shareable)
  latest → run-20260425-093605/   ← symlink to most recent
  viewer.html         ← comparison viewer across all runs
output/library.html   ← master library spanning all projects
```

Open `output/<project>/viewer.html` in a browser to:
- Switch between runs via tabs at the top
- Click **⊞ Compare all** to see every prompt slot side-by-side across runs
- Click any image to open fullscreen lightbox (arrow keys / Esc to navigate); download or copy prompt from the lightbox toolbar
- **★ Star** or **✕ Reject** individual images — ratings persist in `localStorage`
- Filter the grid: **All / ★ Starred / ✕ Rejected / Unreviewed**
- Drag the **Grid** slider to resize cards

### Rebuild viewers without re-generating

```bash
# Rebuild comparison viewer (re-checks which files exist on disk)
python generate.py view philadelphia

# Rebuild all per-run viewers too
python generate.py view philadelphia --all-runs

# Rebuild master library (all projects in one page)
python generate.py library

# Build and open in browser
python generate.py library --open
```

### Local portal (server mode)

```bash
# Start portal, open browser automatically
python generate.py serve --open

# Custom port
python generate.py serve --port 8080
```

The portal runs at `http://localhost:7433/`. Features over the static file:// viewers:

- **Persistent ratings** — stored in `output/ratings.json` on disk; survive page reloads and viewer rebuilds
- **Cross-project search** — live text filter across all prompts in the library
- **Library rebuilt on every page load** — always reflects the current state of disk
- **Ratings API** — `GET /api/ratings`, `POST /api/ratings`; viewer JS syncs automatically

### Project registry

Images can live anywhere on disk — register their directory in `config/extra-outputs.json` and the portal and library will find them:

```json
{
  "cmvan-keynote": "/Users/you/Code/cmvan-keynote/assets/generated/slides",
  "another-project": "/path/to/another/project/images"
}
```

The virtual path `<project-name>/<run-id>/<file.png>` is used consistently as the image URL, rating key, and deduplication key. Extra-root projects take precedence over any same-named directory under `output/`.

For file:// mode (no server), run `python generate.py link-projects` to create symlinks in `output/` pointing at registered external directories.

## Repository layout

```
rafiki/
├── generate.py          # Python CLI entry — generation, view, library, serve subcommands
├── requirements.txt
├── index.js             # Node CLI (AI + Puppeteer render)
├── package.json
├── config/
│   └── extra-outputs.json  # Project registry — maps project names to external image dirs
├── styles/              # styles.yaml + per-style markdown guides
├── prompts/             # Prompt libraries (kk/, bcai/, hopecode/, upgrade/, kk-kb/)
├── examples/            # Long-form workflow notes
├── lib/
│   ├── batch.py         # Parallel batch runner + run isolation
│   ├── core.py          # Single-image generate_image()
│   ├── models.py        # Model aliases + resolution
│   ├── prompts.py       # parse_image_prompts_md()
│   ├── server.py        # Localhost portal server (ratings API, static serving)
│   ├── styles.py        # Style suffix resolution
│   ├── usage.py         # Usage log (data/usage-log.json)
│   └── renderers/
│       ├── viewer.py    # Single-run + comparison viewer HTML
│       └── library.py   # Master library viewer HTML + extra-roots scanner
├── data/                # usage-log.json (gitignored)
├── output/              # Generated images + viewers (gitignored)
│   ├── <project>/       # Per-project run tree
│   ├── library.html     # Master library across all projects
│   └── ratings.json     # Persistent star/reject ratings (gitignored)
└── docs/
    ├── SCOPE.md
    ├── FOLDER-LAYOUT.md
    ├── CHROME-PUPPETEER.md
    ├── image-pipeline-analysis.md
    └── image-pipeline-operator.md
```

## Consuming from another monorepo (e.g. kk-ai-ecosystem)

Keep **one** Rafiki checkout on disk (this repo). The KB repo does **not** duplicate source — it uses a shim.

- **Recommended layout on disk:**

  ```
  <parent>/
    rafiki/              ← ONLY place Rafiki source lives (this git repo)
    kk-ai-ecosystem/     ← KB; contains tools/image-gen = shim + KB outputs only
  ```

- **Sibling clone:** `git clone https://github.com/WalksWithASwagger/rafiki.git rafiki` next to `kk-ai-ecosystem/`. From the KB, `cd tools/image-gen && npx rafiki …` forwards here.
- **Custom path:** set **`RAFIKI_HOME`** (or legacy **`IMAGE_GEN_HOME`**) to this repo’s root.
- **npm:** `npm install https://github.com/WalksWithASwagger/rafiki.git` or depend on package name `rafiki`.

## License

MIT — see [LICENSE](LICENSE).

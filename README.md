# Rafiki

**Rafiki** is the standalone CLI for **AI image generation** (Google Gemini “Nano Banana” image models) and **HTML → PNG** rendering (Puppeteer). It grew out of the KK / BC + AI knowledge base image pipeline; this repository is the **canonical** home.

**One folder = all of Rafiki.** Clone this repo into a directory named `rafiki` (recommended). Everything you need to run and extend the tool — Node CLI, Python generator, styles, prompts, docs — lives **only** inside that checkout. See [docs/FOLDER-LAYOUT.md](docs/FOLDER-LAYOUT.md).

The npm package is **`rafiki`**. The **`image-gen`** command remains available as a **backward-compatible alias** (same `index.js`).

**Repository:** [github.com/WalksWithASwagger/rafiki](https://github.com/WalksWithASwagger/rafiki)

**Scope:** CLI-only for v1 — no HTTP service. See [docs/SCOPE.md](docs/SCOPE.md).

## Features

- **AI generation**: Gemini image models via `google-genai` (Python) with a Node entrypoint
- **HTML rendering**: Puppeteer for diagrams, charts, quote cards
- **Batch processing**: Parse `image-prompts.md` files (numbered sections + blockquote prompts)
- **Style packs**: KK / HOPECODE / BCAI / Upgrade (YAML + markdown guides)
- **Usage tracking**: Optional local `data/usage-log.json` (gitignored by default)

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

### 2. API key

Create a [Google AI Studio API key](https://aistudio.google.com/app/apikey).

```bash
cp .env.example .env
# Edit .env — set GOOGLE_API_KEY=...
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

| Model | Speed | Resolution | Best for |
|-------|-------|------------|----------|
| `gemini-2.5-flash-image` | Fast | 1K | Quick iterations |
| `gemini-3-pro-image-preview` | Slower | up to 4K | Final assets, text |

## Styles

| Style | Notes |
|-------|--------|
| `kk` (default) | Dark editorial, teal / purple |
| `hopecode` | Solarpunk, organic, earth tones |
| `bcai` | Mycelial / community diagrams |
| `upgrade` | Bold training / transformation marketing |

```bash
npx rafiki --prompt "..." --style hopecode
npx rafiki --prompt "..." --no-style
npx rafiki --list-styles
```

Guides: [styles/kk.md](styles/kk.md), [styles/hopecode.md](styles/hopecode.md), [styles/bcai.md](styles/bcai.md), [styles/upgrade.md](styles/upgrade.md).

Example prompt libraries live under [prompts/](prompts/).

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

## Repository layout

```
rafiki/
├── generate.py          # Python Gemini image generator
├── requirements.txt
├── index.js             # Node CLI (AI + Puppeteer render)
├── package.json
├── styles/              # styles.yaml + per-style docs
├── prompts/             # Example prompt libraries
├── examples/            # Long-form workflow notes
├── lib/                 # Optional helpers used by some flows
├── data/                # usage-log.json (optional, gitignored)
└── docs/
    ├── SCOPE.md
    ├── CHROME-PUPPETEER.md
    └── FOLDER-LAYOUT.md
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

# image-gen

Standalone CLI for **AI image generation** (Google Gemini “Nano Banana” image models) and **HTML → PNG** rendering (Puppeteer). Originally developed for the KK / BC + AI knowledge base; this repository is the **canonical** implementation.

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
git clone <your-fork-or-upstream-url> image-gen
cd image-gen

npm install

# Python: local venv (recommended on macOS / Homebrew Python — PEP 668)
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

`generate.py` uses the **`google-genai`** SDK (`pip install google-genai`), not the legacy `google-generativeai` package.

The `npx image-gen` CLI uses `image-gen/.venv/bin/python3` when that venv exists; otherwise it falls back to `python3` on your `PATH`.

### 2. API key

Create a [Google AI Studio API key](https://aistudio.google.com/app/apikey).

```bash
cp .env.example .env
# Edit .env — set GOOGLE_API_KEY=...
```

Run commands from the **repository root** (this directory) so `dotenv` loads `.env`, or export `GOOGLE_API_KEY` in your shell.

## Usage

Paths below are **examples**. Point at any checkout: your KB clone, a temp folder, etc.

### AI image generation

```bash
# Single prompt
npx image-gen --prompt "A creative professional at a mixing console" --output hero.png

# From image-prompts.md (path to your file)
npx image-gen /path/to/your/article/image-prompts.md

# With style and output directory
npx image-gen /path/to/prompts/hopecode/personal-blog-examples.md \
  --style hopecode \
  --output-dir /path/to/images/

npx image-gen /path/to/image-prompts.md \
  --model gemini-3-pro-image-preview \
  --aspect-ratio 16:9 \
  --resolution 2K \
  --style kk \
  --output-dir /path/to/images/

npx image-gen /path/to/image-prompts.md --style hopecode --dry-run
npx image-gen --usage
npx image-gen --list-styles
```

### HTML rendering (Puppeteer)

Chrome resolution is documented in [docs/CHROME-PUPPETEER.md](docs/CHROME-PUPPETEER.md).

```bash
npx image-gen --render /path/to/graphics/hero.html
npx image-gen --render-dir /path/to/graphics/
```

### Python directly

```bash
./.venv/bin/python generate.py --prompt "Your prompt" --output image.png
./.venv/bin/python generate.py --prompt-file image-prompts.md --output-dir ./images/
```

### Reference images

```bash
npx image-gen \
  --prompt "Add certification text below this logo, same style" \
  --reference-image /path/to/logo.png \
  --model gemini-3-pro-image-preview \
  --output /path/to/out.png

npx image-gen /path/to/logo-variations.md \
  --reference-image /path/to/brand-logo.png \
  --model gemini-3-pro-image-preview \
  --resolution 2K \
  --output-dir /path/to/outputs/

npx image-gen /path/to/prompts.md \
  --reference-images "/path/a.png,/path/b.png,/path/c.png" \
  --output-dir /path/to/outputs/
```

**Mockup mode** (keep garment photo, add print): `--reference-role mockup` — see previous monorepo README behavior; same flags apply.

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
npx image-gen --prompt "..." --style hopecode
npx image-gen --prompt "..." --no-style
npx image-gen --list-styles
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
image-gen/
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
    └── CHROME-PUPPETEER.md
```

## Consuming from another monorepo

- **Sibling clone:** place this repo next to your KB (e.g. `notion-local/image-gen` beside `notion-local/kk-ai-ecosystem`) and use the shim in `kk-ai-ecosystem/tools/image-gen` (`npx image-gen` from there), or set **`IMAGE_GEN_HOME`** to this directory.
- **npm:** `npm install /absolute/path/to/image-gen` or publish to a registry and depend on the package name.

## License

MIT — see [LICENSE](LICENSE).

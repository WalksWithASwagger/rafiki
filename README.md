# Rafiki

Rafiki is a local-first workflow for AI image generation, batch prompt runs,
reviewing outputs in a browser, and rendering HTML to PNG.

It combines:

- a Node CLI entry point: `rafiki` and the legacy alias `image-gen`
- a Python generation engine for Gemini and OpenAI image models
- a local review portal for comparing runs, rating outputs, and browsing a
  project library
- a Puppeteer-based HTML-to-image renderer for cards, diagrams, and slide art

Rafiki is designed to run from a checkout on your machine. Your API keys stay
local. There is no hosted Rafiki service.

## Status

Rafiki is ready for real work. The recommended install path is: clone the repo,
install dependencies, run locally. Roadmap: [docs/ROADMAP.md](docs/ROADMAP.md).

## What Rafiki Does

- Generate single images from a prompt
- Run batches from Markdown prompt files
- Keep every batch in an isolated `run-*` directory
- Rebuild viewers without re-running generation
- Review outputs in a local comparison viewer and library
- Rate images as starred, rejected, or unreviewed
- Render HTML files to PNG with Puppeteer
- Register image outputs from other directories on disk
- Export approved assets for downstream workflows

## Quickstart

### 1. Clone and install

```bash
git clone https://github.com/WalksWithASwagger/rafiki.git
cd rafiki

npm install

python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/pip install -r requirements-dev.txt
```

### 2. Add provider keys

```bash
cp .env.example .env
```

Add at least one of:

- `GOOGLE_API_KEY` for Gemini models
- `OPENAI_API_KEY` for OpenAI image models

### 3. Run setup diagnostics

```bash
npm run doctor
```

Or:

```bash
npx rafiki --doctor
```

### 4. Generate something

```bash
npx rafiki --prompt "A cinematic portrait of a radio host in a neon-lit studio" \
  --output output.png
```

For a public batch fixture:

```bash
npx rafiki examples/quickstart-image-prompts.md --dry-run --no-viewer
```

## Common Workflows

### Single prompt

```bash
npx rafiki --prompt "A creative strategist sketching a systems map" --output hero.png
```

### Batch prompt file

```bash
npx rafiki /path/to/image-prompts.md --output-dir /path/to/output/project
```

### Styled generation

```bash
npx rafiki /path/to/image-prompts.md \
  --style hopecode \
  --output-dir /path/to/output/project
```

### No style suffix

```bash
npx rafiki --prompt "Minimal monochrome diagram" --no-style --output diagram.png
```

### Reference images

```bash
npx rafiki \
  --prompt "Keep the composition, modernize the visual language" \
  --reference-image /path/to/reference.png \
  --output output.png
```

### HTML to PNG

```bash
npx rafiki --render /path/to/card.html
npx rafiki --render-dir /path/to/html-assets/
```

### Python directly

```bash
./.venv/bin/python generate.py --prompt "Your prompt" --output image.png
./.venv/bin/python generate.py --prompt-file image-prompts.md --output-dir ./images/
```

## MCP

Rafiki can be installed as a local MCP server so Codex, Claude Code, and other
MCP clients can call it as tools instead of shelling out manually.

```bash
codex mcp add rafiki -- /path/to/rafiki/.venv/bin/python /path/to/rafiki/mcp_server.py
claude mcp add --scope user rafiki -- /path/to/rafiki/.venv/bin/python /path/to/rafiki/mcp_server.py
```

Exposed tools include `rafiki_generate`, `rafiki_batch`,
`rafiki_list_styles`, `rafiki_usage`, `rafiki_status`, and `rafiki_run` for
the broader `generate.py` CLI surface.

Details: [docs/MCP.md](docs/MCP.md)

## Local Portal

Start the portal:

```bash
python generate.py serve --open
```

By default it runs on `http://localhost:7433/`.

The portal adds:

- persistent ratings stored on disk
- cross-project browsing and search
- lightbox review
- run detail with feedback, evaluation decisions, and local metadata
- run-level decision summaries
- library rebuilding on page load
- prompt studio for single prompts and Markdown batches

The prompt studio writes into `output/<project>/run-*` using the same
generation path as the CLI, so portal-generated runs show up in the normal
viewer and library flow.

Useful commands:

```bash
python generate.py view <project>
python generate.py view <project> --all-runs
npx rafiki view <project> --all-runs
python generate.py library
python generate.py library --open
python generate.py archive-health --cleanup-report
npm run smoke:dry-run
```

`library` builds the full local archive: every `run-*` image under `output/`
and any configured extra-output roots, with approval state overlaid from
`approved/index.json` when available.

## Prompt File Format

Rafiki batch runs parse numbered Markdown sections with blockquote prompts:

```markdown
## 1. Hero Image
**For:** Article header
**Prompt:**
> A documentary-style portrait of a community organizer...

## 2. Quote Card
**For:** Social media
**Prompt:**
> Bold editorial typography over textured paper grain...
```

Per-prompt overrides are supported:

```markdown
## 1. Hero Banner
**Aspect Ratio:** 16:9
**Model:** gpt-image-2
**Style:** kk
**Quality:** high
**Prompt:**
> ...
```

## Models

Rafiki supports both Gemini and OpenAI image models through the same CLI.

- `gemini-2.5-flash-image`: fast iteration
- `gemini-3-pro-image-preview`: higher-end Gemini image generation
- `gpt-image-2`: strong general-purpose OpenAI image generation
- `gpt-image-1`
- `dall-e-3`

The CLI, portal, and MCP default is `gemini-2.5-flash-image`. Pass `--model`
to select another provider or model explicitly. Choose Gemini for fast local
iteration and Gemini Pro reference or high-resolution work. Choose OpenAI when
the prompt set was authored against OpenAI outputs, when you need OpenAI-only
model behavior, or when using the separate `gpt-image-1` Streamlit workflow.

Details: [docs/MODEL-POLICY.md](docs/MODEL-POLICY.md)

## Prompt And Media Boundary

The public npm package intentionally excludes private prompt libraries,
campaign media, mirrored knowledge-base prompts, generated outputs, and local
asset folders. It includes only a tiny onboarding fixture:
`examples/quickstart-image-prompts.md`.

Details: [docs/PROMPT-MEDIA-POLICY.md](docs/PROMPT-MEDIA-POLICY.md)

## Styles

Built-in styles are configured in `styles/styles.yaml` and can be composed
with `+`.

Examples (not exhaustive):

- `kk`
- `hopecode`
- `bcai`
- `futureproof-mythic`
- `bcai-ecosystem`
- `upgrade`
- `zine`
- `gni`
- `femme`
- `indigenomics`
- `cmvan`

Useful commands:

```bash
npx rafiki --list-styles
npx rafiki --prompt "..." --style kk+bcai
```

## External Project Registry

If you want the portal and library to include outputs that live outside this
repo, copy the example file and create a local override:

```bash
cp config/extra-outputs.json.example config/extra-outputs.local.json
```

Example:

```json
{
  "workshop-deck": "/absolute/path/to/another/project/output",
  "campaign-assets": "/absolute/path/to/a/generated-images-directory"
}
```

This file is intentionally gitignored.

For `file://` viewing without the server, create symlinks into `output/`:

```bash
python generate.py link-projects
```

## Security and Scope

- Provider keys belong in your shell environment or an untracked `.env`
- `python generate.py serve` binds to `127.0.0.1` by default
- If you use `--public`, set both `PORTAL_USERNAME` and `PORTAL_PASSWORD`
- Rafiki is a local-first tool, not a hosted multi-user platform

Read:

- [SECURITY.md](SECURITY.md)
- [docs/SCOPE.md](docs/SCOPE.md)

## Development

Useful commands:

```bash
npm test
npm run pack:check
npm run docs:check
python3 -m pytest -q
```

Contribution guide: [CONTRIBUTING.md](CONTRIBUTING.md)

## Docs

Start with the [docs index](docs/INDEX.md) for the full map.

Key references:

- [Scope](docs/SCOPE.md)
- [MCP](docs/MCP.md)
- [Command Center](docs/COMMAND-CENTER.md)
- [Asset Registry](docs/ASSET-REGISTRY.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Delivery Pipeline](docs/DELIVERY-PIPELINE.md)
- [Scheduled Regeneration](docs/SCHEDULED-REGEN.md)

## License

MIT. See [LICENSE](LICENSE).

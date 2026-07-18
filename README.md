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
The current public use-case focus is the [keynote visual workflow](docs/use-cases/keynote-visual-workflow.md):
turning talk notes into prompt packs, reviewable image candidates, slide
assets, and downstream web or social artifacts.

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

Rafiki requires Node.js 20.17+ with npm 10+ and Python 3.11+.

```bash
git clone https://github.com/WalksWithASwagger/rafiki.git
cd rafiki

npm install

python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/pip install -r requirements-dev.txt
```

### 2. Add provider keys

Rafiki commits `.env.schema` as the agent-readable environment contract. Keep
real values in your shell environment, an untracked repo-local value file, or
the user-managed shared directory at `~/.agents/env/values/`. Agents validate
the contract without reading any value file directly.

The schema optionally imports reusable provider credentials from
`.env.shared.local`, followed by `.env.rafiki.local` for repo-specific
overrides. Both imports use `pick` allowlists and `allowMissing=true`, so Rafiki
keeps its own declarations authoritative and cloud or CI checks do not depend
on this Mac. The imported allowlist is limited to `GOOGLE_API_KEY`,
`OPENAI_API_KEY`, `FLOYO_KEY`, `REPLICATE_API_TOKEN`, and `NOTION_API_KEY`.
Portal credentials, Notion database IDs, executable paths, and Rafiki-only
settings remain app-local.

The shared directory and value files are created and maintained by the user,
not by agents. The canonical directory is mode `0700`; `.env.shared.local` and
optional `.env.<repo-slug>.local` files are mode `0600`.

```bash
cp .env.example .env
```

Add at least one of:

- `GOOGLE_API_KEY` for Gemini models
- `OPENAI_API_KEY` for OpenAI image models

Varlock is intentionally kept outside Rafiki's Node dependency graph because
the app supports Node 20 while the Varlock CLI has its own runtime requirements.
Keep the application runtime unchanged. Run Varlock 1.10 with Node 22.3+ or use
the standalone CLI, then inspect and audit the contract safely:

```bash
npm run env:validate
npm run env:audit
npm run env:scan
npm run env:smoke
python3 -m pytest -q tests/test_varlock_contract.py
```

The smoke checks only that the schema's non-secret sentinel reaches a child
process. The audit command explicitly excludes generated output, dependency,
cache, and generated route-tree paths. The scan command checks staged files
only and never opts into ignored output. The focused test runs redacted load,
no-op run, and scan checks against sanitized present and missing import
fixtures; it never reads the user-managed shared directory.

When an agent needs to run a secret-dependent command, inject values
through Varlock instead of reading `.env`:

```bash
varlock run --inject vars -- npx rafiki --prompt "..." --output output.png
varlock run --inject vars -- ./.venv/bin/python generate.py --prompt "..." --output output.png
```

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

For the keynote visual workflow fixture:

```bash
npx rafiki examples/keynote-visual-workflow-prompt-pack.md --dry-run --no-viewer
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

Start the live portal shell:

```bash
python3 generate.py serve
```

By default it runs on `http://localhost:7433/`. Open
`http://localhost:7433/library` to use the current TypeScript image library or
`http://localhost:7433/generate` to build dry-run-first image generation runs.

The portal adds:

- persistent ratings stored on disk
- cross-project browsing and search
- viewer pages for image triage and metadata review
- run pages with missing-image placeholders and direct viewer links
- export, registry, health, and spend routes backed by local APIs
- generate workspace for single prompts, inline batches, Markdown prompt packs,
  model/style choices, and library/media references

The Generate route writes into `output/<project>/run-*` through the same
generation path as the CLI, so portal-generated runs show up in the normal
viewer and library flow. It defaults to dry-run; real provider calls require
explicit confirmation in the UI. Python remains the local filesystem, provider,
and API authority; the frontend is spawned behind the Python server. The legacy
rollback surfaces are available at `/legacy-suite` and `/legacy-library`.

The TypeScript portal is currently a repo-checkout capability. The public npm
package intentionally excludes `frontend/`, so `npx rafiki serve` from a package
install falls back to the legacy portal routes instead of building or starting
the React shell. See [Frontend Shell](docs/FRONTEND.md) for the package
boundary and release-policy checkpoint.

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

The GitHub repository is public, so any tracked prompt, asset, or doc should be
treated as public. Keep private prompt libraries, private reference media,
generated review outputs, and local-only paths outside the repo or untracked.

The public npm package stays narrower by design. It ships runtime code, docs,
styles, config examples, and only explicitly listed example prompt packs such
as `examples/quickstart-image-prompts.md` and
`examples/keynote-visual-workflow-prompt-pack.md`. It does not ship the
`frontend/` workspace or frontend build artifacts until a maintainer approves a
package-policy change.

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
- `.env.schema` is the committed env contract for agents; use
  `varlock load --agent --show-all` instead of reading `.env`
- agents must not run `env`, `printenv`, `varlock reveal`, raw `varlock load`,
  or any command that dumps the process environment
- Agent-invoked commands that require resolved secrets should be wrapped
  with `varlock run --inject vars --`
- `python generate.py serve` binds to `127.0.0.1` by default
- `--public` refuses to start unless both `PORTAL_USERNAME` and
  `PORTAL_PASSWORD` are set
- Rafiki is a local-first tool, not a hosted multi-user platform

Read:

- [SECURITY.md](SECURITY.md)
- [docs/SCOPE.md](docs/SCOPE.md)

## Development

Useful commands:

```bash
npm test
npm run public:check
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

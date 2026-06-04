# Product scope

## v1: CLI + local portal

This repository (**Rafiki**) ships as a **command-line tool** (`npx rafiki` / `rafiki`; alias `npx image-gen`) plus a **localhost-only HTTP portal** (`generate.py serve`). There is no multi-user auth, hosted service, or job queue in scope.

Rationale:

- Keeps deployment and security surface minimal (one API key on the operator’s machine; portal binds to 127.0.0.1 only).
- Matches how the tool is used today: agents and humans run batch jobs from a checkout.
- The local portal enables persistent ratings, cross-project search/filter, and local run launching — none of which are possible with file:// viewers alone.

## Out of scope (for now)

- Hosted image generation as a SaaS
- Per-seat billing, rate limiting, or shared usage logs across machines
- Tight coupling to any one knowledge base repository layout (consumers pass paths explicitly)
- Hosted background job orchestration or queue workers

## Portal auth (`generate.py serve`)

By default the portal binds to `127.0.0.1` and runs unauthenticated — the v1
default for solo local use.

To share the portal with a teammate on the same network, two opt-in switches
work together:

- `--public` — bind to `0.0.0.0` (all interfaces) instead of loopback.
- `PORTAL_USERNAME` + `PORTAL_PASSWORD` env vars — when **both** are set, the
  server requires HTTP Basic auth on every request (constant-time compare via
  `secrets.compare_digest`).

Combining them is the recommended pattern for team review:

```bash
PORTAL_USERNAME=team \
PORTAL_PASSWORD=$(openssl rand -hex 16) \
python generate.py serve --public
```

Running `--public` without complete credentials is refused. Run without
`--public` for solo localhost use.

## Prompt Studio

When running through `generate.py serve`, the library page includes a prompt
studio that can:

- generate a single prompt into `output/<project>/run-*`
- run a Markdown prompt file batch into `output/<project>/run-*`
- stage a revision from archive-card feedback back into the single-prompt form
- dry-run a staged revision before spending provider credits

This is intentionally local-first. The server runs the same Python generation
path as the CLI and writes into the same output tree.

## Spend and review state

The portal includes a local Spend & Review Ops panel. It summarizes run counts,
image counts, failed images, known local manifest cost amounts, pricing-profile
estimates, imported provider billing, unpriced images, model mix, and recent
runs. `config/pricing.json` contains public pricing metadata only;
`data/billing-imports.json` contains local/private billing rows and is ignored
by git. Billing exports from Gemini/OpenAI remain the source of truth for exact
spend.

Card-level notes and change requests are stored in `output/feedback.json`
through `/api/feedback`, beside `output/ratings.json`. Card-level evaluation
decisions, scores, use cases, rationale, and next steps are stored in
`output/evaluations.json` through `/api/evaluations`. Title overrides, tags,
export markers, publish markers, and superseded links are stored in
`output/archive-metadata.json` through `/api/archive-metadata`. These files are
local review state and are ignored by git with the rest of `output/`.

## MCP server (`mcp_server.py`)

Rafiki ships an MCP server so local tools can invoke image generation, style
lookup, usage, and the broader `generate.py` CLI surface as structured tool
calls. The server loads `.env` from this repo and keeps the Python generation
path canonical.

See [MCP.md](MCP.md).

## Claude Code skill

`.claude/skills/rafiki.md` (in this repo) teaches Claude Code when and how to invoke Rafiki from any project that has this checkout on the path.

## Future extension

If you need Slack, webhooks, or an internal dashboard, add a thin HTTP layer that shells out to `generate.py` or imports it as a module—**do not duplicate** the Gemini client and prompt assembly.

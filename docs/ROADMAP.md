# Rafiki Roadmap

Last reviewed: 2026-05-07

This roadmap is the maintainers' working plan for Rafiki after reviewing the
current project structure, docs, tests, and code. It replaces the older backlog
items that were already shipped and separates public-release hygiene from
product expansion.

For the public-facing release checklist, see
[PUBLIC-RELEASE-PLAN.md](PUBLIC-RELEASE-PLAN.md).

## Product Direction

Rafiki is a local-first creative operations tool:

- generate images from single prompts or Markdown prompt files
- keep every batch run isolated and reviewable
- browse, rate, approve, export, and deploy generated assets
- let local agents call the same workflows through MCP
- keep provider keys and generated outputs on the operator's machine

Rafiki v1 is not a hosted SaaS, shared queue, billing system, or multi-user
image generation platform.

## Current System Map

| Area | Primary files | Current state |
|---|---|---|
| Node CLI | `index.js`, `package.json` | `rafiki` and `image-gen` bins delegate image generation to Python and handle Puppeteer HTML rendering. |
| Python CLI | `generate.py` | Main command surface for generation, viewer rebuilds, archive cleanup, registry, deploy, exports, scheduled regen, and portal startup. |
| Core generation | `lib/core.py`, `lib/batch.py`, `lib/providers/` | Multi-provider image generation with run isolation, reference images, style composition, and parallel batch support. |
| Local portal | `lib/server.py`, `lib/renderers/library.py` | Local library, ratings API, prompt studio, auth for public binding, and run browsing. |
| Review viewers | `lib/renderers/viewer.py`, `generate-presentation-viewer.py` | Comparison viewers, reusable presentation viewers, social-copy export, and self-contained HTML mode. |
| Asset operations | `lib/archive.py`, `lib/registry.py`, `lib/exporters/` | Approved-image curation, searchable registry cache, Canva bundle export, Notion export, and Vercel deploy helper. |
| Automation | `lib/regen.py`, `config/scheduled-regen.json.example` | Scheduled regeneration jobs are configured locally and can be dry-run or executed from the CLI. |
| Agent access | `mcp_server.py`, `docs/MCP.md` | MCP server exposes direct generation tools plus a constrained `generate.py` bridge for local clients. |
| Prompt collections | `prompts/`, `styles/`, `assets/kb-import/` | Rich working examples and mirrored prompt assets exist, but public/private boundaries need clearer ownership. |
| Tests and CI | `tests/`, `.github/workflows/ci.yml` | 88 Python tests plus CI for Python tests and `npm pack --dry-run`. |

## What Is Already Shipped

- Batch generation from Markdown prompt files
- Single-prompt generation
- Gemini and OpenAI provider support
- Model aliases and style composition
- Reference image and mockup support
- Run isolation with `run-*` directories and `latest` symlink
- Per-run and comparison viewers
- Master library viewer
- Local portal with ratings and prompt studio
- Basic auth for intentionally public portal binding
- Usage log with thread-level write protection and atomic writes
- Archive approval and cleanup flows
- Reusable presentation viewer
- Self-contained presentation viewer mode
- Social post export from presentation viewer data
- Asset registry with search and CSV/JSON export
- Canva export bundle
- Notion export with dry-run and idempotency log
- Vercel static viewer deploy helper
- Scheduled regeneration config and runner
- MCP server for local agent/tool access
- NPM package allowlist and package smoke check
- Contributor, security, scope, and release docs

## Review Findings

### Structure

- The repository has a useful split between CLI, Python library modules, docs,
  prompts, and tests.
- `generate.py` is now the central command dispatcher. That is practical, but
  it is large enough that future subcommands should move toward thin command
  modules instead of continuing to grow the file indefinitely.
- Prompt collections are valuable examples, but they mix reusable public
  examples with project-specific working material and local media references.
  This is fine for the private working repo, but it needs a release policy.
- Generated output, usage logs, registries, local config, and worktrees are
  correctly ignored.

### Documentation

- The top-level README now tells a coherent v1 story: local CLI, portal,
  review flow, exports, and MCP.
- The old roadmap was stale. It listed several shipped features as gaps.
- `docs/PUBLIC-RELEASE-PLAN.md`, `docs/SCOPE.md`, `SECURITY.md`, and
  `CONTRIBUTING.md` agree on the local-first boundary.
- `docs/MCP.md` and the README currently include this machine's absolute
  install path. That is useful locally but a public-release blocker.
- The docs set is broad enough that it needs an index or "start here" map.
  Important workflow docs are discoverable only if you already know their names.

### Code

- Test coverage is now meaningful across usage logging, providers, portal
  generation, auth, registry, Canva export, Notion export, scheduled regen,
  archive cleanup, social expansion, deployment, self-contained viewers, and
  MCP wrappers.
- The core risk is not missing tests anymore; it is end-to-end drift between
  the Node CLI, Python CLI, portal, MCP bridge, and docs.
- Defaults are inconsistent at the product level: code defaults to
  `gemini-2.5-flash-image`, while prior roadmap language favored
  `gpt-image-2`. This needs an explicit decision, not quiet drift.
- The MCP server is useful now, but its `rafiki_run` bridge should keep getting
  stricter typed wrappers for high-value workflows as they stabilize.
- Cost, provenance, and asset lifecycle metadata exist only partially.

## Roadmap Themes

1. Release hygiene before expansion.
2. One canonical workflow per job, exposed consistently through CLI, portal,
   MCP, and docs.
3. Registry-backed asset management instead of repeated filesystem scanning.
4. More evidence in every run: source prompt, model, cost estimate, provenance,
   approval status, and downstream export state.
5. Keep local-first as the security and product boundary.

## Phase 0: Stabilize The Current Branch

Goal: make the current work coherent and safe to merge.

| Priority | Work | Success criteria |
|---|---|---|
| P0 | Decide whether to keep the local MCP install docs with absolute paths or convert them to placeholders plus `rafiki_status` output. | No tracked public docs contain private local paths unless explicitly marked as local-only. |
| P0 | Resolve the default model policy. | README, CLI defaults, portal default, MCP default, examples, and roadmap all say the same thing. |
| P0 | Keep the MCP server registered locally but document that registration is a local setup step, not repo state. | Codex and Claude Code can still list `rafiki`; repo docs explain portable setup. |
| P1 | Add a short docs index. | A new contributor can start from README and find scope, MCP, registry, exports, deploy, scheduled regen, archive, and presentation viewer docs in one place. |
| P1 | Add an end-to-end MCP smoke test script or test fixture. | CI or local test can start the MCP stdio server, list tools, and call `rafiki_status`. |
| P1 | Add a CLI JSON smoke test. | `generate.py --prompt ... --dry-run --json` and one batch dry-run path are covered. |

## Phase 1: Public Release Hygiene

Goal: make Rafiki safe and understandable outside this machine.

| Priority | Work | Success criteria |
|---|---|---|
| P0 | Scrub tracked local paths and private project assumptions from public docs. | `rg "/Users/kk|private|local-only"` has only intentional examples or private docs. |
| P0 | Define prompt/media release policy. | Public package/repo clearly distinguishes reusable examples from private working prompt libraries and local images. |
| P0 | Package story audit. | `npm pack --dry-run` includes all runtime files and excludes private/generated assets by design. |
| P1 | Add a public quickstart fixture. | A tiny sample `image-prompts.md` and dry-run workflow can be used without private prompt libraries. |
| P1 | Add docs lint or link smoke check. | Broken internal links are caught before release. |
| P1 | Expand `npm run doctor`. | Doctor checks MCP dependency, .env presence, Chrome/Puppeteer status, and gives precise remediation. |

## Phase 2: Workflow Reliability

Goal: make common creative workflows hard to break.

| Priority | Work | Success criteria |
|---|---|---|
| P0 | Add cross-surface regression tests. | The same generation options are verified through Python CLI, Node CLI, portal job helper, and MCP wrapper. |
| P1 | Split `generate.py` subcommands into command modules when touched. | New command work does not make the dispatcher larger. |
| P1 | Strengthen run manifests. | `run.json` records provider, model, style, prompt file, reference images, CLI/tool source, timings, and error states consistently. |
| P1 | Add cost and throughput estimates. | Usage and run summaries can answer "what did this run cost and how long did it take?" |
| P2 | Make cleanup safer. | `clean` can report reclaimable disk space and defaults to dry-run in docs. |

## Phase 3: Registry-Backed Asset Library

Goal: make the asset registry the source of truth for browsing, search, and
exports.

| Priority | Work | Success criteria |
|---|---|---|
| P0 | Connect the library viewer to registry metadata. | Library cards can show titles, captions, tags, approval status, and source prompt without custom per-viewer logic. |
| P1 | Add approval/export state to registry entries. | Registry can answer which assets are approved, exported to Notion/Canva, deployed, or stale. |
| P1 | Add registry refresh hooks after generation and curation. | Common workflows do not require the operator to remember `registry index`. |
| P2 | Consider SQLite after JSON limits are clear. | Migration only happens if JSON search/export becomes too slow or awkward. |

## Phase 4: Portal As Command Center

Goal: make the local portal the best default interface for review and curation.

| Priority | Work | Success criteria |
|---|---|---|
| P0 | Surface run status and errors better in the portal. | A failed generation shows useful error state and next action, not just missing images. |
| P1 | Add curation actions from the UI. | Starred assets can be promoted to `approved/` without leaving the portal. |
| P1 | Add export actions from the UI. | Canva bundle, Notion dry-run/export, registry export, and deploy helper are discoverable where assets are reviewed. |
| P2 | Add prompt diffing between runs. | Operators can compare prompt and setting changes across regenerations. |
| P2 | Improve long-running job behavior. | Portal generation has clearer progress, cancellation, and retry affordances while remaining local-first. |

## Phase 5: Agent And Automation Layer

Goal: let local agents use Rafiki safely and predictably.

| Priority | Work | Success criteria |
|---|---|---|
| P0 | Keep MCP docs and tool schemas current with every CLI addition. | New stable CLI workflows either get direct MCP wrappers or explicit `rafiki_run` examples. |
| P1 | Add direct MCP wrappers for the most-used bridge workflows. | Registry search/export, viewer rebuild, Canva export, Notion dry-run/export, and render can be called without free-form args. |
| P1 | Add local automation recipes. | Scheduled regen, prompt library refresh, and post-run summary jobs have copyable examples. |
| P2 | Add agent-readable output contracts. | Tools return stable JSON with paths, URLs, counts, errors, and mutation flags. |

## Phase 6: Sharing And Deployment

Goal: share review artifacts without turning Rafiki into a hosted product.

| Priority | Work | Success criteria |
|---|---|---|
| P1 | Harden static viewer deploy flow. | `deploy` can publish a known viewer dir, report URL, and fail cleanly without Vercel installed. |
| P1 | Document secure team review patterns. | Local public portal with auth and static deploy options are clearly distinguished. |
| P2 | Add self-contained export presets. | Operators can choose "small review file" vs "full quality archive" without tuning flags each time. |
| P2 | Explore CDN-backed approved assets. | Only after registry metadata and export state are reliable locally. |

## Content And Prompt Roadmap

| Area | Current state | Next step |
|---|---|---|
| BC + AI / RAP | Rich prompt files, RAP viewer data, marketing/logos, untracked Martin revisions. | Decide which pieces are public examples, then refresh viewer data and approved outputs. |
| KK personal brand | Prompt files and style assets exist. | Add a README/runbook for the highest-value current series. |
| The Upgrade | Newsletter, social, podcast prompt files exist. | Pick one repeatable series and run it through generation -> review -> approval -> export. |
| KB ecosystem mirror | Large mirrored prompt tree exists. | Keep mirror policy current and add a freshness check or sync summary. |
| Creative Mornings | Prompt and video concept files exist. | Decide whether this is a reusable example or private campaign material. |
| Debbie Krug | Album art and local photo references exist. | Keep out of public package and document private-media handling. |

## Verification Gates

Before declaring a roadmap phase done:

- `npm test`
- `npm run pack:check`
- `npm run doctor`
- MCP smoke: list tools and call `rafiki_status`
- At least one dry-run generation path through CLI or MCP
- Docs checked for stale "known gap" claims
- Git status reviewed for unrelated local artifacts

## Near-Term Execution Order

1. Clean up public docs around absolute local MCP paths.
2. Decide and apply the default model policy.
3. Add docs index and link smoke.
4. Add MCP and CLI dry-run smoke tests.
5. Make registry metadata feed the library viewer.
6. Add portal curation/export actions.
7. Package a small public quickstart fixture.

## Non-Goals For Now

- Hosted multi-tenant image generation
- Shared team billing or centralized usage logs
- Database-backed job queues
- Replacing the local filesystem as the primary asset store
- Moving private prompt/media collections into the public package by default


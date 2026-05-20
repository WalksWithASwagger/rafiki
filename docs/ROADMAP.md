# Rafiki Roadmap

Last reviewed: 2026-05-18

Latest audit: [Rafiki Product Audit (2026-05-18)](../meta/audits/2026-05-18-rafiki-product-audit.md)

This roadmap is the maintainers' working plan for Rafiki. It is intentionally
forward-looking: current product surface lives in `README.md` and the per-area
docs under `docs/`. The roadmap covers themes, phased work, verification gates,
and non-goals.

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
| Python CLI | `generate.py` | Main command surface for generation, viewer rebuilds, archive cleanup, registry, billing imports, deploy, exports, scheduled regen, and portal startup. |
| Core generation | `lib/core.py`, `lib/batch.py`, `lib/providers/` | Multi-provider image generation with run isolation, reference images, style composition, and parallel batch support. |
| Local portal | `lib/server.py`, `lib/renderers/library.py` | Local library with all-runs archive browsing, filters, keyboard review, run detail panel, ratings, feedback, archive metadata and billing APIs, pricing-profile/imported spend summary, deploy readiness, revision staging, prompt studio, auth for public binding, and run browsing. |
| Review viewers | `lib/renderers/viewer.py`, `generate-presentation-viewer.py` | Comparison viewers, reusable presentation viewers, social-copy export, and self-contained HTML mode. |
| Asset operations | `lib/archive.py`, `lib/registry.py`, `lib/exporters/`, `lib/deploy/` | Approved-image curation, searchable registry cache, Canva bundle export, Notion export, Vercel deploy helper, and secret-safe deploy readiness checks. |
| Automation | `lib/regen.py`, `config/scheduled-regen.json.example` | Scheduled regeneration jobs are configured locally and can be dry-run or executed from the CLI. |
| Agent access | `mcp_server.py`, `docs/MCP.md` | MCP server exposes direct generation tools plus a constrained `generate.py` bridge for local clients. |
| Delivery pipeline | `docs/DELIVERY-PIPELINE.md`, `meta/routines/`, `.claude/skills/github-*` | Linear-backed GitHub issue-to-PR loop is now documented for agents and maintainers. |
| Prompt collections | `prompts/`, `styles/`, `assets/kb-import/` | Rich working examples and mirrored prompt assets exist in the repo; the public package ships only the quickstart fixture by policy. |
| Tests and CI | `tests/`, `.github/workflows/ci.yml` | 193 Python tests across product and agentic suites, plus CI for Python tests and `npm pack --dry-run`. |

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
| P0 | Keep public MCP docs portable and use `rafiki_status` for checkout-specific commands. | No tracked public docs contain machine-specific local paths. |
| P0 | Maintain the default model policy. | README, CLI defaults, portal default, MCP default, examples, and roadmap all say `gemini-2.5-flash-image` is the default. |
| P0 | Keep the MCP server registered locally but document that registration is a local setup step, not repo state. | Codex and Claude Code can still list `rafiki`; repo docs explain portable setup. |
| P1 | Add a short docs index. | A new contributor can start from README and find scope, MCP, registry, exports, deploy, scheduled regen, archive, and presentation viewer docs in one place. |
| P1 | Add an end-to-end MCP smoke test script or test fixture. | CI or local test can start the MCP stdio server, list tools, and call `rafiki_status`. |
| P1 | Add a CLI JSON smoke test. | `generate.py --prompt ... --dry-run --json` and one batch dry-run path are covered. |

## Phase 1: Public Release Hygiene

Goal: make Rafiki safe and understandable outside this machine.

| Priority | Work | Success criteria |
|---|---|---|
| P0 | Scrub tracked local paths and private project assumptions from public docs. | `rg "/Users/kk|private|local-only"` has only intentional policy references. |
| P0 | Define prompt/media release policy. | Public package/repo clearly distinguishes the public fixture from private working prompt libraries and local images. |
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
| Shipped | Add cost and throughput summaries. | The portal now summarizes local manifest cost amounts, pricing-profile estimates, unpriced image counts, run duration, model mix, failed images, and recent runs. |
| P2 | Make cleanup safer. | `clean` can report reclaimable disk space and defaults to dry-run in docs. |

## Phase 3: Registry-Backed Asset Library

Goal: make the asset registry the source of truth for browsing, search, and
exports.

Status: the P0 library/archive foundation is shipped. The registry now feeds
the master library, and `generate.py library` / `generate.py serve` show every
historical `run-*` image while keeping curated registry/export scopes available.

| Priority | Work | Success criteria |
|---|---|---|
| Shipped | Connect the library viewer to registry metadata. | Library cards can show titles, captions, tags, approval status, and source prompt without custom per-viewer logic. |
| Shipped | Make the master library a complete local archive. | `generate.py library` and the portal scan every historical `run-*` image, while curated registry/export flows stay available for approved/latest assets. |
| Shipped | Add durable archive metadata state. | `output/archive-metadata.json` stores title overrides, tags, export/publish markers, and superseded links; library cards merge that state into badges and search. |
| P1 | Add approval/export state to registry exports. | Registry exports can answer which assets are approved, exported to Notion/Canva, deployed, or stale. |
| P1 | Add registry refresh hooks after generation and curation. | Common workflows do not require the operator to remember `registry index`. |
| P2 | Consider SQLite after JSON limits are clear. | Migration only happens if JSON search/export becomes too slow or awkward. |

## Phase 4: Portal As Command Center

Goal: make the local portal the best default interface for review and curation.

| Priority | Work | Success criteria |
|---|---|---|
| P0 | Surface run status and errors better in the portal. | A failed generation shows useful error state and next action, not just missing images. |
| Shipped | Add local spend and feedback surfaces. | The portal shows local spend/run summaries, persists per-card feedback to `output/feedback.json`, and can stage feedback-driven reruns into Prompt Studio. |
| Shipped | Add pricing-profile spend estimates. | `config/pricing.json` estimates fixed-price image outputs locally while leaving token-priced or unknown models unpriced until manifests include usage. |
| Shipped | Add local provider billing imports. | CSV/JSON/manual billing rows land in `data/billing-imports.json`, appear in the portal, and take precedence as the spend display total when present. |
| Shipped | Expand curation state from the UI. | Per-card metadata now makes title overrides, tags, exported/published state, and superseded links durable and visible while reviewing. |
| Shipped | Split portal into modes and seed Curriculum Atlas. | Review is the image-first default; Generate, Curate, Spend, and Teach are distinct modes; Teach reads `config/curriculum-atlas.json` and can filter matching archive cards back in Review. |
| P1 | Expand export actions from the UI. | Canva bundle, Notion dry-run/export, registry export, and deploy helper are discoverable from the portal; next, stamp export actions back into archive metadata automatically. |
| P2 | Add prompt diffing between runs. | Operators can compare prompt and setting changes across regenerations. |
| P2 | Improve long-running job behavior. | Portal generation has clearer progress, cancellation, and retry affordances while remaining local-first. |
| Shipped | Add portal browser E2E smoke. | `npm run e2e:portal` creates a disposable dry-run archive, starts the portal, and verifies desktop/mobile review flows in Chromium. |

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
| Shipped | Harden static viewer deploy flow. | `deploy` can publish a known viewer dir, report URL, fail cleanly without Vercel installed, and expose read-only readiness checks. |
| Shipped | Document secure team review patterns. | Local public portal with auth, readiness checks, and static deploy options are clearly distinguished. |
| P2 | Add self-contained export presets. | Operators can choose "small review file" vs "full quality archive" without tuning flags each time. |
| P2 | Explore CDN-backed approved assets. | Only after registry metadata and export state are reliable locally. |

## Content And Prompt Roadmap

| Area | Current state | Next step |
|---|---|---|
| Curriculum Atlas | `config/curriculum-atlas.json` maps programs, modules, objectives, competencies, facilitator notes, discussion prompts, critique criteria, concept links, and asset-matching terms into the portal's Teach mode. | Add graph visualization and visual baselines after real review sessions prove the schema shape. |
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
- `npm run e2e:portal`
- MCP smoke: list tools and call `rafiki_status`
- At least one dry-run generation path through CLI or MCP
- Docs checked for stale "known gap" claims
- Git status reviewed for unrelated local artifacts

## Near-Term Execution Order

1. Add Curriculum Atlas graph visualization and visual baselines.
2. Stamp portal export actions back into archive metadata automatically.
3. Add archive health and cleanup reports.
4. Add MCP and CLI dry-run smoke tests.
5. Expand doctor remediation for package and browser setup.

## Non-Goals For Now

- Hosted multi-tenant image generation
- Shared team billing or centralized usage logs
- Database-backed job queues
- Replacing the local filesystem as the primary asset store
- Moving private prompt/media collections into the public package by default

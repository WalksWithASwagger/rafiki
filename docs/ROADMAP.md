# Rafiki Roadmap

Last reviewed: 2026-06-09

Latest audit: [Rafiki E2E And Showpiece Roadmap Audit (2026-05-19)](../meta/audits/2026-05-19-e2e-roadmap-showpiece-audit.md)

That audit is a dated snapshot. The active roadmap below reflects the later
lineage comparison and Curriculum Atlas story-mode work on `main`.

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

## Current Public Use Case

The active public use case is the keynote visual workflow: ideas and notes
become prompt packs, prompt packs become reviewable image candidates, approved
graphics become slide assets, and slide assets become reusable blog, guide,
site, social, and speaker materials.

The worked use-case doc is
[Keynote Visual Workflow](use-cases/keynote-visual-workflow.md), with a dry-run
prompt pack at `examples/keynote-visual-workflow-prompt-pack.md`.

## Current System Map

| Area | Primary files | Current state |
|---|---|---|
| Node CLI | `index.js`, `package.json` | `rafiki` and `image-gen` bins delegate image generation to Python and handle Puppeteer HTML rendering. |
| Python CLI | `generate.py` | Main command surface for generation, viewer rebuilds, archive cleanup, registry, billing imports, deploy, exports, scheduled regen, and portal startup. |
| Core generation | `lib/core.py`, `lib/batch.py`, `lib/providers/` | Multi-provider image generation with run isolation, reference images, style composition, and parallel batch support. |
| Local portal | `lib/server.py`, `lib/renderers/library.py`, `lib/renderers/library_atlas.py` | Local library with all-runs archive browsing, review queue, lineage chips, filters, keyboard review, run detail panel, ratings, feedback, evaluations, archive metadata and billing APIs, pricing-profile/imported spend summary, deploy readiness, revision staging, prompt studio, auth for public binding, Teach mode, and run browsing. |
| Review viewers | `lib/renderers/viewer.py`, `generate-presentation-viewer.py` | Comparison viewers, reusable presentation viewers, social-copy export, and self-contained HTML mode. |
| Asset operations | `lib/archive.py`, `lib/archive_health.py`, `lib/registry.py`, `lib/exporters/`, `lib/deploy/`, `scripts/workspace_hygiene.py` | Approved-image curation, read-only archive health and workspace hygiene reporting, searchable registry cache, Canva bundle export, Notion export, Vercel deploy helper, and secret-safe deploy readiness checks. |
| Automation | `lib/regen.py`, `config/scheduled-regen.json.example` | Scheduled regeneration jobs are configured locally and can be dry-run or executed from the CLI. |
| Agent access | `mcp_server.py`, `scripts/dry-run-smoke.py`, `docs/MCP.md` | MCP server exposes direct generation tools plus a constrained `generate.py` bridge for local clients; `npm run smoke:dry-run` verifies the spend-free Node CLI, MCP status, MCP bridge, and archive-health path. |
| Delivery pipeline | `docs/DELIVERY-PIPELINE.md`, `meta/routines/`, `.claude/skills/github-*`, `.agents/skills/github-*` | Linear-backed GitHub issue-to-PR loop is now documented for Claude Code, Codex, and maintainers. |
| Prompt collections | `prompts/`, `styles/`, `assets/`, `examples/` | Rich working examples, style references, and mirrored prompt assets exist in the public repo; the public package ships only explicitly listed public fixtures by policy. |
| Tests and CI | `tests/`, `.github/workflows/ci.yml` | 300+ collected Python tests in this checkout, plus CI for Python tests, portal E2E, docs links, npm package contents, and doctor. |

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
| P1 | Add a short docs index. | Shipped: `docs/INDEX.md` maps scope, MCP, registry, exports, deploy, scheduled regen, archive, and presentation viewer docs. |
| Shipped | Add an end-to-end MCP smoke test script or test fixture. | `npm run smoke:dry-run`, `tests/test_mcp_server.py`, and `tests/test_dry_run_smoke.py` start the MCP stdio server, list tools, and call `rafiki_status`. |
| Shipped | Add a CLI JSON smoke test. | `tests/test_cli_surfaces.py` and `tests/test_cli_dispatch.py` cover `generate.py --prompt ... --dry-run --json` and batch dry-run paths. |

## Phase 1: Public Release Hygiene

Goal: make Rafiki safe and understandable outside this machine.

| Priority | Work | Success criteria |
|---|---|---|
| P0 | Scrub tracked local paths and private project assumptions from public docs. | `rg "/Users/kk|private|local-only"` has only intentional policy references. |
| P0 | Define prompt/media release policy. | Public package/repo clearly distinguishes the public fixture from private working prompt libraries and local images. |
| P0 | Package story audit. | `npm pack --dry-run` includes all runtime files and excludes private/generated assets by design. |
| Shipped | Add a public quickstart fixture. | `examples/quickstart-image-prompts.md` and `examples/keynote-visual-workflow-prompt-pack.md` support dry-run workflows without private prompt libraries. |
| Shipped | Add docs lint or link smoke check. | `npm run docs:check` and `scripts/check-doc-links.py` catch broken internal links before release. |
| Shipped | Expand `npm run doctor`. | `index.js --doctor` checks Python, dependencies, env vars, MCP server import, Chrome/Puppeteer status, and gives precise remediation. |
| Shipped | Add safe workspace hygiene reporting. | `npm run workspace:hygiene -- --repo .` reports dirty worktrees, gone upstreams, branches attached to worktrees, dependency/cache bulk hints, and human-gated cleanup risk without deleting anything. |

## Phase 2: Workflow Reliability

Goal: make common creative workflows hard to break.

| Priority | Work | Success criteria |
|---|---|---|
| Shipped | Add cross-surface regression tests. | `tests/test_cli_surfaces.py` verifies the same generation options through Python CLI, Node CLI, portal job helper, and MCP wrapper. |
| Shipped | Add agent-facing dry-run smoke. | `npm run smoke:dry-run` proves Node CLI dry-run generation, MCP `rafiki_status`, MCP tool listing, MCP `rafiki_run`, and archive-health JSON on a disposable output root without provider spend. |
| P1 | Split `generate.py` subcommands into command modules when touched. | New command work does not make the dispatcher larger. |
| Shipped | Strengthen run manifests. | `tests/test_run_manifest.py` and `run.json` record provider, model, style, prompt file, reference images, CLI/tool source, timings, and error states consistently. |
| Shipped | Add cost and throughput summaries. | The portal now summarizes local manifest cost amounts, pricing-profile estimates, unpriced image counts, run duration, model mix, failed images, and recent runs. |
| Shipped | Make cleanup safer to inspect. | `archive-health --cleanup-report` groups cleanup candidates and risky runs by project/run, reports approved coverage and candidate bytes, and suggests dry-run `clean --keep-approved` commands without mutating outputs. |

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
| Shipped | Add durable archive metadata state. | `output/archive-metadata.json` stores title overrides, tags, export/publish markers, and superseded links; library cards merge that state into badges and search, and successful portal Canva/Notion/deploy actions stamp matching source cards automatically. |
| Shipped | Add read-only archive health reporting. | `python generate.py archive-health` reports missing images, malformed run manifests, duplicate filenames, sidecar orphans, disk usage, cleanup risk, and advisory cleanup candidates without mutating outputs. |
| Shipped | Add approval/export state to registry exports. | Registry exports include approval state and archive sidecar fields from `output/archive-metadata.json` (#143). |
| Shipped | Add registry refresh hooks after generation and curation. | Generation and curation workflows refresh the curated registry cache without requiring manual `registry index` (#144). |
| P2 | Consider SQLite after JSON limits are clear. | Migration only happens if JSON search/export becomes too slow or awkward. |

## Phase 4: Portal As Command Center

Goal: make the local portal the best default interface for review and curation.

| Priority | Work | Success criteria |
|---|---|---|
| Shipped | Surface run status and errors better in the portal. | Failed generations show useful error state, retry guidance, and browser-side wait cancellation in Prompt Studio (#142). |
| Shipped | Add local spend and feedback surfaces. | The portal shows local spend/run summaries, persists per-card feedback to `output/feedback.json`, and can stage feedback-driven reruns into Prompt Studio. |
| Shipped | Add card-level evaluation state. | Run Detail writes decisions, 1-5 scores, use cases, rationale, and next steps to `output/evaluations.json`; cards show evaluation badges and Run Detail summarizes decisions across the current run. |
| Shipped | Add pricing-profile spend estimates. | `config/pricing.json` estimates fixed-price image outputs locally while leaving token-priced or unknown models unpriced until manifests include usage. |
| Shipped | Add local provider billing imports. | CSV/JSON/manual billing rows land in `data/billing-imports.json`, appear in the portal, and take precedence as the spend display total when present. |
| Shipped | Expand curation state from the UI. | Per-card metadata now makes title overrides, tags, exported/published state, and superseded links durable and visible while reviewing. |
| Shipped | Split portal into modes and seed Curriculum Atlas. | Review is the image-first default; Generate, Curate, Spend, and Teach are distinct modes; Teach reads `config/curriculum-atlas.json`, renders a concept graph and Cohort Story Mode rail, and can filter matching archive cards back in Review. |
| Shipped | Add review ritual affordances. | Cards now expose lineage chips and copy-prompt actions, while Review Queue combines unreviewed cards, feedback attention, missing evaluation, missing export state, and Atlas-unmapped assets. |
| Shipped | Add portal accessibility guardrails. | The portal has explicit `:focus-visible` treatment, reduced-motion CSS, no `transition: all` in renderer CSS, and E2E assertions for those guardrails. |
| Shipped | Expand export actions from the UI. | Canva bundle, Notion dry-run/export, registry export, and deploy helper are discoverable from the portal; successful Canva, Notion, and static deploy actions stamp archive metadata automatically when their source maps back to run images, including approved, run-level, and project-root static viewers. |
| Shipped | Connect evaluation to curriculum. | Run Detail shows matched Atlas modules, matching terms, critique criteria, and discussion prompts beside the evaluation form; Teach mode summarizes module decision counts and average scores from `output/evaluations.json`. |
| Shipped | Add prompt/run comparison for superseded assets. | Run Detail compares title, prompt, model, style, aspect ratio, run id, and archive metadata state for cards linked through `superseded_by`. |
| P2 | Broaden lineage comparison coverage. | Operators can compare more rerun/export chains even when they are not linked through a superseded-card relationship. |
| P2 | Improve long-running job behavior. | Portal generation has clearer progress, cancellation, and retry affordances while remaining local-first. |
| Shipped | Add portal browser E2E smoke. | `npm run e2e:portal` creates a disposable dry-run archive, starts the portal, and verifies desktop/mobile review flows in Chromium. |

## Phase 5: Agent And Automation Layer

Goal: let local agents use Rafiki safely and predictably.

| Priority | Work | Success criteria |
|---|---|---|
| P0 | Keep MCP docs and tool schemas current with every CLI addition. | New stable CLI workflows either get direct MCP wrappers or explicit `rafiki_run` examples. |
| Shipped | Add direct MCP wrappers for the most-used bridge workflows. | `mcp_server.py` exposes typed tools for registry search/export, archive health, viewer rebuild, library rebuild, Canva export, Notion export, and render (#145). |
| P1 | Add local automation recipes. | Scheduled regen, prompt library refresh, and post-run summary jobs have copyable examples (#213). |
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
| Curriculum Atlas | `config/curriculum-atlas.json` maps programs, modules, objectives, competencies, facilitator notes, discussion prompts, critique criteria, concept links, and asset-matching terms into the portal's Teach mode; the portal now renders a first concept graph from `concept_links`, links Run Detail evaluation context to matched modules, summarizes module evaluation decisions/scores, and exposes a per-program Cohort Story Mode rail. | Validate the story rail in real review sessions, then add presentation/export controls and richer learner-journey metadata. |
| BC + AI / RAP | Rich prompt files, RAP viewer data, marketing/logos, YouTube thumbnail assets, and RAP section-cover assets. | Decide which pieces are public examples, then refresh viewer data and approved outputs. |
| MAC | `mac`, `mac-workshop`, and `femme` styles cover identity tiles, workshop riso graphics, and body-compute art directions. | Visually review the new prompt/reference packs with MAC stakeholders before publishing event or episode assets. |
| Vancouver AI | Mission 30 badge prompts and reference images exist for print-clean, orca-shuttle, and recovery iterations. | Pick a winning badge direction, then generate/export the final print-ready set. |
| KK personal brand | Prompt files and style assets exist. | Add a README/runbook for the highest-value current series. |
| The Upgrade | Newsletter, social, podcast prompt files exist. | Pick one repeatable series and run it through generation -> review -> approval -> export. |
| KB ecosystem mirror | Large mirrored prompt tree exists. | Keep mirror policy current and add a freshness check or sync summary. |
| Creative Mornings | Prompt and video concept files exist. | Decide whether this is a reusable example or private campaign material. |
| Debbie Krug | Album art and local photo references exist. | Keep out of public package and document private-media handling. |

## Verification Gates

Before declaring a roadmap phase done:

- `npm test` (see `CONTRIBUTING.md` for the deterministic-local contract)
- `npm run pack:check`
- `npm run doctor`
- `npm run smoke:dry-run`
- `npm run e2e:portal` (see `docs/PORTAL-COMMAND-CENTER.md` for the extra-outputs isolation contract)
- `python generate.py archive-health --json`
- `python generate.py archive-health --cleanup-report`
- Docs checked for stale "known gap" claims
- Git status reviewed for unrelated local artifacts

## Near-Term Execution Order

Shipped near-term items (#180, #181, #182, #143, #145, #147, #142, #144, #146,
#187) are closed. Active open work:

1. Refresh roadmap statuses against shipped work and closed issues (#207).
2. Close public repo metadata and stale audit follow-ups (#186).
3. Document media-suite MCP tools in `docs/MCP.md` (#208).
4. Add MCP tool/docs sync test (#210; blocked by #208).
5. Extract first command modules from the `generate.py` dispatcher (#211).
6. Spike agent-readable JSON output contract for MCP tools (#212).
7. Add local automation and agent archive recipes doc (#213).
8. Media suite hardening lane: importer fixtures (#189), warning drawer (#188),
   job lifecycle (#192–#193), video validation (#194–#195), MCP mirror (#196),
   acceptance command (#197).
9. Add KB ecosystem mirror freshness check (#214).
10. Workflow power tools: export presets (#198), lineage suggestions (#199).
11. Curriculum Atlas validation (#200) and export controls (#201, blocked).
12. Explore CDN-backed approved asset publishing (#202, research).

## Non-Goals For Now

- Hosted multi-tenant image generation
- Shared team billing or centralized usage logs
- Database-backed job queues
- Replacing the local filesystem as the primary asset store
- Moving private prompt/media collections into the public package by default

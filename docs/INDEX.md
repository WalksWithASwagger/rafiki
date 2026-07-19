# Rafiki Docs Index

Start with the README for install and everyday CLI usage. This index maps the
deeper operating docs by surface area.

## Product And System Shape

- [Scope](SCOPE.md) - what belongs in Rafiki v1, what stays out of scope, and
  the boundaries for portal auth, Prompt Studio, MCP, and future extensions.
- [Folder Layout](FOLDER-LAYOUT.md) - where generated runs, registered assets,
  config, docs, prompts, and optional sibling repos live.
- [Roadmap](ROADMAP.md) - themes, phased work, verification gates, near-term
  execution order, and non-goals.
- [Model Policy](MODEL-POLICY.md) - default model, provider choices, and
  Gemini versus OpenAI guidance.
- [Prompt And Media Release Policy](PROMPT-MEDIA-POLICY.md) - public package
  fixture, private prompt library handling, and media boundaries.
- [Keynote Visual Workflow Use Case](use-cases/keynote-visual-workflow.md) -
  public use case for turning talk notes into prompt packs, reviewable image
  candidates, slides, and downstream publishing assets.

## Runtime Surfaces

- [MCP](MCP.md) - local MCP installation, tool surface, CLI bridge examples,
  and safety notes.
- [MCP Output Contract](MCP-OUTPUT-CONTRACT.md) - proposed stable JSON envelope
  for typed tool outputs (paths, URLs, counts, errors, mutation flags).
- [AgentOpus MCP](AGENT-OPUS-MCP.md) - hosted generative-video MCP (prompt/script
  → finished video); same lane as Rafiki/Floyo, not OpusClip clipping.
- [Floyo Video](FLOYO.md) - drive Floyo (flowyo.ai) hosted-ComfyUI workflows to
  render short clips; dry-run-first CLI + MCP.
- [Doctor](DOCTOR.md) - what `npm run doctor` / `npx rafiki --doctor` checks,
  exit codes, and common fixes.
- [Chrome / Puppeteer](CHROME-PUPPETEER.md) - browser resolution and sandbox
  notes for `rafiki --render`.
- [Presentation Viewer](PRESENTATION-VIEWER.md) - JSON-driven deck viewer,
  portable single-file mode, wrappers, schema, and content-series workflow.
- [Frontend Shell](FRONTEND.md) - TypeScript portal shell, Python proxy/API
  boundary, rollback routes, local build behavior, and verification commands.
- [Generate UI Next Work Plan](GENERATE-UI-NEXT-WORK-PLAN-2026-07.md) -
  stabilization plan for the React generation workspace, dry-run safety,
  reference selection, and future job handling.
- [July 3 Issue-Crush Audit](../meta/audits/2026-07-03-issue-crush-audit.md) -
  open-issue disposition, close candidates, blocked issues, and recommended
  implementation order after Generate UI stabilization.
- [July 3 Closeout](../meta/audits/2026-07-03-rafiki-closeout.md) - merged PRs,
  stale branch cleanup proof, verification, and next work.
- [Portal Command Center](PORTAL-COMMAND-CENTER.md) - local portal spend
  summary, legacy rollback surfaces, feedback, evaluation, archive metadata
  state, revision staging, Curriculum Atlas surface, and API endpoints.
- [Spend Accounting](SPEND-ACCOUNTING.md) - pricing profile semantics,
  estimate rules, and source-of-truth boundaries.

## Registries, Archives, And Libraries

- [Command Center](COMMAND-CENTER.md) - aggregate every Rafiki image across all
  your repos into one dashboard (static library + live portal); registering
  external projects and the one-command refresh.
- [Library And Viewer Designer Handoff](LIBRARY-VIEWER-DESIGNER-HANDOFF-2026-07.md) -
  current system map, archive inventory, diagrams, pain points, and redesign
  requirements for the image library, viewers, portal, registry, and media
  suite.
- [Asset Registry](ASSET-REGISTRY.md) - registry schema, CLI indexing, and
  re-indexing guidance for external or generated assets.
- [Personal Media Suite](PERSONAL-MEDIA-SUITE.md) - multimedia roots, Alex
  importer, local media registry, suite portal, and dry-run job commands.
- [Approved-Image Archive](ARCHIVE.md) - approved-asset archive flow, layout,
  `index.json` schema, and storage location.
- [Library And Archive Roadmap](LIBRARY-ARCHIVE-ROADMAP.md) - build plan for
  the all-runs image archive, portal curation, cleanup, and agent access.
- [Curriculum Atlas](CURRICULUM-ATLAS.md) - local program/module/objective
  scaffold that links generated archive images to teaching surfaces.

## Export, Deployment, And Delivery

- [Canva Export](CANVA-EXPORT.md) - approved-image export layout and metadata
  enrichment for Canva handoff packages.
- [RAP Capstone Thumbnail And YouTube Handoff](RAP-CAPSTONE-THUMBNAILS-YOUTUBE-HANDOFF-2026-07-01.md) -
  V3 thumbnail package location, YouTube upload results, pending rate-limit
  retries, and missing-video follow-up.
- [Notion Export](NOTION-EXPORT.md) - Notion setup, export commands,
  idempotency, and database targeting.
- [Social-Post Expansion](SOCIAL-EXPANSION.md) - platform constraints, source
  preference, environment requirements, and output format.
- [Deployment](DEPLOYMENT.md) - static hosting setup, readiness checks, deploy
  commands, and caveats.
- [CDN Publishing Research](CDN-PUBLISHING-RESEARCH.md) - decision memo on
  optional CDN-backed approved-asset publishing (#202); recommends defer.
- [Delivery Pipeline](DELIVERY-PIPELINE.md) - canonical agentic delivery
  contract: labels, required issue shape, branch/PR traceability, Linear sync,
  pause controls, verification gates, and local commands.

## Regeneration And Operator Workflows

- [Local Automation And Agent Archive Recipes](RECIPES.md) - copy-paste
  dry-run recipes for scheduled regen, prompt refresh, post-run summary, and
  common agent archive jobs.
- [Scheduled Regeneration](SCHEDULED-REGEN.md) - scheduled job config, schema,
  run behavior, and Claude Code automation notes.

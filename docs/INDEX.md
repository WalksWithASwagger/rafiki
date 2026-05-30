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
- [ED + AI Logo Sprint](ED-AI-LOGO-SPRINT.md) - May 2026 education meetup
  logo exploration, prompt-pack lineage, generated review artifacts, and
  production handoff notes.

## Runtime Surfaces

- [MCP](MCP.md) - local MCP installation, tool surface, CLI bridge examples,
  and safety notes.
- [Doctor](DOCTOR.md) - what `npm run doctor` / `npx rafiki --doctor` checks,
  exit codes, and common fixes.
- [Chrome / Puppeteer](CHROME-PUPPETEER.md) - browser resolution and sandbox
  notes for `rafiki --render`.
- [Presentation Viewer](PRESENTATION-VIEWER.md) - JSON-driven deck viewer,
  portable single-file mode, wrappers, schema, and content-series workflow.
- [Portal Command Center](PORTAL-COMMAND-CENTER.md) - local portal spend
  summary, mode navigation, feedback, evaluation, archive metadata state,
  revision staging, Curriculum Atlas surface, and API endpoints.
- [Work Plan 2026-05-21](WORKPLAN-2026-05-21.md) - dated snapshot after the
  quality-polish PR; use the roadmap for the live queue.
- [Spend Accounting](SPEND-ACCOUNTING.md) - pricing profile semantics,
  estimate rules, and source-of-truth boundaries.

## Registries, Archives, And Libraries

- [Command Center](COMMAND-CENTER.md) - aggregate every Rafiki image across all
  your repos into one dashboard (static library + live portal); registering
  external projects and the one-command refresh.
- [Asset Registry](ASSET-REGISTRY.md) - registry schema, CLI indexing, and
  re-indexing guidance for external or generated assets.
- [Approved-Image Archive](ARCHIVE.md) - approved-asset archive flow, layout,
  `index.json` schema, and storage location.
- [Library And Archive Roadmap](LIBRARY-ARCHIVE-ROADMAP.md) - build plan for
  the all-runs image archive, portal curation, cleanup, and agent access.
- [Curriculum Atlas](CURRICULUM-ATLAS.md) - local program/module/objective
  scaffold that links generated archive images to teaching surfaces.
- [KB Mirror Policy](kb-mirror-policy.md) - canonical ownership rule for
  `prompts/kk-kb/` vs the legacy `kk-ai-ecosystem` copies.

## Export, Deployment, And Delivery

- [Canva Export](CANVA-EXPORT.md) - approved-image export layout and metadata
  enrichment for Canva handoff packages.
- [Notion Export](NOTION-EXPORT.md) - Notion setup, export commands,
  idempotency, and database targeting.
- [Social-Post Expansion](SOCIAL-EXPANSION.md) - platform constraints, source
  preference, environment requirements, and output format.
- [Deployment](DEPLOYMENT.md) - static hosting setup, readiness checks, deploy
  commands, and caveats.
- [Delivery Pipeline](DELIVERY-PIPELINE.md) - canonical agentic delivery
  contract: labels, required issue shape, branch/PR traceability, Linear sync,
  pause controls, verification gates, and local commands.

## Regeneration And Operator Workflows

- [Scheduled Regeneration](SCHEDULED-REGEN.md) - scheduled job config, schema,
  run behavior, and Claude Code automation notes.
- [Image Pipeline Operator Guide](image-pipeline-operator.md) - scenario
  decision table, prompt inventory, styles, reference image flow, Streamlit UI
  workflow, viewer commands, and CLI recipes.

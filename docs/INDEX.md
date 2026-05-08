# Rafiki Docs Index

Start with the README for install and everyday CLI usage. This index maps the
deeper operating docs by surface area.

## Product And System Shape

- [Scope](SCOPE.md) - what belongs in Rafiki v1, what stays out of scope, and
  the boundaries for portal auth, Prompt Studio, MCP, and future extensions.
- [Folder Layout](FOLDER-LAYOUT.md) - where generated runs, registered assets,
  config, docs, prompts, and optional sibling repos live.
- [Roadmap](ROADMAP.md) - shipped surfaces, review findings, roadmap phases,
  verification gates, and near-term execution order.
- [Public Release Plan](PUBLIC-RELEASE-PLAN.md) - release hygiene, product
  positioning, onboarding, and public launch checklist.

## Runtime Surfaces

- [MCP](MCP.md) - local MCP installation, tool surface, CLI bridge examples,
  and safety notes.
- [Chrome / Puppeteer](CHROME-PUPPETEER.md) - browser resolution and sandbox
  notes for `rafiki --render`.
- [Presentation Viewer](PRESENTATION-VIEWER.md) - JSON-driven deck viewer,
  portable single-file mode, wrappers, schema, and content-series workflow.

## Registries, Archives, And Libraries

- [Asset Registry](ASSET-REGISTRY.md) - registry schema, CLI indexing, and
  re-indexing guidance for external or generated assets.
- [Approved-Image Archive](ARCHIVE.md) - approved-asset archive flow, layout,
  `index.json` schema, and storage location.
- [Image Prompt Archive](IMAGE-PROMPT-ARCHIVE.md) - prompt bundle locations,
  style references, and rerun/archive pointers.
- [KB Mirror Policy](kb-mirror-policy.md) - canonical ownership rules for KB
  prompt mirrors and stale copy handling.

## Export, Deployment, And Delivery

- [Canva Export](CANVA-EXPORT.md) - approved-image export layout and metadata
  enrichment for Canva handoff packages.
- [Notion Export](NOTION-EXPORT.md) - Notion setup, export commands,
  idempotency, and database targeting.
- [Social-Post Expansion](SOCIAL-EXPANSION.md) - platform constraints, source
  preference, environment requirements, and output format.
- [Deployment](DEPLOYMENT.md) - static hosting setup, deploy commands, and
  caveats.
- [Delivery Pipeline](DELIVERY-PIPELINE.md) - GitHub labels, Linear contract,
  issue intake, agent loop, review loop, and verification gates.

## Regeneration And Operator Workflows

- [Scheduled Regeneration](SCHEDULED-REGEN.md) - scheduled job config, schema,
  run behavior, and Claude Code automation notes.
- [Rerun Pipeline Plan](RERUN-PIPELINE-PLAN.md) - prompt rerun phases,
  command cheatsheet, and housekeeping.
- [Image Pipeline Operator Guide](image-pipeline-operator.md) - prompt
  inventory, styles, reference image flow, viewer commands, and CLI recipes.
- [Image Pipeline Analysis](image-pipeline-analysis.md) - scenario matrix,
  style-system notes, dedupe assessment, and phase status.

# Where everything lives

**All Rafiki product code, config, and docs live in this single repository checkout** — one folder on disk, one `git clone`, one `npm install` + Python venv here.

```
rafiki/                          ← this repo (clone anywhere; name the folder rafiki/)
├── index.js                     # Node CLI entry (delegates generation, runs Puppeteer)
├── generate.py                  # Python CLI dispatcher: generation, viewers, archive,
│                                #   registry, deploy, exports, regen, serve, link-projects
├── generate-presentation-viewer.py  # JSON-driven deck viewer builder
├── mcp_server.py                # MCP server (typed tools + constrained CLI bridge)
├── package.json                 # npm package "rafiki"; bins: rafiki, image-gen
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
├── .env.example                 # provider key template (copy to .env)
├── .github/
│   ├── ISSUE_TEMPLATE/          # Agent-ready issue templates
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── branch-protection.md     # Recommended GitHub protection settings
│   └── workflows/               # ci.yml + agentic-* (issue-quality, dev-loop,
│                                #   traceability-sync, pr-review)
├── .claude/
│   ├── commands/                # Slash commands (e.g. /agentic-intake)
│   └── skills/                  # Local skills: rafiki, github-issue-writer/,
│                                #   github-pr-reviewer/
├── .agents/
│   └── skills/                  # Codex skill mirrors for Rafiki issue and PR work
├── .company-os/
│   └── project.yaml             # Company-OS project manifest (loops, memory, validation)
├── agentic/
│   └── contract.json            # Repo-local agentic delivery contract (labels, limits,
│                                #   linear_sync, verification commands)
├── meta/
│   ├── audits/                  # Agent loop audit logs (dev-loop-log.csv)
│   └── routines/                # Repeatable agent prompts (SETUP, dev-loop-runner,
│                                #   auto-merge-gate)
├── lib/                         # Python library modules
│   ├── core.py                  # generate_image() — unified provider dispatch
│   ├── batch.py                 # Parallel batch runner, run isolation, viewer generation
│   ├── models.py                # Alias resolution + resolution config
│   ├── prompts.py               # parse_image_prompts_md()
│   ├── styles.py                # Style suffix resolution + composition
│   ├── usage.py                 # Usage log (full prompt, model, style, ok/error)
│   ├── billing.py               # Local provider billing imports (CSV/JSON/manual)
│   ├── pricing.py               # Public pricing-profile loader + local cost estimates
│   ├── feedback.py              # Local archive feedback notes + change requests
│   ├── evaluations.py           # Local card decisions, scores, and next steps
│   ├── archive_metadata.py      # Local title/tag/export-state sidecar
│   ├── archive.py               # approved/ curation + clean
│   ├── registry.py              # Asset registry index/search/export
│   ├── regen.py                 # Scheduled regeneration runner
│   ├── server.py                # Local portal (serve, ratings API, prompt studio)
│   ├── portal_actions.py        # Portal curation/export endpoints
│   ├── social.py                # social-expand (LLM social-post expansion)
│   ├── extra_outputs.py         # Loader for config/extra-outputs(.local).json
│   ├── providers/               # Gemini + OpenAI image providers
│   ├── renderers/               # Per-run viewer, comparison viewer, library viewer
│   ├── exporters/               # Canva bundle + Notion gallery exporters
│   └── deploy/                  # Vercel static viewer deploy helper + readiness checks
├── scripts/
│   ├── check-doc-links.py       # `npm run docs:check`
│   ├── run-pytest.js            # `npm test` wrapper
│   ├── sync-kb-image-prompt-mirror.sh
│   └── agentic/                 # Agentic pipeline scripts (issue_lint, dev_loop,
│                                #   pr_traceability, linear_sync, ensure_labels,
│                                #   pr_review, provider_adapter, common)
├── styles/                      # styles.yaml + per-style markdown guides, plus
│                                #   refs/ image plates for a few styles
│                                #   (run `npx rafiki --list-styles` for the live
│                                #   style list — it is the source of truth)
├── prompts/                     # (gitignored) local prompt libraries — your generated
│                                #   content, kept in a private knowledge base, not shipped
├── examples/
│   └── quickstart-image-prompts.md  # Public onboarding fixture (the only prompt
│                                #   shipped in the npm package)
├── assets/                      # (gitignored) local reference images and output assets —
│                                #   private, not tracked or packaged
├── config/
│   ├── extra-outputs.json.example
│   ├── pricing.json             # Public model pricing profile for local estimates
│   └── scheduled-regen.json.example  # Local config templates (real files are gitignored)
├── data/                        # usage-log.json, billing-imports.json,
│                                #   asset-registry.* (gitignored)
├── output/                      # Generated images + viewers (gitignored)
│   ├── ratings.json             # star/reject map, written by the portal
│   ├── feedback.json            # local card notes/change requests, written by the portal
│   ├── evaluations.json         # local card decisions/scores, written by the portal
│   ├── archive-metadata.json    # local title overrides, tags, export/publish state
│   ├── <project>/run-*/         # Per-project run trees with run.json + viewer.html
│   ├── <project>/approved/      # Curated keepers + index.json + viewer.html
│   └── library.html             # Master library — built by `generate.py library`
├── tools/
│   └── gpt-image-batch-ui/      # Streamlit batch UI for gpt-image-1 workflows
├── tests/                       # Python test suite (incl. tests/agentic/)
└── docs/                        # Operating docs. INDEX.md is the full,
                                 #   authoritative map — this tree does not
                                 #   re-list every doc so the two can't drift.
```

## Optional sibling repos

Other repos can point at this checkout instead of duplicating Rafiki source.
If you keep a thin wrapper elsewhere, treat that repo as a consumer and keep
the Rafiki code, config, docs, and Python environment here.

# Where everything lives

**All Rafiki product code, config, and docs live in this single repository checkout** — one folder on disk, one `git clone`, one `npm install` + Python venv here.

```
rafiki/                          ← this repo (clone anywhere; name the folder rafiki/)
├── index.js                     # Node CLI entry (AI + Puppeteer)
├── generate.py                  # Python CLI: generate / view / library subcommands
├── mcp_server.py                # MCP server (generation tools + CLI bridge)
├── package.json                 # npm package "rafiki", bins rafiki + image-gen
├── requirements.txt
├── .github/
│   ├── ISSUE_TEMPLATE/          # Agent-ready issue template
│   ├── branch-protection.md     # Recommended GitHub protection settings
│   └── workflows/ci.yml         # Python tests + npm package smoke
├── .claude/skills/              # Local skills for Rafiki, issue writing, and PR review
├── meta/
│   ├── audits/                  # Agent loop audit logs
│   └── routines/                # Repeatable agent workflow prompts
├── styles/                      # styles.yaml + per-style markdown guides (kk, hopecode, bcai, upgrade, zine, gni)
├── prompts/                     # Prompt libraries — kk/, bcai/, hopecode/, upgrade/, kk-kb/
├── examples/
├── lib/
│   ├── batch.py                 # Parallel batch runner, run isolation, viewer generation
│   ├── core.py                  # generate_image() — unified provider dispatch
│   ├── models.py                # Alias resolution + resolution config
│   ├── prompts.py               # parse_image_prompts_md()
│   ├── styles.py                # Style suffix resolution + composition
│   ├── usage.py                 # Usage log (full prompt, model, style, ok/error)
│   └── renderers/
│       ├── __init__.py
│       ├── viewer.py            # Single-run viewer + comparison viewer HTML
│       └── library.py          # Master library viewer (all projects, project/model filter chips)
├── data/                        # usage-log.json (gitignored)
├── output/                      # Generated images + viewers (gitignored)
│   ├── <project>/run-*/         # Per-project run trees with run.json + viewer.html
│   └── library.html             # Master library — built by `generate.py library`
└── docs/
    ├── SCOPE.md
    ├── MCP.md
    ├── DELIVERY-PIPELINE.md     # Linear/GitHub issue-to-PR workflow
    ├── CHROME-PUPPETEER.md
    ├── FOLDER-LAYOUT.md         # this file
    ├── image-pipeline-analysis.md
    └── image-pipeline-operator.md
```

## Optional sibling repos

Other repos can point at this checkout instead of duplicating Rafiki source.
If you keep a thin wrapper elsewhere, treat that repo as a consumer and keep
the Rafiki code, config, docs, and Python environment here.

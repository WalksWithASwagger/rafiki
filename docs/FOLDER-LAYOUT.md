# Where everything lives

**All Rafiki product code, config, and docs live in this single repository checkout** — one folder on disk, one `git clone`, one `npm install` + Python venv here.

```
rafiki/                          ← this repo (clone anywhere; name the folder rafiki/)
├── index.js                     # Node CLI entry (AI + Puppeteer)
├── generate.py                  # Python CLI: generate / view / library subcommands
├── mcp_server.py                # MCP server (rafiki_generate, rafiki_batch, rafiki_list_styles)
├── package.json                 # npm package "rafiki", bins rafiki + image-gen
├── requirements.txt
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
    ├── CHROME-PUPPETEER.md
    ├── FOLDER-LAYOUT.md         # this file
    ├── image-pipeline-analysis.md
    └── image-pipeline-operator.md
```

## Not in this repo (KB monorepo only)

The knowledge base keeps a **thin shim** at `kk-ai-ecosystem/tools/image-gen/` (`launch.js` + tiny `package.json`) plus **KB-specific artifacts** (e.g. `outputs/`, `data/refs/`) that stay versioned with content. That path is **not** a second copy of Rafiki — it forwards to this checkout via `RAFIKI_HOME` / sibling `../rafiki/` (see that repo’s `tools/image-gen/README.md`).

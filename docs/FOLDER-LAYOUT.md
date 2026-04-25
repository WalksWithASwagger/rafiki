# Where everything lives

**All Rafiki product code, config, and docs live in this single repository checkout** — one folder on disk, one `git clone`, one `npm install` + Python venv here.

```
rafiki/                          ← this repo (clone anywhere; name the folder rafiki/)
├── index.js                     # Node CLI entry
├── generate.py                  # Gemini image generation
├── package.json                 # npm package "rafiki", bins rafiki + image-gen
├── requirements.txt
├── styles/                      # Style YAML + markdown guides
├── prompts/                     # Example prompt libraries + **kk-kb** (KB image/diagram archive)
├── examples/
├── lib/
├── data/                        # optional usage log, refs (see .gitignore)
└── docs/
    ├── SCOPE.md
    ├── CHROME-PUPPETEER.md
    └── FOLDER-LAYOUT.md         # this file
```

## Not in this repo (KB monorepo only)

The knowledge base keeps a **thin shim** at `kk-ai-ecosystem/tools/image-gen/` (`launch.js` + tiny `package.json`) plus **KB-specific artifacts** (e.g. `outputs/`, `data/refs/`) that stay versioned with content. That path is **not** a second copy of Rafiki — it forwards to this checkout via `RAFIKI_HOME` / sibling `../rafiki/` (see that repo’s `tools/image-gen/README.md`).

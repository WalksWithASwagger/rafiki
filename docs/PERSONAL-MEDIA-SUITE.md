# Personal Media Suite

Rafiki can index local image and video pipelines without copying their media.
Use this for private corpora such as `/Users/kk/Desktop/alex-samuel`.

## Rafiki vs the alex-samuel studio — who owns what

These are **two repos by design** (combined June 2026 via the Media Suite Hardening lane,
issues #169–#197):

- **`/Users/kk/Desktop/alex-samuel`** is the **live studio** — its own private git repo
  (`WalksWithASwagger/alex-samuel`). It holds the portrait→LoRA pipeline, the Floyo/ComfyUI
  video work (`andromeda_project/`), the media corpus, and client/festival deliverables.
  This is where generation actually happens.
- **Rafiki** is the **catalog / ops layer**. It **indexes the studio in place** — metadata
  only, no copying — via `lib/importers/alex_samuel.py`, and provides its own dry-run
  Replicate pipelines (`rafiki_train_lora`, `rafiki_video_generate`).

**Boundary rule (non-negotiable):** Rafiki is a **public, tool-only repo**. The studio's
media (real people's faces, client deliverables) is **private** and must never be committed
here — it stays in gitignored local roots. "Bringing work into Rafiki" means porting
*tooling* into `lib/`, while *media* lives under gitignored local roots, not git.

> Retirement of the standalone studio (folding the Floyo video + audio pipelines into
> Rafiki) is a tracked, phased effort — see the consolidation audit in `meta/audits/` and
> the open migration issues. Until that lands, the studio remains the source of truth.

## Local Root Config

Copy the template and keep the local file untracked:

```bash
cp config/media-roots.json.example config/media-roots.local.json
```

The local config uses this shape:

```json
{
  "roots": [
    {
      "key": "alex-samuel",
      "path": "/Users/kk/Desktop/alex-samuel",
      "importer": "alex-samuel",
      "enabled": true
    }
  ]
}
```

`config/media-roots.local.json`, `data/media-registry.json`,
`data/media-registry.csv`, `data/jobs/`, and `data/video-selections.json` are
local state and ignored by git.

## Commands

```bash
python generate.py import alex-samuel --root /Users/kk/Desktop/alex-samuel
python generate.py media index
python generate.py media index --incremental
python generate.py media search kris --kind video
python generate.py subjects list
python generate.py style anchors --source /path/to/style_anchors.json
python generate.py train lora --subject kris
python generate.py video generate --storyboard /path/to/storyboard.json
python generate.py video assemble --edit /path/to/edit.json
python generate.py serve --open
```

Training and video-generation commands default to dry-run. Pass `--execute`
only when the output destination, provider cost, and token setup are intentional.

## Portal

`python generate.py serve` opens the combined local suite at `/`.
The legacy image-only library remains available at `/library`.

The suite serves external media through `/media/<root>/<relative-path>` and
supports byte ranges for MP4 scrubbing.

The 2026-06-04 V1 hardening audit and phased workplan are archived in
[meta/audits/2026-06-04-v1-hardening-audit.md](../meta/audits/2026-06-04-v1-hardening-audit.md);
live planning is tracked in [ROADMAP.md](ROADMAP.md).

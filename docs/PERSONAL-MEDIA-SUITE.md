# Personal Media Suite

Rafiki can index local image and video pipelines without copying their media.
Use this for private corpora such as `/Users/kk/Desktop/alex-samuel`.

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

The current V1 hardening audit and phased workplan live in
[V1 Hardening Audit And Workplan](V1-HARDENING-AUDIT-2026-06-04.md).

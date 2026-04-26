# KB-import asset mirror

This folder holds **copies** of raster assets (and optional slide prompt markdown) gathered from the kk-ai-ecosystem inventory scanner, so you have one place under **Rafiki** to browse outputs without chasing `projects/`, sibling `notion-local/content/`, etc.

## Layout

| Path | Contents |
|------|----------|
| [`mirror/`](mirror/) | **Large / regenerable** — `gitignore`d. Subdirs = `inventory.json` `content_tree` + original relative path (see below). |
| [`prompt-stashes/`](prompt-stashes/) | Optional copies of `image-gen-prompts.md` / slide-adjacent `image-prompts.md` when you run the mirror script with `--include-prompt-stashes`. |

### `mirror/` naming

- **`mirror/<content_tree>/...`** — file was under that scan root (e.g. `kk-ai-ecosystem`, `notion-local-content`).
- **`mirror/<content_tree>/_under_notion_local/...`** — absolute path on disk lived under the Notion-local parent but **outside** the declared tree root (still tagged to the tree the scanner assigned).
- **`mirror/<content_tree>/_unscoped/...`** — fallback for odd paths.

**Source of truth for blobs** remains the original repos; this tree is a **curated mirror**. Re-run the mirror script after regenerating images.

## How to refresh

From **`kk-ai-ecosystem/`** root:

```bash
python3 ./content/assets/rafiki-outputs/scripts/scan_image_gen_assets.py
python3 ./content/assets/rafiki-outputs/scripts/mirror_assets_to_rafiki.py --dry-run
python3 ./content/assets/rafiki-outputs/scripts/mirror_assets_to_rafiki.py
```

Optional: also copy slide/keynote prompt markdown:

```bash
python3 ./content/assets/rafiki-outputs/scripts/mirror_assets_to_rafiki.py --include-prompt-stashes
```

Override paths:

```bash
python3 ./content/assets/rafiki-outputs/scripts/mirror_assets_to_rafiki.py \
  --inventory ./content/assets/rafiki-outputs/inventory.json \
  --rafiki /path/to/rafiki
```

## Canonical prompts

Batch **prompt strings** and style kits still live under [`../prompts/`](../prompts/) in this repo — not under `assets/kb-import/`.

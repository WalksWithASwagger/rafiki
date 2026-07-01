# Cross-Project Command Center

Rafiki can aggregate **every Rafiki-generated image across all your repos** into one dashboard —
not just the runs that live under this repo's `output/`. This is the "command center": one screen
to browse, search, filter, rate, and curate assets from many projects at once.

Two surfaces, same data:

- **Static library** — `output/library.html`. A self-contained page (works over `file://`, no
  server). Project / model / aspect / style filter chips, keyword search, sort, lightbox.
- **Live portal** — `python generate.py serve` → http://localhost:7433. The richer surface:
  persistent ratings, review queue, run detail, plus Generate / Curate / Spend / Teach modes.
  See [Portal Command Center](PORTAL-COMMAND-CENTER.md) for the full mode map and API.

Both read the same cross-project [asset registry](ASSET-REGISTRY.md); the library scans every
`run-*/run.json` directly, so it works even without a prebuilt registry cache.

## Pulling in projects that live outside this repo

Rafiki outputs scattered in other repos (e.g. a keynote repo, a festival repo, a sibling toolchain)
are folded in by **registration + symlink** — no copying, no duplication. The images stay in their
home repos; the command center just indexes them in place.

1. **Register** each external output directory (the dir that directly contains `run-*/`) in the
   local, gitignored `config/extra-outputs.local.json`:

   ```json
   {
     "keynote-slides": "/abs/path/to/keynote/assets/generated/slides",
     "festival-logo-v8": "/abs/path/to/festival/branding/outputs/logo-v8-pro"
   }
   ```

   Use source-prefixed keys (`cmvan-…`, `fpf-…`, `kkai-…`) so projects group cleanly in the filter
   chips and don't collide with names already under `output/`.

2. **Symlink** so the static library can resolve the files over `file://`:

   ```bash
   python generate.py link-projects   # creates output/<key> → /abs/path
   ```

   Skipping this is the #1 cause of broken thumbnails in `library.html`.

3. **Index + build:**

   ```bash
   python generate.py registry index   # registry now spans every project
   python generate.py library          # rebuild output/library.html
   ```

The registry and portal auto-discover registered projects on every scan (via
`lib/extra_outputs.load_extra_outputs()`), so the portal needs no extra step.

> `config/extra-outputs.local.json` and the `output/` symlinks are **local and gitignored** by
> design — they hold machine-specific absolute paths. The repo ships the pattern and the refresh
> tooling, not any one machine's project map.

## Non-standard (loose-image) imports

Some older or hand-organized outputs have images sitting **directly in a folder** with no `run-*/`
subdir. The registry only indexes `run-*`/`approved/` dirs, so `extra-outputs` registration would find
0 assets in them. Bring them in with a local **run-wrapper**: a `output/<name>/run-imported` symlink
pointing at the loose dir (`glob("run-*")` matches `run-imported`, and the collector reads its
top-level PNGs).

List these in the local, gitignored `config/loose-imports.local.json`:

```json
{
  "cmvan-title-redo": "/abs/path/to/keynote/assets/slides/cmvan-title-redo",
  "anim-accelerator": "/abs/path/to/.../ai-animation-accelerator/generated"
}
```

`scripts/refresh-command-center.sh` materializes the wrappers from this file on every run (idempotent;
skips sources that no longer exist). Register **one canonical path** per logical output — skip mirror
copies under `*-split/`, `*-preserved-*/`, or `agent-worktrees/`.

## One-command refresh

```bash
scripts/refresh-command-center.sh
```

Runs `link-projects` → `registry index` → `library` and prints the library path plus the `serve`
hint. Run it after generating new images anywhere, or after editing `extra-outputs.local.json`.

## Verifying nothing is broken

After a refresh, `python generate.py library` prints `N/N present`. If the two numbers differ, some
registered dir isn't resolving — re-run `link-projects`, or confirm the path in
`extra-outputs.local.json` still exists.

Related: [Asset Registry](ASSET-REGISTRY.md) · [Archive](ARCHIVE.md) · [Folder Layout](FOLDER-LAYOUT.md)

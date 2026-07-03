# Approved-Image Archive

Rafiki's `output/` accumulates a `run-*/` directory per generation batch.
Most runs contain a few keepers and a lot of also-rans. The **approved
archive** lets you curate the keepers into a stable set and safely delete
the rest.

## The flow

1. **Rate** images in the portal (`generate.py serve`) — click the star
   button. Ratings persist to `output/ratings.json`, keyed by
   `"<project>/<run-id>/<filename>"`.
2. **Approve** the starred images for a project:
   ```bash
   python generate.py approve rap-week-1
   python generate.py approve rap-week-1 --run 20260502-202936  # specific run
   ```
   This copies starred images into `output/rap-week-1/approved/` and
   appends an entry to `output/rap-week-1/approved/index.json` per image.
   Project names can also come from `config/extra-outputs.json` or
   `config/extra-outputs.local.json`; local mappings override shared ones.
   In that case, `approve <project>` writes to the configured project path's
   `approved/` directory while still reading ratings from `output/ratings.json`
   using the configured project key.
3. **Clean** old run dirs once their keepers are safely in `approved/`:
   ```bash
   python generate.py clean rap-week-1 --keep-approved --dry-run
   python generate.py clean rap-week-1 --keep-approved
   python generate.py clean rap-week-1 --older-than 30d
   ```
4. **View** the curated set:
   ```bash
   python generate.py view rap-week-1 --approved
   open output/rap-week-1/approved/viewer.html
   ```
5. **Browse the full local archive**:
   ```bash
   python generate.py library
   python generate.py library --thumbnail-cache
   python generate.py serve --open
   ```
   The master library scans every `run-*` image across `output/` and configured
   extra-output roots. Approved images are marked from `approved/index.json`,
   but draft runs remain visible until you clean them intentionally.
   Use the library filters to narrow by rating, source, run, approval state,
   project, model, aspect ratio, style, or prompt text. Keyboard review works
   on the active visible card: arrow keys move, `S` stars, `X` rejects, `0`
   clears the rating, `I` opens run details, and Enter opens the lightbox.
   The Info button opens the same run detail panel with links to the run
   viewer, project viewer, `run.json`, prompt file/source metadata, invocation
   surface, provider, state, timestamps, and the manifest JSON.
   Filename warnings are informational: the library flags exact filename
   repeats and simple normalized-stem matches within the same project so you
   can compare reruns before approving or cleaning anything.
   If a card metadata entry includes `superseded_by`, Run Detail also compares
   the local prompt, run, model, style, aspect ratio, and archive state against
   that linked archive card; missing targets stay visible as no-data states.
   The same detail panel can save feedback notes/change requests to
   `output/feedback.json`, save evaluation decisions/scores to
   `output/evaluations.json`, show a run-level decision summary, and stage a
   revision back into Prompt Studio.
   Thumbnail caching is opt-in. `library --thumbnail-cache` writes preview
   images under `output/.rafiki-cache/thumbnails/` and points grid cards at
   those previews while keeping each card's original image path for lightbox,
   download, detail, approval, and export state. You can prebuild the same
   cache without rewriting viewers:
   ```bash
   python generate.py archive-thumbnails --output-dir output --width 480
   python generate.py view rap-week-1 --thumbnail-cache --all-runs
   ```
   `.rafiki-cache/` is git-ignored and can be deleted at any time; rerun the
   command to rebuild it.
6. **Check archive health before cleanup**:
   ```bash
   python generate.py archive-health
   python generate.py archive-health --json
   python generate.py archive-health --cleanup-report
   ```
   This is read-only. It reports missing images, malformed `run.json` files,
   duplicate filenames, orphaned ratings/feedback/evaluation/metadata keys,
   image disk usage, and cleanup-risk counts before anyone deletes generated
   work. The cleanup report groups runs by project, labels low-risk candidates
   versus repair-first or human-review cases, and prints the dry-run follow-up
   command before any destructive cleanup is considered.
   When archive health is used as a release gate, point it at a controlled
   fixture or disposable output root with `--output-dir`; the default live
   `output/` archive is an operator advisory surface.
7. **Repair archive state reversibly**:
   ```bash
   python generate.py archive-repair
   python generate.py archive-repair --apply
   ```
   The default mode is a dry-run. `--apply` writes a rollback bundle under
   `output/.rafiki-cleanup/<timestamp>/` before changing local archive state.
   Repair removes missing manifest records, synthesizes manifests for image
   folders that lost `run.json`, quarantines exact byte-duplicate images, clears
   backed-up orphaned sidecar keys, and rebuilds the all-runs registry. It does
   not permanently delete quarantined files.

## Health page semantics

The live `/health` surface treats missing image records, malformed manifests,
orphaned sidecars, and cleanup-risk items as repair blockers. Failed generation
records are historical run state, not a regeneration queue; keep them unless an
operator explicitly chooses to rewrite history. Duplicate filename groups are
also informational after `archive-repair` reports no exact byte-duplicate
candidates remaining. They are useful for manual rerun comparison, but they are
not safe deletion instructions by themselves.

Machine-local extra-output mappings live in `config/extra-outputs.local.json`.
Prune stale entries there when `/health` reports offline local mounts; do not
replace those warnings with shared repo config unless the path exists for every
operator.

## Layout

```
output/
├── ratings.json                       # star/reject map, written by the portal
├── evaluations.json                   # decision/score/use-case map
└── rap-week-1/
    ├── run-20260502-202936/           # raw run output
    │   ├── 01-foo.png
    │   └── run.json
    └── approved/                      # curated set
        ├── 01-foo.png                 # copied from a starred run
        ├── index.json                 # provenance for every approved image
        └── viewer.html                # built by `view --approved`
```

## `index.json` schema

Each entry records where the approved image came from so you can rebuild
or trace it later:

```json
{
  "images": [
    {
      "slug": "01-foo.png",
      "source_run": "run-20260502-202936",
      "original_file": "01-foo.png",
      "name": "Foo Concept",
      "prompt": "A glowing neural network …",
      "approved_at": "2026-05-02 21:14:08",
      "model": "gpt-image-2",
      "aspect_ratio": "16:9",
      "style": "kk"
    }
  ]
}
```

## Behaviour notes

- **Idempotent.** Running `approve` twice for the same run is a no-op —
  entries are keyed by `(source_run, original_file)`.
- **Filename collisions.** When two distinct runs both produced
  `01-foo.png`, the second is renamed `<run-id>__01-foo.png` in
  `approved/`. The original filename is preserved in
  `index.json.original_file`.
- **Library filename warnings do not mutate files.** Exact and similar
  filename warnings only appear in the master library cards and run detail
  panel. They do not approve, dedupe, rename, or delete anything.
- **`clean --keep-approved` is conservative.** A `run-*/` dir is only
  eligible for deletion when *every* image listed in its `run.json` has a
  matching `approved/index.json` entry for that same `source_run`. If
  even one image in the run hasn't been approved, the run is kept.
- **Extra-output projects stay scoped to their configured path.** If a
  project name appears in `extra-outputs`, `approve` and `clean` use that
  path instead of falling back to `output/<project>/`. Missing configured
  paths fail closed with `FileNotFoundError`.
- **`--older-than 30d` and `--keep-approved` compose.** When both are
  passed, both conditions must hold before a run is deleted.
- **`approved/` is never touched by `clean`.**
- **`archive-health` is a report, not a cleanup command.** It does not mutate
  images, ratings, feedback, evaluations, archive metadata, manifests, or
  approved sets. The `--cleanup-report` view is also advisory only; candidate
  runs still require a separate `clean --keep-approved --dry-run` review.
- **`archive-repair --apply` is reversible-first.** It can rewrite manifests
  and move duplicate/empty runs into `output/.rafiki-cleanup/`, but it keeps a
  repair manifest, sidecar backups, run-json backups, and quarantined files for
  human review before any permanent deletion.
- **Thumbnail/cache paths are explicit.** Default library and viewer rebuilds
  continue to reference original images directly. Use `archive-thumbnails`,
  `library --thumbnail-cache`, or `view --thumbnail-cache` when a large local
  archive needs lighter preview images.

## Where this lives

- CLI dispatch — `generate.py` (`approve`, `clean`, `view --approved`)
- Full archive viewer — `generate.py library`, `generate.py serve`
- Archive curation logic — `lib/archive.py`
- Archive health report — `lib/archive_health.py`
- Thumbnail cache helper — `lib/thumbnail_cache.py`
- Tests — `tests/test_archive.py`, `tests/test_archive_health.py`

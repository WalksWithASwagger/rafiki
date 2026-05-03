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

## Layout

```
output/
├── ratings.json                       # star/reject map, written by the portal
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
- **`clean --keep-approved` is conservative.** A `run-*/` dir is only
  eligible for deletion when *every* image listed in its `run.json` has a
  matching `approved/index.json` entry for that same `source_run`. If
  even one image in the run hasn't been approved, the run is kept.
- **`--older-than 30d` and `--keep-approved` compose.** When both are
  passed, both conditions must hold before a run is deleted.
- **`approved/` is never touched by `clean`.**

## Where this lives

- CLI dispatch — `generate.py` (`approve`, `clean`, `view --approved`)
- All logic — `lib/archive.py`
- Tests — `tests/test_archive.py`

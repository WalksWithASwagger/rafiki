# Deployment — Vercel Static Hosting

`generate.py deploy <project>` ships a project's viewer directory to Vercel as
a static site. Pairs cleanly with `--self-contained` viewers (issue #20) for
zero-companion-file deploys.

## One-time setup

Install the Vercel CLI globally and authenticate:

```bash
npm install -g vercel
vercel login                        # opens browser, caches creds
```

The first `vercel deploy …` from this repo will prompt to link a Vercel
project — accept the defaults (one project per Rafiki project name is fine).
Subsequent deploys are non-interactive.

## Usage

Preview deploy (default — gets a unique `*.vercel.app` URL):

```bash
python generate.py deploy rap-all-weeks
```

Production deploy (assigns the project's primary domain):

```bash
python generate.py deploy rap-all-weeks --prod
```

Dry run (prints the command, doesn't execute):

```bash
python generate.py deploy rap-all-weeks --dry-run
```

Custom viewer directory:

```bash
python generate.py deploy rap-all-weeks --viewer-dir output/rap-all-weeks/approved
```

## Readiness Checks

The local portal exposes a read-only deploy readiness endpoint:

```bash
curl http://127.0.0.1:7433/api/deploy-readiness
```

It reports whether the Vercel CLI is installed, whether portal Basic auth is
configured before public binding, whether provider keys are present, and whether
a selected static viewer has `viewer.html`. It never prints secret values and
does not deploy anything.

For static review deploys, a provider key is optional: the viewer is already
generated. For an interactive public portal, set `PORTAL_USERNAME` and
`PORTAL_PASSWORD` before using `--public`.

## What it deploys

- Default target: `output/<project>/` (or `output/<project>/approved/` if it
  contains a `viewer.html`).
- The directory must contain a `viewer.html`.
- A minimal `vercel.json` (`{"version": 2}`) is created in the viewer dir if
  one isn't already there. Existing `vercel.json` files are left alone.
- All sibling files (`run-*/`, image PNGs, etc.) are uploaded so relative
  `<img src="../run-XXX/foo.png">` references resolve.

## Source Mapping

Portal static deploy actions report how the deployed viewer maps back to local
archive cards:

- `approved/` viewers map through `approved/index.json`.
- `run-*` viewers map through that run's `run.json`.
- project-root viewers map to all `run-*` manifest images in the project.
- custom viewer directories outside those shapes report `unmapped` with a
  reason and do not stamp card metadata.

Successful non-dry-run portal deploys stamp mapped source cards as `deployed`
in `output/archive-metadata.json`. Dry runs report the same source mapping
without writing metadata or calling Vercel.

## Caveats

- The Vercel CLI must be on `$PATH`. Run `which vercel` if the command fails.
- First deploy is interactive (project linking) — run it once from your
  terminal before automating.
- For a self-contained, single-file deploy (no relative image paths to ship),
  use the `--self-contained` viewer flag (issue #20) which inlines images as
  data URLs.

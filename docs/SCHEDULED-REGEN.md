# Scheduled Regeneration

A lightweight config layer over the existing batch pipeline. Lets evergreen prompt sets (newsletter heroes, ecosystem diagrams, brand assets) refresh on a cadence so they keep pace with model and style improvements.

## Quick start

```bash
cp config/scheduled-regen.json.example config/scheduled-regen.json
# edit jobs to taste

python generate.py regen --dry-run   # preview: which jobs are due?
python generate.py regen             # run any due jobs (with confirmation)
python generate.py regen --yes       # same, no prompt — for automation
python generate.py regen --name foo  # force-run a specific job, ignoring schedule
```

The real `config/scheduled-regen.json` is gitignored — the `.example` file is the schema reference.
Keep private or machine-specific paths in the gitignored local config. The
tracked example uses repo-relative paths only.

## Schema

`config/scheduled-regen.json` is a JSON array of job objects:

| Field           | Type     | Required | Description |
|-----------------|----------|----------|-------------|
| `name`          | string   | yes      | Human-readable job id (also used with `--name`) |
| `prompt_file`   | string   | yes      | Path to `image-prompts.md`-style file (relative to repo root) |
| `output_dir`    | string   | yes      | Where `run-*/` directories land |
| `interval_days` | int > 0  | yes      | Re-run if the latest `run-*/` is older than this |
| `model`         | string   | no       | Rafiki model id or alias (passed to `-m`) |
| `style`         | string   | no       | Style preset (passed to `--style`) |
| `notify`        | bool     | no       | Print a notification line after the run (default: false) |
| `workers`       | int      | no       | Parallel workers (default: 2) |

A job is **due** when `output_dir` either contains no `run-*/` directories or its newest one has an mtime older than `interval_days`.

## How it runs

`regen` shells out to `python generate.py -f <prompt_file> -d <output_dir> -w <workers> [--style ...] [-m ...]` for each due job. It does **not** auto-approve output — runs land in the regular `run-*/` layout, and a human reviews via the viewer (`python generate.py view <project>` or `serve`).

## Recipes

### Daily Due-Job Check

Use this for a local runner that wakes up daily, checks for due jobs, and runs
only when an interval has elapsed.

```bash
cd /path/to/rafiki
python generate.py regen --dry-run
python generate.py regen --yes
```

Dry-run first when adding or editing jobs. It prints each configured job, its
interval, and whether its latest `run-*/` is due.

### Force One Evergreen Prompt Set

Use a named run after checking the config shape:

```bash
cd /path/to/rafiki
python generate.py regen --config config/scheduled-regen.json --dry-run
python generate.py regen --name upgrade-newsletter-heroes --yes
```

Keep the `prompt_file` and `output_dir` values repo-relative unless you are
using a private local config. If a job must point at a sibling repo or external
disk, keep that absolute path in `config/scheduled-regen.json`, not in the
tracked example.

### Refresh Prompt Library, Then Rebuild Review Surfaces

Use this after model/style changes when an evergreen batch should be reviewed
again from the portal or static viewers.

```bash
cd /path/to/rafiki
python generate.py regen --name bcai-ecosystem-diagrams --yes
python generate.py view bcai-ecosystem --all-runs
python generate.py library
```

This leaves new images in a fresh `run-*/` directory, rebuilds comparison
viewers, and refreshes the master library. It does not approve, export, or
delete any assets.

### Post-Run Summary For Local Agents

A local agent or cron wrapper can run the dry-run check first, execute due jobs,
then report only changed project directories:

```bash
cd /path/to/rafiki
python generate.py regen --dry-run
python generate.py regen --yes
python generate.py library
```

Report the generated `run-*/` paths and `output/library.html` to the operator.
Do not send provider keys, prompt text from private files, or generated images
to external services unless that is part of a separate approved workflow.

## Automating with Claude Code

Use the `schedule` skill (or any cron-like runner) to invoke `python generate.py regen --yes` daily. A daily wake-up that finds nothing due is essentially free; a job whose interval has elapsed will run on the next cycle.

Example (Claude Code routine, conceptually):

```
schedule: cron "0 8 * * *"
command: cd /path/to/rafiki && python generate.py regen --yes
```

Pair with `notify: true` on individual jobs to get a one-line confirmation in the run log when an evergreen batch refreshes.

See also [Local Automation And Agent Archive Recipes](RECIPES.md) for
copy-paste dry-run recipes and agent archive jobs.

Prefer a two-step automation while a job is new:

```
schedule: cron "0 8 * * *"
command: cd /path/to/rafiki && python generate.py regen --dry-run && python generate.py regen --yes
```

Once the config has behaved for a few cycles, the dry-run line can stay as a
cheap audit trail or move to a separate status check.

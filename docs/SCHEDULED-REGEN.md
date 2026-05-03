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

## Automating with Claude Code

Use the `schedule` skill (or any cron-like runner) to invoke `python generate.py regen --yes` daily. A daily wake-up that finds nothing due is essentially free; a job whose interval has elapsed will run on the next cycle.

Example (Claude Code routine, conceptually):

```
schedule: cron "0 8 * * *"
command: cd /path/to/rafiki && python generate.py regen --yes
```

Pair with `notify: true` on individual jobs to get a one-line confirmation in the run log when an evergreen batch refreshes.

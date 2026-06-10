# Local Automation And Agent Archive Recipes

Copy-paste dry-run recipes for scheduled regeneration, prompt-library refresh,
post-run summaries, and common agent archive jobs. Every command below was
verified locally without provider spend unless noted.

Related docs:

- [Scheduled Regeneration](SCHEDULED-REGEN.md) — job schema and cron patterns
- [MCP](MCP.md) — typed tool surface for agents
- [Library And Archive Roadmap](LIBRARY-ARCHIVE-ROADMAP.md) — archive agent
  contract goals

## Setup Once

```bash
cd /path/to/rafiki
cp config/scheduled-regen.json.example config/scheduled-regen.json
# edit jobs in the gitignored local config
```

Keep private or machine-specific paths in `config/scheduled-regen.json`. The
tracked example uses repo-relative paths only.

## Scheduled Regeneration

**Goal:** Preview which evergreen prompt batches are due, then run only due
jobs.

```bash
python generate.py regen --dry-run
python generate.py regen --yes
```

Use the tracked example config when the local config does not exist yet:

```bash
python generate.py regen --config config/scheduled-regen.json.example --dry-run
```

**Expected output:** A table of configured jobs with `[DUE]` or skip status,
interval days, and last-run age. A real `--yes` run creates fresh `run-*/`
directories under each job's `output_dir` and does not auto-approve images.

## Prompt Library Refresh

**Goal:** Force one evergreen batch to regenerate after model or style changes,
then rebuild review surfaces.

```bash
python generate.py regen --config config/scheduled-regen.json.example --dry-run
python generate.py regen --name upgrade-newsletter-heroes --yes
python generate.py view upgrade-newsletter --all-runs
python generate.py library
```

Replace the job name with any configured `name` field. **Expected output:** A
new `run-*/` directory, updated comparison viewer HTML, and a rebuilt
`output/library.html`.

## Post-Run Summary

**Goal:** Run due jobs, refresh the master library, and report paths for human
or agent review.

```bash
python generate.py regen --dry-run
python generate.py regen --yes
python generate.py library
python generate.py archive-health --json
```

**Expected output:** Due-job execution log, `output/library.html`, and a JSON
health summary with project/run counts. Report generated `run-*/` paths only;
do not send private prompt text or provider keys externally.

## Agent Recipe: Find Unused Good Assets

**Goal:** Search the registry for approved or starred candidates that have not
been exported.

CLI:

```bash
python generate.py registry search "workshop" --limit 20
python generate.py registry export --format json --dry-run
```

MCP (`rafiki_registry_search`):

```json
{"query": "workshop", "limit": 20}
```

**Expected output:** Matching registry entries with titles, tags, approval
state, and export metadata when indexed.

## Agent Recipe: Compare These Runs

**Goal:** Inspect archive health and rebuild viewers for side-by-side review
without regenerating images.

CLI:

```bash
python generate.py archive-health --cleanup-report
python generate.py view <project> --all-runs
python generate.py viewer-rebuild <project> --all-runs --dry-run
```

MCP:

```json
{"output_root": "/absolute/path/to/output", "cleanup_report": true}
```

```json
{"project": "<project>", "all_runs": true, "dry_run": true}
```

**Expected output:** Health report with duplicate filenames and cleanup
candidates; dry-run viewer rebuild paths for each run.

## Agent Recipe: Prepare A Web Gallery Shortlist

**Goal:** Export approved or latest-run assets and rebuild the master library
for a static review handoff.

CLI:

```bash
python generate.py registry index
python generate.py registry export --format json
python generate.py canva-export <project> --dry-run
python generate.py library
```

MCP:

```json
{"format": "json", "dry_run": true}
```

```json
{"project": "<project>", "dry_run": true}
```

**Expected output:** Registry export preview, Canva bundle path preview, and
`output/library.html` for local browsing.

## Agent Recipe: Audit Stale Generated Assets

**Goal:** Read-only audit of missing files, malformed manifests, sidecar
orphans, and conservative cleanup candidates.

CLI:

```bash
python generate.py archive-health --json
python generate.py archive-health --cleanup-report
```

MCP (`rafiki_archive_health`):

```json
{"cleanup_report": true}
```

**Expected output:** JSON with `ok`, summary counts, missing-image lists, and
suggested dry-run cleanup commands. No files are mutated.

## Verification

After editing these recipes:

```bash
npm run docs:check
npm run smoke:dry-run
```

For scheduled regen specifically, always dry-run before `--yes` when adding or
changing jobs.

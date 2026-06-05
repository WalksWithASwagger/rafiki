# Rafiki Handoff - 2026-06-05 Keynote Workflow

This handoff documents the public-release and keynote visual workflow work
completed on 2026-06-05 for `WalksWithASwagger/rafiki`.

## What Shipped

- The existing Rafiki repository was prepared for public release with a
  secrets-only gate.
- A public use case was added for the KrisKrug.co keynote visual workflow:
  ideas and words become prompt packs, candidates, review decisions, slides,
  and downstream artifacts.
- A public-safe example prompt pack was added at
  `examples/keynote-visual-workflow-prompt-pack.md`.
- KrisKrug.co post `12183` was updated to link Rafiki as the local-first tool
  used for batch generation, review, and export.
- GitHub issues were created for the next Rafiki product improvements:
  - #180: Library artifact-chain metadata.
  - #181: Reference-first style chooser.
  - #182: Workflow-first interface mode.
- PR #183 merged those three issue lanes into `main`:
  <https://github.com/WalksWithASwagger/rafiki/pull/183>

## PR #183 Merge

Merged commit:

- `47c6adc` - `Swarm Rafiki keynote workflow issues`

What the PR added:

- `output/archive-metadata.json` now supports artifact-chain fields:
  source use case, public source URL, prompt pack, prompt-pack section,
  artifact review state, export targets, and downstream uses.
- Registry JSON/CSV export and search include the artifact-chain fields.
- Library Run Detail can save/edit those fields, and cards expose the artifact
  review state in the metadata badge.
- Prompt Studio now has searchable style reference cards from
  `styles/styles.yaml`, while keeping blank default, `none`, and composed
  styles such as `kk+bcai`.
- Unknown style values produce visible guidance and are blocked before submit.
- The Library portal now has a Workflow mode that stages the keynote visual
  workflow prompt pack into Prompt Studio as a dry-run batch.

## Review Notes

- PR #183 had no blocking review findings.
- GitHub would not allow a formal approval because the same account opened the
  PR, so a review comment was posted instead:
  <https://github.com/WalksWithASwagger/rafiki/pull/183#issuecomment-4633748105>
- Remote PR checks passed:
  - `test`
  - `pr-sync`
- Skipped checks were expected automation lanes:
  - `issue-sync`
  - `review`

## Verification

Commands run before merge:

```bash
python3 -m py_compile lib/renderers/library.py lib/renderers/library_styles.py lib/archive_metadata.py lib/registry.py
python3 -m pytest tests/test_archive_metadata.py tests/test_registry.py tests/test_library_renderer.py -q
npm run docs:check
npm run e2e:portal
npm run verify
gitleaks protect --staged --verbose
```

Results:

- Targeted pytest: `37 passed`.
- Full `npm run verify`: passed with `328 passed, 1 warning`; the warning is
  the existing Python 3.14 deprecation warning from `google.genai.types`.
- Portal E2E: passed; it verified Workflow staging, style reference cards,
  artifact metadata save/search, desktop/mobile image loading, and no mobile
  generate overflow.
- Docs link check: passed, 34 Markdown files checked.
- Dry-run smoke: passed.
- npm package dry-run: passed, 118 package files.
- Staged gitleaks scan: passed, no leaks found.

## Files And Docs Updated

- `docs/use-cases/keynote-visual-workflow.md`
- `examples/keynote-visual-workflow-prompt-pack.md`
- `docs/PUBLIC-RELEASE-CHECKLIST-2026-06-05.md`
- `docs/ASSET-REGISTRY.md`
- `docs/LIBRARY-ARCHIVE-ROADMAP.md`
- `docs/PORTAL-COMMAND-CENTER.md`
- `lib/archive_metadata.py`
- `lib/registry.py`
- `lib/renderers/library.py`
- `lib/renderers/library_styles.py`
- `scripts/portal-e2e-smoke.mjs`
- `tests/test_archive_metadata.py`
- `tests/test_library_renderer.py`
- `tests/test_registry.py`

## Public Boundary

- `.env`, `node_modules/`, `output/`, and `.venv/` remain ignored.
- The public-release gate was secrets-only. Non-secret tracked prompt examples,
  historical notes, and docs are accepted as public repo content.
- `prompts/`, `assets/`, `output/`, and local dependency folders remain outside
  the npm package allowlist unless explicitly added to `package.json`.

## Local Worktree Notes

These untracked files were intentionally left alone as separate BC AI prompt
and reference work:

- `prompts/bcai/aefl-canva-grounded-style-bakeoff-2026.md`
- `prompts/bcai/aefl-luma-thumbnails-2026.md`
- `prompts/bcai/comox-valley-luma-seasonal-2026-native-branding.md`
- `prompts/bcai/reference/`

Do not delete, stage, or fold them into a Rafiki closeout unless the next task
explicitly resumes that prompt work.

## Recommended Next Steps

1. Visually review the new Workflow mode in the local portal during the next
   image-generation session.
2. Use #180-#182 follow-on comments as the acceptance trail if any rough edges
   appear after real keynote batches.
3. Keep Canva automation out of v1; use Rafiki for prompt packs, generation,
   review, metadata, and export preparation, then finish layers manually.
4. For any future public release changes, rerun the public checklist rather
   than relying on this dated snapshot.

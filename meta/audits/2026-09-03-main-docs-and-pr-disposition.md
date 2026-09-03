# Rafiki Main Sweep — 2026-09-03

Last reviewed: 2026-09-03

This audit records the live GitHub queue against `main` after the
2026-08-02 deps-landing swarm and the later August merges, then the
documentation corrections that follow from that queue. It is a dated
snapshot. Do not treat it as authorization to merge `needs-human` work.

## Why This Exists

Kris asked to get the open issue/PR pile safely onto `main` and then
run a documentation sweep. "Safely" here means: merge only what is
already green, up to date, and within existing batching conventions;
rebase review-ready migrations without crossing live-provider or
live-MCP gates; close work that already landed; and make the living
docs describe the current tree.

## Current `main`

- Tip at audit start: `368be75` (`docs: record Slingsby GBF image handoff`, #446).
- This session squash-merged #440 onto that tip (`01e8413`, CodeQL action
  pins `v4.37.3` → `v4.37.8`).
- Required protection on `main` remains `test` + `secret-scan`.
- The delivery pipeline still does not auto-merge. Humans own merge of
  core-runtime majors and anything labeled `needs-human`.

## Already Landed (issues were still open)

These tracking issues described work that was already on `main`. They
were closed as completed during this sweep:

| Issue | Landed by | Commit |
|---|---|---|
| #423 tenacity 9 | #408 | `def7c38` |
| #424 chalk 6 | #405 | `8ec7a12` |
| #425 eslint 10 + react-hooks 7 | #427 | `eac51ac` |

Related already-merged batches that #420 still listed as open:

- #404 puppeteer 25.4.0
- #406 pip-audit ≥2.10.1
- #411 pytest 9
- #426 jsdom 30 + jest-dom 7 (superseded #412/#409)
- #403 Fellowship Reading Room handoff
- #445 frontend security audit
- #444 / #446 Slingsby Advisors proposal visuals + GBF image handoff

## Merged This Session

| PR | Kind | Why it was safe |
|---|---|---|
| #440 CodeQL action pins v4.37.8 | patch, SHA-pinned | Green, up to date with `main`, no product code |

#431 (puppeteer 25.4.0 → 25.9.0) was rebased onto the post-#440 `main`.
It is a same-major runtime-tool bump with prior puppeteer-25 E2E
validation in #391. Merge only after the post-rebase `test` gate is
green. Do not treat a stale pre-rebase green as sufficient.

## Rebased, Still Human-Gated

Issue #448 asked to land #429 and #430. Both were a month behind
`main`. GitHub update-branch succeeded; both now target current `main`
and need a fresh `test` run.

| PR | Tracks | Why it is not merged here |
|---|---|---|
| #429 google-genai ≥2.16.0 + CI lock | #421 | Core Gemini provider. PR itself forbids auto-merge and requires a maintainer live Gemini dry-run. #421 is `needs-human`. |
| #430 mcp SDK 1.x → 2.x | #422 | Real API rename (`FastMCP` → `MCPServer`) plus lock regen. PR itself forbids auto-merge and requires a live MCP client smoke. #422 is `needs-human`. |

Dependabot #410 (naive `mcp>=2.0.0` floor, red lock gate) was closed
in favor of #430.

## Held

| PR / issue | Disposition |
|---|---|
| #428 / #388 / #383 TypeScript 7 | CI red. `typescript-eslint` peers `typescript <6.1` and refuses TS 7.0 at runtime (upstream typescript-eslint#10940, targets TS ≥7.1). Hold on 5.9.x. |
| #447 frontend-npm group (16 updates) | `test` red. Too large to land as one Dependabot bundle. |
| #432 openai ≥3.3.1 | Major, `test` red. Needs a dedicated migration issue if pursued. |
| #434 pillow ≥12.3.0 | Major. Last recorded `test` was green on 2026-08-23 but the PR is behind `main` and has no dedicated land issue. Do not merge on a stale green. |
| #435 google-genai ≥2.19.0 | `test` red. Overlaps #429 (floor 2.16.0). Revisit only after #429 lands. |
| #437 `@vitejs/plugin-react` 6 | Major, `test` red. |
| #438 `@types/node` 26 | Major types bump, `test` red. |
| #439 `@eslint/js` 10 | `test` red. Frontend already has `eslint` 10 via #427; this leftover `@eslint/js` 9→10 bump still needs a green dedicated PR. |
| #433 jsonschema ≥4.26.0 | Last `test` green, but behind `main` and likely to fail the hashed-lock gate after rebase. Safe-looking floor only after a regenerated lock. |

## Open Issue Queue (after this sweep)

Still human-gated or blocked — do not promote to `agent:ready`:

- Release / policy: #327, #334, #335, #337
- Package boundary: #323, #332, #333
- Content / research: #69, #200, #201, #264, #265, #266, #270, #314, #417, #418
- Studio retirement epic #268 and cutover #267
- Evals: #336 (blocked on #335)
- Style-separation guard: #416
- Core-runtime migrations still open: #421, #422, #388
- Tracking: #308, #420, #448

No open issue currently carries `agent:ready`. That is correct.

## Documentation Corrections In This Sweep

Living docs were describing July state. Updates:

- `docs/ROADMAP.md` last-reviewed date, audit pointer, test-count floor,
  and a near-term note for the remaining deps pile.
- `docs/INDEX.md` points at this audit; MCP output-contract blurb
  matches the ratified status.
- `docs/CDN-PUBLISHING-RESEARCH.md` status matches closed #202
  (decision recorded: defer).
- `docs/LIBRARY-ARCHIVE-ROADMAP.md` last-reviewed date (foundation
  already marked shipped).

Historical audits under `meta/audits/` and dated handoff docs are
left as snapshots. They are not rewritten.

## Verification

Commands intended for the docs PR:

- `npm run docs:check`
- `npm run pack:check`
- `git diff --check`

`npm test` / `npm run doctor` are not required to prove Markdown
link and status edits, but should still be reported if the
environment can run them.

## Recommended Next Step

1. After #431's post-rebase `test` is green, squash-merge it.
2. After #429 and #430 are green on current `main`, Kris runs the
   live Gemini dry-run and live MCP client smoke named in those PRs,
   then squash-merges in that order (#429 then #430).
3. Close #421 / #422 / #435 / #448 only after those merges.
4. Leave TypeScript 7 and the red Dependabot majors closed or held
   until each has a dedicated green migration PR.

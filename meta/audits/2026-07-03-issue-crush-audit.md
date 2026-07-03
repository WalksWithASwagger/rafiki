# Rafiki Issue-Crush Audit - 2026-07-03

## Summary

This is a read-only issue-crush report for the current open Rafiki GitHub issue
queue. No GitHub issues were commented on or closed during this pass.

Current open queue:

- 12 open issues.
- 2 likely close candidates because the issue comments already say the core
  work shipped: #263 and #271.
- 4 explicitly human-gated or blocked issues: #69, #200, #201, #267.
- 6 active roadmap/planning issues to keep: #264, #265, #266, #268, #270, #274.

## Recommended First Actions

1. Close #263 after posting a short completion comment. Evidence: issue comments
   state Track 1 Phase 2 is complete via PR #279, and the roadmap now treats
   Floyo transport, lip-sync, clip audio-mux, and keyframe stills as shipped.
2. Close #271 as the core clips review surface. Evidence: issue comments say
   PR #280 completed the core Video Lab surface with notes; optional audio
   badges and one-at-a-time playback should become follow-up issues only if
   still wanted.
3. Leave #69, #200, #201, and #267 open. They are intentionally blocked by
   credentials, human review, or predecessor tracks.
4. Keep #268 open as the umbrella epic and update its checklist only after
   #263/#271 are actually closed.
5. Treat #265 as the best next implementation issue after the Generate PR lands:
   it is small, testable, and reduces migration uncertainty.

## Issue Disposition

| Issue | Recommendation | Evidence | Next action |
|---|---|---|---|
| #69 Verify Notion signed upload against live workspace | Keep open, needs-human | Comments repeatedly mark this credential-gated; mocked/dry-run coverage exists, live Notion test is still required. | Run only when throwaway Notion credentials/database are available. |
| #200 Validate Curriculum Atlas story rail | Keep open, needs-human | Acceptance requires a real Teach-mode review session and human notes. | Schedule/perform human review; no agent implementation yet. |
| #201 Curriculum Atlas presentation/export controls | Keep blocked | Issue is explicitly blocked by #200. | Do nothing until #200 findings exist. |
| #263 Floyo video pipeline | Close as shipped | Comments say M1 complete, Phase 2 complete, and Track 1 done via PR #279. | Comment with closure evidence, then close. |
| #264 Audio surface | Keep scoped | Audio muxing/media indexing exists, but the issue asks for a first-class audio production surface and a scope decision. | Decide V1 scope: audio reference management first, not generation. |
| #265 Production-knowledge indexing | Keep, next implementation candidate | Importer has media/training coverage, but issue asks for `keyframes.json`, `style_lora.json`, and production `.md` knowledge routing. | Implement as a small importer/docs/test PR. |
| #266 Canonical gitignored media home | Keep | Local roots exist, but the issue asks for a documented canonical media-root decision and migration approach. | Write the decision doc/runbook before moving anything. |
| #267 Retirement cutover | Keep blocked | Acceptance depends on #263, #270, #271, #264, #265, and #266 plus KK sign-off and backup. | Revisit only after predecessor tracks close. |
| #268 Alex-samuel retirement epic | Keep open | Umbrella issue still tracks active children and cutover state. | Update checklist after closing shipped child issues. |
| #270 LoRA lite slice | Keep | `lib/training.py` exists, but issue asks for film LoRA training plus immediate sample gallery. | Implement after #265/#266 unless KK prioritizes LoRA now. |
| #271 Clips review surface | Close core ask | Comment says PR #280 effectively completed the core Video Lab surface and notes. | Close core issue; split optional niceties if desired. |
| #274 Gorgeous-ghost carve-out | Keep open | Phase A done and Phase B partially done; bulk media/cutover remain deferred. | Keep as migration tracker until #266/#267 resolve. |

## Recommended Work Order After The Generate PR

1. Issue hygiene PR/comment pass: close #263 and #271, update #268 checklist,
   and leave clear "still blocked" comments only where useful.
2. #265 production-knowledge indexing: add importer coverage for structured
   manifests and production docs.
3. #266 canonical media home: document the local media-root decision and the
   move-vs-repoint migration policy.
4. #270 LoRA lite: film-only LoRA training plus immediate sample gallery.
5. #264 audio surface: keep it small; start with reference management and local
   assembly, not new music generation.
6. #267 cutover: only after predecessor tracks are closed and KK approves backup
   plus archival.

## Verification Notes

Commands and sources inspected:

- `gh issue view` for #69, #200, #201, #263, #264, #265, #266, #267, #268, #270,
  #271, and #274.
- `docs/ROADMAP.md`
- `docs/GENERATE-UI-NEXT-WORK-PLAN-2026-07.md`
- `docs/PERSONAL-MEDIA-SUITE.md`
- `lib/training.py`, `lib/clip_audio.py`, `lib/keyframe_jobs.py`,
  `lib/media_registry.py`, `lib/importers/alex_samuel.py`,
  `lib/renderers/media_suite.py`, and related tests by targeted search.

No remote issue state was changed.

# Changelog

Public history of Rafiki. Built from the published GitHub release and merged
pull requests (`gh release view v1.1.0`, `gh pr list --state merged`). Nothing
here is guessed. If a date, version, or outcome is unclear, it is marked
TODO for KK.

`package.json` is still `1.1.0`. There is no later GitHub release after
2026-05-03.

## Unreleased since v1.1.0

212 pull requests merged after the v1.1.0 tag (2026-05-03T12:42:54Z through
2026-09-26). Grouped by theme. Dependency-only bumps are listed last.

### Portal, frontend, and Generate UI

The live portal is now the TypeScript shell in `frontend/`, with Python still
owning files, APIs, and provider calls. Generate UI landed as a dry-run-first
workspace.

- Portal curation, export actions, usage/feedback, pricing, billing import,
  archive metadata, and prompt-studio recovery: #74, #106, #108, #110, #112,
  #154
- All-runs archive viewer, review filters, run detail, filename warnings,
  lineage comparisons, thumbnail cache, and library CSS extract: #96, #98,
  #100, #103, #138, #139, #151, #155
- Portal modes, Curriculum Atlas, teaching aids, story mode, evaluations,
  and quality/archive-health work: #121, #123, #124, #125, #140
- Media-suite hardening, importer warnings, Library filters, subject
  workspaces, and cost previews: #176, #234, #238, #240, #242
- Clips in the project, Video Lab Like/Love/Cut labels: #280, #283
- Replace the live portal with the rafikki frontend, then Generate UI V1
  plus dry-run history, inline batch overrides, empty/loading/error states,
  reference-picker filters, and wait-semantics docs: #287, #288, #289, #290,
  #299, #300, #301, #302, #303, #304
- Frontend test foundation and removal of an unreachable catalog: #351, #345
- Portal mutation-request guard: #344
- Frontend inclusion decision for the npm package (source stays out of the
  tarball): #301

### Archive, library, media suite, and command center

- Extra-output archive commands, registry-backed library viewer, registry
  export/cache refresh, and command-center ingest: #75, #76, #150, #153, #159
- Registry/archive/billing extracted from `generate.py`: #225
- Media-suite acceptance, importer fixtures, export presets, lineage
  suggestions, and MCP warning/job status: #231, #233, #235, #236, #237
- Workspace hygiene report: #135

### MCP

- Typed workflow wrappers, archive/library wrappers, and MCP.md coverage
  tests: #63, #152, #222, #226
- Output contract (ok/success/tool envelope, errors, counts, paths/URLs)
  plus ratification docs and eval: #255, #256, #257, #258, #259, #260, #261

### Floyo and video

Floyo hosted-ComfyUI path, then Phase 2 lip-sync, clip audio-mux, and
keyframe-gen. All of these cite #263 or #271 in the PR titles.

- Provider + wan22_endframe, Cloudflare curl transport: #273, #275
- Lip-sync (infinitetalk, multitalk), clip audio-mux, keyframe-gen: #276,
  #277, #279
- Readable clip names, filename-based deposits, workflow snippets: #281,
  #282, #285

### Varlock and secrets

Secrets go through Varlock (`.env.schema` + `varlock load` / `varlock run`).
Not 1Password. Not `op://`. Not `op read`.

- Env schema, runtime contract, selective shared imports: #309, #312, #340
- Protect environment file variants: #343

### Delivery pipeline, CI, and packaging

- Docs index + link smoke, doctor expansion, agentic delivery contract,
  viewer/pipeline coverage: #61, #64, #67, #71
- Linear-era pipeline hardening (#80) was later retired: #346
- Portal E2E smoke and optional visual artifacts: #119, #134
- CI runtime hygiene, ruff + gitleaks, verify gate, hashed Python 3.11 CI
  lock, Node 22 / 22.13 floor, dependency audit, supply-chain monitoring,
  Dependabot policy compatibility: #136, #163, #206, #354, #355, #356, #357,
  #358, #364, #368
- Cross-surface dry-run tests, batch manifests, scheduled-regen recipes,
  CLI/portal HTTP tests, HTML-to-PNG smoke, mocked provider polling,
  optional ffmpeg fixtures, local verification surfaces: #62, #65, #66,
  #161, #164, #209, #232, #239, #241
- js-yaml Dependabot alert: drop unused gray-matter, override js-yaml: #248
- GitHub-only delivery (traceability, intake, skills, docs): #347, #349,
  #350, #353
- Agent guide reset to the shared operating contract: #385
- Skill cleanup (drop stale rafiki.md, fold agentic-intake): #456
- Public-repo boundary, tool-only closeout, pull private program content
  out of the public tree: #227, #228, #229, #230, #244
- Doctor summary fix and remediation docs: #137, #341
- Frontend security-audit clear: #445
- minimatch override for the frontend audit gate: #394

### Docs, audits, and handoffs

- Public-release docs and model policy: #72
- Archive roadmap, product audit, cleanup state, Atlas/roadmap refreshes:
  #101, #115, #117, #149, #221
- Social-expansion viewer handoff, recipes, CDN publishing memo, alex-samuel
  boundary, llms.txt, week plan: #73, #223, #262, #269, #272, #278, #284
- ED + AI logo sprint, Vancouver AI Mission 30, RAP capstone YouTube
  handoff, Fellowship Reading Room: #165, #167, #168, #286, #403
- AgentOpus MCP lane: #342
- Generate wait semantics: #299
- 2026-09-03 main sweep and 2026-09-04 docs audit: #449, #463
- Issue-crush audit and Rafiki closeout records: #291, #295
- Retired model aliases `gpt1` / `dalle3` dropped from docs and code: #457

### Styles, prompt kits, and use cases

- RAP prompts, communities kit, dontsurveil.me, ED + AI logo kits, KK
  signature presets: #78, #92, #93, #133, #156, #245
- MAC / Vancouver AI assets, New God Flow, AEFL, Life Sciences bakeoff,
  God Skills, Comox Valley, Futureproof, ALLEY LEAGUE clubs, dark-crystal,
  kriskrug Aurora: #166, #177, #184, #185, #203, #204, #205, #243, #246,
  #247, #305, #415
- Keynote visual workflow swarm: #183
- Slingsby Advisors proposal visuals and GBF handoff: #444, #446
- Offline “Looks Right. Is It Right?” lesson: #465
- real-sky-poster skill and portable upscaler: #313, #352
- Presentation viewer social platform tabs: #77
- Prompt aspect ratio recorded in the run manifest: #179
- Public portal sharing hardened: #178

### Dependency updates

Dependabot and grouped bumps only. Titles are the GitHub PR titles.

Root / Actions / Python: #90, #365, #369, #370, #371, #372, #373, #375,
#376, #397, #398, #399, #400, #404, #405, #406, #408, #411, #431, #433,
#434, #440, #450, #451, #452, #455, #466, #474, #475, #477, #479, #481,
#482

Frontend npm: #366, #382, #395, #396, #402, #426, #427, #437, #439, #454,
#483

#426 lands #412/#409. #427 lands #413/#414. Those cited numbers are
issues or earlier PRs named in the titles, not extra merges after v1.1.0.

Notable upgrades in that set, from the PR titles: OpenAI Python SDK 2.x
then 3.x (#399, #452, #475, #481), Notion client 3.x (#400), commander 15
(#397), puppeteer 25.x (#398, #404, #431, #466, #479), google-genai
>=2.24.0 (#474), pillow >=12.3.0 (#434).

TODO for KK: whether any of these bumps should be called out as a
compatibility break in a future tagged release. The PR titles do not say.

### Since 28 August 2026

24 PRs in this window. Most are the dependency bumps above. The non-bump
ones are #449 (main sweep), #456 (skills cleanup), #457 (retired aliases),
#463 (docs audit), and #465 (offline lesson).

## 1.1.0 — 2026-05-03

Published GitHub release: [v1.1.0 — Content Pipeline Expansion](https://github.com/WalksWithASwagger/rafiki/releases/tag/v1.1.0).
Tag `v1.1.0` at `e72c3ef`. Text below is a tight restatement of that
release body, not new claims.

- Presentation viewer (`generate-presentation-viewer.py`), `--self-contained`,
  social-post export: #36, #47, #48
- Approved-image archive, safe clean, asset registry, scheduled regen:
  #41, #40, #38
- Canva export, Notion export, Vercel static deploy: #37, #45, #43
- Social-post expansion: #46
- Atomic usage-log writes, portal HTTP Basic auth + `--public`: #32, #39
- Tests for the new modules: #33 (release says 78 tests at ship)
- Upgrade visual-library prompts and four retrofitted READMEs: #34, #35

Follow-ups were tracked in #49. TODO for KK: whether #49 is still open
work or historical.

PRs that landed on 2026-05-03 before the release timestamp and are named
in that release: #32, #33, #34, #35, #36, #37, #38, #39, #40, #41, #43,
#45, #46, #47, #48. The release body also cites issues #17–#31 and #21;
those are issues, not PRs.

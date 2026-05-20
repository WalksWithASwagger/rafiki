# Rafiki E2E And Showpiece Roadmap Audit (2026-05-19)

## Scope

This pass stepped back from implementation work to test the current Rafiki
portal/library surface end to end and identify gaps that would keep the system
from feeling like a world-class creative operations showpiece.

Working tree used: `/Users/kk/.codex/worktrees/rafiki-library-archives`
and then implemented on `/Users/kk/.codex/worktrees/rafiki-portal-e2e`
on `codex/issue-118-portal-e2e-smoke`.

## E2E Results

Commands and checks run:

- `python3 generate.py library` on existing output: passed, but found `0/0`
  archive images because the local Communities assets in this worktree are not
  arranged as standard `run-*` outputs.
- `python3 generate.py --prompt-file examples/quickstart-image-prompts.md
  --output-dir output/e2e-showpiece-smoke --model gemini --style none
  --aspect-ratio square --dry-run --json`: passed and created a standard
  run manifest/viewer.
- Wrote two local fixture images into the smoke run so the archive could test
  real image loading without provider spend.
- `python3 generate.py library`: passed with `2/2 present` across one project.
- `npm run docs:check`: passed; 24 Markdown files checked.
- `npm run pack:check`: passed; dry-run package now includes the E2E smoke
  script and contains 82 files.
- `PATH=/Users/kk/Code/rafiki/.venv/bin:$PATH npm test`: passed;
  194 tests passed with one upstream Python 3.14 deprecation warning.
- `PATH=/Users/kk/Code/rafiki/.venv/bin:$PATH npm run doctor`: passed;
  0 critical issues and expected local provider-key warnings.
- `npm run e2e:portal`: added and passed; it creates a disposable fixture
  archive, starts the portal on a random local port, checks desktop/mobile
  browser behavior in Chromium, asserts screenshots are nonblank, and cleans
  up its temp output/server process.

Browser/API checks:

- Home page returned HTTP 200 and rendered `Rafiki Library`.
- `/api/usage` reported one project, one run, two images, model mix, recent run,
  and local spend data.
- `/api/deploy-readiness` returned a safe readiness report with Vercel detected
  and provider/auth checks marked optional.
- Desktop browser smoke found two cards, both images loaded at natural widths
  960px and 720px, no horizontal overflow, and a nonblank screenshot.
- Mobile browser smoke found no horizontal overflow at 390px width; both images
  lazy loaded correctly after scrolling to the cards.
- Search reduced visible cards from 2 to 1 for `review portal`.
- Run detail opened and showed the source run.
- Metadata save persisted to `output/archive-metadata.json`.
- Feedback save persisted to `output/feedback.json`.
- Rating plus starred filter worked when starting from a known unstarred state.
- Screenshot artifacts are captured in the temporary E2E root and checked for
  nonblank pixel stats. They are deleted by default and kept only when
  `RAFIKI_E2E_KEEP_TMP=1` is set.

## Product Findings

### What Works

- The local-first product spine is real: prompt file -> run manifest -> viewer
  -> library -> portal APIs -> metadata/feedback/rating state.
- The archive/library core is already more than a static gallery. It has
  review state, spend summary, deploy readiness, prompt studio, export actions,
  run detail, metadata, and feedback.
- The system is testable without provider spend by using dry runs plus local
  fixture images.
- The portal fits desktop without horizontal overflow and remains responsive on
  mobile.

### Gaps Exposed By E2E

- The repo had excellent unit/integration coverage but no committed browser E2E
  smoke for the portal. This pass added `npm run e2e:portal`; the remaining gap
  is expanding it with visual baselines and richer workflow assertions.
- The visible local library can contain run images while `registry-export`
  dry-run reports `count: 0`, because export scope is curated/registry-backed.
  That is defensible internally, but the UI should explain the mismatch.
- Mobile review content is buried below Prompt Studio, Curation & Export, and
  Spend & Review Ops. On the smoke page, the first card started around 3330px
  down the mobile page. That is usable, not showpiece-grade.
- Full-page mobile screenshots captured below-fold lazy images before they
  loaded. Human scrolling works, but visual regression needs either scroll
  probes or deterministic eager image loading for test mode.
- The portal previously requested `/favicon.ico` and received a 404. This pass
  now serves a quiet `204` so browser-console smoke stays clean.
- The UI uses small transitions and hover movement but has no explicit
  `prefers-reduced-motion` handling.

## Curriculum And Idea Coverage

Current coverage is strong in:

- RAP four-week Responsible AI visuals: foundations, ethics, societal impact,
  human element, capstone.
- BC + AI ecosystem diagrams and community/subgroup assets.
- HOPECODE maps for relationships, knowledge gardens, power maps, values,
  skill trees, and anti-corporate systems thinking.
- The Upgrade AI marketing, newsletter, podcast, and training imagery.
- AI Animation Accelerator certificate and motion-prompt material.
- Creative Mornings image and video concepts.

Coverage gaps to close:

- No canonical curriculum map across all programs. RAP, Upgrade AI, Hopecode,
  BC + AI, and Creative Mornings exist as prompt islands rather than a browsable
  curriculum atlas.
- No explicit learning-objective schema. Prompt files include concepts, but
  assets are not tagged with objectives, prerequisites, learner level, activity
  type, assessment type, or competency.
- No assessment/rubric layer. RAP has a capstone visual, but Rafiki does not
  expose rubrics, artifacts, critique prompts, or "proof of competence" views.
- No learner journey view. There is no map from novice -> practitioner ->
  facilitator -> community builder across your body of work.
- No "idea genealogy" or "concept dependency" interaction, despite many prompts
  already using tree, garden, network, and atlas metaphors.
- No facilitation mode. The portal is optimized for image review, not for
  teaching a cohort live, walking through a module, or turning images into a
  workshop sequence.
- No live critique/evaluation mode for image candidates. The feedback field is
  there, but there is no guided critique rubric for "on-brand", "teaches the
  concept", "ethically safe", "publish-ready", or "needs regeneration".

## External Research Signals

- UNESCO's AI competency work emphasizes human agency, AI ethics, AI techniques
  and applications, and AI system design for students, plus AI pedagogy and
  professional development for teachers.
- OECD's AI literacy framework consultation highlights two practical barriers:
  lack of shared understanding of AI literacy and uncertainty about how AI fits
  into subject areas.
- The U.S. Department of Labor's 2026 AI literacy framework centers practical
  workforce design: understand AI principles, explore uses, direct AI
  effectively, evaluate outputs, and use AI responsibly.
- MDN's View Transition API docs point toward smoother UI state transitions, but
  also warn about focus, reading-position, and live-region issues.
- web.dev's animation guidance still maps cleanly to this portal: prefer
  `transform` and `opacity`; avoid layout/paint-heavy motion.
- W3C WCAG guidance makes motion control non-negotiable for anything automatic
  or interaction-triggered and non-essential. Rafiki should treat reduced motion
  as part of the product quality bar.
- Playwright's visual comparison docs suggest a path to deterministic visual
  baselines once portal E2E is stable.

Sources:

- UNESCO AI competency frameworks: https://www.unesco.org/en/articles/what-you-need-know-about-unescos-new-ai-competency-frameworks-students-and-teachers
- OECD AILit Framework consultation: https://www.oecd.org/en/events/public-consultations/2025/09/ailit-framework.html
- U.S. Department of Labor AI Literacy Framework release: https://www.dol.gov/newsroom/releases/eta/eta20260213
- MDN View Transition API: https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API
- web.dev animation performance: https://web.dev/articles/animations-and-performance
- W3C Pause, Stop, Hide: https://www.w3.org/WAI/WCAG20/Understanding/pause-stop-hide
- W3C Animation from Interactions: https://www.w3.org/WAI/WCAG21/Understanding/animation-from-interactions.html
- Playwright visual comparisons: https://playwright.dev/docs/test-snapshots

## Showpiece Roadmap

### 1. Expand The E2E Harness

Baseline is now committed as `npm run e2e:portal`. Next improvements:

- Add visual baselines once the portal layout is less volatile.
- Add richer workflow assertions for export actions, prompt studio generation,
  and registry-backed bundles.
- Keep mobile scroll probes explicit so lazy image loading stays deterministic.

### 2. Reframe The Portal As Modes

Replace the one long stacked page with clear modes:

- Review: image grid first, filters, selected-card detail.
- Generate: Prompt Studio.
- Curate: approve, export, deploy, Notion/Canva.
- Spend: cost, provider imports, run history.
- Teach: curriculum atlas, module sequence, concept graph.

On mobile, default to Review first and collapse the other modes behind tabs.

### 3. Build The Curriculum Atlas

Create a first-class `curriculum.json` or `content_map.json` layer that maps
programs, modules, prompts, outputs, and competencies:

- program: RAP, Upgrade AI, HOPECODE, BC + AI, Creative Mornings
- module/week/session
- competency tags
- objective
- learner level
- concept prerequisites
- activity type
- assessment artifact
- visual assets
- recommended interactive view

Then add a portal view that lets someone browse the work as a learning world,
not only an image archive.

### 4. Add Signature Interactive Views

Best next candidates:

- Knowledge Garden: living map of concepts, prompts, modules, and generated
  images.
- Curriculum Tree: prerequisites, branches, capstones, and skill growth.
- Run Lineage: prompt -> model -> outputs -> feedback -> rerun -> approved
  asset.
- Concept Constellation: search result clusters across programs and styles.
- Before/After Studio: compare prompt revisions and visual outcomes.
- Cohort Mode: present a sequence of images as a workshop/story with facilitator
  notes and discussion prompts.

### 5. Define A Motion System

- Add `prefers-reduced-motion` CSS across viewers and portal.
- Keep animations to `transform` and `opacity` unless there is a measured
  reason to do otherwise.
- Add purposeful motion only where it teaches state: card approval, run
  lineage, export completion, concept graph focus, before/after transitions.
- Add a global "Reduce motion" toggle if any non-essential animation becomes
  persistent.

### 6. Make Evaluation A First-Class Workflow

- Add card-level criteria: brand fit, concept clarity, ethical safety,
  accessibility, publish readiness, regeneration priority.
- Add run-level summary: winners, unresolved decisions, blockers, total spend,
  next action.
- Add export-ready bundles that include selected images plus critique notes and
  curriculum context.

## Recommended Next Issues

1. `ux: split portal into Review/Generate/Curate/Spend/Teach modes`
2. `curriculum: add content map schema for programs, modules, competencies, and assets`
3. `showpiece: add Knowledge Garden prototype for concepts and generated images`
4. `motion: add reduced-motion support and transition guidelines`
5. `evals: add visual critique rubric and run-level decision summary`
6. `e2e: add visual baselines and richer workflow assertions to portal smoke`

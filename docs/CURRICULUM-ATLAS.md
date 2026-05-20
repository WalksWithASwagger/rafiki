# Curriculum Atlas

The Curriculum Atlas is Rafiki's local map from generated images to teaching
programs, modules, objectives, and competencies. It is intentionally a small
JSON scaffold, not a database or hosted service.

## Source Of Truth

Edit the atlas at:

```text
config/curriculum-atlas.json
```

The schema is:

| Field | Purpose |
|---|---|
| `version` | Atlas schema version. Currently `1`. |
| `programs[]` | Program-level teaching containers such as RAP, Upgrade AI, HOPECODE, and BC AI Ecosystem. |
| `programs[].project_patterns` | Project slug/text patterns that associate archive cards with the program. |
| `programs[].asset_query` | Additional program-level search terms. |
| `programs[].competencies` | Program-level competency labels. |
| `programs[].modules[]` | Module/session-level teaching units. |
| `modules[].objective` | Learning objective for that module. |
| `modules[].level` | Suggested learner level or sequence marker. |
| `modules[].competencies` | Module-specific competency labels. |
| `modules[].asset_query` | Terms used to link generated archive cards to the module. |
| `modules[].facilitator_notes` | Short teaching notes for how to use or critique the assets. |
| `modules[].discussion_prompts` | Learner-facing prompts for live review or cohort discussion. |
| `modules[].critique_criteria` | Evaluation rubric items with `id`, `label`, `prompt`, and optional `scale`. |
| `modules[].concept_links` | Lightweight concept relationships with `concept`, `relation`, and `target`. |

## Portal Behavior

`python generate.py library` and `python generate.py serve` render the atlas in
the portal's **Teach** mode. Rafiki matches archive cards against program and
module patterns, then exposes:

- linked asset counts per program and module
- an unmapped queue for cards that do not match the scaffold yet
- facilitator notes, discussion prompts, critique rubric items, and concept
  links for each module
- buttons that jump back to **Review** mode with the matching image cards
  filtered

The atlas is read-only in the portal. Keep authoring in the JSON file until the
schema has proved itself through real teaching/review sessions.

## Verification

Run:

```bash
npm run e2e:portal
```

The smoke checks mode navigation, Teach mode rendering, atlas filtering, Review
as the default mobile mode, and the existing image review workflow.

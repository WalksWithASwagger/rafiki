from __future__ import annotations

import json
from pathlib import Path

from lib import curriculum
from lib.renderers.library_atlas import _atlas_panel_html


def test_load_curriculum_atlas_normalizes_missing_file(tmp_path: Path):
    assert curriculum.load_curriculum_atlas(tmp_path / "missing.json") == {"version": 1, "programs": []}


def test_load_curriculum_atlas_keeps_program_dicts_only(tmp_path: Path):
    path = tmp_path / "atlas.json"
    path.write_text(
        json.dumps({"version": 2, "programs": [{"id": "rap"}, "nope"]}),
        encoding="utf-8",
    )

    assert curriculum.load_curriculum_atlas(path) == {"version": 2, "programs": [{"id": "rap"}]}


def test_build_curriculum_atlas_links_modules_and_unmapped_assets():
    config = {
        "version": 1,
        "programs": [{
            "id": "rap",
            "title": "RAP",
            "project_patterns": ["rap"],
            "modules": [{
                "id": "ethics",
                "title": "Ethics",
                "objective": "Evaluate bias and accountability.",
                "asset_query": ["bias"],
                "competencies": ["AI ethics"],
                "facilitator_notes": ["Ask where a human checkpoint belongs."],
                "discussion_prompts": ["Who is affected if the image is wrong?"],
                "critique_criteria": [{
                    "id": "clarity",
                    "label": "Concept clarity",
                    "prompt": "Does the image teach the idea without extra explanation?",
                    "scale": "1-5",
                }],
                "concept_links": [{
                    "concept": "Bias",
                    "relation": "depends_on",
                    "target": "Accountability",
                }],
            }],
        }],
    }
    records = [
        {
            "project": "rap-week-2",
            "title": "Bias Map",
            "prompt": "Map bias and accountability in AI systems.",
            "tags": ["ethics"],
        },
        {
            "project": "studio",
            "title": "Unmapped Card",
            "prompt": "General image review portal smoke.",
            "tags": [],
        },
    ]

    atlas = curriculum.build_curriculum_atlas(records, config)

    assert atlas["summary"] == {
        "programs": 1,
        "modules": 1,
        "linked_assets": 1,
        "unmapped_assets": 1,
    }
    module = atlas["programs"][0]["modules"][0]
    assert module["asset_indices"] == [0]
    assert module["facilitator_notes"] == ["Ask where a human checkpoint belongs."]
    assert module["discussion_prompts"] == ["Who is affected if the image is wrong?"]
    assert module["critique_criteria"] == [{
        "id": "clarity",
        "label": "Concept clarity",
        "prompt": "Does the image teach the idea without extra explanation?",
        "scale": "1-5",
    }]
    assert module["concept_links"] == [{
        "concept": "Bias",
        "relation": "depends_on",
        "target": "Accountability",
    }]
    assert atlas["programs"][0]["story_steps"] == [{
        "sequence": 1,
        "program_id": "rap",
        "module_id": "ethics",
        "title": "Ethics",
        "objective": "Evaluate bias and accountability.",
        "facilitator_notes": ["Ask where a human checkpoint belongs."],
        "discussion_prompts": ["Who is affected if the image is wrong?"],
        "asset_indices": [0],
        "asset_count": 1,
        "evaluation_summary": {
            "asset_count": 1,
            "evaluated_count": 0,
            "unreviewed_count": 1,
            "decision_counts": {
                "approve": 0,
                "revise": 0,
                "reject": 0,
                "reference": 0,
            },
            "average_score": None,
        },
        "review_action": {
            "type": "focusAtlasModule",
            "program_id": "rap",
            "module_id": "ethics",
            "enabled": True,
        },
    }]
    assert atlas["unmapped_asset_indices"] == [1]


def test_build_curriculum_atlas_normalizes_loose_teaching_fields():
    atlas = curriculum.build_curriculum_atlas([], {
        "programs": [{
            "id": "demo",
            "modules": [{
                "title": "Demo",
                "facilitator_notes": "First note, Second note",
                "discussion_prompts": ["What changed?", ""],
                "critique_criteria": [
                    {"label": "Ethical safety", "prompt": "Is harm surfaced?"},
                    {"prompt": "Is there a human checkpoint?"},
                    "skip me",
                ],
                "concept_links": [
                    {"concept": "Agency", "target": "Accountability"},
                    {"target": "Rubric"},
                    "skip me",
                ],
            }],
        }],
    })

    module = atlas["programs"][0]["modules"][0]
    assert module["facilitator_notes"] == ["First note", "Second note"]
    assert module["discussion_prompts"] == ["What changed?"]
    assert module["critique_criteria"][0]["id"] == "ethical-safety"
    assert module["critique_criteria"][1]["label"] == "Is there a human checkpoint?"
    assert module["concept_links"] == [
        {"concept": "Agency", "relation": "related", "target": "Accountability"},
        {"concept": "Rubric", "relation": "related", "target": "Rubric"},
    ]


def test_build_curriculum_atlas_summarizes_evaluations_by_module():
    config = {
        "programs": [{
            "id": "rap",
            "project_patterns": ["rap"],
            "modules": [{
                "id": "ethics",
                "title": "Ethics",
                "asset_query": ["bias"],
            }],
        }],
    }
    records = [
        {
            "project": "rap-week-2",
            "title": "Bias Map",
            "prompt": "Map bias and accountability.",
            "file": "rap-week-2/run-1/bias.png",
        },
        {
            "project": "rap-week-2",
            "title": "Bias Review",
            "prompt": "Bias review checkpoint.",
            "file": "rap-week-2/run-1/checkpoint.png",
        },
    ]
    evaluations = {
        "items": {
            "rap-week-2/run-1/bias.png": {"decision": "approve", "score": 5},
            "rap-week-2/run-1/checkpoint.png": {"decision": "revise", "score": 3},
        }
    }

    atlas = curriculum.build_curriculum_atlas(records, config, evaluations=evaluations)

    summary = atlas["programs"][0]["modules"][0]["evaluation_summary"]
    assert summary["asset_count"] == 2
    assert summary["evaluated_count"] == 2
    assert summary["unreviewed_count"] == 0
    assert summary["decision_counts"] == {
        "approve": 1,
        "revise": 1,
        "reject": 0,
        "reference": 0,
    }
    assert summary["average_score"] == 4.0


def test_build_curriculum_atlas_derives_empty_story_steps_gracefully():
    config = {
        "programs": [
            {
                "id": "empty",
                "modules": [],
            },
            {
                "id": "rap",
                "project_patterns": ["rap"],
                "modules": [{
                    "id": "draft",
                    "title": "Draft Review",
                    "objective": "Review the first cohort draft.",
                    "asset_query": ["draft"],
                    "facilitator_notes": ["Invite one improvement before critique."],
                    "discussion_prompts": ["What would make this usable in class?"],
                }],
            },
        ],
    }
    records = [{
        "project": "studio",
        "title": "Unmapped Card",
        "prompt": "No matching curriculum terms.",
    }]

    atlas = curriculum.build_curriculum_atlas(records, config)

    empty_program = atlas["programs"][0]
    assert empty_program["story_steps"] == []

    step = atlas["programs"][1]["story_steps"][0]
    assert step["sequence"] == 1
    assert step["module_id"] == "draft"
    assert step["asset_indices"] == []
    assert step["asset_count"] == 0
    assert step["evaluation_summary"]["asset_count"] == 0
    assert step["review_action"] == {
        "type": "focusAtlasModule",
        "program_id": "rap",
        "module_id": "draft",
        "enabled": False,
    }
    assert atlas["unmapped_asset_indices"] == [0]


def test_atlas_panel_renders_story_mode_review_actions():
    atlas = {
        "summary": {
            "programs": 1,
            "modules": 2,
            "linked_assets": 1,
            "unmapped_assets": 0,
        },
        "programs": [{
            "id": "rap",
            "title": "RAP",
            "summary": "Responsible AI cohort path.",
            "competencies": [],
            "asset_count": 1,
            "modules": [],
            "story_steps": [
                {
                    "sequence": 1,
                    "program_id": "rap",
                    "module_id": "intro",
                    "title": "Shared Language",
                    "objective": "Build a common language for critique.",
                    "facilitator_notes": ["Invite a quick visual read."],
                    "discussion_prompts": ["What does the image make easier to explain?"],
                    "asset_indices": [0],
                    "asset_count": 1,
                    "evaluation_summary": {"evaluated_count": 0, "average_score": None},
                },
                {
                    "sequence": 2,
                    "program_id": "rap",
                    "module_id": "empty",
                    "title": "Empty Module",
                    "objective": "Hold the place gracefully.",
                    "asset_indices": [],
                    "asset_count": 0,
                    "evaluation_summary": {"evaluated_count": 0, "average_score": None},
                },
            ],
        }],
        "unmapped_asset_indices": [],
    }

    html = _atlas_panel_html(atlas)

    assert "Cohort Story Mode" in html
    assert "Step 1" in html
    assert "Shared Language" in html
    assert "Build a common language for critique." in html
    assert "Invite a quick visual read." in html
    assert "What does the image make easier to explain?" in html
    assert "1 asset · 0/1 evaluated" in html
    assert 'focusAtlasModule("rap", "intro")' in html
    assert 'focusAtlasModule("rap", "empty")\' disabled' in html
    assert "Matching asset indices" not in html

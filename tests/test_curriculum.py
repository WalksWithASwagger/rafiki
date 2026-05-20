from __future__ import annotations

import json
from pathlib import Path

from lib import curriculum


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

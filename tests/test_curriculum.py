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
    assert atlas["programs"][0]["modules"][0]["asset_indices"] == [0]
    assert atlas["unmapped_asset_indices"] == [1]

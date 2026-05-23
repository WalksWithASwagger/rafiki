from __future__ import annotations

import json
from pathlib import Path

import pytest

from lib.evaluations import load_evaluations, update_evaluation


def test_update_evaluation_persists_decision_score_and_notes(tmp_path: Path):
    path = tmp_path / "evaluations.json"

    result = update_evaluation(
        path,
        {
            "key": "demo/run-1/hero.png",
            "decision": "approve",
            "score": "5",
            "use_case": "homepage hero",
            "rationale": "Strong composition and on-brand energy.",
            "next_step": "Export to Canva bundle.",
        },
    )

    assert result["ok"] is True
    saved = load_evaluations(path)
    entry = saved["items"]["demo/run-1/hero.png"]
    assert entry["decision"] == "approve"
    assert entry["score"] == 5
    assert entry["use_case"] == "homepage hero"
    assert entry["rationale"] == "Strong composition and on-brand energy."
    assert entry["next_step"] == "Export to Canva bundle."
    assert entry["updated_at"]


def test_update_evaluation_removes_empty_entry(tmp_path: Path):
    path = tmp_path / "evaluations.json"
    path.write_text(
        json.dumps({"version": 1, "items": {"demo/run-1/hero.png": {"decision": "revise"}}}),
        encoding="utf-8",
    )

    result = update_evaluation(path, {"key": "demo/run-1/hero.png"})

    assert result == {"ok": True, "key": "demo/run-1/hero.png", "evaluation": None}
    assert load_evaluations(path)["items"] == {}


def test_update_evaluation_validates_decision_and_score(tmp_path: Path):
    path = tmp_path / "evaluations.json"

    with pytest.raises(ValueError, match="decision must be one of"):
        update_evaluation(path, {"key": "demo/run-1/hero.png", "decision": "ship-it"})

    with pytest.raises(ValueError, match="score must be an integer from 1 to 5"):
        update_evaluation(path, {"key": "demo/run-1/hero.png", "score": 9})

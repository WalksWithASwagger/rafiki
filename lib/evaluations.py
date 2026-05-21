"""Local card evaluation state for Rafiki archive review."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

EVALUATION_FILENAME = "evaluations.json"
EVALUATION_DECISIONS = {"", "approve", "revise", "reject", "reference"}


def evaluations_path(output_root: Path) -> Path:
    return Path(output_root) / EVALUATION_FILENAME


def _default_evaluations() -> dict[str, Any]:
    return {"version": 1, "items": {}}


def load_evaluations(path: Path) -> dict[str, Any]:
    if not path.exists():
        return _default_evaluations()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return _default_evaluations()
    if not isinstance(data, dict):
        return _default_evaluations()
    items = data.get("items")
    if not isinstance(items, dict):
        data["items"] = {}
    data.setdefault("version", 1)
    return data


def save_evaluations(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".evaluations.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _clean_text(value: object, field: str, *, max_len: int = 1000) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    return value.strip()[:max_len]


def _clean_score(value: object) -> int | None:
    if value in (None, ""):
        return None
    try:
        score = int(value)
    except (TypeError, ValueError) as e:
        raise ValueError("score must be an integer from 1 to 5") from e
    if score < 1 or score > 5:
        raise ValueError("score must be an integer from 1 to 5")
    return score


def update_evaluation(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("request body must be a JSON object")

    key = _clean_text(payload.get("key"), "key", max_len=1000)
    if not key:
        raise ValueError("key is required")

    decision = _clean_text(payload.get("decision"), "decision", max_len=40).lower()
    if decision not in EVALUATION_DECISIONS:
        allowed = ", ".join(sorted(s for s in EVALUATION_DECISIONS if s))
        raise ValueError(f"decision must be one of: {allowed}")

    score = _clean_score(payload.get("score"))
    use_case = _clean_text(payload.get("use_case"), "use_case", max_len=240)
    rationale = _clean_text(payload.get("rationale"), "rationale", max_len=1200)
    next_step = _clean_text(payload.get("next_step"), "next_step", max_len=1200)

    entry: dict[str, Any] = {}
    if decision:
        entry["decision"] = decision
    if score is not None:
        entry["score"] = score
    if use_case:
        entry["use_case"] = use_case
    if rationale:
        entry["rationale"] = rationale
    if next_step:
        entry["next_step"] = next_step

    data = load_evaluations(path)
    items = data.setdefault("items", {})
    if entry:
        entry["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        items[key] = entry
    else:
        items.pop(key, None)
    data["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    save_evaluations(path, data)
    return {"ok": True, "key": key, "evaluation": items.get(key)}

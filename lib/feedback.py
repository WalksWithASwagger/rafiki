"""Local feedback state for Rafiki archive review."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

FEEDBACK_STATUSES = {"", "needs-change", "keep", "maybe", "blocked", "done"}


def _default_feedback() -> dict[str, Any]:
    return {"version": 1, "items": {}}


def load_feedback(path: Path) -> dict[str, Any]:
    if not path.exists():
        return _default_feedback()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return _default_feedback()
    if not isinstance(data, dict):
        return _default_feedback()
    items = data.get("items")
    if not isinstance(items, dict):
        data["items"] = {}
    data.setdefault("version", 1)
    return data


def save_feedback(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        prefix=".feedback.", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _clean_text(value: object, field: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    return value.strip()


def update_feedback(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("request body must be a JSON object")

    key = _clean_text(payload.get("key"), "key")
    if not key:
        raise ValueError("key is required")

    status = _clean_text(payload.get("status"), "status")
    if status not in FEEDBACK_STATUSES:
        allowed = ", ".join(sorted(s for s in FEEDBACK_STATUSES if s))
        raise ValueError(f"status must be one of: {allowed}")

    entry = {
        "note": _clean_text(payload.get("note"), "note"),
        "change_request": _clean_text(payload.get("change_request"), "change_request"),
        "status": status,
    }
    entry = {k: v for k, v in entry.items() if v}

    data = load_feedback(path)
    items = data.setdefault("items", {})
    if entry:
        entry["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        items[key] = entry
    else:
        items.pop(key, None)
    data["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    save_feedback(path, data)
    return {"ok": True, "key": key, "feedback": items.get(key)}

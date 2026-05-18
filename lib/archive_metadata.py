"""Local archive-card metadata for Rafiki review."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

METADATA_FILENAME = "archive-metadata.json"
ARCHIVE_STATES = {"canva", "notion", "deployed", "published", "superseded"}


def archive_metadata_path(output_root: Path) -> Path:
    return Path(output_root) / METADATA_FILENAME


def _default_metadata() -> dict[str, Any]:
    return {"version": 1, "items": {}}


def load_archive_metadata(path: Path) -> dict[str, Any]:
    if not path.exists():
        return _default_metadata()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return _default_metadata()
    if not isinstance(data, dict):
        return _default_metadata()
    items = data.get("items")
    if not isinstance(items, dict):
        data["items"] = {}
    data.setdefault("version", 1)
    return data


def save_archive_metadata(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".archive-metadata.", suffix=".tmp", dir=str(path.parent))
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


def _clean_text(value: object, field: str, *, max_len: int = 500) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    return value.strip()[:max_len]


def _clean_list(value: object, field: str, *, allowed: set[str] | None = None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        raw_values = value.split(",")
    elif isinstance(value, list):
        raw_values = value
    else:
        raise ValueError(f"{field} must be a list or comma-separated string")

    out: list[str] = []
    seen: set[str] = set()
    for raw in raw_values:
        if not isinstance(raw, str):
            raise ValueError(f"{field} values must be strings")
        item = raw.strip()
        if not item:
            continue
        if allowed is not None:
            item = item.lower()
            if item not in allowed:
                allowed_values = ", ".join(sorted(allowed))
                raise ValueError(f"{field} must contain only: {allowed_values}")
        if item in seen:
            continue
        seen.add(item)
        out.append(item[:80])
    return out[:32]


def metadata_for_key(data: dict[str, Any], key: str) -> dict[str, Any]:
    item = data.get("items", {}).get(key, {})
    return item if isinstance(item, dict) else {}


def update_archive_metadata(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("request body must be a JSON object")

    key = _clean_text(payload.get("key"), "key", max_len=1000)
    if not key:
        raise ValueError("key is required")

    title = _clean_text(payload.get("title"), "title")
    tags = _clean_list(payload.get("tags"), "tags")
    states = _clean_list(payload.get("states"), "states", allowed=ARCHIVE_STATES)
    superseded_by = _clean_text(payload.get("superseded_by"), "superseded_by", max_len=1000)

    entry: dict[str, Any] = {}
    if title:
        entry["title"] = title
    if tags:
        entry["tags"] = tags
    if states:
        entry["states"] = states
    if superseded_by:
        entry["superseded_by"] = superseded_by

    data = load_archive_metadata(path)
    items = data.setdefault("items", {})
    if entry:
        entry["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        items[key] = entry
    else:
        items.pop(key, None)
    data["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    save_archive_metadata(path, data)
    return {"ok": True, "key": key, "metadata": items.get(key)}

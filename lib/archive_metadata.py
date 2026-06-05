"""Local archive-card metadata for Rafiki review."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

METADATA_FILENAME = "archive-metadata.json"
ARCHIVE_STATES = {"canva", "notion", "deployed", "published", "superseded"}
ARTIFACT_REVIEW_STATES = {"approved", "rejected", "regenerate", "manual-rebuild"}
METADATA_EDIT_FIELDS = {
    "title",
    "tags",
    "states",
    "superseded_by",
    "source_use_case",
    "source_url",
    "prompt_pack",
    "prompt_pack_section",
    "artifact_review_state",
    "export_targets",
    "downstream_uses",
}


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


def _clean_public_url(value: object, field: str) -> str:
    url = _clean_text(value, field, max_len=1000)
    if not url:
        return ""
    if url.startswith(("http://", "https://")):
        return url
    raise ValueError(f"{field} must be a public http(s) URL")


def _clean_repo_reference(value: object, field: str) -> str:
    ref = _clean_text(value, field, max_len=500)
    if not ref:
        return ""
    if ref.startswith("/") or ref.startswith("file://") or "/Users/" in ref:
        raise ValueError(f"{field} must be a repo-relative path or stable label")
    return ref


def _clean_enum(value: object, field: str, allowed: set[str]) -> str:
    item = _clean_text(value, field, max_len=80).lower()
    if not item:
        return ""
    if item not in allowed:
        allowed_values = ", ".join(sorted(allowed))
        raise ValueError(f"{field} must be one of: {allowed_values}")
    return item


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

    data = load_archive_metadata(path)
    items = data.setdefault("items", {})
    if not any(field in payload for field in METADATA_EDIT_FIELDS):
        items.pop(key, None)
        data["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        save_archive_metadata(path, data)
        return {"ok": True, "key": key, "metadata": None}

    current = items.get(key)
    entry: dict[str, Any] = dict(current) if isinstance(current, dict) else {}

    field_values: dict[str, object] = {}
    if "title" in payload:
        field_values["title"] = _clean_text(payload.get("title"), "title")
    if "tags" in payload:
        field_values["tags"] = _clean_list(payload.get("tags"), "tags")
    if "states" in payload:
        field_values["states"] = _clean_list(payload.get("states"), "states", allowed=ARCHIVE_STATES)
    if "superseded_by" in payload:
        field_values["superseded_by"] = _clean_text(payload.get("superseded_by"), "superseded_by", max_len=1000)
    if "source_use_case" in payload:
        field_values["source_use_case"] = _clean_text(payload.get("source_use_case"), "source_use_case", max_len=200)
    if "source_url" in payload:
        field_values["source_url"] = _clean_public_url(payload.get("source_url"), "source_url")
    if "prompt_pack" in payload:
        field_values["prompt_pack"] = _clean_repo_reference(payload.get("prompt_pack"), "prompt_pack")
    if "prompt_pack_section" in payload:
        field_values["prompt_pack_section"] = _clean_text(payload.get("prompt_pack_section"), "prompt_pack_section")
    if "artifact_review_state" in payload:
        field_values["artifact_review_state"] = _clean_enum(
            payload.get("artifact_review_state"),
            "artifact_review_state",
            ARTIFACT_REVIEW_STATES,
        )
    if "export_targets" in payload:
        field_values["export_targets"] = _clean_list(payload.get("export_targets"), "export_targets")
    if "downstream_uses" in payload:
        field_values["downstream_uses"] = _clean_list(payload.get("downstream_uses"), "downstream_uses")

    for field, value in field_values.items():
        if value:
            entry[field] = value
        else:
            entry.pop(field, None)

    if entry:
        entry["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        items[key] = entry
    else:
        items.pop(key, None)
    data["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    save_archive_metadata(path, data)
    return {"ok": True, "key": key, "metadata": items.get(key)}


def stamp_archive_state(path: Path, keys: Iterable[str], state: str) -> dict[str, Any]:
    """Append an archive state to existing card metadata without erasing fields."""
    clean_state = _clean_list([state], "state", allowed=ARCHIVE_STATES)
    if not clean_state:
        raise ValueError("state is required")
    state = clean_state[0]

    data = load_archive_metadata(path)
    items = data.setdefault("items", {})
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    stamped_keys: list[str] = []

    for raw_key in keys:
        key = _clean_text(raw_key, "key", max_len=1000)
        if not key:
            continue
        entry = items.get(key)
        if not isinstance(entry, dict):
            entry = {}
        states = _clean_list(entry.get("states"), "states", allowed=ARCHIVE_STATES)
        if state not in states:
            states.append(state)
        entry["states"] = states
        entry["updated_at"] = now
        items[key] = entry
        stamped_keys.append(key)

    if stamped_keys:
        data["updated_at"] = now
        save_archive_metadata(path, data)

    return {
        "ok": True,
        "state": state,
        "stamped": len(stamped_keys),
        "keys": stamped_keys,
    }

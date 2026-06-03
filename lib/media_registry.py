"""Multimedia registry for local image, video, audio, style, and training assets."""

from __future__ import annotations

import csv
import json
import os
from dataclasses import MISSING
from datetime import datetime
from pathlib import Path
from typing import Any

from lib.importers import alex_samuel
from lib.media_roots import MediaRoot, load_media_roots
from lib.media_types import MediaEntry, MediaImportResult, StyleProfile, SubjectProfile, VideoEdit

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
MEDIA_REGISTRY_JSON = DATA_DIR / "media-registry.json"
MEDIA_REGISTRY_CSV = DATA_DIR / "media-registry.csv"

CSV_COLUMNS = [
    "id",
    "kind",
    "collection",
    "root_key",
    "subject",
    "project",
    "title",
    "provider",
    "model",
    "style",
    "source_manifest",
    "source_url",
    "tags",
    "indexed_at",
    "path",
]


def import_media_root(root: MediaRoot, *, indexed_at: str | None = None) -> MediaImportResult:
    if root.importer == "alex-samuel":
        return alex_samuel.import_root(root.path, root_key=root.key, indexed_at=indexed_at)
    return _generic_import(root, indexed_at=indexed_at)


def index(
    *,
    roots: dict[str, MediaRoot] | None = None,
    registry_path: Path | None = None,
    write: bool = True,
) -> dict[str, Any]:
    roots = roots if roots is not None else load_media_roots()
    registry_path = registry_path or MEDIA_REGISTRY_JSON
    indexed_at = datetime.now().astimezone().isoformat(timespec="seconds")
    results = [import_media_root(root, indexed_at=indexed_at) for root in roots.values()]

    payload = {
        "version": 1,
        "indexed_at": indexed_at,
        "roots": [root.to_dict() for root in roots.values()],
        "entries": [entry.to_dict() for result in results for entry in result.entries],
        "subjects": [subject.to_dict() for result in results for subject in result.subjects],
        "styles": [style.to_dict() for result in results for style in result.styles],
        "video_edits": [edit.to_dict() for result in results for edit in result.video_edits],
        "warnings": [warning for result in results for warning in result.warnings],
    }
    payload["summary"] = _summary(payload)
    if write:
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def load_registry(path: Path | None = None, *, rebuild_if_missing: bool = True) -> dict[str, Any]:
    path = path or MEDIA_REGISTRY_JSON
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    if rebuild_if_missing:
        return index(registry_path=path)
    return {"version": 1, "entries": [], "subjects": [], "styles": [], "video_edits": [], "summary": {}}


def search(query: str = "", *, kind: str = "", collection: str = "", registry_path: Path | None = None) -> list[MediaEntry]:
    data = load_registry(registry_path)
    q = query.strip().lower()
    entries = [_entry_from_dict(item) for item in data.get("entries", []) if isinstance(item, dict)]
    results = []
    for entry in entries:
        if kind and entry.kind != kind:
            continue
        if collection and entry.collection != collection:
            continue
        haystack = " ".join([
            entry.title,
            entry.subject,
            entry.project,
            entry.kind,
            entry.collection,
            entry.prompt,
            entry.style,
            entry.model,
            " ".join(entry.tags),
            entry.relative_path,
        ]).lower()
        if not q or q in haystack:
            results.append(entry)
    return results


def export(format: str = "csv", *, registry_path: Path | None = None, output_path: Path | None = None) -> Path:
    data = load_registry(registry_path)
    if format not in {"csv", "json"}:
        raise ValueError("format must be csv or json")
    if output_path is None:
        output_path = MEDIA_REGISTRY_JSON if format == "json" else MEDIA_REGISTRY_CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if format == "json":
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return output_path

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for item in data.get("entries", []):
            row = {key: item.get(key, "") for key in CSV_COLUMNS}
            row["tags"] = ",".join(item.get("tags") or [])
            writer.writerow(row)
    return output_path


def subjects(registry_path: Path | None = None) -> list[SubjectProfile]:
    data = load_registry(registry_path)
    return [_subject_from_dict(item) for item in data.get("subjects", []) if isinstance(item, dict)]


def styles(registry_path: Path | None = None) -> list[StyleProfile]:
    data = load_registry(registry_path)
    return [_style_from_dict(item) for item in data.get("styles", []) if isinstance(item, dict)]


def video_edits(registry_path: Path | None = None) -> list[VideoEdit]:
    data = load_registry(registry_path)
    return [_video_edit_from_dict(item) for item in data.get("video_edits", []) if isinstance(item, dict)]


def _summary(payload: dict[str, Any]) -> dict[str, Any]:
    entries = payload.get("entries") or []
    by_kind: dict[str, int] = {}
    by_collection: dict[str, int] = {}
    for entry in entries:
        by_kind[entry.get("kind", "")] = by_kind.get(entry.get("kind", ""), 0) + 1
        by_collection[entry.get("collection", "")] = by_collection.get(entry.get("collection", ""), 0) + 1
    return {
        "entries": len(entries),
        "subjects": len(payload.get("subjects") or []),
        "styles": len(payload.get("styles") or []),
        "video_edits": len(payload.get("video_edits") or []),
        "by_kind": by_kind,
        "by_collection": by_collection,
    }


def _entry_from_dict(item: dict[str, Any]) -> MediaEntry:
    return MediaEntry(**_dataclass_kwargs(MediaEntry, item))


def _subject_from_dict(item: dict[str, Any]) -> SubjectProfile:
    return SubjectProfile(**_dataclass_kwargs(SubjectProfile, item))


def _style_from_dict(item: dict[str, Any]) -> StyleProfile:
    return StyleProfile(**_dataclass_kwargs(StyleProfile, item))


def _video_edit_from_dict(item: dict[str, Any]) -> VideoEdit:
    return VideoEdit(**_dataclass_kwargs(VideoEdit, item))


def _dataclass_kwargs(cls, item: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, field in cls.__dataclass_fields__.items():
        if key in item:
            out[key] = item[key]
        elif field.default_factory is not MISSING:
            out[key] = field.default_factory()
        elif field.default is not MISSING:
            out[key] = field.default
    return out


def _generic_import(root: MediaRoot, *, indexed_at: str | None = None) -> MediaImportResult:
    indexed_at = indexed_at or datetime.now().astimezone().isoformat(timespec="seconds")
    result = MediaImportResult(root_key=root.key, root_path=str(root.path), importer=root.importer)
    if not root.path.exists():
        result.warnings.append(f"root not found: {root.path}")
        return result
    for dirpath, dirnames, filenames in os.walk(root.path):
        dirnames[:] = [name for name in dirnames if name not in {".git", "venv", "venv311", ".venv", "__pycache__", "node_modules"}]
        paths = [Path(dirpath) / filename for filename in filenames if filename != ".env"]
        for path in sorted(p for p in paths if p.is_file()):
            suffix = path.suffix.lower()
            kind = ""
            if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
                kind = "image"
            elif suffix in {".mp4", ".mov", ".m4v", ".webm"}:
                kind = "video"
            elif suffix in {".mp3", ".wav", ".m4a", ".aac", ".flac"}:
                kind = "audio"
            if not kind:
                continue
            relative = path.resolve().relative_to(root.path.resolve()).as_posix()
            result.entries.append(MediaEntry(
                id=f"{root.key}-{kind}-{relative.replace('/', '-')}",
                kind=kind,
                collection=kind,
                root_key=root.key,
                path=str(path.resolve(strict=False)),
                relative_path=relative,
                title=path.stem.replace("-", " ").replace("_", " ").title(),
                indexed_at=indexed_at,
                metadata={"size_bytes": path.stat().st_size},
            ))
    return result

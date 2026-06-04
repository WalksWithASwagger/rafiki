"""Multimedia registry for local image, video, audio, style, and training assets."""

from __future__ import annotations

import csv
import json
import os
from dataclasses import MISSING
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from lib.importers import alex_samuel
from lib.media_roots import MediaRoot, load_media_roots
from lib.media_types import MediaEntry, MediaImportResult, StyleProfile, SubjectProfile, VideoEdit

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
MEDIA_REGISTRY_JSON = DATA_DIR / "media-registry.json"
MEDIA_REGISTRY_CSV = DATA_DIR / "media-registry.csv"

REVIEWABLE_KINDS = {"image", "video", "audio", "prediction", "style"}
KIND_PRIORITY = {
    "image": 0,
    "video": 1,
    "audio": 2,
    "prediction": 3,
    "style": 4,
    "prompt-suite": 5,
    "evaluation": 6,
    "video-edit": 7,
    "storyboard": 8,
    "scene-manifest": 9,
    "shot-list": 10,
    "model-version": 11,
    "training-manifest": 12,
    "dataset": 13,
}
COLLECTION_PRIORITY = {
    "predictions": 0,
    "video": 1,
    "delivery": 2,
    "photos": 3,
    "styles": 4,
    "prompts": 5,
    "evaluations": 6,
    "albums": 7,
    "training": 8,
}
ROOT_FINGERPRINT_SENTINELS = (
    "clients",
    "evals",
    "video_project",
    "festival_submission",
    "prompts",
    "training",
    "training_v3",
    "training_v4_captioned",
)

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
    incremental: bool = False,
) -> dict[str, Any]:
    roots = roots if roots is not None else load_media_roots()
    registry_path = registry_path or MEDIA_REGISTRY_JSON
    indexed_at = datetime.now().astimezone().isoformat(timespec="seconds")
    previous = load_registry(registry_path, rebuild_if_missing=False) if incremental and registry_path.exists() else {}
    previous_fingerprints = previous.get("root_fingerprints") if isinstance(previous, dict) else {}
    if not isinstance(previous_fingerprints, dict):
        previous_fingerprints = {}

    entries: list[dict[str, Any]] = []
    subjects_payload: list[dict[str, Any]] = []
    styles_payload: list[dict[str, Any]] = []
    video_edits_payload: list[dict[str, Any]] = []
    warnings: list[str] = []
    root_fingerprints: dict[str, Any] = {}
    reused_roots: list[str] = []
    imported_roots: list[str] = []

    for root in roots.values():
        fingerprint = root_fingerprint(root)
        root_fingerprints[root.key] = fingerprint
        if incremental and fingerprint == previous_fingerprints.get(root.key):
            entries.extend(_items_for_root(previous, "entries", root.key))
            subjects_payload.extend(_items_for_root(previous, "subjects", root.key))
            styles_payload.extend(_items_for_root(previous, "styles", root.key))
            video_edits_payload.extend(_items_for_root(previous, "video_edits", root.key))
            reused_roots.append(root.key)
            continue

        result = import_media_root(root, indexed_at=indexed_at)
        entries.extend(entry.to_dict() for entry in result.entries)
        subjects_payload.extend(subject.to_dict() for subject in result.subjects)
        styles_payload.extend(style.to_dict() for style in result.styles)
        video_edits_payload.extend(edit.to_dict() for edit in result.video_edits)
        warnings.extend(result.warnings)
        imported_roots.append(root.key)

    payload = {
        "version": 1,
        "indexed_at": indexed_at,
        "roots": [root.to_dict() for root in roots.values()],
        "root_fingerprints": root_fingerprints,
        "entries": sort_entry_dicts(entries),
        "subjects": subjects_payload,
        "styles": styles_payload,
        "video_edits": video_edits_payload,
        "warnings": warnings,
        "indexing": {
            "incremental": incremental,
            "reused_roots": reused_roots,
            "imported_roots": imported_roots,
        },
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
    return [_entry_from_dict(item) for item in filter_entry_dicts(data, query=query, kind=kind, collection=collection)]


def filter_entry_dicts(
    data: dict[str, Any],
    *,
    query: str = "",
    kind: str = "",
    collection: str = "",
    subject: str = "",
    project: str = "",
    view: str = "",
) -> list[dict[str, Any]]:
    q = query.strip().lower()
    review_default = view == "review" and not (q or kind or collection)
    results = []
    for entry in data.get("entries", []):
        if not isinstance(entry, dict):
            continue
        if review_default and entry.get("kind") not in REVIEWABLE_KINDS:
            continue
        if kind and entry.get("kind") != kind:
            continue
        if collection and entry.get("collection") != collection:
            continue
        if subject and entry.get("subject") != subject:
            continue
        if project and entry.get("project") != project:
            continue
        haystack = " ".join([
            str(entry.get("title", "")),
            str(entry.get("subject", "")),
            str(entry.get("project", "")),
            str(entry.get("kind", "")),
            str(entry.get("collection", "")),
            str(entry.get("prompt", "")),
            str(entry.get("style", "")),
            str(entry.get("model", "")),
            " ".join(str(tag) for tag in (entry.get("tags") or [])),
            str(entry.get("relative_path", "")),
        ]).lower()
        if not q or q in haystack:
            results.append(entry)
    return sort_entry_dicts(results)


def sort_entry_dicts(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(entries, key=_entry_sort_key)


def root_fingerprint(root: MediaRoot) -> dict[str, Any]:
    path = root.path.expanduser().resolve(strict=False)
    markers = []
    for marker_path in [path, *(path / name for name in ROOT_FINGERPRINT_SENTINELS)]:
        if not marker_path.exists():
            continue
        try:
            stat = marker_path.stat()
        except OSError:
            continue
        try:
            relative = marker_path.relative_to(path).as_posix()
        except ValueError:
            relative = marker_path.as_posix()
        markers.append({
            "path": relative or ".",
            "mtime_ns": stat.st_mtime_ns,
            "size": stat.st_size,
        })
    return {
        "key": root.key,
        "path": str(path),
        "importer": root.importer,
        "enabled": root.enabled,
        "exists": path.exists(),
        "markers": markers,
    }


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


def subject_profiles(registry_path: Path | None = None, *, output_limit: int = 6) -> list[dict[str, Any]]:
    data = load_registry(registry_path)
    entries = [item for item in data.get("entries", []) if isinstance(item, dict)]
    return [
        _subject_profile_payload(item, entries, output_limit=output_limit)
        for item in data.get("subjects", [])
        if isinstance(item, dict)
    ]


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
        "reviewable_entries": sum(1 for entry in entries if entry.get("kind", "") in REVIEWABLE_KINDS),
        "subjects": len(payload.get("subjects") or []),
        "styles": len(payload.get("styles") or []),
        "video_edits": len(payload.get("video_edits") or []),
        "by_kind": by_kind,
        "by_collection": by_collection,
        "reused_roots": (payload.get("indexing") or {}).get("reused_roots", []),
        "imported_roots": (payload.get("indexing") or {}).get("imported_roots", []),
    }


def _items_for_root(data: dict[str, Any], key: str, root_key: str) -> list[dict[str, Any]]:
    return [item for item in data.get(key, []) if isinstance(item, dict) and item.get("root_key") == root_key]


def _subject_profile_payload(
    subject: dict[str, Any],
    entries: list[dict[str, Any]],
    *,
    output_limit: int,
) -> dict[str, Any]:
    key = str(subject.get("key") or "")
    subject_entries = [entry for entry in entries if str(entry.get("subject") or "") == key]
    output_entries = [entry for entry in subject_entries if _is_representative_subject_output(entry)]
    video_entries = [entry for entry in subject_entries if entry.get("kind") == "video"]
    projects = sorted({str(entry.get("project") or "") for entry in subject_entries if entry.get("project")})
    video_projects = sorted({str(entry.get("project") or "") for entry in video_entries if entry.get("project")})

    payload = dict(subject)
    payload.setdefault("trigger_word", "")
    payload.setdefault("prompt_suites", [])
    payload.setdefault("album_roots", [])
    payload.setdefault("training_roots", [])
    payload.setdefault("model_versions", [])
    payload.setdefault("metadata", {})
    payload["entry_count"] = len(subject_entries)
    payload["output_count"] = len(output_entries)
    payload["video_count"] = len(video_entries)
    payload["projects"] = projects
    payload["representative_outputs"] = [
        _subject_entry_summary(entry)
        for entry in sort_entry_dicts(output_entries)[:output_limit]
    ]
    payload["quick_links"] = {
        "library": _suite_href(tab="library", view="all", subject=key),
        "video_subject": _suite_href(tab="video", videoSubject=key) if video_entries else "",
        "video_projects": [
            {"project": project, "href": _suite_href(tab="video", videoProject=project)}
            for project in video_projects
        ],
    }
    return payload


def _is_representative_subject_output(entry: dict[str, Any]) -> bool:
    return str(entry.get("kind") or "") in {"image", "video", "audio", "prediction"}


def _subject_entry_summary(entry: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "id",
        "kind",
        "collection",
        "root_key",
        "relative_path",
        "path",
        "subject",
        "project",
        "title",
        "prompt",
        "provider",
        "model",
        "source_url",
    ]
    return {key: entry.get(key, "") for key in keys}


def _suite_href(**params: str) -> str:
    return "/?" + urlencode({key: value for key, value in params.items() if value})


def _entry_sort_key(entry: dict[str, Any]) -> tuple[Any, ...]:
    metadata = entry.get("metadata") if isinstance(entry.get("metadata"), dict) else {}
    try:
        mtime_ns = int(metadata.get("mtime_ns") or 0)
    except (TypeError, ValueError):
        mtime_ns = 0
    kind = str(entry.get("kind") or "")
    collection = str(entry.get("collection") or "")
    return (
        KIND_PRIORITY.get(kind, 99),
        COLLECTION_PRIORITY.get(collection, 99),
        -mtime_ns,
        str(entry.get("subject") or ""),
        str(entry.get("project") or ""),
        str(entry.get("title") or ""),
        str(entry.get("relative_path") or ""),
    )


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
                metadata={"size_bytes": path.stat().st_size, "mtime_ns": path.stat().st_mtime_ns},
            ))
    return result

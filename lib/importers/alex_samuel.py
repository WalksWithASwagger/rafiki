"""Importer for the local alex-samuel portrait and video pipeline."""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from lib.media_types import MediaEntry, MediaImportResult, StyleProfile, SubjectProfile, VideoEdit

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
VIDEO_SUFFIXES = {".mp4", ".mov", ".m4v", ".webm"}
AUDIO_SUFFIXES = {".mp3", ".wav", ".m4a", ".aac", ".flac"}
DATASET_SUFFIXES = {".zip"}
SKIP_DIRS = {".git", "venv", "venv311", ".venv", "__pycache__", "node_modules"}
SKIP_FILES = {".env"}


def import_root(root: Path, *, root_key: str = "alex-samuel", indexed_at: str | None = None) -> MediaImportResult:
    root = Path(root).expanduser().resolve()
    indexed_at = indexed_at or datetime.now().astimezone().isoformat(timespec="seconds")
    result = MediaImportResult(
        root_key=root_key,
        root_path=str(root),
        importer="alex-samuel",
    )
    if not root.exists():
        result.warnings.append(f"root not found: {root}")
        return result

    subjects = _discover_subjects(root, root_key=root_key)
    subject_by_key = {subject.key: subject for subject in subjects}
    entries: dict[str, MediaEntry] = {}

    def add(entry: MediaEntry) -> None:
        if not entry.indexed_at:
            entry.indexed_at = indexed_at or ""
        entries[entry.id] = entry

    for subject in subjects:
        for suite in subject.prompt_suites:
            path = Path(suite)
            add(_entry_for_path(root, root_key, path, "prompt-suite", collection="prompts", subject=subject.key))
        for album in subject.album_roots:
            path = Path(album)
            if path.exists():
                add(_entry_for_path(root, root_key, path, "dataset", collection="albums", subject=subject.key))
        for training_root in subject.training_roots:
            path = Path(training_root)
            if path.exists():
                add(_entry_for_path(root, root_key, path, "model-version", collection="training", subject=subject.key))

    for path in _iter_known_json(root):
        rel = _rel(root, path)
        if path.name == "predictions.json":
            for entry in _entries_from_predictions(root, root_key, path):
                add(entry)
        elif path.name == "trainings.json":
            _merge_training_versions(root, path, subject_by_key)
            add(_entry_for_path(root, root_key, path, "training-manifest", collection="training"))
        elif path.name == "storyboard.json":
            add(_entry_for_path(root, root_key, path, "storyboard", collection="video", project=_project_from_video_path(root, path)))
        elif path.name == "shot_list.json":
            add(_entry_for_path(root, root_key, path, "shot-list", collection="video", project=_project_from_video_path(root, path)))
        elif path.name.endswith(".json") and "prompt_suite" in path.name:
            subject = _subject_from_client_path(root, path)
            add(_entry_for_path(root, root_key, path, "prompt-suite", collection="prompts", subject=subject))
        elif path.name.startswith("style_anchors") or "style_anchors" in path.name:
            style = _style_from_anchor_file(root, root_key, path)
            result.styles.append(style)
            add(_entry_for_path(root, root_key, path, "style", collection="styles", title=style.name, style=style.name))
        elif rel.startswith("evals/") and "results" in path.name:
            add(_entry_for_path(root, root_key, path, "evaluation", collection="evaluations"))

    for path in _iter_media_files(root):
        kind = _kind_for_suffix(path.suffix)
        if not kind:
            continue
        collection = _collection_for_path(root, path, kind)
        add(_entry_for_path(
            root,
            root_key,
            path,
            kind,
            collection=collection,
            subject=_subject_for_path(root, path),
            project=_project_for_path(root, path),
        ))

    result.subjects = sorted(subject_by_key.values(), key=lambda subject: subject.key)
    result.entries = sorted(entries.values(), key=lambda entry: (entry.collection, entry.kind, entry.relative_path))
    result.video_edits = _discover_video_edits(root, root_key)
    if not result.styles:
        result.styles = _discover_style_anchors(root, root_key)
    return result


def _iter_known_json(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        for filename in filenames:
            if filename in SKIP_FILES or not filename.endswith(".json"):
                continue
            yield Path(dirpath) / filename


def _iter_media_files(root: Path) -> Iterable[Path]:
    allowed = IMAGE_SUFFIXES | VIDEO_SUFFIXES | AUDIO_SUFFIXES | DATASET_SUFFIXES
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        for filename in filenames:
            if filename in SKIP_FILES:
                continue
            path = Path(dirpath) / filename
            if path.suffix.lower() in allowed:
                yield path


def _should_skip(path: Path, root: Path) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        rel_parts = path.parts
    if any(part in SKIP_DIRS for part in rel_parts[:-1]):
        return True
    return path.name in SKIP_FILES


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _stable_id(root_key: str, relative_path: str, kind: str, collection: str = "") -> str:
    digest = hashlib.sha1(f"{root_key}:{kind}:{collection}:{relative_path}".encode("utf-8")).hexdigest()[:16]
    slug = re.sub(r"[^a-z0-9]+", "-", Path(relative_path).stem.lower()).strip("-")[:48]
    return f"{root_key}-{kind}-{slug or digest}-{digest}"


def _entry_for_path(
    root: Path,
    root_key: str,
    path: Path,
    kind: str,
    *,
    collection: str,
    subject: str = "",
    project: str = "",
    title: str = "",
    prompt: str = "",
    style: str = "",
    negative_prompt: str = "",
    provider: str = "",
    model: str = "",
    source_manifest: str = "",
    source_url: str = "",
    tags: list[str] | None = None,
    lineage: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> MediaEntry:
    relative_path = _rel(root, path)
    title = title or _title_from_path(path)
    meta = dict(metadata or {})
    if path.exists() and path.is_file():
        meta.setdefault("size_bytes", path.stat().st_size)
    return MediaEntry(
        id=_stable_id(root_key, relative_path, kind, collection),
        kind=kind,
        collection=collection,
        root_key=root_key,
        path=str(path.resolve(strict=False)),
        relative_path=relative_path,
        subject=subject,
        project=project,
        title=title,
        prompt=prompt,
        style=style,
        negative_prompt=negative_prompt,
        provider=provider,
        model=model,
        source_manifest=source_manifest,
        source_url=source_url,
        tags=tags or [],
        lineage=lineage or {},
        metadata=meta,
    )


def _title_from_path(path: Path) -> str:
    return path.stem.replace("-", " ").replace("_", " ").strip().title()


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _discover_subjects(root: Path, *, root_key: str) -> list[SubjectProfile]:
    subjects: dict[str, SubjectProfile] = {}

    clients_dir = root / "clients"
    if clients_dir.exists():
        for client_dir in sorted(p for p in clients_dir.iterdir() if p.is_dir()):
            key = client_dir.name
            profile = subjects.setdefault(
                key,
                SubjectProfile(key=key, display_name=_title_from_path(client_dir), root_key=root_key),
            )
            for prompt_suite in sorted(client_dir.glob("prompt_suite*.json")):
                profile.prompt_suites.append(str(prompt_suite.resolve(strict=False)))
            album = client_dir / "album"
            if album.exists():
                profile.album_roots.append(str(album.resolve(strict=False)))

    experiments = root / "evals" / "experiments"
    if experiments.exists():
        for subject_dir in sorted(p for p in experiments.iterdir() if p.is_dir()):
            subject_key = subject_dir.name.split("_", 1)[0]
            profile = subjects.setdefault(
                subject_key,
                SubjectProfile(key=subject_key, display_name=_title_from_path(Path(subject_key)), root_key=root_key),
            )
            profile.training_roots.append(str(subject_dir.resolve(strict=False)))

    return sorted(subjects.values(), key=lambda subject: subject.key)


def _merge_training_versions(root: Path, path: Path, subjects: dict[str, SubjectProfile]) -> None:
    data = _read_json(path)
    runs = data.get("runs") if isinstance(data, dict) else None
    if not isinstance(runs, list):
        return
    subject = _subject_for_path(root, path)
    profile = subjects.get(subject)
    if not profile:
        return
    for run in runs:
        if not isinstance(run, dict):
            continue
        version = run.get("model_version") or run.get("version") or run.get("training_response", {}).get("version")
        model = run.get("destination") or run.get("model") or run.get("training_response", {}).get("model")
        profile.model_versions.append({
            "run_id": run.get("run_id", ""),
            "model": model or "",
            "version": version or "",
            "status": run.get("status") or run.get("training_response", {}).get("status", ""),
            "source_manifest": str(path.resolve(strict=False)),
        })


def _entries_from_predictions(root: Path, root_key: str, manifest: Path) -> list[MediaEntry]:
    data = _read_json(manifest)
    predictions = data
    if isinstance(data, dict):
        predictions = data.get("predictions") or data.get("items") or data.get("results") or []
    if not isinstance(predictions, list):
        return []

    entries: list[MediaEntry] = []
    for idx, prediction in enumerate(predictions):
        if not isinstance(prediction, dict):
            continue
        output_path = _resolve_prediction_output(root, manifest, prediction)
        kind = "video" if output_path and output_path.suffix.lower() in VIDEO_SUFFIXES else "image"
        if output_path is None:
            output_path = manifest
            kind = "prediction"
        project = prediction.get("project") or _project_from_video_path(root, manifest)
        subject = prediction.get("subject") or _subject_for_path(root, manifest)
        title = prediction.get("name") or prediction.get("shot_id") or prediction.get("key") or f"Prediction {idx + 1}"
        model = str(prediction.get("model") or prediction.get("version") or "")
        provider = "replicate" if prediction.get("prediction_id") or prediction.get("urls") else ""
        entry = _entry_for_path(
            root,
            root_key,
            output_path,
            kind,
            collection="predictions" if kind != "video" else "video",
            subject=str(subject or ""),
            project=str(project or ""),
            title=str(title),
            prompt=str(prediction.get("prompt") or ""),
            provider=provider,
            model=model,
            source_manifest=str(manifest.resolve(strict=False)),
            source_url=_output_url(prediction),
            tags=[str(v) for v in [prediction.get("scene_id"), prediction.get("shot_id")] if v],
            lineage={
                "prediction_id": prediction.get("prediction_id") or prediction.get("id", ""),
                "scene_id": prediction.get("scene_id", ""),
                "shot_id": prediction.get("shot_id", ""),
            },
            metadata=_safe_prediction_metadata(prediction),
        )
        if output_path == manifest:
            entry.id = _stable_id(root_key, f"{_rel(root, manifest)}#{idx}", kind, "predictions")
        entries.append(entry)
    return entries


def _safe_prediction_metadata(prediction: dict[str, Any]) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for key in ("status", "metrics", "created_at", "completed_at", "urls"):
        value = prediction.get(key)
        if value not in (None, ""):
            metadata[key] = value
    return metadata


def _resolve_prediction_output(root: Path, manifest: Path, prediction: dict[str, Any]) -> Path | None:
    candidates: list[Any] = [
        prediction.get("file"),
        prediction.get("path"),
        prediction.get("output_path"),
        prediction.get("local_path"),
    ]
    output = prediction.get("output")
    if isinstance(output, dict):
        candidates.extend([output.get("file"), output.get("path"), output.get("local_path")])
    elif isinstance(output, list):
        candidates.extend(output)
    elif isinstance(output, str):
        candidates.append(output)

    for candidate in candidates:
        if not isinstance(candidate, str) or not candidate:
            continue
        if candidate.startswith("http://") or candidate.startswith("https://"):
            continue
        path = Path(candidate).expanduser()
        if not path.is_absolute():
            for base in (manifest.parent, root):
                resolved = (base / path).resolve(strict=False)
                if resolved.exists():
                    return resolved
            path = (manifest.parent / path).resolve(strict=False)
        if path.exists():
            return path.resolve()
    return None


def _output_url(prediction: dict[str, Any]) -> str:
    output = prediction.get("output")
    if isinstance(output, dict):
        for key in ("url", "output_url"):
            value = output.get(key)
            if isinstance(value, str) and value.startswith(("http://", "https://")):
                return value
    if isinstance(output, str) and output.startswith(("http://", "https://")):
        return output
    value = prediction.get("output_url") or prediction.get("url")
    return value if isinstance(value, str) else ""


def _kind_for_suffix(suffix: str) -> str:
    suffix = suffix.lower()
    if suffix in IMAGE_SUFFIXES:
        return "image"
    if suffix in VIDEO_SUFFIXES:
        return "video"
    if suffix in AUDIO_SUFFIXES:
        return "audio"
    if suffix in DATASET_SUFFIXES:
        return "dataset"
    return ""


def _collection_for_path(root: Path, path: Path, kind: str) -> str:
    rel = _rel(root, path)
    if rel.startswith("video_project/"):
        return "video"
    if rel.startswith("festival_submission/"):
        return "festival-submission"
    if rel.startswith("delivery/"):
        return "delivery"
    if rel.startswith("photos/"):
        return "photos"
    if rel.startswith("training"):
        return "training"
    if rel.startswith("evals/"):
        return "evaluations"
    return kind


def _subject_for_path(root: Path, path: Path) -> str:
    rel_parts = _rel(root, path).split("/")
    if len(rel_parts) >= 3 and rel_parts[0] == "evals" and rel_parts[1] == "experiments":
        return rel_parts[2].split("_", 1)[0]
    if len(rel_parts) >= 2 and rel_parts[0] == "clients":
        return rel_parts[1]
    return ""


def _subject_from_client_path(root: Path, path: Path) -> str:
    rel_parts = _rel(root, path).split("/")
    return rel_parts[1] if len(rel_parts) >= 2 and rel_parts[0] == "clients" else ""


def _project_for_path(root: Path, path: Path) -> str:
    rel = _rel(root, path)
    if rel.startswith("video_project/both_hands_full/"):
        return "both_hands_full"
    if rel.startswith("video_project/time_airport/"):
        return "time_airport"
    if rel.startswith("video_project/"):
        return "dont_need_your_permission"
    return ""


def _project_from_video_path(root: Path, path: Path) -> str:
    return _project_for_path(root, path)


def _style_from_anchor_file(root: Path, root_key: str, path: Path) -> StyleProfile:
    data = _read_json(path)
    if not isinstance(data, dict):
        data = {}
    name = str(data.get("version") or path.stem)
    return StyleProfile(
        name=name,
        suffix=str(data.get("style_suffix") or ""),
        negative_suffix=str(data.get("negative_suffix") or ""),
        root_key=root_key,
        source=str(path.resolve(strict=False)),
        media_types=["image", "video"],
        metadata={key: value for key, value in data.items() if key not in {"style_suffix", "negative_suffix"}},
    )


def _discover_style_anchors(root: Path, root_key: str) -> list[StyleProfile]:
    styles = []
    for path in root.rglob("*style_anchors*.json"):
        if not _should_skip(path, root):
            styles.append(_style_from_anchor_file(root, root_key, path))
    return styles


def _discover_video_edits(root: Path, root_key: str) -> list[VideoEdit]:
    edits: list[VideoEdit] = []
    for path in _iter_media_files(root):
        if path.suffix.lower() not in VIDEO_SUFFIXES:
            continue
        rel = _rel(root, path)
        if "/edits/" not in rel and not rel.startswith("festival_submission/"):
            continue
        project = _project_for_path(root, path) or ("festival_submission" if rel.startswith("festival_submission/") else "")
        edit_id = _stable_id(root_key, rel, "video-edit", "video")
        edits.append(VideoEdit(
            id=edit_id,
            project=project,
            title=_title_from_path(path),
            root_key=root_key,
            render_outputs=[str(path.resolve(strict=False))],
            source_manifest=str(path.resolve(strict=False)),
            metadata={"relative_path": rel, "size_bytes": path.stat().st_size if path.exists() else 0},
        ))
    return sorted(edits, key=lambda edit: (edit.project, edit.title))

"""Video generation and assembly helpers for the local suite."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from lib.jobs import provider_cost_preview, write_manifest
from lib.providers import replicate_provider

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VIDEO_MODEL = "wan-video/wan2.1-with-lora"
VIDEO_SELECTION_VALUES = {"focus", "star", "exclude"}
DEFAULT_EDL_SELECTIONS = ("focus", "star")
DURATION_TOLERANCE_SECONDS = 0.05


def build_video_preview(
    *,
    storyboard_path: Path,
    model: str = DEFAULT_VIDEO_MODEL,
    execute: bool = False,
) -> dict[str, Any]:
    """Return a local cost/count preview with no file I/O beyond reading the storyboard."""
    storyboard_path = Path(storyboard_path).expanduser().resolve()
    data = _load_json(storyboard_path)
    scenes = _scenes(data)
    count_preview = {
        "planned_provider_jobs": 1,
        "network_calls": 1 if execute else 0,
        "storyboard_scenes": len(scenes),
        "prompted_scenes": sum(1 for scene in scenes if scene.get("prompt")),
        "requested_videos": 1,
    }
    from lib.jobs import provider_cost_preview as _pcp

    cost_estimate = _pcp(
        provider="Replicate",
        model=model,
        counts=count_preview,
        dry_run=not execute,
        note="Replicate video generation spend is not estimated locally; use provider billing for exact charges.",
    )
    return {
        "kind": "video-generation",
        "provider": "Replicate",
        "model": model,
        "execute": execute,
        "dry_run": not execute,
        "count_preview": count_preview,
        "cost_estimate": cost_estimate,
        "pricing_note": cost_estimate["note"],
    }


def plan_video_generation(
    *,
    storyboard_path: Path,
    output_root: Path | None = None,
    execute: bool = False,
    model: str = DEFAULT_VIDEO_MODEL,
) -> dict[str, Any]:
    storyboard_path = Path(storyboard_path).expanduser().resolve()
    data = _load_json(storyboard_path)
    project = _project_key(data, storyboard_path)
    scenes = _scenes(data)
    output_root = output_root or REPO_ROOT / "output"
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    run_dir = output_root / project / f"video-run-{stamp}"
    manifest_path = run_dir / "run.json"
    request_input = {
        "storyboard": str(storyboard_path),
        "project": project,
        "scene_count": len(scenes),
        "scenes": scenes,
    }
    count_preview = {
        "planned_provider_jobs": 1,
        "network_calls": 1 if execute else 0,
        "storyboard_scenes": len(scenes),
        "prompted_scenes": sum(1 for scene in scenes if scene.get("prompt")),
        "requested_videos": 1,
    }
    cost_estimate = provider_cost_preview(
        provider="Replicate",
        model=model,
        counts=count_preview,
        dry_run=not execute,
        note="Replicate video generation spend is not estimated locally; use provider billing for exact charges.",
    )
    provider_response = replicate_provider.run_prediction(model, request_input, execute=execute)
    job = replicate_provider.create_job(
        kind="video-generation",
        model=model,
        input=request_input,
        target_output_dir=run_dir,
        manifest_path=manifest_path,
        execute=execute,
        endpoint="predictions",
        provider_response=provider_response,
        cost_estimate=cost_estimate,
    )
    manifest = {
        "version": 1,
        "kind": "video-generation",
        "status": "queued" if execute else "dry-run",
        "project": project,
        "model": model,
        "storyboard_path": str(storyboard_path),
        "scenes": scenes,
        "count_preview": count_preview,
        "cost_estimate": cost_estimate,
        "job": job.to_dict(),
        "created_at": job.created_at,
    }
    write_manifest(manifest_path, manifest)
    return {"ok": True, "job": job.to_dict(), "manifest": manifest, "manifest_path": str(manifest_path)}


def assemble_video_edit(*, edit_path: Path, output_dir: Path | None = None, execute: bool = False) -> dict[str, Any]:
    edit_path = Path(edit_path).expanduser().resolve()
    edit = _load_json(edit_path)
    clips = edit.get("clips") if isinstance(edit, dict) else None
    if not isinstance(clips, list) or not clips:
        raise ValueError("edit JSON must contain a non-empty clips array")
    validation = validate_edit_manifest(edit, base_path=edit_path.parent)
    resolved_clips = [Path(item["path"]) for item in validation["clips"]]
    missing = [error["path"] for error in validation["errors"] if error["type"] == "missing_clip"]
    project = str(edit.get("project") or edit_path.stem)
    output_dir = output_dir or REPO_ROOT / "output" / project / f"edit-{edit_path.stem}"
    manifest_path = output_dir / "edit.json"
    output_path = output_dir / f"{edit_path.stem}.mp4"
    status = "dry-run"
    if validation["errors"]:
        status = "blocked"
    elif execute:
        status = "ready"
    manifest = {
        "version": 1,
        "kind": "video-edit",
        "status": status,
        "project": project,
        "source_edit": str(edit_path),
        "clips": [item["path"] for item in validation["clips"]],
        "missing": missing,
        "missing_audio": [error["path"] for error in validation["errors"] if error["type"] == "missing_audio"],
        "audio_path": validation["audio_path"],
        "effects_preset": edit.get("effects_preset", ""),
        "output_path": str(output_path),
        "validation": validation,
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    if execute:
        if validation["errors"]:
            write_manifest(manifest_path, manifest)
            raise FileNotFoundError(_validation_error_summary(validation))
        ffmpeg = _run_ffmpeg_concat(resolved_clips, output_path)
        manifest["ffmpeg"] = ffmpeg
        if ffmpeg["exit_code"] != 0:
            manifest["status"] = "failed"
            write_manifest(manifest_path, manifest)
            raise RuntimeError(f"ffmpeg failed with exit code {ffmpeg['exit_code']}")
        manifest["status"] = "rendered"
    write_manifest(manifest_path, manifest)
    return {"ok": True, "manifest": manifest, "manifest_path": str(manifest_path)}


def export_video_selection_edl(
    *,
    selections: dict[str, Any],
    registry: dict[str, Any],
    selection_values: list[str] | tuple[str, ...] | None = None,
    project: str = "",
) -> dict[str, Any]:
    selected = _selection_items(selections)
    included_values = tuple(selection_values or DEFAULT_EDL_SELECTIONS)
    invalid_values = sorted(set(included_values) - VIDEO_SELECTION_VALUES)
    if invalid_values:
        raise ValueError(f"unknown selection value(s): {', '.join(invalid_values)}")

    entries = [entry for entry in registry.get("entries", []) if isinstance(entry, dict)]
    entries_by_id = {str(entry.get("id")): entry for entry in entries if entry.get("id")}
    clips = []
    for entry in entries:
        entry_id = str(entry.get("id") or "")
        if entry.get("kind") != "video" or selected.get(entry_id) not in included_values:
            continue
        clips.append(_edl_clip_from_entry(entry, selected[entry_id], len(clips) + 1))

    missing_selection_ids = [
        {"id": key, "selection": value}
        for key, value in sorted(selected.items())
        if value in included_values and key not in entries_by_id
    ]
    edl_project = project or _single_project(clips) or "video-lab"
    return {
        "version": 1,
        "kind": "rafiki-video-edl",
        "project": edl_project,
        "selection_values": list(included_values),
        "clip_count": len(clips),
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "clips": clips,
        "missing_selection_ids": missing_selection_ids,
        "edit_manifest": edit_manifest_from_edl_clips(clips, project=edl_project),
    }


def edit_manifest_from_edl_clips(clips: list[dict[str, Any]], *, project: str = "video-lab") -> dict[str, Any]:
    manifest_clips = []
    for clip in clips:
        manifest_clip = {
            "id": clip.get("id", ""),
            "path": clip.get("path", ""),
            "title": clip.get("title", ""),
            "selection": clip.get("selection", ""),
            "root_key": clip.get("root_key", ""),
            "relative_path": clip.get("relative_path", ""),
        }
        for key in ("duration_seconds", "source_duration_seconds", "start_seconds", "end_seconds"):
            if clip.get(key) not in (None, ""):
                manifest_clip[key] = clip[key]
        manifest_clips.append(manifest_clip)
    return {
        "version": 1,
        "kind": "video-edit",
        "project": project,
        "clips": manifest_clips,
    }


def import_video_selection_payload(
    payload: dict[str, Any],
    *,
    registry: dict[str, Any],
    default_selection: str = "focus",
) -> dict[str, Any]:
    if default_selection not in VIDEO_SELECTION_VALUES:
        raise ValueError("default_selection must be focus, star, or exclude")
    clips = _clips_from_selection_payload(payload)
    entries = [entry for entry in registry.get("entries", []) if isinstance(entry, dict) and entry.get("kind") == "video"]
    entries_by_id = {str(entry.get("id")): entry for entry in entries if entry.get("id")}
    entries_by_path = {_normalised_path(entry.get("path")): entry for entry in entries if entry.get("path")}
    items: dict[str, str] = {}
    unmatched = []
    for clip in clips:
        if not isinstance(clip, dict):
            continue
        entry_id = str(clip.get("id") or "")
        entry = entries_by_id.get(entry_id)
        if entry is None:
            entry = entries_by_path.get(_normalised_path(clip.get("path")))
        if entry is None:
            unmatched.append({
                "id": entry_id,
                "path": str(clip.get("path") or ""),
                "title": str(clip.get("title") or ""),
            })
            continue
        selection = str(clip.get("selection") or default_selection)
        if selection not in VIDEO_SELECTION_VALUES:
            selection = default_selection
        items[str(entry["id"])] = selection
    return {
        "ok": len(unmatched) == 0,
        "items": items,
        "imported": len(items),
        "unmatched_clips": unmatched,
    }


def validate_edit_manifest(edit: dict[str, Any], *, base_path: Path) -> dict[str, Any]:
    clips = edit.get("clips") if isinstance(edit, dict) else None
    if not isinstance(clips, list) or not clips:
        raise ValueError("edit JSON must contain a non-empty clips array")
    resolved = []
    errors = []
    for index, clip in enumerate(clips, start=1):
        path = _clip_path(base_path, clip)
        clip_data = clip if isinstance(clip, dict) else {}
        record = _validated_clip_record(index, path, clip_data)
        resolved.append(record)
        if not path.exists():
            errors.append({
                "type": "missing_clip",
                "clip_index": index,
                "path": str(path),
                "message": f"clip {index} is missing: {path}",
            })
        errors.extend(_duration_errors(index, clip_data))

    audio_path = _audio_path(base_path, edit)
    if audio_path and not Path(audio_path).exists():
        errors.append({
            "type": "missing_audio",
            "path": audio_path,
            "message": f"audio file is missing: {audio_path}",
        })
    return {
        "ok": not errors,
        "errors": errors,
        "clips": resolved,
        "audio_path": audio_path,
        "duration_tolerance_seconds": DURATION_TOLERANCE_SECONDS,
    }


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise
    except Exception as e:
        raise ValueError(f"invalid JSON at {path}: {e}") from e
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def _project_key(data: dict[str, Any], path: Path) -> str:
    raw = data.get("key") or data.get("slug") or data.get("project") or data.get("title") or path.parent.name
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in str(raw)).strip("-") or "video"


def _scenes(data: dict[str, Any]) -> list[dict[str, Any]]:
    raw = data.get("scenes") or []
    if isinstance(raw, dict):
        iterable = raw.values()
    elif isinstance(raw, list):
        iterable = raw
    else:
        iterable = []
    scenes = []
    for idx, scene in enumerate(iterable):
        if not isinstance(scene, dict):
            continue
        scenes.append({
            "id": scene.get("id") or scene.get("scene_id") or scene.get("key") or f"scene-{idx + 1}",
            "title": scene.get("title") or scene.get("section") or "",
            "prompt": scene.get("prompt") or scene.get("notes") or "",
        })
    return scenes


def _clip_path(base_path: Path, clip: Any) -> Path:
    raw = clip.get("path") if isinstance(clip, dict) else clip
    if not isinstance(raw, str) or not raw:
        raise ValueError("clip entries must be paths or objects with path")
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = (base_path / path).resolve(strict=False)
    return path


def _run_ffmpeg_concat(clips: list[Path], output_path: Path) -> dict[str, Any]:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise FileNotFoundError("ffmpeg is required for video assembly")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    concat_file = output_path.parent / ".concat.txt"
    concat_file.write_text(
        "\n".join(_concat_line(path) for path in clips),
        encoding="utf-8",
    )
    proc = subprocess.run(
        [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(output_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "command": [ffmpeg, "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(output_path)],
        "exit_code": proc.returncode,
        "stdout": proc.stdout[-2000:],
        "stderr": proc.stderr[-2000:],
        "output_path": str(output_path),
    }


def _concat_line(path: Path) -> str:
    escaped = str(path).replace("'", "'\\''")
    return f"file '{escaped}'"


def _selection_items(selections: dict[str, Any]) -> dict[str, str]:
    raw = selections.get("items") if isinstance(selections, dict) else None
    if not isinstance(raw, dict):
        return {}
    return {str(key): str(value) for key, value in raw.items() if str(value) in VIDEO_SELECTION_VALUES}


def _edl_clip_from_entry(entry: dict[str, Any], selection: str, index: int) -> dict[str, Any]:
    metadata = entry.get("metadata") if isinstance(entry.get("metadata"), dict) else {}
    duration = _seconds(metadata.get("duration_seconds") or metadata.get("duration"))
    clip = {
        "index": index,
        "id": str(entry.get("id") or ""),
        "selection": selection,
        "path": str(entry.get("path") or ""),
        "root_key": str(entry.get("root_key") or ""),
        "relative_path": str(entry.get("relative_path") or ""),
        "project": str(entry.get("project") or ""),
        "title": str(entry.get("title") or entry.get("id") or ""),
    }
    if duration is not None:
        clip["duration_seconds"] = duration
        clip["source_duration_seconds"] = duration
    return clip


def _single_project(clips: list[dict[str, Any]]) -> str:
    projects = {str(clip.get("project") or "") for clip in clips if clip.get("project")}
    return projects.pop() if len(projects) == 1 else ""


def _clips_from_selection_payload(payload: dict[str, Any]) -> list[Any]:
    if not isinstance(payload, dict):
        raise ValueError("import payload must be a JSON object")
    if isinstance(payload.get("clips"), list):
        return payload["clips"]
    edit_manifest = payload.get("edit_manifest")
    if isinstance(edit_manifest, dict) and isinstance(edit_manifest.get("clips"), list):
        return edit_manifest["clips"]
    raise ValueError("import payload must contain clips or edit_manifest.clips")


def _normalised_path(value: Any) -> str:
    if not isinstance(value, str) or not value:
        return ""
    return str(Path(value).expanduser().resolve(strict=False))


def _validated_clip_record(index: int, path: Path, clip: dict[str, Any]) -> dict[str, Any]:
    record = {
        "index": index,
        "path": str(path),
        "exists": path.exists(),
        "id": str(clip.get("id") or ""),
        "title": str(clip.get("title") or ""),
    }
    for key in ("duration_seconds", "source_duration_seconds", "start_seconds", "end_seconds"):
        value = _seconds(clip.get(key))
        if value is not None:
            record[key] = value
    return record


def _duration_errors(index: int, clip: dict[str, Any]) -> list[dict[str, Any]]:
    declared = _seconds(clip.get("duration_seconds") or clip.get("duration"))
    expected = _seconds(clip.get("expected_duration_seconds"))
    start = _seconds(clip.get("start_seconds") or clip.get("in_seconds") or clip.get("in"))
    end = _seconds(clip.get("end_seconds") or clip.get("out_seconds") or clip.get("out"))
    metadata = clip.get("metadata") if isinstance(clip.get("metadata"), dict) else {}
    source_duration = _seconds(clip.get("source_duration_seconds") or metadata.get("duration_seconds") or metadata.get("duration"))
    errors = []
    if start is not None and end is not None:
        if end <= start:
            errors.append(_duration_error(index, "end_seconds must be greater than start_seconds", start, end))
        elif declared is not None and _duration_diff(declared, end - start):
            errors.append(_duration_error(index, "duration_seconds does not match selected range", declared, end - start))
    if declared is not None and expected is not None and _duration_diff(declared, expected):
        errors.append(_duration_error(index, "duration_seconds does not match expected_duration_seconds", declared, expected))
    if source_duration is not None and end is not None and end > source_duration + DURATION_TOLERANCE_SECONDS:
        errors.append(_duration_error(index, "end_seconds exceeds source_duration_seconds", end, source_duration))
    if source_duration is not None and declared is not None and start is None and end is None and _duration_diff(declared, source_duration):
        errors.append(_duration_error(index, "duration_seconds does not match source_duration_seconds", declared, source_duration))
    return errors


def _duration_error(index: int, message: str, actual: float, expected: float) -> dict[str, Any]:
    return {
        "type": "duration_mismatch",
        "clip_index": index,
        "message": f"clip {index}: {message}",
        "actual_seconds": round(actual, 6),
        "expected_seconds": round(expected, 6),
    }


def _duration_diff(left: float, right: float) -> bool:
    return abs(left - right) > DURATION_TOLERANCE_SECONDS


def _seconds(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _audio_path(base_path: Path, edit: dict[str, Any]) -> str:
    raw = edit.get("audio_path") or edit.get("audio")
    if isinstance(raw, dict):
        raw = raw.get("path")
    if not isinstance(raw, str) or not raw:
        return ""
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = (base_path / path).resolve(strict=False)
    return str(path)


def _validation_error_summary(validation: dict[str, Any]) -> str:
    return "; ".join(error["message"] for error in validation.get("errors", [])) or "edit manifest validation failed"

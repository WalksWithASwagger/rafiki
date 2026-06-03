"""Video generation and assembly helpers for the local suite."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from lib.jobs import write_manifest
from lib.providers import replicate_provider

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VIDEO_MODEL = "wan-video/wan2.1-with-lora"


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
    )
    manifest = {
        "version": 1,
        "kind": "video-generation",
        "status": "queued" if execute else "dry-run",
        "project": project,
        "model": model,
        "storyboard_path": str(storyboard_path),
        "scenes": scenes,
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
    resolved_clips = [_clip_path(edit_path, clip) for clip in clips]
    missing = [str(path) for path in resolved_clips if not path.exists()]
    project = str(edit.get("project") or edit_path.stem)
    output_dir = output_dir or REPO_ROOT / "output" / project / f"edit-{edit_path.stem}"
    manifest_path = output_dir / "edit.json"
    output_path = output_dir / f"{edit_path.stem}.mp4"
    manifest = {
        "version": 1,
        "kind": "video-edit",
        "status": "ready" if execute and not missing else "dry-run" if not execute else "blocked",
        "project": project,
        "source_edit": str(edit_path),
        "clips": [str(path) for path in resolved_clips],
        "missing": missing,
        "audio_path": edit.get("audio_path", ""),
        "effects_preset": edit.get("effects_preset", ""),
        "output_path": str(output_path),
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    if execute:
        if missing:
            raise FileNotFoundError(f"missing clip(s): {', '.join(missing)}")
        manifest["ffmpeg"] = _run_ffmpeg_concat(resolved_clips, output_path)
        manifest["status"] = "rendered"
    write_manifest(manifest_path, manifest)
    return {"ok": True, "manifest": manifest, "manifest_path": str(manifest_path)}


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


def _clip_path(edit_path: Path, clip: Any) -> Path:
    raw = clip.get("path") if isinstance(clip, dict) else clip
    if not isinstance(raw, str) or not raw:
        raise ValueError("clip entries must be paths or objects with path")
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = (edit_path.parent / path).resolve(strict=False)
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

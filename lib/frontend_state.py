"""Normalized read-only state for the TypeScript Rafiki frontend."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.parse import quote

from lib.archive_health import archive_health_report

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
PROMPT_PREVIEW_CHARS = 320


def build_library_state(
    output_root: Path,
    *,
    extra_roots: dict[str, Path] | None = None,
    ratings_file: Path | None = None,
    registry_file: Path | None = None,
) -> dict[str, Any]:
    """Return the live archive shape expected by the React frontend."""
    output_root = Path(output_root).resolve()
    extra_roots = {name: Path(path).resolve() for name, path in (extra_roots or {}).items()}
    ratings = _load_json_dict(ratings_file) if ratings_file else {}

    projects: dict[str, dict[str, Any]] = {}
    runs: list[dict[str, Any]] = []
    images: list[dict[str, Any]] = []

    for project, project_dir in _iter_project_roots(output_root, extra_roots):
        project_runs = []
        project_images = []
        for run_dir in sorted(project_dir.glob("run-*")):
            if not run_dir.is_dir():
                continue
            manifest = _load_json_dict(run_dir / "run.json")
            if not manifest:
                continue
            run_id = run_dir.name
            run_key = f"{project}/{run_id}"
            run_images = _image_records(
                project=project,
                run_id=run_id,
                run_dir=run_dir,
                manifest=manifest,
                ratings=ratings,
            )
            run_record = {
                "id": _route_id(run_key),
                "key": run_key,
                "projectId": project,
                "label": run_id,
                "createdAt": _created_at(manifest),
                "imageCount": len(run_images),
                "model": str(manifest.get("model") or ""),
                "style": str(manifest.get("style") or ""),
                "aspectRatio": str(manifest.get("aspect_ratio") or ""),
                "promptFile": str(manifest.get("prompt_file") or ""),
            }
            runs.append(run_record)
            images.extend(run_images)
            project_runs.append(run_record)
            project_images.extend(run_images)

        if project_runs:
            projects[project] = _project_record(project, project_runs, project_images)

    health = _health_payload(output_root, ratings)
    registry = _registry_payload(registry_file)
    return {
        "version": 1,
        "source": "rafiki-local",
        "outputRoot": str(output_root),
        "projects": sorted(projects.values(), key=lambda p: p["updatedAt"], reverse=True),
        "runs": sorted(runs, key=lambda r: r["createdAt"], reverse=True),
        "images": sorted(images, key=lambda i: (i["createdAt"], i["projectId"], i["slot"]), reverse=True),
        "ratings": ratings,
        "health": health,
        "registry": registry,
    }


def _iter_project_roots(output_root: Path, extra_roots: dict[str, Path]) -> list[tuple[str, Path]]:
    roots: list[tuple[str, Path]] = []
    if output_root.exists():
        for path in sorted(output_root.iterdir()):
            if path.is_dir() and not path.name.startswith(".") and path.name not in extra_roots:
                roots.append((path.name, path))
    for project, path in sorted(extra_roots.items()):
        if path.exists() and path.is_dir():
            roots.append((project, path))
    return roots


def _image_records(
    *,
    project: str,
    run_id: str,
    run_dir: Path,
    manifest: dict[str, Any],
    ratings: dict[str, Any],
) -> list[dict[str, Any]]:
    records = []
    model = str(manifest.get("model") or "")
    sampler = str(manifest.get("sampler") or manifest.get("provider") or "")
    created_at = _created_at(manifest)
    items = manifest.get("images") if isinstance(manifest.get("images"), list) else []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue
        filename = str(item.get("file") or "").strip()
        if not filename:
            continue
        key = f"{project}/{run_id}/{filename}"
        source = run_dir / filename
        status = _image_status(item, source)
        records.append({
            "id": _route_id(key),
            "key": key,
            "runId": _route_id(f"{project}/{run_id}"),
            "runKey": f"{project}/{run_id}",
            "projectId": project,
            "slot": int(item.get("slot") or item.get("index") or index),
            "prompt": _prompt_preview(item.get("prompt") or manifest.get("prompt") or ""),
            "name": str(item.get("name") or Path(filename).stem),
            "seed": _number(item.get("seed"), default=0),
            "steps": _number(item.get("steps"), default=0),
            "cfg": _number(item.get("cfg") or item.get("cfg_scale"), default=0),
            "model": str(item.get("model") or model),
            "sampler": str(item.get("sampler") or sampler),
            "latencyMs": int(float(item.get("duration_seconds") or 0) * 1000),
            "status": status,
            "swatch": _swatch(key),
            "createdAt": str(item.get("started_at") or item.get("created_at") or created_at),
            "url": _output_url(key),
            "thumbnailUrl": _output_url(key),
            "rating": _ui_rating(ratings.get(key)),
            "file": filename,
            "ok": status == "present",
        })
    return records


def _project_record(
    project: str,
    runs: list[dict[str, Any]],
    images: list[dict[str, Any]],
) -> dict[str, Any]:
    present = sum(1 for image in images if image["status"] == "present")
    failed = sum(1 for image in images if image["status"] == "failed")
    missing = sum(1 for image in images if image["status"] == "missing")
    if failed or missing:
        health = "fail" if missing else "warn"
    else:
        health = "ok"
    updated_at = max((str(run["createdAt"]) for run in runs), default="")
    tags = sorted({str(run.get("style") or "").strip() for run in runs if str(run.get("style") or "").strip()})
    return {
        "id": project,
        "code": project,
        "name": project.replace("-", " ").title(),
        "runCount": len(runs),
        "imageCount": len(images),
        "presentCount": present,
        "failedCount": failed,
        "missingCount": missing,
        "updatedAt": updated_at,
        "health": health,
        "tags": tags,
    }


def _health_payload(output_root: Path, ratings: dict[str, Any]) -> dict[str, Any]:
    report = archive_health_report(output_root)
    summary = report.get("summary", {})
    return {
        "ok": bool(report.get("ok")),
        "totalProjects": int(summary.get("projects") or 0),
        "totalRuns": int(summary.get("runs") or 0),
        "manifestImages": int(summary.get("manifest_images") or 0),
        "presentImages": int(summary.get("present_images") or 0),
        "missingRecords": int(summary.get("missing_images") or 0),
        "failedImages": int(summary.get("failed_images") or 0),
        "imageFiles": int(summary.get("image_files_on_disk") or 0),
        "duplicateGroups": int(summary.get("duplicate_filename_groups") or 0),
        "cleanupRisk": int(summary.get("cleanup_risk_items") or 0),
        "malformedRuns": len(report.get("malformed_runs") or []),
        "ratings": {
            "starred": sum(1 for value in ratings.values() if value == "star"),
            "rejected": sum(1 for value in ratings.values() if value == "reject"),
        },
        "outputSizeGb": round(int(summary.get("disk_bytes") or 0) / 1_000_000_000, 2),
        "warnings": report.get("recommendations") or [],
    }


def _registry_payload(registry_file: Path | None) -> dict[str, Any]:
    items = _load_json_list(registry_file) if registry_file else []
    approved = sum(1 for item in items if item.get("approval_status") == "approved")
    entries = []
    for item in items:
        path = str(item.get("path") or "")
        entries.append({
            "id": str(item.get("id") or _route_id(path)),
            "projectId": str(item.get("project") or ""),
            "path": path,
            "sizeMb": 0,
            "refs": 1,
            "lastSeen": str(item.get("indexed_at") or ""),
            "status": "indexed" if path else "missing",
            "title": str(item.get("title") or ""),
            "approvalStatus": str(item.get("approval_status") or ""),
        })
    return {
        "entries": entries,
        "summary": {
            "entries": len(items),
            "approved": approved,
            "unapproved": len(items) - approved,
        },
    }


def _created_at(manifest: dict[str, Any]) -> str:
    return str(
        manifest.get("started_at")
        or manifest.get("created_at")
        or manifest.get("timestamp")
        or manifest.get("run_id")
        or ""
    )


def _image_status(item: dict[str, Any], source: Path) -> str:
    if item.get("error"):
        return "failed"
    if source.exists() and source.is_file():
        return "present"
    return "missing"


def _prompt_preview(value: object) -> str:
    text = str(value or "").strip()
    if len(text) <= PROMPT_PREVIEW_CHARS:
        return text
    return text[:PROMPT_PREVIEW_CHARS].rstrip() + "..."


def _number(value: object, *, default: int) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _route_id(key: str) -> str:
    return quote(key, safe="")


def _output_url(key: str) -> str:
    return "/output/" + "/".join(quote(part, safe="") for part in key.split("/"))


def _swatch(key: str) -> str:
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()
    hue = int(digest[:6], 16) % 360
    return f"oklch(0.38 0.08 {hue})"


def _ui_rating(value: object) -> str | None:
    if value == "star":
        return "starred"
    if value == "reject":
        return "rejected"
    return None


def _load_json_dict(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _load_json_list(path: Path | None) -> list[dict[str, Any]]:
    if not path or not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict) and isinstance(data.get("entries"), list):
        return [item for item in data["entries"] if isinstance(item, dict)]
    return []

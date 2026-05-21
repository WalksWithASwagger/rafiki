"""Read-only archive health reporting for Rafiki output roots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lib.archive_metadata import archive_metadata_path, load_archive_metadata
from lib.evaluations import evaluations_path, load_evaluations
from lib.feedback import load_feedback

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return None, str(e)
    if not isinstance(data, dict):
        return None, "JSON root is not an object"
    return data, None


def _safe_file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def _load_ratings(output_root: Path) -> dict[str, str]:
    path = output_root / "ratings.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _image_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    ]


def _load_approved_pairs(project_dir: Path) -> set[tuple[str, str]]:
    data, error = _load_json(project_dir / "approved" / "index.json")
    if error or data is None:
        return set()
    images = data.get("images") if isinstance(data.get("images"), list) else []
    pairs = set()
    for image in images:
        if not isinstance(image, dict):
            continue
        source_run = str(image.get("source_run") or "").strip()
        original_file = str(image.get("original_file") or "").strip()
        if source_run and original_file:
            pairs.add((source_run, original_file))
    return pairs


def _project_dirs(output_root: Path) -> list[Path]:
    if not output_root.exists():
        return []
    return sorted(
        path for path in output_root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    )


def archive_health_report(output_root: Path) -> dict[str, Any]:
    output_root = Path(output_root)
    ratings = _load_ratings(output_root)
    feedback = load_feedback(output_root / "feedback.json").get("items", {})
    evaluations = load_evaluations(evaluations_path(output_root)).get("items", {})
    metadata = load_archive_metadata(archive_metadata_path(output_root)).get("items", {})

    run_count = 0
    manifest_images = 0
    present_images = 0
    failed_images = 0
    known_keys: set[str] = set()
    malformed_runs = []
    missing_images = []
    duplicate_names: dict[tuple[str, str], list[str]] = {}
    cleanup_runs = []

    for project_dir in _project_dirs(output_root):
        project = project_dir.name
        approved_pairs = _load_approved_pairs(project_dir)
        for run_dir in sorted(project_dir.glob("run-*")):
            if not run_dir.is_dir():
                continue
            run_json = run_dir / "run.json"
            if not run_json.exists():
                malformed_runs.append({
                    "project": project,
                    "run": run_dir.name,
                    "path": str(run_json),
                    "error": "missing run.json",
                })
                cleanup_runs.append(_cleanup_run_entry(
                    project=project,
                    run_dir=run_dir,
                    image_count=0,
                    present_images=0,
                    missing_images=0,
                    failed_images=0,
                    approved_images=0,
                    unapproved_images=0,
                    issue="missing run.json",
                ))
                continue
            data, error = _load_json(run_json)
            if error or data is None:
                malformed_runs.append({
                    "project": project,
                    "run": run_dir.name,
                    "path": str(run_json),
                    "error": error or "malformed run.json",
                })
                cleanup_runs.append(_cleanup_run_entry(
                    project=project,
                    run_dir=run_dir,
                    image_count=0,
                    present_images=0,
                    missing_images=0,
                    failed_images=0,
                    approved_images=0,
                    unapproved_images=0,
                    issue=error or "malformed run.json",
                ))
                continue

            run_count += 1
            images = data.get("images") if isinstance(data.get("images"), list) else []
            run_image_count = 0
            run_present_images = 0
            run_missing_images = 0
            run_failed_images = 0
            run_approved_images = 0
            run_unapproved_images = 0
            for image in images:
                if not isinstance(image, dict):
                    continue
                filename = str(image.get("file") or "").strip()
                if not filename:
                    continue
                run_image_count += 1
                manifest_images += 1
                key = f"{project}/{run_dir.name}/{filename}"
                known_keys.add(key)
                duplicate_names.setdefault((project, Path(filename).name.casefold()), []).append(key)
                if image.get("error"):
                    failed_images += 1
                    run_failed_images += 1
                if (run_dir / filename).exists():
                    present_images += 1
                    run_present_images += 1
                else:
                    run_missing_images += 1
                    missing_images.append({
                        "key": key,
                        "path": str(run_dir / filename),
                        "prompt": str(image.get("prompt") or "")[:160],
                    })
                if (run_dir.name, filename) in approved_pairs:
                    run_approved_images += 1
                else:
                    run_unapproved_images += 1
            cleanup_runs.append(_cleanup_run_entry(
                project=project,
                run_dir=run_dir,
                image_count=run_image_count,
                present_images=run_present_images,
                missing_images=run_missing_images,
                failed_images=run_failed_images,
                approved_images=run_approved_images,
                unapproved_images=run_unapproved_images,
            ))

    duplicate_filenames = [
        {"project": project, "basename": basename, "keys": keys}
        for (project, basename), keys in sorted(duplicate_names.items())
        if len(keys) > 1
    ]
    orphaned = {
        "ratings": sorted(key for key in ratings if key not in known_keys),
        "feedback": sorted(key for key in feedback if key not in known_keys),
        "evaluations": sorted(key for key in evaluations if key not in known_keys),
        "metadata": sorted(key for key in metadata if key not in known_keys),
    }
    image_files = _image_files(output_root)
    total_bytes = sum(_safe_file_size(path) for path in image_files)
    cleanup_risk = len(missing_images) + sum(len(items) for items in orphaned.values()) + len(malformed_runs)

    return {
        "ok": not (missing_images or malformed_runs),
        "output_root": str(output_root),
        "summary": {
            "projects": len(_project_dirs(output_root)),
            "runs": run_count,
            "manifest_images": manifest_images,
            "present_images": present_images,
            "missing_images": len(missing_images),
            "failed_images": failed_images,
            "image_files_on_disk": len(image_files),
            "disk_bytes": total_bytes,
            "duplicate_filename_groups": len(duplicate_filenames),
            "orphaned_ratings": len(orphaned["ratings"]),
            "orphaned_feedback": len(orphaned["feedback"]),
            "orphaned_evaluations": len(orphaned["evaluations"]),
            "orphaned_metadata": len(orphaned["metadata"]),
            "cleanup_risk_items": cleanup_risk,
        },
        "malformed_runs": malformed_runs,
        "missing_images": missing_images,
        "duplicate_filenames": duplicate_filenames,
        "orphaned": orphaned,
        "cleanup_report": _cleanup_report(cleanup_runs, orphaned, duplicate_filenames),
        "recommendations": _recommendations(missing_images, malformed_runs, orphaned, duplicate_filenames),
    }


def _cleanup_run_entry(
    *,
    project: str,
    run_dir: Path,
    image_count: int,
    present_images: int,
    missing_images: int,
    failed_images: int,
    approved_images: int,
    unapproved_images: int,
    issue: str | None = None,
) -> dict[str, Any]:
    if issue:
        action = "blocked"
        risk_level = "high"
        reason = f"Cannot prove cleanup safety: {issue}."
    elif missing_images:
        action = "blocked"
        risk_level = "high"
        reason = "Manifest references image files that are missing on disk."
    elif image_count == 0:
        action = "review"
        risk_level = "medium"
        reason = "Run manifest has no image records to compare against approved/."
    elif approved_images == image_count:
        action = "candidate"
        risk_level = "low"
        reason = "Every manifest image is present in approved/index.json."
    else:
        action = "keep"
        risk_level = "medium"
        reason = f"{unapproved_images} manifest image(s) are not yet approved."

    coverage = round((approved_images / image_count) * 100, 1) if image_count else 0.0
    suggested_command = (
        f"python generate.py clean {project} --keep-approved --dry-run"
        if action == "candidate"
        else None
    )
    return {
        "project": project,
        "run": run_dir.name,
        "path": str(run_dir),
        "action": action,
        "risk_level": risk_level,
        "reason": reason,
        "image_count": image_count,
        "present_images": present_images,
        "missing_images": missing_images,
        "failed_images": failed_images,
        "approved_images": approved_images,
        "unapproved_images": unapproved_images,
        "approved_coverage_percent": coverage,
        "disk_bytes": sum(_safe_file_size(path) for path in _image_files(run_dir)),
        "suggested_command": suggested_command,
    }


def _cleanup_report(
    cleanup_runs: list[dict[str, Any]],
    orphaned: dict[str, list[str]],
    duplicate_filenames: list[dict],
) -> dict[str, Any]:
    projects = []
    for project in sorted({run["project"] for run in cleanup_runs}):
        runs = [run for run in cleanup_runs if run["project"] == project]
        candidate_runs = [run for run in runs if run["action"] == "candidate"]
        risky_runs = [run for run in runs if run["action"] != "candidate"]
        projects.append({
            "project": project,
            "summary": {
                "runs": len(runs),
                "candidate_runs": len(candidate_runs),
                "risky_runs": len(risky_runs),
                "candidate_images": sum(run["image_count"] for run in candidate_runs),
                "candidate_bytes": sum(run["disk_bytes"] for run in candidate_runs),
                "total_run_bytes": sum(run["disk_bytes"] for run in runs),
            },
            "suggested_commands": sorted({
                run["suggested_command"] for run in candidate_runs
                if run["suggested_command"]
            }),
            "runs": runs,
        })

    sidecar_orphans = [
        {"collection": collection, "count": len(keys), "keys": keys}
        for collection, keys in sorted(orphaned.items())
        if keys
    ]
    risky_deletions = [
        {
            "project": run["project"],
            "run": run["run"],
            "risk_level": run["risk_level"],
            "reason": run["reason"],
        }
        for run in cleanup_runs
        if run["action"] != "candidate"
    ]
    candidate_runs = [run for run in cleanup_runs if run["action"] == "candidate"]
    return {
        "mutates": False,
        "policy": (
            "Advisory only. Review this report, run the suggested dry-run "
            "commands, and keep approved/ untouched before any cleanup."
        ),
        "summary": {
            "candidate_runs": len(candidate_runs),
            "candidate_images": sum(run["image_count"] for run in candidate_runs),
            "candidate_bytes": sum(run["disk_bytes"] for run in candidate_runs),
            "risky_runs": len(risky_deletions),
            "sidecar_orphan_groups": len(sidecar_orphans),
            "duplicate_filename_groups": len(duplicate_filenames),
        },
        "projects": projects,
        "sidecar_orphans": sidecar_orphans,
        "risky_deletions": risky_deletions,
        "duplicate_filename_groups": duplicate_filenames,
    }


def _recommendations(
    missing_images: list[dict],
    malformed_runs: list[dict],
    orphaned: dict[str, list[str]],
    duplicate_filenames: list[dict],
) -> list[str]:
    recs = []
    if malformed_runs:
        recs.append("Repair or quarantine malformed run manifests before cleanup.")
    if missing_images:
        recs.append("Rebuild viewers after deciding whether missing image records should stay in the archive.")
    if any(orphaned.values()):
        recs.append("Review orphaned ratings, feedback, evaluations, and metadata before deleting sidecar state.")
    if duplicate_filenames:
        recs.append("Inspect duplicate filename groups before approving or removing reruns.")
    if not recs:
        recs.append("Archive health is clean enough for normal review and export work.")
    return recs

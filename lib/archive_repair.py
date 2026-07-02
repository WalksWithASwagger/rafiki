"""Reversible archive repair for missing records, duplicates, and sidecars."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from lib.archive_health import IMAGE_SUFFIXES, archive_health_report

SIDECAR_FILES = {
    "ratings": "ratings.json",
    "feedback": "feedback.json",
    "evaluations": "evaluations.json",
    "metadata": "archive-metadata.json",
}


@dataclass(frozen=True)
class ImageRef:
    project: str
    run: str
    run_dir: Path
    run_json: Path
    file: str
    key: str
    path: Path
    item: dict[str, Any]
    index: int
    mtime: float


def repair_archive(
    output_root: Path,
    *,
    apply: bool = False,
    backup_dir: Path | None = None,
    rebuild_registry: bool = True,
) -> dict[str, Any]:
    output_root = Path(output_root).resolve()
    backup_root = Path(backup_dir).resolve() if backup_dir else _default_backup_dir(output_root)
    health_before = archive_health_report(output_root)
    context = _collect_context(output_root, health_before)
    plan = _build_plan(output_root, backup_root, health_before, context)

    if not apply:
        plan["mutates"] = False
        return plan

    backup_root.mkdir(parents=True, exist_ok=False)
    _write_json(backup_root / "health-before.json", health_before)
    _backup_sidecars(output_root, backup_root)
    _backup_run_jsons(backup_root, plan)
    _write_json(backup_root / "file-hashes.json", plan["file_hashes"])
    _write_json(backup_root / "repair-plan.json", plan)

    result = _apply_plan(output_root, backup_root, plan, context)
    if rebuild_registry:
        from lib import registry

        registry_result = registry.refresh_cache(
            output_root=output_root,
            scope="all-runs",
            reason="archive-repair",
        )
        result["registry"] = registry_result
    health_after = archive_health_report(output_root)
    _write_json(backup_root / "health-after.json", health_after)
    result["health_after"] = {
        "ok": health_after["ok"],
        "summary": health_after["summary"],
    }
    result["mutates"] = True
    return result


def _default_backup_dir(output_root: Path) -> Path:
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    return output_root / ".rafiki-cleanup" / stamp


def _collect_context(output_root: Path, health: dict[str, Any]) -> dict[str, Any]:
    runs: dict[str, dict[str, Any]] = {}
    image_refs: list[ImageRef] = []
    file_hashes: dict[str, dict[str, Any]] = {}
    approved_pairs = _approved_pairs(output_root)
    ratings = _load_json(output_root / "ratings.json")
    evaluations = _sidecar_items(_load_json(output_root / "evaluations.json"))
    metadata = _sidecar_items(_load_json(output_root / "archive-metadata.json"))

    for project_dir in _project_dirs(output_root):
        project = project_dir.name
        for run_dir in sorted(project_dir.glob("run-*")):
            if not run_dir.is_dir():
                continue
            run_json = run_dir / "run.json"
            run_key = f"{project}/{run_dir.name}"
            run_info = {
                "project": project,
                "run": run_dir.name,
                "run_dir": run_dir,
                "run_json": run_json,
                "data": None,
                "images": [],
                "missing_indexes": [],
                "remove_indexes": set(),
                "duplicate_indexes": set(),
                "malformed": False,
                "quarantine_run": False,
                "synthesize": False,
                "synthesize_reason": "",
            }
            data, error = _load_manifest(run_json)
            if data is None:
                run_info["malformed"] = True
                run_info["synthesize"] = bool(_image_files(run_dir))
                run_info["synthesize_reason"] = error or "missing run.json"
                runs[run_key] = run_info
                continue
            images = data.get("images") if isinstance(data.get("images"), list) else []
            run_info["data"] = data
            run_info["images"] = images
            for index, item in enumerate(images):
                if not isinstance(item, dict):
                    continue
                filename = str(item.get("file") or "").strip()
                if not filename:
                    continue
                path = run_dir / filename
                key = f"{project}/{run_dir.name}/{filename}"
                if not path.exists() or not path.is_file():
                    run_info["missing_indexes"].append(index)
                    continue
                digest = _sha256(path)
                file_hashes[key] = {
                    "sha256": digest,
                    "path": str(path),
                    "bytes": path.stat().st_size,
                }
                image_refs.append(ImageRef(
                    project=project,
                    run=run_dir.name,
                    run_dir=run_dir,
                    run_json=run_json,
                    file=filename,
                    key=key,
                    path=path,
                    item=item,
                    index=index,
                    mtime=path.stat().st_mtime,
                ))
            runs[run_key] = run_info

    return {
        "runs": runs,
        "image_refs": image_refs,
        "file_hashes": file_hashes,
        "approved_pairs": approved_pairs,
        "ratings": ratings if isinstance(ratings, dict) else {},
        "evaluations": evaluations,
        "metadata": metadata,
        "health": health,
    }


def _build_plan(
    output_root: Path,
    backup_root: Path,
    health: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    runs = context["runs"]
    for run_info in runs.values():
        run_info["remove_indexes"].update(run_info["missing_indexes"])

    duplicate_groups = _exact_duplicate_groups(context)
    duplicate_removals = []
    for group in duplicate_groups:
        for ref in group["duplicates"]:
            run_key = f"{ref.project}/{ref.run}"
            run_info = runs[run_key]
            index = ref.index
            run_info["remove_indexes"].add(index)
            run_info["duplicate_indexes"].add(index)
            duplicate_removals.append({
                "key": ref.key,
                "path": str(ref.path),
                "canonical_key": group["canonical"].key,
                "sha256": group["sha256"],
            })

    run_rewrites = []
    quarantined_runs = []
    missing_records = []
    duplicate_files = []
    synthesized_runs = []

    for run_key, run_info in sorted(runs.items()):
        if run_info["synthesize"]:
            image_files = _image_files(run_info["run_dir"])
            if image_files:
                synthesized_runs.append({
                    "project": run_info["project"],
                    "run": run_info["run"],
                    "path": str(run_info["run_dir"]),
                    "reason": run_info["synthesize_reason"],
                    "image_count": len(image_files),
                    "run_json": str(run_info["run_json"]),
                })
            else:
                run_info["quarantine_run"] = True
            continue
        if run_info["malformed"]:
            run_info["quarantine_run"] = True
            quarantined_runs.append({
                "project": run_info["project"],
                "run": run_info["run"],
                "path": str(run_info["run_dir"]),
                "reason": run_info["synthesize_reason"] or "malformed run",
            })
            continue

        remove_indexes = set(run_info["remove_indexes"])
        if not remove_indexes:
            continue
        images = run_info["images"]
        kept_images = [item for i, item in enumerate(images) if i not in remove_indexes]
        for index in sorted(remove_indexes):
            item = images[index]
            filename = str(item.get("file") or "")
            entry = {
                "project": run_info["project"],
                "run": run_info["run"],
                "file": filename,
                "key": f"{run_info['project']}/{run_info['run']}/{filename}",
                "record": item,
            }
            if index in run_info["missing_indexes"]:
                missing_records.append(entry)
            if index in run_info["duplicate_indexes"]:
                duplicate_files.append(entry)

        keep_files = [
            run_info["run_dir"] / str(item.get("file") or "")
            for item in kept_images
            if isinstance(item, dict) and item.get("file")
        ]
        has_kept_image_file = any(path.exists() and path.is_file() for path in keep_files)
        if not kept_images and not has_kept_image_file:
            run_info["quarantine_run"] = True
            quarantined_runs.append({
                "project": run_info["project"],
                "run": run_info["run"],
                "path": str(run_info["run_dir"]),
                "reason": "run became empty after repair",
            })
            continue

        run_rewrites.append({
            "project": run_info["project"],
            "run": run_info["run"],
            "path": str(run_info["run_json"]),
            "removed_records": len(remove_indexes),
            "remaining_records": len(kept_images),
        })

    sidecar_orphans = _sidecar_orphans(health)
    operations = {
        "missing_records_removed": missing_records,
        "duplicate_files_quarantined": duplicate_removals,
        "run_json_rewrites": run_rewrites,
        "runs_quarantined": quarantined_runs,
        "malformed_runs_synthesized": synthesized_runs,
        "sidecar_orphans_removed": sidecar_orphans,
    }
    return {
        "schema_version": 1,
        "mutates": False,
        "output_root": str(output_root),
        "backup_dir": str(backup_root),
        "health_before": {
            "ok": health["ok"],
            "summary": health["summary"],
        },
        "counts": {
            "missing_records": len(missing_records),
            "exact_duplicate_files": len(duplicate_removals),
            "run_json_rewrites": len(run_rewrites),
            "runs_quarantined": len(quarantined_runs),
            "malformed_runs_synthesized": len(synthesized_runs),
            "sidecar_orphans": sum(item["count"] for item in sidecar_orphans),
        },
        "operations": operations,
        "file_hashes": context["file_hashes"],
    }


def _apply_plan(
    output_root: Path,
    backup_root: Path,
    plan: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    runs = context["runs"]
    rewritten = 0
    quarantined_files = 0
    quarantined_runs = 0
    synthesized = 0

    for run_info in runs.values():
        if run_info["quarantine_run"]:
            _quarantine_run(backup_root, run_info)
            quarantined_runs += 1
            continue
        if run_info["synthesize"]:
            _synthesize_manifest(run_info)
            synthesized += 1
            continue
        remove_indexes = set(run_info["remove_indexes"])
        if not remove_indexes:
            continue
        for index in sorted(run_info["duplicate_indexes"]):
            item = run_info["images"][index]
            filename = str(item.get("file") or "")
            source = run_info["run_dir"] / filename
            if source.exists() and source.is_file():
                _move_duplicate_file(backup_root, run_info, filename)
                quarantined_files += 1
        data = dict(run_info["data"])
        data["images"] = [
            item for i, item in enumerate(run_info["images"])
            if i not in remove_indexes
        ]
        data["archive_repaired_at"] = _now_iso()
        _write_json(run_info["run_json"], data)
        rewritten += 1

    removed_sidecars = _remove_sidecar_orphans(output_root, plan["operations"]["sidecar_orphans_removed"])
    return {
        "schema_version": 1,
        "output_root": str(output_root),
        "backup_dir": str(backup_root),
        "counts": {
            "run_json_rewrites": rewritten,
            "duplicate_files_quarantined": quarantined_files,
            "runs_quarantined": quarantined_runs,
            "malformed_runs_synthesized": synthesized,
            "sidecar_orphans_removed": removed_sidecars,
        },
        "operations": plan["operations"],
    }


def _exact_duplicate_groups(context: dict[str, Any]) -> list[dict[str, Any]]:
    by_hash: dict[str, list[ImageRef]] = {}
    for ref in context["image_refs"]:
        digest = context["file_hashes"][ref.key]["sha256"]
        by_hash.setdefault(digest, []).append(ref)

    groups = []
    for digest, refs in sorted(by_hash.items()):
        if len(refs) < 2:
            continue
        canonical = max(refs, key=lambda ref: _canonical_score(ref, context))
        duplicates = [ref for ref in refs if ref != canonical]
        if duplicates:
            groups.append({"sha256": digest, "canonical": canonical, "duplicates": duplicates})
    return groups


def _canonical_score(ref: ImageRef, context: dict[str, Any]) -> tuple[int, int, int, float, str]:
    approved = (ref.project, ref.run, ref.file) in context["approved_pairs"]
    rating = context["ratings"].get(ref.key)
    has_review_state = ref.key in context["evaluations"] or ref.key in context["metadata"]
    return (
        1 if approved else 0,
        1 if rating == "star" else 0,
        1 if has_review_state else 0,
        ref.mtime,
        ref.key,
    )


def _approved_pairs(output_root: Path) -> set[tuple[str, str, str]]:
    pairs: set[tuple[str, str, str]] = set()
    for project_dir in _project_dirs(output_root):
        index_path = project_dir / "approved" / "index.json"
        data = _load_json(index_path)
        images = data.get("images") if isinstance(data, dict) and isinstance(data.get("images"), list) else []
        for image in images:
            if not isinstance(image, dict):
                continue
            source_run = str(image.get("source_run") or "")
            original_file = str(image.get("original_file") or "")
            if source_run and original_file:
                pairs.add((project_dir.name, source_run, original_file))
    return pairs


def _sidecar_orphans(health: dict[str, Any]) -> list[dict[str, Any]]:
    orphaned = health.get("orphaned") if isinstance(health.get("orphaned"), dict) else {}
    rows = []
    for collection, keys in sorted(orphaned.items()):
        if not keys:
            continue
        rows.append({
            "collection": collection,
            "count": len(keys),
            "keys": list(keys),
        })
    return rows


def _backup_sidecars(output_root: Path, backup_root: Path) -> None:
    sidecar_dir = backup_root / "sidecars"
    for filename in SIDECAR_FILES.values():
        source = output_root / filename
        if source.exists():
            sidecar_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, sidecar_dir / filename)


def _backup_run_jsons(backup_root: Path, plan: dict[str, Any]) -> None:
    paths = set()
    for row in plan["operations"]["run_json_rewrites"]:
        paths.add(row["path"])
    for row in plan["operations"]["malformed_runs_synthesized"]:
        paths.add(row["run_json"])
    for path in sorted(paths):
        source = Path(path)
        if not source.exists():
            continue
        parts = source.parts[-3:]
        target = backup_root / "run-json" / Path(*parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def _quarantine_run(backup_root: Path, run_info: dict[str, Any]) -> None:
    source = run_info["run_dir"]
    target = backup_root / "quarantine" / "runs" / run_info["project"] / run_info["run"]
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(target))


def _move_duplicate_file(backup_root: Path, run_info: dict[str, Any], filename: str) -> None:
    source = run_info["run_dir"] / filename
    target = backup_root / "quarantine" / "duplicate-files" / run_info["project"] / run_info["run"] / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(target))


def _synthesize_manifest(run_info: dict[str, Any]) -> None:
    images = []
    for index, path in enumerate(_image_files(run_info["run_dir"]), start=1):
        rel = path.relative_to(run_info["run_dir"]).as_posix()
        images.append({
            "name": path.stem,
            "file": rel,
            "prompt": "",
            "slot": index,
            "archive_repair_synthesized": True,
        })
    data = {
        "model": "",
        "aspect_ratio": "",
        "style": "",
        "prompt_file": "",
        "timestamp": _now_iso(),
        "run_id": run_info["run"],
        "archive_repair_synthesized": True,
        "archive_repair_reason": run_info["synthesize_reason"],
        "images": images,
    }
    _write_json(run_info["run_json"], data)


def _remove_sidecar_orphans(output_root: Path, sidecar_orphans: list[dict[str, Any]]) -> int:
    removed = 0
    for group in sidecar_orphans:
        collection = group["collection"]
        filename = SIDECAR_FILES.get(collection)
        if not filename:
            continue
        path = output_root / filename
        data = _load_json(path)
        if not isinstance(data, dict):
            continue
        keys = set(group["keys"])
        if collection == "ratings":
            for key in list(keys):
                if key in data:
                    data.pop(key, None)
                    removed += 1
        else:
            items = data.get("items")
            if not isinstance(items, dict):
                continue
            for key in list(keys):
                if key in items:
                    items.pop(key, None)
                    removed += 1
        _write_json(path, data)
    return removed


def _project_dirs(output_root: Path) -> list[Path]:
    if not output_root.exists():
        return []
    return sorted(
        path for path in output_root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    )


def _image_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        path for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in IMAGE_SUFFIXES
        and ".rafiki-cache" not in path.parts
    )


def _load_manifest(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, "missing run.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return None, str(e)
    if not isinstance(data, dict):
        return None, "JSON root is not an object"
    return data, None


def _load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _sidecar_items(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    items = data.get("items")
    return items if isinstance(items, dict) else {}


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")

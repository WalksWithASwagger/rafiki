"""Portal action helpers for local curation/export workflows."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PortalAction:
    name: str
    label: str
    description: str
    mutating: bool
    external: bool
    confirmable: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "label": self.label,
            "description": self.description,
            "mutating": self.mutating,
            "external": self.external,
            "confirmable": self.confirmable,
        }


ACTIONS = {
    action.name: action
    for action in [
        PortalAction(
            "approve-starred",
            "Approve Starred",
            "Promote starred assets into approved/ and rebuild the approved viewer.",
            mutating=True,
            external=False,
        ),
        PortalAction(
            "canva-export",
            "Canva Export",
            "Build a local Canva bulk-upload bundle from approved assets or the latest run.",
            mutating=True,
            external=False,
        ),
        PortalAction(
            "notion-export",
            "Notion Export",
            "Dry-run or push approved assets to a Notion gallery database.",
            mutating=True,
            external=True,
        ),
        PortalAction(
            "registry-export",
            "Registry Export",
            "Index local assets and export the asset registry as CSV or JSON.",
            mutating=True,
            external=False,
        ),
        PortalAction(
            "static-deploy",
            "Static Deploy",
            "Deploy a project viewer directory with the Vercel static deploy helper.",
            mutating=True,
            external=True,
        ),
    ]
}


def discover_actions() -> list[dict[str, Any]]:
    return [ACTIONS[name].to_dict() for name in sorted(ACTIONS)]


def run_action(payload: dict[str, Any], *, output_root: Path) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("request body must be a JSON object")

    name = _coerce_str(payload.get("action"), "action", required=True)
    action = ACTIONS.get(name)
    if action is None:
        raise ValueError(f"unsupported portal action: {name}")

    dry_run = _coerce_bool(payload.get("dry_run"))
    mutating = action.mutating and not dry_run
    external = action.external and not dry_run
    if (mutating or external) and not _coerce_bool(payload.get("confirm")):
        raise PermissionError(f"{name} requires confirm=true")

    base = {
        "ok": True,
        "action": name,
        "dry_run": dry_run,
        "mutating": mutating,
        "external": external,
    }

    if name == "approve-starred":
        return {**base, **_approve_starred(payload, output_root=output_root, dry_run=dry_run)}
    if name == "canva-export":
        return {**base, **_canva_export(payload, output_root=output_root, dry_run=dry_run)}
    if name == "notion-export":
        return {**base, **_notion_export(payload, output_root=output_root, dry_run=dry_run)}
    if name == "registry-export":
        return {**base, **_registry_export(payload, output_root=output_root, dry_run=dry_run)}
    if name == "static-deploy":
        return {**base, **_static_deploy(payload, output_root=output_root, dry_run=dry_run)}

    raise ValueError(f"unsupported portal action: {name}")


def _approve_starred(payload: dict[str, Any], *, output_root: Path, dry_run: bool) -> dict[str, Any]:
    from lib import archive

    project = _coerce_str(payload.get("project"), "project", required=True)
    run = _coerce_str(payload.get("run"), "run") or None
    project_dir = _project_dir(output_root, project)

    if dry_run:
        run_dir = _resolve_run_dir(project_dir, run)
        rating_count = _count_starred(output_root, project_dir.name, run_dir.name)
        return {
            "project": project_dir.name,
            "run": run_dir.name,
            "approved_count": rating_count,
            "approved_dir": str((project_dir / "approved").resolve(strict=False)),
            "viewer_path": str((project_dir / "approved" / "viewer.html").resolve(strict=False)),
        }

    approved_count = archive.approve(project, run=run, output_root=output_root)
    viewer_path = ""
    approved_dir = project_dir / "approved"
    if approved_dir.exists():
        viewer_path = str(archive.build_approved_viewer(project, output_root=output_root))
    result = {
        "project": project_dir.name,
        "run": run or "latest",
        "approved_count": approved_count,
        "approved_dir": str(approved_dir.resolve(strict=False)),
        "viewer_path": viewer_path,
    }
    if approved_count > 0:
        result.update(_refresh_registry(output_root, reason="approve-starred"))
    return result


def _canva_export(payload: dict[str, Any], *, output_root: Path, dry_run: bool) -> dict[str, Any]:
    from lib.exporters import canva

    project = _coerce_str(payload.get("project"), "project", required=True)
    output_dir_raw = _coerce_str(payload.get("output_dir"), "output_dir")
    no_zip = _coerce_bool(payload.get("no_zip"))
    project_dir = output_root / project
    export_dir = Path(output_dir_raw) if output_dir_raw else project_dir / "canva-export"
    result_path = export_dir if no_zip else export_dir.with_suffix(".zip")

    source = canva._resolve_source(project_dir)
    image_count = len(list(source.glob("*.png")))
    if dry_run:
        return {
            "project": project,
            "source": source.name,
            "image_count": image_count,
            "result_path": str(result_path.resolve(strict=False)),
        }

    result = canva.export(
        project,
        output_dir=export_dir if output_dir_raw else None,
        zip=not no_zip,
        output_root=output_root,
    )
    metadata = _stamp_archive_state_for_source(
        output_root,
        project=project,
        source_label=source.name,
        state="canva",
    )
    result_payload = {
        "project": project,
        "source": source.name,
        "image_count": image_count,
        "result_path": str(result.resolve(strict=False)),
        **metadata,
    }
    result_payload.update(_refresh_registry_after_metadata_change(output_root, metadata, reason="canva-export"))
    return result_payload


def _notion_export(payload: dict[str, Any], *, output_root: Path, dry_run: bool) -> dict[str, Any]:
    from lib.exporters import notion

    project = _coerce_str(payload.get("project"), "project", required=True)
    database_id = _coerce_str(payload.get("database_id"), "database_id") or None
    force = _coerce_bool(payload.get("force"))
    try:
        result = notion.export(
            project,
            database_id=database_id,
            output_root=output_root,
            dry_run=dry_run,
            force=force,
        )
    except notion.NotionExportError as e:
        raise RuntimeError(str(e)) from e
    metadata = {}
    if not dry_run and result.get("exported", 0) > 0 and not result.get("errors"):
        metadata = _stamp_archive_state_for_source(
            output_root,
            project=project,
            source_label=str(result.get("source") or ""),
            state="notion",
        )
    result_payload = {
        "project": project,
        "database_id": database_id or "",
        "force": force,
        **result,
        **metadata,
    }
    result_payload.update(_refresh_registry_after_metadata_change(output_root, metadata, reason="notion-export"))
    return result_payload


def _registry_export(payload: dict[str, Any], *, output_root: Path, dry_run: bool) -> dict[str, Any]:
    from lib import registry

    fmt = _coerce_str(payload.get("format"), "format") or "csv"
    if fmt not in {"csv", "json"}:
        raise ValueError("format must be 'csv' or 'json'")

    if dry_run:
        entries = registry._load_registry()
        path = registry.REGISTRY_CSV if fmt == "csv" else registry.REGISTRY_JSON
        return {
            "format": fmt,
            "count": len(entries),
            "path": str(path.resolve(strict=False)),
        }

    refresh = registry.refresh_cache(output_root=output_root, reason="registry-export")
    path = registry.export(format=fmt)
    return {
        "format": fmt,
        "count": refresh["registry_count"],
        "path": str(path.resolve(strict=False)),
        **refresh,
    }


def _static_deploy(payload: dict[str, Any], *, output_root: Path, dry_run: bool) -> dict[str, Any]:
    from lib.deploy import vercel

    project = _coerce_str(payload.get("project"), "project", required=True)
    prod = _coerce_bool(payload.get("prod"))
    viewer_dir_raw = _coerce_str(payload.get("viewer_dir"), "viewer_dir")
    if viewer_dir_raw:
        viewer_dir = Path(viewer_dir_raw)
        resolved_dir = viewer_dir
    else:
        project_dir = output_root / project
        approved = project_dir / "approved"
        resolved_dir = approved if (approved / "viewer.html").exists() else project_dir
    command = ["vercel", "deploy", str(resolved_dir), "--yes"]
    if prod:
        command.append("--prod")
    source_map = _deploy_source_map(output_root, project=project, viewer_dir=resolved_dir)

    if dry_run:
        if not (resolved_dir / "viewer.html").exists():
            raise vercel.ViewerNotFoundError(f"No viewer.html found at {resolved_dir}.")
        return {
            "project": project,
            "prod": prod,
            "viewer_dir": str(resolved_dir.resolve(strict=False)),
            "command": command,
            "url": "",
            "source_mapping": source_map,
        }

    url = vercel.deploy(project, viewer_dir=resolved_dir, prod=prod, dry_run=False)
    metadata = _stamp_archive_state_for_keys(
        output_root,
        keys=source_map["keys"],
        state="deployed",
    )
    result_payload = {
        "project": project,
        "prod": prod,
        "viewer_dir": str(resolved_dir.resolve(strict=False)),
        "command": command,
        "url": url,
        "source_mapping": source_map,
        "metadata_unmapped": not source_map["mapped"],
        **metadata,
    }
    result_payload.update(_refresh_registry_after_metadata_change(output_root, metadata, reason="static-deploy"))
    return result_payload


def _project_dir(output_root: Path, project: str) -> Path:
    candidate = Path(project)
    if candidate.is_absolute():
        return candidate
    return output_root / project


def _refresh_registry(output_root: Path, *, reason: str) -> dict[str, Any]:
    from lib import registry

    return registry.refresh_cache(output_root=output_root, reason=reason)


def _refresh_registry_after_metadata_change(
    output_root: Path,
    metadata: dict[str, Any],
    *,
    reason: str,
) -> dict[str, Any]:
    if metadata.get("metadata_stamped", 0) <= 0:
        return {}
    return _refresh_registry(output_root, reason=reason)


def _resolve_run_dir(project_dir: Path, run: str | None) -> Path:
    if not project_dir.exists():
        raise FileNotFoundError(f"project not found: {project_dir}")
    if run:
        run_dir = project_dir / (run if run.startswith("run-") else f"run-{run}")
        if not run_dir.exists():
            raise FileNotFoundError(f"run not found: {run_dir}")
        return run_dir
    runs = sorted(p for p in project_dir.glob("run-*") if p.is_dir())
    if not runs:
        raise FileNotFoundError(f"no runs found under {project_dir}")
    return runs[-1]


def _count_starred(output_root: Path, project: str, run: str) -> int:
    ratings_file = output_root / "ratings.json"
    if not ratings_file.exists():
        return 0
    try:
        ratings = json.loads(ratings_file.read_text(encoding="utf-8"))
    except Exception:
        return 0
    prefix = f"{project}/{run}/"
    return sum(1 for key, value in ratings.items() if key.startswith(prefix) and value == "star")


def _stamp_archive_state_for_source(
    output_root: Path,
    *,
    project: str,
    source_label: str,
    state: str,
) -> dict[str, Any]:
    keys = _archive_keys_for_source(output_root, project=project, source_label=source_label)
    return _stamp_archive_state_for_keys(output_root, keys=keys, state=state)


def _stamp_archive_state_for_keys(
    output_root: Path,
    *,
    keys: list[str],
    state: str,
) -> dict[str, Any]:
    from lib.archive_metadata import archive_metadata_path, stamp_archive_state

    result = stamp_archive_state(archive_metadata_path(output_root), keys, state)
    return {
        "metadata_state": result["state"],
        "metadata_stamped": result["stamped"],
    }


def _archive_keys_for_source(output_root: Path, *, project: str, source_label: str) -> list[str]:
    project_dir = _project_dir(output_root, project)
    if not source_label:
        return []
    if source_label == "approved":
        return _archive_keys_for_approved(project_dir, project)
    if source_label.startswith("run-"):
        return _archive_keys_for_run(project_dir / source_label, project)
    return []


def _archive_keys_for_approved(project_dir: Path, project: str) -> list[str]:
    index_path = project_dir / "approved" / "index.json"
    if not index_path.exists():
        return []
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    entries = data.get("images", data) if isinstance(data, dict) else data
    if not isinstance(entries, list):
        return []
    keys = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        source_run = _coerce_str(entry.get("source_run"), "source_run")
        original_file = _coerce_str(entry.get("original_file"), "original_file")
        if source_run and original_file:
            keys.append(f"{project}/{source_run}/{original_file}")
    return keys


def _archive_keys_for_run(run_dir: Path, project: str) -> list[str]:
    run_json = run_dir / "run.json"
    if not run_json.exists():
        return []
    try:
        data = json.loads(run_json.read_text(encoding="utf-8"))
    except Exception:
        return []
    images = data.get("images") if isinstance(data.get("images"), list) else []
    keys = []
    for image in images:
        if not isinstance(image, dict):
            continue
        filename = _coerce_str(image.get("file"), "file")
        if filename:
            keys.append(f"{project}/{run_dir.name}/{filename}")
    return keys


def _deploy_source_map(output_root: Path, *, project: str, viewer_dir: Path) -> dict[str, Any]:
    resolved = Path(viewer_dir).resolve(strict=False)
    project_dir = _project_dir(output_root, project).resolve(strict=False)
    approved_dir = (project_dir / "approved").resolve(strict=False)

    if resolved == approved_dir:
        keys = _archive_keys_for_approved(project_dir, project)
        return _source_map_payload(
            kind="approved",
            label="approved",
            keys=keys,
            reason="approved/index.json maps deployed images to source run cards",
        )

    if resolved == project_dir:
        keys = _archive_keys_for_project(project_dir, project)
        return _source_map_payload(
            kind="project",
            label=project,
            keys=keys,
            reason="project viewer maps to all run-* manifest images",
        )

    try:
        relative = resolved.relative_to(project_dir)
    except ValueError:
        return _source_map_payload(
            kind="unmapped",
            label="",
            keys=[],
            reason="viewer directory is outside the project output root",
        )

    if len(relative.parts) == 1 and relative.parts[0].startswith("run-"):
        run_id = relative.parts[0]
        keys = _archive_keys_for_run(project_dir / run_id, project)
        return _source_map_payload(
            kind="run",
            label=run_id,
            keys=keys,
            reason="run viewer maps directly to its run.json image records",
        )

    return _source_map_payload(
        kind="unmapped",
        label="",
        keys=[],
        reason="viewer directory is not project root, approved/, or a run-* directory",
    )


def _archive_keys_for_project(project_dir: Path, project: str) -> list[str]:
    keys = []
    for run_dir in sorted(project_dir.glob("run-*")):
        if run_dir.is_dir():
            keys.extend(_archive_keys_for_run(run_dir, project))
    return keys


def _source_map_payload(
    *,
    kind: str,
    label: str,
    keys: list[str],
    reason: str,
) -> dict[str, Any]:
    if not keys and kind != "unmapped":
        reason = f"{reason}, but no source image keys were found"
    return {
        "mapped": bool(keys),
        "source_kind": kind,
        "source_label": label,
        "reason": reason,
        "key_count": len(keys),
        "keys": keys,
    }


def _coerce_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return False


def _coerce_str(value: object, field: str, *, required: bool = False) -> str:
    if value is None:
        if required:
            raise ValueError(f"{field} is required")
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    text = value.strip()
    if required and not text:
        raise ValueError(f"{field} is required")
    return text

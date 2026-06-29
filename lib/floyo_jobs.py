"""Floyo video pipeline: fill a workflow template, submit it, record a job.

Dry-run-first, mirroring ``lib/video_jobs.py``. ``--execute`` is the only path
that uploads, submits, or downloads.
"""

from __future__ import annotations

import copy
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from lib.jobs import provider_cost_preview, write_manifest
from lib.providers import floyo_provider

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = REPO_ROOT / "config" / "floyo_workflows"
DEFAULT_WORKFLOW = "wan22_endframe"
_FILE_SLOT_TYPES = {"image", "video", "audio_file"}


def load_workflow_template(name: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (workflow_graph, inputmap) for a shipped Floyo workflow."""
    tpl_path = WORKFLOWS_DIR / f"{name}.api.json"
    imap_path = WORKFLOWS_DIR / "inputmaps.json"
    if not tpl_path.is_file():
        available = sorted(p.stem.replace(".api", "") for p in WORKFLOWS_DIR.glob("*.api.json"))
        raise ValueError(f"unknown workflow {name!r}; available: {available}")
    imap = json.loads(imap_path.read_text(encoding="utf-8")).get(name)
    if not imap:
        raise ValueError(f"workflow {name!r} has no inputmap entry")
    return json.loads(tpl_path.read_text(encoding="utf-8")), imap


def patch_workflow(
    tpl: dict[str, Any],
    imap: dict[str, Any],
    slot: str,
    value: str,
    *,
    execute: bool = False,
) -> Any:
    """Apply one slot=value to the workflow per its inputmap, in place."""
    spec = imap.get("slots", {}).get(slot)
    if not spec:
        raise ValueError(f"unknown slot {slot!r}; known: {list(imap.get('slots', {}))}")
    node, field, typ = spec["node"], spec["field"], spec["type"]
    if typ in _FILE_SLOT_TYPES:
        patched = floyo_provider.upload_asset(value, execute=execute)["input_path"]
    elif typ == "audio":
        up = floyo_provider.upload_asset(value, execute=execute)
        patched = floyo_provider.presigned_url(up.get("id", ""), execute=execute)
    elif typ == "int":
        patched = int(value)
    else:
        patched = value
    tpl[node]["inputs"][field] = patched
    return patched


def _count_preview(inputs: dict[str, str], *, execute: bool) -> dict[str, Any]:
    file_inputs = sum(1 for v in inputs.values() if _looks_like_path(v))
    return {
        "planned_provider_jobs": 1,
        "network_calls": (file_inputs + 1) if execute else 0,
        "input_slots": len(inputs),
        "file_uploads": file_inputs if execute else 0,
        "requested_videos": 1,
    }


def _looks_like_path(value: str) -> bool:
    return isinstance(value, str) and ("/" in value or "." in value)


def build_floyo_preview(
    *,
    workflow: str = DEFAULT_WORKFLOW,
    inputs: dict[str, str] | None = None,
    execute: bool = False,
) -> dict[str, Any]:
    inputs = inputs or {}
    load_workflow_template(workflow)  # validates the workflow exists
    counts = _count_preview(inputs, execute=execute)
    cost = provider_cost_preview(
        provider="Floyo",
        model=workflow,
        counts=counts,
        dry_run=not execute,
        note="Floyo FloTime billing is not estimated locally; use provider billing for exact charges.",
    )
    return {
        "kind": "floyo-video",
        "provider": "Floyo",
        "workflow": workflow,
        "execute": execute,
        "dry_run": not execute,
        "count_preview": counts,
        "cost_estimate": cost,
        "pricing_note": cost["note"],
    }


def plan_floyo_generation(
    *,
    workflow: str = DEFAULT_WORKFLOW,
    inputs: dict[str, str] | None = None,
    project: str = "floyo",
    name: str = "",
    output_root: Path | None = None,
    execute: bool = False,
    wait: bool = True,
    max_attempts: int = 120,
) -> dict[str, Any]:
    inputs = inputs or {}
    tpl, imap = load_workflow_template(workflow)
    tpl = copy.deepcopy(tpl)
    for slot, value in inputs.items():
        patch_workflow(tpl, imap, slot, value, execute=execute)

    output_root = output_root or REPO_ROOT / "output"
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    run_dir = output_root / project / f"floyo-run-{stamp}"
    manifest_path = run_dir / "run.json"
    run_name = name or f"{project} {workflow}"

    counts = _count_preview(inputs, execute=execute)
    cost = provider_cost_preview(
        provider="Floyo",
        model=workflow,
        counts=counts,
        dry_run=not execute,
        note="Floyo FloTime billing is not estimated locally; use provider billing for exact charges.",
    )
    request_input = {"workflow": workflow, "name": run_name, "inputs": inputs, "project": project}
    provider_response = floyo_provider.run_workflow(workflow, tpl, execute=execute)

    job = floyo_provider.create_job(
        kind="floyo-video",
        workflow_name=workflow,
        input=request_input,
        target_output_dir=run_dir,
        manifest_path=manifest_path,
        execute=execute,
        provider_response=provider_response,
        cost_estimate=cost,
    )

    outputs: list[dict[str, Any]] = []
    final_status = job.status
    if execute and wait:
        run_id = str(provider_response.get("id") or "")
        if run_id:
            final = floyo_provider.poll_run(run_id, execute=True, max_attempts=max_attempts)
            final_status = floyo_provider._job_status(final, execute=True)
            for out in floyo_provider.find_outputs(final):
                fn = out.get("file_name") or out.get("filename") or "clip.mp4"
                # Download failures are recorded, not fatal — the run record/id must persist.
                try:
                    url = floyo_provider.output_url(out)
                    if not url and out.get("id"):
                        # Floyo outputs are referenced by file id; resolve a presigned URL.
                        url = floyo_provider.presigned_url(str(out["id"]), execute=True)
                    if not url:
                        outputs.append({"status": "no-url", "file": fn})
                        continue
                    dest = run_dir / f"{workflow}_{run_id}_{fn}"
                    outputs.append(floyo_provider.download_output(url, dest, execute=True))
                except Exception as e:  # noqa: BLE001 - record, don't crash the run
                    outputs.append({"status": "failed", "file": fn, "error": str(e)[:300]})

    manifest = {
        "version": 1,
        "kind": "floyo-video",
        "status": final_status if execute else "dry-run",
        "provider": "Floyo",
        "workflow": workflow,
        "name": run_name,
        "project": project,
        "inputs": inputs,
        "count_preview": counts,
        "cost_estimate": cost,
        "job": job.to_dict(),
        "outputs": outputs,
        "created_at": job.created_at,
    }
    write_manifest(manifest_path, manifest)
    return {
        "ok": True,
        "job": job.to_dict(),
        "manifest": manifest,
        "manifest_path": str(manifest_path),
        "outputs": outputs,
    }

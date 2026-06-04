"""Local job records for long-running or paid media operations."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from lib.media_types import JobRecord

REPO_ROOT = Path(__file__).resolve().parent.parent
JOBS_DIR = REPO_ROOT / "data" / "jobs"


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def new_job_id(kind: str) -> str:
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    clean = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in kind.lower()).strip("-")
    return f"{clean}-{stamp}"


def save_job(record: JobRecord, *, jobs_dir: Path | None = None) -> Path:
    jobs_dir = jobs_dir or JOBS_DIR
    jobs_dir.mkdir(parents=True, exist_ok=True)
    path = jobs_dir / f"{record.id}.json"
    record.updated_at = now_iso()
    path.write_text(json.dumps(record.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def save_job_dict(record: dict[str, Any], *, jobs_dir: Path | None = None) -> Path:
    job_id = str(record.get("id") or "").strip()
    if not job_id:
        raise ValueError("job id is required")
    jobs_dir = jobs_dir or JOBS_DIR
    jobs_dir.mkdir(parents=True, exist_ok=True)
    payload = dict(record)
    payload["updated_at"] = now_iso()
    path = jobs_dir / f"{job_id}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def load_job(job_id: str, *, jobs_dir: Path | None = None) -> dict[str, Any] | None:
    jobs_dir = jobs_dir or JOBS_DIR
    path = jobs_dir / f"{job_id}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def update_job(job_id: str, updates: dict[str, Any], *, jobs_dir: Path | None = None) -> dict[str, Any]:
    record = load_job(job_id, jobs_dir=jobs_dir)
    if record is None:
        raise ValueError(f"job not found: {job_id}")
    record.update(updates)
    save_job_dict(record, jobs_dir=jobs_dir)
    return record


def provider_cost_preview(
    *,
    provider: str,
    model: str,
    counts: dict[str, Any],
    dry_run: bool,
    note: str,
) -> dict[str, Any]:
    return {
        "currency": "USD",
        "amount": 0.0 if dry_run else None,
        "estimated": dry_run,
        "basis": "dry_run_no_provider_spend" if dry_run else "provider_billing_required",
        "provider": provider,
        "model": model,
        "counts": counts,
        "note": note,
    }


def list_jobs(*, jobs_dir: Path | None = None) -> list[dict[str, Any]]:
    jobs_dir = jobs_dir or JOBS_DIR
    if not jobs_dir.exists():
        return []
    out = []
    for path in sorted(jobs_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(data, dict):
            out.append(data)
    return sorted(out, key=lambda item: item.get("created_at", ""), reverse=True)


def write_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

"""Scheduled regeneration of evergreen image batches.

Loads a JSON config describing batches to regenerate on a cadence and
dispatches them to the existing `generate.py` batch pipeline via subprocess
(loose coupling — this module never imports from `generate.py`).

Schema (config/scheduled-regen.json):

    [
      {
        "name": "upgrade-newsletter-heroes",
        "prompt_file": "prompts/upgrade/newsletter-heroes.md",
        "output_dir": "output/upgrade-newsletter",
        "model": "gpt-image-2",
        "style": "upgrade",
        "interval_days": 30,
        "notify": true
      }
    ]
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = ("name", "prompt_file", "output_dir", "interval_days")


@dataclass
class RegenJob:
    name: str
    prompt_file: str
    output_dir: str
    interval_days: int
    model: str | None = None
    style: str | None = None
    notify: bool = False
    workers: int = 2


def load_config(path: Path) -> list[RegenJob]:
    """Load + validate scheduled-regen config.

    Raises:
        FileNotFoundError: config file missing
        ValueError: malformed config or missing required fields
    """
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(f"Config must be a JSON array, got {type(raw).__name__}")

    jobs: list[RegenJob] = []
    for i, entry in enumerate(raw):
        if not isinstance(entry, dict):
            raise ValueError(f"Entry {i} must be an object, got {type(entry).__name__}")
        # Skip leading "_comment"-style keys at the top of objects? No — entries are objects in a list.
        missing = [f for f in REQUIRED_FIELDS if f not in entry]
        if missing:
            raise ValueError(
                f"Entry {i} ({entry.get('name', '?')}) missing required fields: {missing}"
            )
        if not isinstance(entry["interval_days"], int) or entry["interval_days"] <= 0:
            raise ValueError(
                f"Entry {i} ({entry['name']}): interval_days must be a positive int"
            )
        jobs.append(
            RegenJob(
                name=entry["name"],
                prompt_file=entry["prompt_file"],
                output_dir=entry["output_dir"],
                interval_days=entry["interval_days"],
                model=entry.get("model"),
                style=entry.get("style"),
                notify=bool(entry.get("notify", False)),
                workers=int(entry.get("workers", 2)),
            )
        )
    return jobs


def latest_run_age_days(output_dir: Path, *, now: datetime | None = None) -> int | None:
    """Return age in days of the most recent `run-*/` under `output_dir`.

    Returns None if no `run-*/` exists (or `output_dir` doesn't exist).
    """
    if not output_dir.exists() or not output_dir.is_dir():
        return None
    runs = [p for p in output_dir.glob("run-*") if p.is_dir()]
    if not runs:
        return None
    latest_mtime = max(p.stat().st_mtime for p in runs)
    now = now or datetime.now(timezone.utc)
    age_seconds = now.timestamp() - latest_mtime
    return int(age_seconds // 86400)


def due_jobs(
    jobs: list[RegenJob],
    *,
    now: datetime | None = None,
    repo_root: Path | None = None,
) -> list[RegenJob]:
    """Return jobs whose latest run is older than `interval_days` (or never run)."""
    repo_root = repo_root or Path.cwd()
    now = now or datetime.now(timezone.utc)
    out: list[RegenJob] = []
    for job in jobs:
        out_dir = (repo_root / job.output_dir).resolve()
        age = latest_run_age_days(out_dir, now=now)
        if age is None or age >= job.interval_days:
            out.append(job)
    return out


def build_command(job: RegenJob, *, repo_root: Path) -> list[str]:
    """Construct the argv list for invoking generate.py for this job."""
    cmd: list[str] = [
        sys.executable,
        str(repo_root / "generate.py"),
        "-f", job.prompt_file,
        "-d", job.output_dir,
        "-w", str(job.workers),
    ]
    if job.style:
        cmd.extend(["--style", job.style])
    if job.model:
        cmd.extend(["-m", job.model])
    return cmd


def run_job(
    job: RegenJob,
    *,
    repo_root: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Invoke the generate.py batch pipeline for `job`.

    Uses subprocess to keep regen loosely coupled from the generate module.
    Returns a summary dict suitable for JSON output / notifications.
    """
    repo_root = repo_root or Path(__file__).resolve().parent.parent
    cmd = build_command(job, repo_root=repo_root)

    summary: dict[str, Any] = {
        "name": job.name,
        "command": cmd,
        "dry_run": dry_run,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }

    if dry_run:
        summary["status"] = "dry-run"
        return summary

    result = subprocess.run(cmd, cwd=str(repo_root))
    summary["returncode"] = result.returncode
    summary["status"] = "ok" if result.returncode == 0 else "failed"
    summary["finished_at"] = datetime.now(timezone.utc).isoformat()
    return summary

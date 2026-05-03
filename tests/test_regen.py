"""Tests for lib/regen.py — scheduled regeneration."""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.regen import (
    RegenJob,
    build_command,
    due_jobs,
    latest_run_age_days,
    load_config,
    run_job,
)


SAMPLE_CONFIG = [
    {
        "name": "newsletter-heroes",
        "prompt_file": "prompts/upgrade/newsletter-heroes.md",
        "output_dir": "output/upgrade-newsletter",
        "model": "gpt-image-2",
        "style": "upgrade",
        "interval_days": 30,
        "notify": True,
    },
    {
        "name": "minimal-job",
        "prompt_file": "prompts/x.md",
        "output_dir": "output/x",
        "interval_days": 7,
    },
]


def test_load_config_valid(tmp_path: Path) -> None:
    cfg = tmp_path / "scheduled-regen.json"
    cfg.write_text(json.dumps(SAMPLE_CONFIG), encoding="utf-8")

    jobs = load_config(cfg)

    assert len(jobs) == 2
    assert jobs[0].name == "newsletter-heroes"
    assert jobs[0].model == "gpt-image-2"
    assert jobs[0].style == "upgrade"
    assert jobs[0].interval_days == 30
    assert jobs[0].notify is True
    assert jobs[0].workers == 2  # default
    # Minimal entry — optional fields are None / defaults
    assert jobs[1].name == "minimal-job"
    assert jobs[1].model is None
    assert jobs[1].style is None
    assert jobs[1].notify is False


def test_load_config_invalid_raises(tmp_path: Path) -> None:
    cfg = tmp_path / "bad.json"
    cfg.write_text(json.dumps([{"name": "incomplete"}]), encoding="utf-8")
    with pytest.raises(ValueError, match="missing required fields"):
        load_config(cfg)

    cfg.write_text(json.dumps({"not": "a list"}), encoding="utf-8")
    with pytest.raises(ValueError, match="JSON array"):
        load_config(cfg)

    cfg.write_text(
        json.dumps([{
            "name": "bad-interval",
            "prompt_file": "p.md",
            "output_dir": "o/",
            "interval_days": -1,
        }]),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="interval_days"):
        load_config(cfg)


def test_load_config_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "nope.json")


def test_latest_run_age_returns_none_for_no_runs(tmp_path: Path) -> None:
    # Empty dir
    assert latest_run_age_days(tmp_path) is None
    # Non-existent dir
    assert latest_run_age_days(tmp_path / "missing") is None
    # Dir with only non-matching subdirs
    (tmp_path / "other").mkdir()
    assert latest_run_age_days(tmp_path) is None


def test_latest_run_age_finds_recent_run(tmp_path: Path) -> None:
    run_dir = tmp_path / "run-2026-04-01"
    run_dir.mkdir()
    # Backdate mtime to 5 days ago
    five_days_ago = time.time() - (5 * 86400)
    os.utime(run_dir, (five_days_ago, five_days_ago))

    age = latest_run_age_days(tmp_path)
    assert age in (4, 5)  # tolerance for clock drift


def test_due_jobs_filters_by_interval(tmp_path: Path) -> None:
    # Project A: never run → due
    proj_a = tmp_path / "output" / "a"
    proj_a.mkdir(parents=True)
    # Project B: run 2 days ago, interval 30 → not due
    proj_b = tmp_path / "output" / "b"
    proj_b.mkdir(parents=True)
    run_b = proj_b / "run-recent"
    run_b.mkdir()
    two_days_ago = time.time() - (2 * 86400)
    os.utime(run_b, (two_days_ago, two_days_ago))
    # Project C: run 40 days ago, interval 30 → due
    proj_c = tmp_path / "output" / "c"
    proj_c.mkdir(parents=True)
    run_c = proj_c / "run-old"
    run_c.mkdir()
    forty_days_ago = time.time() - (40 * 86400)
    os.utime(run_c, (forty_days_ago, forty_days_ago))

    jobs = [
        RegenJob(name="a", prompt_file="p.md", output_dir="output/a", interval_days=30),
        RegenJob(name="b", prompt_file="p.md", output_dir="output/b", interval_days=30),
        RegenJob(name="c", prompt_file="p.md", output_dir="output/c", interval_days=30),
    ]
    due = due_jobs(jobs, repo_root=tmp_path)
    names = {j.name for j in due}
    assert names == {"a", "c"}


def test_build_command_includes_all_flags(tmp_path: Path) -> None:
    job = RegenJob(
        name="x",
        prompt_file="prompts/x.md",
        output_dir="output/x",
        interval_days=30,
        model="gpt-image-2",
        style="upgrade",
        workers=4,
    )
    cmd = build_command(job, repo_root=tmp_path)
    assert cmd[0] == sys.executable
    assert cmd[1] == str(tmp_path / "generate.py")
    assert "-f" in cmd and "prompts/x.md" in cmd
    assert "-d" in cmd and "output/x" in cmd
    assert "--style" in cmd and "upgrade" in cmd
    assert "-m" in cmd and "gpt-image-2" in cmd
    assert "-w" in cmd and "4" in cmd


def test_build_command_omits_optional_when_unset(tmp_path: Path) -> None:
    job = RegenJob(
        name="x",
        prompt_file="prompts/x.md",
        output_dir="output/x",
        interval_days=30,
    )
    cmd = build_command(job, repo_root=tmp_path)
    assert "--style" not in cmd
    assert "-m" not in cmd


def test_run_job_dry_run_returns_command_without_executing(tmp_path: Path) -> None:
    job = RegenJob(
        name="x",
        prompt_file="prompts/x.md",
        output_dir="output/x",
        interval_days=30,
        model="gpt-image-2",
        style="upgrade",
    )
    summary = run_job(job, repo_root=tmp_path, dry_run=True)

    assert summary["status"] == "dry-run"
    assert summary["dry_run"] is True
    assert summary["name"] == "x"
    cmd = summary["command"]
    assert cmd[0] == sys.executable
    assert "generate.py" in cmd[1]
    assert cmd[2:] == [
        "-f", "prompts/x.md",
        "-d", "output/x",
        "-w", "2",
        "--style", "upgrade",
        "-m", "gpt-image-2",
    ]
    # No subprocess executed → no returncode key
    assert "returncode" not in summary

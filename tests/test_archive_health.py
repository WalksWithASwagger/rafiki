from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from lib.archive_health import archive_health_report


def _write_run(run_dir: Path, images: list[dict]) -> None:
    run_dir.mkdir(parents=True)
    (run_dir / "run.json").write_text(
        json.dumps({"model": "gpt-image-2", "images": images}),
        encoding="utf-8",
    )


def test_archive_health_reports_missing_images_and_sidecar_orphans(tmp_path: Path):
    output_root = tmp_path / "output"
    run_dir = output_root / "demo" / "run-20260520-120000"
    _write_run(
        run_dir,
        [
            {"file": "present.png", "prompt": "present"},
            {"file": "missing.png", "prompt": "missing"},
        ],
    )
    (run_dir / "present.png").write_bytes(b"png")
    (output_root / "ratings.json").write_text(
        json.dumps({
            "demo/run-20260520-120000/present.png": "star",
            "demo/run-old/missing.png": "reject",
        }),
        encoding="utf-8",
    )
    (output_root / "feedback.json").write_text(
        json.dumps({"version": 1, "items": {"demo/run-old/missing.png": {"status": "blocked"}}}),
        encoding="utf-8",
    )
    (output_root / "archive-metadata.json").write_text(
        json.dumps({"version": 1, "items": {"demo/run-old/missing.png": {"title": "Old"}}}),
        encoding="utf-8",
    )

    report = archive_health_report(output_root)

    assert report["ok"] is False
    assert report["summary"]["runs"] == 1
    assert report["summary"]["manifest_images"] == 2
    assert report["summary"]["present_images"] == 1
    assert report["summary"]["missing_images"] == 1
    assert report["missing_images"][0]["key"] == "demo/run-20260520-120000/missing.png"
    assert report["orphaned"]["ratings"] == ["demo/run-old/missing.png"]
    assert report["orphaned"]["feedback"] == ["demo/run-old/missing.png"]
    assert report["orphaned"]["metadata"] == ["demo/run-old/missing.png"]
    assert report["summary"]["cleanup_risk_items"] == 4


def test_archive_health_reports_malformed_runs_and_duplicate_names(tmp_path: Path):
    output_root = tmp_path / "output"
    first = output_root / "demo" / "run-20260520-120000"
    second = output_root / "demo" / "run-20260520-130000"
    _write_run(first, [{"file": "hero.png"}])
    _write_run(second, [{"file": "hero.png"}])
    (first / "hero.png").write_bytes(b"png")
    (second / "hero.png").write_bytes(b"png")
    bad = output_root / "demo" / "run-bad"
    bad.mkdir(parents=True)
    (bad / "run.json").write_text("{bad json", encoding="utf-8")

    report = archive_health_report(output_root)

    assert report["summary"]["duplicate_filename_groups"] == 1
    assert report["duplicate_filenames"][0]["basename"] == "hero.png"
    assert report["malformed_runs"][0]["run"] == "run-bad"


def test_archive_health_cli_emits_json(tmp_path: Path):
    output_root = tmp_path / "output"
    run_dir = output_root / "demo" / "run-20260520-120000"
    _write_run(run_dir, [{"file": "hero.png"}])
    (run_dir / "hero.png").write_bytes(b"png")

    result = subprocess.run(
        [sys.executable, "generate.py", "archive-health", "--output-dir", str(output_root), "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["ok"] is True
    assert payload["summary"]["present_images"] == 1

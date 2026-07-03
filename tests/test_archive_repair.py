from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from lib.archive_health import archive_health_report
from lib.archive_repair import repair_archive


def _write_run(run_dir: Path, images: list[dict], *, write_files: bool = True) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    if write_files:
        for index, image in enumerate(images, start=1):
            if image.get("file"):
                (run_dir / image["file"]).write_bytes(f"image-{index}".encode("utf-8"))
    (run_dir / "run.json").write_text(
        json.dumps({
            "model": "gpt-image-2",
            "timestamp": "2026-01-01T10:00:00",
            "images": images,
        }),
        encoding="utf-8",
    )


def test_archive_repair_dry_run_plans_without_mutating(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    run_dir = output_root / "demo" / "run-1"
    _write_run(
        run_dir,
        [{"file": "present.png"}, {"file": "missing.png"}],
        write_files=False,
    )
    (run_dir / "present.png").write_bytes(b"present")

    result = repair_archive(output_root, backup_dir=tmp_path / "backup")

    assert result["mutates"] is False
    assert result["counts"]["missing_records"] == 1
    assert result["counts"]["run_json_rewrites"] == 1
    assert not (tmp_path / "backup").exists()
    assert len(json.loads((run_dir / "run.json").read_text())["images"]) == 2


def test_archive_repair_apply_quarantines_empty_missing_run_and_removes_orphans(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "output"
    run_dir = output_root / "demo" / "run-empty"
    _write_run(run_dir, [{"file": "missing.png"}], write_files=False)
    (output_root / "ratings.json").write_text(
        json.dumps({
            "demo/run-empty/missing.png": "star",
            "demo/old/orphan.png": "reject",
        }),
        encoding="utf-8",
    )
    backup_dir = tmp_path / "repair-backup"

    result = repair_archive(
        output_root,
        apply=True,
        backup_dir=backup_dir,
        rebuild_registry=False,
    )

    assert result["mutates"] is True
    assert result["counts"]["runs_quarantined"] == 1
    assert not run_dir.exists()
    assert (backup_dir / "quarantine" / "runs" / "demo" / "run-empty").exists()
    assert (backup_dir / "health-before.json").exists()
    assert (backup_dir / "repair-plan.json").exists()
    ratings = json.loads((output_root / "ratings.json").read_text(encoding="utf-8"))
    assert "demo/old/orphan.png" not in ratings


def test_archive_repair_synthesizes_manifest_for_malformed_run_with_images(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "output"
    run_dir = output_root / "demo" / "run-missing-json"
    run_dir.mkdir(parents=True)
    (run_dir / "hero.png").write_bytes(b"hero")

    result = repair_archive(
        output_root,
        apply=True,
        backup_dir=tmp_path / "backup",
        rebuild_registry=False,
    )

    assert result["counts"]["malformed_runs_synthesized"] == 1
    data = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    assert data["archive_repair_synthesized"] is True
    assert data["images"][0]["file"] == "hero.png"


def test_archive_repair_quarantines_malformed_empty_run(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    run_dir = output_root / "demo" / "run-empty"
    run_dir.mkdir(parents=True)
    backup_dir = tmp_path / "backup"

    result = repair_archive(
        output_root,
        apply=True,
        backup_dir=backup_dir,
        rebuild_registry=False,
    )

    assert result["counts"]["runs_quarantined"] == 1
    assert not run_dir.exists()
    assert (backup_dir / "quarantine" / "runs" / "demo" / "run-empty").exists()


def test_archive_repair_quarantines_only_exact_duplicate_files(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    first = output_root / "demo" / "run-1"
    second = output_root / "demo" / "run-2"
    _write_run(first, [{"file": "hero.png"}], write_files=False)
    _write_run(
        second,
        [{"file": "hero.png"}, {"file": "keeper.png"}],
        write_files=False,
    )
    (first / "hero.png").write_bytes(b"same")
    (second / "hero.png").write_bytes(b"same")
    (second / "keeper.png").write_bytes(b"different")
    (output_root / "ratings.json").write_text(
        json.dumps({"demo/run-1/hero.png": "star"}),
        encoding="utf-8",
    )
    backup_dir = tmp_path / "backup"

    result = repair_archive(
        output_root,
        apply=True,
        backup_dir=backup_dir,
        rebuild_registry=False,
    )

    assert result["counts"]["duplicate_files_quarantined"] == 1
    assert (first / "hero.png").exists()
    assert not (second / "hero.png").exists()
    assert (second / "keeper.png").exists()
    assert (
        backup_dir
        / "quarantine"
        / "duplicate-files"
        / "demo"
        / "run-2"
        / "hero.png"
    ).exists()
    images = json.loads((second / "run.json").read_text(encoding="utf-8"))["images"]
    assert [image["file"] for image in images] == ["keeper.png"]


def test_archive_repair_keeps_same_name_non_identical_files(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    first = output_root / "demo" / "run-1"
    second = output_root / "demo" / "run-2"
    _write_run(first, [{"file": "hero.png"}], write_files=False)
    _write_run(second, [{"file": "hero.png"}], write_files=False)
    (first / "hero.png").write_bytes(b"first")
    (second / "hero.png").write_bytes(b"second")

    result = repair_archive(output_root, backup_dir=tmp_path / "backup")

    assert result["counts"]["exact_duplicate_files"] == 0
    assert (first / "hero.png").exists()
    assert (second / "hero.png").exists()
    assert archive_health_report(output_root)["summary"]["duplicate_filename_groups"] == 1


def test_archive_repair_cli_dry_run_json(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    run_dir = output_root / "demo" / "run-1"
    _write_run(run_dir, [{"file": "missing.png"}], write_files=False)

    result = subprocess.run(
        [
            sys.executable,
            "generate.py",
            "archive-repair",
            "--output-dir",
            str(output_root),
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["mutates"] is False
    assert payload["counts"]["missing_records"] == 1
    assert not (output_root / ".rafiki-cleanup").exists()

"""Tests for lib.exporters.canva — Canva CSV/ZIP handoff."""

from __future__ import annotations

import csv
import json
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.exporters import canva  # noqa: E402


PNG_HEADER = b"\x89PNG\r\n\x1a\n"  # enough for "is this a PNG?" smoke checks


def _make_run(project_dir: Path, run_id: str, images: list[dict], aspect: str = "16:9") -> Path:
    run_dir = project_dir / f"run-{run_id}"
    run_dir.mkdir(parents=True)
    for img in images:
        (run_dir / img["file"]).write_bytes(PNG_HEADER + b"fakepngdata")
    (run_dir / "run.json").write_text(json.dumps({
        "model": "gpt-image-2",
        "aspect_ratio": aspect,
        "style": "bcai",
        "prompt_file": "prompts/test/example.md",
        "run_id": run_id,
        "images": images,
    }), encoding="utf-8")
    return run_dir


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    output_root = tmp_path / "output"
    project = output_root / "test-project"
    _make_run(project, "20260101-100000", [
        {"name": "First Image", "prompt": "a forest", "file": "01-first-image.png", "ok": True},
        {"name": "Second Image", "prompt": "a river", "file": "02-second-image.png", "ok": True},
    ])
    return output_root


def test_export_creates_images_dir_and_csv(project_root: Path):
    canva.export("test-project", output_root=project_root, zip=False)
    export_dir = project_root / "test-project" / "canva-export"
    assert (export_dir / "images").is_dir()
    assert (export_dir / "images" / "01-first-image.png").exists()
    assert (export_dir / "images" / "02-second-image.png").exists()
    assert (export_dir / "assets.csv").is_file()


def test_csv_has_expected_columns(project_root: Path):
    canva.export("test-project", output_root=project_root, zip=False)
    csv_path = project_root / "test-project" / "canva-export" / "assets.csv"
    with csv_path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        assert reader.fieldnames == canva.CSV_COLUMNS
        rows = list(reader)
    assert len(rows) == 2
    assert rows[0]["filename"] == "01-first-image.png"
    assert rows[0]["title"] == "First Image"
    assert rows[0]["aspect_ratio"] == "16:9"
    assert rows[0]["prompt"] == "a forest"
    assert rows[0]["caption"] == ""  # no caption source for plain projects


def test_csv_handles_commas_in_captions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    output_root = tmp_path / "output"
    project = output_root / "rap-thing"
    _make_run(project, "20260101-100000", [
        {"name": "Tricky", "prompt": "p, with, commas", "file": "01-tricky.png", "ok": True},
    ])

    # Point the RAP metadata loader at a temp file with caption containing commas.
    rap_path = tmp_path / "rap-viewer-data.json"
    rap_path.write_text(json.dumps([{
        "slug": "01-tricky",
        "title": "Tricky, Indeed",
        "caption": "Commas, quotes \"inside\", and newlines\nall in one cell.",
        "week": 1,
        "social": "Hashtags, more commas, #ResponsibleAI",
    }]), encoding="utf-8")
    monkeypatch.setattr(canva, "RAP_DATA_PATH", rap_path)

    canva.export("rap-thing", output_root=output_root, zip=False)
    csv_path = output_root / "rap-thing" / "canva-export" / "assets.csv"

    with csv_path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 1
    row = rows[0]
    assert row["title"] == "Tricky, Indeed"
    assert row["caption"] == "Commas, quotes \"inside\", and newlines\nall in one cell."
    assert row["social_post"] == "Hashtags, more commas, #ResponsibleAI"
    assert row["week"] == "1"
    assert row["prompt"] == "p, with, commas"


def test_export_zips_by_default(project_root: Path):
    result = canva.export("test-project", output_root=project_root)
    assert result.suffix == ".zip"
    assert result.exists()
    with zipfile.ZipFile(result) as zf:
        names = zf.namelist()
    assert any(n.endswith("assets.csv") for n in names)
    assert any(n.endswith("01-first-image.png") for n in names)
    assert any(n.endswith("02-second-image.png") for n in names)


def test_export_no_zip_flag_skips_zip(project_root: Path):
    result = canva.export("test-project", output_root=project_root, zip=False)
    assert result.is_dir()
    assert result.suffix != ".zip"
    assert not result.with_suffix(".zip").exists()


def test_prefers_approved_over_runs(tmp_path: Path):
    output_root = tmp_path / "output"
    project = output_root / "test-project"
    _make_run(project, "20260101-100000", [
        {"name": "From Run", "prompt": "x", "file": "from-run.png", "ok": True},
    ])
    approved = project / "approved"
    approved.mkdir()
    (approved / "from-approved.png").write_bytes(PNG_HEADER + b"approveddata")

    canva.export("test-project", output_root=output_root, zip=False)
    images_dir = project / "canva-export" / "images"
    assert (images_dir / "from-approved.png").exists()
    assert not (images_dir / "from-run.png").exists()

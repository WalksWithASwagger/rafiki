"""Tests for lib/archive.py — approve, clean, build_approved_viewer."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from lib import archive  # noqa: E402


def _make_run(
    output_root: Path,
    project: str,
    run_id: str,
    images: list[dict],
    *,
    age_seconds: float | None = None,
) -> Path:
    """Create output/<project>/run-<run_id>/ with PNG files + run.json."""
    run_dir = output_root / project / f"run-{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)
    for img in images:
        (run_dir / img["file"]).write_bytes(b"fake-png-bytes")
    (run_dir / "run.json").write_text(
        json.dumps({
            "model": "gemini-2.5-flash-image",
            "aspect_ratio": "16:9",
            "style": "kk",
            "prompt_file": f"prompts/{project}.md",
            "timestamp": "2026-05-01 12:00",
            "run_id": run_id,
            "images": images,
        }),
        encoding="utf-8",
    )
    if age_seconds is not None:
        old = time.time() - age_seconds
        for p in run_dir.rglob("*"):
            import os
            os.utime(p, (old, old))
        import os
        os.utime(run_dir, (old, old))
    return run_dir


def _set_ratings(output_root: Path, ratings: dict[str, str]) -> None:
    (output_root / "ratings.json").write_text(json.dumps(ratings), encoding="utf-8")


def test_approve_copies_starred_images_to_approved_dir(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    project = "test-project"
    _make_run(output_root, project, "20260501-120000", [
        {"name": "A", "file": "01-a.png", "prompt": "a prompt"},
        {"name": "B", "file": "02-b.png", "prompt": "b prompt"},
        {"name": "C", "file": "03-c.png", "prompt": "c prompt"},
    ])
    _set_ratings(output_root, {
        f"{project}/run-20260501-120000/01-a.png": "star",
        f"{project}/run-20260501-120000/03-c.png": "star",
        f"{project}/run-20260501-120000/02-b.png": "reject",
    })

    n = archive.approve(project, output_root=output_root)

    assert n == 2
    approved = output_root / project / "approved"
    assert (approved / "01-a.png").exists()
    assert (approved / "03-c.png").exists()
    assert not (approved / "02-b.png").exists()


def test_approve_writes_index_json_with_provenance(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    project = "test-project"
    _make_run(output_root, project, "20260501-120000", [
        {"name": "Alpha", "file": "01-alpha.png", "prompt": "alpha prompt text"},
    ])
    _set_ratings(output_root, {
        f"{project}/run-20260501-120000/01-alpha.png": "star",
    })

    archive.approve(project, output_root=output_root)

    index = json.loads(
        (output_root / project / "approved" / "index.json").read_text(encoding="utf-8")
    )
    assert len(index["images"]) == 1
    entry = index["images"][0]
    assert entry["slug"] == "01-alpha.png"
    assert entry["source_run"] == "run-20260501-120000"
    assert entry["original_file"] == "01-alpha.png"
    assert entry["prompt"] == "alpha prompt text"
    assert entry["name"] == "Alpha"
    assert "approved_at" in entry
    assert entry["model"] == "gemini-2.5-flash-image"


def test_approve_is_idempotent(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    project = "test-project"
    _make_run(output_root, project, "20260501-120000", [
        {"name": "A", "file": "01-a.png", "prompt": "p"},
    ])
    _set_ratings(output_root, {
        f"{project}/run-20260501-120000/01-a.png": "star",
    })

    assert archive.approve(project, output_root=output_root) == 1
    assert archive.approve(project, output_root=output_root) == 0
    index = json.loads(
        (output_root / project / "approved" / "index.json").read_text(encoding="utf-8")
    )
    assert len(index["images"]) == 1


def test_approve_dedupes_collision_with_run_id_prefix(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    project = "test-project"
    _make_run(output_root, project, "20260501-120000", [
        {"name": "A", "file": "01-a.png", "prompt": "p1"},
    ])
    _make_run(output_root, project, "20260502-120000", [
        {"name": "A2", "file": "01-a.png", "prompt": "p2"},
    ])
    _set_ratings(output_root, {
        f"{project}/run-20260501-120000/01-a.png": "star",
        f"{project}/run-20260502-120000/01-a.png": "star",
    })

    archive.approve(project, run="20260501-120000", output_root=output_root)
    archive.approve(project, run="20260502-120000", output_root=output_root)

    approved = output_root / project / "approved"
    assert (approved / "01-a.png").exists()
    assert (approved / "20260502-120000__01-a.png").exists()


def test_clean_dry_run_returns_runs_without_deleting(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    project = "test-project"
    r1 = _make_run(output_root, project, "20260501-120000", [
        {"name": "A", "file": "01-a.png", "prompt": "p"},
    ])
    r2 = _make_run(output_root, project, "20260502-120000", [
        {"name": "B", "file": "01-b.png", "prompt": "p"},
    ])

    deleted = archive.clean(project, dry_run=True, output_root=output_root)

    assert set(deleted) == {r1, r2}
    assert r1.exists()
    assert r2.exists()


def test_clean_keep_approved_skips_runs_with_unstarred_images(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    project = "test-project"
    # Run 1: both images approved → deletable
    r1 = _make_run(output_root, project, "20260501-120000", [
        {"name": "A", "file": "01-a.png", "prompt": "p"},
        {"name": "B", "file": "02-b.png", "prompt": "p"},
    ])
    # Run 2: only one image approved → must be kept
    r2 = _make_run(output_root, project, "20260502-120000", [
        {"name": "C", "file": "01-c.png", "prompt": "p"},
        {"name": "D", "file": "02-d.png", "prompt": "p"},
    ])
    _set_ratings(output_root, {
        f"{project}/run-20260501-120000/01-a.png": "star",
        f"{project}/run-20260501-120000/02-b.png": "star",
        f"{project}/run-20260502-120000/01-c.png": "star",
    })
    archive.approve(project, run="20260501-120000", output_root=output_root)
    archive.approve(project, run="20260502-120000", output_root=output_root)

    deleted = archive.clean(
        project, keep_approved=True, dry_run=True, output_root=output_root,
    )

    assert deleted == [r1]
    assert r2.exists()


def test_clean_actually_deletes_when_not_dry_run(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    project = "test-project"
    r1 = _make_run(output_root, project, "20260501-120000", [
        {"name": "A", "file": "01-a.png", "prompt": "p"},
    ])

    deleted = archive.clean(project, dry_run=False, output_root=output_root)

    assert deleted == [r1]
    assert not r1.exists()


def test_clean_older_than_days_filters_by_age(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    project = "test-project"
    old = _make_run(output_root, project, "20260301-120000",
                    [{"name": "A", "file": "01-a.png", "prompt": "p"}],
                    age_seconds=60 * 60 * 24 * 60)  # 60 days old
    fresh = _make_run(output_root, project, "20260502-120000",
                      [{"name": "B", "file": "01-b.png", "prompt": "p"}])

    deleted = archive.clean(
        project, older_than_days=30, dry_run=True, output_root=output_root,
    )

    assert deleted == [old]
    assert fresh.exists()


def test_build_approved_viewer_writes_html(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    project = "test-project"
    _make_run(output_root, project, "20260501-120000", [
        {"name": "A", "file": "01-a.png", "prompt": "alpha"},
    ])
    _set_ratings(output_root, {
        f"{project}/run-20260501-120000/01-a.png": "star",
    })
    archive.approve(project, output_root=output_root)

    viewer = archive.build_approved_viewer(project, output_root=output_root)

    assert viewer.exists()
    assert viewer.name == "viewer.html"
    assert viewer.parent.name == "approved"
    html = viewer.read_text(encoding="utf-8")
    assert "01-a.png" in html


def test_approve_raises_when_project_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        archive.approve("nope", output_root=tmp_path / "output")


def test_approve_raises_when_no_runs(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    (output_root / "empty-project").mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        archive.approve("empty-project", output_root=output_root)

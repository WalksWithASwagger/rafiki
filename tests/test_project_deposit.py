"""Tests for depositing generated outputs into the project that owns them."""

from __future__ import annotations

from pathlib import Path

from lib.media_roots import MediaRoot, deposit_outputs_into_project, project_media_dir


def _roots(tmp_path: Path) -> dict[str, MediaRoot]:
    return {"gg": MediaRoot(key="gg", path=tmp_path, importer="generic", enabled=True)}


def test_project_media_dir_resolves_root(tmp_path):
    roots = _roots(tmp_path)
    assert project_media_dir("gg", "clips", roots=roots) == tmp_path / "clips"
    assert project_media_dir("unknown", "clips", roots=roots) is None


def test_deposit_copies_downloaded_outputs(tmp_path, monkeypatch):
    project = tmp_path / "project"
    project.mkdir()
    src = tmp_path / "run" / "clip.mp4"
    src.parent.mkdir()
    src.write_bytes(b"video-bytes")

    monkeypatch.setattr(
        "lib.media_roots.load_media_roots",
        lambda **_: {"gg": MediaRoot(key="gg", path=project, importer="generic", enabled=True)},
    )
    outputs = [
        {"status": "downloaded", "output_path": str(src)},
        {"status": "failed", "url": "x"},  # skipped
        {"status": "no-url", "file": "y"},  # skipped
    ]
    deposit_outputs_into_project(outputs, "gg", "clips")

    deposited = project / "clips" / "clip.mp4"
    assert deposited.exists() and deposited.read_bytes() == b"video-bytes"
    assert outputs[0]["project_path"] == str(deposited)
    assert "project_path" not in outputs[1]


def test_deposit_noop_for_unknown_project(tmp_path, monkeypatch):
    monkeypatch.setattr("lib.media_roots.load_media_roots", lambda **_: {})
    outputs = [{"status": "downloaded", "output_path": str(tmp_path / "x.mp4")}]
    deposit_outputs_into_project(outputs, "nope", "clips")
    assert "project_path" not in outputs[0]

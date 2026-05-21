"""Tests for portal curation/export action helpers."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib import portal_actions, registry


PNG_HEADER = b"\x89PNG\r\n\x1a\n"


def _write_png(path: Path) -> None:
    path.write_bytes(PNG_HEADER + b"fakepngdata")


def _write_run(directory: Path, images: list[dict]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for image in images:
        _write_png(directory / image["file"])
    (directory / "run.json").write_text(
        json.dumps(
            {
                "model": "gpt-image-2",
                "aspect_ratio": "16:9",
                "style": "bcai",
                "run_id": directory.name.removeprefix("run-"),
                "images": images,
            }
        ),
        encoding="utf-8",
    )


def _write_approved_index(approved_dir: Path, entries: list[dict]) -> None:
    approved_dir.mkdir(parents=True, exist_ok=True)
    (approved_dir / "index.json").write_text(
        json.dumps({"images": entries}),
        encoding="utf-8",
    )


def test_discover_actions_marks_external_and_mutating_workflows():
    actions = {action["name"]: action for action in portal_actions.discover_actions()}

    assert actions["approve-starred"]["mutating"] is True
    assert actions["approve-starred"]["external"] is False
    assert actions["notion-export"]["external"] is True
    assert actions["static-deploy"]["external"] is True


def test_mutating_action_requires_explicit_confirmation(tmp_path):
    with pytest.raises(PermissionError, match="requires confirm=true"):
        portal_actions.run_action(
            {"action": "approve-starred", "project": "demo"},
            output_root=tmp_path / "output",
        )


def test_approve_starred_promotes_assets_and_rebuilds_viewer(tmp_path):
    output_root = tmp_path / "output"
    run_dir = output_root / "demo" / "run-20260101-100000"
    _write_run(
        run_dir,
        [
            {"name": "Hero", "prompt": "a hero", "file": "hero.png"},
            {"name": "Alt", "prompt": "alternate", "file": "alt.png"},
        ],
    )
    (output_root / "ratings.json").write_text(
        json.dumps({"demo/run-20260101-100000/hero.png": "star"}),
        encoding="utf-8",
    )

    result = portal_actions.run_action(
        {
            "action": "approve-starred",
            "project": "demo",
            "confirm": True,
        },
        output_root=output_root,
    )

    assert result["ok"] is True
    assert result["mutating"] is True
    assert result["external"] is False
    assert result["approved_count"] == 1
    assert (output_root / "demo" / "approved" / "hero.png").exists()
    assert (output_root / "demo" / "approved" / "viewer.html").exists()
    assert not (output_root / "demo" / "approved" / "alt.png").exists()


def test_canva_export_dry_run_reports_plan_without_writing(tmp_path):
    output_root = tmp_path / "output"
    approved = output_root / "demo" / "approved"
    _write_run(approved, [{"name": "Hero", "prompt": "a hero", "file": "hero.png"}])

    result = portal_actions.run_action(
        {"action": "canva-export", "project": "demo", "dry_run": True},
        output_root=output_root,
    )

    assert result["ok"] is True
    assert result["mutating"] is False
    assert result["external"] is False
    assert result["source"] == "approved"
    assert result["image_count"] == 1
    assert result["result_path"].endswith("canva-export.zip")
    assert not (output_root / "demo" / "canva-export").exists()


def test_canva_export_stamps_archive_metadata_for_source_cards(tmp_path):
    output_root = tmp_path / "output"
    approved = output_root / "demo" / "approved"
    _write_run(approved, [{"name": "Hero", "prompt": "a hero", "file": "hero.png"}])
    _write_approved_index(
        approved,
        [{"slug": "hero.png", "source_run": "run-20260101-100000", "original_file": "hero.png"}],
    )

    result = portal_actions.run_action(
        {"action": "canva-export", "project": "demo", "confirm": True},
        output_root=output_root,
    )

    metadata = json.loads((output_root / "archive-metadata.json").read_text(encoding="utf-8"))
    entry = metadata["items"]["demo/run-20260101-100000/hero.png"]
    assert result["metadata_state"] == "canva"
    assert result["metadata_stamped"] == 1
    assert entry["states"] == ["canva"]


def test_notion_export_dry_run_does_not_require_api_key(tmp_path, monkeypatch):
    output_root = tmp_path / "output"
    approved = output_root / "demo" / "approved"
    _write_run(approved, [{"name": "Hero", "prompt": "caption", "file": "hero.png"}])
    monkeypatch.delenv("NOTION_API_KEY", raising=False)

    result = portal_actions.run_action(
        {
            "action": "notion-export",
            "project": "demo",
            "database_id": "db-123",
            "dry_run": True,
        },
        output_root=output_root,
    )

    assert result["ok"] is True
    assert result["mutating"] is False
    assert result["external"] is False
    assert result["exported"] == 1
    assert not (output_root / "demo" / ".notion-exported.json").exists()
    assert not (output_root / "archive-metadata.json").exists()


def test_notion_export_stamps_archive_metadata_after_success(tmp_path, monkeypatch):
    from lib.exporters import notion

    output_root = tmp_path / "output"
    approved = output_root / "demo" / "approved"
    _write_run(approved, [{"name": "Hero", "prompt": "caption", "file": "hero.png"}])
    _write_approved_index(
        approved,
        [{"slug": "hero.png", "source_run": "run-20260101-100000", "original_file": "hero.png"}],
    )
    monkeypatch.setattr(
        notion,
        "export",
        lambda *args, **kwargs: {
            "exported": 1,
            "skipped": 0,
            "errors": [],
            "source": "approved",
            "dry_run": False,
        },
    )

    result = portal_actions.run_action(
        {
            "action": "notion-export",
            "project": "demo",
            "database_id": "db-123",
            "confirm": True,
        },
        output_root=output_root,
    )

    metadata = json.loads((output_root / "archive-metadata.json").read_text(encoding="utf-8"))
    entry = metadata["items"]["demo/run-20260101-100000/hero.png"]
    assert result["metadata_state"] == "notion"
    assert result["metadata_stamped"] == 1
    assert entry["states"] == ["notion"]


def test_registry_export_reindexes_local_output(tmp_path, monkeypatch):
    output_root = tmp_path / "output"
    approved = output_root / "demo" / "approved"
    data_dir = tmp_path / "data"
    _write_run(approved, [{"name": "Hero", "prompt": "caption", "file": "hero.png"}])

    monkeypatch.setattr(registry, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(registry, "DATA_DIR", data_dir)
    monkeypatch.setattr(registry, "REGISTRY_JSON", data_dir / "asset-registry.json")
    monkeypatch.setattr(registry, "REGISTRY_CSV", data_dir / "asset-registry.csv")
    monkeypatch.setattr(registry, "_load_extra_roots", lambda: {})

    result = portal_actions.run_action(
        {
            "action": "registry-export",
            "format": "csv",
            "confirm": True,
        },
        output_root=output_root,
    )

    assert result["ok"] is True
    assert result["count"] == 1
    assert Path(result["path"]).exists()


def test_static_deploy_dry_run_reports_command_without_calling_vercel(tmp_path):
    viewer_dir = tmp_path / "viewer"
    viewer_dir.mkdir()
    (viewer_dir / "viewer.html").write_text("<html></html>", encoding="utf-8")

    result = portal_actions.run_action(
        {
            "action": "static-deploy",
            "project": "demo",
            "viewer_dir": str(viewer_dir),
            "dry_run": True,
        },
        output_root=tmp_path / "output",
    )

    assert result["ok"] is True
    assert result["mutating"] is False
    assert result["external"] is False
    assert result["command"] == ["vercel", "deploy", str(viewer_dir), "--yes"]
    assert result["source_mapping"]["mapped"] is False
    assert result["source_mapping"]["source_kind"] == "unmapped"


def test_static_deploy_stamps_approved_source_cards(tmp_path, monkeypatch):
    from lib.deploy import vercel

    output_root = tmp_path / "output"
    approved = output_root / "demo" / "approved"
    _write_run(approved, [{"name": "Hero", "prompt": "caption", "file": "hero.png"}])
    _write_approved_index(
        approved,
        [{"slug": "hero.png", "source_run": "run-20260101-100000", "original_file": "hero.png"}],
    )
    (approved / "viewer.html").write_text("<html></html>", encoding="utf-8")
    monkeypatch.setattr(vercel, "deploy", lambda *args, **kwargs: "https://example.vercel.app")

    result = portal_actions.run_action(
        {
            "action": "static-deploy",
            "project": "demo",
            "confirm": True,
        },
        output_root=output_root,
    )

    metadata = json.loads((output_root / "archive-metadata.json").read_text(encoding="utf-8"))
    entry = metadata["items"]["demo/run-20260101-100000/hero.png"]
    assert result["url"] == "https://example.vercel.app"
    assert result["source_mapping"]["source_kind"] == "approved"
    assert result["source_mapping"]["key_count"] == 1
    assert result["metadata_state"] == "deployed"
    assert result["metadata_stamped"] == 1
    assert result["metadata_unmapped"] is False
    assert entry["states"] == ["deployed"]


def test_static_deploy_stamps_project_viewer_run_cards(tmp_path, monkeypatch):
    from lib.deploy import vercel

    output_root = tmp_path / "output"
    project_dir = output_root / "demo"
    run_dir = project_dir / "run-20260101-100000"
    _write_run(run_dir, [{"name": "Hero", "prompt": "caption", "file": "hero.png"}])
    (project_dir / "viewer.html").write_text("<html></html>", encoding="utf-8")
    monkeypatch.setattr(vercel, "deploy", lambda *args, **kwargs: "https://example.vercel.app")

    result = portal_actions.run_action(
        {
            "action": "static-deploy",
            "project": "demo",
            "confirm": True,
        },
        output_root=output_root,
    )

    metadata = json.loads((output_root / "archive-metadata.json").read_text(encoding="utf-8"))
    entry = metadata["items"]["demo/run-20260101-100000/hero.png"]
    assert result["source_mapping"]["source_kind"] == "project"
    assert result["source_mapping"]["key_count"] == 1
    assert result["metadata_stamped"] == 1
    assert entry["states"] == ["deployed"]


def test_static_deploy_stamps_run_viewer_cards(tmp_path, monkeypatch):
    from lib.deploy import vercel

    output_root = tmp_path / "output"
    run_dir = output_root / "demo" / "run-20260101-100000"
    _write_run(run_dir, [{"name": "Hero", "prompt": "caption", "file": "hero.png"}])
    (run_dir / "viewer.html").write_text("<html></html>", encoding="utf-8")
    monkeypatch.setattr(vercel, "deploy", lambda *args, **kwargs: "https://example.vercel.app")

    result = portal_actions.run_action(
        {
            "action": "static-deploy",
            "project": "demo",
            "viewer_dir": str(run_dir),
            "confirm": True,
        },
        output_root=output_root,
    )

    metadata = json.loads((output_root / "archive-metadata.json").read_text(encoding="utf-8"))
    entry = metadata["items"]["demo/run-20260101-100000/hero.png"]
    assert result["source_mapping"]["source_kind"] == "run"
    assert result["source_mapping"]["source_label"] == "run-20260101-100000"
    assert result["metadata_stamped"] == 1
    assert entry["states"] == ["deployed"]


def test_static_deploy_reports_unmapped_custom_viewer(tmp_path, monkeypatch):
    from lib.deploy import vercel

    output_root = tmp_path / "output"
    viewer_dir = tmp_path / "custom-viewer"
    viewer_dir.mkdir()
    (viewer_dir / "viewer.html").write_text("<html></html>", encoding="utf-8")
    monkeypatch.setattr(vercel, "deploy", lambda *args, **kwargs: "https://example.vercel.app")

    result = portal_actions.run_action(
        {
            "action": "static-deploy",
            "project": "demo",
            "viewer_dir": str(viewer_dir),
            "confirm": True,
        },
        output_root=output_root,
    )

    assert result["source_mapping"]["mapped"] is False
    assert result["source_mapping"]["source_kind"] == "unmapped"
    assert "outside the project output root" in result["source_mapping"]["reason"]
    assert result["metadata_stamped"] == 0
    assert result["metadata_unmapped"] is True
    assert not (output_root / "archive-metadata.json").exists()

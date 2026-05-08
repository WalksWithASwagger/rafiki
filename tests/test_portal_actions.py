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

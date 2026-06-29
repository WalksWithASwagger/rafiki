"""Tests for the Floyo pipeline — dry-run writes a manifest with no network."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lib import floyo_jobs
from lib.providers import floyo_provider


def _no_network(monkeypatch, tmp_path):
    monkeypatch.delenv("FLOYO_KEY", raising=False)
    monkeypatch.setattr(floyo_provider, "save_job", lambda record, **kwargs: tmp_path / f"{record.id}.json")
    monkeypatch.setattr(
        floyo_provider, "_post_json",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("network called")),
    )


def test_patch_workflow_maps_slots():
    tpl, imap = floyo_jobs.load_workflow_template("wan22_endframe")
    floyo_jobs.patch_workflow(tpl, imap, "start_image", "/tmp/a.jpg", execute=False)
    floyo_jobs.patch_workflow(tpl, imap, "end_image", "/tmp/b.jpg", execute=False)
    floyo_jobs.patch_workflow(tpl, imap, "prompt", "glam space opera", execute=False)
    assert tpl["67"]["inputs"]["image"].startswith("#dry-run/")
    assert tpl["98"]["inputs"]["image"].startswith("#dry-run/")
    assert tpl["112:16"]["inputs"]["positive_prompt"] == "glam space opera"


def test_unknown_workflow_raises():
    with pytest.raises(ValueError):
        floyo_jobs.load_workflow_template("does-not-exist")


def test_unknown_slot_raises():
    tpl, imap = floyo_jobs.load_workflow_template("wan22_endframe")
    with pytest.raises(ValueError):
        floyo_jobs.patch_workflow(tpl, imap, "nope", "x", execute=False)


def test_build_preview_returns_cost_and_counts():
    preview = floyo_jobs.build_floyo_preview(
        workflow="wan22_endframe",
        inputs={"start_image": "a.jpg", "end_image": "b.jpg", "prompt": "x"},
        execute=False,
    )
    assert preview["dry_run"] is True
    assert preview["cost_estimate"]["amount"] == 0.0
    assert preview["count_preview"]["input_slots"] == 3


def test_plan_dry_run_writes_manifest(tmp_path, monkeypatch):
    _no_network(monkeypatch, tmp_path)
    result = floyo_jobs.plan_floyo_generation(
        workflow="wan22_endframe",
        inputs={"start_image": "/tmp/a.jpg", "end_image": "/tmp/b.jpg", "prompt": "morph"},
        project="andromeda",
        output_root=tmp_path,
        execute=False,
    )
    assert result["ok"] is True
    assert result["job"]["status"] == "dry-run"
    assert result["job"]["provider"] == "Floyo"
    manifest_path = Path(result["manifest_path"])
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["status"] == "dry-run"
    assert manifest["workflow"] == "wan22_endframe"
    assert manifest["project"] == "andromeda"
    assert manifest["inputs"]["prompt"] == "morph"
    assert manifest["cost_estimate"]["amount"] == 0.0


@pytest.mark.parametrize("workflow", ["wan22_endframe", "infinitetalk", "multitalk"])
def test_shipped_workflows_load(workflow):
    tpl, imap = floyo_jobs.load_workflow_template(workflow)
    assert isinstance(tpl, dict) and tpl
    assert imap.get("slots")


def test_infinitetalk_dry_run_plan(tmp_path, monkeypatch):
    _no_network(monkeypatch, tmp_path)
    result = floyo_jobs.plan_floyo_generation(
        workflow="infinitetalk",
        inputs={"image": "/tmp/a.jpg", "audio": "/tmp/song.mp3", "prompt": "singing to camera"},
        project="andromeda",
        output_root=tmp_path,
        execute=False,
    )
    assert result["job"]["status"] == "dry-run"
    assert result["manifest"]["workflow"] == "infinitetalk"
    assert result["manifest"]["inputs"]["audio"] == "/tmp/song.mp3"

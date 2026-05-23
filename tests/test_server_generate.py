"""Tests for server-backed portal generation helpers."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.batch import BatchResult
from lib import registry, server


def _fake_batch_result(project_dir: Path, *, success_count: int = 1, total: int = 1) -> BatchResult:
    run_id = "20260503-101112"
    run_dir = project_dir / f"run-{run_id}"
    return BatchResult(
        success_count=success_count,
        total=total,
        run_dir=run_dir,
        project_dir=project_dir,
        viewer_path=str(project_dir / "viewer.html"),
        run_id=run_id,
        images=[{"name": "Hero", "output_path": str(run_dir / "01-hero.png"), "ok": success_count > 0}],
    )


def test_run_portal_job_single_prompt_uses_run_batch(tmp_path, monkeypatch):
    output_root = tmp_path / "output"
    captured: dict = {}

    def fake_run_batch(**kwargs):
        captured.update(kwargs)
        return _fake_batch_result(kwargs["project_dir"])

    monkeypatch.setattr(server, "run_batch", fake_run_batch)

    result = server._run_portal_job(
        {
            "mode": "single",
            "project": "My Project",
            "name": "Hero Shot",
            "prompt": "A cinematic portrait in warm light",
            "model": "gpt",
            "aspect_ratio": "linkedin",
            "style": "none",
            "quality": "high",
            "resolution": "1K",
            "reference_image": "/tmp/reference.png",
            "global_reference_images": ["/tmp/global-a.png", "/tmp/global-b.png"],
            "dry_run": True,
        },
        output_root=output_root,
    )

    assert captured["project_dir"] == output_root / "my-project"
    assert captured["workers"] == 1
    assert captured["model"] == "gpt-image-2"
    assert captured["aspect_ratio"] == "16:9"
    assert captured["style"] == "none"
    assert captured["ref_paths"] == ["/tmp/reference.png"]
    assert captured["global_reference_images"] == ["/tmp/global-a.png", "/tmp/global-b.png"]
    assert captured["dry_run"] is True
    assert captured["prompts"] == [
        {"name": "Hero Shot", "prompt": "A cinematic portrait in warm light"}
    ]
    assert result["ok"] is True
    assert result["all_ok"] is True
    assert result["viewer_url"] == "/output/my-project/viewer.html"
    assert result["run_viewer_url"].endswith("/run-20260503-101112/viewer.html")


def test_run_portal_job_batch_uses_prompt_file_and_derived_project(tmp_path, monkeypatch):
    output_root = tmp_path / "output"
    prompt_file = tmp_path / "prompts" / "launch-images.md"
    prompt_file.parent.mkdir(parents=True)
    prompt_file.write_text(
        "## 1. Hero\n**Prompt:**\n> first prompt\n\n## 2. Detail\n**Prompt:**\n> second prompt\n",
        encoding="utf-8",
    )

    captured: dict = {}

    def fake_run_batch(**kwargs):
        captured.update(kwargs)
        return _fake_batch_result(kwargs["project_dir"], success_count=1, total=2)

    monkeypatch.setattr(server, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(server, "run_batch", fake_run_batch)

    result = server._run_portal_job(
        {
            "mode": "batch",
            "prompt_file": "prompts/launch-images.md",
            "workers": 3,
            "reference_image": "/tmp/reference.png",
            "global_reference_images": "/tmp/global.png",
        },
        output_root=output_root,
    )

    assert captured["project_dir"] == output_root / "launch-images"
    assert captured["workers"] == 3
    assert captured["prompt_file"] == str(prompt_file.resolve())
    assert len(captured["prompts"]) == 2
    assert captured["ref_paths"] == ["/tmp/reference.png", "/tmp/reference.png"]
    assert captured["global_reference_images"] == ["/tmp/global.png"]
    assert result["ok"] is True
    assert result["all_ok"] is False
    assert result["project"] == "launch-images"
    assert "registry" not in result


def test_run_portal_job_success_refreshes_registry_cache(tmp_path, monkeypatch):
    output_root = tmp_path / "output"
    data_dir = tmp_path / "data"
    monkeypatch.setattr(registry, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(registry, "DATA_DIR", data_dir)
    monkeypatch.setattr(registry, "REGISTRY_JSON", data_dir / "asset-registry.json")
    monkeypatch.setattr(registry, "REGISTRY_CSV", data_dir / "asset-registry.csv")
    monkeypatch.setattr(registry, "_load_extra_roots", lambda: {})

    def fake_run_batch(**kwargs):
        result = _fake_batch_result(kwargs["project_dir"])
        result.run_dir.mkdir(parents=True)
        image_path = result.run_dir / "01-hero.png"
        image_path.write_bytes(b"\x89PNG\r\n\x1a\nfakepngdata")
        (result.run_dir / "run.json").write_text(
            json.dumps(
                {
                    "model": "gpt-image-2",
                    "aspect_ratio": "16:9",
                    "style": "none",
                    "run_id": result.run_id,
                    "images": [{"name": "Hero", "prompt": "caption", "file": image_path.name}],
                }
            ),
            encoding="utf-8",
        )
        return result

    monkeypatch.setattr(server, "run_batch", fake_run_batch)

    result = server._run_portal_job(
        {
            "mode": "single",
            "project": "Studio",
            "prompt": "A vivid local-first archive card",
        },
        output_root=output_root,
    )

    assert result["ok"] is True
    assert result["all_ok"] is True
    assert result["registry"]["registry_refreshed"] is True
    assert result["registry"]["registry_count"] == 1
    assert (data_dir / "asset-registry.json").exists()


def test_run_portal_job_rejects_mismatched_reference_images(tmp_path, monkeypatch):
    output_root = tmp_path / "output"
    prompt_file = tmp_path / "prompts" / "batch.md"
    prompt_file.parent.mkdir(parents=True)
    prompt_file.write_text(
        "## 1. One\n**Prompt:**\n> one\n\n## 2. Two\n**Prompt:**\n> two\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(server, "REPO_ROOT", tmp_path)
    with pytest.raises(ValueError, match="reference_images has 3 path\\(s\\) but 2 prompt\\(s\\)"):
        server._run_portal_job(
            {
                "mode": "batch",
                "prompt_file": "prompts/batch.md",
                "reference_images": ["/tmp/a.png", "/tmp/b.png", "/tmp/c.png"],
            },
            output_root=output_root,
        )


def test_run_portal_job_requires_prompt_for_single(tmp_path):
    with pytest.raises(ValueError, match="prompt is required"):
        server._run_portal_job(
            {"mode": "single", "project": "studio"},
            output_root=tmp_path / "output",
        )


def test_run_portal_job_accepts_brand_reference_role(tmp_path, monkeypatch):
    output_root = tmp_path / "output"
    captured: dict = {}

    def fake_run_batch(**kwargs):
        captured.update(kwargs)
        return _fake_batch_result(kwargs["project_dir"])

    monkeypatch.setattr(server, "run_batch", fake_run_batch)

    result = server._run_portal_job(
        {
            "mode": "single",
            "project": "Brand",
            "prompt": "logo-aware hero art",
            "reference_role": "brand",
            "dry_run": True,
        },
        output_root=output_root,
    )

    assert result["ok"] is True
    assert captured["reference_role"] == "brand"


def test_safe_error_text_preserves_provider_message_without_control_chars():
    text = server._safe_error_text("provider said nope\x00\ntry a smaller prompt")

    assert text == "provider said nope\ntry a smaller prompt"


def test_safe_error_text_redacts_common_secret_shapes():
    text = server._safe_error_text(
        "provider failed: OPENAI_API_KEY=sk-test-secret Authorization: Bearer secret_token_123"
    )

    assert "sk-test-secret" not in text
    assert "secret_token_123" not in text
    assert "OPENAI_API_KEY=[redacted]" in text
    assert "Authorization: Bearer [redacted]" in text

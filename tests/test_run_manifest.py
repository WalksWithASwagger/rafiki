from __future__ import annotations

import json
from pathlib import Path

import lib.batch as batch_module


def _manifest(run_dir: Path) -> dict:
    return json.loads((run_dir / "run.json").read_text(encoding="utf-8"))


def test_run_manifest_records_provenance_and_timing(tmp_path):
    prompt_file = tmp_path / "prompts" / "image-prompts.md"
    prompt_file.parent.mkdir()
    prompt_file.write_text("placeholder", encoding="utf-8")

    result = batch_module.run_batch(
        prompts=[
            {"name": "Hero", "prompt": "hero prompt"},
            {"name": "Detail", "prompt": "detail prompt", "model": "dall-e-3", "style": "kk"},
        ],
        project_dir=tmp_path / "images",
        model="gpt-image-2",
        aspect_ratio="1:1",
        style="bcai",
        ref_paths=["/tmp/ref-a.png", "/tmp/ref-b.png"],
        global_reference_images=["/tmp/global-a.png", "/tmp/global-b.png"],
        reference_role="mockup",
        composition_references=["/tmp/composition.png"],
        dry_run=True,
        generate_viewer_html=False,
        prompt_file=str(prompt_file),
        invocation_source="mcp",
    )

    data = _manifest(result.run_dir)

    assert data["prompt_file"] == str(prompt_file)
    assert data["prompt_source"] == str(prompt_file)
    assert data["invocation"] == {"surface": "mcp"}
    assert data["model"] == "gpt-image-2"
    assert data["provider"] == "OpenAI"
    assert data["style"] == "bcai"
    assert data["reference_images"] == [
        "/tmp/ref-a.png",
        "/tmp/ref-b.png",
        "/tmp/global-a.png",
        "/tmp/global-b.png",
        "/tmp/composition.png",
    ]
    assert data["reference_role"] == "mockup"
    assert data["state"] == "succeeded"
    assert data["cost_estimate"]["estimated"] is False
    assert data["cost_estimate"]["amount"] is None
    assert data["cost_estimate"]["currency"] == "USD"
    assert data["cost_estimate"]["image_count"] == 2
    assert data["duration_seconds"] >= 0
    assert data["started_at"]
    assert data["finished_at"]
    assert "error" not in data

    assert [image["state"] for image in data["images"]] == ["succeeded", "succeeded"]
    assert data["images"][0]["model"] == "gpt-image-2"
    assert data["images"][0]["provider"] == "OpenAI"
    assert data["images"][0]["style"] == "bcai"
    assert data["images"][0]["cost_estimate"]["model"] == "gpt-image-2"
    assert data["images"][0]["cost_estimate"]["provider"] == "OpenAI"
    assert data["images"][0]["reference_images"] == [
        "/tmp/ref-a.png",
        "/tmp/global-a.png",
        "/tmp/global-b.png",
        "/tmp/composition.png",
    ]
    assert data["images"][1]["model"] == "dall-e-3"
    assert data["images"][1]["provider"] == "OpenAI"
    assert data["images"][1]["style"] == "kk"
    assert data["images"][1]["cost_estimate"]["model"] == "dall-e-3"
    assert data["images"][1]["duration_seconds"] >= 0


def test_run_manifest_records_item_failure_state_and_error(tmp_path, monkeypatch):
    def fake_generate_image(**kwargs):
        return "bad" not in kwargs["prompt"]

    monkeypatch.setattr(batch_module, "generate_image", fake_generate_image)

    result = batch_module.run_batch(
        prompts=[
            {"name": "Bad", "prompt": "bad prompt"},
            {"name": "Good", "prompt": "good prompt"},
        ],
        project_dir=tmp_path / "images",
        model="gemini-2.5-flash-image",
        dry_run=True,
        generate_viewer_html=False,
        prompt_file="",
    )

    data = _manifest(result.run_dir)

    assert result.success_count == 1
    assert result.success is False
    assert data["prompt_source"] == "inline"
    assert data["invocation"] == {"surface": "python-cli"}
    assert data["provider"] == "Gemini"
    assert data["state"] == "partial"
    assert data["error"] == "1 of 2 image failed"
    assert data["images"][0]["state"] == "failed"
    assert data["images"][0]["error"] == "generation failed"
    assert data["images"][0]["duration_seconds"] >= 0
    assert data["images"][1]["state"] == "succeeded"
    assert "error" not in data["images"][1]


def test_run_manifest_verifies_success_wrote_file(tmp_path, monkeypatch):
    def fake_generate_image(**kwargs):
        return True

    monkeypatch.setattr(batch_module, "generate_image", fake_generate_image)

    result = batch_module.run_batch(
        prompts=[{"name": "Missing File", "prompt": "no output"}],
        project_dir=tmp_path / "images",
        model="gemini-2.5-flash-image",
        dry_run=False,
        generate_viewer_html=False,
    )

    data = _manifest(result.run_dir)

    assert result.success_count == 0
    assert data["state"] == "failed"
    assert data["images"][0]["ok"] is False
    assert data["images"][0]["state"] == "failed"
    assert data["images"][0]["error"] == "API returned success but file was not written"


def test_run_manifest_records_exception_detail(tmp_path, monkeypatch):
    def fake_generate_image(**kwargs):
        raise RuntimeError("quota exhausted")

    monkeypatch.setattr(batch_module, "generate_image", fake_generate_image)

    result = batch_module.run_batch(
        prompts=[{"name": "Quota", "prompt": "too much"}],
        project_dir=tmp_path / "images",
        model="gemini-2.5-flash-image",
        dry_run=False,
        generate_viewer_html=False,
    )

    data = _manifest(result.run_dir)

    assert result.success is False
    assert data["images"][0]["ok"] is False
    assert data["images"][0]["error"] == "quota exhausted"


def test_run_manifest_uses_provider_list_for_mixed_provider_runs(tmp_path):
    result = batch_module.run_batch(
        prompts=[
            {"name": "Gemini", "prompt": "gemini prompt"},
            {"name": "OpenAI", "prompt": "openai prompt", "model": "gpt-image-2"},
        ],
        project_dir=tmp_path / "images",
        model="gemini-2.5-flash-image",
        dry_run=True,
        generate_viewer_html=False,
        prompt_file="",
        invocation_source="portal",
    )

    data = _manifest(result.run_dir)

    assert "provider" not in data
    assert data["providers"] == ["Gemini", "OpenAI"]
    assert data["models"] == ["gemini-2.5-flash-image", "gpt-image-2"]
    assert data["invocation"] == {"surface": "portal"}
    assert data["images"][0]["provider"] == "Gemini"
    assert data["images"][1]["provider"] == "OpenAI"

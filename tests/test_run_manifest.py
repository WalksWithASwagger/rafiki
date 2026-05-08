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
        reference_role="mockup",
        composition_references=["/tmp/composition.png"],
        dry_run=True,
        generate_viewer_html=False,
        prompt_file=str(prompt_file),
    )

    data = _manifest(result.run_dir)

    assert data["prompt_file"] == str(prompt_file)
    assert data["prompt_source"] == str(prompt_file)
    assert data["model"] == "gpt-image-2"
    assert data["provider"] == "OpenAI"
    assert data["style"] == "bcai"
    assert data["reference_images"] == [
        "/tmp/ref-a.png",
        "/tmp/ref-b.png",
        "/tmp/composition.png",
    ]
    assert data["reference_role"] == "mockup"
    assert data["state"] == "succeeded"
    assert data["duration_seconds"] >= 0
    assert data["started_at"]
    assert data["finished_at"]
    assert "error" not in data

    assert [image["state"] for image in data["images"]] == ["succeeded", "succeeded"]
    assert data["images"][0]["model"] == "gpt-image-2"
    assert data["images"][0]["provider"] == "OpenAI"
    assert data["images"][0]["style"] == "bcai"
    assert data["images"][0]["reference_images"] == ["/tmp/ref-a.png", "/tmp/composition.png"]
    assert data["images"][1]["model"] == "dall-e-3"
    assert data["images"][1]["provider"] == "OpenAI"
    assert data["images"][1]["style"] == "kk"
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
    assert data["provider"] == "Gemini"
    assert data["state"] == "partial"
    assert data["error"] == "1 of 2 image failed"
    assert data["images"][0]["state"] == "failed"
    assert data["images"][0]["error"] == "generation failed"
    assert data["images"][0]["duration_seconds"] >= 0
    assert data["images"][1]["state"] == "succeeded"
    assert "error" not in data["images"][1]

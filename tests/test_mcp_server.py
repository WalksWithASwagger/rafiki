"""Tests for Rafiki's MCP server tool wrappers."""

from __future__ import annotations

import json
from pathlib import Path

import mcp_server
from lib.batch import BatchResult


def test_generate_style_none_stays_unstyled(monkeypatch, tmp_path):
    captured: dict = {}

    def fake_generate_image(**kwargs):
        captured.update(kwargs)
        return True

    monkeypatch.setattr(mcp_server, "generate_image", fake_generate_image)

    payload = json.loads(
        mcp_server.rafiki_generate(
            prompt="A quiet studio portrait",
            output_path=str(tmp_path / "out.png"),
            aspect_ratio="linkedin",
            style="none",
            reference_image="/tmp/ref.png",
            dry_run=True,
        )
    )

    assert payload["success"] is True
    assert payload["aspect_ratio"] == "16:9"
    assert captured["style"] == "none"
    assert captured["reference_image"] == "/tmp/ref.png"


def test_batch_passes_reference_images_and_unstyled(monkeypatch, tmp_path):
    prompt_file = tmp_path / "image-prompts.md"
    prompt_file.write_text(
        "## 1. Hero\n**Prompt:**\n> first\n\n## 2. Detail\n**Prompt:**\n> second\n",
        encoding="utf-8",
    )
    captured: dict = {}

    def fake_run_batch(**kwargs):
        captured.update(kwargs)
        return BatchResult(
            success_count=2,
            total=2,
            run_dir=tmp_path / "images" / "run-20260507-100000",
            project_dir=tmp_path / "images",
            viewer_path=str(tmp_path / "images" / "viewer.html"),
            run_id="20260507-100000",
            images=[],
        )

    monkeypatch.setattr(mcp_server, "run_batch", fake_run_batch)

    payload = json.loads(
        mcp_server.rafiki_batch(
            prompt_file=str(prompt_file),
            output_dir=str(tmp_path / "images"),
            aspect_ratio="instagram",
            style="none",
            reference_images=["/tmp/a.png", "/tmp/b.png"],
            no_viewer=True,
            dry_run=True,
        )
    )

    assert payload["success"] is True
    assert payload["aspect_ratio"] == "1:1"
    assert captured["style"] == "none"
    assert captured["ref_paths"] == ["/tmp/a.png", "/tmp/b.png"]
    assert captured["generate_viewer_html"] is False


def test_batch_rejects_mismatched_reference_images(tmp_path):
    prompt_file = tmp_path / "image-prompts.md"
    prompt_file.write_text(
        "## 1. Hero\n**Prompt:**\n> first\n\n## 2. Detail\n**Prompt:**\n> second\n",
        encoding="utf-8",
    )

    payload = json.loads(
        mcp_server.rafiki_batch(
            prompt_file=str(prompt_file),
            reference_images=["/tmp/a.png", "/tmp/b.png", "/tmp/c.png"],
            dry_run=True,
        )
    )

    assert payload["success"] is False
    assert "reference_images has 3 path(s) but 2 prompt(s)" in payload["error"]


def test_run_rejects_non_rafiki_invocations():
    payload = json.loads(mcp_server.rafiki_run(["python3", "-c", "print('nope')"]))

    assert payload["success"] is False
    assert "unsupported Rafiki CLI invocation" in payload["error"]


def test_run_usage_smoke():
    payload = json.loads(mcp_server.rafiki_run(["--usage"]))

    assert payload["success"] is True
    assert payload["exit_code"] == 0
    assert "Total images generated:" in payload["stdout"]


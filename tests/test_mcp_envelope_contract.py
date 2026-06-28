"""Output-format eval for the MCP output contract (docs/MCP-OUTPUT-CONTRACT.md).

Scenario: an agent calls each typed MCP tool. Expected: every response validates
against the shared envelope schema (`ok`/`success`/`tool` required, flags and `error`
typed). Failure mode caught: silent contract drift — a tool that stops emitting the
envelope (or emits a wrong type) fails here instead of breaking agents in the field.
Passing = schema validation green across success and error paths.

Tools exercised directly below cover 21 of the 23 typed tools plus error paths. The two
not exercised here are covered by their own tests for hermeticity/external reasons:
  - rafiki_media_index: reads real configured media roots; see test_media_* tests.
  - rafiki_notion_export: reaches the Notion API; see test_notion_export_* tests.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import jsonschema
import pytest

import mcp_server

_SCHEMA = json.loads((Path(__file__).parent / "mcp_envelope_schema.json").read_text())

PNG_HEADER = b"\x89PNG\r\n\x1a\n"


def assert_envelope(raw: str, *, expect_ok: bool | None = None) -> dict:
    """Validate a tool's JSON output against the envelope contract."""
    payload = json.loads(raw)
    jsonschema.validate(payload, _SCHEMA)
    assert payload["ok"] == payload["success"], "ok and success must agree"
    if expect_ok is not None:
        assert payload["ok"] is expect_ok
    return payload


def _write_run(directory: Path, images: list[dict]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for image in images:
        (directory / image["file"]).write_bytes(PNG_HEADER + b"fake")
    (directory / "run.json").write_text(
        json.dumps({
            "model": "gpt-image-2",
            "aspect_ratio": "16:9",
            "style": "bcai",
            "run_id": directory.name.removeprefix("run-"),
            "images": images,
        }),
        encoding="utf-8",
    )


# Tools callable with no fixtures, validated as a group.
NO_FIXTURE_CALLS = {
    "status": lambda: mcp_server.rafiki_status(),
    "list_styles": lambda: mcp_server.rafiki_list_styles(),
    "usage": lambda: mcp_server.rafiki_usage(),
    "registry_search": lambda: mcp_server.rafiki_registry_search(query="", limit=1),
    "registry_export": lambda: mcp_server.rafiki_registry_export(format="json", dry_run=True),
    "media_search": lambda: mcp_server.rafiki_media_search(query="", limit=1),
    "subjects": lambda: mcp_server.rafiki_subjects(),
    "jobs": lambda: mcp_server.rafiki_jobs(),
    "train_lora": lambda: mcp_server.rafiki_train_lora(
        subject="contract-test",
        input_images_url="https://example.com/images.zip",
        execute=False,
    ),
    "run_success": lambda: mcp_server.rafiki_run(["--usage"]),
}

# Error paths must satisfy the same envelope.
ERROR_CALLS = {
    "job_status_blank": lambda: mcp_server.rafiki_job_status(job_id=""),
    "run_invalid": lambda: mcp_server.rafiki_run(["python3", "-c", "print(1)"]),
}


@pytest.mark.parametrize("name", sorted(NO_FIXTURE_CALLS))
def test_no_fixture_tool_outputs_match_envelope(name):
    assert_envelope(NO_FIXTURE_CALLS[name](), expect_ok=True)


@pytest.mark.parametrize("name", sorted(ERROR_CALLS))
def test_error_outputs_match_envelope(name):
    payload = assert_envelope(ERROR_CALLS[name](), expect_ok=False)
    assert isinstance(payload["error"], str) and payload["error"]


def test_media_warnings_matches_envelope(tmp_path):
    assert_envelope(
        mcp_server.rafiki_media_warnings(registry_path=str(tmp_path / "none.json")),
        expect_ok=True,
    )


def test_job_status_success_matches_envelope(tmp_path):
    import lib.jobs as jobs_module

    jobs_dir = tmp_path / "jobs"
    jobs_dir.mkdir()
    job_id = "video-generation-20260601-120000"
    (jobs_dir / f"{job_id}.json").write_text(
        json.dumps({
            "id": job_id,
            "kind": "video-generation",
            "provider": "Replicate",
            "status": "queued",
            "polling_status": "pending",
            "created_at": "2026-06-01T12:00:00+00:00",
            "updated_at": "2026-06-01T12:00:01+00:00",
            "cost_estimate": {"currency": "USD", "amount": 0.0, "estimated": True},
        }),
        encoding="utf-8",
    )
    with patch.object(jobs_module, "JOBS_DIR", jobs_dir):
        assert_envelope(mcp_server.rafiki_job_status(job_id), expect_ok=True)


def test_archive_health_matches_envelope(tmp_path):
    output_root = tmp_path / "output"
    _write_run(output_root / "p" / "run-20260101-100000", [{"name": "A", "prompt": "x", "file": "a.png"}])
    assert_envelope(mcp_server.rafiki_archive_health(output_root=str(output_root)))


def test_render_matches_envelope(tmp_path):
    html = tmp_path / "card.html"
    html.write_text("<html><body>hi</body></html>", encoding="utf-8")
    assert_envelope(mcp_server.rafiki_render(html_path=str(html), dry_run=True), expect_ok=True)


def test_generate_matches_envelope(tmp_path, monkeypatch):
    monkeypatch.setattr(mcp_server, "generate_image", lambda **_: True)
    assert_envelope(
        mcp_server.rafiki_generate(
            prompt="a quiet studio portrait",
            output_path=str(tmp_path / "out.png"),
            dry_run=True,
        ),
        expect_ok=True,
    )


def test_batch_matches_envelope(tmp_path):
    prompt_file = tmp_path / "image-prompts.md"
    prompt_file.write_text("## 1. Hero\n**Prompt:**\n> first\n", encoding="utf-8")
    assert_envelope(mcp_server.rafiki_batch(prompt_file=str(prompt_file), dry_run=True))
    # Error path: missing file.
    assert_envelope(
        mcp_server.rafiki_batch(prompt_file=str(tmp_path / "missing.md"), dry_run=False),
        expect_ok=False,
    )


def test_viewer_rebuild_matches_envelope(tmp_path):
    project = tmp_path / "output" / "viewer-project"
    _write_run(project / "run-20260101-100000", [{"name": "Hero", "prompt": "x", "file": "h.png"}])
    assert_envelope(
        mcp_server.rafiki_viewer_rebuild(project=str(project), all_runs=True, dry_run=True),
        expect_ok=True,
    )


def test_library_rebuild_matches_envelope(tmp_path):
    assert_envelope(mcp_server.rafiki_library_rebuild(output_root=str(tmp_path), dry_run=True))


def test_canva_export_matches_envelope(tmp_path):
    output_root = tmp_path / "output"
    _write_run(output_root / "canva-project" / "run-20260101-100000", [{"name": "Hero", "prompt": "x", "file": "h.png"}])
    assert_envelope(
        mcp_server.rafiki_canva_export("canva-project", output_root=str(output_root), dry_run=True),
        expect_ok=True,
    )


def test_style_anchors_matches_envelope(tmp_path):
    source = tmp_path / "anchor.json"
    source.write_text(json.dumps({"name": "t", "positive": ["x"], "negative": ["y"]}), encoding="utf-8")
    assert_envelope(mcp_server.rafiki_style_anchors(source=str(source)), expect_ok=True)


def test_video_generate_matches_envelope(tmp_path):
    storyboard = tmp_path / "storyboard.json"
    storyboard.write_text(
        json.dumps({"title": "contract-test", "scenes": [{"prompt": "a cat walks in"}]}),
        encoding="utf-8",
    )
    assert_envelope(
        mcp_server.rafiki_video_generate(storyboard=str(storyboard), execute=False),
        expect_ok=True,
    )

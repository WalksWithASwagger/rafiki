"""Tests for Rafiki's MCP server tool wrappers."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import patch

import mcp_server
from lib.batch import BatchResult
from lib import extra_outputs, registry


PNG_HEADER = b"\x89PNG\r\n\x1a\n"


def _write_png(path: Path) -> None:
    path.write_bytes(PNG_HEADER + b"fakepngdata")


def _write_run(directory: Path, images: list[dict]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for image in images:
        _write_png(directory / image["file"])
    (directory / "run.json").write_text(
        json.dumps({
            "model": "gpt-image-2",
            "aspect_ratio": "16:9",
            "style": "bcai",
            "prompt_file": "prompts/test/example.md",
            "run_id": directory.name.removeprefix("run-"),
            "images": images,
        }),
        encoding="utf-8",
    )


def _isolate_registry(tmp_path, monkeypatch):
    output_root = tmp_path / "output"
    data_dir = tmp_path / "data"
    config_dir = tmp_path / "config"
    output_root.mkdir()

    monkeypatch.setattr(registry, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(registry, "DEFAULT_OUTPUT_ROOT", output_root)
    monkeypatch.setattr(registry, "DATA_DIR", data_dir)
    monkeypatch.setattr(registry, "REGISTRY_JSON", data_dir / "asset-registry.json")
    monkeypatch.setattr(registry, "REGISTRY_CSV", data_dir / "asset-registry.csv")
    monkeypatch.setattr(extra_outputs, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(extra_outputs, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(extra_outputs, "EXTRA_OUTPUTS_CONFIG", config_dir / "extra-outputs.json")
    monkeypatch.setattr(extra_outputs, "EXTRA_OUTPUTS_LOCAL_CONFIG", config_dir / "extra-outputs.local.json")
    return output_root


def test_typed_workflow_tools_are_registered():
    tools = asyncio.run(mcp_server.mcp.list_tools())
    names = {tool.name for tool in tools}

    assert {
        "rafiki_registry_search",
        "rafiki_registry_export",
        "rafiki_archive_health",
        "rafiki_viewer_rebuild",
        "rafiki_library_rebuild",
        "rafiki_render",
        "rafiki_canva_export",
        "rafiki_notion_export",
        "rafiki_media_warnings",
        "rafiki_job_status",
    }.issubset(names)


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
            global_reference_images=["/tmp/global.png"],
            dry_run=True,
        )
    )

    assert payload["success"] is True
    assert payload["ok"] is True
    assert payload["tool"] == "rafiki_generate"
    assert payload["output_url"].startswith("file://")
    assert payload["aspect_ratio"] == "16:9"
    assert captured["style"] == "none"
    assert captured["reference_image"] == "/tmp/ref.png"
    assert captured["reference_images"] == ["/tmp/global.png"]


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
            global_reference_images=["/tmp/global-a.png", "/tmp/global-b.png"],
            no_viewer=True,
            dry_run=True,
        )
    )

    assert payload["success"] is True
    assert payload["aspect_ratio"] == "1:1"
    assert captured["style"] == "none"
    assert captured["ref_paths"] == ["/tmp/a.png", "/tmp/b.png"]
    assert captured["global_reference_images"] == ["/tmp/global-a.png", "/tmp/global-b.png"]
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
    assert payload["ok"] is False
    assert payload["tool"] == "rafiki_batch"
    assert payload["mutating"] is False
    assert payload["external"] is False
    assert "reference_images has 3 path(s) but 2 prompt(s)" in payload["error"]


def test_batch_missing_prompt_file_returns_full_error_envelope(tmp_path):
    payload = json.loads(
        mcp_server.rafiki_batch(prompt_file=str(tmp_path / "missing.md"), dry_run=False)
    )

    assert payload["success"] is False
    assert payload["ok"] is False
    assert payload["tool"] == "rafiki_batch"
    assert payload["mutating"] is False
    assert payload["external"] is False
    assert "Prompt file not found" in payload["error"]


def test_run_rejects_non_rafiki_invocations():
    payload = json.loads(mcp_server.rafiki_run(["python3", "-c", "print('nope')"]))

    assert payload["success"] is False
    assert payload["ok"] is False
    assert payload["tool"] == "rafiki_run"
    assert payload["timeout"] is False
    assert payload["exit_code"] is None
    assert "unsupported Rafiki CLI invocation" in payload["error"]


def test_status_returns_envelope_fields():
    payload = json.loads(mcp_server.rafiki_status())

    assert payload["success"] is True
    assert payload["ok"] is True
    assert payload["tool"] == "rafiki_status"
    assert "rafiki_run" in payload["common_tools"]


def test_list_styles_returns_envelope_fields():
    payload = json.loads(mcp_server.rafiki_list_styles())

    assert payload["success"] is True
    assert payload["ok"] is True
    assert payload["tool"] == "rafiki_list_styles"
    assert payload["count"] == len(payload["styles"])
    assert isinstance(payload["styles"], dict)


def test_usage_returns_envelope_fields():
    payload = json.loads(mcp_server.rafiki_usage())

    assert payload["success"] is True
    assert payload["ok"] is True
    assert payload["tool"] == "rafiki_usage"
    assert "entries" in payload


def test_run_usage_smoke():
    payload = json.loads(mcp_server.rafiki_run(["--usage"]))

    assert payload["success"] is True
    assert payload["tool"] == "rafiki_run"
    assert payload["timeout"] is False
    assert payload["error"] is None
    assert payload["exit_code"] == 0
    assert "Total images generated:" in payload["stdout"]


def test_run_billing_summary_bridge(tmp_path):
    state = tmp_path / "billing-imports.json"

    payload = json.loads(mcp_server.rafiki_run(["billing", "summary", "--state", str(state), "--json"]))

    assert payload["success"] is True
    assert payload["ok"] is True
    assert payload["mutating"] is False
    summary = json.loads(payload["stdout"])
    assert summary["entries"] == 0


def test_run_archive_health_bridge(tmp_path):
    output_root = tmp_path / "output"
    output_root.mkdir()

    payload = json.loads(mcp_server.rafiki_run(["archive-health", "--output-dir", str(output_root), "--json"]))

    assert payload["success"] is True
    assert payload["mutating"] is False
    assert payload["json"]["ok"] is True
    assert payload["json"]["summary"]["projects"] == 0


def test_registry_search_wrapper_returns_structured_matches(tmp_path, monkeypatch):
    output_root = _isolate_registry(tmp_path, monkeypatch)
    approved = output_root / "search-project" / "approved"
    _write_run(
        approved,
        [
            {"name": "The Hallucination Problem", "prompt": "confident wrong", "file": "hallucination.png"},
            {"name": "Bias In The Machine", "prompt": "skewed data", "file": "bias.png"},
        ],
    )
    registry.index()

    payload = json.loads(mcp_server.rafiki_registry_search("hallucination"))

    assert payload["success"] is True
    assert payload["mutating"] is False
    assert payload["external"] is False
    assert payload["count"] == 1
    assert payload["results"][0]["id"] == "search-project-hallucination"


def test_registry_export_wrapper_dry_run_reports_path_and_count(tmp_path, monkeypatch):
    output_root = _isolate_registry(tmp_path, monkeypatch)
    approved = output_root / "export-project" / "approved"
    _write_run(approved, [{"name": "Only", "prompt": "p", "file": "only.png"}])
    registry.index()

    payload = json.loads(mcp_server.rafiki_registry_export(format="csv", dry_run=True))

    assert payload["success"] is True
    assert payload["dry_run"] is True
    assert payload["mutating"] is False
    assert payload["count"] == 1
    assert payload["path"].endswith("asset-registry.csv")
    assert not (tmp_path / "data" / "asset-registry.csv").exists()


def test_archive_health_wrapper_reports_read_only_counts(tmp_path):
    output_root = tmp_path / "output"
    run_dir = output_root / "healthy-project" / "run-20260101-100000"
    _write_run(
        run_dir,
        [{"name": "Hero", "prompt": "a hero", "file": "hero.png"}],
    )

    payload = json.loads(mcp_server.rafiki_archive_health(output_root=str(output_root)))

    assert payload["success"] is True
    assert payload["ok"] is True
    assert payload["dry_run"] is True
    assert payload["mutating"] is False
    assert payload["project_count"] == 1
    assert payload["run_count"] == 1
    assert payload["manifest_image_count"] == 1
    assert payload["present_image_count"] == 1
    assert payload["errors"] == {"missing_images": [], "malformed_runs": []}


def test_archive_health_wrapper_reports_missing_image_errors(tmp_path):
    output_root = tmp_path / "output"
    run_dir = output_root / "broken-project" / "run-20260101-100000"
    run_dir.mkdir(parents=True)
    (run_dir / "run.json").write_text(
        json.dumps({
            "images": [{"name": "Missing", "prompt": "gone", "file": "missing.png"}],
        }),
        encoding="utf-8",
    )

    payload = json.loads(mcp_server.rafiki_archive_health(output_root=str(output_root)))

    assert payload["success"] is False
    assert payload["ok"] is False
    assert payload["mutating"] is False
    assert payload["missing_image_count"] == 1
    assert payload["errors"]["missing_images"][0]["path"].endswith("missing.png")


def test_viewer_rebuild_wrapper_dry_run_reports_viewer_paths(tmp_path):
    project = tmp_path / "output" / "viewer-project"
    run_dir = project / "run-20260101-100000"
    _write_run(
        run_dir,
        [{"name": "Hero", "prompt": "a hero", "file": "hero.png"}],
    )

    payload = json.loads(
        mcp_server.rafiki_viewer_rebuild(
            project=str(project),
            all_runs=True,
            dry_run=True,
        )
    )

    assert payload["success"] is True
    assert payload["ok"] is True
    assert payload["dry_run"] is True
    assert payload["mutating"] is False
    assert payload["run_count"] == 1
    assert payload["image_count"] == 1
    assert payload["viewer_path"] == str(project / "viewer.html")
    assert payload["viewer_url"].startswith("file://")
    assert payload["run_viewer_paths"] == [str(run_dir / "viewer.html")]
    assert len(payload["run_viewer_urls"]) == len(payload["run_viewer_paths"])
    assert payload["run_viewer_urls"][0].startswith("file://")
    assert not (project / "viewer.html").exists()


def test_viewer_rebuild_wrapper_reports_missing_project_error(tmp_path):
    payload = json.loads(
        mcp_server.rafiki_viewer_rebuild(
            project="missing-project",
            output_root=str(tmp_path / "output"),
            dry_run=True,
        )
    )

    assert payload["success"] is False
    assert payload["ok"] is False
    assert payload["mutating"] is False
    assert "Project not found" in payload["error"]


def test_library_rebuild_wrapper_dry_run_reports_library_path(tmp_path, monkeypatch):
    output_root = _isolate_registry(tmp_path, monkeypatch)
    run_dir = output_root / "library-project" / "run-20260101-100000"
    _write_run(
        run_dir,
        [{"name": "Hero", "prompt": "a hero", "file": "hero.png"}],
    )

    payload = json.loads(
        mcp_server.rafiki_library_rebuild(
            output_root=str(output_root),
            dry_run=True,
        )
    )

    assert payload["success"] is True
    assert payload["ok"] is True
    assert payload["dry_run"] is True
    assert payload["mutating"] is False
    assert payload["library_path"] == str(output_root.resolve() / "library.html")
    assert payload["project_count"] == 1
    assert payload["image_count"] == 1
    assert not (output_root / "library.html").exists()


def test_library_rebuild_wrapper_reports_missing_output_root_error(tmp_path):
    payload = json.loads(
        mcp_server.rafiki_library_rebuild(
            output_root=str(tmp_path / "missing-output"),
            dry_run=True,
        )
    )

    assert payload["success"] is False
    assert payload["ok"] is False
    assert payload["mutating"] is False
    assert "Output root not found" in payload["error"]


def test_render_wrapper_dry_run_reports_png_targets(tmp_path):
    html = tmp_path / "card.html"
    html.write_text("<html><body>Card</body></html>", encoding="utf-8")

    payload = json.loads(mcp_server.rafiki_render(html_path=str(html), dry_run=True))

    assert payload["success"] is True
    assert payload["ok"] is True
    assert payload["dry_run"] is True
    assert payload["mutating"] is False
    assert payload["count"] == 1
    assert payload["output_paths"] == [str(html.with_suffix(".png"))]
    assert not html.with_suffix(".png").exists()


def test_canva_export_wrapper_dry_run_reports_bundle_plan(tmp_path):
    output_root = tmp_path / "output"
    run_dir = output_root / "canva-project" / "run-20260101-100000"
    _write_run(
        run_dir,
        [{"name": "Hero", "prompt": "a hero", "file": "hero.png"}],
    )

    payload = json.loads(
        mcp_server.rafiki_canva_export(
            "canva-project",
            output_root=str(output_root),
            dry_run=True,
        )
    )

    assert payload["success"] is True
    assert payload["ok"] is True
    assert payload["dry_run"] is True
    assert payload["mutating"] is False
    assert payload["count"] == 1
    assert payload["image_count"] == 1
    assert payload["zip"] is True
    assert payload["result_path"].endswith("canva-export.zip")
    assert not (output_root / "canva-project" / "canva-export").exists()


def test_media_warnings_returns_empty_list_when_registry_absent(tmp_path):
    payload = json.loads(
        mcp_server.rafiki_media_warnings(
            registry_path=str(tmp_path / "nonexistent-registry.json")
        )
    )

    assert payload["success"] is True
    assert payload["ok"] is True
    assert payload["mutating"] is False
    assert payload["external"] is False
    assert payload["warnings"] == []
    assert payload["count"] == 0
    assert payload["warning_count"] == 0


def test_media_warnings_returns_warnings_from_registry(tmp_path):
    registry_path = tmp_path / "media-registry.json"
    registry_path.write_text(
        json.dumps({
            "version": 1,
            "indexed_at": "2026-06-01T10:00:00+00:00",
            "entries": [],
            "warnings": ["root not found: /missing/path", "importer skipped: generic"],
        }),
        encoding="utf-8",
    )

    payload = json.loads(
        mcp_server.rafiki_media_warnings(
            registry_path=str(registry_path)
        )
    )

    assert payload["success"] is True
    assert payload["ok"] is True
    assert payload["mutating"] is False
    assert payload["external"] is False
    assert payload["count"] == 2
    assert payload["warning_count"] == 2
    assert payload["registry_url"].startswith("file://")
    assert "root not found: /missing/path" in payload["warnings"]
    assert payload["indexed_at"] == "2026-06-01T10:00:00+00:00"


def test_job_status_returns_error_for_missing_job(tmp_path):
    import lib.jobs as jobs_module

    with patch.object(jobs_module, "JOBS_DIR", tmp_path / "jobs"):
        payload = json.loads(mcp_server.rafiki_job_status("nonexistent-job-id"))

    assert payload["success"] is False
    assert payload["ok"] is False
    assert payload["mutating"] is False
    assert payload["external"] is False
    assert "not found" in payload["error"]


def test_job_status_returns_hardened_fields_for_existing_job(tmp_path):
    import lib.jobs as jobs_module

    jobs_dir = tmp_path / "jobs"
    jobs_dir.mkdir()
    job_record = {
        "id": "video-generation-20260601-120000",
        "kind": "video-generation",
        "provider": "Replicate",
        "status": "queued",
        "polling_status": "pending",
        "error": "",
        "target_output_dir": str(tmp_path / "output"),
        "created_at": "2026-06-01T12:00:00+00:00",
        "updated_at": "2026-06-01T12:00:01+00:00",
        "cost_estimate": {"currency": "USD", "amount": 0.0, "estimated": True},
    }
    (jobs_dir / "video-generation-20260601-120000.json").write_text(
        json.dumps(job_record), encoding="utf-8"
    )

    with patch.object(jobs_module, "JOBS_DIR", jobs_dir):
        payload = json.loads(
            mcp_server.rafiki_job_status("video-generation-20260601-120000")
        )

    assert payload["success"] is True
    assert payload["ok"] is True
    assert payload["mutating"] is False
    assert payload["external"] is False
    assert payload["job_id"] == "video-generation-20260601-120000"
    assert payload["status"] == "queued"
    assert payload["polling_status"] == "pending"
    assert payload["error"] == ""
    assert payload["provider"] == "Replicate"
    assert payload["kind"] == "video-generation"
    assert payload["cost_estimate"]["currency"] == "USD"
    assert "job" in payload
    assert payload["job"]["id"] == "video-generation-20260601-120000"


def test_job_status_rejects_blank_job_id():
    payload = json.loads(mcp_server.rafiki_job_status(""))

    assert payload["success"] is False
    assert payload["ok"] is False
    assert payload["mutating"] is False
    assert payload["external"] is False
    assert "job_id is required" in payload["error"]


def test_notion_export_wrapper_dry_run_uses_exporter_without_api(tmp_path):
    output_root = tmp_path / "output"
    approved = output_root / "notion-project" / "approved"
    _write_run(
        approved,
        [{"name": "Week Three", "prompt": "caption", "file": "01-week-03-hello.png"}],
    )

    payload = json.loads(
        mcp_server.rafiki_notion_export(
            "notion-project",
            database_id="db-123",
            output_root=str(output_root),
            dry_run=True,
        )
    )

    assert payload["success"] is True
    assert payload["ok"] is True
    assert payload["dry_run"] is True
    assert payload["mutating"] is False
    assert payload["external"] is True
    assert payload["exported"] == 1
    assert payload["source"] == "approved"
    assert not (output_root / "notion-project" / ".notion-exported.json").exists()

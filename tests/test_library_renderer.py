"""Tests for the master library renderer's registry-backed metadata path."""

from __future__ import annotations

import json
from pathlib import Path

from lib import extra_outputs, registry
from lib.renderers import library


def _isolate_registry(tmp_path, monkeypatch) -> Path:
    output_root = tmp_path / "output"
    output_root.mkdir()
    config_dir = tmp_path / "config"

    monkeypatch.setattr(registry, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(registry, "DEFAULT_OUTPUT_ROOT", output_root)
    monkeypatch.setattr(registry, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(registry, "REGISTRY_JSON", tmp_path / "data" / "asset-registry.json")
    monkeypatch.setattr(registry, "REGISTRY_CSV", tmp_path / "data" / "asset-registry.csv")
    monkeypatch.setattr(extra_outputs, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(extra_outputs, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(extra_outputs, "EXTRA_OUTPUTS_CONFIG", config_dir / "extra-outputs.json")
    monkeypatch.setattr(extra_outputs, "EXTRA_OUTPUTS_LOCAL_CONFIG", config_dir / "extra-outputs.local.json")
    return output_root


def _write_image(path: Path) -> None:
    path.write_bytes(b"not-a-real-png-but-good-enough-for-library-tests")


def _write_run(directory: Path, image_name: str, title: str, prompt: str, **meta) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    _write_image(directory / image_name)
    payload = {
        "model": meta.get("model", "gpt-image-2"),
        "style": meta.get("style", "bcai"),
        "aspect_ratio": meta.get("aspect_ratio", "16:9"),
        "timestamp": meta.get("timestamp", "2026-05-01 12:00"),
        "images": [{"file": image_name, "name": title, "prompt": prompt}],
    }
    for key in ("prompt_file", "prompt_source", "provider", "state", "started_at", "finished_at", "invocation"):
        if key in meta:
            payload[key] = meta[key]
    (directory / "run.json").write_text(json.dumps(payload), encoding="utf-8")


def test_library_uses_all_run_archive_scope_and_marks_approved(tmp_path, monkeypatch):
    output_root = _isolate_registry(tmp_path, monkeypatch)
    project = output_root / "curated-project"
    _write_run(
        project / "run-20260501-120000",
        "draft.png",
        "Draft Title",
        "draft prompt",
    )

    approved = project / "approved"
    approved.mkdir(parents=True)
    (approved / "index.json").write_text(
        json.dumps({
            "images": [{
                "slug": "draft.png",
                "original_file": "draft.png",
                "name": "Registry Title",
                "prompt": "source prompt from approval index",
                "model": "gemini-2.5-flash-image",
                "style": "editorial",
                "aspect_ratio": "9:16",
                "source_run": "run-20260501-120000",
            }]
        }),
        encoding="utf-8",
    )

    records = library._records_from_registry(output_root)

    assert len(records) == 1
    assert records[0]["file"] == "curated-project/run-20260501-120000/draft.png"
    assert records[0]["title"] == "Registry Title"
    assert records[0]["source_prompt"] == "source prompt from approval index"
    assert records[0]["approval_status"] == "approved"
    assert records[0]["model"] == "gemini-2.5-flash-image"
    assert records[0]["style"] == "editorial"
    assert records[0]["aspect_ratio"] == "9:16"
    assert records[0]["source"] == "run"


def test_library_registry_uses_every_run_when_no_approved(tmp_path, monkeypatch):
    output_root = _isolate_registry(tmp_path, monkeypatch)
    project = output_root / "output-only-project"
    _write_run(
        project / "run-20260401-120000",
        "old.png",
        "Old Title",
        "old prompt",
        timestamp="2026-04-01 12:00",
    )
    _write_run(
        project / "run-20260501-120000",
        "new.png",
        "New Title",
        "new prompt",
        model="gpt-image-2",
        style="product",
        aspect_ratio="1:1",
        timestamp="2026-05-01 12:00",
    )

    records = library._records_from_registry(output_root)

    assert [r["file"] for r in records] == [
        "output-only-project/run-20260401-120000/old.png",
        "output-only-project/run-20260501-120000/new.png",
    ]
    newest = records[1]
    assert newest["title"] == "New Title"
    assert newest["source_prompt"] == "new prompt"
    assert newest["approval_status"] == "unapproved"
    assert newest["model"] == "gpt-image-2"
    assert newest["style"] == "product"
    assert newest["aspect_ratio"] == "1:1"


def test_library_viewer_renders_output_only_project_without_prebuilt_registry(tmp_path, monkeypatch):
    output_root = _isolate_registry(tmp_path, monkeypatch)
    _write_run(
        output_root / "plain-project" / "run-20260501-120000",
        "plain.png",
        "Plain Title",
        "plain source prompt",
    )

    viewer = library.generate_library_viewer(output_root)
    html = viewer.read_text(encoding="utf-8")

    assert viewer == output_root / "library.html"
    assert "Plain Title" in html
    assert "plain source prompt" in html
    assert not registry.REGISTRY_JSON.exists()


def test_library_viewer_merges_local_archive_metadata(tmp_path, monkeypatch):
    output_root = _isolate_registry(tmp_path, monkeypatch)
    _write_run(
        output_root / "metadata-project" / "run-20260501-120000",
        "metadata.png",
        "Original Title",
        "metadata source prompt",
    )
    (output_root / "archive-metadata.json").write_text(
        json.dumps({
            "version": 1,
            "items": {
                "metadata-project/run-20260501-120000/metadata.png": {
                    "title": "Homepage Hero",
                    "tags": ["homepage", "keeper"],
                    "states": ["canva", "published"],
                    "superseded_by": "metadata-project/run-20260502-120000/metadata.png",
                }
            },
        }),
        encoding="utf-8",
    )

    html = library.generate_library_viewer(output_root).read_text(encoding="utf-8")

    assert "Homepage Hero" in html
    assert '"metadata_states": ["canva", "published"]' in html
    assert '"superseded_by": "metadata-project/run-20260502-120000/metadata.png"' in html
    assert 'id="run-detail-metadata"' in html
    assert 'id="metadata-title"' in html
    assert "async function saveMetadataForDetail(event)" in html
    assert "fetch('/api/archive-metadata'" in html
    assert 'class="metadata-state-badge"' in html


def test_library_viewer_renders_archive_review_filters_and_keyboard_hooks(tmp_path, monkeypatch):
    output_root = _isolate_registry(tmp_path, monkeypatch)
    project = output_root / "review-project"
    _write_run(
        project / "run-20260501-120000",
        "approved.png",
        "Approved Title",
        "approved prompt",
        timestamp="2026-05-01 12:00",
    )
    _write_run(
        project / "run-20260502-120000",
        "draft.png",
        "Draft Title",
        "draft prompt",
        timestamp="2026-05-02 12:00",
    )
    approved = project / "approved"
    approved.mkdir(parents=True)
    (approved / "index.json").write_text(
        json.dumps({
            "images": [{
                "slug": "approved.png",
                "original_file": "approved.png",
                "source_run": "run-20260501-120000",
                "name": "Approved Title",
                "prompt": "approved prompt",
            }]
        }),
        encoding="utf-8",
    )

    html = library.generate_library_viewer(output_root).read_text(encoding="utf-8")

    assert 'id="source-filter"' in html
    assert 'id="run-filter"' in html
    assert 'id="approval-filter"' in html
    assert 'id="fb-review-queue"' in html
    assert 'id="fc-review-queue"' in html
    assert '<option value="run">run</option>' in html
    assert '<option value="run-20260502-120000">run-20260502-120000</option>' in html
    assert '<option value="run-20260501-120000">run-20260501-120000</option>' in html
    assert '<option value="approved">approved</option>' in html
    assert '<option value="unapproved">unapproved</option>' in html
    assert "card.dataset.source = item.source || ''" in html
    assert "card.dataset.run = item.run_id || ''" in html
    assert "card.dataset.approval = item.approval_status || 'unapproved'" in html
    assert "function handleLibraryKeydown(event)" in html
    assert "function isReviewQueueCard(card, ratingValue)" in html
    assert "isLibraryTypingTarget(event.target)" in html
    assert "rateActiveCard('star')" in html
    assert "rateActiveCard('reject')" in html
    assert "card.active-card" in html


def test_library_viewer_renders_run_detail_panel_metadata_and_links(tmp_path, monkeypatch):
    output_root = _isolate_registry(tmp_path, monkeypatch)
    _write_run(
        output_root / "detail-project" / "run-20260503-120000",
        "detail.png",
        "Detail Title",
        "detail prompt",
        prompt_file="prompts/detail.md",
        prompt_source="prompts/detail.md",
        provider="OpenAI",
        state="succeeded",
        started_at="2026-05-03T12:00:00-07:00",
        finished_at="2026-05-03T12:00:05-07:00",
        invocation={"surface": "portal"},
    )

    html = library.generate_library_viewer(output_root).read_text(encoding="utf-8")

    assert 'id="run-detail-panel"' in html
    assert "const RUN_DETAILS =" in html
    assert '"detail-project/run-20260503-120000"' in html
    assert '"prompt_file": "prompts/detail.md"' in html
    assert '"prompt_source": "prompts/detail.md"' in html
    assert '"invocation_surface": "portal"' in html
    assert '"run_json": "detail-project/run-20260503-120000/run.json"' in html
    assert '"run_viewer": "detail-project/run-20260503-120000/viewer.html"' in html
    assert '"project_viewer": "detail-project/viewer.html"' in html
    assert "function showRunDetail(item)" in html
    assert "openRunDetail(event," in html
    assert "I details" in html


def test_library_viewer_warns_about_duplicate_and_similar_filenames(tmp_path, monkeypatch):
    output_root = _isolate_registry(tmp_path, monkeypatch)
    duplicate_project = output_root / "duplicate-project"
    _write_run(
        duplicate_project / "run-20260504-120000",
        "01-hero.png",
        "Hero One",
        "first hero prompt",
    )
    _write_run(
        duplicate_project / "run-20260505-120000",
        "01-hero.png",
        "Hero Two",
        "second hero prompt",
    )
    similar_project = output_root / "similar-project"
    _write_run(
        similar_project / "run-20260506-120000",
        "01-poster.png",
        "Poster One",
        "first poster prompt",
    )
    _write_run(
        similar_project / "run-20260507-120000",
        "02-poster.png",
        "Poster Two",
        "second poster prompt",
    )

    html = library.generate_library_viewer(output_root).read_text(encoding="utf-8")

    assert '"filename_warning": {' in html
    assert '"label": "Duplicate filename"' in html
    assert '"level": "exact"' in html
    assert '"basename": "01-hero.png"' in html
    assert '"run_id": "run-20260504-120000"' in html
    assert '"run_id": "run-20260505-120000"' in html
    assert '"label": "Similar filename"' in html
    assert '"level": "similar"' in html
    assert '"normalized_stem": "poster"' in html
    assert '"group_basenames": ["01-poster.png", "02-poster.png"]' in html
    assert 'id="run-detail-warning"' in html
    assert "function renderFilenameWarning(item)" in html
    assert "card.dataset.warning = item.filename_warning?.level || ''" in html
    assert 'class="filename-warning-badge"' in html


def test_library_viewer_renders_usage_feedback_and_revision_hooks(tmp_path, monkeypatch):
    output_root = _isolate_registry(tmp_path, monkeypatch)
    _write_run(
        output_root / "ops-project" / "run-20260508-120000",
        "ops.png",
        "Ops Title",
        "ops prompt",
        model="gpt-image-2",
        style="bcai",
        aspect_ratio="1:1",
    )

    html = library.generate_library_viewer(output_root).read_text(encoding="utf-8")

    assert 'id="ops-panel"' in html
    assert 'id="usage-known-cost"' in html
    assert 'id="usage-billing-amount"' in html
    assert 'id="billing-import-form"' in html
    assert 'id="deploy-readiness-checks"' in html
    assert "async function loadUsageSummary()" in html
    assert "async function saveBillingEntry(event)" in html
    assert "function resolveAssetSrc(path)" in html
    assert "fetch('/api/usage')" in html
    assert "fetch('/api/billing-imports'" in html
    assert "fetch('/api/deploy-readiness')" in html
    assert 'id="run-detail-feedback"' in html
    assert 'id="run-detail-metadata"' in html
    assert 'id="feedback-change-request"' in html
    assert 'id="metadata-state-grid"' in html
    assert "async function saveFeedbackForDetail(event)" in html
    assert "async function saveMetadataForDetail(event)" in html
    assert "fetch('/api/feedback'" in html
    assert "fetch('/api/archive-metadata'" in html
    assert "function stageRevisionFromDetail(event, autoSubmit)" in html
    assert "async function copyPromptForCard(event, idx)" in html
    assert 'class="feedback-badge"' in html
    assert 'class="metadata-state-badge"' in html
    assert 'class="lineage-chip lineage-run"' in html
    assert 'class="lineage-copy"' in html


def test_library_viewer_renders_modes_and_curriculum_atlas(tmp_path, monkeypatch):
    output_root = _isolate_registry(tmp_path, monkeypatch)
    _write_run(
        output_root / "rap-week-2" / "run-20260509-120000",
        "bias-map.png",
        "Bias Map",
        "Map bias, ethics, and accountability in responsible AI systems.",
        model="gemini-2.5-flash-image",
        style="bcai",
        aspect_ratio="16:9",
    )

    html = library.generate_library_viewer(output_root).read_text(encoding="utf-8")

    assert 'class="portal-mode-nav"' in html
    assert 'data-mode-target="review"' in html
    assert 'id="portal-mode-review"' in html
    assert 'id="portal-mode-generate"' in html
    assert 'id="portal-mode-curate"' in html
    assert 'id="portal-mode-spend"' in html
    assert 'id="portal-mode-teach"' in html
    assert 'id="curriculum-atlas-panel"' in html
    assert "Responsible AI Program" in html
    assert "Facilitator Notes" in html
    assert "Discussion Prompts" in html
    assert "Critique Rubric" in html
    assert "Concept Links" in html
    assert "Foundation clarity" in html
    assert "AI literacy" in html
    assert 'class="atlas-rubric-item"' in html
    assert 'class="atlas-concept-link"' in html
    assert 'class="atlas-concept-graph"' in html
    assert 'class="atlas-graph-nodes"' in html
    assert 'aria-label="Curriculum concept relationships"' in html
    assert '"linked_assets": 1' in html
    assert "const CURRICULUM_ATLAS =" in html
    assert "function setPortalMode(mode)" in html
    assert "function focusAtlasModule(programId, moduleId)" in html
    assert "function focusAtlasUnmapped()" in html
    assert "clearAtlasAssetFilter(false)" in html
    assert ":focus-visible" in html
    assert "prefers-reduced-motion" in html
    assert "transition: all" not in html

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lib.archive_metadata import load_archive_metadata, stamp_archive_state, update_archive_metadata


def test_update_archive_metadata_persists_title_tags_and_states(tmp_path: Path):
    path = tmp_path / "archive-metadata.json"

    result = update_archive_metadata(
        path,
        {
            "key": "demo/run-1/hero.png",
            "title": "Homepage Hero",
            "tags": "homepage, keeper, homepage",
            "states": ["canva", "published"],
            "superseded_by": "demo/run-2/hero.png",
        },
    )

    assert result["ok"] is True
    saved = load_archive_metadata(path)
    entry = saved["items"]["demo/run-1/hero.png"]
    assert entry["title"] == "Homepage Hero"
    assert entry["tags"] == ["homepage", "keeper"]
    assert entry["states"] == ["canva", "published"]
    assert entry["superseded_by"] == "demo/run-2/hero.png"
    assert entry["updated_at"]


def test_update_archive_metadata_persists_artifact_chain_fields(tmp_path: Path):
    path = tmp_path / "archive-metadata.json"

    result = update_archive_metadata(
        path,
        {
            "key": "demo/run-1/hero.png",
            "source_use_case": "Keynote visual workflow",
            "source_url": "https://kriskrug.co/2026/06/04/ai-keynote-slides-visual-workflow/",
            "prompt_pack": "examples/keynote-visual-workflow-prompt-pack.md",
            "prompt_pack_section": "3. Review Gate And Anti-Slop Selector",
            "artifact_review_state": "manual-rebuild",
            "export_targets": ["canva", "deck", "canva"],
            "downstream_uses": "slide, blog-post, guide",
        },
    )

    assert result["ok"] is True
    entry = load_archive_metadata(path)["items"]["demo/run-1/hero.png"]
    assert entry["source_use_case"] == "Keynote visual workflow"
    assert entry["source_url"] == "https://kriskrug.co/2026/06/04/ai-keynote-slides-visual-workflow/"
    assert entry["prompt_pack"] == "examples/keynote-visual-workflow-prompt-pack.md"
    assert entry["prompt_pack_section"] == "3. Review Gate And Anti-Slop Selector"
    assert entry["artifact_review_state"] == "manual-rebuild"
    assert entry["export_targets"] == ["canva", "deck"]
    assert entry["downstream_uses"] == ["slide", "blog-post", "guide"]


def test_update_archive_metadata_preserves_unmentioned_artifact_fields(tmp_path: Path):
    path = tmp_path / "archive-metadata.json"
    update_archive_metadata(
        path,
        {
            "key": "demo/run-1/hero.png",
            "source_use_case": "Keynote visual workflow",
            "artifact_review_state": "approved",
        },
    )

    update_archive_metadata(path, {"key": "demo/run-1/hero.png", "title": "Hero"})

    entry = load_archive_metadata(path)["items"]["demo/run-1/hero.png"]
    assert entry["title"] == "Hero"
    assert entry["source_use_case"] == "Keynote visual workflow"
    assert entry["artifact_review_state"] == "approved"


def test_update_archive_metadata_removes_empty_entry(tmp_path: Path):
    path = tmp_path / "archive-metadata.json"
    path.write_text(
        json.dumps({"version": 1, "items": {"demo/run-1/hero.png": {"title": "Old"}}}),
        encoding="utf-8",
    )

    result = update_archive_metadata(path, {"key": "demo/run-1/hero.png"})

    assert result == {"ok": True, "key": "demo/run-1/hero.png", "metadata": None}
    assert load_archive_metadata(path)["items"] == {}


def test_update_archive_metadata_rejects_unknown_states(tmp_path: Path):
    with pytest.raises(ValueError, match="states must contain only"):
        update_archive_metadata(
            tmp_path / "archive-metadata.json",
            {"key": "demo/run-1/hero.png", "states": ["emailed"]},
        )


def test_update_archive_metadata_rejects_unknown_artifact_review_state(tmp_path: Path):
    with pytest.raises(ValueError, match="artifact_review_state must be one of"):
        update_archive_metadata(
            tmp_path / "archive-metadata.json",
            {"key": "demo/run-1/hero.png", "artifact_review_state": "maybe"},
        )


def test_update_archive_metadata_rejects_private_prompt_pack_path(tmp_path: Path):
    with pytest.raises(ValueError, match="prompt_pack must be a repo-relative path"):
        update_archive_metadata(
            tmp_path / "archive-metadata.json",
            {"key": "demo/run-1/hero.png", "prompt_pack": "/Users/kk/private/image-prompts.md"},
        )


def test_stamp_archive_state_preserves_existing_metadata(tmp_path: Path):
    path = tmp_path / "archive-metadata.json"
    update_archive_metadata(
        path,
        {
            "key": "demo/run-1/hero.png",
            "title": "Homepage Hero",
            "tags": ["keeper"],
            "states": ["canva"],
        },
    )

    result = stamp_archive_state(path, ["demo/run-1/hero.png"], "notion")

    assert result["stamped"] == 1
    entry = load_archive_metadata(path)["items"]["demo/run-1/hero.png"]
    assert entry["title"] == "Homepage Hero"
    assert entry["tags"] == ["keeper"]
    assert entry["states"] == ["canva", "notion"]

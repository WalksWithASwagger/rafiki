"""Tests for lib.registry — index, search, export."""

from __future__ import annotations

import csv
import json
import struct
import sys
import zlib
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib import extra_outputs
from lib import registry


def _make_png(path: Path) -> None:
    """Write a minimal valid 1x1 PNG so glob('*.png') picks it up."""
    sig = b"\x89PNG\r\n\x1a\n"

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    raw = b"\x00\xff\xff\xff"
    idat = zlib.compress(raw)
    path.write_bytes(sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b""))


@pytest.fixture
def isolated_registry(tmp_path, monkeypatch):
    """Redirect registry's repo-root-relative paths into tmp_path."""
    output_root = tmp_path / "output"
    output_root.mkdir()
    data_dir = tmp_path / "data"
    extra_config = tmp_path / "config" / "extra-outputs.json"
    extra_local_config = tmp_path / "config" / "extra-outputs.local.json"

    monkeypatch.setattr(registry, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(registry, "DEFAULT_OUTPUT_ROOT", output_root)
    monkeypatch.setattr(registry, "DATA_DIR", data_dir)
    monkeypatch.setattr(registry, "REGISTRY_JSON", data_dir / "asset-registry.json")
    monkeypatch.setattr(registry, "REGISTRY_CSV", data_dir / "asset-registry.csv")
    monkeypatch.setattr(extra_outputs, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(extra_outputs, "CONFIG_DIR", tmp_path / "config")
    monkeypatch.setattr(extra_outputs, "EXTRA_OUTPUTS_CONFIG", extra_config)
    monkeypatch.setattr(extra_outputs, "EXTRA_OUTPUTS_LOCAL_CONFIG", extra_local_config)
    return tmp_path


def _write_run_json(directory: Path, images: list[dict], **meta) -> None:
    payload = {
        "model": meta.get("model", "gpt-image-2"),
        "aspect_ratio": meta.get("aspect_ratio", "16:9"),
        "style": meta.get("style", "bcai"),
        "images": images,
    }
    (directory / "run.json").write_text(json.dumps(payload), encoding="utf-8")


def test_index_walks_approved_dir(isolated_registry):
    project = isolated_registry / "output" / "test-project"
    approved = project / "approved"
    approved.mkdir(parents=True)
    _make_png(approved / "01-hero.png")
    _make_png(approved / "02-detail.png")
    _write_run_json(
        approved,
        [
            {"name": "Hero", "prompt": "a hero", "file": "01-hero.png"},
            {"name": "Detail", "prompt": "a detail", "file": "02-detail.png"},
        ],
        style="bcai",
    )

    entries = registry.index()

    assert len(entries) == 2
    assert {e.id for e in entries} == {"test-project-01-hero", "test-project-02-detail"}
    assert all(e.project == "test-project" for e in entries)
    assert all(e.style == "bcai" for e in entries)


def test_index_falls_back_to_latest_run_when_no_approved(isolated_registry):
    project = isolated_registry / "output" / "fallback-project"
    older = project / "run-20260101-000000"
    newer = project / "run-20260201-000000"
    older.mkdir(parents=True)
    newer.mkdir(parents=True)

    _make_png(older / "old.png")
    _write_run_json(older, [{"name": "Old", "prompt": "old", "file": "old.png"}])

    _make_png(newer / "new.png")
    _write_run_json(newer, [{"name": "New", "prompt": "new", "file": "new.png"}])

    entries = registry.index()

    assert len(entries) == 1
    assert entries[0].id == "fallback-project-new"


def test_search_case_insensitive_substring(isolated_registry):
    project = isolated_registry / "output" / "search-project"
    approved = project / "approved"
    approved.mkdir(parents=True)
    for f in ("hallucination.png", "bias.png", "permission.png"):
        _make_png(approved / f)
    _write_run_json(
        approved,
        [
            {"name": "The Hallucination Problem", "prompt": "confident wrong", "file": "hallucination.png"},
            {"name": "Bias In The Machine", "prompt": "skewed data", "file": "bias.png"},
            {"name": "Permission Point", "prompt": "open the door", "file": "permission.png"},
        ],
    )

    registry.index()

    assert {e.id for e in registry.search("HALLUCINATION")} == {"search-project-hallucination"}
    assert {e.id for e in registry.search("bias")} == {"search-project-bias"}
    assert registry.search("nonexistent") == []


def test_search_matches_caption_and_tags(isolated_registry):
    project = isolated_registry / "output" / "fields-project"
    approved = project / "approved"
    approved.mkdir(parents=True)
    for f in ("a.png", "b.png", "c.png"):
        _make_png(approved / f)
    _write_run_json(
        approved,
        [
            {"name": "Alpha", "prompt": "uniqueprompttoken in caption", "file": "a.png"},
            {"name": "Beta", "prompt": "no match here", "file": "b.png", "tags": ["uniquetagtoken"]},
            {"name": "uniquetitletoken Gamma", "prompt": "still none", "file": "c.png"},
        ],
        aspect_ratio="9:16",
    )

    registry.index()

    assert [e.id for e in registry.search("uniquepromptt")] == ["fields-project-a"]
    assert [e.id for e in registry.search("uniquetagtoken")] == ["fields-project-b"]
    assert [e.id for e in registry.search("uniquetitletoken")] == ["fields-project-c"]
    # aspect_ratio gets injected as a tag
    assert {e.id for e in registry.search("9:16")} == {
        "fields-project-a",
        "fields-project-b",
        "fields-project-c",
    }


def test_export_csv_has_all_columns(isolated_registry):
    project = isolated_registry / "output" / "csv-project"
    approved = project / "approved"
    approved.mkdir(parents=True)
    _make_png(approved / "only.png")
    _write_run_json(approved, [{"name": "Only", "prompt": "p", "file": "only.png"}])

    registry.index()
    csv_path = registry.export(format="csv")

    assert csv_path.exists()
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == registry.CSV_COLUMNS
        rows = list(reader)
    assert len(rows) == 1
    assert rows[0]["id"] == "csv-project-only"
    assert rows[0]["project"] == "csv-project"


def test_index_is_resilient_to_malformed_run_json(isolated_registry):
    """Project with bad run.json should be skipped, not crash the indexer."""
    bad_project = isolated_registry / "output" / "bad-project"
    bad_approved = bad_project / "approved"
    bad_approved.mkdir(parents=True)
    _make_png(bad_approved / "x.png")
    (bad_approved / "run.json").write_text("not-json{", encoding="utf-8")

    good_project = isolated_registry / "output" / "good-project"
    good_approved = good_project / "approved"
    good_approved.mkdir(parents=True)
    _make_png(good_approved / "y.png")
    _write_run_json(good_approved, [{"name": "Y", "prompt": "", "file": "y.png"}])

    entries = registry.index()
    ids = {e.id for e in entries}
    # malformed run.json => no metadata, but the PNG is still indexed with derived title
    assert "good-project-y" in ids
    assert "bad-project-x" in ids


def test_local_extra_outputs_override_wins(isolated_registry):
    config_dir = isolated_registry / "config"
    config_dir.mkdir(parents=True, exist_ok=True)

    local_project = isolated_registry / "external-project"
    approved = local_project / "approved"
    approved.mkdir(parents=True)
    _make_png(approved / "hero.png")
    _write_run_json(
        approved,
        [{"name": "Hero", "prompt": "from local override", "file": "hero.png"}],
        style="kk",
    )

    (config_dir / "extra-outputs.json").write_text(
        json.dumps({"external": str(isolated_registry / "missing-project")}),
        encoding="utf-8",
    )
    (config_dir / "extra-outputs.local.json").write_text(
        json.dumps({"external": str(local_project)}),
        encoding="utf-8",
    )

    entries = registry.index()

    assert len(entries) == 1
    assert entries[0].project == "external"
    assert entries[0].style == "kk"

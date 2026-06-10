"""Tests for lib.lineage.suggest_lineage_candidates."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.lineage import (
    _jaccard,
    _slug_base,
    _title_words,
    suggest_lineage_candidates,
)
from lib.registry import AssetEntry


# ── unit helpers ─────────────────────────────────────────────────────────────

def test_slug_base_strips_version_suffix():
    assert _slug_base("hero-v2") == "hero"
    assert _slug_base("poster-v10") == "poster"
    assert _slug_base("banner-alt") == "banner"
    assert _slug_base("protest-poster-2") == "protest-poster"
    assert _slug_base("hero-r3") == "hero"
    assert _slug_base("take-v2-alt") == "take"


def test_slug_base_leaves_base_unchanged():
    assert _slug_base("hero") == "hero"
    assert _slug_base("protest-poster") == "protest-poster"
    assert _slug_base("banner") == "banner"


def test_title_words_filters_short_words():
    assert _title_words("AI in the wild") == frozenset({"wild"})
    assert _title_words("Climate Justice Now") == frozenset({"climate", "justice"})


def test_jaccard_symmetric_and_bounded():
    a = frozenset({"cat", "dog", "bird"})
    b = frozenset({"cat", "dog", "fish"})
    j = _jaccard(a, b)
    assert 0.0 < j < 1.0
    assert _jaccard(a, b) == _jaccard(b, a)


def test_jaccard_empty_returns_zero():
    assert _jaccard(frozenset(), frozenset({"cat"})) == 0.0
    assert _jaccard(frozenset(), frozenset()) == 0.0


# ── suggest_lineage_candidates ────────────────────────────────────────────────

def _entry(project: str, stem: str, title: str, superseded_by: str = "") -> AssetEntry:
    return AssetEntry(
        id=f"{project}-{stem}",
        project=project,
        title=title,
        caption="",
        path=f"output/{project}/approved/{stem}.png",
        superseded_by=superseded_by,
    )


def test_no_match_returns_empty():
    entries = [
        _entry("proj", "hero", "The Hero Image"),
        _entry("proj", "landscape", "A Landscape Scene"),
    ]
    assert suggest_lineage_candidates(entries) == []


def test_slug_base_match_produces_suggestion():
    entries = [
        _entry("proj", "hero", "Hero"),
        _entry("proj", "hero-v2", "Hero V2"),
    ]
    suggestions = suggest_lineage_candidates(entries)
    assert len(suggestions) == 1
    s = suggestions[0]
    assert s["project"] == "proj"
    assert any("slug base match" in r for r in s["reasons"])
    assert {"proj-hero", "proj-hero-v2"} == {s["source_id"], s["candidate_id"]}


def test_title_overlap_produces_suggestion():
    entries = [
        _entry("proj", "img1", "Climate Justice Poster"),
        _entry("proj", "img2", "Climate Justice Banner"),
    ]
    suggestions = suggest_lineage_candidates(entries)
    assert len(suggestions) == 1
    assert any("title overlap" in r for r in suggestions[0]["reasons"])


def test_ambiguous_multiple_candidates():
    entries = [
        _entry("proj", "protest-v1", "Protest Poster"),
        _entry("proj", "protest-v2", "Protest Poster Version Two"),
        _entry("proj", "protest-v3", "Protest Poster Third Take"),
    ]
    suggestions = suggest_lineage_candidates(entries)
    # All three pairs should be suggested (slug base "protest" for all).
    pair_ids = {(s["source_id"], s["candidate_id"]) for s in suggestions}
    assert len(pair_ids) == 3


def test_explicitly_linked_pair_excluded():
    """Entries connected by superseded_by must not appear in suggestions."""
    entries = [
        _entry("proj", "hero", "Hero", superseded_by="proj-hero-v2"),
        _entry("proj", "hero-v2", "Hero V2"),
    ]
    suggestions = suggest_lineage_candidates(entries)
    assert suggestions == []


def test_cross_project_entries_not_paired():
    entries = [
        _entry("project-a", "hero", "Hero"),
        _entry("project-b", "hero-v2", "Hero V2"),
    ]
    assert suggest_lineage_candidates(entries) == []


def test_suggestion_fields_are_complete():
    entries = [
        _entry("proj", "banner", "Banner Artwork"),
        _entry("proj", "banner-alt", "Banner Artwork Alt"),
    ]
    s = suggest_lineage_candidates(entries)[0]
    assert "source_id" in s
    assert "candidate_id" in s
    assert "source_path" in s
    assert "candidate_path" in s
    assert "project" in s
    assert isinstance(s["reasons"], list)
    assert s["reasons"]


def test_read_only_entries_not_mutated():
    entries = [
        _entry("proj", "hero", "Hero"),
        _entry("proj", "hero-v2", "Hero"),
    ]
    originals = [(e.id, e.superseded_by) for e in entries]
    suggest_lineage_candidates(entries)
    assert [(e.id, e.superseded_by) for e in entries] == originals


# ── CLI surface ───────────────────────────────────────────────────────────────

def test_cmd_registry_suggest_lineage_no_matches(tmp_path, monkeypatch, capsys):
    import json as _json

    from lib import registry, extra_outputs
    from lib.commands.registry_cmds import _cmd_registry

    output_root = tmp_path / "output"
    data_dir = tmp_path / "data"
    output_root.mkdir()

    monkeypatch.setattr(registry, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(registry, "DATA_DIR", data_dir)
    monkeypatch.setattr(registry, "DEFAULT_OUTPUT_ROOT", output_root)
    monkeypatch.setattr(registry, "REGISTRY_JSON", data_dir / "asset-registry.json")
    monkeypatch.setattr(registry, "REGISTRY_CSV", data_dir / "asset-registry.csv")
    monkeypatch.setattr(registry, "_load_extra_roots", lambda: {})

    # One project, two unrelated images — no suggestions expected.
    proj = output_root / "demo" / "approved"
    proj.mkdir(parents=True)

    sig = b"\x89PNG\r\n\x1a\n"
    (proj / "hero.png").write_bytes(sig)
    (proj / "landscape.png").write_bytes(sig)
    (proj / "run.json").write_text(
        _json.dumps({
            "model": "gpt-image-2",
            "aspect_ratio": "16:9",
            "style": "bcai",
            "images": [
                {"name": "Hero", "prompt": "a hero", "file": "hero.png"},
                {"name": "Rolling Hills", "prompt": "hills", "file": "landscape.png"},
            ],
        }),
        encoding="utf-8",
    )

    _cmd_registry(["suggest-lineage"])
    out = capsys.readouterr().out
    assert "No unlinked lineage candidates" in out


def test_cmd_registry_suggest_lineage_with_match(tmp_path, monkeypatch, capsys):
    import json as _json

    from lib import registry
    from lib.commands.registry_cmds import _cmd_registry

    output_root = tmp_path / "output"
    data_dir = tmp_path / "data"
    output_root.mkdir()

    monkeypatch.setattr(registry, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(registry, "DATA_DIR", data_dir)
    monkeypatch.setattr(registry, "DEFAULT_OUTPUT_ROOT", output_root)
    monkeypatch.setattr(registry, "REGISTRY_JSON", data_dir / "asset-registry.json")
    monkeypatch.setattr(registry, "REGISTRY_CSV", data_dir / "asset-registry.csv")
    monkeypatch.setattr(registry, "_load_extra_roots", lambda: {})

    proj = output_root / "demo" / "approved"
    proj.mkdir(parents=True)

    sig = b"\x89PNG\r\n\x1a\n"
    (proj / "hero.png").write_bytes(sig)
    (proj / "hero-v2.png").write_bytes(sig)
    (proj / "run.json").write_text(
        _json.dumps({
            "model": "gpt-image-2",
            "aspect_ratio": "16:9",
            "style": "bcai",
            "images": [
                {"name": "Hero", "prompt": "a hero", "file": "hero.png"},
                {"name": "Hero V2", "prompt": "a hero v2", "file": "hero-v2.png"},
            ],
        }),
        encoding="utf-8",
    )

    _cmd_registry(["suggest-lineage"])
    out = capsys.readouterr().out
    assert "lineage suggestion" in out
    assert "demo" in out
    assert "hero" in out


def test_cmd_registry_suggest_lineage_json_output(tmp_path, monkeypatch, capsys):
    import json as _json

    from lib import registry
    from lib.commands.registry_cmds import _cmd_registry

    output_root = tmp_path / "output"
    data_dir = tmp_path / "data"
    output_root.mkdir()

    monkeypatch.setattr(registry, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(registry, "DATA_DIR", data_dir)
    monkeypatch.setattr(registry, "DEFAULT_OUTPUT_ROOT", output_root)
    monkeypatch.setattr(registry, "REGISTRY_JSON", data_dir / "asset-registry.json")
    monkeypatch.setattr(registry, "REGISTRY_CSV", data_dir / "asset-registry.csv")
    monkeypatch.setattr(registry, "_load_extra_roots", lambda: {})

    proj = output_root / "demo" / "approved"
    proj.mkdir(parents=True)

    sig = b"\x89PNG\r\n\x1a\n"
    (proj / "poster.png").write_bytes(sig)
    (proj / "poster-alt.png").write_bytes(sig)
    (proj / "run.json").write_text(
        _json.dumps({
            "model": "gpt-image-2",
            "aspect_ratio": "16:9",
            "style": "bcai",
            "images": [
                {"name": "Poster", "prompt": "a poster", "file": "poster.png"},
                {"name": "Poster Alt", "prompt": "a poster alt", "file": "poster-alt.png"},
            ],
        }),
        encoding="utf-8",
    )

    _cmd_registry(["suggest-lineage", "--json"])
    raw = capsys.readouterr().out
    data = _json.loads(raw)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["project"] == "demo"
    assert data[0]["reasons"]

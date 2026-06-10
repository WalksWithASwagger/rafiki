"""Fixture-driven tests for real importer output shapes.

Each test loads a committed JSON fixture from tests/fixtures/alex_samuel/,
wires its path references into a synthetic tmp_path tree, and asserts that
the alex-samuel importer produces the expected normalized records and warnings.

Fixture design rules:
- No private media paths; all paths are synthetic and local to tmp_path.
- Fixtures model real manifest shapes (field names, nesting) without real subjects.
- Media files written as empty or minimal byte stubs.
"""

from __future__ import annotations

import json
from pathlib import Path

from lib.importers import alex_samuel

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "alex_samuel"


def _write(path: Path, content: bytes = b"\xff\xd8") -> Path:
    """Write a stub file, using a minimal JPEG header so suffix checks work."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def _write_json(path: Path, data) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _load_fixture(name: str) -> object:
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


def _patch_placeholder_paths(data, placeholder: str, replacement: str) -> object:
    """Recursively replace __placeholder__ in string values."""
    if isinstance(data, dict):
        return {k: _patch_placeholder_paths(v, placeholder, replacement) for k, v in data.items()}
    if isinstance(data, list):
        return [_patch_placeholder_paths(item, placeholder, replacement) for item in data]
    if isinstance(data, str):
        return data.replace(placeholder, replacement)
    return data


# ---------------------------------------------------------------------------
# Shape 1: Alexandra benchmark results (v4_benchmark) + cross-version results
# ---------------------------------------------------------------------------


def test_benchmark_fixture_shape_produces_expected_entries_and_evaluation_records(tmp_path: Path) -> None:
    """benchmark_results.json shape: list of prediction dicts with output_file + output_url."""
    root = tmp_path / "media"

    # Write the stub image files the fixture references
    bench_a = root / "evals" / "v4_benchmark" / "version-a" / "01_core_01.jpg"
    bench_b = root / "evals" / "v4_benchmark" / "version-a" / "11_style_01.jpg"
    _write(bench_a)
    _write(bench_b)

    raw = _load_fixture("benchmark_results.json")
    patched = _patch_placeholder_paths(raw, "__placeholder__", str(root))
    manifest = root / "evals" / "v4_benchmark_results.json"
    _write_json(manifest, patched)

    result = alex_samuel.import_root(root, root_key="fixture")
    entries = result.to_dict()["entries"]

    bench_entries = [e for e in entries if e["source_manifest"].endswith("v4_benchmark_results.json")]
    assert len(bench_entries) == 2, f"expected 2 benchmark entries, got {len(bench_entries)}"
    assert all(e["kind"] == "image" for e in bench_entries)
    assert all(e["collection"] == "predictions" for e in bench_entries)
    assert {e["title"] for e in bench_entries} == {"core_01", "style_01"}
    assert all(e["model"] == "version-a" for e in bench_entries)
    assert all(e["metadata"]["version_ref"].endswith(":version-a") for e in bench_entries)

    # The manifest itself should be indexed as an evaluation record
    eval_entries = [e for e in entries if e["kind"] == "evaluation" and e["relative_path"] == "evals/v4_benchmark_results.json"]
    assert len(eval_entries) == 1


def test_cross_version_fixture_shape_indexes_local_and_remote_only_predictions(tmp_path: Path) -> None:
    """cross_version_results.json shape: local output_file entry + remote-only entry."""
    root = tmp_path / "media"

    cross_img = root / "evals" / "cross_version" / "version-b" / "01_closeup.jpg"
    _write(cross_img)

    raw = _load_fixture("cross_version_results.json")
    patched = _patch_placeholder_paths(raw, "__placeholder__", str(root))
    manifest = root / "evals" / "cross_version_results.json"
    _write_json(manifest, patched)

    result = alex_samuel.import_root(root, root_key="fixture")
    entries = result.to_dict()["entries"]

    cross_entries = [e for e in entries if e["source_manifest"].endswith("cross_version_results.json")]
    assert len(cross_entries) == 2
    assert all(e["collection"] == "predictions" for e in cross_entries)
    assert {e["title"] for e in cross_entries} == {"closeup", "full_body"}

    local_entry = next(e for e in cross_entries if e["title"] == "closeup")
    remote_entry = next(e for e in cross_entries if e["title"] == "full_body")

    assert local_entry["kind"] == "image"
    assert local_entry["metadata"]["version_ref"].endswith(":version-b")
    # Remote-only entry has no local file; importer demotes it to prediction kind
    assert remote_entry["kind"] == "prediction"
    assert remote_entry["source_url"] == "https://example.com/cross-full-body.jpg"

    # Warning: one remote-only prediction without local file
    assert any("remote-only" in w for w in result.warnings)


# ---------------------------------------------------------------------------
# Shape 2: Kris wave predictions — local + remote + missing-local variants
# ---------------------------------------------------------------------------


def test_wave_predictions_fixture_shape_counts_and_warning_surfaces(tmp_path: Path) -> None:
    """wave_predictions.json shape: local file, remote-only dict output, missing local file."""
    root = tmp_path / "media"
    subject = "subject"
    wave_dir = root / "evals" / "experiments" / subject / "wave1"

    hero = wave_dir / "outputs" / "hero.png"
    _write(hero)
    # outputs/does-not-exist.png intentionally NOT written

    _write_json(wave_dir / "predictions.json", _load_fixture("wave_predictions.json"))

    result = alex_samuel.import_root(root, root_key="fixture")
    entries = result.to_dict()["entries"]

    wave_entries = [e for e in entries if "wave1/predictions.json" in e.get("source_manifest", "")]
    assert len(wave_entries) == 3

    # Titles resolve from prompt_key field (the first title-candidate the importer finds)
    hero_entry = next(e for e in wave_entries if e["title"] == "hero")
    assert hero_entry["kind"] == "image"
    assert hero_entry["subject"] == subject

    # Remote-only entry (output is a dict with url key) indexed as prediction
    remote_entry = next(e for e in wave_entries if e["title"] == "remote")
    assert remote_entry["kind"] == "prediction"
    assert remote_entry["source_url"] == "https://example.com/wave-remote.png"

    # Missing-local entry: file referenced but absent — demoted to prediction, warning issued
    missing_entry = next(e for e in wave_entries if e["title"] == "missing")
    assert missing_entry["kind"] == "prediction"

    assert any("1 prediction output(s) reference missing local files" in w for w in result.warnings)
    assert any("remote-only prediction output(s) indexed without local media" in w for w in result.warnings)


# ---------------------------------------------------------------------------
# Shape 3: Song manifest (storyboard.json) + style-anchor extraction
# ---------------------------------------------------------------------------


def test_storyboard_fixture_shape_indexes_manifest_with_correct_project_and_collection(tmp_path: Path) -> None:
    """storyboard.json shape: title/artist/scenes list, indexed as storyboard under video collection."""
    root = tmp_path / "media"
    project_dir = root / "video_project" / "song_fixture"

    _write_json(project_dir / "storyboard.json", _load_fixture("storyboard.json"))
    # Stub clip so the project directory exists and media walk finds something
    _write(project_dir / "clips" / "s01" / "shot.mp4", b"\x00\x00\x00\x18")

    result = alex_samuel.import_root(root, root_key="fixture")
    entries = result.to_dict()["entries"]

    storyboard_entries = [e for e in entries if e["kind"] == "storyboard"]
    assert len(storyboard_entries) >= 1

    sb = next(e for e in storyboard_entries if "song_fixture/storyboard.json" in e["relative_path"])
    assert sb["collection"] == "video"
    # Subdirectories under video_project/ that are not named both_hands_full or time_airport
    # fall through to the default project label used by the importer.
    assert sb["project"] == "dont_need_your_permission"
    assert sb["relative_path"].endswith("storyboard.json")


def test_style_anchor_fixture_shape_extracts_name_suffix_and_metadata(tmp_path: Path) -> None:
    """style_anchors.json shape: version/style_suffix/negative_suffix/source block."""
    root = tmp_path / "media"
    anchor_path = root / "video_project" / "song_fixture" / "style_anchors_cinematic_v1.json"
    _write_json(anchor_path, _load_fixture("style_anchors.json"))

    result = alex_samuel.import_root(root, root_key="fixture")
    payload = result.to_dict()

    assert len(payload["styles"]) == 1
    style = payload["styles"][0]
    assert style["name"] == "cinematic_v1"
    assert style["suffix"] == "cinematic depth of field golden hour"
    assert style["negative_suffix"] == "plastic skin overexposed flat"
    assert style["metadata"]["source"]["starred_prompt_count"] == 4
    assert style["metadata"]["source"]["top_runs"][0]["run_id"] == "wave1"

    # Style also appears as an indexed entry in the entries list
    style_entries = [e for e in payload["entries"] if e["kind"] == "style"]
    assert len(style_entries) == 1
    assert style_entries[0]["style"] == "cinematic_v1"
    assert style_entries[0]["collection"] == "styles"

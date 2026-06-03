from __future__ import annotations

import json
from pathlib import Path

from lib.importers import alex_samuel
from lib.media_registry import index, search
from lib.media_roots import MediaRoot


def _write(path: Path, content: bytes = b"data") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def _write_json(path: Path, data) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _alex_fixture(tmp_path: Path) -> Path:
    root = tmp_path / "alex-samuel"
    _write(root / ".env", b"REPLICATE_API_TOKEN=secret")
    _write(root / ".git" / "objects" / "ignored.jpg", b"ignored")
    _write(root / "clients" / "kris" / "album" / "portrait.jpg")
    _write_json(root / "clients" / "kris" / "prompt_suite.json", [{"id": 1, "prompt": "KRIS portrait"}])
    _write(root / "evals" / "experiments" / "kris" / "wave1" / "outputs" / "hero.png")
    _write_json(
        root / "evals" / "experiments" / "kris" / "wave1" / "predictions.json",
        [
            {"key": "hero", "prompt": "KRIS in rain", "file": "outputs/hero.png"},
            {"key": "remote", "prompt": "KRIS remote", "output": {"url": "https://example.com/out.png"}},
        ],
    )
    _write_json(
        root / "evals" / "experiments" / "kris" / "wave1" / "trainings.json",
        {"runs": [{"run_id": "exp-01", "model": "ostris/flux-dev-lora-trainer", "version": "trainer-v1", "status": "succeeded"}]},
    )
    _write(root / "video_project" / "both_hands_full" / "clips" / "b01" / "shot.mp4", b"0123456789")
    _write_json(root / "video_project" / "both_hands_full" / "storyboard.json", {"title": "Both Hands Full", "scenes": []})
    _write_json(root / "video_project" / "both_hands_full" / "shot_list.json", {"b01": [{"shot_id": "shot"}]})
    _write_json(
        root / "video_project" / "both_hands_full" / "predictions.json",
        [{"scene_id": "b01", "shot_id": "shot", "prompt": "crowd", "file": "clips/b01/shot.mp4", "prediction_id": "p1"}],
    )
    _write(root / "video_project" / "both_hands_full" / "edits" / "final.mp4", b"video")
    _write_json(
        root / "video_project" / "both_hands_full" / "style_anchors_hollywood_v1.json",
        {"version": "hollywood_v1", "style_suffix": "cinematic grit", "negative_suffix": "plastic skin"},
    )
    return root


def test_alex_importer_normalizes_subjects_predictions_video_and_styles(tmp_path: Path) -> None:
    root = _alex_fixture(tmp_path)

    result = alex_samuel.import_root(root, root_key="alex")
    payload = result.to_dict()
    entries = payload["entries"]

    assert payload["summary"]["subjects"] == 1
    assert {subject["key"] for subject in payload["subjects"]} == {"kris"}
    assert any(entry["kind"] == "image" and entry["relative_path"].endswith("hero.png") for entry in entries)
    assert any(entry["kind"] == "prediction" and entry["source_url"] == "https://example.com/out.png" for entry in entries)
    assert any(entry["kind"] == "video" and entry["project"] == "both_hands_full" for entry in entries)
    assert payload["styles"][0]["name"] == "hollywood_v1"
    assert not any(".env" in entry["path"] or ".git" in entry["path"] for entry in entries)


def test_media_registry_indexes_and_searches_explicit_root(tmp_path: Path) -> None:
    root = _alex_fixture(tmp_path)
    registry_path = tmp_path / "media-registry.json"

    payload = index(
        roots={"alex": MediaRoot(key="alex", path=root, importer="alex-samuel")},
        registry_path=registry_path,
    )
    results = search("hollywood", registry_path=registry_path)

    assert payload["summary"]["entries"] > 0
    assert registry_path.exists()
    assert any(result.kind == "style" for result in results)

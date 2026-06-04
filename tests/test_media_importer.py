from __future__ import annotations

import json
from pathlib import Path

from lib import media_registry
from lib.importers import alex_samuel
from lib.media_registry import filter_entry_dicts, index, search
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

    benchmark_a = root / "evals" / "v4_benchmark" / "version-a" / "01_core_01.jpg"
    benchmark_b = root / "evals" / "v4_benchmark" / "version-a" / "11_style_01.jpg"
    cross_version = root / "evals" / "cross_version" / "version-b" / "01_closeup.jpg"
    for path in (benchmark_a, benchmark_b, cross_version):
        _write(path, b"jpg")
    _write_json(
        root / "evals" / "v4_benchmark_results.json",
        [
            {
                "prompt_id": "core_01",
                "prompt": "Alexandra benchmark core",
                "output_file": str(benchmark_a),
                "output_url": "https://example.com/alexandra-core.jpg",
                "prediction_id": "bench-1",
                "version_id": "version-a",
                "version_ref": "walkswithaswagger/alexandra-samuel:version-a",
                "status": "succeeded",
                "predict_time": 1.25,
                "web_url": "https://replicate.example/p/bench-1",
            },
            {
                "prompt_id": "style_01",
                "prompt": "Alexandra benchmark style",
                "output_file": str(benchmark_b),
                "output_url": "https://example.com/alexandra-style.jpg",
                "prediction_id": "bench-2",
                "version_id": "version-a",
                "version_ref": "walkswithaswagger/alexandra-samuel:version-a",
                "status": "succeeded",
                "predict_time": 1.5,
            },
        ],
    )
    _write_json(
        root / "evals" / "cross_version_results.json",
        [
            {
                "prompt_key": "closeup",
                "prompt": "Alexandra cross version closeup",
                "output_file": str(cross_version),
                "output_url": "https://example.com/alexandra-cross.jpg",
                "prediction_id": "cross-1",
                "version_id": "version-b",
                "version_ref": "walkswithaswagger/alexandra-samuel:version-b",
                "status": "succeeded",
                "predict_time": 1.75,
                "web_url": "https://replicate.example/p/cross-1",
            }
        ],
    )

    _write(root / "evals" / "experiments" / "kris" / "wave1" / "outputs" / "hero.png")
    _write_json(
        root / "evals" / "experiments" / "kris" / "wave1" / "predictions.json",
        [
            {
                "prompt_id": "wave1-hero",
                "prompt_key": "hero",
                "prompt": "KRIS in rain",
                "file": "outputs/hero.png",
                "prediction_id": "wave1-local",
                "run_id": "wave1",
                "model_version": "kris-wave1",
                "status": "succeeded",
                "metrics": {"predict_time": 1.0, "total_time": 2.0},
                "urls": {"get": "https://example.com/wave1-local"},
            },
            {
                "prompt_id": "wave1-remote",
                "prompt_key": "remote",
                "prompt": "KRIS remote",
                "output": {"url": "https://example.com/out.png"},
                "prediction_id": "wave1-remote",
                "run_id": "wave1",
                "model_version": "kris-wave1",
                "status": "succeeded",
            },
        ],
    )
    _write_json(
        root / "evals" / "experiments" / "kris" / "wave1" / "trainings.json",
        {"runs": [{"run_id": "exp-01", "model": "ostris/flux-dev-lora-trainer", "version": "trainer-v1", "status": "succeeded"}]},
    )
    _write(root / "evals" / "experiments" / "kris" / "bytedance_beg" / "outputs" / "beg.png")
    _write_json(
        root / "evals" / "experiments" / "kris" / "bytedance_beg" / "predictions.json",
        [
            {
                "prompt_id": "beg-1",
                "prompt_key": "beg",
                "prompt": "KRIS bytedance",
                "local_path": "outputs/beg.png",
                "output": ["https://example.com/beg.png"],
                "prediction_id": "beg-1",
                "run_id": "bytedance_beg",
                "model_label": "bytedance",
                "model_version": "kris-beg",
                "destination": "owner/model",
                "status": "succeeded",
                "metrics": {"predict_time": 1.0, "total_time": 2.0},
            },
            {
                "prompt_id": "beg-2",
                "prompt_key": "beg-remote",
                "prompt": "KRIS bytedance remote",
                "output": ["https://example.com/beg-remote.png"],
                "prediction_id": "beg-2",
                "run_id": "bytedance_beg",
                "model_label": "bytedance",
                "model_version": "kris-beg",
                "status": "succeeded",
            },
        ],
    )
    _write(root / "evals" / "experiments" / "kris" / "bytedance_beg_v2" / "outputs" / "beg-v2.png")
    _write_json(
        root / "evals" / "experiments" / "kris" / "bytedance_beg_v2" / "predictions.json",
        [
            {
                "prompt_id": "beg-v2-1",
                "prompt_key": "beg-v2",
                "prompt": "KRIS bytedance v2",
                "local_path": "outputs/beg-v2.png",
                "output": ["https://example.com/beg-v2.png"],
                "prediction_id": "beg-v2-1",
                "run_id": "bytedance_beg_v2",
                "model_label": "bytedance-v2",
                "model_version": "kris-beg-v2",
                "status": "succeeded",
                "variation": "close",
            }
        ],
    )
    _write(root / "evals" / "experiments" / "kris" / "fashion_masters" / "outputs" / "fashion.png")
    _write_json(
        root / "evals" / "experiments" / "kris" / "fashion_masters" / "predictions.json",
        [
            {
                "prompt_id": "fashion-1",
                "prompt_key": "editorial",
                "prompt": "KRIS fashion",
                "raw_prompt": "KRIS fashion raw",
                "category": "editorial",
                "file": "outputs/fashion.png",
                "prediction_id": "fashion-1",
                "run_id": "fashion_masters",
                "model_version": "kris-fashion",
                "status": "succeeded",
                "urls": {"get": "https://example.com/fashion-1"},
            },
            {
                "prompt_id": "fashion-2",
                "prompt_key": "studio",
                "prompt": "KRIS studio",
                "raw_prompt": "KRIS studio raw",
                "category": "studio",
                "output": ["https://example.com/fashion-2.png"],
                "prediction_id": "fashion-2",
                "run_id": "fashion_masters",
                "model_version": "kris-fashion",
                "status": "succeeded",
                "urls": {"get": "https://example.com/fashion-2"},
            },
        ],
    )
    _write_json(
        root / "evals" / "experiments" / "kris" / "prompt_test" / "predictions.json",
        [
            {
                "id": "prompt-1",
                "key": "prompt-test",
                "category": "test",
                "prompt": "KRIS prompt test",
                "output": ["https://example.com/prompt-test.png"],
                "prediction_id": "prompt-test-1",
                "status": "succeeded",
            }
        ],
    )

    _write(root / "video_project" / "clips" / "s01" / "shot.mp4", b"song1")
    _write_json(
        root / "video_project" / "storyboard.json",
        {
            "title": "Song One",
            "artist": "Alexandra Samuel",
            "duration_sec": 120,
            "audio_file": "song1.mp3",
            "trigger_word": "alexandra",
            "scenes": [{"id": "s01", "start": 0, "end": 5, "section": "intro", "type": "video", "mood": "open", "lyrics": "", "notes": ""}],
        },
    )
    _write_json(root / "video_project" / "shot_list.json", {"_style_bible": "cinematic", "s01": [{"shot_id": "shot", "prompt": "song one shot"}]})
    _write_json(
        root / "video_project" / "predictions.json",
        [{"scene_id": "s01", "shot_id": "shot", "prompt": "song one", "output": ["clips/s01/shot.mp4"], "prediction_id": "song1-p1", "status": "succeeded"}],
    )
    _write_json(
        root / "video_project" / "edits" / "publish_cut_song1_edl.json",
        {"name": "publish_cut_song1", "cuts": 1, "edl": [{"src": "clips/s01/shot.mp4", "in": 0, "out": 2, "t": 0, "note": "intro"}]},
    )
    _write(root / "video_project" / "edits" / "final_publish_song1.mp4", b"video")

    _write(root / "video_project" / "both_hands_full" / "clips" / "b01" / "shot.mp4", b"0123456789")
    _write_json(
        root / "video_project" / "both_hands_full" / "storyboard.json",
        {
            "title": "Both Hands Full",
            "artist": "Alexandra Samuel",
            "duration_sec": 140,
            "audio_file": "song2.mp3",
            "trigger_word": "alexandra",
            "scenes": [{"id": "b01", "start": 0, "end": 4, "section": "intro", "type": "video", "mood": "sharp", "lyrics": "", "notes": ""}],
        },
    )
    _write_json(root / "video_project" / "both_hands_full" / "shot_list.json", {"_style_bible": "hollywood", "b01": [{"shot_id": "shot", "prompt": "song two shot"}]})
    _write_json(
        root / "video_project" / "both_hands_full" / "predictions.json",
        [{"scene_id": "b01", "shot_id": "shot", "prompt": "crowd", "file": "clips/b01/shot.mp4", "prediction_id": "p1"}],
    )
    _write_json(
        root / "video_project" / "both_hands_full" / "edits" / "publish_cut_song2_edl.json",
        {
            "name": "publish_cut_song2",
            "cuts": 1,
            "hollywood_used": 1,
            "fallback_used": 0,
            "edl": [{"src": "clips/b01/shot.mp4", "in": 0, "out": 2, "t": 0, "note": "hook"}],
        },
    )
    _write(root / "video_project" / "both_hands_full" / "edits" / "final.mp4", b"video")
    _write_json(
        root / "video_project" / "both_hands_full" / "style_anchors_hollywood_v1.json",
        {
            "version": "hollywood_v1",
            "style_suffix": "cinematic grit",
            "negative_suffix": "plastic skin",
            "source": {
                "ratings_path": "video_project/both_hands_full/ratings.json",
                "prompt_suite_path": "video_project/both_hands_full/prompt_suite.json",
                "starred_prompt_count": 3,
                "grade_counts": {"high dynamic range filmic grade": 2},
                "lens_counts": {"35mm prime": 2},
                "top_runs": [{"run_id": "song2", "score": 5}],
            },
        },
    )

    _write(root / "video_project" / "time_airport" / "renders" / "ta01.mp4", b"time")
    _write_json(
        root / "video_project" / "time_airport" / "scenes.json",
        {
            "title": "Time Airport",
            "model_fast": "fast-model",
            "model_full": "full-model",
            "version_fast": "fast-version",
            "version_full": "full-version",
            "defaults": {"aspect_ratio": "16:9", "duration": 5, "generate_audio": False, "negative_prompt": "", "resolution": "720p", "style_suffix": "airport"},
            "scenes": [{"id": "ta01", "title": "Gate", "prompt": "airport gate", "narration": "time bends", "keyframe": "gate.jpg"}],
        },
    )
    _write_json(
        root / "video_project" / "time_airport" / "predictions.json",
        [
            {
                "scene_id": "ta01",
                "title": "Gate",
                "file": "renders/ta01.mp4",
                "model": "time-airport-model",
                "output_url": "https://example.com/time-airport.mp4",
                "prediction_id": "time-airport-1",
                "status": "succeeded",
                "error": None,
                "metrics": {"predict_time": 1.0, "total_time": 2.0, "video_output_count": 1, "video_output_duration_seconds": 5},
            }
        ],
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
    assert payload["styles"][0]["metadata"]["source"]["starred_prompt_count"] == 3
    assert not any(".env" in entry["path"] or ".git" in entry["path"] for entry in entries)


def test_alex_importer_indexes_alexandra_benchmark_and_cross_version_outputs(tmp_path: Path) -> None:
    root = _alex_fixture(tmp_path)

    payload = alex_samuel.import_root(root, root_key="alex").to_dict()
    entries = payload["entries"]
    benchmark_entries = [
        entry for entry in entries
        if entry["source_manifest"].endswith("evals/v4_benchmark_results.json")
    ]
    cross_version_entries = [
        entry for entry in entries
        if entry["source_manifest"].endswith("evals/cross_version_results.json")
    ]

    assert len(benchmark_entries) == 2
    assert len(cross_version_entries) == 1
    assert all(entry["kind"] == "image" for entry in benchmark_entries + cross_version_entries)
    assert all(entry["collection"] == "predictions" for entry in benchmark_entries + cross_version_entries)
    assert {entry["title"] for entry in benchmark_entries} == {"core_01", "style_01"}
    assert cross_version_entries[0]["title"] == "closeup"
    assert benchmark_entries[0]["model"] == "version-a"
    assert cross_version_entries[0]["metadata"]["version_ref"].endswith(":version-b")
    assert any(entry["kind"] == "evaluation" and entry["relative_path"] == "evals/v4_benchmark_results.json" for entry in entries)
    assert any(entry["kind"] == "evaluation" and entry["relative_path"] == "evals/cross_version_results.json" for entry in entries)


def test_alex_importer_pins_kris_wave_prediction_counts_and_collections(tmp_path: Path) -> None:
    root = _alex_fixture(tmp_path)

    entries = alex_samuel.import_root(root, root_key="alex").to_dict()["entries"]
    kris_prediction_entries = [
        entry for entry in entries
        if "/evals/experiments/kris/" in entry["source_manifest"]
        and entry["source_manifest"].endswith("predictions.json")
    ]
    counts: dict[str, int] = {}
    for entry in kris_prediction_entries:
        wave = Path(entry["source_manifest"]).parent.name
        counts[wave] = counts.get(wave, 0) + 1

    assert counts == {
        "bytedance_beg": 2,
        "bytedance_beg_v2": 1,
        "fashion_masters": 2,
        "prompt_test": 1,
        "wave1": 2,
    }
    assert all(entry["collection"] == "predictions" for entry in kris_prediction_entries)
    assert any(entry["kind"] == "image" and entry["metadata"].get("model_label") == "bytedance" for entry in kris_prediction_entries)
    assert any(entry["kind"] == "prediction" and entry["title"] == "beg-remote" for entry in kris_prediction_entries)
    assert any(entry["metadata"].get("variation") == "close" for entry in kris_prediction_entries)
    assert any(entry["metadata"].get("category") == "editorial" for entry in kris_prediction_entries)


def test_alex_importer_indexes_song_and_time_airport_video_manifest_shapes(tmp_path: Path) -> None:
    root = _alex_fixture(tmp_path)

    payload = alex_samuel.import_root(root, root_key="alex").to_dict()
    entries = payload["entries"]
    video_manifest_entries = {
        (entry["kind"], entry["project"], entry["relative_path"])
        for entry in entries
        if entry["collection"] == "video"
    }

    assert ("storyboard", "dont_need_your_permission", "video_project/storyboard.json") in video_manifest_entries
    assert ("shot-list", "dont_need_your_permission", "video_project/shot_list.json") in video_manifest_entries
    assert ("video-edit", "dont_need_your_permission", "video_project/edits/publish_cut_song1_edl.json") in video_manifest_entries
    assert ("storyboard", "both_hands_full", "video_project/both_hands_full/storyboard.json") in video_manifest_entries
    assert ("shot-list", "both_hands_full", "video_project/both_hands_full/shot_list.json") in video_manifest_entries
    assert ("video-edit", "both_hands_full", "video_project/both_hands_full/edits/publish_cut_song2_edl.json") in video_manifest_entries
    assert ("scene-manifest", "time_airport", "video_project/time_airport/scenes.json") in video_manifest_entries
    assert any(entry["kind"] == "video" and entry["project"] == "time_airport" and entry["source_url"].endswith("time-airport.mp4") for entry in entries)

    edits = {edit["title"]: edit for edit in payload["video_edits"]}
    assert edits["publish_cut_song1"]["clips"][0]["src"] == "clips/s01/shot.mp4"
    assert edits["publish_cut_song2"]["metadata"]["hollywood_used"] == 1
    assert any(edit["project"] == "both_hands_full" and edit["render_outputs"] for edit in payload["video_edits"])


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


def test_alex_importer_warns_for_malformed_remote_and_missing_predictions(tmp_path: Path) -> None:
    root = _alex_fixture(tmp_path)
    _write_json(
        root / "evals" / "experiments" / "kris" / "wave2" / "predictions.json",
        [
            "bad-row",
            {"key": "missing", "prompt": "KRIS missing", "file": "outputs/nope.png"},
            {"key": "remote", "prompt": "KRIS remote", "output": "https://example.com/remote.png"},
        ],
    )

    result = alex_samuel.import_root(root, root_key="alex")

    assert any("ignored 1 malformed prediction row" in warning for warning in result.warnings)
    assert any("1 prediction output(s) reference missing local files" in warning for warning in result.warnings)
    assert any("remote-only prediction output(s) indexed without local media" in warning for warning in result.warnings)


def test_media_registry_review_view_prioritizes_reviewable_entries(tmp_path: Path) -> None:
    root = _alex_fixture(tmp_path)
    payload = index(
        roots={"alex": MediaRoot(key="alex", path=root, importer="alex-samuel")},
        registry_path=tmp_path / "media-registry.json",
    )

    review_entries = filter_entry_dicts(payload, view="review")
    all_entries = filter_entry_dicts(payload, view="all")
    dataset_entries = filter_entry_dicts(payload, kind="dataset", view="review")

    assert review_entries
    assert all(entry["kind"] in media_registry.REVIEWABLE_KINDS for entry in review_entries)
    assert all_entries[0]["kind"] in media_registry.REVIEWABLE_KINDS
    assert any(entry["kind"] == "dataset" for entry in all_entries)
    assert any(entry["kind"] == "dataset" for entry in dataset_entries)


def test_subject_profiles_include_profile_details_outputs_and_filter_links(tmp_path: Path) -> None:
    registry_path = tmp_path / "media-registry.json"
    payload = {
        "version": 1,
        "subjects": [
            {
                "key": "kris",
                "display_name": "Kris Krug",
                "root_key": "alex",
                "trigger_word": "KRIS",
                "prompt_suites": ["/media/clients/kris/prompt_suite.json"],
                "album_roots": ["/media/clients/kris/album"],
                "training_roots": ["/media/evals/experiments/kris"],
                "model_versions": [{"model": "rafiki/kris-flux-lora", "version": "v1", "status": "succeeded"}],
            },
            {"key": "jai", "display_name": "Jai", "root_key": "alex"},
        ],
        "entries": [
            {
                "id": "kris-image",
                "kind": "image",
                "collection": "predictions",
                "root_key": "alex",
                "subject": "kris",
                "project": "portraits",
                "title": "Portrait",
                "path": "/media/kris.png",
                "relative_path": "kris.png",
            },
            {
                "id": "kris-video",
                "kind": "video",
                "collection": "video",
                "root_key": "alex",
                "subject": "kris",
                "project": "both_hands_full",
                "title": "Clip",
                "path": "/media/clip.mp4",
                "relative_path": "clip.mp4",
            },
            {
                "id": "jai-image",
                "kind": "image",
                "collection": "predictions",
                "root_key": "alex",
                "subject": "jai",
                "project": "",
                "title": "Jai Portrait",
                "path": "/media/jai.png",
                "relative_path": "jai.png",
            },
        ],
    }
    registry_path.write_text(json.dumps(payload), encoding="utf-8")

    profiles = media_registry.subject_profiles(registry_path, output_limit=2)
    kris = next(profile for profile in profiles if profile["key"] == "kris")
    jai = next(profile for profile in profiles if profile["key"] == "jai")

    assert kris["trigger_word"] == "KRIS"
    assert kris["prompt_suites"] == ["/media/clients/kris/prompt_suite.json"]
    assert kris["album_roots"] == ["/media/clients/kris/album"]
    assert kris["training_roots"] == ["/media/evals/experiments/kris"]
    assert kris["model_versions"][0]["version"] == "v1"
    assert [entry["id"] for entry in kris["representative_outputs"]] == ["kris-image", "kris-video"]
    assert kris["quick_links"]["library"] == "/?tab=library&view=all&subject=kris"
    assert kris["quick_links"]["video_subject"] == "/?tab=video&videoSubject=kris"
    assert kris["quick_links"]["video_projects"] == [
        {"project": "both_hands_full", "href": "/?tab=video&videoProject=both_hands_full"}
    ]
    assert jai["prompt_suites"] == []
    assert jai["model_versions"] == []


def test_media_registry_incremental_refreshes_stale_cache_then_reuses_unchanged_root(tmp_path: Path, monkeypatch) -> None:
    root = _alex_fixture(tmp_path)
    registry_path = tmp_path / "media-registry.json"
    roots = {"alex": MediaRoot(key="alex", path=root, importer="alex-samuel")}
    first = media_registry.index(roots=roots, registry_path=registry_path)
    stale = dict(first)
    stale.pop("root_fingerprints")
    registry_path.write_text(json.dumps(stale, indent=2), encoding="utf-8")
    refreshed = media_registry.index(roots=roots, registry_path=registry_path, incremental=True)

    assert refreshed["summary"]["entries"] == first["summary"]["entries"]
    assert refreshed["summary"]["imported_roots"] == ["alex"]
    assert refreshed["summary"]["reused_roots"] == []
    assert "alex" in refreshed["root_fingerprints"]

    def fail_import(*args, **kwargs):
        raise AssertionError("incremental index should reuse refreshed unchanged root")

    monkeypatch.setattr(media_registry, "import_media_root", fail_import)
    second = media_registry.index(roots=roots, registry_path=registry_path, incremental=True)

    assert second["summary"]["entries"] == refreshed["summary"]["entries"]
    assert second["summary"]["reused_roots"] == ["alex"]

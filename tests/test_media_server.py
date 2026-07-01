from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import HTTPServer
from pathlib import Path

import pytest

from lib import media_registry
from lib.media_roots import MediaRoot
from lib.server import _RafikiHandler


@pytest.fixture
def media_server(tmp_path: Path):
    media_root = tmp_path / "media"
    media_root.mkdir()
    (media_root / "clip.mp4").write_bytes(b"0123456789")
    output_root = tmp_path / "output"
    output_root.mkdir()
    registry_file = tmp_path / "media-registry.json"
    media_registry.index(
        roots={"demo": MediaRoot(key="demo", path=media_root, importer="generic")},
        registry_path=registry_file,
    )

    class Handler(_RafikiHandler):
        pass

    Handler.output_root = output_root
    Handler.ratings_file = output_root / "ratings.json"
    Handler.feedback_file = output_root / "feedback.json"
    Handler.evaluations_file = output_root / "evaluations.json"
    Handler.archive_metadata_file = output_root / "archive-metadata.json"
    Handler.billing_imports_file = tmp_path / "billing-imports.json"
    Handler.video_selections_file = tmp_path / "video-selections.json"
    Handler.media_registry_file = registry_file
    Handler.extra_roots = {}
    Handler.media_roots = {"demo": MediaRoot(key="demo", path=media_root, importer="generic")}

    try:
        httpd = HTTPServer(("127.0.0.1", 0), Handler)
    except PermissionError:
        pytest.skip("socket binding not permitted")
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)


def _request(url: str, *, method: str = "GET", data: dict | None = None, headers: dict | None = None):
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        return urllib.request.urlopen(req, timeout=5)
    except urllib.error.HTTPError as e:
        return e


def test_media_file_route_supports_byte_ranges(media_server: str) -> None:
    resp = _request(f"{media_server}/media/demo/clip.mp4", headers={"Range": "bytes=2-5"})

    assert resp.status == 206
    assert resp.headers["Content-Range"] == "bytes 2-5/10"
    assert resp.read() == b"2345"


def test_media_selections_endpoint_persists_local_state(media_server: str) -> None:
    resp = _request(
        f"{media_server}/api/media/selections",
        method="POST",
        data={"key": "media/demo/clip.mp4", "value": "star"},
    )
    assert resp.status == 200

    saved = json.loads(_request(f"{media_server}/api/media/selections").read().decode("utf-8"))
    assert saved["items"]["media/demo/clip.mp4"] == "star"


def test_media_notes_endpoint_persists_and_clears(media_server: str) -> None:
    resp = _request(
        f"{media_server}/api/media/notes",
        method="POST",
        data={"key": "demo-video-clip.mp4", "note": "great take, use this"},
    )
    assert resp.status == 200

    saved = json.loads(_request(f"{media_server}/api/media/selections").read().decode("utf-8"))
    assert saved["notes"]["demo-video-clip.mp4"] == "great take, use this"

    # empty note clears it
    _request(f"{media_server}/api/media/notes", method="POST", data={"key": "demo-video-clip.mp4", "note": ""})
    saved = json.loads(_request(f"{media_server}/api/media/selections").read().decode("utf-8"))
    assert "demo-video-clip.mp4" not in saved["notes"]


def test_media_selection_edl_exports_indexed_video_selection(media_server: str) -> None:
    resp = _request(
        f"{media_server}/api/media/selections",
        method="POST",
        data={"key": "demo-video-clip.mp4", "value": "focus"},
    )
    assert resp.status == 200

    edl = json.loads(_request(f"{media_server}/api/media/selections/edl").read().decode("utf-8"))

    assert edl["kind"] == "rafiki-video-edl"
    assert edl["clip_count"] == 1
    assert edl["clips"][0]["id"] == "demo-video-clip.mp4"
    assert edl["clips"][0]["path"].endswith("clip.mp4")
    assert edl["edit_manifest"]["clips"][0]["id"] == "demo-video-clip.mp4"


def test_media_selection_import_accepts_edl_and_edit_manifest(media_server: str) -> None:
    edl = {
        "kind": "rafiki-video-edl",
        "clips": [{"id": "demo-video-clip.mp4", "selection": "star", "path": "/not/needed.mp4"}],
    }
    resp = _request(
        f"{media_server}/api/media/selections/import",
        method="POST",
        data={"edl": edl},
    )
    assert resp.status == 200

    saved = json.loads(_request(f"{media_server}/api/media/selections").read().decode("utf-8"))
    assert saved["items"] == {"demo-video-clip.mp4": "star"}

    registry = json.loads(_request(f"{media_server}/api/media?view=all").read().decode("utf-8"))
    clip_path = registry["entries"][0]["path"]
    edit_manifest = {"clips": [{"path": clip_path}]}
    resp = _request(
        f"{media_server}/api/media/selections/import",
        method="POST",
        data={"edl": edit_manifest, "default_selection": "focus", "replace": True},
    )
    assert resp.status == 200

    saved = json.loads(_request(f"{media_server}/api/media/selections").read().decode("utf-8"))
    assert saved["items"] == {"demo-video-clip.mp4": "focus"}


def test_media_endpoint_defaults_to_reviewable_entries(media_server: str, monkeypatch) -> None:
    data = {
        "summary": {"entries": 2},
        "warnings": [],
        "entries": [
            {
                "id": "dataset",
                "kind": "dataset",
                "collection": "albums",
                "root_key": "demo",
                "path": "/tmp/dataset.zip",
                "relative_path": "dataset.zip",
                "title": "Dataset",
            },
            {
                "id": "image",
                "kind": "image",
                "collection": "predictions",
                "root_key": "demo",
                "path": "/tmp/image.png",
                "relative_path": "image.png",
                "title": "Image",
            },
        ],
    }
    monkeypatch.setattr(media_registry, "load_registry", lambda *args, **kwargs: data)

    default_payload = json.loads(_request(f"{media_server}/api/media").read().decode("utf-8"))
    all_payload = json.loads(_request(f"{media_server}/api/media?view=all").read().decode("utf-8"))

    assert default_payload["view"] == "review"
    assert [entry["id"] for entry in default_payload["entries"]] == ["image"]
    assert {entry["id"] for entry in all_payload["entries"]} == {"dataset", "image"}


def test_media_subject_filters_and_profiles_use_registry_payload(media_server: str, monkeypatch) -> None:
    data = {
        "summary": {"entries": 3},
        "warnings": [],
        "subjects": [
            {
                "key": "kris",
                "display_name": "Kris Krug",
                "root_key": "demo",
                "trigger_word": "KRIS",
                "prompt_suites": ["/demo/prompts/kris.json"],
                "album_roots": [],
                "training_roots": ["/demo/training/kris"],
                "model_versions": [{"model": "rafiki/kris", "version": "v1", "status": "succeeded"}],
            }
        ],
        "entries": [
            {
                "id": "kris-image",
                "kind": "image",
                "collection": "predictions",
                "root_key": "demo",
                "subject": "kris",
                "project": "portraits",
                "path": "/tmp/kris.png",
                "relative_path": "kris.png",
                "title": "Kris Portrait",
            },
            {
                "id": "kris-video",
                "kind": "video",
                "collection": "video",
                "root_key": "demo",
                "subject": "kris",
                "project": "both_hands_full",
                "path": "/tmp/clip.mp4",
                "relative_path": "clip.mp4",
                "title": "Kris Clip",
            },
            {
                "id": "jai-image",
                "kind": "image",
                "collection": "predictions",
                "root_key": "demo",
                "subject": "jai",
                "project": "portraits",
                "path": "/tmp/jai.png",
                "relative_path": "jai.png",
                "title": "Jai Portrait",
            },
        ],
    }
    monkeypatch.setattr(media_registry, "load_registry", lambda *args, **kwargs: data)

    media_payload = json.loads(_request(f"{media_server}/api/media?view=all&subject=kris").read().decode("utf-8"))
    subjects_payload = json.loads(_request(f"{media_server}/api/media/subjects").read().decode("utf-8"))

    assert {entry["id"] for entry in media_payload["entries"]} == {"kris-image", "kris-video"}
    subject = subjects_payload["subjects"][0]
    assert subject["display_name"] == "Kris Krug"
    assert subject["trigger_word"] == "KRIS"
    assert subject["prompt_suites"] == ["/demo/prompts/kris.json"]
    assert subject["training_roots"] == ["/demo/training/kris"]
    assert subject["model_versions"][0]["version"] == "v1"
    assert [entry["id"] for entry in subject["representative_outputs"]] == ["kris-image", "kris-video"]
    assert subject["quick_links"]["library"] == "/?tab=library&view=all&subject=kris"
    assert subject["quick_links"]["video_subject"] == "/?tab=video&videoSubject=kris"


def test_media_warnings_endpoint_returns_empty_list_when_no_warnings(media_server: str, monkeypatch) -> None:
    data = {"warnings": [], "entries": [], "summary": {}}
    monkeypatch.setattr(media_registry, "load_registry", lambda *args, **kwargs: data)

    payload = json.loads(_request(f"{media_server}/api/media/warnings").read().decode("utf-8"))

    assert payload == {"warnings": []}


def test_media_warnings_endpoint_surfaces_registry_warnings(media_server: str, monkeypatch) -> None:
    data = {"warnings": ["root not found: /missing", "stale ref: abc123"], "entries": [], "summary": {}}
    monkeypatch.setattr(media_registry, "load_registry", lambda *args, **kwargs: data)

    payload = json.loads(_request(f"{media_server}/api/media/warnings").read().decode("utf-8"))

    assert payload["warnings"] == ["root not found: /missing", "stale ref: abc123"]

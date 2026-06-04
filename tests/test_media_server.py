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

    class Handler(_RafikiHandler):
        pass

    Handler.output_root = output_root
    Handler.ratings_file = output_root / "ratings.json"
    Handler.feedback_file = output_root / "feedback.json"
    Handler.evaluations_file = output_root / "evaluations.json"
    Handler.archive_metadata_file = output_root / "archive-metadata.json"
    Handler.billing_imports_file = tmp_path / "billing-imports.json"
    Handler.video_selections_file = tmp_path / "video-selections.json"
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
    monkeypatch.setattr(media_registry, "load_registry", lambda: data)

    default_payload = json.loads(_request(f"{media_server}/api/media").read().decode("utf-8"))
    all_payload = json.loads(_request(f"{media_server}/api/media?view=all").read().decode("utf-8"))

    assert default_payload["view"] == "review"
    assert [entry["id"] for entry in default_payload["entries"]] == ["image"]
    assert {entry["id"] for entry in all_payload["entries"]} == {"dataset", "image"}

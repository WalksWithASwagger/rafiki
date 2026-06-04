#!/usr/bin/env python3
"""Local acceptance checks for Video Lab without private media or provider spend."""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from http.server import HTTPServer
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    tmp_root = Path(tempfile.mkdtemp(prefix="rafiki-video-lab-acceptance-"))
    keep_tmp = os.environ.get("RAFIKI_VIDEO_ACCEPTANCE_KEEP_TMP") == "1"
    try:
        result = run_acceptance(tmp_root)
        print(json.dumps(result, indent=2))
        return 0
    finally:
        if keep_tmp:
            print(f"Kept acceptance temp dir: {tmp_root}", file=sys.stderr)
        else:
            shutil.rmtree(tmp_root, ignore_errors=True)


def run_acceptance(tmp_root: Path) -> dict[str, Any]:
    from lib import media_registry
    from lib.media_roots import MediaRoot
    from lib.video_jobs import assemble_video_edit

    fixture = _write_fixture(tmp_root)
    registry_path = tmp_root / "data" / "media-registry.json"
    registry = media_registry.index(
        roots={fixture["root_key"]: MediaRoot(key=fixture["root_key"], path=fixture["media_root"], importer="generic")},
        registry_path=registry_path,
    )
    _assert_registry_counts(registry)
    _assert_external_media_only(registry, fixture["media_root"])

    httpd, thread, base_url = _start_server(tmp_root, registry_path, fixture)
    try:
        portal = _portal_checks(base_url, fixture)
        dry_run_job = _dry_run_job_check(base_url, tmp_root, fixture["storyboard"])
        edit = assemble_video_edit(edit_path=fixture["edit"], output_dir=tmp_root / "output" / "acceptance-edit")
        assert edit["manifest"]["status"] == "dry-run"
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)

    _assert_no_fixture_media_copied(tmp_root, fixture["clip"])
    return {
        "ok": True,
        "registry": {
            "entries": registry["summary"]["entries"],
            "videos": registry["summary"]["by_kind"].get("video", 0),
            "audio": registry["summary"]["by_kind"].get("audio", 0),
        },
        "portal": portal,
        "dry_run_job": {
            "status": dry_run_job["job"]["status"],
            "manifest_path": dry_run_job["manifest_path"],
        },
        "edit_assembly": {
            "status": edit["manifest"]["status"],
            "manifest_path": edit["manifest_path"],
        },
        "private_media": {
            "copied_alex_media": False,
            "fixture_root": str(fixture["media_root"]),
        },
    }


def _write_fixture(tmp_root: Path) -> dict[str, Any]:
    media_root = tmp_root / "external-alex-media"
    clips_dir = media_root / "clips"
    audio_dir = media_root / "audio"
    clips_dir.mkdir(parents=True)
    audio_dir.mkdir(parents=True)
    clip = clips_dir / "acceptance.mp4"
    audio = audio_dir / "bed.wav"
    clip.write_bytes(b"fixture-mp4-0123456789")
    audio.write_bytes(b"fixture-audio")

    storyboard = tmp_root / "storyboard.json"
    storyboard.write_text(
        json.dumps({"title": "Acceptance", "scenes": [{"id": "s1", "prompt": "fixture clip"}]}),
        encoding="utf-8",
    )
    edit = tmp_root / "edit.json"
    edit.write_text(
        json.dumps(
            {
                "project": "acceptance",
                "audio_path": str(audio),
                "clips": [
                    {
                        "path": str(clip),
                        "duration_seconds": 1.0,
                        "source_duration_seconds": 1.0,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return {
        "root_key": "alex-samuel",
        "media_root": media_root,
        "clip": clip,
        "audio": audio,
        "storyboard": storyboard,
        "edit": edit,
    }


def _start_server(tmp_root: Path, registry_path: Path, fixture: dict[str, Any]):
    from lib.media_roots import MediaRoot
    from lib.server import _RafikiHandler

    output_root = tmp_root / "output"
    output_root.mkdir(parents=True, exist_ok=True)

    class Handler(_RafikiHandler):
        pass

    Handler.output_root = output_root
    Handler.ratings_file = output_root / "ratings.json"
    Handler.feedback_file = output_root / "feedback.json"
    Handler.evaluations_file = output_root / "evaluations.json"
    Handler.archive_metadata_file = output_root / "archive-metadata.json"
    Handler.billing_imports_file = tmp_root / "billing-imports.json"
    Handler.video_selections_file = tmp_root / "video-selections.json"
    Handler.media_registry_file = registry_path
    Handler.extra_roots = {}
    Handler.media_roots = {
        fixture["root_key"]: MediaRoot(key=fixture["root_key"], path=fixture["media_root"], importer="generic")
    }

    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, thread, f"http://127.0.0.1:{httpd.server_address[1]}"


def _portal_checks(base_url: str, fixture: dict[str, Any]) -> dict[str, Any]:
    media_payload = _json_request(f"{base_url}/api/media?view=all")
    video_entries = [entry for entry in media_payload["entries"] if entry["kind"] == "video"]
    assert len(video_entries) == 1
    video = video_entries[0]

    range_resp = _request(
        f"{base_url}/media/{fixture['root_key']}/clips/acceptance.mp4",
        headers={"Range": "bytes=2-5"},
    )
    assert range_resp.status == 206
    assert range_resp.read() == b"xtur"

    _json_request(
        f"{base_url}/api/media/selections",
        method="POST",
        data={"key": video["id"], "value": "focus"},
    )
    edl = _json_request(f"{base_url}/api/media/selections/edl")
    assert edl["clip_count"] == 1
    assert edl["edit_manifest"]["clips"][0]["id"] == video["id"]

    edit_manifest = json.loads(json.dumps(edl["edit_manifest"]))
    for clip in edit_manifest["clips"]:
        clip.pop("selection", None)
    imported = _json_request(
        f"{base_url}/api/media/selections/import",
        method="POST",
        data={"edl": edit_manifest, "replace": True, "default_selection": "star"},
    )
    assert imported["items"] == {video["id"]: "star"}
    return {
        "entries": media_payload["total_entries"],
        "video_entries": len(video_entries),
        "range_status": range_resp.status,
        "edl_clips": edl["clip_count"],
    }


def _dry_run_job_check(base_url: str, tmp_root: Path, storyboard: Path) -> dict[str, Any]:
    from lib.providers import replicate_provider

    jobs_dir = tmp_root / "jobs"
    old_save_job = replicate_provider.save_job

    def save_temp_job(record, **_kwargs):
        jobs_dir.mkdir(parents=True, exist_ok=True)
        path = jobs_dir / f"{record.id}.json"
        path.write_text(json.dumps(record.to_dict(), indent=2), encoding="utf-8")
        return path

    replicate_provider.save_job = save_temp_job
    try:
        result = _json_request(
            f"{base_url}/api/jobs/video-generate",
            method="POST",
            data={"storyboard": str(storyboard)},
        )
    finally:
        replicate_provider.save_job = old_save_job
    assert result["job"]["status"] == "dry-run"
    assert Path(result["manifest_path"]).exists()
    assert len(list(jobs_dir.glob("*.json"))) == 1
    return result


def _assert_registry_counts(registry: dict[str, Any]) -> None:
    summary = registry["summary"]
    assert summary["entries"] == 2
    assert summary["by_kind"].get("video") == 1
    assert summary["by_kind"].get("audio") == 1


def _assert_external_media_only(registry: dict[str, Any], media_root: Path) -> None:
    root = media_root.resolve()
    for entry in registry.get("entries", []):
        path = Path(entry["path"]).resolve()
        assert path.is_relative_to(root)
        assert not path.is_relative_to(REPO_ROOT)


def _assert_no_fixture_media_copied(tmp_root: Path, clip: Path) -> None:
    copied = []
    for path in (tmp_root / "output").rglob(clip.name):
        if path.resolve() != clip.resolve():
            copied.append(path)
    assert copied == []


def _request(url: str, *, method: str = "GET", data: dict[str, Any] | None = None, headers: dict[str, str] | None = None):
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        return urllib.request.urlopen(req, timeout=10)
    except urllib.error.HTTPError as e:
        return e


def _json_request(url: str, *, method: str = "GET", data: dict[str, Any] | None = None) -> dict[str, Any]:
    resp = _request(url, method=method, data=data)
    text = resp.read().decode("utf-8")
    if resp.status >= 400:
        raise AssertionError(f"{method} {url} returned {resp.status}: {text}")
    return json.loads(text)


if __name__ == "__main__":
    raise SystemExit(main())

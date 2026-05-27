"""HTTP-layer tests for portal endpoints not covered by test_server_auth.py.

Drives the real `_RafikiHandler` through the shared `server` fixture
(conftest.py). Focuses on the static-file handler (incl. path-traversal
safety), the read-only `/api/runs` and `/api/actions` endpoints, the ratings
POST round-trip, and the request-parsing / status-code wiring of the `/api/regen`
and `/api/actions` POST handlers (their underlying lib logic is covered
elsewhere).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.server_harness import http_get, http_post_json, http_post_raw, raw_get


PNG_HEADER = b"\x89PNG\r\n\x1a\n"


def _write_run(directory: Path, images: list[dict]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for image in images:
        (directory / image["file"]).write_bytes(PNG_HEADER + b"fakepng")
    (directory / "run.json").write_text(
        json.dumps(
            {
                "model": "gpt-image-2",
                "aspect_ratio": "16:9",
                "style": "bcai",
                "timestamp": "2026-01-01 10:00",
                "run_id": directory.name.removeprefix("run-"),
                "images": images,
            }
        ),
        encoding="utf-8",
    )


# ── _serve_library (GET /) ─────────────────────────────────────────────────

def test_library_endpoint_returns_html(server):
    resp = http_get(f"{server}/")
    assert resp.status == 200
    assert resp.headers.get("Content-Type", "").startswith("text/html")
    assert b"<" in resp.read()


# ── _serve_static (GET /output/<file>) ─────────────────────────────────────

def test_static_endpoint_serves_existing_image(server, tmp_path):
    run_dir = tmp_path / "output" / "demo" / "run-20260101-100000"
    _write_run(run_dir, [{"name": "Hero", "prompt": "p", "file": "hero.png"}])

    resp = http_get(f"{server}/output/demo/run-20260101-100000/hero.png")
    assert resp.status == 200
    assert resp.headers.get("Content-Type") == "image/png"
    assert resp.read().startswith(PNG_HEADER)


def test_static_endpoint_404s_for_missing_file(server):
    resp = http_get(f"{server}/output/demo/nope.png")
    assert resp.status == 404


def test_static_endpoint_rejects_path_traversal(server, tmp_path):
    # A secret living a sibling of output_root must never be reachable.
    secret = tmp_path / "secret.txt"
    secret.write_text("TOP-SECRET", encoding="utf-8")

    # raw_get bypasses client-side dot-segment normalization so the server's
    # own normpath/relative_to guard is what gets exercised.
    for target in (
        "/output/../secret.txt",
        "/output/../../etc/passwd",
        "/output/demo/../../secret.txt",
    ):
        status, body = raw_get(server, target)
        assert status == 404, target
        assert b"TOP-SECRET" not in body, target


# ── _serve_runs (GET /api/runs) ────────────────────────────────────────────

def test_runs_endpoint_lists_project_runs(server, tmp_path):
    run_dir = tmp_path / "output" / "demo" / "run-20260101-100000"
    _write_run(
        run_dir,
        [
            {"name": "Hero", "prompt": "p", "file": "hero.png"},
            {"name": "Missing", "prompt": "p", "file": "gone.png"},
        ],
    )
    # Simulate a manifested-but-absent image.
    (run_dir / "gone.png").unlink()

    payload = json.loads(http_get(f"{server}/api/runs").read().decode("utf-8"))
    runs = {(r["project"], r["run_id"]): r for r in payload}
    entry = runs[("demo", "run-20260101-100000")]
    assert entry["model"] == "gpt-image-2"
    by_file = {img["file"]: img for img in entry["images"]}
    assert by_file["demo/run-20260101-100000/hero.png"]["ok"] is True
    assert by_file["demo/run-20260101-100000/gone.png"]["ok"] is False


# ── _serve_actions (GET /api/actions) ──────────────────────────────────────

def test_actions_endpoint_lists_available_actions(server):
    payload = json.loads(http_get(f"{server}/api/actions").read().decode("utf-8"))
    names = {a["name"] for a in payload["actions"]}
    assert "approve-starred" in names
    assert "notion-export" in names


# ── _update_ratings (POST /api/ratings) ────────────────────────────────────

def test_ratings_post_round_trip_and_delete(server):
    key = "demo/run-1/01-hero.png"

    resp = http_post_json(f"{server}/api/ratings", {"key": key, "value": "star"})
    assert resp.status == 200
    assert json.loads(resp.read().decode("utf-8")) == {"ok": True}

    saved = json.loads(http_get(f"{server}/api/ratings").read().decode("utf-8"))
    assert saved[key] == "star"

    # value=None removes the key.
    resp = http_post_json(f"{server}/api/ratings", {"key": key, "value": None})
    assert resp.status == 200
    saved = json.loads(http_get(f"{server}/api/ratings").read().decode("utf-8"))
    assert key not in saved


def test_ratings_post_missing_key_returns_400(server):
    resp = http_post_json(f"{server}/api/ratings", {"value": "star"})
    assert resp.status == 400


# ── _regen (POST /api/regen) ───────────────────────────────────────────────

def test_regen_post_dry_run_returns_result(server):
    resp = http_post_json(
        f"{server}/api/regen",
        {"mode": "single", "project": "studio", "prompt": "a poster", "dry_run": True},
    )
    assert resp.status == 200
    payload = json.loads(resp.read().decode("utf-8"))
    assert payload["ok"] is True
    assert payload["mode"] == "single"
    assert payload["project"] == "studio"


def test_regen_post_malformed_json_returns_400(server):
    resp = http_post_raw(f"{server}/api/regen", b"this is not json")
    assert resp.status == 400


def test_regen_post_invalid_mode_returns_400(server):
    resp = http_post_json(f"{server}/api/regen", {"mode": "bogus", "prompt": "x"})
    assert resp.status == 400
    assert "error" in json.loads(resp.read().decode("utf-8"))


# ── _run_action (POST /api/actions) ────────────────────────────────────────

def test_action_post_mutating_without_confirm_returns_409(server):
    resp = http_post_json(
        f"{server}/api/actions",
        {"action": "approve-starred", "project": "demo"},
    )
    assert resp.status == 409


def test_action_post_unknown_action_returns_400(server):
    resp = http_post_json(f"{server}/api/actions", {"action": "does-not-exist"})
    assert resp.status == 400


def test_action_post_malformed_json_returns_400(server):
    resp = http_post_raw(f"{server}/api/actions", b"<<<not json>>>")
    assert resp.status == 400

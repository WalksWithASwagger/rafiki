"""Tests for portal Basic auth (issue #29)."""

from __future__ import annotations

import inspect
import json
import sys
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib import server as server_module
from lib import training as training_module
from lib import video_jobs as video_jobs_module
from lib.server import _RafikiHandler
from tests.server_harness import http_get as _get
from tests.server_harness import http_post_json as _post_json
from tests.server_harness import http_post_raw as _post_raw


def _get_with_origin(url: str, origin: str):
    req = urllib.request.Request(url)
    req.add_header("Origin", origin)
    return urllib.request.urlopen(req, timeout=5)


def test_no_credentials_serves_freely(server, monkeypatch):
    monkeypatch.delenv("PORTAL_USERNAME", raising=False)
    monkeypatch.delenv("PORTAL_PASSWORD", raising=False)
    # /api/ratings is a stable JSON endpoint that doesn't depend on filesystem
    # state beyond what the fixture provides.
    resp = _get(f"{server}/api/ratings")
    assert resp.status == 200


def test_favicon_request_is_quiet_no_content(server):
    resp = _get(f"{server}/favicon.ico")

    assert resp.status == 204
    assert resp.read() == b""


def test_feedback_endpoint_persists_review_notes(server):
    resp = _post_json(
        f"{server}/api/feedback",
        {
            "key": "demo/run-1/01-hero.png",
            "status": "needs-change",
            "note": "Too dark",
            "change_request": "Add warmer light",
        },
    )
    assert resp.status == 200
    payload = json.loads(resp.read().decode("utf-8"))
    assert payload["ok"] is True
    assert payload["feedback"]["status"] == "needs-change"

    saved = json.loads(_get(f"{server}/api/feedback").read().decode("utf-8"))
    assert saved["items"]["demo/run-1/01-hero.png"]["note"] == "Too dark"


def test_evaluations_endpoint_persists_review_decision(server):
    resp = _post_json(
        f"{server}/api/evaluations",
        {
            "key": "demo/run-1/01-hero.png",
            "decision": "approve",
            "score": 5,
            "use_case": "homepage hero",
            "rationale": "Strong, legible, and on-brand.",
            "next_step": "Export with the launch bundle.",
        },
    )
    assert resp.status == 200
    payload = json.loads(resp.read().decode("utf-8"))
    assert payload["ok"] is True
    assert payload["evaluation"]["decision"] == "approve"
    assert payload["evaluation"]["score"] == 5

    saved = json.loads(_get(f"{server}/api/evaluations").read().decode("utf-8"))
    entry = saved["items"]["demo/run-1/01-hero.png"]
    assert entry["use_case"] == "homepage hero"
    assert entry["next_step"] == "Export with the launch bundle."


def test_archive_metadata_endpoint_persists_card_state(server):
    resp = _post_json(
        f"{server}/api/archive-metadata",
        {
            "key": "demo/run-1/01-hero.png",
            "title": "Homepage Hero",
            "tags": "homepage, keeper",
            "states": ["canva", "published"],
            "superseded_by": "demo/run-2/01-hero.png",
        },
    )

    assert resp.status == 200
    payload = json.loads(resp.read().decode("utf-8"))
    assert payload["ok"] is True
    assert payload["metadata"]["title"] == "Homepage Hero"

    saved = json.loads(_get(f"{server}/api/archive-metadata").read().decode("utf-8"))
    entry = saved["items"]["demo/run-1/01-hero.png"]
    assert entry["tags"] == ["homepage", "keeper"]
    assert entry["states"] == ["canva", "published"]
    assert entry["superseded_by"] == "demo/run-2/01-hero.png"


def test_usage_endpoint_returns_local_summary(server):
    payload = json.loads(_get(f"{server}/api/usage").read().decode("utf-8"))

    assert payload["usage_log"]["entries"] == 0
    assert payload["archive"]["projects"] == 0
    assert payload["archive"]["known_cost"]["currency"] == "USD"
    assert payload["archive"]["estimated_cost"]["currency"] == "USD"
    assert payload["provider_billing"]["entries"] == 0


def test_billing_import_endpoint_persists_manual_entry(server):
    resp = _post_json(
        f"{server}/api/billing-imports",
        {
            "provider": "OpenAI",
            "model": "gpt-image-2",
            "amount": 12.34,
            "note": "May image billing",
        },
    )

    assert resp.status == 200
    payload = json.loads(resp.read().decode("utf-8"))
    assert payload["imported"] == 1

    saved = json.loads(_get(f"{server}/api/billing-imports").read().decode("utf-8"))
    assert saved["entries"] == 1
    assert saved["amount"] == 12.34
    assert saved["by_provider"] == [{"provider": "OpenAI", "amount": 12.34, "entries": 1}]

    usage = json.loads(_get(f"{server}/api/usage").read().decode("utf-8"))
    assert usage["archive"]["spend"]["basis"] == "provider_billing_imports"
    assert usage["archive"]["spend"]["amount"] == 12.34


def test_train_lora_execute_requires_confirmation(server):
    resp = _post_json(
        f"{server}/api/jobs/train-lora",
        {"subject": "kris", "execute": True},
    )

    assert resp.status == 400
    payload = json.loads(resp.read().decode("utf-8"))
    assert "confirm_execute=true" in payload["error"]


def test_train_lora_dry_run_is_default(server, monkeypatch):
    captured: dict = {}

    def fake_plan_lora_training(**kwargs):
        captured.update(kwargs)
        return {"ok": True, "job": {"status": "dry-run"}}

    monkeypatch.setattr(training_module, "plan_lora_training", fake_plan_lora_training)

    resp = _post_json(
        f"{server}/api/jobs/train-lora",
        {"subject": "kris", "input_images_url": "https://example.com/data.zip"},
    )

    assert resp.status == 200
    assert captured["execute"] is False


def test_video_generate_execute_requires_confirmation(server):
    resp = _post_json(
        f"{server}/api/jobs/video-generate",
        {"storyboard": "/tmp/storyboard.json", "execute": True},
    )

    assert resp.status == 400
    payload = json.loads(resp.read().decode("utf-8"))
    assert "confirm_execute=true" in payload["error"]


def test_video_generate_execute_passes_with_confirmation(server, monkeypatch):
    captured: dict = {}

    def fake_plan_video_generation(**kwargs):
        captured.update(kwargs)
        return {"ok": True, "job": {"status": "queued"}}

    monkeypatch.setattr(video_jobs_module, "plan_video_generation", fake_plan_video_generation)

    resp = _post_json(
        f"{server}/api/jobs/video-generate",
        {"storyboard": "/tmp/storyboard.json", "execute": True, "confirm_execute": True},
    )

    assert resp.status == 200
    assert captured["execute"] is True


def test_public_serve_requires_complete_credentials(tmp_path, monkeypatch):
    output_root = tmp_path / "output"
    output_root.mkdir()

    for username, password in ((None, None), ("team", None), (None, "s3cret")):
        if username is None:
            monkeypatch.delenv("PORTAL_USERNAME", raising=False)
        else:
            monkeypatch.setenv("PORTAL_USERNAME", username)
        if password is None:
            monkeypatch.delenv("PORTAL_PASSWORD", raising=False)
        else:
            monkeypatch.setenv("PORTAL_PASSWORD", password)

        with pytest.raises(ValueError, match="--public requires both PORTAL_USERNAME and PORTAL_PASSWORD"):
            server_module.serve(output_root=output_root, public=True)


def test_same_origin_cors_echoes_origin(server):
    resp = _get_with_origin(f"{server}/api/ratings", server)

    assert resp.status == 200
    assert resp.headers.get("Access-Control-Allow-Origin") == server
    assert resp.headers.get("Vary") == "Origin"


def test_cross_origin_cors_is_not_wildcard(server):
    resp = _get_with_origin(f"{server}/api/ratings", "http://example.com")

    assert resp.status == 200
    assert resp.headers.get("Access-Control-Allow-Origin") is None


@pytest.mark.parametrize(
    ("path", "handler_name", "origin", "content_type", "expected_status"),
    [
        ("/api/actions", "_run_action", "http://example.com", "text/plain", 403),
        ("/api/regen", "_regen", "http://example.com", "application/json", 403),
        ("/api/feedback", "_update_feedback", "wrong-scheme", "application/json", 403),
        ("/api/media/selections", "_update_media_selection", "same-origin", "text/plain", 415),
        ("/api/ratings", "_update_ratings", "same-origin", None, 415),
    ],
)
def test_post_guard_rejects_before_mutation_handler(
    server,
    monkeypatch,
    path,
    handler_name,
    origin,
    content_type,
    expected_status,
):
    called = []

    def mutation_handler(self):
        called.append(True)
        self._respond(200, "application/json", b'{"unexpected":true}')

    monkeypatch.setattr(_RafikiHandler, handler_name, mutation_handler)
    if origin == "same-origin":
        request_origin = server
    elif origin == "wrong-scheme":
        request_origin = server.replace("http://", "https://", 1)
    else:
        request_origin = origin

    resp = _post_raw(
        f"{server}{path}",
        b"{}",
        content_type=content_type,
        origin=request_origin,
    )

    assert resp.status == expected_status
    assert resp.headers.get("Content-Type") == "application/json"
    assert "error" in json.loads(resp.read().decode("utf-8"))
    assert called == []


@pytest.mark.parametrize("include_origin", [False, True])
def test_post_guard_allows_json_from_supported_clients(server, monkeypatch, include_origin):
    called = []

    def mutation_handler(self):
        called.append(True)
        self._respond(200, "application/json", b'{"ok":true}')

    monkeypatch.setattr(_RafikiHandler, "_update_ratings", mutation_handler)

    resp = _post_json(
        f"{server}/api/ratings",
        {},
        origin=server if include_origin else None,
    )

    assert resp.status == 200
    assert called == [True]


def test_deploy_readiness_endpoint_is_secret_safe(server, monkeypatch):
    monkeypatch.setenv("PORTAL_USERNAME", "team")
    monkeypatch.setenv("PORTAL_PASSWORD", "s3cret")
    monkeypatch.setenv("GEMINI_API_KEY", "secret-gemini")

    payload = json.loads(
        _get(f"{server}/api/deploy-readiness?public=true", auth=("team", "s3cret")).read().decode("utf-8")
    )

    assert payload["public"] is True
    checks = {check["key"]: check for check in payload["checks"]}
    assert checks["portal_auth"]["ok"] is True
    assert checks["gemini_key"]["ok"] is True
    assert "secret" not in json.dumps(payload)


def test_credentials_set_unauth_returns_401(server, monkeypatch):
    monkeypatch.setenv("PORTAL_USERNAME", "team")
    monkeypatch.setenv("PORTAL_PASSWORD", "s3cret")
    resp = _get(f"{server}/api/ratings")
    assert resp.status == 401
    assert resp.headers.get("WWW-Authenticate", "").startswith("Basic")


def test_credentials_set_wrong_password_returns_401(server, monkeypatch):
    monkeypatch.setenv("PORTAL_USERNAME", "team")
    monkeypatch.setenv("PORTAL_PASSWORD", "s3cret")
    resp = _get(f"{server}/api/ratings", auth=("team", "wrong"))
    assert resp.status == 401


def test_credentials_set_wrong_username_returns_401(server, monkeypatch):
    monkeypatch.setenv("PORTAL_USERNAME", "team")
    monkeypatch.setenv("PORTAL_PASSWORD", "s3cret")
    resp = _get(f"{server}/api/ratings", auth=("nope", "s3cret"))
    assert resp.status == 401


def test_credentials_set_correct_returns_200(server, monkeypatch):
    monkeypatch.setenv("PORTAL_USERNAME", "team")
    monkeypatch.setenv("PORTAL_PASSWORD", "s3cret")
    resp = _get(f"{server}/api/ratings", auth=("team", "s3cret"))
    assert resp.status == 200


def test_constant_time_compare_used():
    """Source-level check that secrets.compare_digest is in the auth path."""
    src = inspect.getsource(_RafikiHandler._check_auth)
    assert "secrets.compare_digest" in src or "compare_digest" in src
    # Also verify the module imports the secrets module
    assert hasattr(server_module, "secrets")


def test_only_one_env_var_set_disables_auth(server, monkeypatch):
    """Auth turns on only when BOTH PORTAL_USERNAME and PORTAL_PASSWORD are
    set — partial config = off for localhost and refused for --public."""
    monkeypatch.setenv("PORTAL_USERNAME", "team")
    monkeypatch.delenv("PORTAL_PASSWORD", raising=False)
    resp = _get(f"{server}/api/ratings")
    assert resp.status == 200

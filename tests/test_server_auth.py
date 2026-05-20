"""Tests for portal Basic auth (issue #29)."""

from __future__ import annotations

import base64
import inspect
import json
import sys
import threading
import urllib.error
import urllib.request
from http.server import HTTPServer
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib import server as server_module
from lib.server import _RafikiHandler


def _make_handler_class(tmp_path: Path) -> type:
    """Build a concrete handler class with the class attrs the real server
    sets in `serve()`."""
    output_root = tmp_path / "output"
    output_root.mkdir(exist_ok=True)
    ratings_file = output_root / "ratings.json"

    class Handler(_RafikiHandler):
        pass

    Handler.output_root = output_root
    Handler.ratings_file = ratings_file
    Handler.feedback_file = output_root / "feedback.json"
    Handler.archive_metadata_file = output_root / "archive-metadata.json"
    Handler.billing_imports_file = tmp_path / "billing-imports.json"
    Handler.extra_roots = {}
    return Handler


@pytest.fixture
def server(tmp_path, monkeypatch):
    """Start a real HTTPServer on a random port in a thread; tear down after."""
    # Default: clear creds. Individual tests can re-set with monkeypatch.
    monkeypatch.delenv("PORTAL_USERNAME", raising=False)
    monkeypatch.delenv("PORTAL_PASSWORD", raising=False)

    Handler = _make_handler_class(tmp_path)
    try:
        httpd = HTTPServer(("127.0.0.1", 0), Handler)
    except PermissionError:
        pytest.skip("socket binding not permitted in this environment")
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)


def _get(url: str, auth: tuple[str, str] | None = None):
    req = urllib.request.Request(url)
    if auth is not None:
        token = base64.b64encode(f"{auth[0]}:{auth[1]}".encode()).decode()
        req.add_header("Authorization", f"Basic {token}")
    try:
        return urllib.request.urlopen(req, timeout=5)
    except urllib.error.HTTPError as e:
        return e


def _post_json(url: str, payload: dict):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        return urllib.request.urlopen(req, timeout=5)
    except urllib.error.HTTPError as e:
        return e


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
    set — partial config = off (warned by --public, but auth stays disabled)."""
    monkeypatch.setenv("PORTAL_USERNAME", "team")
    monkeypatch.delenv("PORTAL_PASSWORD", raising=False)
    resp = _get(f"{server}/api/ratings")
    assert resp.status == 200

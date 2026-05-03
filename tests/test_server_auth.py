"""Tests for portal Basic auth (issue #29)."""

from __future__ import annotations

import base64
import inspect
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
    Handler.extra_roots = {}
    return Handler


@pytest.fixture
def server(tmp_path, monkeypatch):
    """Start a real HTTPServer on a random port in a thread; tear down after."""
    # Default: clear creds. Individual tests can re-set with monkeypatch.
    monkeypatch.delenv("PORTAL_USERNAME", raising=False)
    monkeypatch.delenv("PORTAL_PASSWORD", raising=False)

    Handler = _make_handler_class(tmp_path)
    httpd = HTTPServer(("127.0.0.1", 0), Handler)
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


def test_no_credentials_serves_freely(server, monkeypatch):
    monkeypatch.delenv("PORTAL_USERNAME", raising=False)
    monkeypatch.delenv("PORTAL_PASSWORD", raising=False)
    # /api/ratings is a stable JSON endpoint that doesn't depend on filesystem
    # state beyond what the fixture provides.
    resp = _get(f"{server}/api/ratings")
    assert resp.status == 200


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

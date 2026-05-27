"""Ensure repo root is on sys.path so `import lib.social` works."""

from __future__ import annotations

import sys
import threading
from http.server import HTTPServer
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from lib import usage as usage_module
from tests.server_harness import make_handler_class


@pytest.fixture
def server(tmp_path, monkeypatch):
    """Start a real portal HTTPServer on a random port in a daemon thread.

    Yields the base URL. Auth is disabled by default; individual tests can
    re-enable it by setting PORTAL_USERNAME / PORTAL_PASSWORD via monkeypatch,
    since auth is evaluated per-request from the environment.
    """
    monkeypatch.delenv("PORTAL_USERNAME", raising=False)
    monkeypatch.delenv("PORTAL_PASSWORD", raising=False)
    monkeypatch.setattr(usage_module, "USAGE_LOG_PATH", tmp_path / "usage-log.json")

    Handler = make_handler_class(tmp_path)
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

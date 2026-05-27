"""Shared harness for driving the Rafiki portal HTTP handler in tests.

Exposes a Handler factory plus small HTTP helpers so both the auth tests and
the endpoint tests share one socket/thread setup (see the `server` fixture in
conftest.py).
"""

from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request
from http.client import HTTPConnection
from pathlib import Path
from urllib.parse import urlparse

from lib.server import _RafikiHandler


def make_handler_class(tmp_path: Path, *, extra_roots: dict | None = None) -> type:
    """Build a concrete handler class with the class attrs `serve()` sets.

    The output root lives at ``tmp_path/"output"`` so tests can stage files
    there and reach them through the running server.
    """
    output_root = tmp_path / "output"
    output_root.mkdir(exist_ok=True)

    class Handler(_RafikiHandler):
        pass

    Handler.output_root = output_root
    Handler.ratings_file = output_root / "ratings.json"
    Handler.feedback_file = output_root / "feedback.json"
    Handler.evaluations_file = output_root / "evaluations.json"
    Handler.archive_metadata_file = output_root / "archive-metadata.json"
    Handler.billing_imports_file = tmp_path / "billing-imports.json"
    Handler.extra_roots = extra_roots or {}
    return Handler


def _auth_header(req: urllib.request.Request, auth: tuple[str, str] | None) -> None:
    if auth is not None:
        token = base64.b64encode(f"{auth[0]}:{auth[1]}".encode()).decode()
        req.add_header("Authorization", f"Basic {token}")


def http_get(url: str, auth: tuple[str, str] | None = None):
    req = urllib.request.Request(url)
    _auth_header(req, auth)
    try:
        return urllib.request.urlopen(req, timeout=5)
    except urllib.error.HTTPError as e:
        return e


def http_post_json(url: str, payload: dict, auth: tuple[str, str] | None = None):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    _auth_header(req, auth)
    try:
        return urllib.request.urlopen(req, timeout=5)
    except urllib.error.HTTPError as e:
        return e


def http_post_raw(url: str, body: bytes, auth: tuple[str, str] | None = None):
    """POST an arbitrary (possibly non-JSON) body — for malformed-input paths."""
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    _auth_header(req, auth)
    try:
        return urllib.request.urlopen(req, timeout=5)
    except urllib.error.HTTPError as e:
        return e


def raw_get(base_url: str, raw_path: str) -> tuple[int, bytes]:
    """GET with a request-target sent verbatim, bypassing client-side dot-segment
    normalization. Needed to exercise the server's own path-traversal guard."""
    parts = urlparse(base_url)
    conn = HTTPConnection(parts.hostname, parts.port, timeout=5)
    try:
        conn.putrequest("GET", raw_path, skip_host=False, skip_accept_encoding=True)
        conn.putheader("Host", f"{parts.hostname}:{parts.port}")
        conn.endheaders()
        resp = conn.getresponse()
        return resp.status, resp.read()
    finally:
        conn.close()

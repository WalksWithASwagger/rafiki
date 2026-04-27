"""Lightweight local server for the Rafiki generative portal."""

from __future__ import annotations

import json
import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse


_MIME_MAP: dict[str, str] = {
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif":  "image/gif",
    ".html": "text/html; charset=utf-8",
    ".json": "application/json",
    ".css":  "text/css",
    ".js":   "application/javascript",
}


def _guess_mime(suffix: str) -> str:
    return _MIME_MAP.get(suffix.lower(), "application/octet-stream")


def _load_ratings(ratings_file: Path) -> dict:
    if ratings_file.exists():
        try:
            return json.loads(ratings_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


class _RafikiHandler(BaseHTTPRequestHandler):
    output_root: Path
    ratings_file: Path

    def log_message(self, fmt, *args):  # suppress noisy access log
        pass

    def do_OPTIONS(self):
        self._respond(204, "text/plain", b"")

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", ""):
            self._serve_library()
        elif path.startswith("/output/"):
            self._serve_static(path[len("/output/"):])
        elif path == "/api/ratings":
            self._serve_ratings()
        elif path == "/api/runs":
            self._serve_runs()
        else:
            self._404()

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/ratings":
            self._update_ratings()
        elif path == "/api/regen":
            self._regen()
        else:
            self._404()

    # ── Route handlers ────────────────────────────────────────────────────────

    def _serve_library(self):
        from lib.renderers.library import generate_library_viewer
        lib_path = generate_library_viewer(self.output_root)
        self._respond(200, "text/html; charset=utf-8", lib_path.read_bytes())

    def _serve_static(self, rel_path: str):
        # Strip leading slash; use normpath (not resolve) so symlinks under
        # output_root are served correctly without resolving them away.
        rel_path = rel_path.lstrip("/")
        target = Path(os.path.normpath(self.output_root / rel_path))
        try:
            target.relative_to(self.output_root)
        except ValueError:
            self._404()
            return
        if not target.exists() or not target.is_file():
            self._404()
            return
        self._respond(200, _guess_mime(target.suffix), target.read_bytes())

    def _serve_ratings(self):
        ratings = _load_ratings(self.ratings_file)
        self._respond(200, "application/json", json.dumps(ratings).encode())

    def _update_ratings(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
            key = data["key"]
            value = data.get("value")
        except Exception:
            self._respond(400, "application/json", b'{"error":"bad request"}')
            return
        ratings = _load_ratings(self.ratings_file)
        if value is None:
            ratings.pop(key, None)
        else:
            ratings[key] = value
        self.ratings_file.write_text(json.dumps(ratings, indent=2), encoding="utf-8")
        self._respond(200, "application/json", b'{"ok":true}')

    def _serve_runs(self):
        runs: list[dict] = []
        for rjp in sorted(self.output_root.glob("*/run-*/run.json")):
            try:
                data = json.loads(rjp.read_text(encoding="utf-8"))
                project = rjp.parent.parent.name
                run_id = rjp.parent.name
                images = []
                for img in data.get("images", []):
                    img_path = rjp.parent / img["file"]
                    images.append({
                        "file": f"{project}/{run_id}/{img['file']}",
                        "ok": img_path.exists(),
                        "name": img.get("name", ""),
                    })
                runs.append({
                    "project": project,
                    "run_id": run_id,
                    "model": data.get("model", ""),
                    "timestamp": data.get("timestamp", ""),
                    "aspect_ratio": data.get("aspect_ratio", "16:9"),
                    "style": data.get("style", ""),
                    "prompt_file": data.get("prompt_file", ""),
                    "images": images,
                })
            except Exception:
                continue
        self._respond(200, "application/json", json.dumps(runs).encode())

    def _regen(self):
        # Phase 3 placeholder — SSE regen not yet implemented
        self._respond(501, "application/json", b'{"error":"regen not yet implemented"}')

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _respond(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _404(self) -> None:
        self._respond(404, "application/json", b'{"error":"not found"}')


def serve(output_root: Path, port: int = 7433, open_browser: bool = False) -> None:
    """Start the Rafiki portal server and block until Ctrl-C."""
    output_root = Path(output_root).resolve()
    ratings_file = output_root / "ratings.json"

    class Handler(_RafikiHandler):
        pass

    Handler.output_root = output_root
    Handler.ratings_file = ratings_file

    httpd = HTTPServer(("127.0.0.1", port), Handler)
    url = f"http://localhost:{port}/"
    print(f"Rafiki portal → {url}")
    print(f"Output root:    {output_root}")
    print("Ctrl-C to stop.")

    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

"""Lightweight local server for the Rafiki generative portal."""

from __future__ import annotations

import base64
import json
import os
import secrets
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse


def _basic_auth_credentials() -> tuple[str, str] | None:
    """Return (user, password) if both PORTAL_USERNAME and PORTAL_PASSWORD are
    set in the environment; otherwise None (auth disabled)."""
    user = os.environ.get("PORTAL_USERNAME")
    pw = os.environ.get("PORTAL_PASSWORD")
    if user and pw:
        return user, pw
    return None


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
    extra_roots: dict[str, Path]  # project_name → real dir

    def log_message(self, fmt, *args):  # suppress noisy access log
        pass

    def _check_auth(self) -> bool:
        """If PORTAL_USERNAME + PORTAL_PASSWORD are set, require Basic auth.
        Returns True if the request may proceed; otherwise sends 401 and
        returns False."""
        creds = _basic_auth_credentials()
        if creds is None:
            return True
        expected_user, expected_pw = creds
        header = self.headers.get("Authorization", "")
        if header.startswith("Basic "):
            try:
                decoded = base64.b64decode(header[len("Basic "):]).decode("utf-8")
                user, _, pw = decoded.partition(":")
            except Exception:
                user, pw = "", ""
            user_ok = secrets.compare_digest(user, expected_user)
            pw_ok = secrets.compare_digest(pw, expected_pw)
            if user_ok and pw_ok:
                return True
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Rafiki Portal"')
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", "0")
        self.end_headers()
        return False

    def do_OPTIONS(self):
        if not self._check_auth():
            return
        self._respond(204, "text/plain", b"")

    def do_GET(self):
        if not self._check_auth():
            return
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
        if not self._check_auth():
            return
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
        """Serve a file from output_root or, for registered projects, from
        their real external directory — no symlinks needed."""
        rel_path = rel_path.lstrip("/")
        parts = rel_path.split("/", 1)
        project = parts[0]
        rest = parts[1] if len(parts) > 1 else ""

        if project in self.extra_roots:
            # Route directly to the external project directory
            root = self.extra_roots[project]
            target = Path(os.path.normpath(root / rest))
            try:
                target.relative_to(root)
            except ValueError:
                self._404()
                return
        else:
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
        from lib.renderers.library import load_extra_outputs, _scan_root
        runs: list[dict] = []
        extra_roots = load_extra_outputs()

        # output_root projects (excluding any overridden by extra_roots)
        for proj_dir in sorted(self.output_root.iterdir()):
            if not proj_dir.is_dir() or proj_dir.name in extra_roots:
                continue
            for rjp in sorted(proj_dir.glob("run-*/run.json")):
                try:
                    data = json.loads(rjp.read_text(encoding="utf-8"))
                    project = proj_dir.name
                    run_id = rjp.parent.name
                    images = [
                        {"file": f"{project}/{run_id}/{img['file']}",
                         "ok": (rjp.parent / img["file"]).exists(),
                         "name": img.get("name", "")}
                        for img in data.get("images", [])
                    ]
                    runs.append({
                        "project": project, "run_id": run_id,
                        "model": data.get("model", ""),
                        "timestamp": data.get("timestamp", ""),
                        "aspect_ratio": data.get("aspect_ratio", "16:9"),
                        "style": data.get("style", ""),
                        "prompt_file": data.get("prompt_file", ""),
                        "images": images,
                    })
                except Exception:
                    continue

        # extra_roots projects
        for project_name, extra_root in extra_roots.items():
            if not extra_root.exists():
                continue
            for rjp in sorted(extra_root.glob("run-*/run.json")):
                try:
                    data = json.loads(rjp.read_text(encoding="utf-8"))
                    run_id = rjp.parent.name
                    images = [
                        {"file": f"{project_name}/{run_id}/{img['file']}",
                         "ok": (rjp.parent / img["file"]).exists(),
                         "name": img.get("name", "")}
                        for img in data.get("images", [])
                    ]
                    runs.append({
                        "project": project_name, "run_id": run_id,
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


def serve(
    output_root: Path,
    port: int = 7433,
    open_browser: bool = False,
    public: bool = False,
) -> None:
    """Start the Rafiki portal server and block until Ctrl-C."""
    from lib.renderers.library import load_extra_outputs
    output_root = Path(output_root).resolve()
    ratings_file = output_root / "ratings.json"
    extra_roots = {name: Path(p) for name, p in load_extra_outputs().items()}

    class Handler(_RafikiHandler):
        pass

    Handler.output_root = output_root
    Handler.ratings_file = ratings_file
    Handler.extra_roots = extra_roots

    bind_host = "0.0.0.0" if public else "127.0.0.1"
    httpd = HTTPServer((bind_host, port), Handler)
    display_host = "localhost" if not public else "0.0.0.0"
    url = f"http://{display_host}:{port}/"
    print(f"Rafiki portal → {url}")
    print(f"Output root:    {output_root}")
    if extra_roots:
        for name, path in extra_roots.items():
            print(f"  + {name} → {path}")

    auth_on = _basic_auth_credentials() is not None
    if public and not auth_on:
        print(
            "WARNING: --public bound to 0.0.0.0 with NO authentication. "
            "Set PORTAL_USERNAME and PORTAL_PASSWORD to enable Basic auth."
        )
    elif auth_on:
        print("Auth: Basic (PORTAL_USERNAME / PORTAL_PASSWORD)")

    print("Ctrl-C to stop.")

    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

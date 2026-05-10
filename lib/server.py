"""Lightweight local server for the Rafiki generative portal."""

from __future__ import annotations

import base64
import json
import os
import re
import secrets
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from lib.batch import run_batch
from lib.models import DEFAULT_IMAGE_MODEL, resolve_model
from lib.prompts import ASPECT_RATIOS, parse_image_prompts_md

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = DEFAULT_IMAGE_MODEL
_TRUE_VALUES = {"1", "true", "yes", "on"}


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


def _slugify(value: str) -> str:
    out = []
    for ch in value.lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in "-_ ":
            out.append("-")
    slug = "".join(out)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug


def _coerce_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in _TRUE_VALUES
    return False


def _coerce_str(value: object, *, field: str, required: bool = False) -> str:
    if value is None:
        if required:
            raise ValueError(f"{field} is required")
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    text = value.strip()
    if required and not text:
        raise ValueError(f"{field} is required")
    return text


def _coerce_list_of_paths(value: object, *, field: str) -> list[str]:
    if value in (None, "", []):
        return []
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    if isinstance(value, list):
        parts = []
        for item in value:
            if not isinstance(item, str):
                raise ValueError(f"{field} entries must be strings")
            item = item.strip()
            if item:
                parts.append(item)
        return parts
    raise ValueError(f"{field} must be a comma-separated string or list of strings")


def _coerce_workers(value: object) -> int:
    if value in (None, ""):
        return 1
    try:
        workers = int(value)
    except (TypeError, ValueError) as e:
        raise ValueError("workers must be an integer") from e
    if workers < 1:
        raise ValueError("workers must be at least 1")
    return min(workers, 8)


def _normalise_aspect_ratio(value: object) -> str:
    text = _coerce_str(value, field="aspect_ratio") if value is not None else "16:9"
    if not text:
        text = "16:9"
    return ASPECT_RATIOS.get(text, text)


def _resolve_project_name(payload: dict, *, mode: str) -> str:
    raw = _coerce_str(payload.get("project"), field="project")
    if not raw and mode == "batch":
        prompt_file = _coerce_str(payload.get("prompt_file"), field="prompt_file")
        if prompt_file:
            raw = Path(prompt_file).stem
    if not raw:
        raw = "studio"
    slug = _slugify(raw)
    if not slug:
        raise ValueError("project must contain at least one letter or number")
    return slug


def _resolve_prompt_file(value: object) -> Path:
    raw = _coerce_str(value, field="prompt_file", required=True)
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    else:
        path = path.resolve()
    if not path.exists() or not path.is_file():
        raise ValueError(f"prompt_file not found: {path}")
    if path.suffix.lower() not in {".md", ".markdown"}:
        raise ValueError("prompt_file must be a Markdown file")
    return path


def _resolve_ref_paths(
    *,
    prompt_count: int,
    reference_image: str = "",
    reference_images: object = None,
) -> list[str | None]:
    multi = _coerce_list_of_paths(reference_images, field="reference_images")
    if multi:
        if len(multi) == 1:
            return multi * prompt_count
        if len(multi) != prompt_count:
            raise ValueError(
                f"reference_images has {len(multi)} path(s) but {prompt_count} prompt(s)"
            )
        return multi
    if reference_image:
        return [reference_image] * prompt_count
    return [None] * prompt_count


def _prompt_name_from_text(prompt: str) -> str:
    first_line = prompt.strip().splitlines()[0] if prompt.strip() else "Prompt Studio"
    compact = re.sub(r"\s+", " ", first_line).strip()
    return compact[:60] if compact else "Prompt Studio"


def _result_payload(result, *, mode: str, project: str) -> dict:
    return {
        "ok": True,
        "all_ok": result.success,
        "mode": mode,
        "project": project,
        "generated": result.success_count,
        "total": result.total,
        "run_id": result.run_id,
        "run_dir": str(result.run_dir),
        "project_dir": str(result.project_dir),
        "viewer_path": result.viewer_path,
        "viewer_url": f"/output/{project}/viewer.html",
        "run_viewer_url": f"/output/{project}/run-{result.run_id}/viewer.html",
        "library_url": "/",
        "images": result.images,
    }


def _run_portal_job(payload: dict, *, output_root: Path) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("request body must be a JSON object")

    mode = _coerce_str(payload.get("mode"), field="mode") or "single"
    if mode not in {"single", "batch"}:
        raise ValueError("mode must be 'single' or 'batch'")

    project = _resolve_project_name(payload, mode=mode)
    project_dir = output_root / project
    model = resolve_model(_coerce_str(payload.get("model"), field="model") or DEFAULT_MODEL)
    aspect_ratio = _normalise_aspect_ratio(payload.get("aspect_ratio"))
    resolution = _coerce_str(payload.get("resolution"), field="resolution") or "1K"
    quality = _coerce_str(payload.get("quality"), field="quality") or "high"
    style = _coerce_str(payload.get("style"), field="style") or None
    reference_image = _coerce_str(payload.get("reference_image"), field="reference_image")
    global_reference_images = _coerce_list_of_paths(
        payload.get("global_reference_images"),
        field="global_reference_images",
    )
    reference_role = _coerce_str(payload.get("reference_role"), field="reference_role") or "style"
    if reference_role not in {"style", "brand", "mockup"}:
        raise ValueError("reference_role must be 'style', 'brand', or 'mockup'")
    composition_references = _coerce_list_of_paths(
        payload.get("composition_references"),
        field="composition_references",
    ) or None
    dry_run = _coerce_bool(payload.get("dry_run"))
    workers = _coerce_workers(payload.get("workers"))

    if mode == "single":
        prompt = _coerce_str(payload.get("prompt"), field="prompt", required=True)
        name = _coerce_str(payload.get("name"), field="name") or _prompt_name_from_text(prompt)
        result = run_batch(
            prompts=[{"name": name, "prompt": prompt}],
            project_dir=project_dir,
            model=model,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            quality=quality,
            style=style,
            ref_paths=[reference_image or None],
            global_reference_images=global_reference_images,
            reference_role=reference_role,
            composition_references=composition_references,
            dry_run=dry_run,
            workers=1,
            generate_viewer_html=True,
            prompt_file="",
            invocation_source="portal",
        )
        return _result_payload(result, mode=mode, project=project)

    prompt_file = _resolve_prompt_file(payload.get("prompt_file"))
    prompts = parse_image_prompts_md(prompt_file)
    if not prompts:
        raise ValueError(f"no prompts found in {prompt_file}")
    ref_paths = _resolve_ref_paths(
        prompt_count=len(prompts),
        reference_image=reference_image,
        reference_images=payload.get("reference_images"),
    )
    result = run_batch(
        prompts=prompts,
        project_dir=project_dir,
        model=model,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        quality=quality,
        style=style,
        ref_paths=ref_paths,
        global_reference_images=global_reference_images,
        reference_role=reference_role,
        composition_references=composition_references,
        dry_run=dry_run,
        workers=workers,
        generate_viewer_html=True,
        prompt_file=str(prompt_file),
        invocation_source="portal",
    )
    return _result_payload(result, mode=mode, project=project)


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
        elif path == "/api/actions":
            self._serve_actions()
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
        elif path == "/api/actions":
            self._run_action()
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

    def _serve_actions(self):
        from lib.portal_actions import discover_actions

        self._respond(200, "application/json", json.dumps({"actions": discover_actions()}).encode())

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
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body or b"{}")
        except Exception:
            self._respond(400, "application/json", b'{"error":"bad request"}')
            return

        try:
            result = _run_portal_job(payload, output_root=self.output_root)
        except ValueError as e:
            self._respond(
                400,
                "application/json",
                json.dumps({"error": str(e)}).encode("utf-8"),
            )
            return
        except Exception as e:
            self._respond(
                500,
                "application/json",
                json.dumps({"error": "generation failed", "detail": str(e)}).encode("utf-8"),
            )
            return

        self._respond(200, "application/json", json.dumps(result).encode("utf-8"))

    def _run_action(self):
        from lib.portal_actions import run_action

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body or b"{}")
        except Exception:
            self._respond(400, "application/json", b'{"error":"bad request"}')
            return

        try:
            result = run_action(payload, output_root=self.output_root)
        except PermissionError as e:
            self._respond(409, "application/json", json.dumps({"error": str(e)}).encode("utf-8"))
            return
        except (ValueError, FileNotFoundError) as e:
            self._respond(400, "application/json", json.dumps({"error": str(e)}).encode("utf-8"))
            return
        except Exception as e:
            self._respond(
                500,
                "application/json",
                json.dumps({"error": "portal action failed", "detail": str(e)}).encode("utf-8"),
            )
            return

        self._respond(200, "application/json", json.dumps(result).encode("utf-8"))

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
    httpd = ThreadingHTTPServer((bind_host, port), Handler)
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

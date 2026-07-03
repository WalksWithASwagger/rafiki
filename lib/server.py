"""Lightweight local server for the Rafiki generative portal."""

from __future__ import annotations

import base64
import json
import os
import re
import secrets
import socket
import subprocess
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, unquote, urlparse
from urllib.request import Request, urlopen

from lib.batch import run_batch
from lib.models import ALIASES, DEFAULT_IMAGE_MODEL, resolve_model
from lib.prompts import ASPECT_RATIOS, parse_image_prompts_md

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = DEFAULT_IMAGE_MODEL
_TRUE_VALUES = {"1", "true", "yes", "on"}
FRONTEND_DIR = REPO_ROOT / "frontend"
FRONTEND_ENTRY = FRONTEND_DIR / ".output" / "server" / "index.mjs"
FRONTEND_ROUTES = (
    "/",
    "/generate",
    "/library",
    "/viewer",
    "/export",
    "/registry",
    "/health",
    "/spend",
    "/assets",
)
PORTAL_MODEL_OPTIONS = (
    "gemini-2.5-flash-image",
    "gemini-3-pro-image-preview",
    "gpt-image-2",
    "gpt-image-1",
    "dall-e-3",
    "dall-e-2",
)
QUALITY_OPTIONS = ("low", "medium", "high")
RESOLUTION_OPTIONS = ("1K", "2K", "4K")
REFERENCE_ROLES = ("style", "brand", "mockup")


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
    ".mp4":  "video/mp4",
    ".mov":  "video/quicktime",
    ".m4v":  "video/mp4",
    ".webm": "video/webm",
    ".mp3":  "audio/mpeg",
    ".wav":  "audio/wav",
    ".m4a":  "audio/mp4",
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


def _confirmed_execute(payload: dict, *, label: str) -> bool:
    execute = _coerce_bool(payload.get("execute"))
    if execute and not _coerce_bool(payload.get("confirm_execute")):
        raise ValueError(f"{label} execute mode requires confirm_execute=true")
    return execute


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
        raise ValueError("prompt_file not found")
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


def _normalise_reference_request_path(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https"}:
        return parsed.path
    return value


def _resolve_output_reference(
    value: str,
    *,
    output_root: Path,
    extra_roots: dict[str, Path] | None = None,
) -> str:
    rel_path = unquote(value.removeprefix("/output/")).lstrip("/")
    if not rel_path:
        raise ValueError("output reference must include a file path")

    extra_roots = extra_roots or {}
    project, _, rest = rel_path.partition("/")
    if project in extra_roots:
        root = Path(extra_roots[project]).expanduser().resolve()
        rest_path = Path(os.path.normpath(rest))
        if not rest or rest_path.is_absolute() or ".git" in rest_path.parts or rest_path.name == ".env":
            raise ValueError("output reference is not allowed")
        target = (root / rest_path).resolve()
        try:
            target.relative_to(root)
        except ValueError as e:
            raise ValueError("output reference escapes its project root") from e
    else:
        root = output_root.expanduser().resolve()
        rel_norm = Path(os.path.normpath(rel_path))
        if rel_norm.is_absolute() or ".git" in rel_norm.parts or rel_norm.name == ".env":
            raise ValueError("output reference is not allowed")
        target = (root / rel_norm).resolve()
        try:
            target.relative_to(root)
        except ValueError as e:
            raise ValueError("output reference escapes the output root") from e

    if not target.exists() or not target.is_file():
        raise ValueError(f"output reference not found: {value}")
    return str(target)


def _resolve_media_reference(value: str, *, media_roots: dict[str, object] | None = None) -> str:
    rel_path = unquote(value.removeprefix("/media/")).lstrip("/")
    root_key, _, rest = rel_path.partition("/")
    if not root_key or not rest:
        raise ValueError("media reference must include a root and file path")
    root = (media_roots or {}).get(root_key)
    if root is None:
        raise ValueError(f"unknown media reference root: {root_key}")
    root_path = Path(getattr(root, "path", root)).expanduser().resolve()
    rest_path = Path(os.path.normpath(rest))
    if rest_path.is_absolute() or ".git" in rest_path.parts or rest_path.name == ".env":
        raise ValueError("media reference is not allowed")
    target = (root_path / rest_path).resolve()
    try:
        target.relative_to(root_path)
    except ValueError as e:
        raise ValueError("media reference escapes its root") from e
    if not target.exists() or not target.is_file():
        raise ValueError(f"media reference not found: {value}")
    return str(target)


def _resolve_reference_source(
    value: str,
    *,
    output_root: Path,
    extra_roots: dict[str, Path] | None = None,
    media_roots: dict[str, object] | None = None,
) -> str:
    path = _normalise_reference_request_path(value.strip())
    if path.startswith("/output/"):
        return _resolve_output_reference(path, output_root=output_root, extra_roots=extra_roots)
    if path.startswith("/media/"):
        return _resolve_media_reference(path, media_roots=media_roots)
    return value.strip()


def _resolve_reference_sources(
    value: object,
    *,
    field: str,
    output_root: Path,
    extra_roots: dict[str, Path] | None = None,
    media_roots: dict[str, object] | None = None,
) -> list[str]:
    return [
        _resolve_reference_source(
            item,
            output_root=output_root,
            extra_roots=extra_roots,
            media_roots=media_roots,
        )
        for item in _coerce_list_of_paths(value, field=field)
    ]


def _prompt_name_from_text(prompt: str) -> str:
    first_line = prompt.strip().splitlines()[0] if prompt.strip() else "Prompt Studio"
    compact = re.sub(r"\s+", " ", first_line).strip()
    return compact[:60] if compact else "Prompt Studio"


def _coerce_inline_prompts(value: object) -> list[dict]:
    if value in (None, "", []):
        return []
    if not isinstance(value, list):
        raise ValueError("prompts must be an array of prompt objects")
    prompts: list[dict] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"prompts[{index}] must be an object")
        prompt = _coerce_str(item.get("prompt"), field=f"prompts[{index}].prompt", required=True)
        name = _coerce_str(item.get("name"), field=f"prompts[{index}].name") or _prompt_name_from_text(prompt)
        row = {"name": name, "prompt": prompt}
        model = _coerce_str(item.get("model"), field=f"prompts[{index}].model")
        style = _coerce_str(item.get("style"), field=f"prompts[{index}].style")
        quality = _coerce_str(item.get("quality"), field=f"prompts[{index}].quality")
        aspect_ratio = _coerce_str(item.get("aspect_ratio"), field=f"prompts[{index}].aspect_ratio")
        usage = _coerce_str(item.get("usage"), field=f"prompts[{index}].usage")
        if model:
            row["model"] = resolve_model(model)
        if style:
            row["style"] = style
        if quality:
            row["quality"] = quality
        if aspect_ratio:
            row["aspect_ratio"] = _normalise_aspect_ratio(aspect_ratio)
        if usage:
            row["usage"] = usage
        prompts.append(row)
    return prompts


def _style_registry_entries() -> list[dict]:
    try:
        from lib.styles import get_default_style, load_styles

        styles = load_styles()
        default_style = get_default_style()
    except Exception:
        styles = {}
        default_style = "none"

    entries = [
        {
            "key": "none",
            "name": "No style",
            "description": "Use the prompt without an appended style preset.",
            "default": default_style == "none",
            "special": True,
        }
    ]
    for key, cfg in sorted(styles.items()):
        if not isinstance(cfg, dict):
            continue
        entries.append(
            {
                "key": key,
                "name": cfg.get("name") or key.replace("-", " ").title(),
                "description": cfg.get("description", ""),
                "useContext": cfg.get("use_context", ""),
                "default": key == default_style,
                "special": False,
            }
        )
    return entries


def _generate_options_payload() -> dict:
    aliases_by_model: dict[str, list[str]] = {}
    for alias, model in ALIASES.items():
        aliases_by_model.setdefault(model, []).append(alias)
    return {
        "defaultModel": DEFAULT_MODEL,
        "models": [
            {
                "id": model,
                "label": model,
                "aliases": sorted(aliases_by_model.get(model, [])),
            }
            for model in PORTAL_MODEL_OPTIONS
        ],
        "aliases": ALIASES,
        "aspectPresets": [
            {"key": key, "label": key, "value": value}
            for key, value in sorted(ASPECT_RATIOS.items())
        ],
        "aspectRatios": ["16:9", "1:1", "9:16", "4:3", "3:4"],
        "qualities": list(QUALITY_OPTIONS),
        "resolutions": list(RESOLUTION_OPTIONS),
        "referenceRoles": list(REFERENCE_ROLES),
        "styles": _style_registry_entries(),
    }


def _prompt_preview_payload(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("request body must be a JSON object")
    prompt_file = _resolve_prompt_file(payload.get("prompt_file"))
    prompts = parse_image_prompts_md(prompt_file)
    return {
        "ok": True,
        "promptFile": _coerce_str(payload.get("prompt_file"), field="prompt_file", required=True),
        "count": len(prompts),
        "prompts": prompts,
        "metadata": {
            "source": "markdown",
            "format": prompt_file.suffix.lower().lstrip("."),
        },
    }


def _result_payload(result, *, mode: str, project: str, registry_refresh: dict | None = None) -> dict:
    payload = {
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
    if registry_refresh:
        payload["registry"] = registry_refresh
    return payload


def _refresh_registry_after_generation(result, *, output_root: Path, dry_run: bool) -> dict | None:
    if dry_run or not result.success:
        return None
    from lib import registry

    return registry.refresh_cache(output_root=output_root, reason="portal-generation")


def _safe_error_text(value: object) -> str:
    text = str(value or "").strip()
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(
        r"(?i)\b([A-Z0-9_-]*(?:api[_-]?key|token|secret|password))(\s*[=:]\s*)([^\s,;]+)",
        r"\1\2[redacted]",
        text,
    )
    text = re.sub(
        r"(?i)\b(authorization\s*:\s*bearer\s+)([A-Za-z0-9._~+/=-]+)",
        r"\1[redacted]",
        text,
    )
    text = re.sub(
        r"(?i)\b(bearer\s+)(sk-[A-Za-z0-9_-]+|secret_[A-Za-z0-9_-]+|[A-Za-z0-9._~+/=-]{20,})",
        r"\1[redacted]",
        text,
    )
    return text[:2000]


def _run_portal_job(
    payload: dict,
    *,
    output_root: Path,
    extra_roots: dict[str, Path] | None = None,
    media_roots: dict[str, object] | None = None,
) -> dict:
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
    reference_image_raw = _coerce_str(payload.get("reference_image"), field="reference_image")
    reference_image = (
        _resolve_reference_source(
            reference_image_raw,
            output_root=output_root,
            extra_roots=extra_roots,
            media_roots=media_roots,
        )
        if reference_image_raw
        else ""
    )
    global_reference_images = _resolve_reference_sources(
        payload.get("global_reference_images"),
        field="global_reference_images",
        output_root=output_root,
        extra_roots=extra_roots,
        media_roots=media_roots,
    )
    reference_role = _coerce_str(payload.get("reference_role"), field="reference_role") or "style"
    if reference_role not in set(REFERENCE_ROLES):
        raise ValueError("reference_role must be 'style', 'brand', or 'mockup'")
    composition_references = _resolve_reference_sources(
        payload.get("composition_references"),
        field="composition_references",
        output_root=output_root,
        extra_roots=extra_roots,
        media_roots=media_roots,
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
        refresh = _refresh_registry_after_generation(result, output_root=output_root, dry_run=dry_run)
        return _result_payload(result, mode=mode, project=project, registry_refresh=refresh)

    inline_prompts = _coerce_inline_prompts(payload.get("prompts"))
    prompt_file: Path | None = None
    if inline_prompts:
        prompts = inline_prompts
    else:
        prompt_file = _resolve_prompt_file(payload.get("prompt_file"))
        prompts = parse_image_prompts_md(prompt_file)
    if not prompts:
        source = prompt_file if prompt_file else "inline prompts"
        raise ValueError(f"no prompts found in {source}")
    reference_images = _resolve_reference_sources(
        payload.get("reference_images"),
        field="reference_images",
        output_root=output_root,
        extra_roots=extra_roots,
        media_roots=media_roots,
    )
    ref_paths = _resolve_ref_paths(
        prompt_count=len(prompts),
        reference_image=reference_image,
        reference_images=reference_images,
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
        prompt_file=str(prompt_file) if prompt_file else "",
        invocation_source="portal",
    )
    refresh = _refresh_registry_after_generation(result, output_root=output_root, dry_run=dry_run)
    return _result_payload(result, mode=mode, project=project, registry_refresh=refresh)


class _RafikiHandler(BaseHTTPRequestHandler):
    output_root: Path
    ratings_file: Path
    feedback_file: Path
    evaluations_file: Path
    archive_metadata_file: Path
    billing_imports_file: Path
    video_selections_file: Path = REPO_ROOT / "data" / "video-selections.json"
    media_registry_file: Path | None = None
    extra_roots: dict[str, Path]  # project_name → real dir
    media_roots: dict[str, object] = {}
    frontend_origin: str | None = None

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
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/api/library-state":
            self._serve_library_state()
        elif path == "/api/generate-options":
            self._serve_generate_options()
        elif path in ("/legacy-suite", "/legacy-suite/"):
            self._serve_legacy_suite()
        elif path in ("/legacy-library", "/legacy-library/"):
            self._serve_legacy_library()
        elif _is_frontend_route(path):
            self._serve_frontend(parsed)
        elif path == "/favicon.ico":
            self._serve_frontend(parsed)
        elif path.startswith("/output/"):
            self._serve_static(path[len("/output/"):])
        elif path.startswith("/media/"):
            self._serve_media_file(path[len("/media/"):])
        elif path == "/api/media":
            self._serve_media(parsed.query)
        elif path == "/api/media/subjects":
            self._serve_media_subjects()
        elif path == "/api/media/styles":
            self._serve_media_styles()
        elif path == "/api/media/video-edits":
            self._serve_media_video_edits()
        elif path == "/api/media/jobs":
            self._serve_media_jobs()
        elif path == "/api/media/warnings":
            self._serve_media_warnings()
        elif path == "/api/media/selections/edl":
            self._serve_media_selection_edl(parsed.query)
        elif path == "/api/media/selections":
            self._serve_media_selections()
        elif path == "/api/actions":
            self._serve_actions()
        elif path == "/api/ratings":
            self._serve_ratings()
        elif path == "/api/feedback":
            self._serve_feedback()
        elif path == "/api/evaluations":
            self._serve_evaluations()
        elif path == "/api/archive-metadata":
            self._serve_archive_metadata()
        elif path == "/api/usage":
            self._serve_usage()
        elif path == "/api/deploy-readiness":
            self._serve_deploy_readiness(parsed.query)
        elif path == "/api/billing-imports":
            self._serve_billing_imports()
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
        elif path == "/api/feedback":
            self._update_feedback()
        elif path == "/api/evaluations":
            self._update_evaluation()
        elif path == "/api/archive-metadata":
            self._update_archive_metadata()
        elif path == "/api/billing-imports":
            self._update_billing_imports()
        elif path == "/api/regen":
            self._regen()
        elif path == "/api/prompt-preview":
            self._prompt_preview()
        elif path == "/api/actions":
            self._run_action()
        elif path == "/api/media/selections/import":
            self._import_media_selection_edl()
        elif path == "/api/media/selections":
            self._update_media_selection()
        elif path == "/api/media/notes":
            self._update_media_note()
        elif path == "/api/jobs/train-lora/preview":
            self._preview_train_lora()
        elif path == "/api/jobs/train-lora":
            self._run_train_lora()
        elif path == "/api/jobs/video-generate/preview":
            self._preview_video_generate()
        elif path == "/api/jobs/video-generate":
            self._run_video_generate()
        else:
            self._404()

    # ── Route handlers ────────────────────────────────────────────────────────

    def _serve_legacy_library(self):
        from lib.renderers.library import generate_library_viewer
        lib_path = generate_library_viewer(self.output_root)
        self._respond(200, "text/html; charset=utf-8", lib_path.read_bytes())

    def _serve_legacy_suite(self):
        from lib.renderers.media_suite import render_media_suite

        self._respond(200, "text/html; charset=utf-8", render_media_suite())

    def _serve_frontend(self, parsed):
        if not self.frontend_origin:
            if parsed.path in ("/", ""):
                self._serve_legacy_suite()
            elif parsed.path.startswith("/library"):
                self._serve_legacy_library()
            elif parsed.path == "/favicon.ico":
                self._respond(204, "image/x-icon", b"")
            else:
                self._respond(503, "application/json", b'{"error":"frontend unavailable"}')
            return

        target = f"{self.frontend_origin}{parsed.path}"
        if parsed.query:
            target = f"{target}?{parsed.query}"
        req = Request(
            target,
            headers={
                "Accept": self.headers.get("Accept", "*/*"),
                "User-Agent": self.headers.get("User-Agent", "rafiki-python-proxy"),
            },
        )
        try:
            with urlopen(req, timeout=15) as resp:
                self._respond_proxy(resp.status, resp.headers, resp.read())
        except HTTPError as e:
            self._respond_proxy(e.code, e.headers, e.read())
        except URLError:
            self._respond(502, "application/json", b'{"error":"frontend proxy failed"}')

    def _serve_library_state(self):
        from lib.frontend_state import build_library_state

        payload = build_library_state(
            self.output_root,
            extra_roots=self.extra_roots,
            ratings_file=self.ratings_file,
            registry_file=REPO_ROOT / "data" / "asset-registry.json",
        )
        self._respond(200, "application/json", json.dumps(payload).encode())

    def _serve_generate_options(self):
        self._respond(200, "application/json", json.dumps(_generate_options_payload()).encode())

    def _serve_static(self, rel_path: str):
        """Serve a file from output_root or, for registered projects, from
        their real external directory — no symlinks needed."""
        rel_path = unquote(rel_path).lstrip("/")
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
        self._respond_file(target)

    def _serve_media_file(self, rel_path: str):
        rel_path = unquote(rel_path).lstrip("/")
        parts = rel_path.split("/", 1)
        if len(parts) != 2:
            self._404()
            return
        root_key, rest = parts
        root = self.media_roots.get(root_key)
        if root is None:
            self._404()
            return
        root_path = Path(getattr(root, "path", "")).expanduser().resolve()
        rest_path = Path(os.path.normpath(rest))
        if rest_path.is_absolute() or ".git" in rest_path.parts or rest_path.name == ".env":
            self._404()
            return
        target = (root_path / rest_path).resolve()
        try:
            target.relative_to(root_path)
        except ValueError:
            self._404()
            return
        if not target.exists() or not target.is_file():
            self._404()
            return
        self._respond_file(target)

    def _serve_media(self, query: str = ""):
        from lib import media_registry

        params = parse_qs(query)
        refresh = (params.get("refresh") or [""])[0].strip().lower() in _TRUE_VALUES
        incremental = (params.get("incremental") or [""])[0].strip().lower() in _TRUE_VALUES
        registry_path = self._media_registry_path()
        if refresh:
            data = media_registry.index(
                roots=self.media_roots or None,
                registry_path=registry_path,
                incremental=incremental,
            )
        else:
            data = media_registry.load_registry(registry_path)
        q = (params.get("q") or [""])[0].strip()
        kind = (params.get("kind") or [""])[0].strip()
        collection = (params.get("collection") or [""])[0].strip()
        subject = (params.get("subject") or [""])[0].strip()
        project = (params.get("project") or [""])[0].strip()
        view = (params.get("view") or ["review"])[0].strip()
        entries = media_registry.filter_entry_dicts(
            data,
            query=q,
            kind=kind,
            collection=collection,
            subject=subject,
            project=project,
            view=view,
        )
        payload = {
            "summary": data.get("summary", {}),
            "entries": entries,
            "collections": sorted({entry.get("collection", "") for entry in data.get("entries", []) if entry.get("collection")}),
            "warnings": data.get("warnings", []),
            "view": view,
            "matched_entries": len(entries),
            "total_entries": len(data.get("entries", [])),
        }
        self._respond(200, "application/json", json.dumps(payload).encode())

    def _serve_media_subjects(self):
        from lib import media_registry

        payload = {"subjects": media_registry.subject_profiles()}
        self._respond(200, "application/json", json.dumps(payload).encode())

    def _serve_media_styles(self):
        from lib import media_registry

        payload = {"styles": [style.to_dict() for style in media_registry.styles()]}
        self._respond(200, "application/json", json.dumps(payload).encode())

    def _serve_media_video_edits(self):
        from lib import media_registry

        payload = {"video_edits": [edit.to_dict() for edit in media_registry.video_edits()]}
        self._respond(200, "application/json", json.dumps(payload).encode())

    def _serve_media_jobs(self):
        from lib.jobs import list_jobs

        self._respond(200, "application/json", json.dumps({"jobs": list_jobs()}).encode())

    def _serve_media_warnings(self):
        from lib import media_registry

        data = media_registry.load_registry(self._media_registry_path())
        payload = {"warnings": data.get("warnings", [])}
        self._respond(200, "application/json", json.dumps(payload).encode())

    def _serve_media_selections(self):
        self._respond(200, "application/json", json.dumps(self._load_video_selections()).encode())

    def _serve_media_selection_edl(self, query: str = ""):
        from lib import media_registry
        from lib.video_jobs import export_video_selection_edl

        params = parse_qs(query)
        include = [
            item.strip()
            for raw in params.get("include", [])
            for item in raw.split(",")
            if item.strip()
        ]
        project = (params.get("project") or [""])[0].strip()
        try:
            registry = media_registry.load_registry(self._media_registry_path())
            edl = export_video_selection_edl(
                selections=self._load_video_selections(),
                registry=registry,
                selection_values=include or None,
                project=project,
            )
        except ValueError as e:
            self._respond(400, "application/json", json.dumps({"error": str(e)}).encode("utf-8"))
            return
        self._respond(200, "application/json", json.dumps(edl).encode("utf-8"))

    def _serve_ratings(self):
        ratings = _load_ratings(self.ratings_file)
        self._respond(200, "application/json", json.dumps(ratings).encode())

    def _serve_feedback(self):
        from lib.feedback import load_feedback

        self._respond(200, "application/json", json.dumps(load_feedback(self.feedback_file)).encode())

    def _serve_evaluations(self):
        from lib.evaluations import load_evaluations

        self._respond(200, "application/json", json.dumps(load_evaluations(self.evaluations_file)).encode())

    def _serve_archive_metadata(self):
        from lib.archive_metadata import load_archive_metadata

        self._respond(200, "application/json", json.dumps(load_archive_metadata(self.archive_metadata_file)).encode())

    def _serve_usage(self):
        from lib.usage import summarize_usage

        summary = summarize_usage(
            self.output_root,
            extra_roots=self.extra_roots,
            billing_import_path=self.billing_imports_file,
        )
        self._respond(200, "application/json", json.dumps(summary).encode())

    def _serve_billing_imports(self):
        from lib.billing import summarize_billing_imports

        summary = summarize_billing_imports(self.billing_imports_file)
        self._respond(200, "application/json", json.dumps(summary).encode())

    def _serve_deploy_readiness(self, query: str = ""):
        from lib.deploy.readiness import check_deploy_readiness

        params = parse_qs(query)
        project = (params.get("project") or [""])[0].strip()
        viewer_raw = (params.get("viewer_dir") or [""])[0].strip()
        viewer_dir = Path(viewer_raw).expanduser() if viewer_raw else None
        public = (params.get("public") or [""])[0].strip().lower() in _TRUE_VALUES
        summary = check_deploy_readiness(
            output_root=self.output_root,
            project=project,
            viewer_dir=viewer_dir,
            public=public,
        )
        self._respond(200, "application/json", json.dumps(summary).encode())

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

    def _update_feedback(self):
        from lib.feedback import update_feedback

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body or b"{}")
            result = update_feedback(self.feedback_file, payload)
        except ValueError as e:
            self._respond(400, "application/json", json.dumps({"error": str(e)}).encode("utf-8"))
            return
        except Exception as e:
            self._respond(
                500,
                "application/json",
                json.dumps({"error": "feedback update failed", "detail": str(e)}).encode("utf-8"),
            )
            return
        self._respond(200, "application/json", json.dumps(result).encode("utf-8"))

    def _update_evaluation(self):
        from lib.evaluations import update_evaluation

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body or b"{}")
            result = update_evaluation(self.evaluations_file, payload)
        except ValueError as e:
            self._respond(400, "application/json", json.dumps({"error": str(e)}).encode("utf-8"))
            return
        except Exception as e:
            self._respond(
                500,
                "application/json",
                json.dumps({"error": "evaluation update failed", "detail": str(e)}).encode("utf-8"),
            )
            return
        self._respond(200, "application/json", json.dumps(result).encode("utf-8"))

    def _update_archive_metadata(self):
        from lib.archive_metadata import update_archive_metadata

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body or b"{}")
            result = update_archive_metadata(self.archive_metadata_file, payload)
        except ValueError as e:
            self._respond(400, "application/json", json.dumps({"error": str(e)}).encode("utf-8"))
            return
        except Exception as e:
            self._respond(
                500,
                "application/json",
                json.dumps({"error": "archive metadata update failed", "detail": str(e)}).encode("utf-8"),
            )
            return
        self._respond(200, "application/json", json.dumps(result).encode("utf-8"))

    def _update_billing_imports(self):
        from lib.billing import append_billing_entries

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body or b"{}")
            if not isinstance(payload, dict):
                raise ValueError("request body must be a JSON object")
            rows = payload.get("entries")
            if rows is None:
                rows = [payload]
            if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
                raise ValueError("entries must be an array of objects")
            result = append_billing_entries(
                self.billing_imports_file,
                rows,
                provider=_coerce_str(payload.get("provider"), field="provider"),
                label=_coerce_str(payload.get("label"), field="label"),
                source="portal",
            )
        except ValueError as e:
            self._respond(400, "application/json", json.dumps({"error": str(e)}).encode("utf-8"))
            return
        except Exception as e:
            self._respond(
                500,
                "application/json",
                json.dumps({"error": "billing import failed", "detail": str(e)}).encode("utf-8"),
            )
            return
        self._respond(200, "application/json", json.dumps(result).encode("utf-8"))

    def _serve_runs(self):
        from lib.renderers.library import load_extra_outputs
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
            result = _run_portal_job(
                payload,
                output_root=self.output_root,
                extra_roots=self.extra_roots,
                media_roots=self.media_roots,
            )
        except ValueError as e:
            self._respond(
                400,
                "application/json",
                json.dumps({"error": _safe_error_text(e)}).encode("utf-8"),
            )
            return
        except Exception as e:
            self._respond(
                500,
                "application/json",
                json.dumps({"error": "generation failed", "detail": _safe_error_text(e)}).encode("utf-8"),
            )
            return

        self._respond(200, "application/json", json.dumps(result).encode("utf-8"))

    def _prompt_preview(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body or b"{}")
            result = _prompt_preview_payload(payload)
        except ValueError as e:
            self._respond(400, "application/json", json.dumps({"error": _safe_error_text(e)}).encode("utf-8"))
            return
        except Exception as e:
            self._respond(
                500,
                "application/json",
                json.dumps({"error": "prompt preview failed", "detail": _safe_error_text(e)}).encode("utf-8"),
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

    def _update_media_selection(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body or b"{}")
            key = _coerce_str(payload.get("key"), field="key", required=True)
            value = _coerce_str(payload.get("value"), field="value")
            if value and value not in {"focus", "star", "exclude"}:
                raise ValueError("value must be focus, star, exclude, or empty")
        except ValueError as e:
            self._respond(400, "application/json", json.dumps({"error": str(e)}).encode("utf-8"))
            return
        except Exception:
            self._respond(400, "application/json", b'{"error":"bad request"}')
            return

        data = self._load_video_selections()
        items = data.setdefault("items", {})
        if value:
            items[key] = value
        else:
            items.pop(key, None)
        self.video_selections_file.parent.mkdir(parents=True, exist_ok=True)
        self.video_selections_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self._respond(200, "application/json", json.dumps({"ok": True, "items": items}).encode("utf-8"))

    def _update_media_note(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body or b"{}")
            key = _coerce_str(payload.get("key"), field="key", required=True)
            note = _coerce_str(payload.get("note"), field="note")
        except ValueError as e:
            self._respond(400, "application/json", json.dumps({"error": str(e)}).encode("utf-8"))
            return
        except Exception:
            self._respond(400, "application/json", b'{"error":"bad request"}')
            return

        data = self._load_video_selections()
        notes = data.setdefault("notes", {})
        if note:
            notes[key] = note[:2000]
        else:
            notes.pop(key, None)
        self.video_selections_file.parent.mkdir(parents=True, exist_ok=True)
        self.video_selections_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self._respond(200, "application/json", json.dumps({"ok": True, "notes": notes}).encode("utf-8"))

    def _import_media_selection_edl(self):
        from lib import media_registry
        from lib.video_jobs import import_video_selection_payload

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body or b"{}")
            if not isinstance(payload, dict):
                raise ValueError("request body must be a JSON object")
            source = payload.get("edl") if isinstance(payload.get("edl"), dict) else payload
            default_selection = _coerce_str(payload.get("default_selection"), field="default_selection") or "focus"
            replace = True if "replace" not in payload else _coerce_bool(payload.get("replace"))
            registry = media_registry.load_registry(self._media_registry_path())
            imported = import_video_selection_payload(
                source,
                registry=registry,
                default_selection=default_selection,
            )
        except ValueError as e:
            self._respond(400, "application/json", json.dumps({"error": str(e)}).encode("utf-8"))
            return
        except Exception as e:
            self._respond(
                500,
                "application/json",
                json.dumps({"error": "selection import failed", "detail": _safe_error_text(e)}).encode("utf-8"),
            )
            return

        data = self._load_video_selections()
        items = {} if replace else dict(data.get("items") or {})
        items.update(imported["items"])
        data["items"] = items
        self.video_selections_file.parent.mkdir(parents=True, exist_ok=True)
        self.video_selections_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        imported["items"] = items
        self._respond(200, "application/json", json.dumps(imported).encode("utf-8"))

    def _preview_train_lora(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body or b"{}")
            subject = _coerce_str(payload.get("subject"), field="subject", required=True)
            execute = _coerce_bool(payload.get("execute"))
            from lib.training import build_training_preview

            result = build_training_preview(
                subject=subject,
                input_images_url=_coerce_str(payload.get("input_images_url"), field="input_images_url"),
                execute=execute,
            )
        except ValueError as e:
            self._respond(400, "application/json", json.dumps({"error": str(e)}).encode("utf-8"))
            return
        except Exception as e:
            self._respond(500, "application/json", json.dumps({"error": "preview failed", "detail": _safe_error_text(e)}).encode("utf-8"))
            return
        self._respond(200, "application/json", json.dumps(result).encode("utf-8"))

    def _preview_video_generate(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body or b"{}")
            storyboard = _coerce_str(payload.get("storyboard"), field="storyboard", required=True)
            execute = _coerce_bool(payload.get("execute"))
            from lib.video_jobs import build_video_preview

            result = build_video_preview(
                storyboard_path=Path(storyboard),
                model=_coerce_str(payload.get("model"), field="model") or "wan-video/wan2.1-with-lora",
                execute=execute,
            )
        except ValueError as e:
            self._respond(400, "application/json", json.dumps({"error": str(e)}).encode("utf-8"))
            return
        except Exception as e:
            self._respond(500, "application/json", json.dumps({"error": "preview failed", "detail": _safe_error_text(e)}).encode("utf-8"))
            return
        self._respond(200, "application/json", json.dumps(result).encode("utf-8"))

    def _run_train_lora(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body or b"{}")
            subject = _coerce_str(payload.get("subject"), field="subject", required=True)
            from lib.training import plan_lora_training

            result = plan_lora_training(
                subject=subject,
                output_root=self.output_root,
                execute=_confirmed_execute(payload, label="training"),
                input_images_url=_coerce_str(payload.get("input_images_url"), field="input_images_url"),
            )
        except ValueError as e:
            self._respond(400, "application/json", json.dumps({"error": str(e)}).encode("utf-8"))
            return
        except Exception as e:
            self._respond(500, "application/json", json.dumps({"error": "training job failed", "detail": _safe_error_text(e)}).encode("utf-8"))
            return
        self._respond(200, "application/json", json.dumps(result).encode("utf-8"))

    def _run_video_generate(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body or b"{}")
            storyboard = _coerce_str(payload.get("storyboard"), field="storyboard", required=True)
            from lib.video_jobs import plan_video_generation

            result = plan_video_generation(
                storyboard_path=Path(storyboard),
                output_root=self.output_root,
                execute=_confirmed_execute(payload, label="video generation"),
                model=_coerce_str(payload.get("model"), field="model") or "wan-video/wan2.1-with-lora",
            )
        except ValueError as e:
            self._respond(400, "application/json", json.dumps({"error": str(e)}).encode("utf-8"))
            return
        except Exception as e:
            self._respond(500, "application/json", json.dumps({"error": "video generation job failed", "detail": _safe_error_text(e)}).encode("utf-8"))
            return
        self._respond(200, "application/json", json.dumps(result).encode("utf-8"))

    def _load_video_selections(self) -> dict:
        if self.video_selections_file.exists():
            try:
                data = json.loads(self.video_selections_file.read_text(encoding="utf-8"))
            except Exception:
                data = {}
        else:
            data = {}
        if not isinstance(data, dict):
            data = {}
        items = data.get("items")
        if not isinstance(items, dict):
            data["items"] = {}
        if not isinstance(data.get("notes"), dict):
            data["notes"] = {}
        data.setdefault("version", 1)
        return data

    def _media_registry_path(self) -> Path | None:
        return self.media_registry_file

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _respond_file(self, target: Path) -> None:
        size = target.stat().st_size
        mime = _guess_mime(target.suffix)
        range_header = self.headers.get("Range", "")
        if range_header.startswith("bytes="):
            start, end = self._parse_byte_range(range_header, size)
            if start is None:
                try:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                except (BrokenPipeError, ConnectionResetError):
                    pass
                return
            with target.open("rb") as f:
                f.seek(start)
                body = f.read(end - start + 1)
            try:
                self.send_response(206)
                self.send_header("Content-Type", mime)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                self.send_header("Accept-Ranges", "bytes")
                self._send_same_origin_cors()
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        try:
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(size))
            self.send_header("Accept-Ranges", "bytes")
            self._send_same_origin_cors()
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            with target.open("rb") as f:
                self.wfile.write(f.read())
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _parse_byte_range(self, header: str, size: int) -> tuple[int | None, int]:
        raw = header.removeprefix("bytes=").split(",", 1)[0].strip()
        start_raw, _, end_raw = raw.partition("-")
        try:
            if start_raw:
                start = int(start_raw)
                end = int(end_raw) if end_raw else size - 1
            else:
                suffix = int(end_raw)
                start = max(size - suffix, 0)
                end = size - 1
        except ValueError:
            return None, size - 1
        if start < 0 or start >= size:
            return None, size - 1
        end = min(max(end, start), size - 1)
        return start, end

    def _send_same_origin_cors(self) -> None:
        origin = self.headers.get("Origin")
        if not origin:
            return
        parsed = urlparse(origin)
        if parsed.scheme != "http" or parsed.netloc != self.headers.get("Host", ""):
            return
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Vary", "Origin")

    def _respond(self, status: int, content_type: str, body: bytes) -> None:
        try:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self._send_same_origin_cors()
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _respond_proxy(self, status: int, headers, body: bytes) -> None:
        try:
            self.send_response(status)
            for name in ("Content-Type", "Location", "Cache-Control", "ETag", "Last-Modified"):
                value = headers.get(name)
                if value:
                    self.send_header(name, value)
            if not headers.get("Content-Type"):
                self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _404(self) -> None:
        self._respond(404, "application/json", b'{"error":"not found"}')


def _is_frontend_route(path: str) -> bool:
    if path in ("", "/"):
        return True
    return any(path == route or path.startswith(f"{route}/") for route in FRONTEND_ROUTES if route != "/")


def _free_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _ensure_frontend_build() -> bool:
    if FRONTEND_ENTRY.exists():
        return True
    if not (FRONTEND_DIR / "package.json").exists():
        return False
    subprocess.run(
        ["npm", "--prefix", str(FRONTEND_DIR), "run", "build"],
        cwd=REPO_ROOT,
        check=True,
        timeout=120,
    )
    return FRONTEND_ENTRY.exists()


def _wait_for_frontend(origin: str, proc: subprocess.Popen, *, timeout_seconds: float = 15.0) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if proc.poll() is not None:
            return False
        try:
            with urlopen(f"{origin}/health", timeout=1) as resp:
                return resp.status < 500
        except Exception:
            time.sleep(0.15)
    return False


def _start_frontend_server() -> tuple[subprocess.Popen | None, str | None]:
    if os.environ.get("RAFIKI_DISABLE_FRONTEND") == "1":
        return None, None
    try:
        if not _ensure_frontend_build():
            return None, None
        port = _free_local_port()
        env = os.environ.copy()
        env.update({"HOST": "127.0.0.1", "PORT": str(port)})
        proc = subprocess.Popen(
            ["node", str(FRONTEND_ENTRY)],
            cwd=FRONTEND_DIR,
            env=env,
        )
        origin = f"http://127.0.0.1:{port}"
        if _wait_for_frontend(origin, proc):
            return proc, origin
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    except Exception as e:
        print(f"Frontend unavailable, falling back to legacy routes: {e}")
    return None, None


def _stop_frontend_server(proc: subprocess.Popen | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


def serve(
    output_root: Path,
    port: int = 7433,
    open_browser: bool = False,
    public: bool = False,
) -> None:
    """Start the Rafiki portal server and block until Ctrl-C."""
    from lib.renderers.library import load_extra_outputs
    from lib.media_roots import load_media_roots
    output_root = Path(output_root).resolve()
    ratings_file = output_root / "ratings.json"
    feedback_file = output_root / "feedback.json"
    evaluations_file = output_root / "evaluations.json"
    archive_metadata_file = output_root / "archive-metadata.json"
    billing_imports_file = REPO_ROOT / "data" / "billing-imports.json"
    video_selections_file = REPO_ROOT / "data" / "video-selections.json"
    extra_roots = {name: Path(p) for name, p in load_extra_outputs().items()}
    media_roots = load_media_roots()

    class Handler(_RafikiHandler):
        pass

    Handler.output_root = output_root
    Handler.ratings_file = ratings_file
    Handler.feedback_file = feedback_file
    Handler.evaluations_file = evaluations_file
    Handler.archive_metadata_file = archive_metadata_file
    Handler.billing_imports_file = billing_imports_file
    Handler.video_selections_file = video_selections_file
    Handler.media_registry_file = REPO_ROOT / "data" / "media-registry.json"
    Handler.extra_roots = extra_roots
    Handler.media_roots = media_roots
    frontend_proc, frontend_origin = _start_frontend_server()
    Handler.frontend_origin = frontend_origin

    auth_on = _basic_auth_credentials() is not None
    if public and not auth_on:
        _stop_frontend_server(frontend_proc)
        raise ValueError("--public requires both PORTAL_USERNAME and PORTAL_PASSWORD")

    bind_host = "0.0.0.0" if public else "127.0.0.1"
    httpd = ThreadingHTTPServer((bind_host, port), Handler)
    display_host = "localhost" if not public else "0.0.0.0"
    url = f"http://{display_host}:{port}/"
    print(f"Rafiki portal → {url}")
    print(f"Output root:    {output_root}")
    if extra_roots:
        for name, path in extra_roots.items():
            print(f"  + {name} → {path}")
    if media_roots:
        print("Media roots:")
        for name, root in media_roots.items():
            print(f"  + {name} → {root.path} ({root.importer})")

    if auth_on:
        print("Auth: Basic (PORTAL_USERNAME / PORTAL_PASSWORD)")
    if frontend_origin:
        print(f"Frontend:      {frontend_origin}")
    else:
        print("Frontend:      legacy fallback")

    print("Ctrl-C to stop.")

    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        _stop_frontend_server(frontend_proc)

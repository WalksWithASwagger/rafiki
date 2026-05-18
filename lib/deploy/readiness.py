"""Read-only deployment readiness checks for the Rafiki portal."""

from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


def _check(key: str, label: str, ok: bool, detail: str, *, required: bool = True) -> dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "ok": ok,
        "required": required,
        "detail": detail,
    }


def check_deploy_readiness(
    *,
    output_root: Path,
    project: str = "",
    viewer_dir: Path | None = None,
    public: bool = False,
) -> dict[str, Any]:
    """Return a secret-safe checklist for getting Rafiki online.

    This does not deploy or call provider APIs. It only checks local files,
    executable availability, and whether expected environment variables are set.
    """
    output_root = Path(output_root)
    checks: list[dict[str, Any]] = []

    if viewer_dir is not None:
        resolved_viewer = Path(viewer_dir)
    elif project:
        resolved_viewer = output_root / project
    else:
        resolved_viewer = None

    if resolved_viewer is None:
        checks.append(_check(
            "static_viewer",
            "Static viewer",
            False,
            "Choose a project or viewer directory before static deploy.",
            required=False,
        ))
    else:
        checks.append(_check(
            "static_viewer",
            "Static viewer",
            (resolved_viewer / "viewer.html").exists(),
            f"viewer.html at {resolved_viewer}",
        ))

    vercel_path = shutil.which("vercel")
    checks.append(_check(
        "vercel_cli",
        "Vercel CLI",
        vercel_path is not None,
        vercel_path or "Install with npm install -g vercel, then run vercel login.",
    ))

    portal_user = bool(os.environ.get("PORTAL_USERNAME"))
    portal_password = bool(os.environ.get("PORTAL_PASSWORD"))
    portal_auth_ok = portal_user and portal_password
    checks.append(_check(
        "portal_auth",
        "Portal auth",
        portal_auth_ok,
        "PORTAL_USERNAME and PORTAL_PASSWORD are set."
        if portal_auth_ok
        else "Set PORTAL_USERNAME and PORTAL_PASSWORD before binding --public.",
        required=public,
    ))

    gemini_ok = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    checks.append(_check(
        "gemini_key",
        "Gemini key",
        gemini_ok,
        "Gemini key is set." if gemini_ok else "Set GEMINI_API_KEY or GOOGLE_API_KEY for Gemini generation.",
        required=False,
    ))

    openai_ok = bool(os.environ.get("OPENAI_API_KEY"))
    checks.append(_check(
        "openai_key",
        "OpenAI key",
        openai_ok,
        "OPENAI_API_KEY is set." if openai_ok else "Set OPENAI_API_KEY for OpenAI generation.",
        required=False,
    ))

    required_checks = [check for check in checks if check["required"]]
    return {
        "ok": all(check["ok"] for check in required_checks),
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "public": public,
        "project": project,
        "viewer_dir": str(resolved_viewer) if resolved_viewer is not None else "",
        "checks": checks,
    }

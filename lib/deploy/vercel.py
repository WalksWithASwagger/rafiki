"""Deploy a Rafiki viewer directory to Vercel as a static site.

Uses the Vercel CLI as a subprocess. The CLI handles auth interactively the
first time and caches credentials at ~/.local/share/com.vercel.cli/. This
module never touches credentials directly.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "output"

_URL_RE = re.compile(r"https?://[^\s]+")


class VercelNotInstalledError(RuntimeError):
    """Raised when the Vercel CLI is not on PATH."""


class ViewerNotFoundError(FileNotFoundError):
    """Raised when no viewer.html exists at the resolved viewer directory."""


def _resolve_viewer_dir(project: str, viewer_dir: Path | None) -> Path:
    if viewer_dir is not None:
        return Path(viewer_dir)
    base = DEFAULT_OUTPUT_ROOT / project
    approved = base / "approved"
    if (approved / "viewer.html").exists():
        return approved
    return base


def _ensure_vercel_json(viewer_dir: Path) -> Path:
    """Write a minimal static-site vercel.json if one doesn't exist."""
    vercel_json = viewer_dir / "vercel.json"
    if not vercel_json.exists():
        vercel_json.write_text('{"version": 2}\n', encoding="utf-8")
    return vercel_json


def _parse_url(stdout: str) -> str | None:
    matches = _URL_RE.findall(stdout)
    return matches[-1].rstrip(".,") if matches else None


def deploy(
    project: str,
    *,
    viewer_dir: Path | None = None,
    prod: bool = False,
    dry_run: bool = False,
) -> str:
    """Deploy the project's viewer directory to Vercel.

    Args:
        project: Project name (used to locate output/<project>/ when viewer_dir is None).
        viewer_dir: Explicit path to the directory containing viewer.html.
        prod: If True, deploy to production (--prod). Otherwise a preview deploy.
        dry_run: If True, print the command and return an empty string without executing.

    Returns:
        The deployment URL parsed from the Vercel CLI output (empty if dry_run).

    Raises:
        VercelNotInstalledError: If `vercel` is not on PATH.
        ViewerNotFoundError: If <viewer_dir>/viewer.html does not exist.
    """
    resolved_dir = _resolve_viewer_dir(project, viewer_dir)

    if not (resolved_dir / "viewer.html").exists():
        raise ViewerNotFoundError(
            f"No viewer.html found at {resolved_dir}. "
            "Run `python generate.py view <project>` first or pass --viewer-dir."
        )

    if shutil.which("vercel") is None:
        raise VercelNotInstalledError(
            "The `vercel` CLI is not on PATH. Install it with:\n"
            "    npm install -g vercel\n"
            "Then run `vercel login` to authenticate."
        )

    _ensure_vercel_json(resolved_dir)

    cmd = ["vercel", "deploy", str(resolved_dir), "--yes"]
    if prod:
        cmd.append("--prod")

    if dry_run:
        print(f"[dry-run] {' '.join(cmd)}")
        return ""

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    url = _parse_url(combined)
    if not url:
        raise RuntimeError(
            f"Could not parse deployment URL from `vercel deploy` output:\n{combined}"
        )
    return url

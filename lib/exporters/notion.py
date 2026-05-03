"""Notion exporter — push approved Rafiki images to a Notion gallery database.

Source preference:
  1. ``output/<project>/approved/`` (curated via the rating system)
  2. Latest ``output/<project>/run-*/`` as fallback

Each image becomes a row in the configured Notion database with these
properties (the database must define them; create them once when you set up
the integration — see ``docs/NOTION-EXPORT.md``):

  * Name        — title
  * Caption     — rich_text
  * Week        — select   (optional; derived from ``week-NN`` in filename)
  * Source Run  — rich_text
  * Image       — files    (the uploaded PNG)

Idempotency: filenames already exported to ``database_id`` are tracked in
``output/<project>/.notion-exported.json`` and skipped on subsequent runs
unless ``force=True``.

The Notion file-upload flow is a 3-step process implemented inline because
the official ``notion-client`` SDK only thinly wraps the REST endpoints:
  1. POST /v1/file_uploads             → returns ``{id, upload_url}``
  2. PUT (multipart)                   → bytes go to ``upload_url``
  3. Reference ``{type:"file_upload", file_upload:{id}}`` in a page property
"""

from __future__ import annotations

import json
import mimetypes
import os
import re
import urllib.request
import uuid
from pathlib import Path
from typing import Any

NOTION_API_VERSION = "2022-06-28"
NOTION_FILE_UPLOAD_URL = "https://api.notion.com/v1/file_uploads"

_WEEK_RE = re.compile(r"week[-_]?(\d{1,3})", re.IGNORECASE)


class NotionExportError(RuntimeError):
    """Raised for any non-recoverable error during export."""


def _get_client(api_key: str) -> Any:
    """Lazy import keeps ``notion_client`` optional at module-import time
    (so tests can patch this function without the SDK installed)."""
    from notion_client import Client  # type: ignore[import-not-found]

    return Client(auth=api_key)


def _resolve_source_dir(project_root: Path) -> tuple[Path, str]:
    """Return (dir, label) — prefer ``approved/``, fall back to latest run-*."""
    approved = project_root / "approved"
    if approved.is_dir() and any(approved.glob("*.png")):
        return approved, "approved"

    runs = sorted(
        (p for p in project_root.glob("run-*") if p.is_dir()),
        key=lambda p: p.name,
    )
    if not runs:
        raise NotionExportError(
            f"No images to export: {project_root} has no approved/ dir "
            f"and no run-*/ subdirectories."
        )
    return runs[-1], runs[-1].name


def _load_index(source_dir: Path) -> dict[str, dict]:
    """Build {filename: {caption, week, ...}} from index.json or run.json.

    ``approved/index.json`` (PR #41 shape) is preferred when present.
    Otherwise ``run.json`` from a run-* dir is used to recover names/prompts.
    Missing metadata is tolerated — the filename alone is enough to export.
    """
    by_file: dict[str, dict] = {}

    index_path = source_dir / "index.json"
    if index_path.exists():
        try:
            data = json.loads(index_path.read_text(encoding="utf-8"))
            entries = data.get("images", data) if isinstance(data, dict) else data
            if isinstance(entries, list):
                for e in entries:
                    fn = e.get("file") or e.get("filename") or e.get("name")
                    if fn:
                        by_file[Path(fn).name] = e
        except (json.JSONDecodeError, OSError):
            pass

    run_json = source_dir / "run.json"
    if run_json.exists():
        try:
            data = json.loads(run_json.read_text(encoding="utf-8"))
            for img in data.get("images", []):
                fn = img.get("file")
                if fn and fn not in by_file:
                    by_file[fn] = img
        except (json.JSONDecodeError, OSError):
            pass

    return by_file


def _derive_week(filename: str, meta: dict) -> str | None:
    if meta.get("week"):
        return str(meta["week"])
    m = _WEEK_RE.search(filename)
    if m:
        return f"Week {int(m.group(1))}"
    return None


def _load_export_log(project_root: Path) -> dict:
    p = project_root / ".notion-exported.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_export_log(project_root: Path, log: dict) -> None:
    p = project_root / ".notion-exported.json"
    p.write_text(json.dumps(log, indent=2, sort_keys=True), encoding="utf-8")


def _upload_file(api_key: str, file_path: Path) -> str:
    """Run the Notion 3-step file upload, return the ``file_upload`` id.

    Uses stdlib ``urllib`` to avoid pulling in ``requests`` as a hard dep.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": NOTION_API_VERSION,
    }

    # Step 1 — request an upload slot
    create_req = urllib.request.Request(
        NOTION_FILE_UPLOAD_URL,
        data=b"{}",
        method="POST",
        headers={**headers, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(create_req) as resp:
        slot = json.loads(resp.read().decode("utf-8"))

    upload_url = slot["upload_url"]
    file_upload_id = slot["id"]

    # Step 2 — multipart PUT of the bytes
    boundary = f"----rafiki{uuid.uuid4().hex}"
    mime = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode("utf-8")
    body += file_path.read_bytes()
    body += f"\r\n--{boundary}--\r\n".encode("utf-8")

    put_req = urllib.request.Request(
        upload_url,
        data=body,
        method="POST",  # Notion's signed URL accepts POST for multipart
        headers={
            **headers,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
    )
    with urllib.request.urlopen(put_req) as resp:
        resp.read()

    return file_upload_id


def _page_properties(name: str, caption: str, week: str | None,
                     source_run: str, file_upload_id: str,
                     filename: str) -> dict:
    props: dict[str, Any] = {
        "Name": {"title": [{"text": {"content": name[:2000]}}]},
        "Caption": {"rich_text": [{"text": {"content": caption[:2000]}}]},
        "Source Run": {"rich_text": [{"text": {"content": source_run}}]},
        "Image": {
            "files": [
                {
                    "name": filename,
                    "type": "file_upload",
                    "file_upload": {"id": file_upload_id},
                }
            ]
        },
    }
    if week:
        props["Week"] = {"select": {"name": week}}
    return props


def export(
    project: str,
    *,
    database_id: str | None = None,
    output_root: Path | None = None,
    dry_run: bool = False,
    force: bool = False,
    api_key: str | None = None,
) -> dict:
    """Push approved images for ``project`` to a Notion database.

    Args:
        project: Project name under ``output_root`` (or absolute path).
        database_id: Target Notion database id (falls back to env
            ``NOTION_DATABASE_ID``).
        output_root: Override the default ``./output`` root (mostly for tests).
        dry_run: Skip all API calls; print what would happen.
        force: Re-export images already recorded in the local export log.
        api_key: Override the ``NOTION_API_KEY`` env var (mostly for tests).

    Returns:
        ``{"exported": int, "skipped": int, "errors": [str, ...],
           "source": str, "dry_run": bool}``
    """
    api_key = api_key or os.environ.get("NOTION_API_KEY")
    database_id = database_id or os.environ.get("NOTION_DATABASE_ID")

    if not dry_run and not api_key:
        raise NotionExportError(
            "NOTION_API_KEY is not set. Create an internal integration at "
            "https://www.notion.so/my-integrations, copy the secret, and add "
            "NOTION_API_KEY=secret_... to your .env file. "
            "See docs/NOTION-EXPORT.md for the full setup."
        )
    if not dry_run and not database_id:
        raise NotionExportError(
            "No database_id provided. Pass --database <id> or set "
            "NOTION_DATABASE_ID in your .env. "
            "See docs/NOTION-EXPORT.md for how to find a database id."
        )

    project_path = Path(project)
    if not project_path.is_absolute():
        root = output_root or Path("output")
        project_path = root / project
    project_path = project_path.resolve()

    if not project_path.is_dir():
        raise NotionExportError(f"Project not found: {project_path}")

    source_dir, source_label = _resolve_source_dir(project_path)
    images_meta = _load_index(source_dir)
    image_files = sorted(source_dir.glob("*.png"))

    if not image_files:
        return {"exported": 0, "skipped": 0, "errors": [],
                "source": source_label, "dry_run": dry_run}

    log = _load_export_log(project_path)
    db_log = log.setdefault(database_id or "_dry_run_", {})

    exported = 0
    skipped = 0
    errors: list[str] = []
    client = None if dry_run else _get_client(api_key or "")

    for img_path in image_files:
        filename = img_path.name
        if not force and filename in db_log:
            skipped += 1
            print(f"  skip   {filename} (already in {database_id})")
            continue

        meta = images_meta.get(filename, {})
        name = meta.get("name") or img_path.stem
        caption = meta.get("caption") or meta.get("prompt") or ""
        week = _derive_week(filename, meta)

        if dry_run:
            print(f"  would upload {filename}  →  database {database_id or '<unset>'}")
            print(f"    name={name!r}  week={week!r}  caption={caption[:80]!r}")
            exported += 1
            continue

        try:
            file_upload_id = _upload_file(api_key or "", img_path)
            props = _page_properties(
                name=name,
                caption=caption,
                week=week,
                source_run=source_label,
                file_upload_id=file_upload_id,
                filename=filename,
            )
            client.pages.create(
                parent={"database_id": database_id},
                properties=props,
            )
            db_log[filename] = {
                "source_run": source_label,
                "file_upload_id": file_upload_id,
            }
            exported += 1
            print(f"  export {filename}  →  Notion ({source_label})")
        except Exception as e:  # surface, continue with remaining images
            err = f"{filename}: {e}"
            errors.append(err)
            print(f"  ERROR  {err}")

    if not dry_run and exported:
        _save_export_log(project_path, log)

    return {
        "exported": exported,
        "skipped": skipped,
        "errors": errors,
        "source": source_label,
        "dry_run": dry_run,
    }

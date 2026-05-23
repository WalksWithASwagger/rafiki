"""Optional local thumbnail cache for large Rafiki archives."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

from PIL import Image

CACHE_DIR_NAME = ".rafiki-cache"
THUMBNAIL_DIR = "thumbnails"
THUMBNAIL_VERSION = "v1"
DEFAULT_WIDTH = 480
DEFAULT_QUALITY = 82


def thumbnail_cache_root(output_root: Path, width: int = DEFAULT_WIDTH) -> Path:
    return Path(output_root) / CACHE_DIR_NAME / THUMBNAIL_DIR / THUMBNAIL_VERSION / f"w{width}"


def thumbnail_cache_stats(output_root: Path) -> dict[str, Any]:
    root = Path(output_root) / CACHE_DIR_NAME / THUMBNAIL_DIR
    files = [path for path in root.rglob("*") if path.is_file()] if root.exists() else []
    return {
        "exists": root.exists(),
        "path": str(root),
        "files": len(files),
        "disk_bytes": sum(_safe_size(path) for path in files),
    }


def build_thumbnail_cache(
    output_root: Path,
    records: list[dict[str, Any]],
    *,
    html_dir: Path | None = None,
    width: int = DEFAULT_WIDTH,
    quality: int = DEFAULT_QUALITY,
    force: bool = False,
) -> dict[str, Any]:
    output_root = Path(output_root)
    html_dir = Path(html_dir) if html_dir is not None else output_root
    cache_root = thumbnail_cache_root(output_root, width)
    summary = {
        "path": str(cache_root),
        "width": width,
        "quality": quality,
        "checked": 0,
        "created": 0,
        "reused": 0,
        "failed": 0,
        "bytes": 0,
        "errors": [],
    }

    for record in records:
        source = _source_path(record, output_root)
        if source is None or not source.exists() or not source.is_file():
            continue
        summary["checked"] += 1
        target = _target_path(cache_root, source, str(record.get("file") or source.name))
        try:
            if force or not target.exists():
                _write_thumbnail(source, target, width=width, quality=quality)
                summary["created"] += 1
            else:
                summary["reused"] += 1
            summary["bytes"] += _safe_size(target)
            record["thumbnail_file"] = _relative_link(target, html_dir)
        except Exception as e:
            summary["failed"] += 1
            if len(summary["errors"]) < 10:
                summary["errors"].append({"file": str(source), "error": str(e)})

    return summary


def _source_path(record: dict[str, Any], output_root: Path) -> Path | None:
    explicit = record.get("source_path")
    if explicit:
        return Path(str(explicit))

    raw = str(record.get("file") or "").strip()
    if not raw or raw.startswith(("http://", "https://", "data:", "file:")):
        return None
    path = Path(raw)
    return path if path.is_absolute() else output_root / path


def _target_path(cache_root: Path, source: Path, cache_key: str) -> Path:
    stat = source.stat()
    digest_input = f"{cache_key}|{source.resolve()}|{stat.st_size}|{stat.st_mtime_ns}"
    digest = hashlib.sha256(digest_input.encode("utf-8")).hexdigest()[:16]
    suffix = ".png" if source.suffix.lower() in {".png", ".gif"} else ".jpg"
    stem = _safe_stem(Path(cache_key).stem or source.stem)
    return cache_root / f"{stem}-{digest}{suffix}"


def _write_thumbnail(source: Path, target: Path, *, width: int, quality: int) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image.thumbnail((width, width * 4), Image.Resampling.LANCZOS)
        if target.suffix == ".jpg":
            image = image.convert("RGB")
            image.save(target, "JPEG", quality=quality, optimize=True)
        else:
            image.save(target, "PNG", optimize=True)


def _relative_link(path: Path, html_dir: Path) -> str:
    return Path(os.path.relpath(path.resolve(), html_dir.resolve())).as_posix()


def _safe_stem(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in value).strip("-_")
    return cleaned[:80] or "thumbnail"


def _safe_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0

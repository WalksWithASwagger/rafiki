"""Canva asset handoff — copy images and write a metadata CSV ready for bulk upload.

Source preference (per project):
  1. ``output/<project>/approved/``  — curated set, if present
  2. latest ``output/<project>/run-*/`` (by run id sort)

Output:
  ``<output_dir>/images/``  — PNG copies
  ``<output_dir>/assets.csv`` — quoted CSV, one row per image
  ``<output_dir>.zip`` — zipped bundle (when ``zip=True``)
"""

from __future__ import annotations

import csv
import json
import shutil
import zipfile
from pathlib import Path
from typing import Iterable

CSV_COLUMNS = [
    "filename",
    "title",
    "caption",
    "week",
    "social_post",
    "aspect_ratio",
    "source_run",
    "prompt",
]

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "output"
RAP_DATA_PATH = REPO_ROOT / "prompts" / "bcai" / "rap-viewer-data.json"

# Named export presets — operators pass --preset instead of tuning flags.
# Each value is a dict of keyword arguments forwarded to export().
PRESETS: dict[str, dict] = {
    # Compact zip for quick sharing (e.g. email, Slack, Canva upload).
    "small-review": {"zip": True},
    # Unzipped directory with full asset structure preserved for archiving.
    "full-archive": {"zip": False},
}


def apply_preset(preset_name: str) -> dict:
    """Return export() kwargs for a named preset.

    Raises ValueError for unknown preset names.
    """
    if preset_name not in PRESETS:
        known = ", ".join(sorted(PRESETS))
        raise ValueError(f"Unknown preset {preset_name!r}. Known presets: {known}")
    return dict(PRESETS[preset_name])


def _slug_to_title(slug: str) -> str:
    """Strip a leading ``NN-`` index and turn the rest into Title Case."""
    stem = Path(slug).stem
    parts = stem.split("-", 1)
    if len(parts) == 2 and parts[0].isdigit():
        stem = parts[1]
    return stem.replace("-", " ").replace("_", " ").title()


def _load_rap_metadata() -> dict[str, dict]:
    """Load optional RAP caption/social metadata, keyed by image slug.

    Returns an empty dict if the file is absent or malformed — callers
    should treat this as "no enrichment available".
    """
    if not RAP_DATA_PATH.exists():
        return {}
    try:
        data = json.loads(RAP_DATA_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    by_slug: dict[str, dict] = {}
    for entry in data if isinstance(data, list) else data.get("images", []):
        slug = entry.get("slug") or Path(entry.get("file", "")).stem
        if slug:
            by_slug[slug] = entry
    return by_slug


def _resolve_source(project_dir: Path) -> Path:
    """Return the directory to copy images from."""
    approved = project_dir / "approved"
    if approved.is_dir() and any(approved.glob("*.png")):
        return approved
    runs = sorted(p for p in project_dir.glob("run-*") if p.is_dir())
    if not runs:
        raise FileNotFoundError(
            f"No 'approved/' or 'run-*/' directories found in {project_dir}"
        )
    return runs[-1]


def _load_run_meta(source: Path) -> dict:
    """Load ``run.json`` from a run directory; return ``{}`` for ``approved/``."""
    run_json = source / "run.json"
    if not run_json.exists():
        return {}
    try:
        return json.loads(run_json.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _build_rows(
    images: Iterable[Path],
    run_meta: dict,
    rap_meta: dict[str, dict],
    source_label: str,
) -> list[dict]:
    """Build CSV row dicts from on-disk images plus any available metadata."""
    by_file: dict[str, dict] = {
        img["file"]: img for img in run_meta.get("images", []) if "file" in img
    }
    aspect = run_meta.get("aspect_ratio", "")

    rows: list[dict] = []
    for img_path in sorted(images):
        filename = img_path.name
        slug = img_path.stem
        run_entry = by_file.get(filename, {})
        rap_entry = rap_meta.get(slug, {})

        title = (
            rap_entry.get("title")
            or run_entry.get("name")
            or _slug_to_title(slug)
        )
        caption = rap_entry.get("caption", "") or ""
        week = rap_entry.get("week", "")
        social_post = rap_entry.get("social") or rap_entry.get("social_post") or ""
        prompt = run_entry.get("prompt", "") or rap_entry.get("prompt", "")

        rows.append({
            "filename": filename,
            "title": title,
            "caption": caption,
            "week": week,
            "social_post": social_post,
            "aspect_ratio": aspect,
            "source_run": source_label,
            "prompt": prompt,
        })
    return rows


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _zip_dir(src_dir: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(src_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(src_dir.parent))


def export(
    project: str,
    output_dir: Path | None = None,
    zip: bool = True,
    output_root: Path | None = None,
) -> Path:
    """Export approved/latest-run images + ``assets.csv`` for Canva.

    Args:
        project: Project directory name under ``output/`` (e.g. ``rap-all-weeks``).
        output_dir: Where to write the bundle. Defaults to
            ``output/<project>/canva-export/``.
        zip: When True, also produce a sibling ``.zip`` and return its path.
            When False, return the export directory path.
        output_root: Root output directory (defaults to the repo's ``output/``).

    Returns:
        Path to the zip file (default) or the export directory.
    """
    root = output_root or DEFAULT_OUTPUT_ROOT
    project_dir = root / project
    if not project_dir.is_dir():
        raise FileNotFoundError(f"Project not found: {project_dir}")

    source = _resolve_source(project_dir)
    run_meta = _load_run_meta(source)
    rap_meta = _load_rap_metadata()

    images = list(source.glob("*.png"))
    if not images:
        raise FileNotFoundError(f"No PNG images found in {source}")

    export_dir = output_dir or (project_dir / "canva-export")
    images_dir = export_dir / "images"
    if export_dir.exists():
        shutil.rmtree(export_dir)
    images_dir.mkdir(parents=True)

    for img in images:
        shutil.copy2(img, images_dir / img.name)

    rows = _build_rows(images, run_meta, rap_meta, source.name)
    _write_csv(export_dir / "assets.csv", rows)

    if not zip:
        return export_dir

    zip_path = export_dir.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    _zip_dir(export_dir, zip_path)
    return zip_path

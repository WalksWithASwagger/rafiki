"""Cross-project image asset registry — index, search, export.

Walks every project under output/ (and any roots in config/extra-outputs.json),
preferring an approved/ subdir, and falls back to the latest run-* dir. Pulls
metadata from run.json (canonical) and merges optional title/caption/tags from
a sibling viewer-data.json when present.

The on-disk registry is a local cache (gitignored) — regenerate with
`generate.py registry index` after a batch run or curation.
"""

from __future__ import annotations

import csv
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "output"
EXTRA_OUTPUTS_CONFIG = REPO_ROOT / "config" / "extra-outputs.json"
REGISTRY_JSON = DATA_DIR / "asset-registry.json"
REGISTRY_CSV = DATA_DIR / "asset-registry.csv"

CSV_COLUMNS = [
    "id",
    "project",
    "title",
    "caption",
    "tags",
    "style",
    "model",
    "aspect_ratio",
    "indexed_at",
    "path",
]


@dataclass
class AssetEntry:
    id: str
    project: str
    title: str
    caption: str
    tags: list[str] = field(default_factory=list)
    style: str = ""
    model: str = ""
    aspect_ratio: str = ""
    indexed_at: str = ""
    path: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def to_csv_row(self) -> dict[str, str]:
        d = self.to_dict()
        d["tags"] = ",".join(self.tags)
        return d


def _load_extra_roots() -> dict[str, Path]:
    if not EXTRA_OUTPUTS_CONFIG.exists():
        return {}
    try:
        raw = json.loads(EXTRA_OUTPUTS_CONFIG.read_text(encoding="utf-8"))
        return {name: Path(p) for name, p in raw.items()}
    except Exception as e:
        logger.warning("Failed to read %s: %s", EXTRA_OUTPUTS_CONFIG, e)
        return {}


def _latest_run_dir(project_dir: Path) -> Path | None:
    runs = sorted(project_dir.glob("run-*"))
    return runs[-1] if runs else None


def _load_viewer_data(directory: Path) -> dict[str, dict]:
    """Optional sibling viewer-data.json — keyed by image filename."""
    vd = directory / "viewer-data.json"
    if not vd.exists():
        return {}
    try:
        data = json.loads(vd.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning("Malformed viewer-data.json at %s: %s", vd, e)
        return {}

    if isinstance(data, dict) and "images" in data:
        items = data["images"]
    elif isinstance(data, list):
        items = data
    else:
        return {}

    out: dict[str, dict] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        key = item.get("file") or item.get("filename") or item.get("name")
        if key:
            out[str(key)] = item
    return out


def _load_run_meta(directory: Path) -> tuple[dict, dict[str, dict]]:
    """Return (run-level meta, per-file image meta) from run.json (or empty)."""
    rj = directory / "run.json"
    if not rj.exists():
        return {}, {}
    try:
        data = json.loads(rj.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning("Malformed run.json at %s: %s", rj, e)
        return {}, {}

    per_file: dict[str, dict] = {}
    for img in data.get("images", []) or []:
        if isinstance(img, dict) and img.get("file"):
            per_file[img["file"]] = img
    return data, per_file


def _slugify(value: str) -> str:
    out = []
    for ch in value.lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in "-_ ":
            out.append("-")
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def _entries_from_dir(
    project: str,
    directory: Path,
    indexed_at: str,
) -> list[AssetEntry]:
    """Build AssetEntry list from PNGs in directory + adjacent metadata."""
    if not directory.exists():
        return []

    run_meta, per_file = _load_run_meta(directory)
    viewer_meta = _load_viewer_data(directory)

    style = run_meta.get("style", "") or ""
    model = run_meta.get("model", "") or ""
    aspect_ratio = run_meta.get("aspect_ratio", "") or ""

    entries: list[AssetEntry] = []
    for png in sorted(directory.glob("*.png")):
        fname = png.name
        img_meta = per_file.get(fname, {})
        view = viewer_meta.get(fname, {})

        title = (
            view.get("title")
            or img_meta.get("name")
            or png.stem.replace("-", " ").replace("_", " ").title()
        )
        caption = view.get("caption") or img_meta.get("prompt") or ""

        tags: list[str] = []
        for src in (view.get("tags"), img_meta.get("tags")):
            if isinstance(src, list):
                tags.extend(str(t) for t in src)
        if aspect_ratio and aspect_ratio not in tags:
            tags.append(aspect_ratio)

        try:
            rel_path = png.resolve().relative_to(REPO_ROOT).as_posix()
        except ValueError:
            rel_path = png.resolve().as_posix()

        entries.append(
            AssetEntry(
                id=f"{project}-{png.stem}",
                project=project,
                title=str(title),
                caption=str(caption),
                tags=tags,
                style=str(style),
                model=str(model),
                aspect_ratio=str(aspect_ratio),
                indexed_at=indexed_at,
                path=rel_path,
            )
        )
    return entries


def _project_roots(output_root: Path | None = None) -> dict[str, Path]:
    """Map project name -> project dir, merging output/ and extra-outputs.json."""
    output_root = Path(output_root) if output_root else DEFAULT_OUTPUT_ROOT
    roots: dict[str, Path] = {}

    if output_root.exists():
        for child in sorted(output_root.iterdir()):
            if child.is_dir():
                roots[child.name] = child

    for name, path in _load_extra_roots().items():
        if path.exists():
            roots[name] = path  # extras win — canonical source
        else:
            logger.warning("extra-outputs project %s missing on disk: %s", name, path)

    return roots


def index(output_root: Path | None = None) -> list[AssetEntry]:
    """Walk projects, build registry entries, persist to data/asset-registry.json."""
    indexed_at = datetime.now().isoformat(timespec="seconds")
    roots = _project_roots(output_root)

    all_entries: list[AssetEntry] = []
    for project, project_dir in roots.items():
        try:
            approved = project_dir / "approved"
            if approved.is_dir():
                entries = _entries_from_dir(project, approved, indexed_at)
            else:
                latest = _latest_run_dir(project_dir)
                if latest is None:
                    logger.info("No approved/ or run-* in %s — skipping", project_dir)
                    continue
                entries = _entries_from_dir(project, latest, indexed_at)
            all_entries.extend(entries)
        except Exception as e:
            logger.warning("Skipping project %s due to error: %s", project, e)
            continue

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REGISTRY_JSON.write_text(
        json.dumps([e.to_dict() for e in all_entries], indent=2) + "\n",
        encoding="utf-8",
    )
    return all_entries


def _load_registry() -> list[AssetEntry]:
    if not REGISTRY_JSON.exists():
        return []
    try:
        raw = json.loads(REGISTRY_JSON.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning("Failed to read %s: %s", REGISTRY_JSON, e)
        return []
    return [AssetEntry(**item) for item in raw if isinstance(item, dict)]


def search(query: str) -> list[AssetEntry]:
    """Case-insensitive substring search across title, caption, tags."""
    needle = (query or "").lower().strip()
    if not needle:
        return []
    out: list[AssetEntry] = []
    for entry in _load_registry():
        haystack = " ".join([
            entry.title.lower(),
            entry.caption.lower(),
            " ".join(t.lower() for t in entry.tags),
        ])
        if needle in haystack:
            out.append(entry)
    return out


def export(format: str = "csv") -> Path:
    """Export the persisted registry as CSV or JSON. Returns the file path."""
    fmt = format.lower()
    entries = _load_registry()
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if fmt == "csv":
        with REGISTRY_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for entry in entries:
                writer.writerow(entry.to_csv_row())
        return REGISTRY_CSV

    if fmt == "json":
        REGISTRY_JSON.write_text(
            json.dumps([e.to_dict() for e in entries], indent=2) + "\n",
            encoding="utf-8",
        )
        return REGISTRY_JSON

    raise ValueError(f"Unsupported export format: {format!r} (use 'csv' or 'json')")

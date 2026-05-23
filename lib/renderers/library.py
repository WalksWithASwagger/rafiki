"""Master library viewer — all Rafiki images across all projects in one page."""

from __future__ import annotations

import json
import re
import webbrowser
from datetime import datetime
from pathlib import Path

from lib.archive_metadata import archive_metadata_path, load_archive_metadata, metadata_for_key
from lib.curriculum import build_curriculum_atlas
from lib.evaluations import evaluations_path, load_evaluations
from lib import registry
from lib.extra_outputs import load_extra_outputs
from lib.lineage import annotate_lineage_comparisons
from lib.renderers.library_atlas import _atlas_panel_html
from lib.renderers.library_styles import _library_extra_css
from lib.styles import get_default_style, load_styles
from lib.renderers.viewer import _shared_css, _lightbox_html, _lightbox_js


def _scan_root(root: Path, project_name: str, virtual_prefix: str, output_root: Path | None = None) -> list[dict]:
    """Yield image records from all run-*/run.json files under root."""
    records: list[dict] = []
    output_root = Path(output_root) if output_root else root.parent
    for rjp in sorted(root.glob("run-*/run.json")):
        try:
            data = json.loads(rjp.read_text(encoding="utf-8"))
        except Exception:
            continue
        run_id = rjp.parent.name
        model = data.get("model", "unknown")
        timestamp = data.get("timestamp", "")
        aspect_ratio = data.get("aspect_ratio", "16:9")
        style = data.get("style", "")
        detail = _run_detail(project_name, run_id, rjp.parent, output_root, data)
        for img in data.get("images", []):
            img_path = rjp.parent / img["file"]
            records.append({
                "project": project_name,
                "run_id": run_id,
                "run_key": detail["key"],
                "model": model,
                "timestamp": timestamp,
                "aspect_ratio": aspect_ratio,
                "style": style,
                "name": img.get("name", ""),
                "prompt": img.get("prompt", ""),
                # virtual path used as img src — routed by server or via symlink
                "file": f"{virtual_prefix}/{run_id}/{img['file']}",
                "source": "run",
                "approval_status": "unapproved",
                "run_detail": detail,
                "ok": img_path.exists(),
            })
    return records


def _entry_file_src(entry: registry.AssetEntry, output_root: Path) -> str:
    path = Path(entry.path)
    resolved = path if path.is_absolute() else registry.REPO_ROOT / path

    try:
        return resolved.resolve().relative_to(output_root.resolve()).as_posix()
    except ValueError:
        pass

    if not path.is_absolute() and path.parts and path.parts[0] == output_root.name:
        return Path(*path.parts[1:]).as_posix()

    if entry.source == "approved":
        return f"{entry.project}/approved/{path.name}"
    if entry.source_run:
        return f"{entry.project}/{entry.source_run}/{path.name}"
    return path.as_posix()


def _library_href(path: Path, output_root: Path) -> str:
    try:
        return path.resolve().relative_to(output_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_uri()


def _run_detail(project: str, run_id: str, run_dir: Path, output_root: Path, manifest: dict) -> dict:
    invocation = manifest.get("invocation", {})
    if not isinstance(invocation, dict):
        invocation = {}

    images = manifest.get("images", [])
    image_count = len(images) if isinstance(images, list) else 0
    return {
        "key": f"{project}/{run_id}" if run_id else project,
        "project": project,
        "run_id": run_id,
        "model": manifest.get("model", ""),
        "style": manifest.get("style", ""),
        "aspect_ratio": manifest.get("aspect_ratio", ""),
        "timestamp": manifest.get("timestamp", ""),
        "started_at": manifest.get("started_at", ""),
        "finished_at": manifest.get("finished_at", ""),
        "state": manifest.get("state", ""),
        "provider": manifest.get("provider", ""),
        "prompt_file": manifest.get("prompt_file", ""),
        "prompt_source": manifest.get("prompt_source", ""),
        "invocation_surface": invocation.get("surface", ""),
        "image_count": image_count,
        "run_json": _library_href(run_dir / "run.json", output_root),
        "run_viewer": _library_href(run_dir / "viewer.html", output_root),
        "project_viewer": _library_href(run_dir.parent / "viewer.html", output_root),
        "manifest": manifest,
    }


def _run_detail_from_dir(project: str, run_dir: Path, output_root: Path) -> dict:
    run_id = run_dir.name if run_dir.name.startswith("run-") else ""
    run_meta, _ = registry._load_run_meta(run_dir)
    if not run_meta:
        return {}
    return _run_detail(project, run_id, run_dir, output_root, run_meta)


def _run_detail_for_entry(entry: registry.AssetEntry, file_src: str, output_root: Path) -> dict:
    if not entry.source_run:
        return {}

    path = Path(entry.path)
    resolved = path if path.is_absolute() else registry.REPO_ROOT / path
    run_dir = resolved.parent if resolved.parent.name == entry.source_run else output_root / entry.project / entry.source_run

    detail = _run_detail_from_dir(entry.project, run_dir, output_root)
    if detail:
        return detail

    if file_src:
        src_parts = Path(file_src).parts
        if len(src_parts) >= 2:
            return _run_detail_from_dir(entry.project, output_root.joinpath(*src_parts[:-1]), output_root)
    return {}


def _filename_basename(record: dict) -> str:
    return Path(str(record.get("file") or "")).name


def _normalized_filename_stem(filename: str) -> str:
    stem = Path(filename).stem.casefold()
    stem = re.sub(r"^\d+[\s._-]*", "", stem)
    stem = re.sub(r"[\s._-]+", "-", stem)
    stem = re.sub(r"[^a-z0-9-]", "", stem)
    return re.sub(r"-+", "-", stem).strip("-")


def _filename_warning_related(record: dict) -> dict:
    return {
        "basename": _filename_basename(record),
        "file": record.get("file", ""),
        "run_id": record.get("run_id", ""),
        "title": record.get("title") or record.get("name") or "",
    }


def _annotate_filename_warnings(records: list[dict]) -> None:
    exact_groups: dict[tuple[str, str], list[dict]] = {}
    similar_groups: dict[tuple[str, str], list[dict]] = {}

    for record in records:
        basename = _filename_basename(record)
        if not basename:
            continue
        project = str(record.get("project") or "")
        exact_groups.setdefault((project, basename.casefold()), []).append(record)
        normalized = _normalized_filename_stem(basename)
        if len(normalized) >= 3:
            similar_groups.setdefault((project, normalized), []).append(record)

    for group in exact_groups.values():
        if len(group) < 2:
            continue
        basenames = sorted({_filename_basename(record) for record in group})
        for record in group:
            related = [_filename_warning_related(other) for other in group if other is not record]
            if not related:
                continue
            basename = _filename_basename(record)
            record["filename_warning"] = {
                "level": "exact",
                "label": "Duplicate filename",
                "basename": basename,
                "message": (
                    f"Another image in this project also uses {basename}. "
                    "Check the related runs before approving or cleaning."
                ),
                "related_count": len(related),
                "related": related[:8],
                "group_basenames": basenames,
            }

    for (_, normalized), group in similar_groups.items():
        distinct_basenames = sorted({_filename_basename(record) for record in group})
        if len(distinct_basenames) < 2:
            continue
        for record in group:
            if record.get("filename_warning"):
                continue
            related = [_filename_warning_related(other) for other in group if other is not record]
            if not related:
                continue
            record["filename_warning"] = {
                "level": "similar",
                "label": "Similar filename",
                "basename": _filename_basename(record),
                "normalized_stem": normalized,
                "message": (
                    f"Other files in this project share the normalized stem {normalized}. "
                    "Check whether this is a rerun or intentional variation."
                ),
                "related_count": len(related),
                "related": related[:8],
                "group_basenames": distinct_basenames,
            }


def _dedupe_text(values: list[object]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _apply_archive_metadata(records: list[dict], output_root: Path) -> None:
    metadata = load_archive_metadata(archive_metadata_path(output_root))
    for record in records:
        base_tags = record.get("tags") if isinstance(record.get("tags"), list) else []
        record.setdefault("base_title", record.get("title") or record.get("name") or "")
        record.setdefault("base_name", record.get("name") or "")
        record.setdefault("base_tags", _dedupe_text(base_tags))
        key = str(record.get("file") or "")
        entry = metadata_for_key(metadata, key)
        if not entry:
            record.setdefault("metadata_states", [])
            continue

        title = str(entry.get("title") or "").strip()
        if title:
            record["title"] = title
            record["name"] = title

        entry_tags = entry.get("tags") if isinstance(entry.get("tags"), list) else []
        record["tags"] = _dedupe_text([*base_tags, *entry_tags])

        states = entry.get("states") if isinstance(entry.get("states"), list) else []
        record["metadata_states"] = _dedupe_text(states)
        superseded_by = str(entry.get("superseded_by") or "").strip()
        if superseded_by:
            record["superseded_by"] = superseded_by
        record["metadata"] = entry


def _records_from_registry(output_root: Path) -> list[dict]:
    records: list[dict] = []
    for entry in registry.collect(output_root, scope="all-runs"):
        file_src = _entry_file_src(entry, output_root)
        title = entry.title or entry.caption or Path(entry.path).stem
        source_prompt = entry.source_prompt or entry.caption
        run_detail = _run_detail_for_entry(entry, file_src, output_root)
        records.append({
            "project": entry.project,
            "run_id": entry.source_run,
            "run_key": run_detail.get("key", f"{entry.project}/{entry.source_run}" if entry.source_run else entry.project),
            "model": entry.model or "unknown",
            "timestamp": entry.indexed_at,
            "aspect_ratio": entry.aspect_ratio or "16:9",
            "style": entry.style,
            "name": title,
            "title": title,
            "caption": entry.caption,
            "tags": entry.tags,
            "approval_status": entry.approval_status,
            "source": entry.source,
            "source_prompt": source_prompt,
            "prompt": source_prompt,
            "file": file_src,
            "run_detail": run_detail,
            "ok": Path(entry.path).exists() if Path(entry.path).is_absolute() else (registry.REPO_ROOT / entry.path).exists(),
        })
    return records


def generate_library_viewer(output_root: Path, open_browser: bool = False) -> Path:
    """Scan output_root + any extra-outputs and build output_root/library.html."""
    output_root = Path(output_root)
    extra_roots = load_extra_outputs()

    records = _records_from_registry(output_root)

    if not records:
        # Legacy fallback for malformed or output-only projects that cannot be
        # represented by the registry metadata loader.
        seen: set[str] = set()

        for project_name, extra_root in extra_roots.items():
            if not extra_root.exists():
                continue
            for rec in _scan_root(extra_root, project_name, project_name, output_root):
                seen.add(rec["file"])
                records.append(rec)

        for proj_dir in sorted(output_root.iterdir()):
            if not proj_dir.is_dir():
                continue
            for rec in _scan_root(proj_dir, proj_dir.name, proj_dir.name, output_root):
                if rec["file"] not in seen:
                    seen.add(rec["file"])
                    records.append(rec)

    _apply_archive_metadata(records, output_root)
    records.sort(key=lambda r: r["timestamp"], reverse=True)

    html = _render_library(records, output_root=output_root)
    out_path = output_root / "library.html"
    out_path.write_text(html, encoding="utf-8")

    if open_browser:
        webbrowser.open(out_path.as_uri())

    return out_path


def _portal_model_options() -> list[str]:
    return [
        "gemini-2.5-flash-image",
        "gemini-3-pro-image-preview",
        "gpt-image-2",
        "gpt-image-1",
        "dall-e-3",
        "dall-e-2",
    ]


def _studio_panel_html(style_names: list[str], default_style: str, model_options: list[str]) -> str:
    model_opts = "".join(
        f'<option value="{model}"{" selected" if model == "gemini-2.5-flash-image" else ""}>{model}</option>'
        for model in model_options
    )
    style_opts = "".join(f'<option value="{style}"></option>' for style in style_names)
    return f"""
<section class="studio-panel" id="studio-panel">
  <div class="studio-heading">
    <div>
      <h2>Prompt Studio</h2>
      <p>Generate directly from the portal. Every run lands in <code>output/&lt;project&gt;/run-*/</code> and updates the same review workflow.</p>
    </div>
    <div class="studio-note">Single prompt or Markdown batch. Local-first, same machine, same keys.</div>
  </div>
  <form id="studio-form" class="studio-form" onsubmit="submitStudio(event)">
    <div class="studio-grid">
      <label class="studio-field">
        <span>Mode</span>
        <select id="studio-mode" name="mode" onchange="syncStudioMode()">
          <option value="single" selected>Single prompt</option>
          <option value="batch">Prompt file batch</option>
        </select>
      </label>
      <label class="studio-field">
        <span>Project</span>
        <input id="studio-project" name="project" type="text" value="studio" placeholder="studio">
      </label>
      <label class="studio-field studio-single">
        <span>Image Name</span>
        <input id="studio-name" name="name" type="text" placeholder="Optional label for this image">
      </label>
      <label class="studio-field">
        <span>Model</span>
        <select id="studio-model" name="model">{model_opts}</select>
      </label>
      <label class="studio-field">
        <span>Style</span>
        <input id="studio-style" name="style" type="text" list="studio-style-options" placeholder="blank = default ({default_style}); use none to disable">
      </label>
      <label class="studio-field">
        <span>Aspect Ratio</span>
        <select id="studio-ar" name="aspect_ratio">
          <option value="16:9" selected>16:9</option>
          <option value="1:1">1:1</option>
          <option value="9:16">9:16</option>
          <option value="linkedin">linkedin</option>
          <option value="instagram">instagram</option>
          <option value="story">story</option>
          <option value="square">square</option>
        </select>
      </label>
      <label class="studio-field">
        <span>Quality</span>
        <select id="studio-quality" name="quality">
          <option value="high" selected>high</option>
          <option value="medium">medium</option>
          <option value="low">low</option>
        </select>
      </label>
      <label class="studio-field">
        <span>Resolution</span>
        <select id="studio-resolution" name="resolution">
          <option value="1K" selected>1K</option>
          <option value="2K">2K</option>
          <option value="4K">4K</option>
        </select>
      </label>
      <label class="studio-field studio-batch studio-hidden">
        <span>Workers</span>
        <input id="studio-workers" name="workers" type="number" min="1" max="8" value="2">
      </label>
      <label class="studio-field studio-wide">
        <span>Reference Image</span>
        <input id="studio-reference" name="reference_image" type="text" placeholder="/absolute/path/to/reference.png">
      </label>
      <label class="studio-field studio-single studio-wide">
        <span>Prompt</span>
        <textarea id="studio-prompt" name="prompt" rows="5" placeholder="Describe the image you want Rafiki to generate"></textarea>
      </label>
      <label class="studio-field studio-batch studio-wide studio-hidden">
        <span>Prompt File</span>
        <input id="studio-prompt-file" name="prompt_file" type="text" placeholder="/absolute/path/to/image-prompts.md">
      </label>
    </div>
    <div class="studio-actions">
      <label class="studio-check">
        <input id="studio-dry-run" name="dry_run" type="checkbox">
        <span>Dry run</span>
      </label>
      <button id="studio-submit" class="studio-submit" type="submit">Run</button>
    </div>
    <div class="studio-status" id="studio-status" aria-live="polite"></div>
  </form>
  <datalist id="studio-style-options">
    <option value="none"></option>
    {style_opts}
  </datalist>
</section>
"""


def _actions_panel_html(projects: list[str]) -> str:
    project_opts = "".join(f'<option value="{project}">{project}</option>' for project in projects)
    return f"""
<section class="portal-actions-panel" id="portal-actions-panel">
  <div class="portal-actions-heading">
    <h2>Curation & Export</h2>
    <span id="actions-discovery" class="portal-actions-note">Loading actions...</span>
  </div>
  <form id="portal-action-form" class="portal-actions-form" onsubmit="submitPortalAction(event)">
    <label>
      <span>Project</span>
      <select id="action-project" name="project">{project_opts}</select>
    </label>
    <label>
      <span>Action</span>
      <select id="action-name" name="action" onchange="syncPortalAction()">
        <option value="approve-starred">Approve Starred</option>
        <option value="canva-export">Canva Export</option>
        <option value="notion-export">Notion Dry Run</option>
        <option value="registry-export">Registry Export</option>
        <option value="static-deploy">Static Deploy Helper</option>
      </select>
    </label>
    <label class="portal-action-field action-run">
      <span>Run</span>
      <input id="action-run" type="text" placeholder="latest">
    </label>
    <label class="portal-action-field action-format">
      <span>Format</span>
      <select id="action-format">
        <option value="csv">CSV</option>
        <option value="json">JSON</option>
      </select>
    </label>
    <label class="portal-action-field action-database">
      <span>Database</span>
      <input id="action-database" type="text" placeholder="Notion database id">
    </label>
    <label class="portal-action-field action-viewer">
      <span>Viewer Dir</span>
      <input id="action-viewer" type="text" placeholder="auto">
    </label>
    <div class="portal-action-toggles">
      <label><input id="action-dry-run" type="checkbox" checked onchange="syncPortalAction()"> Dry run</label>
      <label><input id="action-confirm" type="checkbox"> Confirm</label>
      <label class="action-nozip"><input id="action-nozip" type="checkbox"> No zip</label>
      <label class="action-prod"><input id="action-prod" type="checkbox"> Prod</label>
      <label class="action-force"><input id="action-force" type="checkbox"> Force</label>
    </div>
    <button id="action-submit" class="portal-action-submit" type="submit">Run Action</button>
  </form>
  <div class="portal-action-status" id="portal-action-status" aria-live="polite"></div>
</section>
"""


def _ops_panel_html() -> str:
    return """
<section class="ops-panel" id="ops-panel">
  <div class="ops-heading">
    <h2>Spend & Review Ops</h2>
    <span id="usage-status" class="ops-note">Loading usage...</span>
  </div>
  <div class="ops-grid">
    <div class="ops-tile">
      <span>Estimated Spend</span>
      <strong id="usage-known-cost">$0.00</strong>
      <small id="usage-cost-note">pricing profile</small>
    </div>
    <div class="ops-tile">
      <span>Provider Billing</span>
      <strong id="usage-billing-amount">$0.00</strong>
      <small id="usage-billing-note">0 imported rows</small>
    </div>
    <div class="ops-tile">
      <span>Archive Images</span>
      <strong id="usage-image-count">0</strong>
      <small id="usage-image-note">0 unpriced</small>
    </div>
    <div class="ops-tile">
      <span>Runs</span>
      <strong id="usage-run-count">0</strong>
      <small id="usage-project-count">0 projects</small>
    </div>
    <div class="ops-tile">
      <span>Run Time</span>
      <strong id="usage-duration">0m</strong>
      <small id="usage-failed-count">0 failed</small>
    </div>
  </div>
  <div class="ops-columns">
    <div>
      <h3>Model Mix</h3>
      <div class="ops-list" id="usage-models"></div>
    </div>
    <div>
      <h3>Recent Runs</h3>
      <div class="ops-list" id="usage-recent-runs"></div>
    </div>
  </div>
  <form class="ops-billing-form" id="billing-import-form" onsubmit="saveBillingEntry(event)">
    <h3>Add Billing Entry</h3>
    <label>
      <span>Provider</span>
      <input id="billing-provider" type="text" placeholder="OpenAI">
    </label>
    <label>
      <span>Amount</span>
      <input id="billing-amount" type="number" step="0.0001" min="0" placeholder="0.00">
    </label>
    <label>
      <span>Model</span>
      <input id="billing-model" type="text" placeholder="gpt-image-2">
    </label>
    <label>
      <span>Note</span>
      <input id="billing-note" type="text" placeholder="Invoice or export note">
    </label>
    <button type="submit">Add</button>
    <span id="billing-import-status" class="ops-note" aria-live="polite"></span>
  </form>
  <div class="ops-readiness">
    <div>
      <h3>Online Readiness</h3>
      <p id="deploy-readiness-status" class="ops-note">Checking deploy readiness...</p>
    </div>
    <div class="ops-list" id="deploy-readiness-checks"></div>
  </div>
</section>
"""


def _render_library(records: list[dict], output_root: Path | None = None) -> str:
    _annotate_filename_warnings(records)
    annotate_lineage_comparisons(records)

    run_details: dict[str, dict] = {}
    library_records: list[dict] = []
    for record in records:
        detail = record.get("run_detail")
        if isinstance(detail, dict) and detail.get("key"):
            run_details.setdefault(str(detail["key"]), detail)
        item = dict(record)
        item.pop("run_detail", None)
        library_records.append(item)

    records = library_records
    evaluations = (
        load_evaluations(evaluations_path(output_root))
        if output_root is not None
        else {"items": {}}
    )
    curriculum_atlas = build_curriculum_atlas(records, evaluations=evaluations)
    library_json = json.dumps(records, ensure_ascii=False)
    run_details_json = json.dumps(run_details, ensure_ascii=False)
    atlas_json = json.dumps(curriculum_atlas, ensure_ascii=False)
    ok_count = sum(1 for r in records if r["ok"])
    projects = sorted({r["project"] for r in records})
    models = sorted({r["model"] for r in records if r["model"] not in ("unknown", "")})
    aspect_ratios = sorted({r["aspect_ratio"] for r in records if r.get("aspect_ratio")})
    styles = sorted({r["style"] for r in records if r.get("style") and r["style"] not in ("none", "")})
    sources = sorted({r["source"] for r in records if r.get("source")})
    runs = sorted({r["run_id"] for r in records if r.get("run_id")}, reverse=True)
    approval_states = ["approved", "unapproved"]
    all_style_names = sorted(load_styles().keys())
    default_style = get_default_style()
    model_options = _portal_model_options()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    project_chips = "".join(
        f'<button class="filter-btn chip-proj" data-proj="{p}" '
        f"onclick=\"filterLib('proj','{p}')\">{p.replace('-', ' ').title()}</button>"
        for p in projects
    )
    model_chips = "".join(
        f'<button class="filter-btn chip-model" data-model="{m}" '
        f"onclick=\"filterLib('model','{m}')\">{m}</button>"
        for m in models
    )
    ar_chips = "".join(
        f'<button class="filter-btn chip-ar" data-ar="{a}" '
        f"onclick=\"filterLib('ar','{a}')\">{a}</button>"
        for a in aspect_ratios
    )
    style_chips = "".join(
        f'<button class="filter-btn chip-style" data-style="{s}" '
        f"onclick=\"filterLib('style','{s}')\">{s}</button>"
        for s in styles
    )
    source_opts = "".join(f'<option value="{source}">{source}</option>' for source in sources)
    run_opts = "".join(f'<option value="{run}">{run}</option>' for run in runs)
    approval_opts = "".join(f'<option value="{state}">{state}</option>' for state in approval_states)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rafiki Library</title>
{_shared_css()}
{_library_extra_css()}
</head>
<body>
<header>
  <h1>Rafiki Library</h1>
  <div class="meta">
    <span class="pill">{ok_count} image{'s' if ok_count != 1 else ''}</span>
    <span class="pill teal-pill">{len(projects)} project{'s' if len(projects) != 1 else ''}</span>
    <span>Built {now}</span>
  </div>
</header>

<nav class="portal-mode-nav" aria-label="Portal modes">
  <button type="button" class="portal-mode-btn active" data-mode-target="review" onclick="setPortalMode('review')">Review</button>
  <button type="button" class="portal-mode-btn" data-mode-target="generate" onclick="setPortalMode('generate')">Generate</button>
  <button type="button" class="portal-mode-btn" data-mode-target="curate" onclick="setPortalMode('curate')">Curate</button>
  <button type="button" class="portal-mode-btn" data-mode-target="spend" onclick="setPortalMode('spend')">Spend</button>
  <button type="button" class="portal-mode-btn" data-mode-target="teach" onclick="setPortalMode('teach')">Teach</button>
</nav>

<main class="portal-modes">
  <section class="portal-mode-panel review-mode is-active" id="portal-mode-review" data-portal-mode="review">
    <div class="mode-heading review-heading">
      <div>
        <h2>Review</h2>
        <p>Image-first archive review with filters, ratings, feedback, and run detail.</p>
      </div>
      <span class="mode-note">{ok_count} visible archive image{'s' if ok_count != 1 else ''}</span>
    </div>
    <div class="filter-bar" id="filter-bar">
      <button class="filter-btn active" id="fb-all"        onclick="setRatingFilter('all')">All <span id="fc-all"></span></button>
      <button class="filter-btn"        id="fb-star"       onclick="setRatingFilter('star')">&#9733; Starred <span id="fc-star"></span></button>
      <button class="filter-btn"        id="fb-reject"     onclick="setRatingFilter('reject')">&#x2715; Rejected <span id="fc-reject"></span></button>
      <button class="filter-btn"        id="fb-unreviewed" onclick="setRatingFilter('unreviewed')">Unreviewed <span id="fc-unreviewed"></span></button>
      <button class="filter-btn"        id="fb-review-queue" onclick="setRatingFilter('review-queue')">Review Queue <span id="fc-review-queue"></span></button>
      <input id="search" type="text" placeholder="Search prompts…" autocomplete="off"
             oninput="_searchQuery=this.value.toLowerCase().trim();clearAtlasAssetFilter(false);applyFilters()">
      <label class="filter-select-label">
        Source
        <select id="source-filter" onchange="setLibrarySelectFilter('source', this.value)">
          <option value="">All sources</option>
          {source_opts}
        </select>
      </label>
      <label class="filter-select-label">
        Run
        <select id="run-filter" onchange="setLibrarySelectFilter('run', this.value)">
          <option value="">All runs</option>
          {run_opts}
        </select>
      </label>
      <label class="filter-select-label">
        Approval
        <select id="approval-filter" onchange="setLibrarySelectFilter('approval', this.value)">
          <option value="">All approval</option>
          {approval_opts}
        </select>
      </label>
      <span class="chip-sep">|</span>
      {project_chips}
      <span class="chip-sep">|</span>
      {model_chips}
      <span class="chip-sep">|</span>
      {ar_chips}
      <span class="chip-sep">|</span>
      {style_chips}
      <label class="grid-size-label">
        <select class="sort-select" onchange="applySort(this.value)">
          <option value="default">⇅ Order</option>
          <option value="newest">Newest</option>
          <option value="oldest">Oldest</option>
          <option value="project">Project</option>
          <option value="model">Model</option>
          <option value="name">A → Z</option>
        </select>
        Grid <input type="range" min="160" max="560" value="280" id="grid-sizer" oninput="resizeGrid(this.value)">
      </label>
      <span class="keyboard-hint">Keys: ←/→ move · S star · X reject · 0 clear · I details</span>
    </div>
    <div class="atlas-filter-banner" id="atlas-filter-banner" hidden>
      <span id="atlas-filter-label"></span>
      <button type="button" onclick="clearAtlasAssetFilter()">Clear atlas filter</button>
    </div>
    <div class="grid" id="grid"></div>
  </section>

  <section class="portal-mode-panel" id="portal-mode-generate" data-portal-mode="generate" hidden>
    {_studio_panel_html(all_style_names, default_style, model_options)}
  </section>

  <section class="portal-mode-panel" id="portal-mode-curate" data-portal-mode="curate" hidden>
    {_actions_panel_html(projects)}
  </section>

  <section class="portal-mode-panel" id="portal-mode-spend" data-portal-mode="spend" hidden>
    {_ops_panel_html()}
  </section>

  <section class="portal-mode-panel" id="portal-mode-teach" data-portal-mode="teach" hidden>
    {_atlas_panel_html(curriculum_atlas)}
  </section>
</main>

<aside class="run-detail-panel" id="run-detail-panel" aria-live="polite" aria-hidden="true">
  <div class="run-detail-head">
    <div>
      <h2>Run Detail</h2>
      <p id="run-detail-subtitle">Select a card to inspect its source run.</p>
    </div>
    <button class="run-detail-close" type="button" onclick="closeRunDetail()" title="Close detail panel">&#x2715;</button>
  </div>
  <div class="run-detail-body">
    <div class="run-detail-warning" id="run-detail-warning"></div>
    <div class="run-detail-links" id="run-detail-links"></div>
    <div class="run-lineage-comparison" id="run-lineage-comparison"></div>
    <div class="run-decision-summary" id="run-decision-summary"></div>
    <div class="run-detail-curriculum" id="run-detail-curriculum"></div>
    <dl class="run-detail-fields" id="run-detail-fields"></dl>
    <div class="run-detail-metadata" id="run-detail-metadata">
      <h3>Card Metadata</h3>
      <label>
        <span>Title Override</span>
        <input id="metadata-title" type="text">
      </label>
      <label>
        <span>Tags</span>
        <input id="metadata-tags" type="text" placeholder="campaign, keeper, web">
      </label>
      <div class="metadata-state-grid" id="metadata-state-grid">
        <label><input type="checkbox" value="canva"> Canva</label>
        <label><input type="checkbox" value="notion"> Notion</label>
        <label><input type="checkbox" value="deployed"> Deployed</label>
        <label><input type="checkbox" value="published"> Published</label>
        <label><input type="checkbox" value="superseded"> Superseded</label>
      </div>
      <label>
        <span>Superseded By</span>
        <input id="metadata-superseded-by" type="text" placeholder="project/run/file">
      </label>
      <div class="metadata-actions">
        <button type="button" onclick="saveMetadataForDetail(event)">Save Metadata</button>
      </div>
      <div class="metadata-status" id="metadata-status-message" aria-live="polite"></div>
    </div>
    <div class="run-detail-feedback" id="run-detail-feedback">
      <h3>Feedback</h3>
      <label>
        <span>Status</span>
        <select id="feedback-status">
          <option value="">None</option>
          <option value="needs-change">Needs Change</option>
          <option value="keep">Keep</option>
          <option value="maybe">Maybe</option>
          <option value="blocked">Blocked</option>
          <option value="done">Done</option>
        </select>
      </label>
      <label>
        <span>Notes</span>
        <textarea id="feedback-note" rows="3"></textarea>
      </label>
      <label>
        <span>Change Request</span>
        <textarea id="feedback-change-request" rows="4"></textarea>
      </label>
      <div class="feedback-actions">
        <button type="button" onclick="saveFeedbackForDetail(event)">Save</button>
        <button type="button" onclick="stageRevisionFromDetail(event, false)">Stage Rerun</button>
        <button type="button" onclick="stageRevisionFromDetail(event, true)">Dry Run</button>
      </div>
      <div class="feedback-status" id="feedback-status-message" aria-live="polite"></div>
    </div>
    <div class="run-detail-evaluation" id="run-detail-evaluation">
      <h3>Evaluation</h3>
      <label>
        <span>Decision</span>
        <select id="evaluation-decision">
          <option value="">None</option>
          <option value="approve">Approve</option>
          <option value="revise">Revise</option>
          <option value="reject">Reject</option>
          <option value="reference">Reference</option>
        </select>
      </label>
      <label>
        <span>Score</span>
        <select id="evaluation-score">
          <option value="">No score</option>
          <option value="5">5 - Excellent</option>
          <option value="4">4 - Strong</option>
          <option value="3">3 - Useful</option>
          <option value="2">2 - Weak</option>
          <option value="1">1 - Not usable</option>
        </select>
      </label>
      <label>
        <span>Use Case</span>
        <input id="evaluation-use-case" type="text" placeholder="homepage hero, module opener, social">
      </label>
      <label>
        <span>Rationale</span>
        <textarea id="evaluation-rationale" rows="3"></textarea>
      </label>
      <label>
        <span>Next Step</span>
        <textarea id="evaluation-next-step" rows="3"></textarea>
      </label>
      <div class="evaluation-actions">
        <button type="button" onclick="saveEvaluationForDetail(event)">Save Evaluation</button>
      </div>
      <div class="evaluation-status" id="evaluation-status-message" aria-live="polite"></div>
    </div>
    <pre class="run-detail-json" id="run-detail-json"></pre>
  </div>
</aside>

{_lightbox_html()}

<script>
const LIBRARY = {library_json};
const ITEMS = LIBRARY;
const RUN_DETAILS = {run_details_json};
const CURRICULUM_ATLAS = {atlas_json};
const RATINGS_KEY = 'rafiki:ratings';
const FEEDBACK_KEY = 'rafiki:feedback';
const EVALUATIONS_KEY = 'rafiki:evaluations';
const METADATA_KEY = 'rafiki:archiveMetadata';
const SERVER_MODE = location.protocol !== 'file:';
let FEEDBACK = {{}};
let EVALUATIONS = {{}};
let ARCHIVE_METADATA = {{}};
let _ratingFilter = 'all';
let _projFilter = null;
let _modelFilter = null;
let _arFilter = null;
let _styleFilter = null;
let _sourceFilter = null;
let _runFilter = null;
let _approvalFilter = null;
let _searchQuery = '';
let _atlasAssetFilter = null;
let _activeCard = null;
let _detailItem = null;

function _loadRatings() {{
  try {{ return JSON.parse(localStorage.getItem(RATINGS_KEY) || '{{}}'); }} catch(e) {{ return {{}}; }}
}}
function _saveRatings(r) {{ localStorage.setItem(RATINGS_KEY, JSON.stringify(r)); }}
function _loadLocalFeedback() {{
  try {{ return JSON.parse(localStorage.getItem(FEEDBACK_KEY) || '{{}}'); }} catch(e) {{ return {{}}; }}
}}
function _saveLocalFeedback(items) {{ localStorage.setItem(FEEDBACK_KEY, JSON.stringify(items || {{}})); }}
function _loadLocalEvaluations() {{
  try {{ return JSON.parse(localStorage.getItem(EVALUATIONS_KEY) || '{{}}'); }} catch(e) {{ return {{}}; }}
}}
function _saveLocalEvaluations(items) {{ localStorage.setItem(EVALUATIONS_KEY, JSON.stringify(items || {{}})); }}
function _loadLocalMetadata() {{
  try {{ return JSON.parse(localStorage.getItem(METADATA_KEY) || '{{}}'); }} catch(e) {{ return {{}}; }}
}}
function _saveLocalMetadata(items) {{ localStorage.setItem(METADATA_KEY, JSON.stringify(items || {{}})); }}
function studioEscapeHtml(value) {{
  return String(value || '').replace(/[&<>"]/g, ch => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[ch]));
}}
function formatUsd(amount) {{
  const value = Number(amount || 0);
  return '$' + value.toFixed(value >= 10 ? 2 : 4).replace(/0+$/, '').replace(/\\.$/, '.00');
}}
function formatDuration(seconds) {{
  const total = Math.max(0, Number(seconds || 0));
  if (total >= 3600) return (total / 3600).toFixed(1) + 'h';
  if (total >= 60) return Math.round(total / 60) + 'm';
  return Math.round(total) + 's';
}}
function resolveAssetSrc(path) {{
  const raw = String(path || '');
  if (!raw || /^(https?:|data:|file:|\\/)/.test(raw)) return raw;
  return SERVER_MODE ? '/output/' + raw.replace(/^\\/+/, '') : raw;
}}
function setPortalMode(mode) {{
  const targetMode = ['review', 'generate', 'curate', 'spend', 'teach'].includes(mode) ? mode : 'review';
  document.querySelectorAll('.portal-mode-panel').forEach(panel => {{
    const active = panel.dataset.portalMode === targetMode;
    panel.hidden = !active;
    panel.classList.toggle('is-active', active);
  }});
  document.querySelectorAll('.portal-mode-btn').forEach(button => {{
    const active = button.dataset.modeTarget === targetMode;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', active ? 'true' : 'false');
  }});
  try {{ localStorage.setItem('rafiki:portalMode', targetMode); }} catch (err) {{}}
  if (targetMode === 'review') syncActiveCardAfterFilter();
}}
function initPortalMode() {{
  let requested = '';
  try {{
    const hashMode = (location.hash || '').replace(/^#/, '');
    const mobileDefault = window.matchMedia && window.matchMedia('(max-width: 700px)').matches;
    const savedMode = mobileDefault ? '' : localStorage.getItem('rafiki:portalMode') || '';
    requested = hashMode || savedMode;
  }} catch (err) {{}}
  setPortalMode(requested || 'review');
}}
function atlasProgramById(programId) {{
  return (CURRICULUM_ATLAS.programs || []).find(program => program.id === programId) || null;
}}
function atlasModuleById(programId, moduleId) {{
  const program = atlasProgramById(programId);
  if (!program) return null;
  return (program.modules || []).find(module => module.id === moduleId) || null;
}}
function updateAtlasFilterBanner(label, count) {{
  const banner = document.getElementById('atlas-filter-banner');
  const text = document.getElementById('atlas-filter-label');
  if (!banner || !text) return;
  if (!label) {{
    banner.hidden = true;
    text.textContent = '';
    return;
  }}
  banner.hidden = false;
  text.textContent = label + ' · ' + count + ' asset' + (count === 1 ? '' : 's');
}}
function clearAtlasAssetFilter(shouldApply = true) {{
  _atlasAssetFilter = null;
  updateAtlasFilterBanner('', 0);
  if (shouldApply) applyFilters();
}}
function focusAtlasAssets(indices, label) {{
  const assetIndices = Array.isArray(indices) ? indices.map(String) : [];
  _atlasAssetFilter = new Set(assetIndices);
  const search = document.getElementById('search');
  if (search) search.value = '';
  _searchQuery = '';
  updateAtlasFilterBanner(label || 'Curriculum Atlas', assetIndices.length);
  setPortalMode('review');
  applyFilters();
  document.getElementById('grid')?.scrollIntoView({{block: 'start'}});
}}
function focusAtlasModule(programId, moduleId) {{
  const program = atlasProgramById(programId);
  const module = atlasModuleById(programId, moduleId);
  if (!program || !module) return;
  focusAtlasAssets(module.asset_indices || [], program.title + ' / ' + module.title);
}}
function focusAtlasUnmapped() {{
  focusAtlasAssets(CURRICULUM_ATLAS.unmapped_asset_indices || [], 'Unmapped curriculum queue');
}}
function curriculumMatchesForIndex(idx) {{
  const needle = String(idx);
  const matches = [];
  (CURRICULUM_ATLAS.programs || []).forEach(program => {{
    (program.modules || []).forEach(module => {{
      const indices = (module.asset_indices || []).map(value => String(value));
      if (indices.includes(needle)) matches.push({{program, module}});
    }});
  }});
  return matches;
}}
function curriculumMatchesForItem(item) {{
  const idx = LIBRARY.indexOf(item);
  return idx >= 0 ? curriculumMatchesForIndex(idx) : [];
}}
function evaluationSummaryForIndices(indices) {{
  const counts = {{approve: 0, revise: 0, reject: 0, reference: 0}};
  const scores = [];
  let evaluated = 0;
  const assetIndices = Array.isArray(indices) ? indices : [];
  assetIndices.forEach(idx => {{
    const item = LIBRARY[parseInt(idx, 10)];
    const entry = evaluationForItem(item) || {{}};
    const decision = String(entry.decision || '').toLowerCase();
    const hasEvaluation = Boolean(decision || entry.score || entry.use_case || entry.rationale || entry.next_step);
    if (!hasEvaluation) return;
    evaluated += 1;
    if (counts[decision] !== undefined) counts[decision] += 1;
    const score = Number(entry.score);
    if (Number.isFinite(score) && score >= 1 && score <= 5) scores.push(score);
  }});
  const avg = scores.length
    ? (scores.reduce((total, value) => total + value, 0) / scores.length).toFixed(1)
    : '';
  return {{
    assetCount: assetIndices.length,
    evaluated,
    unreviewed: Math.max(0, assetIndices.length - evaluated),
    counts,
    average: avg,
  }};
}}
function evaluationSummaryText(summary) {{
  const bits = [
    summary.evaluated + '/' + summary.assetCount + ' evaluated',
    'approve ' + summary.counts.approve,
    'revise ' + summary.counts.revise,
    'reject ' + summary.counts.reject,
    'reference ' + summary.counts.reference,
  ];
  if (summary.average) bits.push('avg ' + summary.average);
  if (summary.unreviewed) bits.push(summary.unreviewed + ' unreviewed');
  return bits.join(' · ');
}}
function renderAtlasEvaluationSummaries() {{
  document.querySelectorAll('.atlas-evaluation-summary').forEach(box => {{
    const module = atlasModuleById(box.dataset.programId || '', box.dataset.moduleId || '');
    if (!module) return;
    box.textContent = evaluationSummaryText(evaluationSummaryForIndices(module.asset_indices || []));
  }});
}}
function appendCurriculumList(parent, title, values, className) {{
  const clean = cleanList(values || []);
  if (!clean.length) return;
  const block = document.createElement('div');
  block.className = 'curriculum-context-list ' + className;
  const heading = document.createElement('strong');
  heading.textContent = title;
  const list = document.createElement('ul');
  clean.slice(0, 4).forEach(value => {{
    const item = document.createElement('li');
    item.textContent = value;
    list.appendChild(item);
  }});
  block.appendChild(heading);
  block.appendChild(list);
  parent.appendChild(block);
}}
function renderCurriculumContext(item) {{
  const box = document.getElementById('run-detail-curriculum');
  if (!box) return;
  box.innerHTML = '';
  const title = document.createElement('h3');
  title.textContent = 'Curriculum Fit';
  box.appendChild(title);
  const matches = curriculumMatchesForItem(item);
  if (!matches.length) {{
    const empty = document.createElement('p');
    empty.className = 'curriculum-context-empty';
    empty.textContent = 'No Atlas module match yet.';
    box.appendChild(empty);
    return;
  }}
  matches.slice(0, 3).forEach(match => {{
    const program = match.program || {{}};
    const module = match.module || {{}};
    const article = document.createElement('article');
    article.className = 'curriculum-context-card';
    const heading = document.createElement('h4');
    heading.textContent = [program.title, module.title].filter(Boolean).join(' / ');
    article.appendChild(heading);
    if (module.objective) {{
      const objective = document.createElement('p');
      objective.textContent = module.objective;
      article.appendChild(objective);
    }}
    const why = document.createElement('div');
    why.className = 'curriculum-context-why';
    const query = cleanList(module.asset_query || []);
    why.textContent = query.length ? 'Matches: ' + query.join(', ') : 'Matched through program context.';
    article.appendChild(why);
    appendCurriculumList(article, 'Criteria', (module.critique_criteria || []).map(item => item.label || item.prompt), 'curriculum-context-criteria');
    appendCurriculumList(article, 'Discuss', module.discussion_prompts || [], 'curriculum-context-prompts');
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = 'Open module';
    button.addEventListener('click', () => focusAtlasModule(program.id || '', module.id || ''));
    article.appendChild(button);
    box.appendChild(article);
  }});
}}
function detailForItem(item) {{
  if (!item) return null;
  const key = item.run_key || [item.project, item.run_id].filter(Boolean).join('/');
  return RUN_DETAILS[key] || null;
}}
function setDetailText(id, value) {{
  const el = document.getElementById(id);
  if (el) el.textContent = value || '';
}}
function appendDetailLink(target, label, href) {{
  if (!href) return;
  const link = document.createElement('a');
  link.href = href;
  link.textContent = label;
  link.target = '_blank';
  link.rel = 'noopener';
  target.appendChild(link);
}}
function feedbackKeyForItem(item) {{
  return item?.file || '';
}}
function evaluationKeyForItem(item) {{
  return item?.file || '';
}}
function metadataKeyForItem(item) {{
  return item?.file || '';
}}
function metadataForItem(item) {{
  const key = metadataKeyForItem(item);
  return key ? (ARCHIVE_METADATA[key] || item.metadata || null) : null;
}}
function cleanList(value) {{
  if (Array.isArray(value)) return value.map(v => String(v || '').trim()).filter(Boolean);
  return String(value || '').split(',').map(v => v.trim()).filter(Boolean);
}}
function metadataStatesForItem(item) {{
  const entry = metadataForItem(item) || {{}};
  return cleanList(item?.metadata_states || entry.states || []);
}}
function metadataStateLabel(item) {{
  const states = metadataStatesForItem(item);
  return states.map(state => state.replace(/-/g, ' ')).join(', ');
}}
function warningTextForItem(item) {{
  const warning = item?.filename_warning;
  if (!warning) return '';
  return [
    warning.label,
    warning.level,
    warning.basename,
    warning.normalized_stem,
    ...(warning.group_basenames || []),
  ].filter(Boolean).join(' ');
}}
function searchTextForItem(item) {{
  return (
    (item.title || item.name || '') + ' ' +
    (item.caption || '') + ' ' +
    (item.source_prompt || item.prompt || '') + ' ' +
    cleanList(item.tags || []).join(' ') + ' ' +
    (item.project || '') + ' ' +
    (item.run_id || '') + ' ' +
    (item.source || '') + ' ' +
    (item.approval_status || '') + ' ' +
    metadataStateLabel(item) + ' ' +
    (item.superseded_by || '') + ' ' +
    evaluationSearchText(item) + ' ' +
    warningTextForItem(item)
  ).toLowerCase();
}}
function feedbackForItem(item) {{
  const key = feedbackKeyForItem(item);
  return key ? (FEEDBACK[key] || null) : null;
}}
function evaluationForItem(item) {{
  const key = evaluationKeyForItem(item);
  return key ? (EVALUATIONS[key] || null) : null;
}}
function evaluationDecisionLabel(entry) {{
  if (!entry) return '';
  return String(entry.decision || '').replace(/-/g, ' ');
}}
function evaluationSearchText(item) {{
  const entry = evaluationForItem(item) || {{}};
  return [
    entry.decision,
    entry.score ? 'score ' + entry.score : '',
    entry.use_case,
    entry.rationale,
    entry.next_step,
  ].filter(Boolean).join(' ');
}}
function hasEvaluationDecision(item) {{
  const entry = evaluationForItem(item) || {{}};
  return Boolean(entry.decision || entry.score || entry.use_case || entry.rationale || entry.next_step);
}}
function atlasUnmappedIndexSet() {{
  return new Set((CURRICULUM_ATLAS.unmapped_asset_indices || []).map(value => String(value)));
}}
function hasExportState(item) {{
  const states = metadataStatesForItem(item).map(state => state.toLowerCase());
  return states.some(state => ['canva', 'exported', 'delivered', 'published'].includes(state));
}}
function hasFeedbackAttention(item) {{
  const entry = feedbackForItem(item) || {{}};
  const status = String(entry.status || '').toLowerCase();
  return ['needs-change', 'blocked', 'maybe', 'revise', 'revision-requested'].includes(status) || Boolean(entry.change_request);
}}
function isReviewQueueCard(card, ratingValue) {{
  const idx = card?.dataset?.idx || '';
  const item = LIBRARY[parseInt(idx || '0', 10)] || {{}};
  return !ratingValue || hasFeedbackAttention(item) || !hasEvaluationDecision(item) || !hasExportState(item) || atlasUnmappedIndexSet().has(idx);
}}
function feedbackLabel(entry) {{
  if (!entry) return '';
  return (entry.status || 'feedback').replace(/-/g, ' ');
}}
function applyFeedbackToCard(card, item) {{
  const badge = card.querySelector('.feedback-badge');
  if (!badge) return;
  const entry = feedbackForItem(item);
  if (!entry) {{
    badge.textContent = '';
    badge.title = '';
    badge.className = 'feedback-badge';
    return;
  }}
  badge.textContent = feedbackLabel(entry);
  badge.title = [entry.note, entry.change_request].filter(Boolean).join(' | ');
  badge.className = 'feedback-badge feedback-on';
}}
function applyFeedbackToCards() {{
  document.querySelectorAll('.card').forEach(card => {{
    const idx = parseInt(card.dataset.idx || '0', 10);
    applyFeedbackToCard(card, LIBRARY[idx]);
  }});
}}
function applyEvaluationToCard(card, item) {{
  const badge = card.querySelector('.evaluation-badge');
  if (!badge) return;
  const entry = evaluationForItem(item);
  if (!entry) {{
    badge.textContent = '';
    badge.title = '';
    badge.className = 'evaluation-badge';
    return;
  }}
  const label = evaluationDecisionLabel(entry) || (entry.score ? 'score ' + entry.score : 'evaluated');
  badge.textContent = label;
  badge.title = [
    entry.score ? 'Score ' + entry.score : '',
    entry.use_case,
    entry.next_step,
  ].filter(Boolean).join(' | ');
  badge.className = 'evaluation-badge evaluation-on evaluation-' + (entry.decision || 'scored');
}}
function applyEvaluationsToCards() {{
  document.querySelectorAll('.card').forEach(card => {{
    const idx = parseInt(card.dataset.idx || '0', 10);
    applyEvaluationToCard(card, LIBRARY[idx]);
  }});
}}
function applyMetadataToItem(item, entry) {{
  if (!item) return;
  const metadata = entry || null;
  if (metadata) {{
    item.metadata = metadata;
    item.title = metadata.title || item.base_title || item.title || item.name || '';
    item.name = item.title;
    item.metadata_states = cleanList(metadata.states || []);
    item.superseded_by = metadata.superseded_by || '';
    item.tags = [...cleanList(item.base_tags || []), ...cleanList(metadata.tags || [])]
      .filter((tag, index, all) => tag && all.indexOf(tag) === index);
  }} else {{
    item.metadata = null;
    item.title = item.base_title || item.title || item.name || '';
    item.name = item.base_name || item.title || '';
    item.metadata_states = [];
    item.superseded_by = '';
    item.tags = cleanList(item.base_tags || item.tags || []);
  }}
}}
function renderTagsForCard(card, item) {{
  const tagRow = card.querySelector('.tag-row');
  if (!tagRow) return;
  tagRow.innerHTML = '';
  cleanList(item.tags || []).slice(0, 5).forEach(tag => {{
    const el = document.createElement('span');
    el.className = 'tag';
    el.textContent = tag;
    tagRow.appendChild(el);
  }});
}}
function lineageNextLabel(item) {{
  if (item?.superseded_by) return 'next: compare';
  if (hasFeedbackAttention(item)) return 'next: revise';
  if (!hasEvaluationDecision(item)) return 'next: evaluate';
  if (!metadataStatesForItem(item).length) return 'next: tag';
  if (!hasExportState(item)) return 'next: export';
  return 'ready';
}}
function syncLineageForCard(card, item) {{
  const run = card.querySelector('.lineage-run');
  const source = card.querySelector('.lineage-source');
  const next = card.querySelector('.lineage-next');
  if (run) {{
    run.textContent = item.run_id ? item.run_id.replace(/^run-/, '') : 'run unknown';
    run.title = item.run_id || '';
  }}
  if (source) {{
    source.textContent = [item.source || 'archive', item.approval_status || 'unapproved'].filter(Boolean).join(' · ');
  }}
  if (next) next.textContent = lineageNextLabel(item);
}}
function syncCardContent(card, item) {{
  if (!card || !item) return;
  card.dataset.name = item.name || item.title || '';
  card.dataset.metadataStates = cleanList(item.metadata_states || []).join(',');
  card.dataset.search = searchTextForItem(item);
  const title = card.querySelector('.card-title');
  const prompt = card.querySelector('.card-prompt');
  const name = card.querySelector('.card-name');
  if (title) title.textContent = item.title || item.name || '';
  if (prompt) prompt.textContent = item.caption || item.source_prompt || item.prompt || '';
  if (name) name.textContent = item.name || '';
  const metadataBadge = card.querySelector('.metadata-state-badge');
  if (metadataBadge) {{
    const label = metadataStateLabel(item);
    metadataBadge.textContent = label;
    metadataBadge.title = item.superseded_by ? 'Superseded by ' + item.superseded_by : label;
    metadataBadge.className = label ? 'metadata-state-badge metadata-state-on' : 'metadata-state-badge';
  }}
  renderTagsForCard(card, item);
  syncLineageForCard(card, item);
  applyEvaluationToCard(card, item);
}}
function applyMetadataToCards() {{
  document.querySelectorAll('.card').forEach(card => {{
    const idx = parseInt(card.dataset.idx || '0', 10);
    syncCardContent(card, LIBRARY[idx]);
  }});
}}
function renderFeedback(item) {{
  const entry = feedbackForItem(item) || {{}};
  const status = document.getElementById('feedback-status');
  const note = document.getElementById('feedback-note');
  const change = document.getElementById('feedback-change-request');
  const msg = document.getElementById('feedback-status-message');
  if (status) status.value = entry.status || '';
  if (note) note.value = entry.note || '';
  if (change) change.value = entry.change_request || '';
  if (msg) msg.textContent = entry.updated_at ? 'Saved ' + entry.updated_at : '';
}}
function setFeedbackStatus(kind, message) {{
  const msg = document.getElementById('feedback-status-message');
  if (!msg) return;
  msg.className = 'feedback-status feedback-status-' + kind;
  msg.textContent = message || '';
}}
async function loadFeedback() {{
  FEEDBACK = _loadLocalFeedback();
  applyFeedbackToCards();
  updateFilterCounts();
  applyFilters();
  if (!SERVER_MODE) return;
  try {{
    const resp = await fetch('/api/feedback');
    const data = await resp.json();
    FEEDBACK = data.items || {{}};
    _saveLocalFeedback(FEEDBACK);
    applyFeedbackToCards();
    updateFilterCounts();
    applyFilters();
    if (_detailItem) renderFeedback(_detailItem);
  }} catch (err) {{}}
}}
async function saveFeedbackForDetail(event) {{
  if (event) {{
    event.preventDefault();
    event.stopPropagation();
  }}
  if (!_detailItem) return;
  const key = feedbackKeyForItem(_detailItem);
  const payload = {{
    key,
    status: document.getElementById('feedback-status')?.value || '',
    note: document.getElementById('feedback-note')?.value || '',
    change_request: document.getElementById('feedback-change-request')?.value || '',
  }};
  setFeedbackStatus('busy', 'Saving...');
  if (!SERVER_MODE) {{
    const localEntry = {{}};
    if (payload.status) localEntry.status = payload.status;
    if (payload.note.trim()) localEntry.note = payload.note.trim();
    if (payload.change_request.trim()) localEntry.change_request = payload.change_request.trim();
    if (Object.keys(localEntry).length) {{
      localEntry.updated_at = new Date().toISOString();
      FEEDBACK[key] = localEntry;
    }} else {{
      delete FEEDBACK[key];
    }}
    _saveLocalFeedback(FEEDBACK);
    applyFeedbackToCards();
    updateFilterCounts();
    applyFilters();
    setFeedbackStatus('success', 'Saved locally');
    return;
  }}
  try {{
    const resp = await fetch('/api/feedback', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify(payload),
    }});
    const data = await resp.json().catch(() => ({{error: 'Invalid server response'}}));
    if (!resp.ok || !data.ok) {{
      setFeedbackStatus('error', data.error || 'Save failed');
      return;
    }}
    if (data.feedback) FEEDBACK[key] = data.feedback;
    else delete FEEDBACK[key];
    _saveLocalFeedback(FEEDBACK);
    applyFeedbackToCards();
    updateFilterCounts();
    applyFilters();
    renderFeedback(_detailItem);
    setFeedbackStatus('success', 'Saved');
  }} catch (err) {{
    setFeedbackStatus('error', err?.message || 'Save failed');
  }}
}}
function renderEvaluation(item) {{
  const entry = evaluationForItem(item) || {{}};
  const decision = document.getElementById('evaluation-decision');
  const score = document.getElementById('evaluation-score');
  const useCase = document.getElementById('evaluation-use-case');
  const rationale = document.getElementById('evaluation-rationale');
  const nextStep = document.getElementById('evaluation-next-step');
  const msg = document.getElementById('evaluation-status-message');
  if (decision) decision.value = entry.decision || '';
  if (score) score.value = entry.score ? String(entry.score) : '';
  if (useCase) useCase.value = entry.use_case || '';
  if (rationale) rationale.value = entry.rationale || '';
  if (nextStep) nextStep.value = entry.next_step || '';
  if (msg) msg.textContent = entry.updated_at ? 'Saved ' + entry.updated_at : '';
}}
function setEvaluationStatus(kind, message) {{
  const msg = document.getElementById('evaluation-status-message');
  if (!msg) return;
  msg.className = 'evaluation-status evaluation-status-' + kind;
  msg.textContent = message || '';
}}
function runKeyForItem(item) {{
  return item?.run_key || [item?.project, item?.run_id].filter(Boolean).join('/');
}}
function renderRunDecisionSummary(detail, item) {{
  const box = document.getElementById('run-decision-summary');
  if (!box) return;
  const runKey = runKeyForItem(item);
  const runItems = LIBRARY.filter(candidate => runKeyForItem(candidate) === runKey);
  const counts = {{approve: 0, revise: 0, reject: 0, reference: 0, unreviewed: 0}};
  const scores = [];
  runItems.forEach(candidate => {{
    const entry = evaluationForItem(candidate) || {{}};
    const decision = entry.decision || '';
    if (decision && counts[decision] !== undefined) counts[decision] += 1;
    else counts.unreviewed += 1;
    if (entry.score) scores.push(Number(entry.score));
  }});
  const average = scores.length
    ? (scores.reduce((total, value) => total + value, 0) / scores.length).toFixed(1)
    : '';
  box.innerHTML = '';
  const title = document.createElement('h3');
  title.textContent = 'Run Decision Summary';
  const row = document.createElement('div');
  row.className = 'run-decision-chip-row';
  [
    ['Images', runItems.length],
    ['Approve', counts.approve],
    ['Revise', counts.revise],
    ['Reject', counts.reject],
    ['Reference', counts.reference],
    ['Unreviewed', counts.unreviewed],
  ].forEach(([label, value]) => {{
    const chip = document.createElement('span');
    chip.className = 'run-decision-chip';
    chip.textContent = label + ' ' + value;
    row.appendChild(chip);
  }});
  if (average) {{
    const avg = document.createElement('span');
    avg.className = 'run-decision-chip run-decision-score';
    avg.textContent = 'Avg score ' + average;
    row.appendChild(avg);
  }}
  box.appendChild(title);
  box.appendChild(row);
}}
async function loadEvaluations() {{
  EVALUATIONS = _loadLocalEvaluations();
  applyEvaluationsToCards();
  renderAtlasEvaluationSummaries();
  updateFilterCounts();
  applyFilters();
  if (!SERVER_MODE) return;
  try {{
    const resp = await fetch('/api/evaluations');
    const data = await resp.json();
    EVALUATIONS = data.items || {{}};
    _saveLocalEvaluations(EVALUATIONS);
    applyEvaluationsToCards();
    renderAtlasEvaluationSummaries();
    updateFilterCounts();
    applyFilters();
    if (_detailItem) {{
      renderEvaluation(_detailItem);
      renderRunDecisionSummary(detailForItem(_detailItem), _detailItem);
      renderCurriculumContext(_detailItem);
    }}
  }} catch (err) {{}}
}}
async function saveEvaluationForDetail(event) {{
  if (event) {{
    event.preventDefault();
    event.stopPropagation();
  }}
  if (!_detailItem) return;
  const key = evaluationKeyForItem(_detailItem);
  const payload = {{
    key,
    decision: document.getElementById('evaluation-decision')?.value || '',
    score: document.getElementById('evaluation-score')?.value || '',
    use_case: document.getElementById('evaluation-use-case')?.value || '',
    rationale: document.getElementById('evaluation-rationale')?.value || '',
    next_step: document.getElementById('evaluation-next-step')?.value || '',
  }};
  setEvaluationStatus('busy', 'Saving...');
  if (!SERVER_MODE) {{
    const localEntry = {{}};
    if (payload.decision) localEntry.decision = payload.decision;
    if (payload.score) localEntry.score = Number(payload.score);
    if (payload.use_case.trim()) localEntry.use_case = payload.use_case.trim();
    if (payload.rationale.trim()) localEntry.rationale = payload.rationale.trim();
    if (payload.next_step.trim()) localEntry.next_step = payload.next_step.trim();
    if (Object.keys(localEntry).length) {{
      localEntry.updated_at = new Date().toISOString();
      EVALUATIONS[key] = localEntry;
    }} else {{
      delete EVALUATIONS[key];
    }}
    _saveLocalEvaluations(EVALUATIONS);
    applyEvaluationsToCards();
    renderAtlasEvaluationSummaries();
    updateFilterCounts();
    applyFilters();
    renderEvaluation(_detailItem);
    renderRunDecisionSummary(detailForItem(_detailItem), _detailItem);
    renderCurriculumContext(_detailItem);
    setEvaluationStatus('success', 'Saved locally');
    return;
  }}
  try {{
    const resp = await fetch('/api/evaluations', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify(payload),
    }});
    const data = await resp.json().catch(() => ({{error: 'Invalid server response'}}));
    if (!resp.ok || !data.ok) {{
      setEvaluationStatus('error', data.error || 'Save failed');
      return;
    }}
    if (data.evaluation) EVALUATIONS[key] = data.evaluation;
    else delete EVALUATIONS[key];
    _saveLocalEvaluations(EVALUATIONS);
    applyEvaluationsToCards();
    renderAtlasEvaluationSummaries();
    updateFilterCounts();
    applyFilters();
    renderEvaluation(_detailItem);
    renderRunDecisionSummary(detailForItem(_detailItem), _detailItem);
    renderCurriculumContext(_detailItem);
    setEvaluationStatus('success', 'Saved');
  }} catch (err) {{
    setEvaluationStatus('error', err?.message || 'Save failed');
  }}
}}
function renderMetadata(item) {{
  const entry = metadataForItem(item) || {{}};
  const title = document.getElementById('metadata-title');
  const tags = document.getElementById('metadata-tags');
  const supersededBy = document.getElementById('metadata-superseded-by');
  const msg = document.getElementById('metadata-status-message');
  if (title) title.value = entry.title || '';
  if (tags) tags.value = cleanList(entry.tags || []).join(', ');
  if (supersededBy) supersededBy.value = entry.superseded_by || '';
  const states = new Set(cleanList(entry.states || []));
  document.querySelectorAll('#metadata-state-grid input[type="checkbox"]').forEach(input => {{
    input.checked = states.has(input.value);
  }});
  if (msg) msg.textContent = entry.updated_at ? 'Saved ' + entry.updated_at : '';
}}
function setMetadataStatus(kind, message) {{
  const msg = document.getElementById('metadata-status-message');
  if (!msg) return;
  msg.className = 'metadata-status metadata-status-' + kind;
  msg.textContent = message || '';
}}
async function loadArchiveMetadata() {{
  ARCHIVE_METADATA = _loadLocalMetadata();
  for (const item of LIBRARY) {{
    const key = metadataKeyForItem(item);
    if (key && ARCHIVE_METADATA[key]) applyMetadataToItem(item, ARCHIVE_METADATA[key]);
  }}
  applyMetadataToCards();
  updateFilterCounts();
  applyFilters();
  if (!SERVER_MODE) return;
  try {{
    const resp = await fetch('/api/archive-metadata');
    const data = await resp.json();
    ARCHIVE_METADATA = data.items || {{}};
    _saveLocalMetadata(ARCHIVE_METADATA);
    for (const item of LIBRARY) {{
      const key = metadataKeyForItem(item);
      applyMetadataToItem(item, key ? ARCHIVE_METADATA[key] || null : null);
    }}
    applyMetadataToCards();
    updateFilterCounts();
    applyFilters();
    if (_detailItem) renderMetadata(_detailItem);
  }} catch (err) {{}}
}}
async function saveMetadataForDetail(event) {{
  if (event) {{
    event.preventDefault();
    event.stopPropagation();
  }}
  if (!_detailItem) return;
  const key = metadataKeyForItem(_detailItem);
  const states = Array.from(document.querySelectorAll('#metadata-state-grid input[type="checkbox"]:checked')).map(input => input.value);
  const payload = {{
    key,
    title: document.getElementById('metadata-title')?.value || '',
    tags: document.getElementById('metadata-tags')?.value || '',
    states,
    superseded_by: document.getElementById('metadata-superseded-by')?.value || '',
  }};
  setMetadataStatus('busy', 'Saving...');
  if (!SERVER_MODE) {{
    const localEntry = {{}};
    if (payload.title.trim()) localEntry.title = payload.title.trim();
    const tags = cleanList(payload.tags);
    if (tags.length) localEntry.tags = tags;
    if (states.length) localEntry.states = states;
    if (payload.superseded_by.trim()) localEntry.superseded_by = payload.superseded_by.trim();
    if (Object.keys(localEntry).length) {{
      localEntry.updated_at = new Date().toISOString();
      ARCHIVE_METADATA[key] = localEntry;
    }} else {{
      delete ARCHIVE_METADATA[key];
    }}
    _saveLocalMetadata(ARCHIVE_METADATA);
    applyMetadataToItem(_detailItem, ARCHIVE_METADATA[key] || null);
    applyMetadataToCards();
    updateFilterCounts();
    applyFilters();
    renderMetadata(_detailItem);
    setMetadataStatus('success', 'Saved locally');
    return;
  }}
  try {{
    const resp = await fetch('/api/archive-metadata', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify(payload),
    }});
    const data = await resp.json().catch(() => ({{error: 'Invalid server response'}}));
    if (!resp.ok || !data.ok) {{
      setMetadataStatus('error', data.error || 'Save failed');
      return;
    }}
    if (data.metadata) ARCHIVE_METADATA[key] = data.metadata;
    else delete ARCHIVE_METADATA[key];
    _saveLocalMetadata(ARCHIVE_METADATA);
    applyMetadataToItem(_detailItem, data.metadata || null);
    applyMetadataToCards();
    updateFilterCounts();
    applyFilters();
    renderMetadata(_detailItem);
    setMetadataStatus('success', 'Saved');
  }} catch (err) {{
    setMetadataStatus('error', err?.message || 'Save failed');
  }}
}}
function revisionPromptForItem(item) {{
  const base = item?.source_prompt || item?.prompt || item?.caption || '';
  const change = document.getElementById('feedback-change-request')?.value.trim() || feedbackForItem(item)?.change_request || '';
  return change ? base + '\\n\\nRevision request:\\n' + change : base;
}}
async function copyPromptForCard(event, idx) {{
  if (event) {{
    event.preventDefault();
    event.stopPropagation();
  }}
  const item = LIBRARY[idx] || {{}};
  const text = item.source_prompt || item.prompt || item.caption || '';
  const button = event?.currentTarget || null;
  if (!text) return;
  try {{
    if (navigator.clipboard && window.isSecureContext) {{
      await navigator.clipboard.writeText(text);
    }} else {{
      const area = document.createElement('textarea');
      area.value = text;
      area.setAttribute('readonly', '');
      area.style.position = 'fixed';
      area.style.left = '-9999px';
      document.body.appendChild(area);
      area.select();
      document.execCommand('copy');
      document.body.removeChild(area);
    }}
    if (button) {{
      const original = button.textContent;
      button.textContent = 'Copied';
      window.setTimeout(() => {{ button.textContent = original; }}, 1400);
    }}
  }} catch (err) {{
    if (button) button.textContent = 'Copy failed';
  }}
}}
function stageRevisionFromDetail(event, autoSubmit) {{
  if (event) {{
    event.preventDefault();
    event.stopPropagation();
  }}
  if (!_detailItem) return;
  const mode = document.getElementById('studio-mode');
  if (mode) mode.value = 'single';
  syncStudioMode();
  const set = (id, value) => {{ const el = document.getElementById(id); if (el) el.value = value || ''; }};
  set('studio-project', _detailItem.project || 'studio');
  set('studio-name', ((_detailItem.title || _detailItem.name || 'Image') + ' Revision').trim());
  set('studio-model', _detailItem.model || 'gemini-2.5-flash-image');
  set('studio-style', _detailItem.style === 'none' ? '' : _detailItem.style || '');
  set('studio-ar', _detailItem.aspect_ratio || '16:9');
  set('studio-prompt', revisionPromptForItem(_detailItem));
  const dryRun = document.getElementById('studio-dry-run');
  if (dryRun && autoSubmit) dryRun.checked = true;
  setPortalMode('generate');
  document.getElementById('studio-panel')?.scrollIntoView({{block: 'start'}});
  setStudioStatus('info', autoSubmit ? 'Starting dry run revision...' : 'Revision staged from selected card.');
  if (autoSubmit) document.getElementById('studio-form')?.requestSubmit();
}}
function renderUsageSummary(data) {{
  const archive = data.archive || {{}};
  const cost = archive.estimated_cost || archive.known_cost || {{}};
  const spend = archive.spend || cost;
  const billing = data.provider_billing || {{}};
  const set = (id, text) => {{ const el = document.getElementById(id); if (el) el.textContent = text; }};
  set('usage-status', data.pricing_note || 'Usage loaded');
  set('usage-known-cost', formatUsd(spend.amount || cost.amount || 0));
  set('usage-cost-note', spend.basis === 'provider_billing_imports' ? 'provider billing import' : (cost.profile_estimated_images || 0) + ' profile + ' + (cost.manifest_amount_images || 0) + ' manifest');
  set('usage-billing-amount', formatUsd(billing.amount || 0));
  set('usage-billing-note', (billing.entries || 0) + ' imported row(s)');
  set('usage-image-count', String(archive.images || 0));
  const fallbackUnpriced = ((archive.known_cost || {{}}).unestimated_images || 0);
  set('usage-image-note', ((cost.unpriced_images ?? fallbackUnpriced) || 0) + ' unpriced');
  set('usage-run-count', String(archive.runs || 0));
  set('usage-project-count', (archive.projects || 0) + ' project(s)');
  set('usage-duration', formatDuration(archive.duration_seconds || 0));
  set('usage-failed-count', (archive.failed_images || 0) + ' failed image(s)');

  const models = document.getElementById('usage-models');
  if (models) {{
    const rows = (archive.by_model || []).slice(0, 6).map(row => (
      '<div class="ops-row"><span>' + studioEscapeHtml(row.model || 'unknown') + '</span><strong>' + studioEscapeHtml(row.images || 0) + '</strong></div>'
    ));
    models.innerHTML = rows.join('') || '<div class="ops-empty">No model data</div>';
  }}
  const recent = document.getElementById('usage-recent-runs');
  if (recent) {{
    const rows = (data.recent_runs || []).slice(0, 5).map(run => (
      '<div class="ops-row ops-run"><span>' + studioEscapeHtml(run.project || '') + '<small>' + studioEscapeHtml(run.run_id || '') + '</small></span><strong>' + studioEscapeHtml(run.image_count || 0) + '</strong></div>'
    ));
    recent.innerHTML = rows.join('') || '<div class="ops-empty">No runs yet</div>';
  }}
}}
async function saveBillingEntry(event) {{
  event.preventDefault();
  const status = document.getElementById('billing-import-status');
  if (!SERVER_MODE) {{
    if (status) status.textContent = 'Start the portal server first';
    return;
  }}
  const amount = Number(document.getElementById('billing-amount')?.value || 0);
  if (!amount) {{
    if (status) status.textContent = 'Enter an amount';
    return;
  }}
  if (status) status.textContent = 'Saving...';
  const payload = {{
    provider: document.getElementById('billing-provider')?.value || '',
    amount,
    model: document.getElementById('billing-model')?.value || '',
    note: document.getElementById('billing-note')?.value || '',
    label: 'portal manual entry',
  }};
  try {{
    const resp = await fetch('/api/billing-imports', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify(payload),
    }});
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'billing save failed');
    if (status) status.textContent = data.imported ? 'Saved' : 'Already imported';
    document.getElementById('billing-amount').value = '';
    await loadUsageSummary();
  }} catch (err) {{
    if (status) status.textContent = err.message || 'Save failed';
  }}
}}
function renderDeployReadiness(data) {{
  const status = document.getElementById('deploy-readiness-status');
  if (status) status.textContent = data.ok ? 'Ready for required deploy checks' : 'Missing required deploy checks';
  const checks = document.getElementById('deploy-readiness-checks');
  if (!checks) return;
  const rows = (data.checks || []).map(check => {{
    const state = check.ok ? 'ready' : (check.required ? 'missing' : 'optional');
    return '<div class="ops-row readiness-row readiness-' + state + '"><span>' +
      studioEscapeHtml(check.label || check.key || 'check') +
      '<small>' + studioEscapeHtml(check.detail || '') + '</small></span><strong>' +
      (check.ok ? 'OK' : (check.required ? 'Missing' : 'Optional')) +
      '</strong></div>';
  }});
  checks.innerHTML = rows.join('') || '<div class="ops-empty">No readiness checks</div>';
}}
async function loadUsageSummary() {{
  if (!SERVER_MODE) {{
    const status = document.getElementById('usage-status');
    if (status) status.textContent = 'Start the portal server for usage';
    const deployStatus = document.getElementById('deploy-readiness-status');
    if (deployStatus) deployStatus.textContent = 'Start the portal server for deploy readiness';
    return;
  }}
  try {{
    const resp = await fetch('/api/usage');
    const data = await resp.json();
    renderUsageSummary(data);
  }} catch (err) {{
    const status = document.getElementById('usage-status');
    if (status) status.textContent = 'Usage unavailable';
  }}
  try {{
    const resp = await fetch('/api/deploy-readiness');
    const data = await resp.json();
    renderDeployReadiness(data);
  }} catch (err) {{
    const status = document.getElementById('deploy-readiness-status');
    if (status) status.textContent = 'Deploy readiness unavailable';
  }}
}}
function renderDetailFields(detail, item) {{
  const fields = document.getElementById('run-detail-fields');
  if (!fields) return;
  fields.innerHTML = '';
  const rows = [
    ['Project', detail.project || item?.project || ''],
    ['Run', detail.run_id || item?.run_id || ''],
    ['Model', detail.model || item?.model || ''],
    ['Style', detail.style || item?.style || ''],
    ['Aspect', detail.aspect_ratio || item?.aspect_ratio || ''],
    ['State', detail.state || ''],
    ['Provider', detail.provider || ''],
    ['Timestamp', detail.timestamp || item?.timestamp || ''],
    ['Started', detail.started_at || ''],
    ['Finished', detail.finished_at || ''],
    ['Images', detail.image_count === 0 ? '0' : detail.image_count || ''],
    ['Prompt file', detail.prompt_file || ''],
    ['Prompt source', detail.prompt_source || ''],
    ['Invocation', detail.invocation_surface || ''],
  ];
  rows.forEach(([label, value]) => {{
    if (value === null || value === undefined || value === '') return;
    const dt = document.createElement('dt');
    const dd = document.createElement('dd');
    dt.textContent = label;
    dd.textContent = String(value);
    fields.appendChild(dt);
    fields.appendChild(dd);
  }});
}}
function renderFilenameWarning(item) {{
  const box = document.getElementById('run-detail-warning');
  if (!box) return;
  const warning = item?.filename_warning;
  if (!warning) {{
    box.className = 'run-detail-warning';
    box.innerHTML = '';
    return;
  }}
  box.className = 'run-detail-warning run-detail-warning-' + (warning.level || 'similar');
  const related = Array.isArray(warning.related) ? warning.related : [];
  const relatedHtml = related.slice(0, 8).map(entry => {{
    const run = entry.run_id ? '<span>' + studioEscapeHtml(entry.run_id) + '</span>' : '';
    const title = entry.title ? '<span>' + studioEscapeHtml(entry.title) + '</span>' : '';
    return '<li><strong>' + studioEscapeHtml(entry.basename || entry.file || '') + '</strong>' + run + title + '</li>';
  }}).join('');
  box.innerHTML = `
    <div class="run-detail-warning-title">${{studioEscapeHtml(warning.label || 'Filename warning')}}</div>
    <p>${{studioEscapeHtml(warning.message || '')}}</p>
    ${{relatedHtml ? '<ul class="run-detail-warning-list">' + relatedHtml + '</ul>' : ''}}
  `;
}}
function renderLineageComparison(item) {{
  const box = document.getElementById('run-lineage-comparison');
  if (!box) return;
  const comparison = item?.lineage_comparison || null;
  box.className = 'run-lineage-comparison';
  if (!comparison) {{
    box.innerHTML = `
      <h3>Prompt / Run Comparison</h3>
      <p class="lineage-empty">No linked comparison yet. Add a Superseded By key in card metadata to compare this asset with a local rerun.</p>
    `;
    return;
  }}
  if (comparison.status !== 'linked') {{
    box.className = 'run-lineage-comparison lineage-comparison-missing';
    box.innerHTML = `
      <h3>Prompt / Run Comparison</h3>
      <p class="lineage-empty">${{studioEscapeHtml(comparison.message || 'Comparison target unavailable.')}}</p>
      <code>${{studioEscapeHtml(comparison.target_key || '')}}</code>
    `;
    return;
  }}
  const changedRows = (comparison.changes || []).filter(row => row.changed);
  const steadyRows = (comparison.changes || []).filter(row => !row.changed);
  const rows = [...changedRows, ...steadyRows].map(row => `
    <tr class="${{row.changed ? 'lineage-changed' : 'lineage-steady'}}">
      <th>${{studioEscapeHtml(row.label || row.field || '')}}</th>
      <td>${{studioEscapeHtml(row.before || '')}}</td>
      <td>${{studioEscapeHtml(row.after || '')}}</td>
    </tr>
  `).join('');
  const targetBits = [comparison.target_project, comparison.target_run_id].filter(Boolean).join(' / ');
  box.className = 'run-lineage-comparison lineage-comparison-linked';
  box.innerHTML = `
    <div class="lineage-comparison-head">
      <div>
        <h3>Prompt / Run Comparison</h3>
        <p>Compared with ${{studioEscapeHtml(comparison.target_title || comparison.target_key || 'linked rerun')}}</p>
        ${{targetBits ? '<small>' + studioEscapeHtml(targetBits) + '</small>' : ''}}
      </div>
      <span>${{changedRows.length}} changed</span>
    </div>
    <table>
      <thead><tr><th>Field</th><th>This card</th><th>Superseding card</th></tr></thead>
      <tbody>${{rows || '<tr><td colspan="3">No visible prompt or setting changes.</td></tr>'}}</tbody>
    </table>
  `;
  if (Number.isInteger(comparison.target_index)) {{
    const action = document.createElement('button');
    action.type = 'button';
    action.textContent = 'Open Superseding Card';
    action.addEventListener('click', () => {{
      const target = LIBRARY[comparison.target_index];
      if (target) showRunDetail(target);
    }});
    box.appendChild(action);
  }}
}}
function openRunDetail(event, idx) {{
  if (event) event.stopPropagation();
  const item = LIBRARY[idx];
  if (!item) return;
  const card = document.querySelector('.card[data-idx="' + idx + '"]');
  if (card) setActiveCard(card, {{scroll: false}});
  showRunDetail(item);
}}
function showRunDetail(item) {{
  const panel = document.getElementById('run-detail-panel');
  const detail = detailForItem(item);
  if (!panel || !detail) return;
  _detailItem = item;
  panel.classList.add('open');
  panel.setAttribute('aria-hidden', 'false');
  setDetailText('run-detail-subtitle', [detail.project || item.project, detail.run_id || item.run_id].filter(Boolean).join(' / '));

  const links = document.getElementById('run-detail-links');
  if (links) {{
    links.innerHTML = '';
    appendDetailLink(links, 'Run viewer', detail.run_viewer);
    appendDetailLink(links, 'Project viewer', detail.project_viewer);
    appendDetailLink(links, 'run.json', detail.run_json);
  }}

  renderFilenameWarning(item);
  renderLineageComparison(item);
  renderRunDecisionSummary(detail, item);
  renderCurriculumContext(item);
  renderDetailFields(detail, item);
  renderMetadata(item);
  renderFeedback(item);
  renderEvaluation(item);
  const jsonEl = document.getElementById('run-detail-json');
  if (jsonEl) jsonEl.textContent = JSON.stringify(detail.manifest || {{}}, null, 2);
}}
function closeRunDetail() {{
  const panel = document.getElementById('run-detail-panel');
  if (!panel) return;
  panel.classList.remove('open');
  panel.setAttribute('aria-hidden', 'true');
}}
function getRating(key) {{ return _loadRatings()[key] || null; }}
function setRating(key, val) {{
  const r = _loadRatings();
  if (!val) delete r[key];
  else if (r[key] === val) delete r[key];
  else r[key] = val;
  _saveRatings(r);
  if (SERVER_MODE) {{
    fetch('/api/ratings', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{key, value: r[key] !== undefined ? r[key] : null}}),
    }}).catch(() => {{}});
  }}
}}
function applyRating(card, key) {{
  const val = getRating(key);
  card.classList.remove('rated-star','rated-reject');
  if (val === 'star')   card.classList.add('rated-star');
  if (val === 'reject') card.classList.add('rated-reject');
  const btnS = card.querySelector('.btn-rate.star');
  const btnR = card.querySelector('.btn-rate.reject');
  if (btnS) btnS.classList.toggle('starred',  val === 'star');
  if (btnR) btnR.classList.toggle('rejected', val === 'reject');
}}
function rateCard(e, key, val, card) {{
  e.stopPropagation();
  setActiveCard(card, {{scroll: false}});
  setRating(key, val);
  applyRating(card, key);
  updateFilterCounts();
  applyFilters();
}}
function setRatingFilter(mode) {{
  _ratingFilter = mode;
  document.querySelectorAll('#fb-all,#fb-star,#fb-reject,#fb-unreviewed,#fb-review-queue').forEach(b => b.classList.remove('active'));
  const a = document.getElementById('fb-' + mode);
  if (a) a.classList.add('active');
  applyFilters();
}}
function setLibrarySelectFilter(field, val) {{
  const selected = val || null;
  if (field === 'source') _sourceFilter = selected;
  else if (field === 'run') _runFilter = selected;
  else if (field === 'approval') _approvalFilter = selected;
  applyFilters();
}}
function filterLib(dim, val) {{
  if (dim === 'proj') {{
    const was = _projFilter === val;
    document.querySelectorAll('.chip-proj').forEach(b => b.classList.remove('active'));
    _projFilter = was ? null : val;
    if (!was) document.querySelector('.chip-proj[data-proj="' + val + '"]')?.classList.add('active');
  }} else if (dim === 'model') {{
    const was = _modelFilter === val;
    document.querySelectorAll('.chip-model').forEach(b => b.classList.remove('active'));
    _modelFilter = was ? null : val;
    if (!was) document.querySelector('.chip-model[data-model="' + val + '"]')?.classList.add('active');
  }} else if (dim === 'ar') {{
    const was = _arFilter === val;
    document.querySelectorAll('.chip-ar').forEach(b => b.classList.remove('active'));
    _arFilter = was ? null : val;
    if (!was) document.querySelector('.chip-ar[data-ar="' + val + '"]')?.classList.add('active');
  }} else if (dim === 'style') {{
    const was = _styleFilter === val;
    document.querySelectorAll('.chip-style').forEach(b => b.classList.remove('active'));
    _styleFilter = was ? null : val;
    if (!was) document.querySelector('.chip-style[data-style="' + val + '"]')?.classList.add('active');
  }}
  applyFilters();
}}
function applyFilters() {{
  const ratings = _loadRatings();
  document.querySelectorAll('.card').forEach(card => {{
    const rk = card.dataset.ratingKey;
    const val = ratings[rk] || null;
    let show = true;
    if (_ratingFilter === 'star')            show = val === 'star';
    else if (_ratingFilter === 'reject')     show = val === 'reject';
    else if (_ratingFilter === 'unreviewed') show = !val;
    else if (_ratingFilter === 'review-queue') show = isReviewQueueCard(card, val);
    if (show && _projFilter)   show = card.dataset.project === _projFilter;
    if (show && _modelFilter)  show = card.dataset.model === _modelFilter;
    if (show && _arFilter)     show = card.dataset.ar === _arFilter;
    if (show && _styleFilter)  show = card.dataset.style === _styleFilter;
    if (show && _sourceFilter) show = card.dataset.source === _sourceFilter;
    if (show && _runFilter)    show = card.dataset.run === _runFilter;
    if (show && _approvalFilter) show = card.dataset.approval === _approvalFilter;
    if (show && _atlasAssetFilter) show = _atlasAssetFilter.has(card.dataset.idx || '');
    if (show && _searchQuery)  show = (card.dataset.search || '').includes(_searchQuery);
    card.classList.toggle('hidden-filter', !show);
  }});
  syncActiveCardAfterFilter();
}}
function updateFilterCounts() {{
  const ratings = _loadRatings();
  const cards = Array.from(document.querySelectorAll('.card'));
  let stars = 0, rejects = 0, unreviewed = 0, reviewQueue = 0;
  cards.forEach(c => {{
    const v = ratings[c.dataset.ratingKey] || null;
    if (v === 'star') stars++; else if (v === 'reject') rejects++; else unreviewed++;
    if (isReviewQueueCard(c, v)) reviewQueue++;
  }});
  const set = (id, n) => {{ const el = document.getElementById(id); if (el) el.textContent = n ? ' ' + n : ''; }};
  set('fc-all', cards.length); set('fc-star', stars);
  set('fc-reject', rejects); set('fc-unreviewed', unreviewed);
  set('fc-review-queue', reviewQueue);
}}
function resizeGrid(v) {{
  document.documentElement.style.setProperty('--card-w', v + 'px');
  localStorage.setItem('rafiki:cardWidth', v);
}}
function applySort(mode) {{
  const grid = document.getElementById('grid');
  if (!grid) return;
  const cards = Array.from(grid.querySelectorAll('.card'));
  if (mode === 'default') {{
    cards.sort((a, b) => (parseInt(a.dataset.idx) || 0) - (parseInt(b.dataset.idx) || 0));
  }} else if (mode === 'newest') {{
    cards.sort((a, b) => (b.dataset.ts || '').localeCompare(a.dataset.ts || ''));
  }} else if (mode === 'oldest') {{
    cards.sort((a, b) => (a.dataset.ts || '').localeCompare(b.dataset.ts || ''));
  }} else if (mode === 'project') {{
    cards.sort((a, b) => (a.dataset.project || '').localeCompare(b.dataset.project || ''));
  }} else if (mode === 'model') {{
    cards.sort((a, b) => (a.dataset.model || '').localeCompare(b.dataset.model || ''));
  }} else if (mode === 'name') {{
    cards.sort((a, b) => (a.dataset.name || '').localeCompare(b.dataset.name || ''));
  }}
  cards.forEach(c => grid.appendChild(c));
  syncActiveCardAfterFilter();
}}
function visibleCards() {{
  return Array.from(document.querySelectorAll('.card:not(.hidden-filter)'));
}}
function setActiveCard(card, options = {{}}) {{
  document.querySelectorAll('.card.active-card').forEach(el => el.classList.remove('active-card'));
  _activeCard = card || null;
  if (!_activeCard) return;
  _activeCard.classList.add('active-card');
  if (options.scroll !== false) {{
    _activeCard.scrollIntoView({{block: 'nearest', inline: 'nearest'}});
  }}
}}
function syncActiveCardAfterFilter() {{
  if (_activeCard && document.body.contains(_activeCard) && !_activeCard.classList.contains('hidden-filter')) return;
  setActiveCard(visibleCards()[0] || null, {{scroll: false}});
}}
function moveActiveCard(dir) {{
  const cards = visibleCards();
  if (!cards.length) {{
    setActiveCard(null);
    return;
  }}
  let idx = cards.indexOf(_activeCard);
  if (idx < 0) idx = dir > 0 ? -1 : 0;
  setActiveCard(cards[(idx + dir + cards.length) % cards.length]);
}}
function rateActiveCard(val) {{
  const card = _activeCard || visibleCards()[0];
  if (!card) return;
  setActiveCard(card, {{scroll: false}});
  setRating(card.dataset.ratingKey, val);
  applyRating(card, card.dataset.ratingKey);
  updateFilterCounts();
  applyFilters();
}}
function isLibraryTypingTarget(target) {{
  if (!target) return false;
  const tag = (target.tagName || '').toLowerCase();
  return target.isContentEditable || ['input', 'select', 'textarea', 'button'].includes(tag);
}}
function handleLibraryKeydown(event) {{
  if (lb?.classList.contains('open')) return;
  if (event.key === 'Escape') {{
    closeRunDetail();
    return;
  }}
  if (isLibraryTypingTarget(event.target)) return;
  const key = event.key.toLowerCase();
  if (event.key === 'ArrowRight' || event.key === 'ArrowDown' || key === 'j' || key === 'n') {{
    event.preventDefault();
    moveActiveCard(1);
  }} else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp' || key === 'k' || key === 'p') {{
    event.preventDefault();
    moveActiveCard(-1);
  }} else if (key === 's') {{
    event.preventDefault();
    rateActiveCard('star');
  }} else if (key === 'x') {{
    event.preventDefault();
    rateActiveCard('reject');
  }} else if (event.key === '0' || event.key === 'Backspace') {{
    event.preventDefault();
    rateActiveCard(null);
  }} else if (key === 'i' && _activeCard) {{
    event.preventDefault();
    showRunDetail(LIBRARY[parseInt(_activeCard.dataset.idx || '0', 10)]);
  }} else if (event.key === 'Enter' && _activeCard) {{
    event.preventDefault();
    lbOpen(parseInt(_activeCard.dataset.idx || '0', 10));
  }}
}}
function syncStudioMode() {{
  const mode = document.getElementById('studio-mode')?.value || 'single';
  const showBatch = mode === 'batch';
  document.querySelectorAll('.studio-single').forEach(el => el.classList.toggle('studio-hidden', showBatch));
  document.querySelectorAll('.studio-batch').forEach(el => el.classList.toggle('studio-hidden', !showBatch));
}}
function setStudioStatus(kind, html) {{
  const status = document.getElementById('studio-status');
  if (!status) return;
  status.className = 'studio-status studio-status-' + kind;
  status.innerHTML = html;
}}
function setPortalActionStatus(kind, html) {{
  const status = document.getElementById('portal-action-status');
  if (!status) return;
  status.className = 'portal-action-status portal-action-status-' + kind;
  status.innerHTML = html;
}}
function syncPortalAction() {{
  const action = document.getElementById('action-name')?.value || 'approve-starred';
  const show = (selector, enabled) => document.querySelectorAll(selector).forEach(el => el.classList.toggle('portal-action-hidden', !enabled));
  show('.action-run', action === 'approve-starred');
  show('.action-format', action === 'registry-export');
  show('.action-database,.action-force', action === 'notion-export');
  show('.action-viewer,.action-prod', action === 'static-deploy');
  show('.action-nozip', action === 'canva-export');
}}
async function loadPortalActions() {{
  if (!SERVER_MODE) return;
  try {{
    const resp = await fetch('/api/actions');
    const data = await resp.json();
    const count = Array.isArray(data.actions) ? data.actions.length : 0;
    const target = document.getElementById('actions-discovery');
    if (target) target.textContent = count + ' local action' + (count === 1 ? '' : 's') + ' available';
  }} catch (err) {{
    const target = document.getElementById('actions-discovery');
    if (target) target.textContent = 'Actions unavailable';
  }}
}}
async function submitPortalAction(event) {{
  event.preventDefault();
  const action = document.getElementById('action-name')?.value || '';
  const payload = {{
    action,
    project: document.getElementById('action-project')?.value || '',
    dry_run: document.getElementById('action-dry-run')?.checked || false,
    confirm: document.getElementById('action-confirm')?.checked || false,
  }};
  const run = document.getElementById('action-run')?.value.trim() || '';
  const databaseId = document.getElementById('action-database')?.value.trim() || '';
  const viewerDir = document.getElementById('action-viewer')?.value.trim() || '';
  if (action === 'approve-starred' && run) payload.run = run;
  if (action === 'registry-export') payload.format = document.getElementById('action-format')?.value || 'csv';
  if (action === 'canva-export') payload.no_zip = document.getElementById('action-nozip')?.checked || false;
  if (action === 'notion-export') {{
    if (databaseId) payload.database_id = databaseId;
    payload.force = document.getElementById('action-force')?.checked || false;
  }}
  if (action === 'static-deploy') {{
    if (viewerDir) payload.viewer_dir = viewerDir;
    payload.prod = document.getElementById('action-prod')?.checked || false;
  }}

  const submit = document.getElementById('action-submit');
  if (submit) submit.disabled = true;
  setPortalActionStatus('busy', 'Running ' + studioEscapeHtml(action) + '...');
  try {{
    const resp = await fetch('/api/actions', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify(payload),
    }});
    const data = await resp.json().catch(() => ({{error: 'Invalid server response'}}));
    if (!resp.ok || !data.ok) {{
      setPortalActionStatus('error', studioEscapeHtml(data.error || data.detail || 'Action failed.'));
      return;
    }}
    const bits = [];
    if (data.approved_count !== undefined) bits.push(data.approved_count + ' approved');
    if (data.image_count !== undefined) bits.push(data.image_count + ' image(s)');
    if (data.exported !== undefined) bits.push(data.exported + ' exported');
    if (data.count !== undefined) bits.push(data.count + ' indexed');
    if (data.metadata_stamped !== undefined) bits.push(data.metadata_stamped + ' card state' + (data.metadata_stamped === 1 ? '' : 's') + ' stamped');
    if (data.source_mapping) {{
      const mapping = data.source_mapping;
      bits.push(mapping.mapped
        ? mapping.source_kind + ' source map (' + mapping.key_count + ' card' + (mapping.key_count === 1 ? '' : 's') + ')'
        : 'unmapped: ' + mapping.reason);
    }}
    if (data.result_path) bits.push('<code>' + studioEscapeHtml(data.result_path) + '</code>');
    if (data.path) bits.push('<code>' + studioEscapeHtml(data.path) + '</code>');
    if (data.url) bits.push('<a href="' + data.url + '">' + studioEscapeHtml(data.url) + '</a>');
    if (data.viewer_path) bits.push('<code>' + studioEscapeHtml(data.viewer_path) + '</code>');
    setPortalActionStatus('success', studioEscapeHtml(data.action) + ': ' + (bits.join(' · ') || 'complete'));
  }} catch (err) {{
    setPortalActionStatus('error', studioEscapeHtml(err?.message || 'Request failed.'));
  }} finally {{
    if (submit) submit.disabled = false;
  }}
}}
async function submitStudio(event) {{
  event.preventDefault();
  const mode = document.getElementById('studio-mode')?.value || 'single';
  const project = document.getElementById('studio-project')?.value.trim() || 'studio';
  const payload = {{
    mode,
    project,
    model: document.getElementById('studio-model')?.value || 'gemini-2.5-flash-image',
    style: document.getElementById('studio-style')?.value.trim() || '',
    aspect_ratio: document.getElementById('studio-ar')?.value || '16:9',
    quality: document.getElementById('studio-quality')?.value || 'high',
    resolution: document.getElementById('studio-resolution')?.value || '1K',
    reference_image: document.getElementById('studio-reference')?.value.trim() || '',
    dry_run: document.getElementById('studio-dry-run')?.checked || false,
  }};
  if (mode === 'single') {{
    payload.name = document.getElementById('studio-name')?.value.trim() || '';
    payload.prompt = document.getElementById('studio-prompt')?.value.trim() || '';
    if (!payload.prompt) {{
      setStudioStatus('error', 'A prompt is required for single-prompt mode.');
      return;
    }}
  }} else {{
    payload.prompt_file = document.getElementById('studio-prompt-file')?.value.trim() || '';
    payload.workers = parseInt(document.getElementById('studio-workers')?.value || '1', 10) || 1;
    if (!payload.prompt_file) {{
      setStudioStatus('error', 'A Markdown prompt file path is required for batch mode.');
      return;
    }}
  }}
  const submit = document.getElementById('studio-submit');
  if (submit) {{
    submit.disabled = true;
    submit.textContent = mode === 'single' ? 'Generating…' : 'Running batch…';
  }}
  setStudioStatus(
    'busy',
    payload.dry_run
      ? 'Running dry run. Rafiki is validating inputs and building the run metadata.'
      : 'Generation in progress. This request stays open until the run completes.'
  );
  try {{
    const resp = await fetch('/api/regen', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify(payload),
    }});
    const data = await resp.json().catch(() => ({{error: 'Invalid server response'}}));
    if (!resp.ok || !data.ok) {{
      const msg = data.error || data.detail || 'Generation failed.';
      setStudioStatus('error', studioEscapeHtml(msg));
      return;
    }}
    const links = [];
    if (data.viewer_url) links.push(`<a href="${{data.viewer_url}}">Project viewer</a>`);
    if (data.run_viewer_url) links.push(`<a href="${{data.run_viewer_url}}">This run</a>`);
    links.push('<button type="button" class="studio-inline-btn" onclick="location.reload()">Refresh library</button>');
    const summary = data.all_ok
      ? `Completed <strong>${{data.generated}}/${{data.total}}</strong> image(s)`
      : `Run finished with partial success: <strong>${{data.generated}}/${{data.total}}</strong> image(s) generated`;
    setStudioStatus(
      data.all_ok ? 'success' : 'info',
      `${{summary}} in <code>${{studioEscapeHtml(data.project)}}</code> · run <code>${{studioEscapeHtml(data.run_id)}}</code><div class="studio-links">${{links.join('')}}</div>`
    );
  }} catch (err) {{
    setStudioStatus('error', studioEscapeHtml(err?.message || 'Request failed.'));
  }} finally {{
    if (submit) {{
      submit.disabled = false;
      submit.textContent = 'Run';
    }}
  }}
}}
(function() {{
  const saved = localStorage.getItem('rafiki:cardWidth');
  if (saved) {{ resizeGrid(saved); const sl = document.getElementById('grid-sizer'); if (sl) sl.value = saved; }}
  syncStudioMode();
  syncPortalAction();
  initPortalMode();
  loadPortalActions();
  loadUsageSummary();
  loadArchiveMetadata();
  loadFeedback();
  loadEvaluations();
  if (!SERVER_MODE) {{
    document.getElementById('studio-panel')?.classList.add('studio-disabled');
    document.getElementById('portal-actions-panel')?.classList.add('studio-disabled');
    document.querySelectorAll('#studio-form input, #studio-form textarea, #studio-form select, #studio-form button').forEach(el => {{
      el.disabled = true;
    }});
    document.querySelectorAll('#portal-action-form input, #portal-action-form select, #portal-action-form button').forEach(el => {{
      el.disabled = true;
    }});
    setStudioStatus('info', 'Prompt Studio requires <code>python generate.py serve</code>. File-based viewers are read-only.');
    setPortalActionStatus('info', 'Curation and export actions require <code>python generate.py serve</code>.');
  }}
}})();
if (SERVER_MODE) {{
  fetch('/api/ratings').then(r => r.json()).then(sv => {{
    const merged = Object.assign(_loadRatings(), sv);
    _saveRatings(merged);
    document.querySelectorAll('.card').forEach(c => {{
      if (c.dataset.ratingKey) applyRating(c, c.dataset.ratingKey);
    }});
    updateFilterCounts();
  }}).catch(() => {{}});
}}

const grid = document.getElementById('grid');
LIBRARY.forEach((item, i) => {{
  const arCss = (item.aspect_ratio || '16:9').replace(':', '/');
  const card = document.createElement('div');
  card.className = 'card';
  card.dataset.ratingKey = item.file;
  card.dataset.idx = i;
  card.dataset.project = item.project;
  card.dataset.model = item.model;
  card.dataset.ar = item.aspect_ratio || '';
  card.dataset.style = item.style || '';
  card.dataset.source = item.source || '';
  card.dataset.run = item.run_id || '';
  card.dataset.runKey = item.run_key || '';
  card.dataset.approval = item.approval_status || 'unapproved';
  card.dataset.warning = item.filename_warning?.level || '';
  card.dataset.ts = item.timestamp || '';
  card.dataset.name = item.name || '';
  card.dataset.search = searchTextForItem(item);
  card.onclick = () => {{
    setActiveCard(card, {{scroll: false}});
    lbOpen(i);
  }};
  card.innerHTML = `
    <div class="img-wrap" style="aspect-ratio:${{arCss}}">
      <span class="img-num">${{String(i + 1).padStart(2, '0')}}</span>
      ${{item.ok
        ? '<img src="' + resolveAssetSrc(item.file) + '" alt="" loading="lazy">'
        : '<div class="missing-img">not generated</div>'}}
    </div>
    <div class="card-meta-row">
      <span class="approval-badge"></span>
      <span class="filename-warning-badge"></span>
      <span class="metadata-state-badge"></span>
      <span class="feedback-badge"></span>
      <span class="evaluation-badge"></span>
      <span class="model-badge"></span>
    </div>
    <div class="card-title"></div>
    <div class="card-prompt"></div>
    <div class="tag-row"></div>
    <div class="lineage-row">
      <span class="lineage-chip lineage-run"></span>
      <span class="lineage-chip lineage-source"></span>
      <span class="lineage-chip lineage-next"></span>
      <button type="button" class="lineage-copy" onclick="copyPromptForCard(event, ${{i}})">Copy Prompt</button>
    </div>
    <div class="card-foot">
      <span class="card-name"></span>
      <span class="proj-badge">${{item.project.replace(/-/g, ' ')}}</span>
      <button class="btn-rate detail" onclick="openRunDetail(event, ${{i}})">Info</button>
      <button class="btn-rate star"   onclick="rateCard(event,'${{item.file}}','star',  this.closest('.card'))">&#9733;</button>
      <button class="btn-rate reject" onclick="rateCard(event,'${{item.file}}','reject',this.closest('.card'))">&#x2715;</button>
    </div>
  `;
  const approval = card.querySelector('.approval-badge');
  if (approval) {{
    approval.textContent = item.approval_status || 'run';
    approval.classList.toggle('approval-approved', item.approval_status === 'approved');
  }}
  const filenameWarning = card.querySelector('.filename-warning-badge');
  if (filenameWarning && item.filename_warning) {{
    filenameWarning.textContent = item.filename_warning.label || 'Filename warning';
    filenameWarning.title = item.filename_warning.message || '';
    filenameWarning.classList.add('filename-warning-' + (item.filename_warning.level || 'similar'));
  }}
  const modelBadge = card.querySelector('.model-badge');
  if (modelBadge) {{
    modelBadge.textContent = [item.model, item.style, item.aspect_ratio].filter(Boolean).join(' · ');
  }}
  syncCardContent(card, item);
  applyFeedbackToCard(card, item);
  const img = card.querySelector('img');
  if (img) img.addEventListener('error', () => {{
    img.closest('.img-wrap').innerHTML = '<div class="missing-img">file missing</div>';
  }});
  grid.appendChild(card);
  applyRating(card, item.file);
}});
updateFilterCounts();
syncActiveCardAfterFilter();
document.addEventListener('keydown', handleLibraryKeydown);

{_lightbox_js()}
</script>
</body>
</html>"""

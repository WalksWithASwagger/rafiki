"""Master library viewer — all Rafiki images across all projects in one page."""

from __future__ import annotations

import json
import re
import webbrowser
from datetime import datetime
from pathlib import Path

from lib import registry
from lib.extra_outputs import load_extra_outputs
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

    records.sort(key=lambda r: r["timestamp"], reverse=True)

    html = _render_library(records)
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


def _render_library(records: list[dict]) -> str:
    _annotate_filename_warnings(records)

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
    library_json = json.dumps(records, ensure_ascii=False)
    run_details_json = json.dumps(run_details, ensure_ascii=False)
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

{_studio_panel_html(all_style_names, default_style, model_options)}
{_actions_panel_html(projects)}

<div class="filter-bar" id="filter-bar">
  <button class="filter-btn active" id="fb-all"        onclick="setRatingFilter('all')">All <span id="fc-all"></span></button>
  <button class="filter-btn"        id="fb-star"       onclick="setRatingFilter('star')">&#9733; Starred <span id="fc-star"></span></button>
  <button class="filter-btn"        id="fb-reject"     onclick="setRatingFilter('reject')">&#x2715; Rejected <span id="fc-reject"></span></button>
  <button class="filter-btn"        id="fb-unreviewed" onclick="setRatingFilter('unreviewed')">Unreviewed <span id="fc-unreviewed"></span></button>
  <input id="search" type="text" placeholder="Search prompts…" autocomplete="off"
         oninput="_searchQuery=this.value.toLowerCase().trim();applyFilters()">
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

<div class="grid" id="grid"></div>

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
    <dl class="run-detail-fields" id="run-detail-fields"></dl>
    <pre class="run-detail-json" id="run-detail-json"></pre>
  </div>
</aside>

{_lightbox_html()}

<script>
const LIBRARY = {library_json};
const ITEMS = LIBRARY;
const RUN_DETAILS = {run_details_json};
const RATINGS_KEY = 'rafiki:ratings';
const SERVER_MODE = location.protocol !== 'file:';
let _ratingFilter = 'all';
let _projFilter = null;
let _modelFilter = null;
let _arFilter = null;
let _styleFilter = null;
let _sourceFilter = null;
let _runFilter = null;
let _approvalFilter = null;
let _searchQuery = '';
let _activeCard = null;

function _loadRatings() {{
  try {{ return JSON.parse(localStorage.getItem(RATINGS_KEY) || '{{}}'); }} catch(e) {{ return {{}}; }}
}}
function _saveRatings(r) {{ localStorage.setItem(RATINGS_KEY, JSON.stringify(r)); }}
function studioEscapeHtml(value) {{
  return String(value || '').replace(/[&<>"]/g, ch => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[ch]));
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
  renderDetailFields(detail, item);
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
  document.querySelectorAll('#fb-all,#fb-star,#fb-reject,#fb-unreviewed').forEach(b => b.classList.remove('active'));
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
    if (show && _projFilter)   show = card.dataset.project === _projFilter;
    if (show && _modelFilter)  show = card.dataset.model === _modelFilter;
    if (show && _arFilter)     show = card.dataset.ar === _arFilter;
    if (show && _styleFilter)  show = card.dataset.style === _styleFilter;
    if (show && _sourceFilter) show = card.dataset.source === _sourceFilter;
    if (show && _runFilter)    show = card.dataset.run === _runFilter;
    if (show && _approvalFilter) show = card.dataset.approval === _approvalFilter;
    if (show && _searchQuery)  show = (card.dataset.search || '').includes(_searchQuery);
    card.classList.toggle('hidden-filter', !show);
  }});
  syncActiveCardAfterFilter();
}}
function updateFilterCounts() {{
  const ratings = _loadRatings();
  const cards = Array.from(document.querySelectorAll('.card'));
  let stars = 0, rejects = 0, unreviewed = 0;
  cards.forEach(c => {{
    const v = ratings[c.dataset.ratingKey] || null;
    if (v === 'star') stars++; else if (v === 'reject') rejects++; else unreviewed++;
  }});
  const set = (id, n) => {{ const el = document.getElementById(id); if (el) el.textContent = n ? ' ' + n : ''; }};
  set('fc-all', cards.length); set('fc-star', stars);
  set('fc-reject', rejects); set('fc-unreviewed', unreviewed);
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
  loadPortalActions();
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
  const warningText = item.filename_warning
    ? [
        item.filename_warning.label,
        item.filename_warning.level,
        item.filename_warning.basename,
        item.filename_warning.normalized_stem,
        ...(item.filename_warning.group_basenames || []),
      ].filter(Boolean).join(' ')
    : '';
  card.dataset.search = ((item.title || item.name || '') + ' ' + (item.caption || '') + ' ' + (item.source_prompt || item.prompt || '') + ' ' + (item.tags || []).join(' ') + ' ' + (item.project || '') + ' ' + (item.run_id || '') + ' ' + (item.source || '') + ' ' + (item.approval_status || '') + ' ' + warningText).toLowerCase();
  card.onclick = () => {{
    setActiveCard(card, {{scroll: false}});
    lbOpen(i);
  }};
  card.innerHTML = `
    <div class="img-wrap" style="aspect-ratio:${{arCss}}">
      <span class="img-num">${{String(i + 1).padStart(2, '0')}}</span>
      ${{item.ok
        ? '<img src="' + item.file + '" alt="" loading="lazy">'
        : '<div class="missing-img">not generated</div>'}}
    </div>
    <div class="card-meta-row">
      <span class="approval-badge"></span>
      <span class="filename-warning-badge"></span>
      <span class="model-badge"></span>
    </div>
    <div class="card-title"></div>
    <div class="card-prompt"></div>
    <div class="tag-row"></div>
    <div class="card-foot">
      <span class="card-name"></span>
      <span class="proj-badge">${{item.project.replace(/-/g, ' ')}}</span>
      <button class="btn-rate detail" onclick="openRunDetail(event, ${{i}})">Info</button>
      <button class="btn-rate star"   onclick="rateCard(event,'${{item.file}}','star',  this.closest('.card'))">&#9733;</button>
      <button class="btn-rate reject" onclick="rateCard(event,'${{item.file}}','reject',this.closest('.card'))">&#x2715;</button>
    </div>
  `;
  card.querySelector('.card-title').textContent = item.title || item.name || '';
  card.querySelector('.card-prompt').textContent = item.caption || item.source_prompt || item.prompt || '';
  card.querySelector('.card-name').textContent = item.name || '';
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
  const tagRow = card.querySelector('.tag-row');
  (item.tags || []).slice(0, 5).forEach(tag => {{
    const el = document.createElement('span');
    el.className = 'tag';
    el.textContent = tag;
    tagRow.appendChild(el);
  }});
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


def _library_extra_css() -> str:
    return """<style>
.teal-pill {
  background: rgba(0,200,180,0.12);
  border: 1px solid rgba(0,200,180,0.3);
  color: var(--teal);
}
.chip-sep {
  color: var(--border);
  margin: 0 0.1rem;
  font-size: 0.85rem;
}
.proj-badge {
  font-size: 0.62rem;
  background: rgba(0,200,180,0.1);
  border: 1px solid rgba(0,200,180,0.2);
  color: var(--teal);
  padding: 0.08rem 0.3rem;
  border-radius: 4px;
  font-family: ui-monospace, monospace;
  white-space: nowrap;
  flex-shrink: 0;
}
.card-meta-row {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.55rem 0.65rem 0;
  min-height: 1.35rem;
}
.approval-badge,
.filename-warning-badge,
.model-badge,
.tag {
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--dim);
  font-size: 0.58rem;
  line-height: 1.1;
  padding: 0.14rem 0.3rem;
  white-space: nowrap;
}
.filename-warning-badge:empty {
  display: none;
}
.filename-warning-exact,
.filename-warning-similar {
  color: #ffd78f;
  border-color: rgba(255,193,94,0.34);
  background: rgba(255,193,94,0.10);
}
.filename-warning-similar {
  color: #d7c7ff;
  border-color: rgba(124,106,247,0.34);
  background: rgba(124,106,247,0.12);
}
.approval-approved {
  border-color: rgba(0,200,180,0.32);
  background: rgba(0,200,180,0.10);
  color: var(--teal);
}
.model-badge {
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}
.card-title {
  color: var(--ink);
  font-size: 0.78rem;
  font-weight: 600;
  line-height: 1.25;
  padding: 0.38rem 0.65rem 0;
}
.tag-row {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
  padding: 0.35rem 0.65rem 0;
  min-height: 1rem;
}
#search {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--ink);
  padding: 0.22rem 0.65rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-family: inherit;
  outline: none;
  flex: 1;
  min-width: 100px;
  max-width: 220px;
  transition: border-color 0.15s;
}
#search:focus, #search:hover { border-color: var(--accent); }
#search::placeholder { color: var(--dim); opacity: 0.6; }
.filter-select-label {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  color: var(--dim);
  font-size: 0.72rem;
  user-select: none;
}
.filter-select-label select {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--dim);
  padding: 0.22rem 0.5rem;
  border-radius: 6px;
  font-size: 0.75rem;
  cursor: pointer;
  font-family: inherit;
  outline: none;
  max-width: 170px;
}
.filter-select-label select:focus,
.filter-select-label select:hover {
  border-color: var(--accent);
  color: var(--ink);
}
.keyboard-hint {
  color: var(--dim);
  font-size: 0.68rem;
  white-space: nowrap;
  opacity: 0.78;
}
.sort-select {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--dim);
  padding: 0.22rem 0.5rem;
  border-radius: 6px;
  font-size: 0.75rem;
  cursor: pointer;
  font-family: inherit;
  outline: none;
}
.sort-select:focus, .sort-select:hover { border-color: var(--accent); color: var(--ink); }
.card.active-card {
  border-color: var(--teal);
  box-shadow: 0 0 0 2px rgba(0,200,180,0.22), 0 8px 32px rgba(0,200,180,0.12);
}
.btn-rate.detail {
  color: var(--teal);
  border-color: rgba(0,200,180,0.24);
}
.run-detail-panel {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: min(480px, 92vw);
  background: #12101f;
  border-left: 1px solid var(--border);
  box-shadow: -18px 0 48px rgba(0,0,0,0.35);
  transform: translateX(105%);
  transition: transform 0.18s ease;
  z-index: 8500;
  display: flex;
  flex-direction: column;
}
.run-detail-panel.open {
  transform: translateX(0);
}
.run-detail-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid var(--border);
}
.run-detail-head h2 {
  margin: 0 0 0.2rem;
  font-size: 1rem;
}
.run-detail-head p {
  margin: 0;
  color: var(--dim);
  font-size: 0.76rem;
  overflow-wrap: anywhere;
}
.run-detail-close {
  background: rgba(255,255,255,0.08);
  border: 1px solid var(--border);
  color: var(--ink);
  border-radius: 50%;
  width: 2rem;
  height: 2rem;
  cursor: pointer;
  flex-shrink: 0;
}
.run-detail-body {
  padding: 1rem;
  overflow: auto;
}
.run-detail-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.run-detail-links a {
  color: var(--teal);
  border: 1px solid rgba(0,200,180,0.22);
  background: rgba(0,200,180,0.08);
  border-radius: 8px;
  padding: 0.32rem 0.55rem;
  text-decoration: none;
  font-size: 0.75rem;
}
.run-detail-links a:hover {
  border-color: var(--teal);
}
.run-detail-warning {
  display: none;
  border: 1px solid rgba(255,193,94,0.26);
  background: rgba(255,193,94,0.08);
  border-radius: 8px;
  padding: 0.75rem;
  margin-bottom: 1rem;
  color: var(--ink);
}
.run-detail-warning-exact,
.run-detail-warning-similar {
  display: block;
}
.run-detail-warning-similar {
  border-color: rgba(124,106,247,0.28);
  background: rgba(124,106,247,0.10);
}
.run-detail-warning-title {
  font-size: 0.78rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}
.run-detail-warning p {
  margin: 0;
  color: var(--dim);
  font-size: 0.74rem;
  line-height: 1.45;
}
.run-detail-warning-list {
  margin: 0.55rem 0 0;
  padding-left: 1rem;
  color: var(--dim);
  font-size: 0.7rem;
}
.run-detail-warning-list li {
  margin: 0.25rem 0;
  overflow-wrap: anywhere;
}
.run-detail-warning-list span {
  margin-left: 0.35rem;
}
.run-detail-fields {
  display: grid;
  grid-template-columns: minmax(6rem, 0.38fr) 1fr;
  gap: 0.35rem 0.75rem;
  margin: 0 0 1rem;
  font-size: 0.76rem;
}
.run-detail-fields dt {
  color: var(--dim);
}
.run-detail-fields dd {
  color: var(--ink);
  overflow-wrap: anywhere;
}
.run-detail-json {
  border: 1px solid var(--border);
  background: rgba(0,0,0,0.22);
  border-radius: 8px;
  padding: 0.75rem;
  color: var(--dim);
  font-size: 0.68rem;
  line-height: 1.45;
  overflow: auto;
  max-height: 42vh;
}
.studio-panel {
  margin: 1rem 1.5rem 0.9rem;
  padding: 1rem 1rem 0.9rem;
  border: 1px solid var(--border);
  border-radius: 14px;
  background:
    linear-gradient(145deg, rgba(124,106,247,0.10), rgba(0,200,180,0.05)),
    var(--surface);
}
.studio-heading {
  display: flex;
  gap: 1rem;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.9rem;
}
.studio-heading h2 {
  margin: 0 0 0.25rem;
  font-size: 1rem;
}
.studio-heading p {
  margin: 0;
  color: var(--dim);
  font-size: 0.83rem;
  max-width: 62ch;
}
.studio-note {
  color: var(--teal);
  font-size: 0.72rem;
  border: 1px solid rgba(0,200,180,0.22);
  background: rgba(0,200,180,0.08);
  padding: 0.35rem 0.6rem;
  border-radius: 999px;
  white-space: nowrap;
}
.studio-form {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}
.studio-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.8rem;
}
.studio-field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  min-width: 0;
}
.studio-wide { grid-column: 1 / -1; }
.studio-field span {
  color: var(--dim);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.studio-field input,
.studio-field select,
.studio-field textarea {
  width: 100%;
  min-width: 0;
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border);
  color: var(--ink);
  border-radius: 10px;
  padding: 0.65rem 0.75rem;
  font: inherit;
  outline: none;
  transition: border-color 0.15s, background 0.15s;
  box-sizing: border-box;
}
.studio-field textarea {
  resize: vertical;
  min-height: 7rem;
}
.studio-field input:focus,
.studio-field select:focus,
.studio-field textarea:focus,
.studio-field input:hover,
.studio-field select:hover,
.studio-field textarea:hover {
  border-color: var(--accent);
  background: rgba(255,255,255,0.05);
}
.studio-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
  flex-wrap: wrap;
}
.studio-check {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: var(--dim);
  font-size: 0.8rem;
}
.studio-submit,
.studio-inline-btn {
  border: 1px solid rgba(0,200,180,0.28);
  background: rgba(0,200,180,0.13);
  color: var(--teal);
  border-radius: 10px;
  padding: 0.62rem 0.95rem;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.12s, border-color 0.12s, background 0.12s;
}
.studio-submit:hover,
.studio-inline-btn:hover {
  border-color: var(--teal);
  background: rgba(0,200,180,0.18);
  transform: translateY(-1px);
}
.studio-submit:disabled,
.studio-inline-btn:disabled {
  cursor: wait;
  opacity: 0.7;
  transform: none;
}
.studio-inline-btn {
  padding: 0.42rem 0.65rem;
}
.studio-status {
  min-height: 1.2rem;
  font-size: 0.82rem;
  color: var(--dim);
}
.studio-status-success { color: var(--ink); }
.studio-status-error { color: #ff8f8f; }
.studio-status-busy { color: var(--teal); }
.studio-status-info { color: var(--dim); }
.studio-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  margin-top: 0.55rem;
}
.studio-links a {
  color: var(--accent);
  text-decoration: none;
}
.studio-links a:hover { text-decoration: underline; }
.studio-hidden { display: none; }
.studio-disabled {
  opacity: 0.72;
  filter: grayscale(0.12);
}
.portal-actions-panel {
  margin: 0.8rem 1.5rem 0.9rem;
  padding: 0.9rem 1rem;
  border: 1px solid var(--border);
  border-radius: 14px;
  background: var(--surface);
}
.portal-actions-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.8rem;
}
.portal-actions-heading h2 {
  margin: 0;
  font-size: 1rem;
}
.portal-actions-note {
  color: var(--dim);
  font-size: 0.76rem;
}
.portal-actions-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 0.75rem;
  align-items: end;
}
.portal-actions-form label {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  min-width: 0;
}
.portal-actions-form label span {
  color: var(--dim);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.portal-actions-form input[type="text"],
.portal-actions-form select {
  width: 100%;
  min-width: 0;
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border);
  color: var(--ink);
  border-radius: 10px;
  padding: 0.58rem 0.68rem;
  font: inherit;
  box-sizing: border-box;
}
.portal-action-toggles {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: center;
  color: var(--dim);
  font-size: 0.78rem;
}
.portal-action-toggles label {
  flex-direction: row;
  align-items: center;
  gap: 0.35rem;
}
.portal-action-submit {
  border: 1px solid rgba(124,106,247,0.34);
  background: rgba(124,106,247,0.14);
  color: var(--accent);
  border-radius: 10px;
  padding: 0.62rem 0.95rem;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}
.portal-action-submit:disabled {
  cursor: wait;
  opacity: 0.7;
}
.portal-action-status {
  min-height: 1.2rem;
  margin-top: 0.75rem;
  color: var(--dim);
  font-size: 0.82rem;
}
.portal-action-status-error { color: #ff8f8f; }
.portal-action-status-busy { color: var(--teal); }
.portal-action-status-success { color: var(--ink); }
.portal-action-hidden { display: none !important; }
@media (max-width: 820px) {
  .studio-heading {
    flex-direction: column;
  }
  .portal-actions-heading {
    align-items: flex-start;
    flex-direction: column;
  }
  .studio-note {
    white-space: normal;
  }
}
</style>"""

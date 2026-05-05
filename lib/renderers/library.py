"""Master library viewer — all Rafiki images across all projects in one page."""

from __future__ import annotations

import json
import webbrowser
from datetime import datetime
from pathlib import Path

from lib.extra_outputs import load_extra_outputs
from lib.styles import get_default_style, load_styles
from lib.renderers.viewer import _shared_css, _lightbox_html, _lightbox_js


def _scan_root(root: Path, project_name: str, virtual_prefix: str) -> list[dict]:
    """Yield image records from all run-*/run.json files under root."""
    records: list[dict] = []
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
        for img in data.get("images", []):
            img_path = rjp.parent / img["file"]
            records.append({
                "project": project_name,
                "run_id": run_id,
                "model": model,
                "timestamp": timestamp,
                "aspect_ratio": aspect_ratio,
                "style": style,
                "name": img.get("name", ""),
                "prompt": img.get("prompt", ""),
                # virtual path used as img src — routed by server or via symlink
                "file": f"{virtual_prefix}/{run_id}/{img['file']}",
                "ok": img_path.exists(),
            })
    return records


def generate_library_viewer(output_root: Path, open_browser: bool = False) -> Path:
    """Scan output_root + any extra-outputs and build output_root/library.html."""
    output_root = Path(output_root)
    extra_roots = load_extra_outputs()

    # Scan extra_roots first (canonical sources); track virtual paths to
    # deduplicate — output/ may have symlinks or copies of the same run.
    seen: set[str] = set()
    records: list[dict] = []

    for project_name, extra_root in extra_roots.items():
        if not extra_root.exists():
            continue
        for rec in _scan_root(extra_root, project_name, project_name):
            seen.add(rec["file"])
            records.append(rec)

    for proj_dir in sorted(output_root.iterdir()):
        if not proj_dir.is_dir():
            continue
        for rec in _scan_root(proj_dir, proj_dir.name, proj_dir.name):
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


def _render_library(records: list[dict]) -> str:
    library_json = json.dumps(records, ensure_ascii=False)
    ok_count = sum(1 for r in records if r["ok"])
    projects = sorted({r["project"] for r in records})
    models = sorted({r["model"] for r in records if r["model"] not in ("unknown", "")})
    aspect_ratios = sorted({r["aspect_ratio"] for r in records if r.get("aspect_ratio")})
    styles = sorted({r["style"] for r in records if r.get("style") and r["style"] not in ("none", "")})
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

<div class="filter-bar" id="filter-bar">
  <button class="filter-btn active" id="fb-all"        onclick="setRatingFilter('all')">All <span id="fc-all"></span></button>
  <button class="filter-btn"        id="fb-star"       onclick="setRatingFilter('star')">&#9733; Starred <span id="fc-star"></span></button>
  <button class="filter-btn"        id="fb-reject"     onclick="setRatingFilter('reject')">&#x2715; Rejected <span id="fc-reject"></span></button>
  <button class="filter-btn"        id="fb-unreviewed" onclick="setRatingFilter('unreviewed')">Unreviewed <span id="fc-unreviewed"></span></button>
  <input id="search" type="text" placeholder="Search prompts…" autocomplete="off"
         oninput="_searchQuery=this.value.toLowerCase().trim();applyFilters()">
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
</div>

<div class="grid" id="grid"></div>

{_lightbox_html()}

<script>
const LIBRARY = {library_json};
const ITEMS = LIBRARY;
const RATINGS_KEY = 'rafiki:ratings';
const SERVER_MODE = location.protocol !== 'file:';
let _ratingFilter = 'all';
let _projFilter = null;
let _modelFilter = null;
let _arFilter = null;
let _styleFilter = null;
let _searchQuery = '';

function _loadRatings() {{
  try {{ return JSON.parse(localStorage.getItem(RATINGS_KEY) || '{{}}'); }} catch(e) {{ return {{}}; }}
}}
function _saveRatings(r) {{ localStorage.setItem(RATINGS_KEY, JSON.stringify(r)); }}
function studioEscapeHtml(value) {{
  return String(value || '').replace(/[&<>"]/g, ch => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[ch]));
}}
function getRating(key) {{ return _loadRatings()[key] || null; }}
function setRating(key, val) {{
  const r = _loadRatings();
  if (r[key] === val) delete r[key]; else r[key] = val;
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
    if (show && _searchQuery)  show = (card.dataset.search || '').includes(_searchQuery);
    card.classList.toggle('hidden-filter', !show);
  }});
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
  if (!SERVER_MODE) {{
    document.getElementById('studio-panel')?.classList.add('studio-disabled');
    document.querySelectorAll('#studio-form input, #studio-form textarea, #studio-form select, #studio-form button').forEach(el => {{
      el.disabled = true;
    }});
    setStudioStatus('info', 'Prompt Studio requires <code>python generate.py serve</code>. File-based viewers are read-only.');
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
  card.dataset.ts = item.timestamp || '';
  card.dataset.name = item.name || '';
  card.dataset.search = ((item.name || '') + ' ' + (item.prompt || '') + ' ' + (item.project || '')).toLowerCase();
  card.onclick = () => lbOpen(i);
  card.innerHTML = `
    <div class="img-wrap" style="aspect-ratio:${{arCss}}">
      <span class="img-num">${{String(i + 1).padStart(2, '0')}}</span>
      ${{item.ok
        ? '<img src="' + item.file + '" alt="" loading="lazy">'
        : '<div class="missing-img">not generated</div>'}}
    </div>
    <div class="card-prompt"></div>
    <div class="card-foot">
      <span class="card-name">${{item.name}}</span>
      <span class="proj-badge">${{item.project.replace(/-/g, ' ')}}</span>
      <button class="btn-rate star"   onclick="rateCard(event,'${{item.file}}','star',  this.closest('.card'))">&#9733;</button>
      <button class="btn-rate reject" onclick="rateCard(event,'${{item.file}}','reject',this.closest('.card'))">&#x2715;</button>
    </div>
  `;
  card.querySelector('.card-prompt').textContent = item.prompt || '';
  const img = card.querySelector('img');
  if (img) img.addEventListener('error', () => {{
    img.closest('.img-wrap').innerHTML = '<div class="missing-img">file missing</div>';
  }});
  grid.appendChild(card);
  applyRating(card, item.file);
}});
updateFilterCounts();

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
@media (max-width: 820px) {
  .studio-heading {
    flex-direction: column;
  }
  .studio-note {
    white-space: normal;
  }
}
</style>"""

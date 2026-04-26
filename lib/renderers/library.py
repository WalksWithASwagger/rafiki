"""Master library viewer — all Rafiki images across all projects in one page."""

from __future__ import annotations

import json
import webbrowser
from datetime import datetime
from pathlib import Path

from lib.renderers.viewer import _shared_css, _lightbox_html, _lightbox_js


def generate_library_viewer(output_root: Path, open_browser: bool = False) -> Path:
    """Scan output_root/*/run-*/run.json and build output_root/library.html."""
    output_root = Path(output_root)

    records: list[dict] = []
    for rjp in sorted(output_root.glob("*/run-*/run.json")):
        try:
            data = json.loads(rjp.read_text(encoding="utf-8"))
        except Exception:
            continue
        project = rjp.parent.parent.name
        run_id = rjp.parent.name
        model = data.get("model", "unknown")
        timestamp = data.get("timestamp", "")
        aspect_ratio = data.get("aspect_ratio", "16:9")

        for img in data.get("images", []):
            img_path = rjp.parent / img["file"]
            try:
                rel = str(img_path.relative_to(output_root))
            except ValueError:
                rel = img["file"]
            records.append({
                "project": project,
                "run_id": run_id,
                "model": model,
                "timestamp": timestamp,
                "aspect_ratio": aspect_ratio,
                "name": img.get("name", ""),
                "prompt": img.get("prompt", ""),
                "file": rel,
                "ok": img_path.exists(),
            })

    records.sort(key=lambda r: r["timestamp"], reverse=True)

    html = _render_library(records)
    out_path = output_root / "library.html"
    out_path.write_text(html, encoding="utf-8")

    if open_browser:
        webbrowser.open(out_path.as_uri())

    return out_path


def _render_library(records: list[dict]) -> str:
    library_json = json.dumps(records, ensure_ascii=False)
    ok_count = sum(1 for r in records if r["ok"])
    projects = sorted({r["project"] for r in records})
    models = sorted({r["model"] for r in records if r["model"] not in ("unknown", "")})
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

<div class="filter-bar" id="filter-bar">
  <button class="filter-btn active" id="fb-all"        onclick="setRatingFilter('all')">All <span id="fc-all"></span></button>
  <button class="filter-btn"        id="fb-star"       onclick="setRatingFilter('star')">&#9733; Starred <span id="fc-star"></span></button>
  <button class="filter-btn"        id="fb-reject"     onclick="setRatingFilter('reject')">&#x2715; Rejected <span id="fc-reject"></span></button>
  <button class="filter-btn"        id="fb-unreviewed" onclick="setRatingFilter('unreviewed')">Unreviewed <span id="fc-unreviewed"></span></button>
  <span class="chip-sep">|</span>
  {project_chips}
  <span class="chip-sep">|</span>
  {model_chips}
  <label class="grid-size-label">Grid <input type="range" min="160" max="560" value="280" id="grid-sizer" oninput="resizeGrid(this.value)"></label>
</div>

<div class="grid" id="grid"></div>

{_lightbox_html()}

<script>
const LIBRARY = {library_json};
const ITEMS = LIBRARY;
const RATINGS_KEY = 'rafiki:lib:ratings';
let _ratingFilter = 'all';
let _projFilter = null;
let _modelFilter = null;

function _loadRatings() {{
  try {{ return JSON.parse(localStorage.getItem(RATINGS_KEY) || '{{}}'); }} catch(e) {{ return {{}}; }}
}}
function _saveRatings(r) {{ localStorage.setItem(RATINGS_KEY, JSON.stringify(r)); }}
function getRating(key) {{ return _loadRatings()[key] || null; }}
function setRating(key, val) {{
  const r = _loadRatings();
  if (r[key] === val) delete r[key]; else r[key] = val;
  _saveRatings(r);
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
    const wasActive = _projFilter === val;
    document.querySelectorAll('.chip-proj').forEach(b => b.classList.remove('active'));
    _projFilter = wasActive ? null : val;
    if (!wasActive) document.querySelector('.chip-proj[data-proj="' + val + '"]')?.classList.add('active');
  }} else {{
    const wasActive = _modelFilter === val;
    document.querySelectorAll('.chip-model').forEach(b => b.classList.remove('active'));
    _modelFilter = wasActive ? null : val;
    if (!wasActive) document.querySelector('.chip-model[data-model="' + val + '"]')?.classList.add('active');
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
    if (show && _projFilter)  show = card.dataset.project === _projFilter;
    if (show && _modelFilter) show = card.dataset.model === _modelFilter;
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
(function() {{
  const saved = localStorage.getItem('rafiki:cardWidth');
  if (saved) {{ resizeGrid(saved); const sl = document.getElementById('grid-sizer'); if (sl) sl.value = saved; }}
}})();

const grid = document.getElementById('grid');
LIBRARY.forEach((item, i) => {{
  const arCss = (item.aspect_ratio || '16:9').replace(':', '/');
  const card = document.createElement('div');
  card.className = 'card';
  card.dataset.ratingKey = item.file;
  card.dataset.project = item.project;
  card.dataset.model = item.model;
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
</style>"""

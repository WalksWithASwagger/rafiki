from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def generate_viewer(
    output_dir: Path,
    items: list[dict],
    title: str = "Rafiki — Image Batch",
    run_meta: dict | None = None,
) -> Path:
    """Generate a single-run HTML viewer alongside the batch output images."""
    output_dir = Path(output_dir)
    meta = run_meta or {}

    timestamp = meta.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M"))
    model = meta.get("model", "—")
    aspect_ratio = meta.get("aspect_ratio", "16:9")
    style = meta.get("style", "—")
    prompt_file = meta.get("prompt_file", "")

    js_items = []
    for item in items:
        out = Path(item.get("output_path", ""))
        try:
            rel = str(out.relative_to(output_dir))
        except ValueError:
            rel = out.name
        js_items.append({
            "name": item.get("name", "Untitled"),
            "prompt": item.get("prompt", ""),
            "file": rel,
            "ok": out.exists(),
            "aspect_ratio": item.get("aspect_ratio") or aspect_ratio,
            "error": item.get("error", ""),
        })

    project = output_dir.parent.name
    run_id = output_dir.name
    html = _render_single(title, js_items, model, aspect_ratio, style, timestamp, prompt_file, project, run_id)
    viewer_path = output_dir / "viewer.html"
    viewer_path.write_text(html, encoding="utf-8")
    return viewer_path


def generate_comparison_viewer(project_dir: Path) -> Path:
    """Scan all run-* subdirs and generate a multi-run comparison viewer."""
    project_dir = Path(project_dir)

    run_json_paths = sorted(project_dir.glob("run-*/run.json"))
    runs = []
    for rjp in run_json_paths:
        try:
            data = json.loads(rjp.read_text(encoding="utf-8"))
            # Re-verify file existence at render time — don't trust run.json ok field
            images = []
            for img in data.get("images", []):
                img_path = rjp.parent / img["file"]
                images.append({**img, "ok": img_path.exists()})
            runs.append({
                "id": rjp.parent.name,
                "dir": rjp.parent.name,
                "timestamp": data.get("timestamp", ""),
                "model": data.get("model", ""),
                "style": data.get("style", "none"),
                "aspect_ratio": data.get("aspect_ratio", "16:9"),
                "prompt_file": data.get("prompt_file", ""),
                "images": images,
            })
        except Exception:
            continue

    title = project_dir.name.replace("-", " ").replace("_", " ").title()
    project = project_dir.name
    html = _render_comparison(title, runs, project)
    viewer_path = project_dir / "viewer.html"
    viewer_path.write_text(html, encoding="utf-8")
    return viewer_path


# ─── aspect ratio → CSS helper ───────────────────────────────────────────────

def _ar_css(ar: str) -> str:
    return ar.replace(":", "/") if ar else "16/9"


# ─── Single-run renderer ─────────────────────────────────────────────────────

def _render_single(
    title: str,
    items: list[dict],
    model: str,
    aspect_ratio: str,
    style: str,
    timestamp: str,
    prompt_file: str,
    project: str = "",
    run_id: str = "",
) -> str:
    items_json = json.dumps(items, ensure_ascii=False)
    count = len(items)
    ar_css = _ar_css(aspect_ratio)
    source_line = f"<code>{prompt_file}</code> · " if prompt_file else ""
    project_js = json.dumps(project)
    run_id_js = json.dumps(run_id)
    model_js = json.dumps(model)
    style_js = json.dumps(style)
    ar_js = json.dumps(aspect_ratio)
    ts_js = json.dumps(timestamp)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
{_shared_css(ar_css)}
</head>
<body>
<header>
  <h1>{title}</h1>
  <div class="meta">
    <span class="pill">{count} image{'' if count == 1 else 's'}</span>
    <span><code>{model}</code></span>
    <span><code>{aspect_ratio}</code></span>
    <span><code>{style}</code></span>
    <span>{source_line}{timestamp}</span>
  </div>
</header>

{_filter_bar_html()}
<div class="grid" id="grid"></div>

{_lightbox_html()}

<script>
const ITEMS = {items_json};
const AR_CSS = "{ar_css}";
const PROJECT = {project_js};
const RUN_ID = {run_id_js};
const MODEL = {model_js};
const STYLE = {style_js};
const AR = {ar_js};
const TIMESTAMP = {ts_js};
{_rating_js()}
{_grid_js()}
{_lightbox_js()}
</script>
</body>
</html>"""


# ─── Comparison renderer ──────────────────────────────────────────────────────

def _render_comparison(title: str, runs: list[dict], project: str = "") -> str:
    runs_json = json.dumps(runs, ensure_ascii=False)
    run_count = len(runs)
    ar_css = _ar_css(runs[-1]["aspect_ratio"]) if runs else "16/9"
    project_js = json.dumps(project)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — Rafiki</title>
{_shared_css(ar_css)}
<style>
.run-tabs {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  padding: 0.6rem 1.5rem;
  border-bottom: 1px solid var(--border);
  background: rgba(0,0,0,0.15);
  align-items: center;
}}
.run-tab {{
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--dim);
  padding: 0.28rem 0.75rem;
  border-radius: 20px;
  font-size: 0.78rem;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
  user-select: none;
}}
.run-tab:hover {{ border-color: var(--accent); color: var(--ink); }}
.run-tab.active {{ background: rgba(124,106,247,0.2); border-color: var(--accent); color: var(--accent); font-weight: 600; }}
.run-tab.compare-btn {{
  margin-left: auto;
  background: rgba(0,200,180,0.08);
  border-color: rgba(0,200,180,0.3);
  color: var(--teal);
}}
.run-tab.compare-btn.active {{
  background: rgba(0,200,180,0.2);
  border-color: var(--teal);
}}
/* Compare table */
.compare-table {{ display: none; padding: 1.5rem 1.5rem 4rem; overflow-x: auto; }}
.compare-table.visible {{ display: block; }}
.compare-label {{
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--ink);
  padding: 0.75rem 0 0.4rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 0.6rem;
}}
.compare-row {{
  display: grid;
  gap: 0.75rem;
  margin-bottom: 1.75rem;
  align-items: start;
}}
.compare-cell {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.15s, transform 0.15s;
}}
.compare-cell:hover {{ border-color: var(--accent); transform: translateY(-2px); }}
.compare-cell .run-badge {{
  font-size: 0.68rem;
  color: var(--accent);
  padding: 0.3rem 0.6rem 0.2rem;
  font-weight: 600;
  font-family: ui-monospace, monospace;
}}
.no-runs {{ padding: 4rem; text-align: center; color: var(--dim); }}
</style>
</head>
<body>

<header>
  <h1>{title}</h1>
  <div class="meta">
    <span class="pill" id="run-pill">{run_count} run{'' if run_count == 1 else 's'}</span>
    <span id="cur-model"></span>
    <span id="cur-ts"></span>
  </div>
</header>

<div class="run-tabs" id="run-tabs">
  <button class="run-tab compare-btn" id="compare-btn" onclick="toggleCompare()">⊞ Compare all</button>
</div>

{_filter_bar_html()}
<div class="grid" id="grid"></div>
<div class="compare-table" id="compare-table"></div>

{_lightbox_html()}

<script>
const RUNS = {runs_json};
const AR_CSS = "{ar_css}";
const PROJECT = {project_js};
let currentRun = RUNS.length - 1;
let compareMode = false;

{_rating_js()}
{_lightbox_js()}
{_comparison_js()}
init();
</script>
</body>
</html>"""


# ─── Shared CSS ───────────────────────────────────────────────────────────────

def _shared_css(ar_css: str = "16/9") -> str:
    return f"""<style>
:root {{
  --bg:      #0d0b18;
  --bg2:     #171428;
  --surface: rgba(255,255,255,0.045);
  --border:  #252040;
  --ink:     #edeaff;
  --dim:     #8a86b0;
  --accent:  #7c6af7;
  --teal:    #00c8b4;
  --gold:    #f5c518;
  --card-w:  280px;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  background: var(--bg);
  color: var(--ink);
  font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
  line-height: 1.5;
  min-height: 100vh;
}}

/* ── Header ── */
header {{
  padding: 1.25rem 1.5rem 1rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: baseline;
  gap: 1.5rem;
  flex-wrap: wrap;
}}
header h1 {{
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  background: linear-gradient(90deg, var(--accent), var(--teal));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  white-space: nowrap;
}}
.meta {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem 1rem;
  font-size: 0.8rem;
  color: var(--dim);
  align-items: center;
}}
.meta code {{
  background: rgba(255,255,255,0.07);
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  font-size: 0.75rem;
  color: var(--teal);
  font-family: ui-monospace, monospace;
}}
.pill {{
  background: rgba(124,106,247,0.15);
  border: 1px solid rgba(124,106,247,0.3);
  color: var(--accent);
  padding: 0.1rem 0.5rem;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 700;
}}

/* ── Filter bar ── */
.filter-bar {{
  display: flex;
  gap: 0.35rem;
  padding: 0.6rem 1.5rem;
  flex-wrap: wrap;
  align-items: center;
  border-bottom: 1px solid var(--border);
}}
.filter-btn {{
  background: none;
  border: 1px solid var(--border);
  color: var(--dim);
  padding: 0.22rem 0.65rem;
  border-radius: 20px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
  user-select: none;
}}
.filter-btn:hover {{ border-color: var(--accent); color: var(--ink); }}
.filter-btn.active {{ background: rgba(124,106,247,0.18); border-color: var(--accent); color: var(--accent); font-weight: 600; }}
.grid-size-label {{
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.72rem;
  color: var(--dim);
  user-select: none;
}}
#grid-sizer {{ width: 80px; accent-color: var(--accent); cursor: pointer; }}

/* ── Grid ── */
.grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(var(--card-w), 1fr));
  gap: 1.25rem;
  padding: 1.25rem 1.5rem 4rem;
}}

/* ── Card ── */
.card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.15s, border-color 0.15s, box-shadow 0.15s;
  display: flex;
  flex-direction: column;
}}
.card:hover {{
  transform: translateY(-3px);
  border-color: var(--accent);
  box-shadow: 0 8px 32px rgba(124,106,247,0.2);
}}
.card.rated-star   {{ border-color: var(--gold) !important; box-shadow: 0 0 20px rgba(245,197,24,0.2); }}
.card.rated-reject {{ opacity: 0.38; }}
.card.hidden-filter {{ display: none !important; }}

/* ── Image wrapper ── */
.img-wrap {{
  position: relative;
  width: 100%;
  aspect-ratio: {ar_css};
  background: #080612;
  overflow: hidden;
  flex-shrink: 0;
}}
.img-wrap img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.3s ease;
}}
.card:hover .img-wrap img {{ transform: scale(1.03); }}
.img-num {{
  position: absolute;
  top: 0.4rem;
  left: 0.4rem;
  background: rgba(0,0,0,0.6);
  color: rgba(255,255,255,0.8);
  font-size: 0.65rem;
  font-weight: 700;
  font-family: ui-monospace, monospace;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  backdrop-filter: blur(4px);
  user-select: none;
}}
.missing-img {{
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--dim);
  font-size: 0.75rem;
  opacity: 0.5;
  padding: 0.5rem;
  text-align: center;
}}

/* ── Card prompt ── */
.card-prompt {{
  padding: 0.55rem 0.75rem 0.4rem;
  font-size: 0.72rem;
  color: var(--dim);
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
  border-top: 1px solid var(--border);
}}

/* ── Card footer ── */
.card-foot {{
  padding: 0.4rem 0.65rem 0.4rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  border-top: 1px solid var(--border);
  flex-shrink: 0;
}}
.card-name {{
  flex: 1;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
.btn-rate {{
  background: none;
  border: 1px solid rgba(255,255,255,0.1);
  color: var(--dim);
  font-size: 0.72rem;
  padding: 0.15rem 0.45rem;
  border-radius: 10px;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
  white-space: nowrap;
  flex-shrink: 0;
}}
.btn-rate:hover {{ border-color: rgba(255,255,255,0.25); color: var(--ink); }}
.btn-rate.starred  {{ background: rgba(245,197,24,0.15); border-color: var(--gold); color: var(--gold); }}
.btn-rate.rejected {{ background: rgba(255,60,60,0.1); border-color: rgba(255,80,80,0.5); color: #ff6060; }}

/* ── Lightbox ── */
.lb {{
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.97);
  z-index: 9000;
  flex-direction: column;
  align-items: center;
}}
.lb.open {{ display: flex; }}

.lb-top {{
  position: fixed;
  top: 0; left: 0; right: 0;
  padding: 0.75rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(to bottom, rgba(0,0,0,0.8), transparent);
  z-index: 9001;
}}
.lb-counter {{
  font-size: 0.82rem;
  color: rgba(255,255,255,0.6);
  font-variant-numeric: tabular-nums;
}}
.lb-top-actions {{
  display: flex;
  gap: 0.5rem;
  align-items: center;
}}
.lb-close {{
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.15);
  color: #fff;
  font-size: 1.1rem;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
  line-height: 1;
}}
.lb-close:hover {{ background: rgba(255,255,255,0.22); }}
.lb-action-btn {{
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  color: rgba(255,255,255,0.75);
  font-size: 0.76rem;
  padding: 0.25rem 0.7rem;
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  white-space: nowrap;
  font-family: inherit;
}}
.lb-action-btn:hover {{ background: rgba(255,255,255,0.16); color: #fff; border-color: rgba(255,255,255,0.3); }}
.lb-action-btn.copied {{ border-color: var(--teal); color: var(--teal); }}

.lb-img-area {{
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  flex: 1;
  padding: 3.5rem 5rem 0.5rem;
  min-height: 0;
}}
.lb-img-area img {{
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 6px;
  box-shadow: 0 20px 80px rgba(0,0,0,0.9);
  display: block;
}}
.lb-arrow {{
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
  color: #fff;
  font-size: 1.2rem;
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
  user-select: none;
  z-index: 2;
  line-height: 1;
}}
.lb-arrow:hover {{ background: rgba(255,255,255,0.18); }}
.lb-arrow.prev {{ left: 1rem; }}
.lb-arrow.next {{ right: 1rem; }}

.lb-bottom {{
  width: 100%;
  max-width: 900px;
  padding: 0.6rem 1.5rem 1rem;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}}
.lb-name {{
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--ink);
}}
.lb-prompt {{
  font-size: 0.78rem;
  color: var(--dim);
  line-height: 1.6;
  max-height: 7rem;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--border) transparent;
}}

/* ── Lightbox meta ── */
.lb-meta {{
  font-size: 0.7rem;
  color: var(--dim);
  font-family: ui-monospace, monospace;
  opacity: 0.75;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}

/* ── Search + sort ── */
#search {{
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
}}
#search:focus, #search:hover {{ border-color: var(--accent); }}
#search::placeholder {{ color: var(--dim); opacity: 0.6; }}
.sort-select {{
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--dim);
  padding: 0.22rem 0.5rem;
  border-radius: 6px;
  font-size: 0.75rem;
  cursor: pointer;
  font-family: inherit;
  outline: none;
}}
.sort-select:focus, .sort-select:hover {{ border-color: var(--accent); color: var(--ink); }}

/* ── Run strip (compare lightbox) ── */
.lb-run-strip {{
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
  justify-content: center;
  padding: 0 1.5rem 0.75rem;
  flex-shrink: 0;
}}
.lb-run-dot {{
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
  color: var(--dim);
  padding: 0.18rem 0.55rem;
  border-radius: 12px;
  font-size: 0.7rem;
  cursor: pointer;
  transition: border-color 0.12s, color 0.12s, background 0.12s;
}}
.lb-run-dot:hover {{ border-color: var(--teal); color: var(--teal); }}
.lb-run-dot.active {{ background: rgba(0,200,180,0.18); border-color: var(--teal); color: var(--teal); font-weight: 600; }}
</style>"""


def _filter_bar_html() -> str:
    return """<div class="filter-bar" id="filter-bar">
  <button class="filter-btn active" id="fb-all"        onclick="filterCards('all')">All <span id="fc-all"></span></button>
  <button class="filter-btn"        id="fb-star"       onclick="filterCards('star')">&#9733; Starred <span id="fc-star"></span></button>
  <button class="filter-btn"        id="fb-reject"     onclick="filterCards('reject')">&#x2715; Rejected <span id="fc-reject"></span></button>
  <button class="filter-btn"        id="fb-unreviewed" onclick="filterCards('unreviewed')">Unreviewed <span id="fc-unreviewed"></span></button>
  <input id="search" type="text" placeholder="Search prompts…" autocomplete="off"
         oninput="_searchQuery=this.value.toLowerCase().trim();applyFilters()">
  <label class="grid-size-label">
    <select class="sort-select" onchange="applySort(this.value)">
      <option value="default">⇅ Order</option>
      <option value="name">A → Z</option>
    </select>
    Grid <input type="range" min="160" max="560" value="280" id="grid-sizer" oninput="resizeGrid(this.value)">
  </label>
</div>"""


def _lightbox_html() -> str:
    return """<div class="lb" id="lb" onclick="lbClickBg(event)">
  <div class="lb-top">
    <span class="lb-counter" id="lb-counter"></span>
    <div class="lb-top-actions">
      <a id="lb-download" class="lb-action-btn" download="">&#11015; Download</a>
      <button id="lb-copy" class="lb-action-btn" onclick="lbCopyPrompt(); event.stopPropagation()">&#x2398; Copy prompt</button>
      <button class="lb-close" onclick="lbClose()" title="Close (Esc)">&#x2715;</button>
    </div>
  </div>
  <div class="lb-img-area" onclick="event.stopPropagation()">
    <button class="lb-arrow prev" onclick="lbStep(-1); event.stopPropagation()">&#8592;</button>
    <img id="lb-img" src="" alt="">
    <button class="lb-arrow next" onclick="lbStep(1); event.stopPropagation()">&#8594;</button>
  </div>
  <div class="lb-bottom" onclick="event.stopPropagation()">
    <div class="lb-name" id="lb-name"></div>
    <div class="lb-meta" id="lb-meta"></div>
    <div class="lb-prompt" id="lb-prompt"></div>
  </div>
  <div class="lb-run-strip" id="lb-run-strip"></div>
</div>"""


def _rating_js() -> str:
    return """
const RATINGS_KEY = 'rafiki:ratings';
const SERVER_MODE = location.protocol !== 'file:';
let _currentFilter = 'all';
let _searchQuery = '';

function resizeGrid(v) {
  document.documentElement.style.setProperty('--card-w', v + 'px');
  localStorage.setItem('rafiki:cardWidth', v);
}
(function() {
  const saved = localStorage.getItem('rafiki:cardWidth');
  if (saved) { resizeGrid(saved); const sl = document.getElementById('grid-sizer'); if (sl) sl.value = saved; }
})();

function _loadRatings() {
  try { return JSON.parse(localStorage.getItem(RATINGS_KEY) || '{}'); } catch(e) { return {}; }
}
function _saveRatings(r) { localStorage.setItem(RATINGS_KEY, JSON.stringify(r)); }
function getRating(key) { return _loadRatings()[key] || null; }
function setRating(key, val) {
  const r = _loadRatings();
  if (r[key] === val) delete r[key]; else r[key] = val;
  _saveRatings(r);
  if (SERVER_MODE) {
    fetch('/api/ratings', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({key, value: r[key] !== undefined ? r[key] : null}),
    }).catch(() => {});
  }
}
function applyRating(card, key) {
  const val = getRating(key);
  card.classList.remove('rated-star', 'rated-reject');
  if (val === 'star')   card.classList.add('rated-star');
  if (val === 'reject') card.classList.add('rated-reject');
  const btnS = card.querySelector('.btn-rate.star');
  const btnR = card.querySelector('.btn-rate.reject');
  if (btnS) btnS.classList.toggle('starred',  val === 'star');
  if (btnR) btnR.classList.toggle('rejected', val === 'reject');
}
function rateCard(e, key, val, card) {
  e.stopPropagation();
  setRating(key, val);
  applyRating(card, key);
  updateFilterCounts();
  if (_currentFilter !== 'all' || _searchQuery) applyFilters();
}
function filterCards(mode) {
  _currentFilter = mode;
  document.querySelectorAll('.filter-btn[id^="fb-"]').forEach(b => b.classList.remove('active'));
  const a = document.getElementById('fb-' + mode);
  if (a) a.classList.add('active');
  applyFilters();
}
function applyFilters() {
  const ratings = _loadRatings();
  document.querySelectorAll('.card').forEach(card => {
    const val = ratings[card.dataset.ratingKey] || null;
    let show = true;
    if (_currentFilter === 'star')            show = val === 'star';
    else if (_currentFilter === 'reject')     show = val === 'reject';
    else if (_currentFilter === 'unreviewed') show = !val;
    if (show && _searchQuery) show = (card.dataset.search || '').includes(_searchQuery);
    card.classList.toggle('hidden-filter', !show);
  });
}
function updateFilterCounts() {
  const ratings = _loadRatings();
  const cards = Array.from(document.querySelectorAll('.card'));
  let stars = 0, rejects = 0, unreviewed = 0;
  cards.forEach(c => {
    const v = ratings[c.dataset.ratingKey] || null;
    if (v === 'star') stars++; else if (v === 'reject') rejects++; else unreviewed++;
  });
  const set = (id, n) => { const el = document.getElementById(id); if (el) el.textContent = n ? ` ${n}` : ''; };
  set('fc-all', cards.length); set('fc-star', stars);
  set('fc-reject', rejects); set('fc-unreviewed', unreviewed);
}
function applySort(mode) {
  const grid = document.getElementById('grid');
  if (!grid) return;
  const cards = Array.from(grid.querySelectorAll('.card'));
  if (mode === 'default') {
    cards.sort((a, b) => (parseInt(a.dataset.idx) || 0) - (parseInt(b.dataset.idx) || 0));
  } else if (mode === 'name') {
    cards.sort((a, b) => (a.dataset.name || '').localeCompare(b.dataset.name || ''));
  } else if (mode === 'newest') {
    cards.sort((a, b) => (b.dataset.ts || '').localeCompare(a.dataset.ts || ''));
  } else if (mode === 'oldest') {
    cards.sort((a, b) => (a.dataset.ts || '').localeCompare(b.dataset.ts || ''));
  } else if (mode === 'project') {
    cards.sort((a, b) => (a.dataset.project || '').localeCompare(b.dataset.project || ''));
  } else if (mode === 'model') {
    cards.sort((a, b) => (a.dataset.model || '').localeCompare(b.dataset.model || ''));
  }
  cards.forEach(c => grid.appendChild(c));
}
if (SERVER_MODE) {
  fetch('/api/ratings').then(r => r.json()).then(sv => {
    const merged = Object.assign(_loadRatings(), sv);
    _saveRatings(merged);
    document.querySelectorAll('.card').forEach(c => {
      if (c.dataset.ratingKey) applyRating(c, c.dataset.ratingKey);
    });
    updateFilterCounts();
  }).catch(() => {});
}
"""


def _lightbox_js() -> str:
    return """
var lbIdx = 0;
var lbItems = typeof ITEMS !== 'undefined' ? ITEMS : [];
var lbRunIdx = -1;
const lb        = document.getElementById('lb');
const lbImg     = document.getElementById('lb-img');
const lbName    = document.getElementById('lb-name');
const lbPrompt  = document.getElementById('lb-prompt');
const lbStrip   = document.getElementById('lb-run-strip');
const lbCounter = document.getElementById('lb-counter');

function lbOpen(i, runIdx) {
  if (typeof runIdx !== 'undefined') lbRunIdx = runIdx;
  lbIdx = ((i % lbItems.length) + lbItems.length) % lbItems.length;
  const item = lbItems[lbIdx];
  const prefix = (lbRunIdx >= 0 && typeof RUNS !== 'undefined')
    ? RUNS[lbRunIdx].dir + '/' : '';
  const rawImgSrc = prefix + item.file;
  const imgSrc = typeof resolveAssetSrc === 'function'
    ? resolveAssetSrc(rawImgSrc)
    : rawImgSrc;
  lbImg.src = imgSrc;
  lbImg.alt = item.name || '';
  lbName.textContent = item.name || '';
  lbPrompt.textContent = item.prompt || '';
  if (lbCounter) lbCounter.textContent = `${lbIdx + 1} / ${lbItems.length}`;
  const metaEl = document.getElementById('lb-meta');
  if (metaEl) {
    const run = (typeof RUNS !== 'undefined' && lbRunIdx >= 0) ? RUNS[lbRunIdx] : null;
    const m = item.model || (run ? run.model : '') || (typeof MODEL !== 'undefined' ? MODEL : '');
    const s = item.style || (run ? run.style : '') || (typeof STYLE !== 'undefined' ? STYLE : '');
    const ar = item.aspect_ratio || (run ? run.aspect_ratio : '') || (typeof AR !== 'undefined' ? AR : '');
    const ts = item.timestamp || (run ? run.timestamp : '') || (typeof TIMESTAMP !== 'undefined' ? TIMESTAMP : '');
    const proj = item.project || (typeof PROJECT !== 'undefined' ? PROJECT : '');
    const rid = item.run_id || (run ? run.dir : '') || (typeof RUN_ID !== 'undefined' ? RUN_ID : '');
    const parts = [m, s && s !== 'none' ? s : '', ar, (ts || '').slice(0, 16), proj && rid ? proj + '/' + rid : (proj || rid)].filter(Boolean);
    metaEl.textContent = parts.join('  ·  ');
  }

  const dlBtn = document.getElementById('lb-download');
  if (dlBtn) {
    dlBtn.href = imgSrc;
    dlBtn.download = (item.name || 'image').replace(/[^a-z0-9]+/gi, '-').toLowerCase() + '.png';
  }

  _buildRunStrip(lbIdx);
  lb.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function _buildRunStrip(slotIdx) {
  if (!lbStrip) return;
  lbStrip.innerHTML = '';
  if (typeof RUNS === 'undefined' || RUNS.length <= 1) return;
  RUNS.forEach((run, ri) => {
    const dot = document.createElement('button');
    dot.className = 'lb-run-dot' + (ri === lbRunIdx ? ' active' : '');
    dot.textContent = `${run.model || 'Run ' + (ri+1)} · ${run.timestamp}`;
    dot.onclick = (e) => {
      e.stopPropagation();
      lbRunIdx = ri;
      lbItems = run.images;
      lbOpen(slotIdx, ri);
    };
    lbStrip.appendChild(dot);
  });
}

function lbCopyPrompt() {
  const text = document.getElementById('lb-prompt')?.textContent || '';
  if (!text) return;
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.getElementById('lb-copy');
    if (!btn) return;
    const orig = btn.innerHTML;
    btn.innerHTML = '&#x2713; Copied!';
    btn.classList.add('copied');
    setTimeout(() => { btn.innerHTML = orig; btn.classList.remove('copied'); }, 2000);
  });
}

function lbClose() {
  lb.classList.remove('open');
  document.body.style.overflow = '';
}
function lbStep(dir) {
  event.stopPropagation();
  lbOpen(lbIdx + dir);
}
function lbClickBg(e) { if (e.target === lb) lbClose(); }

document.addEventListener('keydown', e => {
  if (!lb.classList.contains('open')) return;
  if (e.key === 'Escape')     { lbClose(); return; }
  if (e.key === 'ArrowLeft')  { lbOpen(lbIdx - 1); return; }
  if (e.key === 'ArrowRight') { lbOpen(lbIdx + 1); return; }
});
"""


def _grid_js() -> str:
    return """
const grid = document.getElementById('grid');
ITEMS.forEach((item, i) => {
  const rk = PROJECT + '/' + RUN_ID + '/' + item.file;
  const card = document.createElement('div');
  card.className = 'card';
  card.dataset.ratingKey = rk;
  card.dataset.idx = i;
  card.dataset.name = item.name || '';
  card.dataset.search = ((item.name || '') + ' ' + (item.prompt || '')).toLowerCase();
  card.onclick = () => lbOpen(i);

  const arCss = (item.aspect_ratio || '16:9').replace(':', '/');
  const missingMsg = item.error
    ? item.error.replace(/[<>&"]/g, '').slice(0, 80)
    : 'not generated';

  card.innerHTML = `
    <div class="img-wrap" style="aspect-ratio:${arCss}">
      <span class="img-num">${String(i + 1).padStart(2, '0')}</span>
      ${item.ok
        ? `<img src="${item.file}" alt="" loading="lazy">`
        : `<div class="missing-img">${missingMsg}</div>`}
    </div>
    <div class="card-prompt"></div>
    <div class="card-foot">
      <span class="card-name">${item.name}</span>
      <button class="btn-rate star"   onclick="rateCard(event,'${rk}','star',  this.closest('.card'))">&#9733;</button>
      <button class="btn-rate reject" onclick="rateCard(event,'${rk}','reject',this.closest('.card'))">&#x2715;</button>
    </div>
  `;
  card.querySelector('.card-prompt').textContent = item.prompt || '';
  const img = card.querySelector('img');
  if (img) img.addEventListener('error', () => {
    img.closest('.img-wrap').innerHTML = '<div class="missing-img">file missing</div>';
  });
  grid.appendChild(card);
  applyRating(card, rk);
});
updateFilterCounts();
"""


def _comparison_js() -> str:
    return """
function init() {
  if (!RUNS.length) {
    document.getElementById('grid').innerHTML = '<div style="padding:4rem;text-align:center;color:var(--dim)">No runs found.</div>';
    return;
  }
  const tabsEl = document.getElementById('run-tabs');
  const compareBtn = document.getElementById('compare-btn');
  RUNS.forEach((run, ri) => {
    const tab = document.createElement('button');
    tab.className = 'run-tab' + (ri === currentRun ? ' active' : '');
    tab.textContent = `${run.model || 'Run ' + (ri+1)}  ·  ${run.timestamp}`;
    tab.title = run.dir;
    tab.onclick = () => switchRun(ri);
    tabsEl.insertBefore(tab, compareBtn);
  });
  showRun(currentRun);
}

function switchRun(ri) {
  compareMode = false;
  currentRun = ri;
  document.querySelectorAll('.run-tab:not(.compare-btn)').forEach((t, i) => t.classList.toggle('active', i === ri));
  document.getElementById('compare-btn').classList.remove('active');
  document.getElementById('compare-table').classList.remove('visible');
  const fb = document.getElementById('filter-bar');
  if (fb) fb.style.display = 'flex';
  showRun(ri);
}

function showRun(ri) {
  const run = RUNS[ri];
  const arCss = (run.aspect_ratio || '16:9').replace(':', '/');
  lbItems = run.images;
  lbRunIdx = ri;
  const el = id => document.getElementById(id);
  el('cur-model').innerHTML = run.model ? `<code>${run.model}</code>` : '';
  el('cur-ts').textContent  = run.timestamp || '';

  const grid = el('grid');
  grid.style.display = 'grid';
  grid.innerHTML = '';

  run.images.forEach((item, i) => {
    const card = document.createElement('div');
    card.className = 'card';
    const rk = PROJECT + '/' + run.dir + '/' + item.file;
    card.dataset.ratingKey = rk;
    card.dataset.idx = i;
    card.dataset.name = item.name || '';
    card.dataset.ts = run.timestamp || '';
    card.dataset.search = ((item.name || '') + ' ' + (item.prompt || '')).toLowerCase();
    card.onclick = () => lbOpen(i, ri);
    const missingMsg = item.error
      ? item.error.replace(/[<>&"]/g, '').slice(0, 80)
      : 'not generated';
    card.innerHTML = `
      <div class="img-wrap" style="aspect-ratio:${arCss}">
        <span class="img-num">${String(i + 1).padStart(2, '0')}</span>
        ${item.ok
          ? `<img src="${run.dir}/${item.file}" alt="" loading="lazy">`
          : `<div class="missing-img">${missingMsg}</div>`}
      </div>
      <div class="card-prompt"></div>
      <div class="card-foot">
        <span class="card-name">${item.name}</span>
        <button class="btn-rate star"   onclick="rateCard(event,'${rk}','star',  this.closest('.card'))">&#9733;</button>
        <button class="btn-rate reject" onclick="rateCard(event,'${rk}','reject',this.closest('.card'))">&#x2715;</button>
      </div>
    `;
    card.querySelector('.card-prompt').textContent = item.prompt || '';
    const img = card.querySelector('img');
    if (img) img.addEventListener('error', () => {
      img.closest('.img-wrap').innerHTML = '<div class="missing-img">file missing</div>';
    });
    grid.appendChild(card);
    applyRating(card, rk);
  });
  updateFilterCounts();
}

function toggleCompare() {
  compareMode = !compareMode;
  document.getElementById('compare-btn').classList.toggle('active', compareMode);
  document.getElementById('grid').style.display = compareMode ? 'none' : 'grid';
  const fb = document.getElementById('filter-bar');
  if (fb) fb.style.display = compareMode ? 'none' : 'flex';
  const ct = document.getElementById('compare-table');
  ct.classList.toggle('visible', compareMode);
  if (compareMode) buildCompareTable();
}

function buildCompareTable() {
  const ct = document.getElementById('compare-table');
  ct.innerHTML = '';
  if (!RUNS.length) return;
  const slotCount = Math.max(...RUNS.map(r => r.images.length));
  for (let si = 0; si < slotCount; si++) {
    const first = RUNS.find(r => r.images[si]);
    if (!first) continue;
    const slotName = first.images[si]?.name || `Slot ${si + 1}`;
    const label = document.createElement('div');
    label.className = 'compare-label';
    label.textContent = `${String(si + 1).padStart(2, '0')} — ${slotName}`;
    ct.appendChild(label);
    const row = document.createElement('div');
    row.className = 'compare-row';
    row.style.gridTemplateColumns = `repeat(${RUNS.length}, minmax(180px, 1fr))`;
    ct.appendChild(row);
    RUNS.forEach((run, ri) => {
      const img = run.images[si];
      const runArCss = (run.aspect_ratio || '16:9').replace(':', '/');
      const cell = document.createElement('div');
      cell.className = 'compare-cell';
      if (img) cell.onclick = () => { lbItems = run.images; lbOpen(si, ri); };
      const missingMsg = img && img.error
        ? img.error.replace(/[<>&"]/g, '').slice(0, 60)
        : (img ? 'failed' : '—');
      cell.innerHTML = `
        <div class="img-wrap" style="aspect-ratio:${runArCss}">
          ${img && img.ok
            ? `<img src="${run.dir}/${img.file}" loading="lazy">`
            : `<div class="missing-img">${missingMsg}</div>`}
        </div>
        <div class="run-badge">${run.model || 'Run ' + (ri+1)}</div>
      `;
      const cellImg = cell.querySelector('img');
      if (cellImg) cellImg.addEventListener('error', () => {
        cellImg.closest('.img-wrap').innerHTML = '<div class="missing-img">file missing</div>';
      });
      row.appendChild(cell);
    });
  }
}
"""

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
    """Generate an HTML gallery viewer alongside the batch output images.

    Args:
        output_dir: Directory where images were saved (viewer lands here too).
        items: List of dicts with keys: name, prompt, output_path.
        title: Gallery title shown in the header.
        run_meta: Optional dict with model, aspect_ratio, style, timestamp, prompt_file.

    Returns:
        Path to the generated viewer.html.
    """
    output_dir = Path(output_dir)
    meta = run_meta or {}

    timestamp = meta.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M"))
    model = meta.get("model", "—")
    aspect_ratio = meta.get("aspect_ratio", "—")
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
        })

    html = _render(title, js_items, model, aspect_ratio, style, timestamp, prompt_file)
    viewer_path = output_dir / "viewer.html"
    viewer_path.write_text(html, encoding="utf-8")
    return viewer_path


# ─── HTML renderer ──────────────────────────────────────────────────────────

def _render(
    title: str,
    items: list[dict],
    model: str,
    aspect_ratio: str,
    style: str,
    timestamp: str,
    prompt_file: str,
) -> str:
    items_json = json.dumps(items, ensure_ascii=False)
    count = len(items)
    source_line = f"Source: <code>{prompt_file}</code> · " if prompt_file else ""

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root {{
  --bg:      #0f0c1a;
  --bg2:     #1a1530;
  --surface: rgba(255,255,255,0.04);
  --border:  #2d2550;
  --ink:     #ede9ff;
  --dim:     #9f9abd;
  --accent:  #7c6af7;
  --accent2: #00c8b4;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  background: linear-gradient(160deg, var(--bg) 0%, var(--bg2) 100%);
  color: var(--ink);
  font-family: ui-sans-serif, system-ui, -apple-system, "Helvetica Neue", sans-serif;
  line-height: 1.5;
  min-height: 100vh;
}}

/* ── Header ── */
header {{
  padding: 2rem 2rem 1.25rem;
  border-bottom: 1px solid var(--border);
}}
header h1 {{
  font-size: 1.6rem;
  letter-spacing: -0.02em;
  margin-bottom: 0.4rem;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}}
.meta {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.5rem;
  font-size: 0.85rem;
  color: var(--dim);
  margin-top: 0.25rem;
}}
.meta code {{
  background: rgba(255,255,255,0.07);
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-size: 0.8rem;
  color: var(--accent2);
}}
.meta .pill {{
  background: rgba(124,106,247,0.15);
  border: 1px solid rgba(124,106,247,0.3);
  color: var(--accent);
  padding: 0.15rem 0.55rem;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.01em;
}}

/* ── Grid ── */
.grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.1rem;
  padding: 1.5rem 2rem 3rem;
}}

/* ── Card ── */
.card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
}}
.card:hover {{
  transform: translateY(-3px);
  border-color: var(--accent);
  box-shadow: 0 8px 30px rgba(124,106,247,0.18);
}}
.img-wrap {{
  aspect-ratio: 16/9;
  background: #0a0814;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}}
.img-wrap img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}}
.missing {{
  color: var(--dim);
  font-size: 0.8rem;
  text-align: center;
  padding: 1.5rem;
  opacity: 0.6;
}}
.card-body {{
  padding: 0.75rem 0.9rem 0.85rem;
}}
.card-name {{
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 0.3rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
.card-num {{
  font-size: 0.72rem;
  color: var(--accent);
  font-weight: 700;
  margin-right: 0.35rem;
  font-variant-numeric: tabular-nums;
}}
.card-prompt {{
  font-size: 0.78rem;
  color: var(--dim);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}}
.card-file {{
  margin-top: 0.4rem;
  font-size: 0.72rem;
  color: rgba(255,255,255,0.2);
  font-family: ui-monospace, monospace;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}

/* ── Lightbox ── */
.lb {{
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.94);
  z-index: 1000;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  flex-direction: column;
  gap: 1rem;
}}
.lb.open {{ display: flex; }}
.lb-img-wrap {{
  position: relative;
  max-width: min(92vw, 1400px);
  max-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
}}
.lb img {{
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
  border-radius: 6px;
  box-shadow: 0 20px 70px rgba(0,0,0,0.7);
  display: block;
}}
.lb-nav {{
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.15);
  color: #fff;
  font-size: 1.4rem;
  line-height: 1;
  width: 2.6rem;
  height: 2.6rem;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
  user-select: none;
}}
.lb-nav:hover {{ background: rgba(255,255,255,0.2); }}
.lb-nav.prev {{ left: -3.5rem; }}
.lb-nav.next {{ right: -3.5rem; }}
.lb-caption {{
  text-align: center;
  max-width: 700px;
}}
.lb-caption .name {{
  font-size: 1rem;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 0.25rem;
}}
.lb-caption .prompt {{
  font-size: 0.82rem;
  color: var(--dim);
  line-height: 1.5;
}}
.lb-close {{
  position: fixed;
  top: 1.2rem;
  right: 1.5rem;
  background: rgba(255,255,255,0.1);
  border: none;
  color: #fff;
  font-size: 1.5rem;
  line-height: 1;
  width: 2.4rem;
  height: 2.4rem;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}}
.lb-close:hover {{ background: rgba(255,255,255,0.2); }}

/* ── Footer ── */
footer {{
  padding: 1.5rem 2rem;
  border-top: 1px solid var(--border);
  text-align: center;
  color: var(--dim);
  font-size: 0.82rem;
}}
footer code {{ color: var(--accent2); }}
</style>
</head>
<body>

<header>
  <h1>{title}</h1>
  <div class="meta">
    <span class="pill">{count} image{'' if count == 1 else 's'}</span>
    <span>Model: <code>{model}</code></span>
    <span>Ratio: <code>{aspect_ratio}</code></span>
    <span>Style: <code>{style}</code></span>
    <span>{source_line}Generated {timestamp}</span>
  </div>
</header>

<div class="grid" id="grid"></div>

<div class="lb" id="lb" onclick="lbClickBg(event)">
  <button class="lb-close" onclick="lbClose()" title="Close (Esc)">✕</button>
  <div class="lb-img-wrap">
    <button class="lb-nav prev" onclick="lbStep(-1); event.stopPropagation()">&#8592;</button>
    <img id="lb-img" src="" alt="">
    <button class="lb-nav next" onclick="lbStep(1); event.stopPropagation()">&#8594;</button>
  </div>
  <div class="lb-caption">
    <div class="name" id="lb-name"></div>
    <div class="prompt" id="lb-prompt"></div>
  </div>
</div>

<footer>
  Generated by <code>rafiki</code> · {timestamp}
</footer>

<script>
const ITEMS = {items_json};

// Build grid
const grid = document.getElementById('grid');
ITEMS.forEach((item, i) => {{
  const card = document.createElement('div');
  card.className = 'card';
  card.onclick = () => lbOpen(i);

  const promptShort = item.prompt.length > 140
    ? item.prompt.slice(0, 140) + '…'
    : item.prompt;

  card.innerHTML = `
    <div class="img-wrap">
      ${{item.ok
        ? `<img src="${{item.file}}" alt="${{item.name}}" loading="lazy">`
        : `<div class="missing">Not generated yet</div>`
      }}
    </div>
    <div class="card-body">
      <div class="card-name">
        <span class="card-num">${{String(i + 1).padStart(2, '0')}}</span>${{item.name}}
      </div>
      <div class="card-prompt" title="${{item.prompt.replace(/"/g, '&quot;')}}">${{promptShort}}</div>
      <div class="card-file">${{item.file}}</div>
    </div>
  `;
  grid.appendChild(card);
}});

// Lightbox
let lbIdx = 0;
const lb    = document.getElementById('lb');
const lbImg = document.getElementById('lb-img');
const lbName   = document.getElementById('lb-name');
const lbPrompt = document.getElementById('lb-prompt');

function lbOpen(i) {{
  lbIdx = ((i % ITEMS.length) + ITEMS.length) % ITEMS.length;
  const item = ITEMS[lbIdx];
  lbImg.src = item.file;
  lbName.textContent = item.name;
  lbPrompt.textContent = item.prompt.length > 300
    ? item.prompt.slice(0, 300) + '…'
    : item.prompt;
  lb.classList.add('open');
}}
function lbClose() {{ lb.classList.remove('open'); }}
function lbStep(dir) {{ lbOpen(lbIdx + dir); event.stopPropagation(); }}
function lbClickBg(e) {{ if (e.target === lb) lbClose(); }}

document.addEventListener('keydown', e => {{
  if (!lb.classList.contains('open')) return;
  if (e.key === 'Escape')      lbClose();
  if (e.key === 'ArrowLeft')   lbOpen(lbIdx - 1);
  if (e.key === 'ArrowRight')  lbOpen(lbIdx + 1);
}});
</script>
</body>
</html>"""

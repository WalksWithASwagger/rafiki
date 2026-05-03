#!/usr/bin/env python3
"""Generate a polished presentation viewer (filter tabs, lightbox, social copy) from a JSON data file.

The viewer mirrors the look and behavior of the original RAP certification viewer
(`generate-rap-viewer.py`) but is parameterized over an arbitrary set of categories
and items, so the same code can power any image series.

Usage:
    python generate-presentation-viewer.py --data <data.json> --output <dir> [--title <override>]

See `docs/PRESENTATION-VIEWER.md` for the JSON schema.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent

SIZE_WARN_THRESHOLD = 50 * 1024 * 1024  # 50 MB


def _load_data(data_path: Path) -> Dict[str, Any]:
    with data_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _resolve_image_dir(image_dir: str) -> Path:
    """Resolve an image_dir from the JSON.

    Absolute paths are honored as-is. Relative paths are resolved against the
    repo root (where this script lives), matching the convention used by the
    legacy `generate-rap-viewer.py` and the wrappers that follow it. Existence
    is not required at generation time — the original viewer also blindly
    constructed paths whether or not the targets were on disk."""
    p = Path(image_dir)
    if p.is_absolute():
        return p
    return SCRIPT_DIR / p


def _encode_image_data_uri(image_path: Path, max_width: Optional[int]) -> str:
    """Read an image from disk, optionally resize to max_width, return a data: URI.

    Pillow is imported lazily so the default code path has no hard dependency.
    """
    from PIL import Image  # noqa: WPS433 — lazy import keeps default path light

    if max_width is not None:
        with Image.open(image_path) as im:
            im.load()
            if im.width > max_width:
                new_height = round(im.height * (max_width / im.width))
                im = im.resize((max_width, new_height), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, format="PNG")
            payload = buf.getvalue()
    else:
        payload = image_path.read_bytes()

    encoded = base64.b64encode(payload).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _build_items_js(
    data: Dict[str, Any],
    output_dir: Path,
    self_contained: bool = False,
    max_width: Optional[int] = None,
) -> tuple[str, int]:
    """Build the JS-embedded items array.

    Returns ``(json_string, embedded_bytes)`` where ``embedded_bytes`` is the
    total raw byte count of all base64 payloads (zero in non-self-contained
    mode). The caller uses it to print a size warning.
    """
    categories = {c["id"]: c for c in data["categories"]}
    image_dirs = {int(k): v for k, v in data["image_dirs"].items()}

    enriched: List[Dict[str, Any]] = []
    embedded_bytes = 0
    for item in data["items"]:
        cat_id = item["category"]
        cat = categories[cat_id]
        run_dir = _resolve_image_dir(image_dirs[cat_id])
        image_path = run_dir / f"{item['slug']}.png"
        if self_contained:
            src = _encode_image_data_uri(image_path, max_width)
            embedded_bytes += len(src)
        else:
            src = os.path.relpath(os.path.abspath(image_path), os.path.abspath(output_dir))
        enriched.append(
            {
                "category": cat_id,
                "categoryShort": cat["short"],
                "categoryLabel": cat["label"],
                "title": item["title"],
                "caption": item["caption"],
                "social": item.get("social"),
                "square": bool(item.get("square", False)),
                "src": src,
            }
        )
    return json.dumps(enriched, indent=2, ensure_ascii=False), embedded_bytes


def _build_tabs_html(data: Dict[str, Any]) -> str:
    all_label = data.get("all_tab_label", f"All {data['category_label_singular']}s")
    parts = [f'    <button class="tab active" data-cat="0">{all_label}</button>']
    for cat in data["categories"]:
        label = cat.get("tab_label", cat["label"])
        parts.append(f'    <button class="tab" data-cat="{cat["id"]}">{label}</button>')
    return "\n".join(parts)


def build_viewer(
    data: Dict[str, Any],
    output_dir: Path,
    self_contained: bool = False,
    max_width: Optional[int] = None,
) -> str:
    html, _ = _build_viewer_with_size(data, output_dir, self_contained, max_width)
    return html


def _build_viewer_with_size(
    data: Dict[str, Any],
    output_dir: Path,
    self_contained: bool,
    max_width: Optional[int],
) -> tuple[str, int]:
    items_js, embedded_bytes = _build_items_js(data, output_dir, self_contained, max_width)
    tabs_html = _build_tabs_html(data)
    item_count = len(data["items"])
    page_title = data.get("page_title", data["title"])
    header = data.get("header", {})
    logo = header.get("logo", "✦")
    style_label = header.get("style_label", "")
    style_meta = header.get("style_meta", "")
    style_description = header.get("style_description", "")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title}</title>
<style>
  :root {{
    --green: #1E3A2B;
    --gold: #D4A017;
    --gold-light: #e8b93a;
    --bg: #0d1f16;
    --surface: #162b1e;
    --surface2: #1e3a28;
    --text: #e8e4d8;
    --muted: #8a9e8e;
    --radius: 10px;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; min-height: 100vh; }}

  /* ── Header ── */
  header {{ background: var(--green); border-bottom: 2px solid var(--gold); padding: 20px 32px; display: flex; align-items: center; gap: 16px; }}
  .logo {{ width: 48px; height: 48px; border: 2.5px solid var(--gold); border-radius: 8px; display: grid; place-items: center; font-size: 22px; color: var(--gold); flex-shrink: 0; }}
  header h1 {{ font-size: 1.4rem; font-weight: 700; color: var(--text); line-height: 1.2; }}
  header p {{ font-size: 0.85rem; color: var(--muted); margin-top: 2px; }}
  .header-right {{ margin-left: auto; font-size: 0.8rem; color: var(--muted); text-align: right; }}
  .header-right strong {{ color: var(--gold); }}

  /* ── Controls ── */
  .controls {{ padding: 20px 32px; display: flex; flex-wrap: wrap; gap: 12px; align-items: center; border-bottom: 1px solid #2a3e30; }}
  .tab-group {{ display: flex; gap: 6px; flex-wrap: wrap; }}
  .tab {{ padding: 7px 16px; border-radius: 20px; border: 1px solid #2e4a34; background: var(--surface); color: var(--muted); cursor: pointer; font-size: 0.82rem; font-weight: 500; transition: all .15s; }}
  .tab:hover {{ border-color: var(--gold); color: var(--text); }}
  .tab.active {{ background: var(--gold); border-color: var(--gold); color: #0d1f16; font-weight: 700; }}
  .search-wrap {{ margin-left: auto; position: relative; }}
  .search-wrap input {{ background: var(--surface); border: 1px solid #2e4a34; border-radius: 20px; color: var(--text); padding: 7px 16px 7px 36px; font-size: 0.82rem; width: 220px; outline: none; transition: border-color .15s; }}
  .search-wrap input:focus {{ border-color: var(--gold); }}
  .search-wrap::before {{ content: "🔍"; position: absolute; left: 12px; top: 50%; transform: translateY(-50%); font-size: 12px; pointer-events: none; }}
  .count {{ font-size: 0.78rem; color: var(--muted); white-space: nowrap; }}

  /* ── Grid ── */
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; padding: 24px 32px 48px; }}

  /* ── Card ── */
  .card {{ background: var(--surface); border-radius: var(--radius); overflow: hidden; border: 1px solid #2a3e30; transition: transform .15s, border-color .15s, box-shadow .15s; cursor: pointer; display: flex; flex-direction: column; }}
  .card:hover {{ transform: translateY(-3px); border-color: var(--gold); box-shadow: 0 8px 24px rgba(0,0,0,.4); }}
  .card-img {{ width: 100%; aspect-ratio: 16/9; object-fit: cover; display: block; background: #0d1f16; }}
  .card-img.square {{ aspect-ratio: 1/1; }}
  .card-body {{ padding: 14px 16px 16px; flex: 1; display: flex; flex-direction: column; gap: 8px; }}
  .card-meta {{ display: flex; align-items: center; gap: 8px; }}
  .week-badge {{ font-size: 0.68rem; font-weight: 700; letter-spacing: .04em; padding: 3px 8px; border-radius: 10px; background: var(--green); border: 1px solid var(--gold); color: var(--gold); white-space: nowrap; }}
  .social-badge {{ font-size: 0.68rem; font-weight: 700; padding: 3px 8px; border-radius: 10px; background: #2a1a05; border: 1px solid #c98a10; color: #e8a820; white-space: nowrap; }}
  .card-title {{ font-size: 0.95rem; font-weight: 700; color: var(--text); line-height: 1.3; }}
  .card-caption {{ font-size: 0.8rem; color: var(--muted); line-height: 1.5; flex: 1; }}

  /* ── Lightbox ── */
  #lightbox {{ display: none; position: fixed; inset: 0; z-index: 1000; background: rgba(0,0,0,.88); backdrop-filter: blur(6px); align-items: center; justify-content: center; padding: 20px; }}
  #lightbox.open {{ display: flex; }}
  .lb-inner {{ background: var(--surface); border-radius: 14px; border: 1px solid #2e4a34; max-width: 960px; width: 100%; max-height: 90vh; overflow-y: auto; display: flex; flex-direction: column; }}
  .lb-img-wrap {{ position: relative; background: #0a180f; }}
  .lb-img-wrap img {{ width: 100%; max-height: 60vh; object-fit: contain; display: block; }}
  .lb-close {{ position: absolute; top: 12px; right: 12px; background: rgba(0,0,0,.6); border: 1px solid #3a5040; border-radius: 50%; width: 36px; height: 36px; display: grid; place-items: center; cursor: pointer; color: var(--text); font-size: 18px; line-height: 1; transition: background .15s; }}
  .lb-close:hover {{ background: rgba(0,0,0,.9); border-color: var(--gold); }}
  .lb-nav {{ position: absolute; top: 50%; transform: translateY(-50%); background: rgba(0,0,0,.6); border: 1px solid #3a5040; border-radius: 50%; width: 40px; height: 40px; display: grid; place-items: center; cursor: pointer; color: var(--text); font-size: 20px; transition: background .15s; }}
  .lb-nav:hover {{ background: rgba(0,0,0,.9); border-color: var(--gold); }}
  #lb-prev {{ left: 12px; }}
  #lb-next {{ right: 12px; }}
  .lb-info {{ padding: 20px 24px 24px; display: flex; flex-direction: column; gap: 12px; }}
  .lb-meta {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
  .lb-title {{ font-size: 1.2rem; font-weight: 700; color: var(--text); }}
  .lb-caption {{ font-size: 0.9rem; color: var(--muted); line-height: 1.6; }}
  .lb-social {{ background: #1a1005; border: 1px solid #8a5a10; border-radius: 8px; padding: 14px 16px; display: flex; flex-direction: column; gap: 10px; }}
  .lb-social-label {{ font-size: 0.75rem; font-weight: 700; letter-spacing: .06em; color: #e8a820; text-transform: uppercase; }}
  .lb-social-text {{ font-size: 0.85rem; color: #d4c090; line-height: 1.6; white-space: pre-wrap; }}
  .lb-download {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }}
  .btn {{ display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border-radius: 20px; font-size: 0.82rem; font-weight: 600; cursor: pointer; border: none; transition: all .15s; text-decoration: none; }}
  .btn-gold {{ background: var(--gold); color: #0d1f16; }}
  .btn-gold:hover {{ background: var(--gold-light); }}
  .btn-outline {{ background: transparent; border: 1px solid #2e4a34; color: var(--muted); }}
  .btn-outline:hover {{ border-color: var(--gold); color: var(--text); }}
  .copy-confirm {{ font-size: 0.75rem; color: #6fcf6f; display: none; }}
  .copy-confirm.show {{ display: inline; }}

  /* ── Empty ── */
  .empty {{ grid-column: 1/-1; text-align: center; padding: 60px 20px; color: var(--muted); font-size: 0.95rem; }}

  @media (max-width: 600px) {{
    header {{ padding: 16px 16px; }}
    .controls {{ padding: 14px 16px; }}
    .grid {{ padding: 16px 16px 40px; gap: 14px; }}
    .search-wrap input {{ width: 160px; }}
  }}
</style>
</head>
<body>

<header>
  <div class="logo">{logo}</div>
  <div>
    <h1>{data["title"]}</h1>
    <p>{data["subtitle"]}</p>
  </div>
  <div class="header-right">
    <strong>{style_label}</strong> {style_meta}<br>
    {style_description}
  </div>
</header>

<div class="controls">
  <div class="tab-group">
{tabs_html}
  </div>
  <span class="count" id="count">{item_count} images</span>
  <div class="search-wrap">
    <input type="text" id="search" placeholder="Search titles & captions…" autocomplete="off">
  </div>
</div>

<div class="grid" id="grid"></div>

<div id="lightbox">
  <div class="lb-inner">
    <div class="lb-img-wrap">
      <img id="lb-img" src="" alt="">
      <button class="lb-close" id="lb-close">×</button>
      <button class="lb-nav" id="lb-prev">‹</button>
      <button class="lb-nav" id="lb-next">›</button>
    </div>
    <div class="lb-info">
      <div class="lb-meta">
        <span class="week-badge" id="lb-week"></span>
        <span class="social-badge" id="lb-social-badge" style="display:none">📣 Social Post</span>
      </div>
      <div class="lb-title" id="lb-title"></div>
      <div class="lb-caption" id="lb-caption"></div>
      <div class="lb-social" id="lb-social-box" style="display:none">
        <div class="lb-social-label">📣 Ready-to-post copy</div>
        <div class="lb-social-text" id="lb-social-text"></div>
      </div>
      <div class="lb-download">
        <a class="btn btn-gold" id="lb-dl" download>⬇ Download</a>
        <button class="btn btn-outline" id="lb-copy-social" style="display:none">Copy social post</button>
        <span class="copy-confirm" id="copy-confirm">Copied!</span>
      </div>
    </div>
  </div>
</div>

<script>
const ITEMS = {items_js};

let activeCat = 0;
let activeIndex = 0;
let visibleItems = [];

function render() {{
  const q = document.getElementById("search").value.toLowerCase().trim();
  visibleItems = ITEMS.filter(item => {{
    if (activeCat && item.category !== activeCat) return false;
    if (q && !item.title.toLowerCase().includes(q) && !item.caption.toLowerCase().includes(q)) return false;
    return true;
  }});

  const grid = document.getElementById("grid");
  grid.innerHTML = "";
  document.getElementById("count").textContent = visibleItems.length + " image" + (visibleItems.length !== 1 ? "s" : "");

  if (!visibleItems.length) {{
    grid.innerHTML = '<div class="empty">No images match your search.</div>';
    return;
  }}

  visibleItems.forEach((item, i) => {{
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <img class="card-img${{item.square ? " square" : ""}}" src="${{item.src}}" alt="${{item.title}}" loading="lazy">
      <div class="card-body">
        <div class="card-meta">
          <span class="week-badge">${{item.categoryShort}} · ${{item.categoryLabel.replace(/^[^—]+—\\s*/, "")}}</span>
          ${{item.social ? '<span class="social-badge">📣 Social</span>' : ""}}
        </div>
        <div class="card-title">${{item.title}}</div>
        <div class="card-caption">${{item.caption}}</div>
      </div>`;
    card.addEventListener("click", () => openLightbox(i));
    grid.appendChild(card);
  }});
}}

function openLightbox(i) {{
  activeIndex = i;
  const item = visibleItems[i];
  document.getElementById("lb-img").src = item.src;
  document.getElementById("lb-week").textContent = item.categoryLabel;
  document.getElementById("lb-title").textContent = item.title;
  document.getElementById("lb-caption").textContent = item.caption;
  document.getElementById("lb-dl").href = item.src;
  document.getElementById("lb-dl").download = item.src.split("/").pop();

  const socialBadge = document.getElementById("lb-social-badge");
  const socialBox = document.getElementById("lb-social-box");
  const copyBtn = document.getElementById("lb-copy-social");
  const confirmEl = document.getElementById("copy-confirm");

  if (item.social) {{
    socialBadge.style.display = "";
    socialBox.style.display = "";
    document.getElementById("lb-social-text").textContent = item.social;
    copyBtn.style.display = "";
  }} else {{
    socialBadge.style.display = "none";
    socialBox.style.display = "none";
    copyBtn.style.display = "none";
  }}
  confirmEl.classList.remove("show");

  document.getElementById("lightbox").classList.add("open");
  document.body.style.overflow = "hidden";
}}

function closeLightbox() {{
  document.getElementById("lightbox").classList.remove("open");
  document.body.style.overflow = "";
}}

document.getElementById("lb-close").addEventListener("click", closeLightbox);
document.getElementById("lightbox").addEventListener("click", e => {{ if (e.target === document.getElementById("lightbox")) closeLightbox(); }});

document.getElementById("lb-prev").addEventListener("click", e => {{
  e.stopPropagation();
  openLightbox((activeIndex - 1 + visibleItems.length) % visibleItems.length);
}});
document.getElementById("lb-next").addEventListener("click", e => {{
  e.stopPropagation();
  openLightbox((activeIndex + 1) % visibleItems.length);
}});

document.getElementById("lb-copy-social").addEventListener("click", () => {{
  const item = visibleItems[activeIndex];
  if (!item.social) return;
  navigator.clipboard.writeText(item.social).then(() => {{
    const el = document.getElementById("copy-confirm");
    el.classList.add("show");
    setTimeout(() => el.classList.remove("show"), 2000);
  }});
}});

document.addEventListener("keydown", e => {{
  if (!document.getElementById("lightbox").classList.contains("open")) return;
  if (e.key === "Escape") closeLightbox();
  if (e.key === "ArrowLeft") openLightbox((activeIndex - 1 + visibleItems.length) % visibleItems.length);
  if (e.key === "ArrowRight") openLightbox((activeIndex + 1) % visibleItems.length);
}});

document.querySelectorAll(".tab").forEach(tab => {{
  tab.addEventListener("click", () => {{
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    tab.classList.add("active");
    activeCat = parseInt(tab.dataset.cat);
    render();
  }});
}});

document.getElementById("search").addEventListener("input", render);

render();
</script>
</body>
</html>"""
    return html, embedded_bytes


def _format_size(num_bytes: int) -> str:
    mb = num_bytes / (1024 * 1024)
    if mb >= 1:
        return f"{mb:.1f} MB"
    kb = num_bytes / 1024
    return f"{kb:.1f} KB"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a presentation viewer from a JSON data file.")
    parser.add_argument("--data", required=True, type=Path, help="Path to viewer JSON data file")
    parser.add_argument("--output", required=True, type=Path, help="Output directory (viewer.html written here)")
    parser.add_argument("--title", help="Override the title from the data file")
    parser.add_argument(
        "--self-contained",
        action="store_true",
        help="Embed every image as a base64 data: URI so the HTML is a single portable file.",
    )
    parser.add_argument(
        "--max-width",
        type=int,
        default=None,
        help="With --self-contained, resize each image to this max width (px) before encoding. "
             "Aspect ratio is preserved. Without this, images are embedded at full resolution.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    data_path = args.data
    output_dir = args.output

    if args.max_width is not None and not args.self_contained:
        print("warning: --max-width has no effect without --self-contained", file=sys.stderr)

    data = _load_data(data_path)
    if args.title:
        data["title"] = args.title

    output_dir.mkdir(parents=True, exist_ok=True)
    html, embedded_bytes = _build_viewer_with_size(
        data, output_dir, args.self_contained, args.max_width
    )
    out = output_dir / "viewer.html"
    out.write_text(html, encoding="utf-8")

    if args.self_contained and embedded_bytes > SIZE_WARN_THRESHOLD:
        print(
            f"warning: embedded image payload is {_format_size(embedded_bytes)} "
            f"(over {_format_size(SIZE_WARN_THRESHOLD)} threshold). "
            f"Consider --max-width to reduce file size.",
            file=sys.stderr,
        )

    file_size = out.stat().st_size
    print(f"Viewer: {out}")
    print(f"File: {out.name} ({_format_size(file_size)})")
    print(f"Items: {len(data['items'])} entries across {len(data['categories'])} {data['category_label_singular'].lower()}s")


if __name__ == "__main__":
    main()

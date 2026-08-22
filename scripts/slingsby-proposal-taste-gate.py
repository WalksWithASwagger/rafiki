#!/usr/bin/env python3
"""Build a local side-by-side taste-gate page. No provider calls.

Writes gitignored HTML under the Slingsby output dir so a human can
compare authorized likeness refs to generated plates without publishing
faces. Paths in the page are relative file links only.
"""

from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def _images(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        p
        for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES
    )


def _load_run(run_dir: Path) -> dict:
    manifest = run_dir / "run.json"
    if not manifest.is_file():
        return {}
    try:
        data = json.loads(manifest.read_text())
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _role(run_dir: Path) -> str:
    role = str(_load_run(run_dir).get("reference_role") or "").strip().lower()
    if role in {"style", "likeness"}:
        return role
    names = [p.name for p in _images(run_dir)]
    if any(name.startswith("01-hero") or name.startswith("01-through") for name in names):
        if any("hero" in name or "bio" in name or "counsel" in name for name in names):
            return "likeness"
        return "style"
    return "unknown"


def _rel(page: Path, target: Path) -> str:
    return os.path.relpath(target.resolve(), start=page.parent.resolve())


def _figure(page: Path, image: Path, caption: str) -> str:
    src = html.escape(_rel(page, image), quote=True)
    cap = html.escape(caption)
    return (
        f'<figure><img src="{src}" alt="{cap}">'
        f"<figcaption>{cap}</figcaption></figure>"
    )


def _latest_runs(output_dir: Path) -> dict[str, Path]:
    found: dict[str, Path] = {}
    runs = sorted(
        (p for p in output_dir.glob("run-*") if p.is_dir() and _images(p)),
        key=lambda p: p.name,
    )
    for run_dir in runs:
        role = _role(run_dir)
        if role in {"style", "likeness"}:
            found[role] = run_dir
        elif "likeness" not in found and any(
            "hero" in p.name for p in _images(run_dir)
        ):
            found["likeness"] = run_dir
        elif "style" not in found:
            found["style"] = run_dir
    return found


def build_taste_gate(
    *,
    output_dir: Path,
    likeness_dir: Path,
    page_name: str = "taste-gate.html",
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    page = output_dir / page_name
    runs = _latest_runs(output_dir)
    refs = _images(likeness_dir)

    sections: list[str] = [
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">",
        "<title>Slingsby Advisors taste gate (local)</title>",
        "<style>",
        "body{font:16px/1.4 sans-serif;margin:24px;color:#111;background:#f6f4f0}",
        "h1,h2{font-weight:600} .row{display:flex;flex-wrap:wrap;gap:16px}",
        "figure{margin:0;width:280px} img{width:100%;height:auto;background:#ddd}",
        "figcaption{font-size:12px;margin-top:6px} .note{max-width:52rem}",
        "</style></head><body>",
        "<h1>Slingsby Advisors taste gate</h1>",
        "<p class=\"note\">Local only. Compare authorized refs to generated "
        "plates. Confirm the face before any proposal export. Do not publish "
        "this page.</p>",
        "<p class=\"note\">Reject stock-face leakage, youth-wash, nametags, "
        "letterhead, readable text, Vancouver AI / MAC slides, or invented "
        "wordmarks.</p>",
    ]

    sections.append("<h2>Authorized likeness refs</h2><div class=\"row\">")
    if refs:
        for image in refs:
            sections.append(_figure(page, image, image.name))
    else:
        sections.append("<p>No likeness refs found.</p>")
    sections.append("</div>")

    style_run = runs.get("style")
    sections.append("<h2>Style plates</h2>")
    if style_run:
        sections.append(f"<p>{html.escape(style_run.name)}</p><div class=\"row\">")
        for image in _images(style_run):
            sections.append(_figure(page, image, image.name))
        sections.append("</div>")
    else:
        sections.append("<p>No style run with PNGs.</p>")

    likeness_run = runs.get("likeness")
    sections.append("<h2>Likeness plates</h2>")
    if likeness_run:
        sections.append(f"<p>{html.escape(likeness_run.name)}</p><div class=\"row\">")
        for image in _images(likeness_run):
            sections.append(_figure(page, image, image.name))
        sections.append("</div>")
    else:
        sections.append("<p>No likeness run with PNGs.</p>")

    sections.append(
        "<h2>Human checklist</h2><ul>"
        "<li>Hero / bio / stewardship / studio / counsel: same person as refs</li>"
        "<li>07-urban-canyon: foreground silhouette acceptable?</li>"
        "<li>Studio: open laptop / paper acceptable?</li>"
        "<li>Hands: over-shoulder crop acceptable, or regen tight hands?</li>"
        "<li>Keep / regen / reject each plate before export</li>"
        "</ul></body></html>\n"
    )
    page.write_text("".join(sections))
    return page


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--likeness-dir", type=Path, required=True)
    args = parser.parse_args()
    page = build_taste_gate(
        output_dir=args.output_dir,
        likeness_dir=args.likeness_dir,
    )
    print(f"taste-gate: {page}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

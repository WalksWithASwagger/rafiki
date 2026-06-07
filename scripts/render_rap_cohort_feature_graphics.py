#!/usr/bin/env python3
"""Composite RAP cohort feature graphics from generated background plates."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_DIR = REPO_ROOT / "output" / "rap-cohort-feature-graphics-2026"
PROMPT_FILE = REPO_ROOT / "prompts" / "bcai" / "rap-cohort-feature-graphics-2026-06-06.md"
GPT_RAW_DIR = PROJECT_DIR / "raw-gpt-image-2"
GEMINI_RAW_DIR = PROJECT_DIR / "raw-gemini-pro"
REVIEW_DIR = PROJECT_DIR / "review"
CANVAS = (1536, 1024)
LOGOS = {
    "bcai": Path("/Users/kk/Code/RAP/web/public/brand/bcai/bcai-logo-official.png"),
    "rap_wordmark": Path("/Users/kk/Code/RAP/web/public/brand/rap/rap-wordmark.png"),
    "rap_shield": Path("/Users/kk/Code/RAP/web/public/brand/rap/rap-shield.png"),
}
FONT_CANDIDATES = [
    Path("/Users/kk/Library/Fonts/Montserrat-SemiBold.otf"),
    Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
]
COHORTS = {
    "august": {
        "label": "Cohort 2",
        "start": "Starts August 7, 2026",
        "accent": (216, 238, 39),
    },
    "september": {
        "label": "Cohort 3",
        "start": "Starts September 18, 2026",
        "accent": (229, 174, 83),
    },
}


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def latest_run(directory: Path) -> Path:
    runs = sorted(path for path in directory.glob("run-*") if (path / "run.json").exists())
    if not runs:
        raise FileNotFoundError(f"No run-*/run.json found under {directory}")
    return runs[-1]


def load_manifest(run_dir: Path) -> dict[str, Any]:
    return json.loads((run_dir / "run.json").read_text(encoding="utf-8"))


def prompt_records(run_dir: Path) -> list[dict[str, Any]]:
    manifest = load_manifest(run_dir)
    records = manifest.get("images")
    if not isinstance(records, list):
        raise RuntimeError(f"{run_dir}/run.json has no images list")
    missing = []
    usable: list[dict[str, Any]] = []
    for item in records:
        path = run_dir / str(item.get("file", ""))
        if not item.get("ok") or not path.exists():
            missing.append(str(path))
            continue
        usable.append({**item, "path": path})
    if missing:
        raise RuntimeError(f"{run_dir} has {len(missing)} missing or failed raw image(s): {missing[:3]}")
    if len(usable) != 20:
        raise RuntimeError(f"{run_dir} should have 20 usable raw images, found {len(usable)}")
    return usable


def font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if not path.exists():
            continue
        try:
            return ImageFont.truetype(str(path), size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def resize_to_width(image: Image.Image, width: int) -> Image.Image:
    ratio = width / image.width
    height = int(round(image.height * ratio))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def draw_left_gradient(base: Image.Image) -> None:
    overlay = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    pixels = overlay.load()
    for x in range(CANVAS[0]):
        left_alpha = max(0, int(205 * (1 - x / 940)))
        for y in range(CANVAS[1]):
            bottom = max(0, int(145 * ((y - 690) / 334))) if y > 690 else 0
            top = max(0, int(70 * (1 - y / 260))) if y < 260 else 0
            alpha = min(225, max(left_alpha, bottom, top))
            if alpha:
                pixels[x, y] = (2, 12, 35, alpha)
    base.alpha_composite(overlay)


def shadowed_paste(base: Image.Image, logo: Image.Image, xy: tuple[int, int], radius: int = 18) -> None:
    x, y = xy
    alpha = logo.split()[-1] if logo.mode == "RGBA" else Image.new("L", logo.size, 255)
    shadow = Image.new("RGBA", logo.size, (0, 0, 0, 160))
    shadow.putalpha(alpha.filter(ImageFilter.GaussianBlur(radius)))
    base.alpha_composite(shadow, (x + 10, y + 12))
    base.alpha_composite(logo.convert("RGBA"), (x, y))


def draw_text_block(base: Image.Image, cohort_key: str) -> None:
    cfg = COHORTS[cohort_key]
    draw = ImageDraw.Draw(base)
    accent = cfg["accent"]
    white = (248, 252, 250)
    muted = (191, 223, 214)
    title_font = font(82)
    subtitle_font = font(42)
    date_font = font(38)
    label_font = font(31)

    x = 94
    y = 124
    pill_text = cfg["label"]
    bbox = draw.textbbox((0, 0), pill_text, font=label_font)
    pill_w = bbox[2] - bbox[0] + 58
    draw.rounded_rectangle((x, y, x + pill_w, y + 58), radius=29, fill=(4, 24, 53, 214), outline=accent, width=2)
    draw.text((x + 29, y + 12), pill_text, font=label_font, fill=white)

    draw.rectangle((x, y + 104, x + 8, y + 312), fill=accent)
    draw.text((x + 30, y + 86), "Responsible AI", font=title_font, fill=white)
    draw.text((x + 30, y + 174), "Professional", font=title_font, fill=white)
    draw.text((x + 32, y + 282), "Certification Program", font=subtitle_font, fill=muted)
    draw.text((x + 32, y + 354), cfg["start"], font=date_font, fill=white)


def composite_one(raw: Path, output: Path, cohort_key: str) -> None:
    background = Image.open(raw).convert("RGB")
    canvas = ImageOps.fit(background, CANVAS, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5)).convert("RGBA")
    draw_left_gradient(canvas)

    shield = resize_to_width(Image.open(LOGOS["rap_shield"]).convert("RGBA"), 210)
    wordmark = resize_to_width(Image.open(LOGOS["rap_wordmark"]).convert("RGBA"), 430)
    bcai = resize_to_width(Image.open(LOGOS["bcai"]).convert("RGBA"), 154)

    shadowed_paste(canvas, shield, (1230, 122), radius=14)
    shadowed_paste(canvas, bcai, (88, 798), radius=12)
    shadowed_paste(canvas, wordmark, (1014, 762), radius=12)
    draw_text_block(canvas, cohort_key)

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output, format="PNG", optimize=True)


def cohort_key(name: str) -> str:
    lower = name.lower()
    if "august" in lower:
        return "august"
    if "september" in lower:
        return "september"
    raise RuntimeError(f"Cannot infer cohort date from {name!r}")


def direction(name: str) -> str:
    return name.split(" - ", 1)[-1].strip()


def build_review_run(gpt_run: Path, gemini_run: Path, review_run: Path) -> dict[str, Any]:
    raw_sets = [
        ("gpt-image-2", gpt_run, prompt_records(gpt_run)),
        ("gemini-3-pro-image-preview", gemini_run, prompt_records(gemini_run)),
    ]
    images: list[dict[str, Any]] = []
    index = 1
    for model_name, run_dir, records in raw_sets:
        for record in records:
            key = cohort_key(str(record["name"]))
            out_name = f"{index:02d}-{slugify(str(record['name']))}-{slugify(model_name)}.png"
            out_path = review_run / out_name
            composite_one(Path(record["path"]), out_path, key)
            with Image.open(out_path) as check:
                if check.size != CANVAS:
                    raise RuntimeError(f"{out_path} rendered at {check.size}, expected {CANVAS}")
            cfg = COHORTS[key]
            images.append(
                {
                    "name": f"{cfg['label']} - {direction(str(record['name']))} - {model_name}",
                    "prompt": str(record.get("prompt") or ""),
                    "file": out_name,
                    "ok": True,
                    "state": "succeeded",
                    "model": model_name,
                    "provider": "openai" if model_name.startswith("gpt") else "gemini",
                    "aspect_ratio": "3:2",
                    "resolution": "1536x1024",
                    "style": "none",
                    "source_run": str(run_dir),
                    "source_file": str(record.get("file") or ""),
                    "cohort": cfg["label"],
                    "start_date": cfg["start"],
                    "direction": direction(str(record["name"])),
                    "contains_exact_overlays": [
                        "BC+AI logo",
                        "RAP wordmark",
                        "RAP shield",
                        cfg["label"],
                        cfg["start"],
                        "Responsible AI Professional",
                        "Certification Program",
                    ],
                }
            )
            index += 1

    now = dt.datetime.now().astimezone()
    manifest = {
        "model": "composited-review",
        "models": ["gpt-image-2", "gemini-3-pro-image-preview"],
        "aspect_ratio": "3:2",
        "resolution": "1536x1024",
        "quality": "deterministic-composite",
        "style": "none",
        "prompt_file": str(PROMPT_FILE),
        "prompt_source": str(PROMPT_FILE),
        "timestamp": now.strftime("%Y-%m-%d %H:%M"),
        "started_at": now.isoformat(timespec="seconds"),
        "finished_at": now.isoformat(timespec="seconds"),
        "run_id": review_run.name.removeprefix("run-"),
        "state": "succeeded",
        "source_runs": {"gpt-image-2": str(gpt_run), "gemini-3-pro-image-preview": str(gemini_run)},
        "logo_assets": {key: str(path) for key, path in LOGOS.items()},
        "images": images,
    }
    (review_run / "run.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def refresh_links(review_run: Path) -> None:
    latest = REVIEW_DIR / "latest"
    if latest.is_symlink() or latest.exists():
        latest.unlink()
    latest.symlink_to(review_run.name)

    root_link = PROJECT_DIR / review_run.name
    if root_link.is_symlink() or root_link.exists():
        root_link.unlink()
    root_link.symlink_to(Path("review") / review_run.name)

    project_latest = PROJECT_DIR / "latest"
    if project_latest.is_symlink() or project_latest.exists():
        project_latest.unlink()
    project_latest.symlink_to(review_run.name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", type=Path, default=PROJECT_DIR)
    parser.add_argument("--gpt-run", type=Path, default=None)
    parser.add_argument("--gemini-run", type=Path, default=None)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--no-root-link", action="store_true", help="Do not symlink review run into the project root for generate.py view")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    global PROJECT_DIR, GPT_RAW_DIR, GEMINI_RAW_DIR, REVIEW_DIR
    PROJECT_DIR = args.project_dir
    GPT_RAW_DIR = PROJECT_DIR / "raw-gpt-image-2"
    GEMINI_RAW_DIR = PROJECT_DIR / "raw-gemini-pro"
    REVIEW_DIR = PROJECT_DIR / "review"

    for label, path in LOGOS.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing {label} logo asset: {path}")

    gpt_run = args.gpt_run or latest_run(GPT_RAW_DIR)
    gemini_run = args.gemini_run or latest_run(GEMINI_RAW_DIR)
    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    review_run = REVIEW_DIR / f"run-{run_id}"
    review_run.mkdir(parents=True, exist_ok=False)
    manifest = build_review_run(gpt_run, gemini_run, review_run)
    if not args.no_root_link:
        refresh_links(review_run)
    print(json.dumps({"review_run": str(review_run), "images": len(manifest["images"])}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.exit(f"ERROR: {exc}")

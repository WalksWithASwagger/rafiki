#!/usr/bin/env python3
"""Build Gemini-safe Slingsby refs from the local (gitignored) intake.

Creates:
  assets/slingsby/style-refs/moodboard/face-free/  — architecture/light only
  assets/slingsby/likeness-clean/                  — Tanya face crops, no badges

Raw album frames and full mood-board pages stay in place as archive.
This script never prints or copies files into git.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

# Relative crops (left, top, right, bottom) chosen to drop nametags, other
# people, and event slides while keeping Tanya's face/hair.
LIKENESS_CROPS: dict[str, tuple[float, float, float, float]] = {
    "014-front-smile-crop.jpg": (0.18, 0.10, 0.98, 0.72),
    "015-front-smile-outdoor-crop.jpg": (0.00, 0.00, 0.55, 0.55),
    "024-profile-stage-black.jpg": (0.00, 0.00, 1.00, 0.56),
    "045-threequarter-stage-black.jpg": (0.00, 0.00, 1.00, 0.54),
    "070-front-white-blouse-down.jpg": (0.10, 0.00, 0.90, 0.50),
    "075-threequarter-white-blouse.jpg": (0.10, 0.00, 0.90, 0.50),
    "086-threequarter-white-mic.jpg": (0.12, 0.00, 0.88, 0.30),
    "130-profile-stage-mic.jpg": (0.18, 0.00, 0.82, 0.88),
    "133-threequarter-tanya-slingsby-tag.jpg": (0.02, 0.00, 0.62, 0.68),
    "146-front-smile-blue-coat-crop.jpg": (0.36, 0.00, 0.82, 0.48),
}

# Source tile → (crop or None for copy) → destination name.
# Crops keep rooms/city and drop stock faces / readable PARK signage.
STYLE_PLATES: list[tuple[str, tuple[float, float, float, float] | None, str]] = [
    ("tile-039.jpg", None, "glass-geometry.jpg"),
    ("tile-040.jpg", (0.48, 0.00, 1.00, 0.48), "urban-canyon.jpg"),
    ("tile-016.jpg", (0.00, 0.00, 1.00, 0.40), "boardroom-windows.jpg"),
    ("tile-026.jpg", (0.00, 0.00, 0.55, 0.48), "city-through-window.jpg"),
    ("tile-029.jpg", (0.48, 0.00, 1.00, 0.42), "advisory-windows.jpg"),
]


def _box(size: tuple[int, int], rel: tuple[float, float, float, float]) -> tuple[int, int, int, int]:
    width, height = size
    left, top, right, bottom = rel
    return (
        int(width * left),
        int(height * top),
        max(int(width * left) + 1, int(width * right)),
        max(int(height * top) + 1, int(height * bottom)),
    )


def _write_jpeg(image: Image.Image, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    rgb = image.convert("RGB")
    rgb.save(dest, "JPEG", quality=92, optimize=True)


def crop_or_copy(src: Path, dest: Path, rel: tuple[float, float, float, float] | None) -> None:
    image = Image.open(src)
    if rel is not None:
        image = image.crop(_box(image.size, rel))
    _write_jpeg(image, dest)


def _reset_image_dir(dest_dir: Path, keep_names: set[str]) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    for path in dest_dir.iterdir():
        if path.name not in keep_names and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            path.unlink()


def prep_likeness(src_dir: Path, dest_dir: Path) -> int:
    written = 0
    _reset_image_dir(dest_dir, set(LIKENESS_CROPS))
    readme = dest_dir / "README.txt"
    readme.write_text(
        "Nametag-cropped Tanya refs for Gemini (local only).\n"
        "Do not commit. Raw frames stay in assets/slingsby/likeness/.\n"
    )
    for name, rel in LIKENESS_CROPS.items():
        src = src_dir / name
        if not src.is_file():
            continue
        crop_or_copy(src, dest_dir / name, rel)
        written += 1
    return written


def prep_style(tiles_dir: Path, dest_dir: Path) -> int:
    written = 0
    keep = {dest_name for _, _, dest_name in STYLE_PLATES}
    _reset_image_dir(dest_dir, keep)
    (dest_dir / "README.txt").write_text(
        "Face-free mood-board crops for Gemini style refs (local only).\n"
        "Full pages with stock faces stay in moodboard/pages/ and selected/.\n"
        "Do not attach those pages as Gemini style refs.\n"
    )
    for src_name, rel, dest_name in STYLE_PLATES:
        src = tiles_dir / src_name
        if not src.is_file():
            continue
        crop_or_copy(src, dest_dir / dest_name, rel)
        written += 1
    return written


def main() -> int:
    likeness_src = Path(os.environ.get("SLINGSBY_LIKENESS_DIR", ROOT / "assets/slingsby/likeness"))
    likeness_dest = Path(
        os.environ.get("SLINGSBY_LIKENESS_CLEAN_DIR", ROOT / "assets/slingsby/likeness-clean")
    )
    tiles_dir = Path(
        os.environ.get(
            "SLINGSBY_STYLE_TILES_DIR",
            ROOT / "assets/slingsby/style-refs/moodboard/tiles",
        )
    )
    style_dest = Path(
        os.environ.get(
            "SLINGSBY_FACE_FREE_DIR",
            ROOT / "assets/slingsby/style-refs/moodboard/face-free",
        )
    )

    likeness_n = prep_likeness(likeness_src, likeness_dest) if likeness_src.is_dir() else 0
    style_n = prep_style(tiles_dir, style_dest) if tiles_dir.is_dir() else 0
    print(f"likeness-clean: {likeness_n} file(s) -> {likeness_dest}")
    print(f"face-free style: {style_n} file(s) -> {style_dest}")
    if likeness_n == 0 and style_n == 0:
        print("Nothing to prep. Drop intake under assets/slingsby/ first.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

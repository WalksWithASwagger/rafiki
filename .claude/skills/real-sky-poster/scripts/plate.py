"""Stage 1 -- wipe the invented sky, keep the painting.

Erases every fabricated star and constellation stroke from the open sky and
leaves the aurora, gradient and brushwork untouched, producing a clean plate to
draw the real sky onto.

This is destructive and it is aimed at somebody's artwork, so the whole design
is defensive: the horizon line and protect boxes come from the profile, the
residual pass is gated on a dark local background, and `disturbance()` measures
whether any paint actually moved.

    python3 plate.py <profile.json> <out.png>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np


def load(profile_path: str) -> dict:
    with open(Path(profile_path).expanduser()) as fh:
        return json.load(fh)


def sky_mask(profile: dict, pad_protect: int = 0, scale: float = 1.0) -> np.ndarray:
    """255 where open sky lives. Geometry is authored at 1x and scaled up."""
    w = round(profile["width"] * scale)
    h = round(profile["height"] * scale)

    m = np.zeros((h, w), np.uint8)
    pts = [(x * scale, y * scale) for x, y in profile["horizon"]["points"]]
    cv2.fillPoly(m, [np.array(pts + [(w, 0), (0, 0)], np.int32)], 255)

    protect = np.zeros((h, w), np.uint8)
    boxes = [profile["protect"]["title"], *profile["protect"]["figures"]]
    for x0, y0, x1, y1 in boxes:
        cv2.rectangle(protect, (round(x0 * scale), round(y0 * scale)),
                      (round(x1 * scale), round(y1 * scale)), 255, -1)
    if pad_protect:
        k = max(1, round(pad_protect * scale))
        protect = cv2.dilate(protect, np.ones((k, k), np.uint8))

    return cv2.bitwise_and(m, cv2.bitwise_not(protect))


def wipe(profile: dict) -> np.ndarray:
    img = cv2.imread(str(Path(profile["source"]).expanduser())).astype(np.float32)
    if img is None:
        raise SystemExit(f"cannot read {profile['source']}")
    sky = sky_mask(profile)

    # A grayscale opening removes every bright point and hairline stroke. The
    # aurora is far wider than the structuring element, so it survives intact.
    opened = cv2.morphologyEx(
        img, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
    smooth = cv2.medianBlur(opened.astype(np.uint8), 7).astype(np.float32)
    smooth = cv2.GaussianBlur(smooth, (0, 0), 1.6)

    alpha = cv2.GaussianBlur(sky.astype(np.float32) / 255.0, (0, 0), 3.0)[..., None]
    plate = (smooth * alpha + img * (1 - alpha)).astype(np.uint8)
    return _residual_pass(profile, plate)


def _residual_pass(profile: dict, plate: np.ndarray) -> np.ndarray:
    """Fabricated dots that sit just *below* the horizon line, in the gaps
    between painted shapes. Three separate gates keep this off the artwork:
    a shallow band, dark-background only, and dot-sized blobs only. A painted
    highlight is bigger and sits on brighter ground than any drawn star."""
    h, w = plate.shape[:2]
    pts = profile["horizon"]["points"]

    band = np.zeros((h, w), np.uint8)
    lip = [(x, y + 62) for x, y in reversed(pts)]
    cv2.fillPoly(band, [np.array(pts + lip, np.int32)], 255)

    protect = np.zeros_like(band)
    for x0, y0, x1, y1 in [profile["protect"]["title"], *profile["protect"]["figures"]]:
        cv2.rectangle(protect, (x0, y0), (x1, y1), 255, -1)
    band[cv2.dilate(protect, np.ones((25, 25), np.uint8)) > 0] = 0

    # Only where stragglers actually survived. Elsewhere, paint sits right under
    # the line and must not be second-guessed.
    keep = np.zeros_like(band)
    for x0, x1 in profile["horizon"]["residual_zones"]:
        keep[:, x0:x1] = 255
    band = cv2.bitwise_and(band, keep)

    v = cv2.cvtColor(plate, cv2.COLOR_BGR2HSV)[..., 2]
    band[cv2.medianBlur(v, 31) > 58] = 0            # anything but open night sky

    th = cv2.morphologyEx(
        v, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    _, hits = cv2.threshold(cv2.bitwise_and(th, th, mask=band), 12, 255, cv2.THRESH_BINARY)

    dots = np.zeros_like(hits)
    n, lbl, stats, _ = cv2.connectedComponentsWithStats(hits, 8)
    for i in range(1, n):
        if stats[i][4] <= 70:
            dots[lbl == i] = 255
    dots = cv2.bitwise_and(cv2.dilate(dots, np.ones((5, 5), np.uint8)), band)
    return cv2.inpaint(plate, dots, 4, cv2.INPAINT_TELEA)


def disturbance(profile: dict, result: np.ndarray) -> int:
    """THE FIDELITY GATE. How many painted pixels moved?

    Saturated, bright pixels are the artwork: the salmon, the ravens, the type.
    None of them should change. Run this after every render. A number in the
    hundreds is new stars sitting over saturated aurora; a number in the
    thousands means the wipe ate somebody's painting."""
    src = cv2.imread(str(Path(profile["source"]).expanduser()))
    if result.shape != src.shape:
        result = cv2.resize(result, (src.shape[1], src.shape[0]), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    art = cv2.morphologyEx(
        ((hsv[..., 1] > 70) & (hsv[..., 2] > 80)).astype(np.uint8),
        cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    moved = np.abs(src.astype(int) - result.astype(int)).max(2) > 40
    return int((moved & (art > 0)).sum())


if __name__ == "__main__":
    prof = load(sys.argv[1])
    out = wipe(prof)
    cv2.imwrite(sys.argv[2], out)
    print(f"{sys.argv[2]}  painted px disturbed: {disturbance(prof, out)}")

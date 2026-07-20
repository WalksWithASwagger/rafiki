"""Stage 4 -- extend the sky, set the type, export every size.

Tall formats (1:1, 4:5, 9:16) GROW THE CANVAS UPWARD rather than centre-cropping.
Cropping a 16:9 poster to a square throws away the left and right edges -- which
is exactly where the constellations are. Growing upward means growing toward the
zenith, which is where the figures that could not fit the wide frame actually
were. So the tall formats gain real sky instead of losing it.

Nothing is outpainted: the gradient is extrapolated from the plate's own top
edge and the stars come from the catalogue.

    python3 kit.py <profile.json> <master.jpg> <outdir>
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from plate import load
from render import STYLES, StarPainter, place, radius, supersample_for
from sky import STARS, Sky

FONTS = Path(__file__).parent / "fonts"

WIDE = [("master-4x", None), ("web-hero", (2752, 1536)), ("luma-cover", (1920, 1080)),
        ("wide", (1600, 900)), ("twitter", (1200, 675)), ("og-share", (1200, 630))]
TALL = [("square", 1.0, (1080, 1080)), ("portrait", 1.25, (1080, 1350)),
        ("story", 16 / 9, (1080, 1920))]
STORY_SAFE_PX = 250          # platform UI eats the top and bottom of a 9:16 story


def extend(profile: dict, base: Image.Image, ext_units: float,
           style: str = "stars", seed: int = 20261028) -> Image.Image:
    """Grow `ext_units` (in 1x art units) of real sky above the artwork."""
    st = STYLES[style]
    scale = base.width / profile["width"]
    ext_px = round(ext_units * scale)
    arr = np.asarray(base.convert("RGB"), np.float32)

    sky_img = Image.fromarray(_gradient(arr, ext_px, scale, np.random.default_rng(seed)))

    obs = profile["observer"]
    sky = Sky(tuple(obs["utc"]), obs["lat"], obs["lon"])
    painter = StarPainter(profile["width"], ext_units,
                          scale * supersample_for(scale), st)

    rnd = random.Random(seed)
    taken = []
    for fig, (cx, fy, ppd) in profile["zenith"].items():
        if not sky.is_up(fig):
            continue
        for name, (x, y) in place(sky, fig, cx, (1.0 - fy) * ext_units, ppd).items():
            # These carry the extension, so give them a touch more presence.
            painter.star(x, y, radius(STARS[name][2], st["star_gain"] * 1.18))
            taken.append((x, y))

    # A vast empty sky at the painting's own star density reads as static, not
    # as stars. Thin it out.
    n_field = round(st["field"] * (profile["width"] * ext_units) / 252_000 * 0.42)
    n = 0
    while n < n_field:
        x, y = rnd.uniform(0, profile["width"]), rnd.uniform(0, ext_units)
        if any(abs(x - tx) < 9 and abs(y - ty) < 9 for tx, ty in taken):
            continue
        painter.star(x, y, radius(rnd.triangular(3.8, 6.4, 5.7), st["star_gain"]),
                     warmth=rnd.uniform(0.93, 1.0), bright=rnd.uniform(0.45, 0.95))
        n += 1

    layer = painter.compose((base.width, ext_px))
    sky_img = Image.alpha_composite(sky_img.convert("RGBA"), layer).convert("RGB")

    out = Image.new("RGB", (base.width, ext_px + base.height))
    out.paste(sky_img, (0, 0))
    out.paste(base, (0, ext_px))
    return out


def _gradient(arr: np.ndarray, ext_px: int, scale: float, rng) -> np.ndarray:
    """Extrapolate the plate's own top edge upward, fading to deep night."""
    w = arr.shape[1]
    edge = arr[:max(2, round(6 * scale))].mean(axis=0)
    edge = np.asarray(Image.fromarray(edge[None].astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(40 * scale)), np.float32)[0]

    deep = np.percentile(arr.reshape(-1, 3), 4, axis=0) * 0.82
    t = (np.linspace(0, 1, ext_px)[::-1] ** 0.85)[:, None, None]
    grad = edge[None] * (1 - t) + deep[None, None] * t

    # Low-frequency mottle, or the gradient bands visibly across a big canvas.
    noise = rng.normal(0, 1, (max(1, ext_px // 24), max(1, w // 24)))
    noise = np.asarray(Image.fromarray(((noise * 40) + 128).clip(0, 255).astype(np.uint8))
                       .resize((w, ext_px), Image.BICUBIC)
                       .filter(ImageFilter.GaussianBlur(6 * scale)), np.float32)[..., None]
    return (grad + (noise - 128) * 0.055).clip(0, 255).astype(np.uint8)


def _font(name: str, px: int, weight: str):
    f = ImageFont.truetype(str(FONTS / f"{name}.ttf"), px)
    f.set_variation_by_name(weight)
    return f


def _wrap(draw, text, fnt, max_w):
    """Balanced, not greedy. Greedy leaves orphans -- a line reading just
    'year.' -- so once the line count is known, squeeze the measure to the
    narrowest width that still fits in that many lines."""
    def greedy(limit):
        lines, cur = [], ""
        for word in text.split():
            t = f"{cur} {word}".strip()
            if draw.textlength(t, font=fnt) <= limit or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = word
        return lines + ([cur] if cur else [])

    n = len(greedy(max_w))
    lo, hi = 1, max_w
    while hi - lo > 1:
        mid = (lo + hi) / 2
        if len(greedy(mid)) <= n:
            hi = mid
        else:
            lo = mid
    return greedy(hi)


def _tracked(draw, text, fnt, cx, y, fill, track):
    """Letterspaced and centred. PIL has no tracking, so place glyph by glyph."""
    widths = [draw.textlength(c, font=fnt) for c in text]
    x = cx - (sum(widths) + track * (len(text) - 1)) / 2
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=fnt, fill=fill)
        x += w + track


def set_type(profile: dict, img: Image.Image, ext_px: int, line: str,
             date: bool = False) -> Image.Image:
    """Type sits in the sky, above the painted title.

    The type layer adds only what the painting does not already say. If the
    artwork carries a wordmark, do not stack a second one on top of it.
    """
    pal = profile["copy"]["palette"]
    d = ImageDraw.Draw(img, "RGBA")
    w = img.width
    cx = w / 2

    big = _font("Cormorant", round(w * 0.062), "Medium")
    small = _font("Inter", round(w * 0.0165), "Medium")
    tiny = _font("Inter", round(w * 0.0150), "Regular")

    lines = _wrap(d, line, big, w * 0.80)
    lh, gap = round(w * 0.070), round(w * 0.045)
    tail = gap + round(w * 0.030) * (3 if date else 2)
    bottom = ext_px - round(w * 0.075)
    y = bottom - (len(lines) * lh + tail)

    scrim = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(scrim).rectangle(
        [0, y - lh * 0.6, w, bottom + lh * 0.3], fill=(*pal["ink"], 92))
    img.alpha_composite(scrim.filter(ImageFilter.GaussianBlur(w * 0.045)))

    for ln in lines:
        d.text((cx, y), ln, font=big, fill=(*pal["parchment"], 255), anchor="ma")
        y += lh

    y += gap
    _tracked(d, profile["copy"]["venue"].upper(), small, cx, y,
             (*pal["aurora"], 235), w * 0.0028)
    y += round(w * 0.030)
    if date:
        # A 9:16 story has platform UI over its bottom 250px -- which is often
        # exactly where a painted date sits. Restate it up here so it survives.
        _tracked(d, profile["copy"]["date"].upper(), small, cx, y,
                 (*pal["ember"], 225), w * 0.0028)
        y += round(w * 0.030)
    _tracked(d, profile["copy"]["url"].upper(), tiny, cx, y,
             (*pal["parchment"], 175), w * 0.0040)
    return img


def _fit(master: Image.Image, target: tuple[int, int]) -> Image.Image:
    """Ratios that are not the artwork's own (an OG card, say) centre-crop."""
    tw, th = target
    want = tw / th
    w, h = master.size
    if abs(want - w / h) > 0.005:
        nh = round(w / want)
        top = (h - nh) // 2
        master = master.crop((0, top, w, top + nh))
    return master.resize(target, Image.LANCZOS)


def build(profile: dict, master_path: str, outdir: str) -> list[Path]:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    master = Image.open(master_path).convert("RGB")
    name = profile["name"]
    made = []

    for label, size in WIDE:
        img = master if size is None else _fit(master, size)
        p = out / f"{name}-{label}-{img.width}x{img.height}.jpg"
        img.save(p, quality=94, subsampling=0)
        made.append(p)

    # A smaller base keeps the extension cheap; it still oversamples 1080.
    base_h = round(2752 * profile["height"] / profile["width"])
    base = master.resize((2752, base_h), Image.LANCZOS)
    aw = profile["width"]

    for label, ratio, size in TALL:
        ext_units = aw * ratio - profile["height"]
        tall = extend(profile, base, ext_units)
        scale = base.width / aw
        ext_px = round(ext_units * scale * size[0] / tall.width)

        clean = tall.resize(size, Image.LANCZOS)
        p = out / f"{name}-{label}-{size[0]}x{size[1]}.jpg"
        clean.save(p, quality=94, subsampling=0)
        made.append(p)

        titled = set_type(profile, tall.resize(size, Image.LANCZOS).convert("RGBA"),
                          ext_px, profile["copy"]["line"], date=(label == "story"))
        p = out / f"{name}-{label}-titled-{size[0]}x{size[1]}.jpg"
        titled.convert("RGB").save(p, quality=94, subsampling=0)
        made.append(p)

    return made


if __name__ == "__main__":
    prof = load(sys.argv[1])
    files = build(prof, sys.argv[2], sys.argv[3])
    for f in files:
        im = Image.open(f)
        print(f"  {f.name:<58} {im.width}x{im.height}")
    print(f"\n{len(files)} files -> {sys.argv[3]}")

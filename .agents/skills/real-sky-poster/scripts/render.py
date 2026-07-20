"""Stage 3 -- draw the real stars, at any resolution.

Stars are drawn procedurally from the catalogue, so every output is native.
Nothing here is ever upscaled: a 4x poster gets 4x stars, not 4x-blurry ones.
That is the whole reason the pipeline upscales the *plate* and redraws, rather
than upscaling a finished image.

    python3 render.py <profile.json> <plate.png> <out.jpg> [scale]
"""

from __future__ import annotations

import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from plate import load, sky_mask
from sky import GROUPS, STARS, Sky

STYLES = {
    # The default. No connecting lines: accurate positions, nothing else. Reads
    # as sky rather than as an infographic, and never fights the artwork.
    "stars": dict(line=None, line_a=0, line_w=0, star_gain=1.05, halo=1.25,
                  spikes=True, field=300),
    "lines": dict(line=(226, 245, 248), line_a=74, line_w=1.25, star_gain=1.10,
                  halo=1.35, spikes=True, field=250),
    "delicate": dict(line=(214, 236, 240), line_a=50, line_w=1.0, star_gain=0.90,
                     halo=0.85, spikes=False, field=230),
}

EDGES = {
    "Ursa Major": [("Dubhe", "Merak"), ("Merak", "Phecda"), ("Phecda", "Megrez"),
                   ("Megrez", "Dubhe"), ("Megrez", "Alioth"), ("Alioth", "Mizar"),
                   ("Mizar", "Alkaid")],
    "Cassiopeia": [("Caph", "Schedar"), ("Schedar", "gam Cas"),
                   ("gam Cas", "Ruchbah"), ("Ruchbah", "Segin")],
    "Cygnus": [("Deneb", "Sadr"), ("Sadr", "Albireo"), ("del Cyg", "Sadr"),
               ("Sadr", "Gienah")],
    "Lyra": [("Vega", "eps Lyr"), ("Vega", "zet Lyr"), ("zet Lyr", "bet Lyr"),
             ("bet Lyr", "gam Lyr"), ("gam Lyr", "zet Lyr")],
    "Perseus": [("gam Per", "Mirfak"), ("Mirfak", "del Per"), ("del Per", "eps Per"),
                ("eps Per", "zet Per"), ("Mirfak", "Algol"), ("Algol", "eps Per")],
}


def radius(vmag: float, gain: float) -> float:
    """Brighter star, bigger dot. Roughly perceptual, clamped for legibility."""
    return max(0.80, min(3.3, (6.9 - vmag) * 0.46)) * gain


def supersample_for(scale: float) -> int:
    """Enough antialiasing to hide PIL's hard-edged ellipses, without building a
    22k-wide RGBA buffer at 4x."""
    return 4 if scale <= 1 else 2


class StarPainter:
    """Draws in 1x coordinates onto a canvas `unit` times larger, then
    downsamples. Halos are small solid discs, gaussian-blurred afterwards, so
    they fall off smoothly instead of reading as flat grey bubbles."""

    def __init__(self, w1x: float, h1x: float, unit: float, style: dict) -> None:
        self.u, self.st = unit, style
        big = (round(w1x * unit), round(h1x * unit))
        self.lines = Image.new("RGBA", big, (0, 0, 0, 0))
        self.near = Image.new("RGBA", big, (0, 0, 0, 0))
        self.far = Image.new("RGBA", big, (0, 0, 0, 0))
        self.core = Image.new("RGBA", big, (0, 0, 0, 0))
        self.dl, self.dn, self.df, self.dc = (
            ImageDraw.Draw(i) for i in (self.lines, self.near, self.far, self.core))

    def _disc(self, d, x, y, r, colour) -> None:
        u = self.u
        d.ellipse([(x - r) * u, (y - r) * u, (x + r) * u, (y + r) * u], fill=colour)

    def star(self, x, y, r, warmth=1.0, bright=1.0) -> None:
        halo = self.st["halo"]
        self._disc(self.dn, x, y, r * 1.25 * halo, (176, 216, 236, int(185 * bright)))
        if r > 1.35:
            self._disc(self.df, x, y, r * 1.7 * halo, (150, 205, 230, int(120 * bright)))

        c = (255, int(253 * warmth), int(246 * warmth), int(255 * min(1.0, bright)))
        self._disc(self.dc, x, y, r * 0.78, c)
        if self.st["spikes"] and r > 2.0:
            length, w = r * 4.2, max(1, round(0.55 * self.u))
            for dx, dy in ((length, 0), (0, length)):
                self.dc.line([(x - dx) * self.u, (y - dy) * self.u,
                              (x + dx) * self.u, (y + dy) * self.u],
                             fill=(*c[:3], 52), width=w)

    def line(self, p, q) -> None:
        u = self.u
        self.dl.line([p[0] * u, p[1] * u, q[0] * u, q[1] * u],
                     fill=(*self.st["line"], self.st["line_a"]),
                     width=max(1, round(self.st["line_w"] * u)))

    def compose(self, out_size):
        near = self.near.filter(ImageFilter.GaussianBlur(2.2 * self.u))
        far = self.far.filter(ImageFilter.GaussianBlur(7.0 * self.u))
        layer = Image.new("RGBA", self.lines.size, (0, 0, 0, 0))
        for lyr in (self.lines, far, near, self.core):
            layer = Image.alpha_composite(layer, lyr)
        return layer.resize(out_size, Image.LANCZOS)


def place(sky: Sky, figure: str, cx: float, cy: float, ppd: float):
    local = sky.project(GROUPS[figure], ppd)
    mx = sum(p[0] for p in local.values()) / len(local)
    my = sum(p[1] for p in local.values()) / len(local)
    return {n: (cx + x - mx, cy + y - my) for n, (x, y) in local.items()}


def render(profile: dict, plate_path: str, scale: float = 1.0,
           style: str = "stars", seed: int = 28102026) -> Image.Image:
    st = STYLES[style]
    base = Image.open(plate_path).convert("RGB")
    w1x, h1x = profile["width"], profile["height"]
    want = (round(w1x * scale), round(h1x * scale))
    if base.size != want:
        raise SystemExit(f"plate is {base.size}, scale {scale} wants {want}")

    obs = profile["observer"]
    sky = Sky(tuple(obs["utc"]), obs["lat"], obs["lon"])

    for fig in profile["layout"]:
        if not sky.is_up(fig):
            raise SystemExit(f"{fig} is below the horizon on this date. Do not draw it.")

    painter = StarPainter(w1x, h1x, scale * supersample_for(scale), st)
    mask = sky_mask(profile, pad_protect=6, scale=scale)
    pos = {f: place(sky, f, *xy) for f, xy in profile["layout"].items()}

    if st["line"]:
        for fig, edges in EDGES.items():
            if fig in pos:
                for a, b in edges:
                    painter.line(pos[fig][a], pos[fig][b])

    rnd = random.Random(seed)
    taken = [(x, y) for f in pos.values() for x, y in f.values()]
    n = 0
    while n < st["field"]:
        x, y = rnd.uniform(0, w1x), rnd.uniform(0, h1x)
        gy = min(int(y * scale), mask.shape[0] - 1)
        gx = min(int(x * scale), mask.shape[1] - 1)
        if mask[gy, gx] == 0:
            continue
        if any(abs(x - tx) < 9 and abs(y - ty) < 9 for tx, ty in taken):
            continue
        painter.star(x, y, radius(rnd.triangular(3.8, 6.4, 5.7), st["star_gain"]),
                     warmth=rnd.uniform(0.93, 1.0), bright=rnd.uniform(0.45, 0.95))
        n += 1

    for stars in pos.values():
        for name, (x, y) in stars.items():
            painter.star(x, y, radius(STARS[name][2], st["star_gain"]))

    layer = painter.compose(base.size)

    # Nothing may spill onto the artwork.
    alpha = np.array(layer.getchannel("A"), np.float32)
    keep = np.array(Image.fromarray(mask).filter(
        ImageFilter.GaussianBlur(1.5 * scale)), np.float32) / 255.0
    layer.putalpha(Image.fromarray((alpha * keep).astype(np.uint8)))

    return Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")


if __name__ == "__main__":
    prof = load(sys.argv[1])
    img = render(prof, sys.argv[2], float(sys.argv[4]) if len(sys.argv) > 4 else 1.0)
    img.save(sys.argv[3], quality=95, subsampling=0)
    print(f"{sys.argv[3]}  {img.width}x{img.height}")
    print(Sky(tuple(prof["observer"]["utc"]),
              prof["observer"]["lat"], prof["observer"]["lon"]).report())

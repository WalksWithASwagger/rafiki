"""Stage 2 -- upscale the clean plate with a local ESRGAN.

Runs locally with torch and spandrel. No server, API, or provider call.

Upscale the PLATE, not the finished poster. The stars get redrawn natively
afterwards, so they stay razor sharp instead of becoming blurry blobs. The
upscaler also never sees a fabricated dot, which is one less thing for it to
sharpen into an artifact.

Use an illustration-trained model (4x-UltraSharp, 4x_foolhardy_Remacri). Do NOT
use RealESRGAN_x4plus: it is photo-trained and will plasticize brushwork.

    python3 upscale.py <in.png> <out.png> --model <weights.pth>
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

TILE, OVERLAP = 512, 32


def upscale(src: Path, dst: Path, model_path: Path) -> None:
    import numpy as np
    import torch
    from PIL import Image
    from spandrel import ModelLoader

    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    model = ModelLoader().load_from_file(str(model_path)).eval().to(dev)
    s = model.scale
    print(f"{model.architecture.name}  x{s}  on {dev}")

    img = Image.open(src).convert("RGB")
    w, h = img.size
    x = torch.from_numpy(np.asarray(img, np.float32) / 255.0).permute(2, 0, 1)[None].to(dev)

    out = torch.zeros(1, 3, h * s, w * s, device=dev)
    weight = torch.zeros(1, 1, h * s, w * s, device=dev)
    step = TILE - OVERLAP
    t0 = time.time()

    with torch.no_grad():
        for ty in range(0, h, step):
            for tx in range(0, w, step):
                x0, y0 = min(tx, max(0, w - TILE)), min(ty, max(0, h - TILE))
                x1, y1 = min(x0 + TILE, w), min(y0 + TILE, h)
                tile = model(x[:, :, y0:y1, x0:x1]).clamp(0, 1)

                # Cosine feather, or tile seams show in the smooth sky gradient.
                th, tw = tile.shape[-2:]
                fy = torch.hann_window(th, periodic=False, device=dev).clamp(min=1e-3)
                fx = torch.hann_window(tw, periodic=False, device=dev).clamp(min=1e-3)
                wgt = (fy[:, None] * fx[None, :])[None, None]

                out[:, :, y0 * s:y0 * s + th, x0 * s:x0 * s + tw] += tile * wgt
                weight[:, :, y0 * s:y0 * s + th, x0 * s:x0 * s + tw] += wgt

    out = (out / weight.clamp(min=1e-6)).clamp(0, 1)
    arr = (out[0].permute(1, 2, 0).cpu().numpy() * 255).round().astype(np.uint8)
    Image.fromarray(arr).save(dst)
    print(f"{w}x{h} -> {arr.shape[1]}x{arr.shape[0]}  in {time.time() - t0:.1f}s  -> {dst}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Upscale a clean poster plate with local ESRGAN weights.")
    parser.add_argument("input", type=Path, help="clean plate image")
    parser.add_argument("output", type=Path, help="destination image")
    parser.add_argument("--model", required=True, type=Path, help="ESRGAN model weights")
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"input file not found: {args.input}")
    if not args.model.is_file():
        parser.error(f"model file not found: {args.model}")

    upscale(args.input, args.output, args.model)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

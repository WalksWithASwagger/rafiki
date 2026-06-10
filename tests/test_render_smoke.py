from __future__ import annotations

import shutil
import struct
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_JS = REPO_ROOT / "index.js"

# Fixed viewport set in index.js renderHtmlFiles (page.setViewport).
EXPECTED_WIDTH = 1200
EXPECTED_HEIGHT = 630

FIXTURE_HTML = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <style>
      html, body { margin: 0; padding: 0; }
      body {
        width: 1200px;
        height: 630px;
        background: #0b1021;
        color: #f5f5f5;
        font-family: sans-serif;
        display: flex;
        align-items: center;
        justify-content: center;
      }
    </style>
  </head>
  <body>
    <h1>Rafiki render smoke test</h1>
  </body>
</html>
"""


def _png_dimensions(png_path: Path) -> tuple[int, int]:
    """Read width/height from a PNG IHDR chunk without extra dependencies."""
    header = png_path.read_bytes()[:24]
    assert header[:8] == b"\x89PNG\r\n\x1a\n", "output is not a valid PNG"
    width, height = struct.unpack(">II", header[16:24])
    return width, height


@pytest.mark.skipif(
    shutil.which("node") is None,
    reason="node is required to run the Rafiki CLI render path",
)
@pytest.mark.skipif(
    not (REPO_ROOT / "node_modules" / "puppeteer").exists(),
    reason="puppeteer is not installed (run npm install)",
)
def test_render_html_to_png_smoke(tmp_path: Path) -> None:
    html_path = tmp_path / "card.html"
    html_path.write_text(FIXTURE_HTML, encoding="utf-8")

    proc = subprocess.run(
        ["node", str(INDEX_JS), "--render", str(html_path)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=120,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr

    png_path = tmp_path / "card.png"
    assert png_path.exists(), f"expected PNG at {png_path}\n{proc.stdout}\n{proc.stderr}"
    assert png_path.stat().st_size > 0

    width, height = _png_dimensions(png_path)
    assert (width, height) == (EXPECTED_WIDTH, EXPECTED_HEIGHT)

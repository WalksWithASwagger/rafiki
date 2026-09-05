"""Local Slingsby taste-gate page (no provider calls)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "slingsby-proposal-taste-gate.py"


def _load():
    spec = importlib.util.spec_from_file_location("slingsby_taste_gate", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _png(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (32, 32), (80, 80, 80)).save(path, "PNG")


def test_taste_gate_links_refs_and_runs_without_embedding(tmp_path: Path) -> None:
    module = _load()
    output = tmp_path / "out"
    style = output / "run-20260822-style"
    likeness = output / "run-20260822-likeness"
    _png(style / "07-urban-canyon.png")
    (style / "run.json").write_text('{"reference_role":"style","state":"succeeded"}\n')
    _png(likeness / "01-hero-three-quarter.png")
    (likeness / "run.json").write_text(
        '{"reference_role":"likeness","state":"succeeded"}\n'
    )
    refs = tmp_path / "likeness-clean"
    refs.mkdir()
    Image.new("RGB", (32, 32), (20, 20, 20)).save(
        refs / "014-front-smile-crop.jpg", "JPEG"
    )

    page = module.build_taste_gate(output_dir=output, likeness_dir=refs)
    html = page.read_text()
    assert page.name == "taste-gate.html"
    assert "014-front-smile-crop.jpg" in html
    assert "07-urban-canyon.png" in html
    assert "01-hero-three-quarter.png" in html
    assert "data:image" not in html
    assert "GOOGLE_API_KEY" not in html
    assert "../likeness-clean/014-front-smile-crop.jpg" in html

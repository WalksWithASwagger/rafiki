"""Tests for the --self-contained / --max-width modes of the presentation viewer."""

from __future__ import annotations

import base64
import importlib.util
import io
import re
import sys
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

import pytest
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "generate-presentation-viewer.py"


def _load_viewer_module():
    spec = importlib.util.spec_from_file_location("viewer_module", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["viewer_module"] = module
    spec.loader.exec_module(module)
    return module


viewer = _load_viewer_module()


def _write_png(path: Path, size=(10, 10), color=(255, 0, 0)) -> None:
    Image.new("RGB", size, color).save(path, format="PNG")


def _make_data(image_root: Path, slugs=("a", "b")) -> Dict[str, Any]:
    return {
        "title": "Test",
        "subtitle": "Test sub",
        "header": {
            "logo": "x",
            "style_label": "test",
            "style_meta": "meta",
            "style_description": "desc",
        },
        "category_field": "week",
        "category_label_singular": "Week",
        "all_tab_label": "All Weeks",
        "categories": [{"id": 1, "label": "Week 1", "short": "W1"}],
        "image_dirs": {"1": str(image_root)},
        "items": [
            {"category": 1, "slug": slug, "title": f"Title {slug}", "caption": f"Cap {slug}"}
            for slug in slugs
        ],
    }


def test_default_uses_relative_paths(tmp_path):
    images = tmp_path / "imgs"
    images.mkdir()
    _write_png(images / "a.png")
    _write_png(images / "b.png")

    output = tmp_path / "out"
    output.mkdir()

    data = _make_data(images)
    html = viewer.build_viewer(data, output)

    assert "data:image/png;base64," not in html
    # The rendered items array uses the relative path
    assert "../imgs/a.png" in html
    assert "../imgs/b.png" in html


def test_self_contained_embeds_base64(tmp_path):
    images = tmp_path / "imgs"
    images.mkdir()
    _write_png(images / "a.png")
    _write_png(images / "b.png")

    output = tmp_path / "out"
    output.mkdir()

    data = _make_data(images)
    html = viewer.build_viewer(data, output, self_contained=True)

    # Two data URIs embedded
    assert html.count('"src": "data:image/png;base64,') == 2
    # No relative path src remaining
    assert "../imgs/a.png" not in html
    assert "../imgs/b.png" not in html


def test_max_width_resizes_images(tmp_path):
    images = tmp_path / "imgs"
    images.mkdir()
    _write_png(images / "a.png", size=(2000, 1000))

    output = tmp_path / "out"
    output.mkdir()

    data = _make_data(images, slugs=("a",))
    html = viewer.build_viewer(data, output, self_contained=True, max_width=800)

    match = re.search(r'"src": "data:image/png;base64,([A-Za-z0-9+/=]+)"', html)
    assert match is not None, "no embedded data URI found"
    payload = base64.b64decode(match.group(1))
    with Image.open(io.BytesIO(payload)) as im:
        assert im.size == (800, 400)


def test_size_warning_emitted_above_threshold(tmp_path, capsys):
    images = tmp_path / "imgs"
    images.mkdir()
    _write_png(images / "a.png")

    output = tmp_path / "out"
    output.mkdir()

    data = _make_data(images, slugs=("a",))

    # Mock the encoder to return a payload that exceeds the 50 MB threshold.
    big_payload = "data:image/png;base64," + ("A" * (51 * 1024 * 1024))
    with patch.object(viewer, "_encode_image_data_uri", return_value=big_payload):
        argv = [
            "generate-presentation-viewer.py",
            "--data", "ignored",
            "--output", str(output),
            "--self-contained",
        ]
        with patch.object(sys, "argv", argv), patch.object(viewer, "_load_data", return_value=data):
            viewer.main()

    captured = capsys.readouterr()
    assert "warning" in captured.err.lower()
    assert "50.0 MB" in captured.err or "embedded image payload" in captured.err

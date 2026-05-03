"""Tests for social post export from the presentation viewer."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parent.parent
GEN_PATH = REPO_ROOT / "generate-presentation-viewer.py"

spec = importlib.util.spec_from_file_location("generate_presentation_viewer", GEN_PATH)
gpv = importlib.util.module_from_spec(spec)
sys.modules["generate_presentation_viewer"] = gpv
spec.loader.exec_module(gpv)


def _data_with_social() -> Dict[str, Any]:
    return {
        "title": "Test Series",
        "subtitle": "subtitle",
        "header": {"logo": "T", "style_label": "x", "style_meta": "", "style_description": ""},
        "category_field": "week",
        "category_label_singular": "Week",
        "all_tab_label": "All",
        "categories": [
            {"id": 1, "label": "Week 1 — A", "short": "W1"},
            {"id": 2, "label": "Week 2 — B", "short": "W2"},
        ],
        "image_dirs": {"1": "output/test-1", "2": "output/test-2"},
        "items": [
            {"category": 1, "slug": "01-foo", "title": "Foo Title",
             "caption": "Foo caption.", "social": "Foo social copy.\n\n#tag"},
            {"category": 1, "slug": "02-bar", "title": "Bar Title",
             "caption": "Bar caption.", "social": None},
            {"category": 2, "slug": "01-baz", "title": "Baz Title",
             "caption": "Baz caption.", "social": "Baz social copy."},
        ],
    }


def _data_without_social() -> Dict[str, Any]:
    data = _data_with_social()
    for item in data["items"]:
        item["social"] = None
    return data


def test_social_posts_md_emitted(tmp_path):
    data = _data_with_social()
    md = gpv.build_social_posts_md(data, tmp_path)
    assert md is not None
    assert "## W1 · Foo Title" in md
    assert "## W2 · Baz Title" in md
    assert "## W1 · Bar Title" not in md
    assert "**Caption:** Foo caption." in md
    assert "Foo social copy." in md
    assert "Baz social copy." in md
    assert "```" in md
    assert md.count("---") >= 2


def test_social_posts_md_skipped_when_no_social_items(tmp_path):
    data = _data_without_social()
    assert gpv.build_social_posts_md(data, tmp_path) is None


def test_export_button_in_html_when_social_items_present(tmp_path):
    html = gpv.build_viewer(_data_with_social(), tmp_path)
    assert 'id="export-social"' in html
    assert "Export social posts" in html
    assert "test-series-social-posts.txt" in html
    assert "URL.createObjectURL" in html


def test_export_button_absent_when_no_social_items(tmp_path):
    html = gpv.build_viewer(_data_without_social(), tmp_path)
    assert 'id="export-social"' not in html
    assert "Export social posts" not in html
    assert "URL.createObjectURL" not in html

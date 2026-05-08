"""Tests for social post export from the presentation viewer."""

from __future__ import annotations

import importlib.util
import json
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


def _data_with_social_posts_json(tmp_path: Path) -> Dict[str, Any]:
    run_dir = tmp_path / "run-20260101-000000"
    run_dir.mkdir()
    (run_dir / "social-posts.json").write_text(
        json.dumps({
            "01-foo": {
                "title": "Foo Title",
                "caption": "Foo caption.",
                "platforms": {
                    "linkedin": "LinkedIn copy",
                    "x": "X copy",
                    "instagram": "Instagram copy",
                },
            }
        }),
        encoding="utf-8",
    )
    data = _data_without_social()
    data["image_dirs"] = {"1": str(run_dir), "2": str(tmp_path / "missing")}
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


def test_viewer_loads_platform_social_posts_json(tmp_path):
    html = gpv.build_viewer(_data_with_social_posts_json(tmp_path), tmp_path)

    assert '"socialPlatforms": {' in html
    assert '"linkedin": "LinkedIn copy"' in html
    assert '"x": "X copy"' in html
    assert '"instagram": "Instagram copy"' in html
    assert 'id="lb-social-tabs"' in html
    assert "function socialEntries(item)" in html
    assert "renderSocialTabs(entries, 0)" in html
    assert 'id="export-social"' in html


def test_social_posts_md_includes_platform_variants_from_json(tmp_path):
    md = gpv.build_social_posts_md(_data_with_social_posts_json(tmp_path), tmp_path)

    assert md is not None
    assert "**LinkedIn:**" in md
    assert "LinkedIn copy" in md
    assert "**X:**" in md
    assert "X copy" in md
    assert "**Instagram:**" in md
    assert "Instagram copy" in md

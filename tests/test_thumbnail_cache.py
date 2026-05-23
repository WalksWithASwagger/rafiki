from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

from lib.archive_health import archive_health_report
from lib.renderers.library import generate_library_viewer
from lib.renderers.viewer import generate_comparison_viewer, generate_viewer
from lib.thumbnail_cache import build_thumbnail_cache, thumbnail_cache_stats


REPO_ROOT = Path(__file__).resolve().parent.parent


def _write_png(path: Path, size: tuple[int, int] = (1200, 800)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color=(40, 80, 120)).save(path)


def _write_run(run_dir: Path, image_name: str = "hero.png") -> None:
    _write_png(run_dir / image_name)
    (run_dir / "run.json").write_text(
        json.dumps({
            "model": "gpt-image-2",
            "aspect_ratio": "16:9",
            "timestamp": "2026-05-22 12:00",
            "images": [{"file": image_name, "name": "Hero", "prompt": "hero prompt"}],
        }),
        encoding="utf-8",
    )


def test_thumbnail_cache_writes_gitignored_local_previews_and_keeps_original_key(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    source = output_root / "demo" / "run-20260522-120000" / "hero.png"
    _write_png(source)
    records = [{"file": "demo/run-20260522-120000/hero.png"}]

    summary = build_thumbnail_cache(output_root, records, width=320)

    assert summary["created"] == 1
    assert records[0]["file"] == "demo/run-20260522-120000/hero.png"
    assert records[0]["thumbnail_file"].startswith(".rafiki-cache/thumbnails/v1/w320/")
    assert (output_root / records[0]["thumbnail_file"]).exists()


def test_library_thumbnail_cache_uses_thumbnail_for_card_but_original_for_lightbox(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    _write_run(output_root / "demo" / "run-20260522-120000")

    html = generate_library_viewer(output_root, thumbnail_cache=True, thumbnail_width=320).read_text(encoding="utf-8")

    assert '"file": "demo/run-20260522-120000/hero.png"' in html
    assert '"thumbnail_file": ".rafiki-cache/thumbnails/v1/w320/' in html
    assert "resolveAssetSrc(item.thumbnail_file || item.file)" in html
    assert "const rawImgSrc = prefix + item.file;" in html


def test_project_and_run_viewers_use_cached_grid_previews_only_when_requested(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    run_dir = output_root / "demo" / "run-20260522-120000"
    _write_run(run_dir)

    run_html = generate_viewer(
        run_dir,
        [{"name": "Hero", "prompt": "hero prompt", "output_path": str(run_dir / "hero.png")}],
        thumbnail_cache=True,
        thumbnail_width=320,
    ).read_text(encoding="utf-8")
    project_html = generate_comparison_viewer(
        output_root / "demo",
        thumbnail_cache=True,
        thumbnail_width=320,
    ).read_text(encoding="utf-8")

    assert '"thumbnail_file": "../../.rafiki-cache/thumbnails/v1/w320/' in run_html
    assert '"thumbnail_file": "../.rafiki-cache/thumbnails/v1/w320/' in project_html
    assert "${item.thumbnail_file || item.file}" in run_html
    assert "${item.thumbnail_file || (run.dir + '/' + item.file)}" in project_html


def test_archive_thumbnails_cli_and_health_report_cache_stats(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    _write_run(output_root / "demo" / "run-20260522-120000")

    result = subprocess.run(
        [
            sys.executable,
            "generate.py",
            "archive-thumbnails",
            "--output-dir",
            str(output_root),
            "--width",
            "320",
            "--json",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    report = archive_health_report(output_root)
    stats = thumbnail_cache_stats(output_root)

    assert payload["created"] == 1
    assert stats["files"] == 1
    assert report["thumbnail_cache"]["files"] == 1
    assert ".rafiki-cache/thumbnails" in report["thumbnail_cache"]["path"]

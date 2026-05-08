from __future__ import annotations

import json
import subprocess
from pathlib import Path

from lib.renderers.viewer import generate_comparison_viewer, generate_viewer


REPO_ROOT = Path(__file__).resolve().parent.parent
PNG_HEADER = b"\x89PNG\r\n\x1a\n"


def _write_run(project_dir: Path, run_name: str, aspect_ratio: str, images: list[dict]) -> Path:
    run_dir = project_dir / run_name
    run_dir.mkdir(parents=True)
    (run_dir / "run.json").write_text(
        json.dumps(
            {
                "model": "gpt-image-2",
                "aspect_ratio": aspect_ratio,
                "timestamp": "2026-05-08 12:00",
                "images": images,
            }
        ),
        encoding="utf-8",
    )
    return run_dir


def test_comparison_viewer_rechecks_files_and_keeps_per_run_aspect_ratios(tmp_path: Path) -> None:
    project_dir = tmp_path / "viewer-project"
    first = _write_run(
        project_dir,
        "run-20260508-120000",
        "16:9",
        [
            {
                "name": "Missing Hero",
                "prompt": "missing",
                "file": "missing.png",
                "ok": True,
                "error": "provider returned no image",
            }
        ],
    )
    second = _write_run(
        project_dir,
        "run-20260508-121000",
        "9:16",
        [{"name": "Portrait", "prompt": "present", "file": "portrait.png", "ok": True}],
    )
    (second / "portrait.png").write_bytes(PNG_HEADER + b"present")

    viewer_path = generate_comparison_viewer(project_dir)
    html = viewer_path.read_text(encoding="utf-8")

    assert '"file": "missing.png", "ok": false' in html
    assert "provider returned no image" in html
    assert 'const arCss = (run.aspect_ratio || \'16:9\').replace(\':\', \'/\');' in html
    assert 'const runArCss = (run.aspect_ratio || \'16:9\').replace(\':\', \'/\');' in html
    assert "aspect-ratio:${arCss}" in html
    assert "aspect-ratio:${runArCss}" in html
    assert str(first) not in html


def test_single_viewer_degrades_broken_images_to_placeholder(tmp_path: Path) -> None:
    run_dir = tmp_path / "project" / "run-20260508-120000"
    run_dir.mkdir(parents=True)
    image_path = run_dir / "hero.png"
    image_path.write_bytes(PNG_HEADER + b"present")

    viewer_path = generate_viewer(
        output_dir=run_dir,
        items=[
            {
                "name": "Hero",
                "prompt": "hero prompt",
                "output_path": str(image_path),
                "aspect_ratio": "4:5",
            }
        ],
        run_meta={"aspect_ratio": "4:5"},
    )
    html = viewer_path.read_text(encoding="utf-8")

    assert 'img.addEventListener(\'error\'' in html
    assert "file missing" in html
    assert "aspect-ratio:${arCss}" in html


def test_node_view_command_rebuilds_project_and_run_viewers(tmp_path: Path) -> None:
    project_dir = tmp_path / "node-viewer"
    run_dir = _write_run(
        project_dir,
        "run-20260508-120000",
        "1:1",
        [{"name": "Hero", "prompt": "hero prompt", "file": "hero.png", "ok": True}],
    )
    (run_dir / "hero.png").write_bytes(PNG_HEADER + b"present")

    proc = subprocess.run(
        ["node", "index.js", "view", str(project_dir), "--all-runs"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    assert "Rafiki" in proc.stdout
    assert f"Viewer:  {project_dir / 'viewer.html'}" in proc.stdout
    assert (project_dir / "viewer.html").exists()
    assert (run_dir / "viewer.html").exists()

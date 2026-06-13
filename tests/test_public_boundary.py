from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def _load_checker():
    spec = importlib.util.spec_from_file_location(
        "check_public_boundary",
        ROOT / "scripts" / "check-public-boundary.py",
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_public_boundary_allows_normal_public_sources() -> None:
    checker = _load_checker()

    violations = checker.public_boundary_violations(
        [
            "README.md",
            "docs/MCP.md",
            "config/pricing.json",
            "examples/quickstart-image-prompts.md",
            "styles/kk.md",
            "data/refs/animation-accelerator-source.jpg",
        ]
    )

    assert violations == []


def test_public_boundary_rejects_tracked_output() -> None:
    checker = _load_checker()

    violations = checker.public_boundary_violations(
        ["output/demo/run-20260612-120000/hero.png"]
    )

    assert violations == [
        ("output/demo/run-20260612-120000/hero.png", "generated review outputs are local state")
    ]


def test_public_boundary_reports_actionable_local_paths() -> None:
    checker = _load_checker()

    violations = checker.public_boundary_violations(
        [
            ".env",
            "data/media-registry.json",
            "config/media-roots.local.json",
            "lib/__pycache__/core.cpython-314.pyc",
        ]
    )

    paths = [path for path, _reason in violations]
    assert paths == [
        ".env",
        "config/media-roots.local.json",
        "data/media-registry.json",
        "lib/__pycache__/core.cpython-314.pyc",
    ]

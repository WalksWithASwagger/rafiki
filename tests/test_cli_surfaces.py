"""Dry-run regressions across Rafiki's agent-facing generation surfaces."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import generate
import mcp_server
from lib import registry, server

REPO_ROOT = Path(__file__).resolve().parent.parent
PNG_HEADER = b"\x89PNG\r\n\x1a\n"


def _prompt_file(tmp_path: Path) -> Path:
    path = tmp_path / "image-prompts.md"
    path.write_text(
        "\n".join(
            [
                "## 1. Hero",
                "**Prompt:**",
                "> A layered community AI workshop poster",
                "",
                "## 2. Detail",
                "**Prompt:**",
                "> A close-up of collaborative field notes and luminous diagrams",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def _write_png(path: Path) -> None:
    path.write_bytes(PNG_HEADER + b"fakepngdata")


def _write_run(directory: Path, images: list[dict]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for image in images:
        _write_png(directory / image["file"])
    (directory / "run.json").write_text(
        json.dumps(
            {
                "model": "gpt-image-2",
                "aspect_ratio": "16:9",
                "style": "bcai",
                "run_id": directory.name.removeprefix("run-"),
                "images": images,
            }
        ),
        encoding="utf-8",
    )


def _batch_options(output_dir: Path) -> list[str]:
    return [
        "--output-dir",
        str(output_dir),
        "--model",
        "gpt",
        "--aspect-ratio",
        "instagram",
        "--quality",
        "medium",
        "--style",
        "none",
        "--reference-images",
        "/tmp/ref-a.png,/tmp/ref-b.png",
        "--global-reference-images",
        "/tmp/global-a.png,/tmp/global-b.png",
        "--reference-role",
        "mockup",
        "--composition-references",
        "/tmp/print-art.png",
        "--dry-run",
        "--no-viewer",
        "--json",
    ]


def _single_options(output_path: Path) -> list[str]:
    return [
        "--prompt",
        "A compact studio poster for a local AI image workflow",
        "--output",
        str(output_path),
        "--model",
        "gpt-image-2",
        "--aspect-ratio",
        "4:5",
        "--quality",
        "medium",
        "--no-style",
        "--reference-image",
        "/tmp/ref-single.png",
        "--global-reference-images",
        "/tmp/global-single-a.png,/tmp/global-single-b.png",
        "--reference-role",
        "mockup",
        "--composition-references",
        "/tmp/print-single.png",
        "--dry-run",
        "--json",
    ]


def _python_batch_args(prompt_file: Path, output_dir: Path) -> list[str]:
    return ["--prompt-file", str(prompt_file), *_batch_options(output_dir)]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )


def _isolate_registry_cache(tmp_path: Path, monkeypatch) -> Path:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(registry, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(registry, "DATA_DIR", data_dir)
    monkeypatch.setattr(registry, "REGISTRY_JSON", data_dir / "asset-registry.json")
    monkeypatch.setattr(registry, "REGISTRY_CSV", data_dir / "asset-registry.csv")
    monkeypatch.setattr(registry, "_load_extra_roots", lambda: {})
    return data_dir


def _assert_batch_json_contract(payload: dict, output_dir: Path) -> None:
    assert payload["success"] is True
    assert payload["mode"] == "batch"
    assert payload["dry_run"] is True
    assert payload["generated"] == 2
    assert payload["total"] == 2
    assert payload["project_dir"] == str(output_dir)
    assert payload["model"] == "gpt-image-2"
    assert payload["aspect_ratio"] == "1:1"
    assert payload["style"] == "none"
    assert payload["global_reference_images"] == ["/tmp/global-a.png", "/tmp/global-b.png"]
    assert len(payload["images"]) == 2
    assert all(image["ok"] is True for image in payload["images"])

    run_dir = Path(payload["run_dir"])
    assert run_dir.exists()
    assert (run_dir / "run.json").exists()
    manifest = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    assert manifest["reference_images"] == [
        "/tmp/ref-a.png",
        "/tmp/ref-b.png",
        "/tmp/global-a.png",
        "/tmp/global-b.png",
        "/tmp/print-art.png",
    ]
    assert manifest["images"][0]["reference_images"] == [
        "/tmp/ref-a.png",
        "/tmp/global-a.png",
        "/tmp/global-b.png",
        "/tmp/print-art.png",
    ]
    assert list(run_dir.glob("*.png")) == []


def _assert_single_json_contract(payload: dict, output_path: Path) -> None:
    assert payload["success"] is True
    assert payload["mode"] == "single"
    assert payload["dry_run"] is True
    assert payload["output_path"] == str(output_path)
    assert payload["model"] == "gpt-image-2"
    assert payload["aspect_ratio"] == "4:5"
    assert payload["style"] == "none"
    assert payload["reference_images"] == [
        "/tmp/ref-single.png",
        "/tmp/global-single-a.png",
        "/tmp/global-single-b.png",
        "/tmp/print-single.png",
    ]
    assert payload["prompt_preview"].startswith("A compact studio poster")
    assert not output_path.exists()


def test_python_cli_single_prompt_dry_run_json_contract(tmp_path: Path) -> None:
    output_path = tmp_path / "single-python.png"

    proc = _run([sys.executable, "generate.py", *_single_options(output_path)])
    payload = json.loads(proc.stdout)

    assert "[DRY RUN]" in proc.stderr
    _assert_single_json_contract(payload, output_path)


def test_node_cli_single_prompt_dry_run_json_stdout_contract(tmp_path: Path) -> None:
    output_path = tmp_path / "single-node.png"

    proc = _run(["node", "index.js", *_single_options(output_path)])
    payload = json.loads(proc.stdout)

    assert "Rafiki" in proc.stderr
    assert "[DRY RUN]" in proc.stderr
    _assert_single_json_contract(payload, output_path)


def test_python_cli_batch_dry_run_json_contract(tmp_path: Path) -> None:
    prompt_file = _prompt_file(tmp_path)
    output_dir = tmp_path / "python-output"

    proc = _run([sys.executable, "generate.py", *_python_batch_args(prompt_file, output_dir)])
    payload = json.loads(proc.stdout)

    assert "[DRY RUN]" in proc.stderr
    _assert_batch_json_contract(payload, output_dir)


def test_python_cli_approve_refreshes_registry_cache(tmp_path: Path, monkeypatch, capsys) -> None:
    data_dir = _isolate_registry_cache(tmp_path, monkeypatch)
    output_root = tmp_path / "output"
    run_dir = output_root / "demo" / "run-20260101-100000"
    _write_run(run_dir, [{"name": "Hero", "prompt": "caption", "file": "hero.png"}])
    (output_root / "ratings.json").write_text(
        json.dumps({"demo/run-20260101-100000/hero.png": "star"}),
        encoding="utf-8",
    )

    generate._cmd_approve(
        [
            "demo",
            "--run",
            "20260101-100000",
            "--output-dir",
            str(output_root),
        ]
    )

    out = capsys.readouterr().out
    payload = json.loads((data_dir / "asset-registry.json").read_text(encoding="utf-8"))
    assert "Approved 1 image" in out
    assert "Registry refreshed:" in out
    assert len(payload) == 1
    assert payload[0]["id"] == "demo-hero"
    assert payload[0]["source"] == "approved"
    assert payload[0]["path"].endswith("/demo/approved/hero.png")


def test_node_cli_batch_dry_run_json_contract(tmp_path: Path) -> None:
    prompt_file = _prompt_file(tmp_path)
    output_dir = tmp_path / "node-output"

    proc = _run(["node", "index.js", str(prompt_file), *_batch_options(output_dir)])
    payload = json.loads(proc.stdout)

    assert "Rafiki" in proc.stderr
    assert "[DRY RUN]" in proc.stderr
    _assert_batch_json_contract(payload, output_dir)


def test_mcp_cli_bridge_preserves_dry_run_json_contract(tmp_path: Path) -> None:
    prompt_file = _prompt_file(tmp_path)
    output_dir = tmp_path / "mcp-output"

    payload = json.loads(
        mcp_server.rafiki_run(
            _python_batch_args(prompt_file, output_dir),
            timeout_seconds=30,
        )
    )

    assert payload["success"] is True
    assert payload["exit_code"] == 0
    assert payload["json"] is not None
    assert payload["stdout"].lstrip().startswith("{")
    _assert_batch_json_contract(payload["json"], output_dir)


def test_portal_helper_batch_dry_run_contract(tmp_path: Path) -> None:
    prompt_file = _prompt_file(tmp_path)
    output_root = tmp_path / "portal-output"

    result = server._run_portal_job(
        {
            "mode": "batch",
            "project": "Surface Regression",
            "prompt_file": str(prompt_file),
            "model": "gpt",
            "aspect_ratio": "instagram",
            "quality": "medium",
            "style": "none",
            "reference_images": ["/tmp/ref-a.png", "/tmp/ref-b.png"],
            "reference_role": "mockup",
            "composition_references": ["/tmp/print-art.png"],
            "dry_run": True,
            "workers": 2,
        },
        output_root=output_root,
    )

    assert result["ok"] is True
    assert result["all_ok"] is True
    assert result["mode"] == "batch"
    assert result["project"] == "surface-regression"
    assert result["generated"] == 2
    assert result["total"] == 2
    assert result["project_dir"] == str(output_root / "surface-regression")
    assert result["viewer_url"] == "/output/surface-regression/viewer.html"
    assert result["run_viewer_url"].endswith(f"/run-{result['run_id']}/viewer.html")
    assert list(Path(result["run_dir"]).glob("*.png")) == []

"""Dispatch-layer tests for generate.py command handlers.

These exercise argument parsing, flag handling, error paths, exit codes, and
the wiring between each `_cmd_*` handler and its underlying lib function. The
lib functions themselves are covered by their own test modules; here we mock
or stage minimal inputs and assert the CLI glue behaves correctly without
touching the network.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import generate
from lib import registry


PNG_HEADER = b"\x89PNG\r\n\x1a\n"


def _write_run(directory: Path, images: list[dict]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for image in images:
        (directory / image["file"]).write_bytes(PNG_HEADER + b"fakepng")
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


# ── pure helpers ───────────────────────────────────────────────────────────

def test_parse_days_accepts_plain_and_suffixed():
    assert generate._parse_days("30d") == 30
    assert generate._parse_days("7") == 7
    assert generate._parse_days(" 14D ") == 14


def test_parse_days_rejects_garbage():
    with pytest.raises(argparse.ArgumentTypeError):
        generate._parse_days("soon")


def test_split_csv_paths_trims_and_filters():
    assert generate._split_csv_paths("a, b ,c", flag="--refs") == ["a", "b", "c"]
    assert generate._split_csv_paths(None, flag="--refs") == []
    assert generate._split_csv_paths("", flag="--refs") == []


def test_split_csv_paths_all_empty_exits(capsys):
    with pytest.raises(SystemExit) as exc:
        generate._split_csv_paths(" , , ", flag="--refs")
    assert exc.value.code == 1
    assert "--refs has no paths" in capsys.readouterr().out


# ── clean ────────────────────────────────────────────────────────────────--

def test_cmd_clean_dry_run_lists_without_deleting(tmp_path, capsys):
    project_dir = tmp_path / "output" / "demo"
    _write_run(project_dir / "run-A", [{"name": "Hero", "prompt": "p", "file": "hero.png"}])
    _write_run(project_dir / "run-B", [{"name": "Alt", "prompt": "p", "file": "alt.png"}])

    generate._cmd_clean([str(project_dir), "--dry-run"])

    out = capsys.readouterr().out
    assert "Would delete 2 run dir(s)" in out
    # Nothing actually removed.
    assert (project_dir / "run-A").exists()
    assert (project_dir / "run-B").exists()


# ── regen ────────────────────────────────────────────────────────────────--

def test_cmd_regen_dry_run_lists_configured_jobs(tmp_path, capsys):
    cfg = tmp_path / "scheduled-regen.json"
    cfg.write_text(
        json.dumps(
            [
                {
                    "name": "newsletter-heroes",
                    "prompt_file": "prompts/x.md",
                    "output_dir": "output/never-run-xyz",
                    "interval_days": 30,
                }
            ]
        ),
        encoding="utf-8",
    )

    generate._cmd_regen(["--dry-run", "--config", str(cfg)])

    out = capsys.readouterr().out
    assert "Scheduled regen jobs (1 configured)" in out
    assert "newsletter-heroes" in out


def test_cmd_regen_missing_config_exits(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        generate._cmd_regen(["--config", str(tmp_path / "nope.json")])
    assert exc.value.code == 1
    assert "No config at" in capsys.readouterr().out


def test_cmd_regen_unknown_name_exits(tmp_path, capsys):
    cfg = tmp_path / "scheduled-regen.json"
    cfg.write_text(
        json.dumps(
            [{"name": "real", "prompt_file": "p.md", "output_dir": "output/real", "interval_days": 30}]
        ),
        encoding="utf-8",
    )
    with pytest.raises(SystemExit) as exc:
        generate._cmd_regen(["--name", "ghost", "--config", str(cfg)])
    assert exc.value.code == 1
    assert "no job named 'ghost'" in capsys.readouterr().out


# ── registry ──────────────────────────────────────────────────────────────-

def _isolate_registry(tmp_path, monkeypatch) -> Path:
    output_root = tmp_path / "output"
    data_dir = tmp_path / "data"
    monkeypatch.setattr(registry, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(registry, "DATA_DIR", data_dir)
    monkeypatch.setattr(registry, "DEFAULT_OUTPUT_ROOT", output_root)
    monkeypatch.setattr(registry, "REGISTRY_JSON", data_dir / "asset-registry.json")
    monkeypatch.setattr(registry, "REGISTRY_CSV", data_dir / "asset-registry.csv")
    monkeypatch.setattr(registry, "_load_extra_roots", lambda: {})
    return output_root


def test_cmd_registry_index_then_search(tmp_path, monkeypatch, capsys):
    output_root = _isolate_registry(tmp_path, monkeypatch)
    _write_run(
        output_root / "demo" / "approved",
        [{"name": "Hero", "prompt": "a luminous hero", "file": "hero.png"}],
    )

    generate._cmd_registry(["index"])
    index_out = capsys.readouterr().out
    assert "Indexed 1 assets across 1 project(s)" in index_out

    generate._cmd_registry(["search", "hero", "--json"])
    results = json.loads(capsys.readouterr().out)
    assert len(results) == 1
    assert results[0]["project"] == "demo"


# ── deploy ────────────────────────────────────────────────────────────────-

def test_cmd_deploy_wires_args_and_prints_url(tmp_path, monkeypatch, capsys):
    from lib.deploy import vercel

    viewer_dir = tmp_path / "viewer"
    viewer_dir.mkdir()
    calls = {}

    def fake_deploy(project, *, viewer_dir=None, prod=False, dry_run=False):
        calls.update(project=project, viewer_dir=viewer_dir, prod=prod, dry_run=dry_run)
        return "https://example.vercel.app"

    monkeypatch.setattr(vercel, "deploy", fake_deploy)

    generate._cmd_deploy(["demo", "--viewer-dir", str(viewer_dir), "--prod"])

    assert calls == {
        "project": "demo",
        "viewer_dir": viewer_dir,
        "prod": True,
        "dry_run": False,
    }
    assert "Deployed: https://example.vercel.app" in capsys.readouterr().out


def test_cmd_deploy_reports_error_and_exits(monkeypatch, capsys):
    from lib.deploy import vercel

    def boom(*args, **kwargs):
        raise vercel.ViewerNotFoundError("no viewer.html")

    monkeypatch.setattr(vercel, "deploy", boom)

    with pytest.raises(SystemExit) as exc:
        generate._cmd_deploy(["demo"])
    assert exc.value.code == 1
    assert "Error: no viewer.html" in capsys.readouterr().err


# ── social-expand ──────────────────────────────────────────────────────────

def test_cmd_social_expand_passes_flags_through(monkeypatch):
    from lib import social

    calls = {}
    monkeypatch.setattr(
        social,
        "expand",
        lambda project, **kw: calls.update(project=project, **kw) or {},
    )

    generate._cmd_social_expand(
        ["demo", "--platform", "x", "linkedin", "--dry-run", "--model", "gpt-4o"]
    )

    assert calls["project"] == "demo"
    assert calls["platforms"] == ["x", "linkedin"]
    assert calls["model"] == "gpt-4o"
    assert calls["dry_run"] is True


# ── canva-export ───────────────────────────────────────────────────────────

def test_cmd_canva_export_passes_flags_through(tmp_path, monkeypatch, capsys):
    from lib.exporters import canva

    out_dir = tmp_path / "bundle"
    calls = {}

    def fake_export(project, output_dir=None, zip=True, output_root=None):
        calls.update(project=project, output_dir=output_dir, zip=zip)
        return out_dir / "canva-export"

    monkeypatch.setattr(canva, "export", fake_export)

    generate._cmd_canva_export(["demo", "--no-zip", "-o", str(out_dir)])

    assert calls["project"] == "demo"
    assert calls["output_dir"] == out_dir
    assert calls["zip"] is False
    assert "Canva export:" in capsys.readouterr().out


# ── notion-export ──────────────────────────────────────────────────────────

def test_cmd_notion_export_success_exits_zero(monkeypatch, capsys):
    from lib.exporters import notion

    monkeypatch.setattr(
        notion,
        "export",
        lambda *a, **k: {"exported": 2, "skipped": 1, "errors": [], "source": "approved"},
    )

    with pytest.raises(SystemExit) as exc:
        generate._cmd_notion_export(["demo", "--dry-run"])
    assert exc.value.code == 0
    assert "Notion export: 2 exported" in capsys.readouterr().out


def test_cmd_notion_export_error_exits_one(monkeypatch, capsys):
    from lib.exporters import notion

    def boom(*a, **k):
        raise notion.NotionExportError("missing NOTION_API_KEY")

    monkeypatch.setattr(notion, "export", boom)

    with pytest.raises(SystemExit) as exc:
        generate._cmd_notion_export(["demo"])
    assert exc.value.code == 1
    assert "Error: missing NOTION_API_KEY" in capsys.readouterr().err


# ── serve ────────────────────────────────────────────────────────────────--

def test_cmd_serve_wires_args_without_blocking(tmp_path, monkeypatch):
    import lib.server as server_module

    output_root = tmp_path / "output"
    output_root.mkdir()
    calls = {}
    monkeypatch.setattr(
        server_module,
        "serve",
        lambda **kw: calls.update(kw),
    )

    generate._cmd_serve(
        ["--port", "9100", "--output-dir", str(output_root), "--public"]
    )

    assert calls["port"] == 9100
    assert calls["public"] is True
    assert calls["open_browser"] is False
    assert Path(calls["output_root"]) == output_root


def test_cmd_serve_missing_output_dir_exits(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        generate._cmd_serve(["--output-dir", str(tmp_path / "missing")])
    assert exc.value.code == 1
    assert "output dir not found" in capsys.readouterr().out


# ── view / library error paths ─────────────────────────────────────────────

def test_cmd_view_missing_project_exits(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exc:
        generate._cmd_view(["definitely-not-a-project"])
    assert exc.value.code == 1
    assert "project not found" in capsys.readouterr().out


def test_cmd_library_missing_output_exits(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        generate._cmd_library(["--output-dir", str(tmp_path / "missing")])
    assert exc.value.code == 1
    assert "output dir not found" in capsys.readouterr().out


# ── link-projects ──────────────────────────────────────────────────────────

def test_cmd_link_projects_no_mappings(tmp_path, monkeypatch, capsys):
    from lib import extra_outputs

    monkeypatch.setattr(extra_outputs, "load_extra_outputs", lambda: {})
    monkeypatch.setattr(
        extra_outputs,
        "extra_outputs_config_paths",
        lambda: [Path("config/extra-outputs.json")],
    )

    generate._cmd_link_projects(["--output-dir", str(tmp_path / "output")])

    assert "nothing to link" in capsys.readouterr().out


def test_cmd_link_projects_creates_symlink(tmp_path, monkeypatch, capsys):
    from lib import extra_outputs

    real = tmp_path / "external" / "proj"
    real.mkdir(parents=True)
    output_root = tmp_path / "output"

    monkeypatch.setattr(extra_outputs, "load_extra_outputs", lambda: {"proj": real})

    generate._cmd_link_projects(["--output-dir", str(output_root)])

    link = output_root / "proj"
    assert link.is_symlink()
    assert link.resolve() == real.resolve()
    assert "link proj" in capsys.readouterr().out

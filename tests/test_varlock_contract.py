from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures" / "varlock"
VARLOCK = shutil.which("varlock")
REUSABLE_KEYS = (
    "GOOGLE_API_KEY",
    "OPENAI_API_KEY",
    "FLOYO_KEY",
    "REPLICATE_API_TOKEN",
    "NOTION_API_KEY",
)
APP_LOCAL_KEYS = (
    "GEMINI_API_KEY",
    "PUPPETEER_EXECUTABLE_PATH",
    "CHROME_PATH",
    "GOOGLE_CHROME_BIN",
    "RAFIKI_DOCTOR_PYTHON",
    "RAFIKI_E2E_ARTIFACT_DIR",
    "PORTAL_USERNAME",
    "PORTAL_PASSWORD",
    "NOTION_DATABASE_ID",
    "RAFIKI_VARLOCK_SMOKE",
)
SANITIZED_VALUES = (
    "fixture-shared-contract-value",
    "fixture-rafiki-override-value",
)


def test_schema_selectively_imports_reusable_values() -> None:
    schema = (ROOT / ".env.schema").read_text(encoding="utf-8")
    picked = ", ".join(REUSABLE_KEYS)
    imports = [line for line in schema.splitlines() if line.startswith("# @import(")]

    assert imports == [
        f"# @import(~/.agents/env/values/.env.shared.local, pick=[{picked}], allowMissing=true)",
        f"# @import(~/.agents/env/values/.env.rafiki.local, pick=[{picked}], allowMissing=true)",
    ]
    for key in (*REUSABLE_KEYS, *APP_LOCAL_KEYS):
        assert f"{key}=" in schema
    for key in APP_LOCAL_KEYS:
        assert all(key not in import_line for import_line in imports)


def test_audit_and_scan_scripts_exclude_non_source_artifacts() -> None:
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    audit = package["scripts"]["env:audit"]

    for path in (
        "node_modules",
        "frontend/node_modules",
        ".venv",
        "output",
        "outputs",
        "assets",
        "prompts",
        "examples/images",
        ".rafiki-cache",
        "frontend/.output",
        "frontend/.vinxi",
        "frontend/.wrangler",
        "frontend/src/routeTree.gen.ts",
    ):
        assert f"--ignore {path}" in audit
    assert package["scripts"]["env:scan"] == "varlock scan --staged"


def test_agent_guidance_requires_safe_varlock_commands() -> None:
    instructions = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "secret-dependent child commands" in instructions
    assert "varlock run --inject vars" in instructions
    assert "npm run env:audit" in instructions
    assert "staged-only `npm run env:scan`" in instructions
    assert "Node 22.3+ or the standalone CLI" in instructions


@pytest.mark.skipif(VARLOCK is None, reason="standalone Varlock CLI is not installed")
def test_sanitized_imports_load_run_and_scan_without_exposing_values() -> None:
    version = subprocess.run(
        [str(VARLOCK), "--version"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert tuple(int(part) for part in version.split(".")[:3]) >= (1, 10, 0)

    scan_target = FIXTURES / "scan-target.txt"
    for fixture_name in ("present", "missing"):
        fixture = FIXTURES / fixture_name
        _run_varlock("load", "--agent", "--show-all", "--path", fixture)
        _run_varlock(
            "run",
            "--inject",
            "vars",
            "--path",
            fixture,
            "--",
            sys.executable,
            "-c",
            "pass",
        )
        _run_varlock("scan", scan_target, cwd=fixture)

    _run_varlock(
        "run",
        "--inject",
        "vars",
        "--path",
        FIXTURES / "present",
        "--",
        sys.executable,
        "-c",
        (
            "import os,sys;"
            "sys.exit(os.environ.get('RAFIKI_SHARED_FIXTURE') != "
            "'fixture-rafiki-override-value')"
        ),
    )
    _run_varlock(
        "run",
        "--inject",
        "vars",
        "--path",
        FIXTURES / "missing",
        "--",
        sys.executable,
        "-c",
        "import os,sys;sys.exit(os.environ.get('RAFIKI_SHARED_FIXTURE') is not None)",
    )


def _run_varlock(*arguments: str | Path, cwd: Path = ROOT) -> None:
    result = subprocess.run(
        [str(VARLOCK), *(str(argument) for argument in arguments)],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout + result.stderr

    assert result.returncode == 0, output
    assert not any(value in output for value in SANITIZED_VALUES)

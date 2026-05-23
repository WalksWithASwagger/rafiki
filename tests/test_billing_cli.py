from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_billing_cli_import_and_summary_json(tmp_path: Path):
    source = tmp_path / "billing.csv"
    state = tmp_path / "billing-imports.json"
    source.write_text(
        "provider,model,amount,currency\n"
        "OpenAI,gpt-image-2,9.99,USD\n",
        encoding="utf-8",
    )

    imported = subprocess.run(
        [
            sys.executable,
            "generate.py",
            "billing",
            "import",
            str(source),
            "--state",
            str(state),
            "--json",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    summary = subprocess.run(
        [
            sys.executable,
            "generate.py",
            "billing",
            "summary",
            "--state",
            str(state),
            "--json",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    assert json.loads(imported.stdout)["imported"] == 1
    payload = json.loads(summary.stdout)
    assert payload["entries"] == 1
    assert payload["amount"] == 9.99

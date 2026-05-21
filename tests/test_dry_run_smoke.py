from __future__ import annotations

import json
import subprocess
import sys


def test_dry_run_smoke_script_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/dry-run-smoke.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["ok"] is True
    assert payload["node_cli"]["generated"] == 2
    assert payload["mcp"]["bridge_generated"] == 2
    assert payload["archive_health"]["expected_missing_images"] == 4

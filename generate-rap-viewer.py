#!/usr/bin/env python3
"""Generate the combined RAP certification viewer.

Thin wrapper around `generate-presentation-viewer.py` driven by
`prompts/bcai/rap-viewer-data.json`. Kept as a stable entry point so existing
docs and muscle memory (`python generate-rap-viewer.py`) keep working.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_FILE = SCRIPT_DIR / "prompts" / "bcai" / "rap-viewer-data.json"
OUTPUT_DIR = SCRIPT_DIR / "output" / "rap-all-weeks"
GENERIC = SCRIPT_DIR / "generate-presentation-viewer.py"


def main() -> None:
    subprocess.run(
        [
            sys.executable,
            str(GENERIC),
            "--data",
            str(DATA_FILE),
            "--output",
            str(OUTPUT_DIR),
        ],
        check=True,
    )


if __name__ == "__main__":
    main()

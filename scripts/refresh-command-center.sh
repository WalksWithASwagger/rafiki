#!/usr/bin/env bash
# Refresh the cross-project command center:
#   1. symlink registered external projects into output/  (file:// resolution)
#   2. rebuild the cross-project asset registry
#   3. regenerate the master library viewer
# Project mappings live in config/extra-outputs.local.json (local, gitignored).
# See docs/COMMAND-CENTER.md.
set -euo pipefail
cd "$(dirname "$0")/.."

PY="${RAFIKI_PYTHON:-.venv/bin/python}"
[ -x "$PY" ] || PY="python3"

# Non-standard "loose image" dirs (no run-*/) get a local run-wrapper so the
# indexer can see them: output/<name>/run-imported -> <loose dir>. Sources are
# listed in the local, gitignored config/loose-imports.local.json. Idempotent.
LOOSE="config/loose-imports.local.json"
if [ -f "$LOOSE" ]; then
  echo "→ loose-import wrappers"
  "$PY" - "$LOOSE" <<'PYEOF'
import json, os, sys
cfg = json.load(open(sys.argv[1]))
for name, path in cfg.items():
    if not os.path.isdir(path):
        print(f"  skip {name}: source missing ({path})"); continue
    wrap = os.path.join("output", name)
    os.makedirs(wrap, exist_ok=True)
    link = os.path.join(wrap, "run-imported")
    if os.path.islink(link):
        if os.path.realpath(link) == os.path.realpath(path):
            print(f"  ok   {name} (already wrapped)"); continue
        os.unlink(link)
    elif os.path.exists(link):
        print(f"  skip {name}: {link} exists and is not a symlink"); continue
    os.symlink(path, link)
    print(f"  wrap {name} → {path}")
PYEOF
fi

echo "→ link-projects"   && "$PY" generate.py link-projects
echo "→ registry index"  && "$PY" generate.py registry index
echo "→ library"         && "$PY" generate.py library

echo
echo "Static library : output/library.html"
echo "Live portal    : $PY generate.py serve   # then open http://localhost:8000"

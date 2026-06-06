#!/usr/bin/env bash
#
# Rafiki GUI screenshot driver.
#
# The no-spend CLI/MCP and portal-DOM smokes already live in the repo
# (`npm run smoke:dry-run`, `npm run e2e:portal`). This driver covers the one
# thing they don't: actually launching the portal + a run viewer and capturing
# PNG screenshots you can open and look at. No API keys, no image generation.
#
# Usage (run from repo root):
#   bash .claude/skills/run-rafiki/driver.sh
#
# Output: PNGs written to a temp dir, paths printed at the end.
# Override Chrome with:  CHROME=/path/to/chrome bash .../driver.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$REPO_ROOT"

PY="$REPO_ROOT/.venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3)"

# --- locate a Chrome/Chromium binary ---------------------------------------
find_chrome() {
  if [ -n "${CHROME:-}" ]; then echo "$CHROME"; return; fi
  local mac="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  [ -x "$mac" ] && { echo "$mac"; return; }
  for c in google-chrome chromium chromium-browser google-chrome-stable; do
    command -v "$c" >/dev/null 2>&1 && { command -v "$c"; return; }
  done
  # fall back to puppeteer's bundled chromium
  "$PY" - <<'PY' 2>/dev/null || true
import glob, os
hits = glob.glob(os.path.expanduser("~/.cache/puppeteer/**/chrome*"), recursive=True)
hits += glob.glob(os.path.join(os.getcwd(), "node_modules/puppeteer/.local-chromium/**/chrome*"), recursive=True)
print(next((h for h in hits if os.access(h, os.X_OK) and not os.path.isdir(h)), ""))
PY
}
CHROME_BIN="$(find_chrome)"
[ -n "$CHROME_BIN" ] && [ -x "$CHROME_BIN" ] || { echo "FATAL: no Chrome/Chromium found; set CHROME=..." >&2; exit 1; }
echo "Chrome: $CHROME_BIN"

# --- pick a free port -------------------------------------------------------
PORT="$("$PY" - <<'PY'
import socket
s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()
PY
)"
echo "Port:   $PORT"

OUT="$(mktemp -d -t rafiki-driver-XXXXXX)"
echo "Shots:  $OUT"

shot() { # url, file
  "$CHROME_BIN" --headless --disable-gpu --hide-scrollbars \
    --window-size=1440,1200 --virtual-time-budget=5000 \
    --screenshot="$2" "$1" >/dev/null 2>&1
}

# --- 1. make sure the library index + a viewer exist ------------------------
"$PY" generate.py library >/dev/null
PROJECT="$(find output -mindepth 2 -maxdepth 2 -type d -name 'run-*' 2>/dev/null \
  | head -1 | sed -E 's#^output/([^/]+)/.*#\1#')"
echo "Project: ${PROJECT:-<none>}"

# --- 2. launch the portal, wait for HTTP 200 --------------------------------
"$PY" generate.py serve --port "$PORT" --output-dir output >"$OUT/portal.log" 2>&1 &
SERVER_PID=$!
trap '[ -n "${SERVER_PID:-}" ] && kill "$SERVER_PID" 2>/dev/null || true' EXIT

for i in $(seq 1 30); do
  code="$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/" || true)"
  [ "$code" = "200" ] && break
  kill -0 "$SERVER_PID" 2>/dev/null || { echo "portal exited early:"; cat "$OUT/portal.log"; exit 1; }
  sleep 0.5
done
[ "$code" = "200" ] || { echo "portal never served 200"; cat "$OUT/portal.log"; exit 1; }
echo "Portal: http://127.0.0.1:$PORT/ -> 200"

# --- 3. screenshots ---------------------------------------------------------
shot "http://127.0.0.1:$PORT/" "$OUT/portal.png"
echo "  wrote $OUT/portal.png"

if [ -n "$PROJECT" ]; then
  "$PY" generate.py view "$PROJECT" >/dev/null
  VIEWER="$REPO_ROOT/output/$PROJECT/viewer.html"
  if [ -f "$VIEWER" ]; then
    shot "file://$VIEWER" "$OUT/viewer.png"
    echo "  wrote $OUT/viewer.png  (project: $PROJECT)"
  fi
fi

echo "OK. Screenshots in: $OUT"

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

# --- 4. Studio dry-run (the same call the portal "Dry Run" button makes) -----
# POST /api/regen with dry_run:true — no provider call, no spend. Writes a run
# dir under output/<SMOKE_PROJECT> (dry-run always does), which we then remove.
SMOKE_PROJECT="_driver-studio-smoke"
echo "Studio dry-run -> POST /api/regen (project: $SMOKE_PROJECT)"
curl -s -X POST "http://127.0.0.1:$PORT/api/regen" \
  -H 'Content-Type: application/json' \
  -d "{\"mode\":\"single\",\"dry_run\":true,\"prompt\":\"A radio host in a neon-lit studio\",\"project\":\"$SMOKE_PROJECT\",\"model\":\"gemini-2.5-flash-image\",\"style\":\"kk\",\"aspect_ratio\":\"16:9\"}" \
  >"$OUT/studio.json" 2>/dev/null
"$PY" - "$OUT/studio.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d.get("ok") and d.get("dry_run", True) is not False, d
assert d.get("generated") == d.get("total") and d.get("total", 0) >= 1, d
print(f"  ok: generated {d['generated']}/{d['total']}, run {d.get('run_id')}")
PY
rm -rf "$REPO_ROOT/output/$SMOKE_PROJECT"

# --- 5. HTML -> PNG render (the Puppeteer renderer surface) ------------------
# `--render` writes <name>.png next to the .html. No keys, no spend.
echo "Render -> node index.js --render (HTML to PNG)"
cat > "$OUT/card.html" <<'HTML'
<!doctype html><html><body style="margin:0;width:600px;height:400px;background:#0b132b;color:#5eead4;font-family:sans-serif;display:flex;align-items:center;justify-content:center;font-size:40px">Rafiki render ✓</body></html>
HTML
node index.js --render "$OUT/card.html" >/dev/null 2>&1
if [ -s "$OUT/card.png" ]; then
  echo "  wrote $OUT/card.png ($(wc -c <"$OUT/card.png" | tr -d ' ') bytes)"
else
  echo "  FATAL: render produced no card.png" >&2; exit 1
fi

# --- 6. Video Lab EDL export (the "Export EDL" button) ----------------------
# GET /api/media/selections/edl — read-only, no spend. clip_count is 0 on a
# fresh checkout (no selections yet), but the EDL structure is still valid.
echo "Video EDL export -> GET /api/media/selections/edl"
curl -s "http://127.0.0.1:$PORT/api/media/selections/edl?include=focus,star" \
  >"$OUT/video-edl.json" 2>/dev/null
"$PY" - "$OUT/video-edl.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d.get("kind") == "rafiki-video-edl", d
assert isinstance(d.get("clips"), list) and d.get("clip_count") == len(d["clips"]), d
assert isinstance(d.get("edit_manifest"), dict), d
print(f"  ok: {d['clip_count']} clip(s), project {d.get('project')}")
PY

# --- 7. Canva export dry-run (the "canva-export" portal action) -------------
# POST /api/actions with dry_run:true — counts source images and reports the
# would-be zip path without writing anything. Needs a project with images.
if [ -n "$PROJECT" ]; then
  echo "Canva export dry-run -> POST /api/actions (project: $PROJECT)"
  curl -s -X POST "http://127.0.0.1:$PORT/api/actions" \
    -H 'Content-Type: application/json' \
    -d "{\"action\":\"canva-export\",\"dry_run\":true,\"project\":\"$PROJECT\"}" \
    >"$OUT/canva-export.json" 2>/dev/null
  "$PY" - "$OUT/canva-export.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d.get("ok") and d.get("dry_run") is True and d.get("mutating") is False, d
assert isinstance(d.get("image_count"), int) and str(d.get("result_path", "")).endswith(".zip"), d
print(f"  ok: {d['image_count']} image(s) from {d.get('source')} -> {d['result_path'].split('/')[-1]}")
PY

  # --- 8. Notion export dry-run (the "notion-export" portal action) ----------
  # POST /api/actions with dry_run:true — counts what would be exported with no
  # Notion token and no external call (external:true action, so dry-run drops
  # the confirm guard and the network request).
  echo "Notion export dry-run -> POST /api/actions (project: $PROJECT)"
  curl -s -X POST "http://127.0.0.1:$PORT/api/actions" \
    -H 'Content-Type: application/json' \
    -d "{\"action\":\"notion-export\",\"dry_run\":true,\"project\":\"$PROJECT\"}" \
    >"$OUT/notion-export.json" 2>/dev/null
  "$PY" - "$OUT/notion-export.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d.get("ok") and d.get("dry_run") is True and d.get("external") is False, d
assert isinstance(d.get("exported"), int) and d.get("errors") == [], d
print(f"  ok: would export {d['exported']} from {d.get('source')}, {d.get('skipped')} skipped")
PY

  # --- 10. Static deploy dry-run (the "static-deploy" portal action) ---------
  # POST /api/actions with dry_run:true — resolves the viewer dir and returns
  # the `vercel deploy` command it WOULD run, with no network call (external).
  # Needs viewer.html, which the `generate.py view` step above produced.
  echo "Static deploy dry-run -> POST /api/actions (project: $PROJECT)"
  curl -s -X POST "http://127.0.0.1:$PORT/api/actions" \
    -H 'Content-Type: application/json' \
    -d "{\"action\":\"static-deploy\",\"dry_run\":true,\"project\":\"$PROJECT\"}" \
    >"$OUT/static-deploy.json" 2>/dev/null
  "$PY" - "$OUT/static-deploy.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d.get("ok") and d.get("dry_run") is True and d.get("external") is False, d
assert d.get("command", [None])[0] == "vercel" and d.get("url") == "", d
assert isinstance(d.get("source_mapping"), dict), d
print(f"  ok: would run `{' '.join(d['command'])}` ({d['source_mapping'].get('key_count')} mapped key(s))")
PY

  # --- 11. Approve-starred dry-run (the "approve-starred" portal action) -----
  # POST /api/actions with dry_run:true — resolves the latest run and counts
  # starred images that WOULD be approved, without copying anything into
  # approved/.
  echo "Approve-starred dry-run -> POST /api/actions (project: $PROJECT)"
  curl -s -X POST "http://127.0.0.1:$PORT/api/actions" \
    -H 'Content-Type: application/json' \
    -d "{\"action\":\"approve-starred\",\"dry_run\":true,\"project\":\"$PROJECT\"}" \
    >"$OUT/approve-starred.json" 2>/dev/null
  "$PY" - "$OUT/approve-starred.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d.get("ok") and d.get("dry_run") is True and d.get("mutating") is False, d
assert isinstance(d.get("approved_count"), int) and d.get("run"), d
print(f"  ok: would approve {d['approved_count']} starred from {d['run']}")
PY
fi

# --- 9. Registry export dry-run (the "registry-export" portal action) --------
# POST /api/actions with dry_run:true — reports the asset-registry row count and
# the would-be CSV path without rewriting the file. Registry-wide, no project.
echo "Registry export dry-run -> POST /api/actions (format: csv)"
curl -s -X POST "http://127.0.0.1:$PORT/api/actions" \
  -H 'Content-Type: application/json' \
  -d '{"action":"registry-export","dry_run":true,"format":"csv"}' \
  >"$OUT/registry-export.json" 2>/dev/null
"$PY" - "$OUT/registry-export.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d.get("ok") and d.get("dry_run") is True and d.get("mutating") is False, d
assert isinstance(d.get("count"), int) and str(d.get("path", "")).endswith(".csv"), d
print(f"  ok: {d['count']} registry row(s) -> {d['path'].split('/')[-1]}")
PY

echo "OK. Artifacts in: $OUT"

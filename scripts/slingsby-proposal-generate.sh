#!/usr/bin/env bash
# Generate Slingsby Advisors proposal plates. Private photos stay in
# assets/slingsby/ (gitignored). Defaults to dry-run.
#
#   bash scripts/slingsby-proposal-generate.sh
#   bash scripts/slingsby-proposal-generate.sh --execute
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

EXECUTE=0
if [[ "${1:-}" == "--execute" ]]; then
  EXECUTE=1
fi

LIKENESS_DIR="${SLINGSBY_LIKENESS_DIR:-$ROOT/assets/slingsby/likeness}"
STYLE_DIR="${SLINGSBY_STYLE_DIR:-$ROOT/assets/slingsby/style-refs}"
OUT_DIR="${SLINGSBY_OUTPUT_DIR:-$ROOT/output/slingsby-advisors}"
PY="${RAFIKI_DOCTOR_PYTHON:-python3}"

if [[ "$EXECUTE" -eq 1 && -z "${GOOGLE_API_KEY:-}${GEMINI_API_KEY:-}" ]]; then
  echo "Error: --execute needs GOOGLE_API_KEY (or GEMINI_API_KEY)." >&2
  exit 2
fi

style_refs=()
if [[ -d "$STYLE_DIR" ]]; then
  while IFS= read -r -d '' file; do
    style_refs+=("$file")
  done < <(find "$STYLE_DIR" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' \) -print0 | sort -z)
fi

likeness_refs=()
if [[ -d "$LIKENESS_DIR" ]]; then
  while IFS= read -r -d '' file; do
    likeness_refs+=("$file")
  done < <(find "$LIKENESS_DIR" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' \) -print0 | sort -z)
fi

join_csv() {
  local IFS=,
  printf '%s' "$*"
}

dry_flag=(--dry-run --no-viewer)
if [[ "$EXECUTE" -eq 1 ]]; then
  dry_flag=(--no-viewer)
fi

style_cmd=(
  "$PY" generate.py
  --prompt-file examples/slingsby-advisors-style-plates.md
  --style slingsby
  --reference-role style
  --output-dir "$OUT_DIR"
  "${dry_flag[@]}"
)
if [[ ${#style_refs[@]} -gt 0 ]]; then
  style_cmd+=(--global-reference-images "$(join_csv "${style_refs[@]}")")
fi

echo "Style plates: ${style_cmd[*]}"
"${style_cmd[@]}"

if [[ ${#likeness_refs[@]} -eq 0 ]]; then
  echo "Likeness jobs skipped: no photos in $LIKENESS_DIR"
  echo "Drop authorized portraits there, then re-run."
  exit 0
fi

likeness_cmd=(
  "$PY" generate.py
  --prompt-file examples/slingsby-advisors-likeness-jobs.md
  --style slingsby
  --reference-role likeness
  --global-reference-images "$(join_csv "${likeness_refs[@]}")"
  --output-dir "$OUT_DIR"
  "${dry_flag[@]}"
)

echo "Likeness jobs: ${likeness_cmd[*]}"
"${likeness_cmd[@]}"

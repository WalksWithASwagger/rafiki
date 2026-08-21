#!/usr/bin/env bash
# Generate Slingsby Advisors proposal plates. Private photos stay in
# assets/slingsby/ (gitignored). Defaults to dry-run.
#
#   bash scripts/slingsby-proposal-generate.sh
#   bash scripts/slingsby-proposal-generate.sh --status
#   bash scripts/slingsby-proposal-generate.sh --execute
#   bash scripts/slingsby-proposal-generate.sh --execute --style-only
#   bash scripts/slingsby-proposal-generate.sh --train-lora-plan
#   bash scripts/slingsby-proposal-generate.sh --review
#   python3 scripts/slingsby-proposal-prep-refs.py
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Load local dotenv the same way generate.py does: setdefault, never print values.
_load_dotenv() {
  local file="$1"
  [[ -f "$file" ]] || return 0
  local line key val
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%$'\r'}"
    line="${line#"${line%%[![:space:]]*}"}"
    [[ -z "$line" || "$line" == \#* ]] && continue
    [[ "$line" == *=* ]] || continue
    key="${line%%=*}"
    val="${line#*=}"
    key="${key%"${key##*[![:space:]]}"}"
    [[ -n "$key" ]] || continue
    if [[ -z "${!key:-}" ]]; then
      export "${key}=${val}"
    fi
  done < "$file"
}

_load_dotenv "${SLINGSBY_ENV_FILE:-$ROOT/.env}"
_load_dotenv "$ROOT/.env.local"

EXECUTE=0
STATUS=0
TRAIN_LORA_PLAN=0
STYLE_ONLY=0
LIKENESS_ONLY=0
REVIEW=0

for arg in "$@"; do
  case "$arg" in
    --execute) EXECUTE=1 ;;
    --status|status) STATUS=1 ;;
    --train-lora-plan) TRAIN_LORA_PLAN=1 ;;
    --style-only) STYLE_ONLY=1 ;;
    --likeness-only) LIKENESS_ONLY=1 ;;
    --review) REVIEW=1 ;;
    -h|--help)
      sed -n '2,12p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      exit 1
      ;;
  esac
done

if [[ "$STYLE_ONLY" -eq 1 && "$LIKENESS_ONLY" -eq 1 ]]; then
  echo "Error: --style-only and --likeness-only cannot be combined." >&2
  exit 1
fi

ASSETS_ROOT="${SLINGSBY_ASSETS_ROOT:-$ROOT/assets/slingsby}"
if [[ -n "${SLINGSBY_LIKENESS_DIR:-}" ]]; then
  LIKENESS_DIR="$SLINGSBY_LIKENESS_DIR"
elif [[ -d "$ASSETS_ROOT/likeness-clean" ]]; then
  LIKENESS_DIR="$ASSETS_ROOT/likeness-clean"
else
  LIKENESS_DIR="$ASSETS_ROOT/likeness"
fi
if [[ -n "${SLINGSBY_STYLE_DIR:-}" ]]; then
  STYLE_DIR="$SLINGSBY_STYLE_DIR"
elif [[ -d "$ASSETS_ROOT/style-refs/moodboard/face-free" ]]; then
  STYLE_DIR="$ASSETS_ROOT/style-refs/moodboard/face-free"
elif [[ -d "$ASSETS_ROOT/style-refs/moodboard/selected" ]]; then
  STYLE_DIR="$ASSETS_ROOT/style-refs/moodboard/selected"
elif [[ -d "$ASSETS_ROOT/style-refs/moodboard" ]]; then
  STYLE_DIR="$ASSETS_ROOT/style-refs/moodboard"
else
  STYLE_DIR="$ASSETS_ROOT/style-refs"
fi
OUT_DIR="${SLINGSBY_OUTPUT_DIR:-$ROOT/output/slingsby-advisors}"
CONSENT_FILE="${SLINGSBY_CONSENT_FILE:-$ASSETS_ROOT/CONSENT.md}"
PY="${RAFIKI_DOCTOR_PYTHON:-python3}"
MAX_STYLE_REFS="${SLINGSBY_MAX_STYLE_REFS:-16}"
STYLE_PACK="${SLINGSBY_STYLE_PACK:-$ROOT/examples/slingsby-advisors-style-plates.md}"
if [[ -n "${SLINGSBY_LIKENESS_PACK:-}" ]]; then
  LIKENESS_PACK="$SLINGSBY_LIKENESS_PACK"
elif [[ -f "$ROOT/prompts/slingsby-advisors-proposal.md" ]]; then
  LIKENESS_PACK="$ROOT/prompts/slingsby-advisors-proposal.md"
else
  LIKENESS_PACK="$ROOT/examples/slingsby-advisors-likeness-jobs.md"
fi

has_gemini_key() {
  [[ -n "${GOOGLE_API_KEY:-}${GEMINI_API_KEY:-}" ]]
}

has_replicate_key() {
  [[ -n "${REPLICATE_API_TOKEN:-}" ]]
}

consent_ok() {
  local flag
  flag="$(printf '%s' "${SLINGSBY_LIKENESS_CONSENT:-}" | tr '[:upper:]' '[:lower:]')"
  case "$flag" in
    1|yes|true|ok) return 0 ;;
  esac
  # An explicit path wins so tests (and operators) can fail closed.
  if [[ -n "${SLINGSBY_CONSENT_FILE:-}" ]]; then
    [[ -f "$SLINGSBY_CONSENT_FILE" ]] && return 0
    return 1
  fi
  [[ -f "$CONSENT_FILE" ]] && return 0
  [[ -f "$ASSETS_ROOT/CONSENT.md" ]] && return 0
  [[ -f "$ASSETS_ROOT/CONSENT" ]] && return 0
  return 1
}

list_images() {
  local dir="$1"
  [[ -d "$dir" ]] || return 0
  find "$dir" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' \) | sort
}

# Prefer larger files so a dumped mood board of thumbs does not crowd Gemini.
cap_images() {
  local max="$1"
  shift
  if [[ "$#" -eq 0 ]]; then
    return 0
  fi
  if [[ "$#" -le "$max" ]]; then
    printf '%s\n' "$@"
    return 0
  fi
  "$PY" -c '
import os, sys

limit = int(sys.argv[1])
paths = sys.argv[2:]
SERIES = ("meridians", "mutual", "shoru", "arcana", "artinsitu", "hautepeinture")

def sort_key(path: str):
    norm = path.replace("\\\\", "/").lower()
    name = os.path.basename(norm)
    if "/pages/" in norm:
        return (0, name, 0)
    for index, key in enumerate(SERIES):
        if key in name:
            return (1, index, -os.path.getsize(path))
    return (2, 99, -os.path.getsize(path))

paths.sort(key=sort_key)
print("\n".join(paths[:limit]))
' "$max" "$@"
}

join_csv() {
  local IFS=,
  printf '%s' "$*"
}

style_refs=()
while IFS= read -r file; do
  [[ -n "$file" ]] && style_refs+=("$file")
done < <(list_images "$STYLE_DIR")
if [[ ${#style_refs[@]} -gt 0 ]]; then
  mapfile -t style_refs < <(cap_images "$MAX_STYLE_REFS" "${style_refs[@]}")
fi

likeness_refs=()
while IFS= read -r file; do
  [[ -n "$file" ]] && likeness_refs+=("$file")
done < <(list_images "$LIKENESS_DIR")

if [[ "$STATUS" -eq 1 ]]; then
  echo "Slingsby Advisors generation gates"
  echo "  style pack:     $STYLE_PACK"
  echo "  likeness pack:  $LIKENESS_PACK"
  echo "  style refs:     ${#style_refs[@]} file(s) in $STYLE_DIR (cap $MAX_STYLE_REFS)"
  echo "  likeness refs:  ${#likeness_refs[@]} file(s) in $LIKENESS_DIR"
  echo "  GOOGLE_API_KEY: $(has_gemini_key && echo set || echo unset)"
  echo "  REPLICATE_API_TOKEN: $(has_replicate_key && echo set || echo unset)"
  echo "  likeness consent: $(consent_ok && echo present || echo missing)"
  if has_gemini_key; then
    echo "  style plates:   ready (bash $0 --execute --style-only)"
  else
    echo "  style plates:   blocked — need GOOGLE_API_KEY"
  fi
  if has_gemini_key && [[ ${#likeness_refs[@]} -gt 0 ]] && consent_ok; then
    echo "  likeness jobs:  ready (bash $0 --execute --likeness-only)"
  else
    missing=()
    has_gemini_key || missing+=("GOOGLE_API_KEY")
    [[ ${#likeness_refs[@]} -gt 0 ]] || missing+=("authorized portraits")
    consent_ok || missing+=("written consent")
    echo "  likeness jobs:  blocked — need ${missing[*]}"
  fi
  echo "  LoRA fallback:  dry-run via bash $0 --train-lora-plan (needs zip URL + REPLICATE to execute)"
  exit 0
fi

if [[ "$TRAIN_LORA_PLAN" -eq 1 ]]; then
  echo "LoRA training plan (dry-run, no spend):"
  "$PY" generate.py train lora --subject tanya --output-dir "$OUT_DIR"
  echo "Execute later only with written consent, a provider-accessible zip URL, and REPLICATE_API_TOKEN."
  exit 0
fi

build_viewer() {
  if [[ -d "$OUT_DIR" ]]; then
    "$PY" generate.py view "$OUT_DIR"
  else
    echo "No run dir yet at $OUT_DIR"
    return 1
  fi
}

if [[ "$REVIEW" -eq 1 && "$EXECUTE" -eq 0 && "$STYLE_ONLY" -eq 0 && "$LIKENESS_ONLY" -eq 0 ]]; then
  build_viewer
  exit 0
fi

will_style=1
will_likeness=1
[[ "$LIKENESS_ONLY" -eq 1 ]] && will_style=0
[[ "$STYLE_ONLY" -eq 1 ]] && will_likeness=0

if [[ "$will_likeness" -eq 1 && ${#likeness_refs[@]} -eq 0 ]]; then
  will_likeness=0
  if [[ "$LIKENESS_ONLY" -eq 1 ]]; then
    echo "Likeness jobs skipped: no photos in $LIKENESS_DIR"
    echo "Drop authorized portraits there, then re-run."
    exit 0
  fi
fi

if [[ "$EXECUTE" -eq 1 ]]; then
  if [[ "$will_style" -eq 1 || "$will_likeness" -eq 1 ]] && ! has_gemini_key; then
    echo "Error: --execute needs GOOGLE_API_KEY (or GEMINI_API_KEY). Use --status." >&2
    exit 2
  fi
  if [[ "$will_likeness" -eq 1 ]] && ! consent_ok; then
    echo "Error: likeness --execute needs written consent." >&2
    echo "Copy examples/slingsby-advisors-intake/CONSENT.example.md to assets/slingsby/CONSENT.md" >&2
    echo "or set SLINGSBY_LIKENESS_CONSENT=1 after Tanya has approved this job." >&2
    exit 3
  fi
fi

dry_flag=(--dry-run --no-viewer)
if [[ "$EXECUTE" -eq 1 ]]; then
  dry_flag=(--no-viewer)
fi

if [[ "$will_style" -eq 1 ]]; then
  style_cmd=(
    "$PY" generate.py
    --prompt-file "$STYLE_PACK"
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
fi

if [[ "$will_likeness" -eq 1 ]]; then
  likeness_cmd=(
    "$PY" generate.py
    --prompt-file "$LIKENESS_PACK"
    --style slingsby
    --reference-role likeness
    --global-reference-images "$(join_csv "${likeness_refs[@]}")"
    --output-dir "$OUT_DIR"
    "${dry_flag[@]}"
  )
  echo "Likeness jobs: ${likeness_cmd[*]}"
  "${likeness_cmd[@]}"
elif [[ "$STYLE_ONLY" -eq 0 && ${#likeness_refs[@]} -eq 0 ]]; then
  echo "Likeness jobs skipped: no photos in $LIKENESS_DIR"
  echo "Drop authorized portraits there, then re-run."
fi

if [[ "$EXECUTE" -eq 1 || "$REVIEW" -eq 1 ]]; then
  build_viewer || true
fi

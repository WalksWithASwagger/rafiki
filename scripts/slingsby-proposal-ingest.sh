#!/usr/bin/env bash
# Ingest operator-supplied style or likeness media into gitignored
# assets/slingsby/. Accepts a PDF, zip, folder, or image files.
#
#   bash scripts/slingsby-proposal-ingest.sh --style /path/to/board.pdf
#   bash scripts/slingsby-proposal-ingest.sh --likeness /path/to/portraits.pdf
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MODE=""
SOURCES=()

for arg in "$@"; do
  case "$arg" in
    --style) MODE=style ;;
    --likeness) MODE=likeness ;;
    -h|--help)
      sed -n '2,10p' "$0"
      exit 0
      ;;
    *)
      SOURCES+=("$arg")
      ;;
  esac
done

if [[ -z "$MODE" ]]; then
  echo "Error: pass --style or --likeness." >&2
  exit 1
fi

if [[ ${#SOURCES[@]} -eq 0 ]]; then
  echo "Error: pass a PDF, zip, folder, or image path." >&2
  echo "Do not ingest the style mood-board PDF as likeness." >&2
  exit 1
fi

if [[ "$MODE" == "style" ]]; then
  DEST="${SLINGSBY_STYLE_INGEST_DIR:-$ROOT/assets/slingsby/style-refs/moodboard/tiles}"
  PAGES="${SLINGSBY_STYLE_PAGES_DIR:-$ROOT/assets/slingsby/style-refs/moodboard/pages}"
else
  DEST="${SLINGSBY_LIKENESS_DIR:-$ROOT/assets/slingsby/likeness}"
  PAGES=""
fi
mkdir -p "$DEST"
[[ -n "$PAGES" ]] && mkdir -p "$PAGES"

is_image() {
  case "${1,,}" in
    *.jpg|*.jpeg|*.png|*.webp) return 0 ;;
    *) return 1 ;;
  esac
}

copy_image() {
  local src="$1" dest_dir="$2"
  local base
  base="$(basename "$src")"
  cp -n "$src" "$dest_dir/$base" 2>/dev/null || cp "$src" "$dest_dir/$base"
  echo "copied $base -> $dest_dir"
}

extract_pdf() {
  local pdf="$1"
  local stem
  stem="$(basename "$pdf" | sed 's/\.[Pp][Dd][Ff]$//')"
  if command -v pdfimages >/dev/null 2>&1; then
    pdfimages -j "$pdf" "$DEST/${stem}-tile"
    echo "extracted embedded images from $pdf -> $DEST"
  fi
  if [[ -n "$PAGES" ]] && command -v pdftoppm >/dev/null 2>&1; then
    pdftoppm -jpeg -r 200 -jpegopt quality=90 "$pdf" "$PAGES/${stem}-page"
    echo "rendered pages from $pdf -> $PAGES"
  elif [[ "$MODE" == "likeness" ]] && command -v pdftoppm >/dev/null 2>&1; then
    pdftoppm -jpeg -r 200 -jpegopt quality=90 "$pdf" "$DEST/${stem}-page"
    echo "rendered pages from $pdf -> $DEST"
  fi
}

extract_zip() {
  local zip="$1"
  python3 - "$zip" "$DEST" <<'PY'
import sys, zipfile
from pathlib import Path
zf = Path(sys.argv[1])
dest = Path(sys.argv[2])
ok = {".jpg", ".jpeg", ".png", ".webp"}
with zipfile.ZipFile(zf) as archive:
    for info in archive.infolist():
        if info.is_dir():
            continue
        suffix = Path(info.filename).suffix.lower()
        if suffix not in ok:
            continue
        name = Path(info.filename).name
        target = dest / name
        target.write_bytes(archive.read(info))
        print(f"unzipped {name} -> {dest}")
PY
}

for src in "${SOURCES[@]}"; do
  if [[ -d "$src" ]]; then
    while IFS= read -r file; do
      [[ -n "$file" ]] && copy_image "$file" "$DEST"
    done < <(find "$src" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' \) | sort)
  elif [[ -f "$src" ]]; then
    case "${src,,}" in
      *.pdf) extract_pdf "$src" ;;
      *.zip) extract_zip "$src" ;;
      *)
        if is_image "$src"; then
          copy_image "$src" "$DEST"
        else
          echo "skip unsupported: $src" >&2
        fi
        ;;
    esac
  else
    echo "skip missing: $src" >&2
  fi
done

# Likeness: drop obvious tiny icons. Style tiles already curated separately.
if [[ "$MODE" == "likeness" ]]; then
  python3 - "$DEST" <<'PY'
import sys
from pathlib import Path
try:
    from PIL import Image
except ImportError:
    raise SystemExit(0)
dest = Path(sys.argv[1])
for path in dest.iterdir():
    if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
        continue
    try:
        with Image.open(path) as image:
            width, height = image.size
    except OSError:
        continue
    if min(width, height) < 250:
        path.unlink()
        print(f"dropped tiny {path.name} ({width}x{height})")
PY
fi

count=$(find "$DEST" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' \) | wc -l)
echo "Ingested $MODE media. Image files now in $DEST: $count"
echo "Next: bash scripts/slingsby-proposal-generate.sh --status"
if [[ "$MODE" == "likeness" ]]; then
  echo "Likeness execute still needs assets/slingsby/CONSENT.md and GOOGLE_API_KEY."
fi

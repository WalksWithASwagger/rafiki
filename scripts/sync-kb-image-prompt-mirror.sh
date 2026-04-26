#!/usr/bin/env bash
# Rebuild prompts/kb-ecosystem-mirror from a local kk-b (kk-ai-ecosystem) clone.
# Usage: from repo root: ./scripts/sync-kb-image-prompt-mirror.sh
# Optional: KB_ROOT=/path/to/kk-ai-ecosystem

set -euo pipefail
RAFIKI_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
KB_ROOT="${KB_ROOT:-$RAFIKI_ROOT/../kk-ai-ecosystem}"
DEST="$RAFIKI_ROOT/prompts/kb-ecosystem-mirror"

if [[ ! -d "$KB_ROOT" ]]; then
  echo "Expected kk-ai-ecosystem at: $KB_ROOT" >&2
  echo "Set KB_ROOT= to your clone path." >&2
  exit 1
fi

echo "Rebuilding $DEST from $KB_ROOT"
rm -rf "$DEST"
mkdir -p "$DEST"
cd "$KB_ROOT"
while IFS= read -r f; do
  rel="${f#./}"
  d="$DEST/$(dirname "$rel")"
  mkdir -p "$d"
  cp "$f" "$DEST/$rel"
done < <(find . -type f \( -name 'image-prompts.md' -o -name 'image-prompts*.md' -o -name 'image-prompt*.md' -o -name 'image-gen-prompts.md' \) 2>/dev/null | grep -v node_modules | grep -v '.git')

# Overlays: KB may still point here with stubs; keep full bodies in the mirror
CM_SRC="$RAFIKI_ROOT/prompts/creative-mornings-vancouver-may-2026/image-gen-prompts.md"
if [[ -f "$CM_SRC" ]]; then
  mkdir -p "$DEST/projects/02-bc-ai-ecosystem-nonprofit/speaking-engagements/2026/creative-mornings-vancouver-may-2026/slides"
  cp "$CM_SRC" "$DEST/projects/02-bc-ai-ecosystem-nonprofit/speaking-engagements/2026/creative-mornings-vancouver-may-2026/slides/image-gen-prompts.md"
fi
WAIFF_SRC="$RAFIKI_ROOT/prompts/kk-kb/waiff-brazil-2026-keynote-image-prompts.md"
if [[ -f "$WAIFF_SRC" ]]; then
  mkdir -p "$DEST/projects/03-theupgrade-ai-training/speaking-engagements/uai-film-festival-brazil-2026"
  cp "$WAIFF_SRC" "$DEST/projects/03-theupgrade-ai-training/speaking-engagements/uai-film-festival-brazil-2026/image-prompts.md"
fi

n="$(find "$DEST" -type f | wc -l | tr -d ' ')"
echo "Done. $n files under kb-ecosystem-mirror/"

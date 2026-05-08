#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
REFERENCE_LINK_RE = re.compile(r"^\s*\[[^\]\n]+\]:\s*(\S+)", re.MULTILINE)


def markdown_sources() -> list[Path]:
    sources = [ROOT / "README.md"]
    sources.extend(sorted(DOCS_DIR.glob("**/*.md")))
    return [source for source in sources if source.exists()]


def split_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")]
    return target.split()[0]


def is_external(target: str) -> bool:
    parsed = urlsplit(target)
    return bool(parsed.scheme or parsed.netloc)


def candidate_path(source: Path, target: str) -> Path | None:
    if not target or target.startswith("#") or is_external(target):
        return None

    parsed = urlsplit(target)
    path = unquote(parsed.path)
    if not path or Path(path).suffix.lower() != ".md":
        return None

    if path.startswith("/"):
        return ROOT / path.lstrip("/")
    return source.parent / path


def iter_link_targets(content: str) -> list[str]:
    targets = [match.group(1) for match in MARKDOWN_LINK_RE.finditer(content)]
    targets.extend(match.group(1) for match in REFERENCE_LINK_RE.finditer(content))
    return targets


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def main() -> int:
    missing: list[tuple[Path, str, Path]] = []
    sources = markdown_sources()

    for source in sources:
        content = source.read_text(encoding="utf-8")
        for raw_target in iter_link_targets(content):
            target = split_target(raw_target)
            candidate = candidate_path(source, target)
            if candidate is None:
                continue
            if not candidate.resolve().is_file():
                missing.append((source, target, candidate))

    if missing:
        print("Missing local Markdown links:")
        for source, target, candidate in missing:
            print(f"- {source.relative_to(ROOT)}: {target} -> {display_path(candidate)}")
        return 1

    print(f"Checked {len(sources)} Markdown files; all local Markdown links resolved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

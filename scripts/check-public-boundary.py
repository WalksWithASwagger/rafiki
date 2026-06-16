#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

BANNED_PREFIXES: dict[str, str] = {
    ".pytest_cache/": "pytest cache is local state",
    ".rafiki-cache/": "thumbnail cache is local state",
    ".ruff_cache/": "ruff cache is local state",
    ".venv/": "virtualenv files are local state",
    "assets/": "generated/private assets are not part of the public tool repo",
    "node_modules/": "Node dependencies are restored from package-lock.json",
    "output/": "generated review outputs are local state",
    "outputs/": "generated outputs are local state",
    "prompts/": "private prompt libraries are not part of the public tool repo",
    "data/jobs/": "local job records are not public repo state",
}

BANNED_FILES: dict[str, str] = {
    ".DS_Store": "macOS metadata is local state",
    ".env": "environment files may contain secrets",
    "data/asset-registry.csv": "asset registry exports are local cache",
    "data/asset-registry.json": "asset registry exports are local cache",
    "data/billing-imports.json": "billing imports are private local state",
    "data/media-registry.csv": "media registry exports are local cache",
    "data/media-registry.json": "media registry exports are local cache",
    "data/usage-log.json": "usage logs are private local state",
    "data/video-selections.json": "video selections are local state",
    "config/extra-outputs.local.json": "local output mappings are machine-specific",
    "config/loose-imports.local.json": "loose import mappings are machine-specific",
    "config/media-roots.local.json": "media roots are machine-specific",
    "config/scheduled-regen.json": "scheduled regen config is local state",
}

BANNED_SUFFIXES: dict[str, str] = {
    ".pyc": "Python bytecode is generated cache",
    ".pyo": "Python optimized bytecode is generated cache",
    ".tgz": "package tarballs are generated artifacts",
}

# Explicit public fixtures that override a banned prefix/file/suffix.
# Each entry is an intentional, reviewed exception to the tool-only boundary.
ALLOWED_EXCEPTIONS: dict[str, str] = {
    "prompts/bcai/ed-ai-logo-variations.md": "public BC+AI ED+AI logo prompt kit, intentionally shipped",
}


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def public_boundary_violations(paths: list[str]) -> list[tuple[str, str]]:
    violations: list[tuple[str, str]] = []
    for path in sorted(paths):
        normalized = path.replace("\\", "/")
        if normalized in ALLOWED_EXCEPTIONS:
            continue
        reason = BANNED_FILES.get(normalized)
        if reason is None:
            reason = next(
                (prefix_reason for prefix, prefix_reason in BANNED_PREFIXES.items() if normalized.startswith(prefix)),
                None,
            )
        if reason is None:
            reason = next(
                (suffix_reason for suffix, suffix_reason in BANNED_SUFFIXES.items() if normalized.endswith(suffix)),
                None,
            )
        if reason is not None:
            violations.append((normalized, reason))
    return violations


def main() -> int:
    violations = public_boundary_violations(tracked_files())
    if not violations:
        print("Public boundary check passed: no local/generated surfaces are tracked.")
        return 0

    print("Public boundary check failed: tracked files include local/generated surfaces.", file=sys.stderr)
    for path, reason in violations:
        print(f"- {path}: {reason}", file=sys.stderr)
    print("\nRemove these from git tracking or document an explicit public fixture exception.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

"""LLM social-post expansion — platform-specific variants from generated runs.

After a Rafiki batch generates images, this module runs a second LLM pass
that takes each item's title + caption and produces platform-specific
social copy (LinkedIn long-form, X short, Instagram). Output lives in
``<latest-run>/social-posts.json`` for downstream tools and the
presentation viewer's platform toggle.

Source preference (first match wins):
    1. ``<latest-run>/social-posts.md``  (PR #19, parsed line-by-line)
    2. ``prompts/.../<project>-viewer-data.json``  (PR #36)
    3. ``<latest-run>/run.json``  (always present after a batch)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

DEFAULT_PLATFORMS = ["linkedin", "x", "instagram"]
DEFAULT_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """You are writing social media posts for a creator focused on AI & society.
Given an image title, caption, and optional source post, produce platform-specific variants.

Platform constraints:
- linkedin: 150–250 words, professional thought-leadership tone, 3–5 hashtags at the end, opens with a hook
- x: under 280 characters total including hashtags, punchy single-thought, 2–3 hashtags
- instagram: 3–5 sentences, evocative/visual tone, 8–10 hashtags at the end (one per line OK), emoji optional

Return strict JSON with the requested platform keys only. No explanation, no preamble."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _resolve_project_dir(project: str) -> Path:
    """Resolve a project arg to its on-disk directory."""
    p = Path(project)
    if p.exists() and p.is_dir():
        return p
    candidate = _repo_root() / "output" / project
    if candidate.exists():
        return candidate
    raise FileNotFoundError(
        f"Project not found: {project!r} (tried {p} and {candidate})"
    )


def _latest_run_dir(project_dir: Path) -> Path:
    """Return the most recent run-* dir under project_dir."""
    runs = sorted(project_dir.glob("run-*"))
    if not runs:
        raise FileNotFoundError(f"No run-* dirs under {project_dir}")
    return runs[-1]


def _viewer_data_path(project: str) -> Path | None:
    """Locate prompts/.../<project>-viewer-data.json if it exists."""
    root = _repo_root() / "prompts"
    if not root.exists():
        return None
    # Use only the project basename — absolute paths would break rglob.
    name = Path(project).name
    if not name:
        return None
    matches = list(root.rglob(f"{name}-viewer-data.json"))
    return matches[0] if matches else None


def _slug_from_file(filename: str) -> str:
    return Path(filename).stem


def _items_from_run_json(run_dir: Path) -> list[dict]:
    """Build expansion items from run.json (always-present fallback)."""
    rj = run_dir / "run.json"
    data = json.loads(rj.read_text(encoding="utf-8"))
    items: list[dict] = []
    for img in data.get("images", []):
        if not img.get("prompt"):
            continue
        items.append({
            "slug": _slug_from_file(img["file"]),
            "title": img.get("name", img["file"]),
            "caption": img.get("prompt", ""),
            "social": img.get("social"),
        })
    return items


def _items_from_viewer_data(path: Path) -> list[dict]:
    """Build items from a viewer-data.json (PR #36 shape — best-effort)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    raw_items = data.get("items") if isinstance(data, dict) else data
    items: list[dict] = []
    for entry in raw_items or []:
        slug = entry.get("slug") or _slug_from_file(entry.get("file", ""))
        if not slug:
            continue
        items.append({
            "slug": slug,
            "title": entry.get("title") or entry.get("name") or slug,
            "caption": entry.get("caption") or entry.get("prompt") or "",
            "social": entry.get("social"),
        })
    return items


def _items_from_social_md(path: Path) -> list[dict]:
    """Parse a social-posts.md file (PR #19) into expansion items.

    Format expected: H2 headings as item titles, body paragraphs as caption.
    Best-effort — falls back gracefully if the file uses a different shape.
    """
    text = path.read_text(encoding="utf-8")
    items: list[dict] = []
    current: dict | None = None
    body: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if current is not None:
                current["caption"] = "\n".join(body).strip()
                items.append(current)
            title = line[3:].strip()
            slug = title.lower().replace(" ", "-")
            current = {"slug": slug, "title": title, "caption": "", "social": None}
            body = []
        elif current is not None:
            body.append(line)
    if current is not None:
        current["caption"] = "\n".join(body).strip()
        items.append(current)
    return items


def _load_items(project: str, run_dir: Path) -> list[dict]:
    """Return source items, preferring social-posts.md > viewer-data > run.json."""
    md_path = run_dir / "social-posts.md"
    if md_path.exists():
        items = _items_from_social_md(md_path)
        if items:
            return items
    viewer_path = _viewer_data_path(project)
    if viewer_path is not None:
        items = _items_from_viewer_data(viewer_path)
        if items:
            return items
    return _items_from_run_json(run_dir)


def _build_user_prompt(item: dict, platforms: list[str]) -> str:
    parts = [
        f"Title: {item['title']}",
        f"Caption: {item['caption']}",
    ]
    if item.get("social"):
        parts.append(f"Source post: {item['social']}")
    parts.append(f"Platforms requested: {', '.join(platforms)}")
    return "\n".join(parts)


def _call_openai(client, model: str, item: dict, platforms: list[str]) -> dict:
    """Single chat.completions.create call returning a dict of platform → text."""
    user_prompt = _build_user_prompt(item, platforms)
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    raw = response.choices[0].message.content
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError(f"Expected JSON object, got {type(parsed).__name__}")
    return {k: parsed[k] for k in platforms if k in parsed}


def expand(
    project: str,
    *,
    platforms: list[str] | None = None,
    model: str = DEFAULT_MODEL,
    dry_run: bool = False,
) -> dict:
    """Generate platform-specific social variants for a project's latest run.

    Writes ``<latest-run-dir>/social-posts.json`` and returns the same dict.

    Args:
        project: Project name under ``output/`` or a direct project dir path.
        platforms: Subset of platforms to generate (default: linkedin, x, instagram).
        model: OpenAI chat model id (default: gpt-4o-mini).
        dry_run: Skip API calls; write a placeholder file showing what would run.

    Raises:
        FileNotFoundError: project dir or run-* dir is missing.
        RuntimeError: OPENAI_API_KEY is not set (only when dry_run=False).
    """
    platforms = platforms or DEFAULT_PLATFORMS

    if not dry_run and not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not set. "
            "Get one at https://platform.openai.com/api-keys and export it."
        )

    project_dir = _resolve_project_dir(project)
    run_dir = _latest_run_dir(project_dir)
    items = _load_items(project, run_dir)
    out_path = run_dir / "social-posts.json"

    if dry_run:
        placeholder = {
            item["slug"]: {
                "title": item["title"],
                "caption": item["caption"],
                "platforms": {p: f"[dry-run: would generate {p}]" for p in platforms},
            }
            for item in items
        }
        out_path.write_text(json.dumps(placeholder, indent=2), encoding="utf-8")
        print(f"Dry-run: would expand {len(items)} item(s) → {out_path}")
        return placeholder

    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    result: dict = {}
    for item in items:
        try:
            variants = _call_openai(client, model, item, platforms)
        except (json.JSONDecodeError, ValueError) as e:
            print(
                f"  skip {item['slug']}: invalid JSON from model ({e})",
                file=sys.stderr,
            )
            continue
        except Exception as e:
            print(f"  skip {item['slug']}: {e}", file=sys.stderr)
            continue
        result[item["slug"]] = {
            "title": item["title"],
            "caption": item["caption"],
            "platforms": variants,
        }
        print(f"  expand {item['slug']}: {', '.join(variants.keys())}")

    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {out_path} ({len(result)}/{len(items)} items)")
    return result

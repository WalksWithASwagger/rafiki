#!/usr/bin/env python3
"""
Rafiki — multi-provider image generator

Providers:
  Gemini (Google)  — gemini-2.5-flash-image, gemini-3-pro-image-preview
  OpenAI           — gpt-image-2, gpt-image-1, dall-e-3, dall-e-2

Model aliases: flash, nano, pro (Gemini) · gpt, gpt1, dalle3, dalle2 (OpenAI)
Style composition: --style kk+bcai stacks both style suffixes

Usage:
    python generate.py --prompt "A creative professional..." --output image.png
    python generate.py --prompt "..." -m gpt --quality high
    python generate.py -f image-prompts.md -d ./images/ --workers 4
    python generate.py --list-styles
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Auto-load .env from repo root so API keys work without `source .env`
def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    import os
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

_load_dotenv(Path(__file__).parent / ".env")

from lib.core import generate_image
from lib.models import resolve_model, ALIASES
from lib.prompts import parse_image_prompts_md, ASPECT_RATIOS
from lib.styles import load_styles, get_default_style
from lib.usage import load_usage_log
from lib.batch import run_batch

# Re-export for MCP server and other importers that do `import generate`
__all__ = [
    "generate_image",
    "parse_image_prompts_md",
    "load_styles",
    "get_default_style",
]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rafiki — AI image generator (Gemini + OpenAI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join([
            "Model aliases: " + ", ".join(f"{k}→{v}" for k, v in ALIASES.items()),
            "Style composition: --style kk+bcai stacks both style suffixes",
        ]),
    )

    parser.add_argument("--prompt", "-p", help="Text prompt for image generation")
    parser.add_argument("--prompt-file", "-f", help="Path to image-prompts.md file")
    parser.add_argument("--output", "-o", default="output.png",
                        help="Output file path (default: output.png)")
    parser.add_argument("--output-dir", "-d",
                        help="Output directory for batch runs")
    parser.add_argument(
        "--model", "-m", default="gemini-2.5-flash-image",
        help=(
            "Model ID or alias (default: gemini-2.5-flash-image). "
            "Aliases: flash/nano/pro (Gemini), gpt/gpt1/dalle3 (OpenAI). "
            "Full IDs: gpt-image-2, dall-e-3, gemini-3-pro-image-preview."
        ),
    )
    parser.add_argument("--quality", "-q", default="high",
                        choices=["low", "medium", "high"],
                        help="Quality for OpenAI models (default: high). Ignored by Gemini.")
    parser.add_argument("--aspect-ratio", "-a", default="16:9",
                        help="Aspect ratio (default: 16:9). Presets: linkedin, instagram, twitter, story, square")
    parser.add_argument("--resolution", "-r", default="1K",
                        choices=["1K", "2K", "4K"],
                        help="Resolution (default: 1K). 2K/4K: Gemini Pro only.")
    parser.add_argument(
        "--style", "-s", default=None,
        help=(
            "Style preset or composed spec (e.g. kk, bcai, kk+bcai). "
            "Use 'none' for no style. Default: kk. Run --list-styles to see all."
        ),
    )
    parser.add_argument("--no-style", action="store_true",
                        help="No style suffix (same as --style none)")
    parser.add_argument("--list-styles", action="store_true",
                        help="Show available styles and exit")
    parser.add_argument("--reference-image", "--ref",
                        help="Path to reference image for style/composition guidance")
    parser.add_argument(
        "--reference-images", metavar="PATHS",
        help=(
            "Comma-separated reference image paths for batch mode. "
            "One path per prompt (in order), or a single path to reuse for all."
        ),
    )
    parser.add_argument("--reference-role", choices=["style", "mockup"], default="style",
                        help="'style' (look-and-feel) or 'mockup' (preserve garment + add print)")
    parser.add_argument("--composition-references", metavar="PATHS",
                        help="Extra comma-separated ref images for mockup mode")
    parser.add_argument("--workers", "-w", type=int, default=1, metavar="N",
                        help="Parallel generation workers for batch mode (default: 1)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without calling any API")
    parser.add_argument("--no-viewer", action="store_true",
                        help="Skip generating viewer.html after a batch run")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Emit structured JSON to stdout; progress to stderr")
    parser.add_argument("--usage", action="store_true",
                        help="Show usage statistics")

    args = parser.parse_args()

    # JSON mode: all print() → stderr so stdout carries only the result JSON
    _real_stdout = sys.stdout
    if args.json_output:
        sys.stdout = sys.stderr

    # Resolve model alias early
    args.model = resolve_model(args.model)

    # Resolve aspect ratio preset
    if args.aspect_ratio in ASPECT_RATIOS:
        args.aspect_ratio = ASPECT_RATIOS[args.aspect_ratio]

    composition_refs: list[str] | None = None
    if args.composition_references:
        composition_refs = [p.strip() for p in args.composition_references.split(",") if p.strip()]
        if not composition_refs:
            print("Error: --composition-references has no paths")
            sys.exit(1)

    # ── Informational flags ──────────────────────────────────────────────────

    if args.list_styles:
        styles = load_styles()
        print("Available styles:")
        for name, cfg in styles.items():
            marker = " (default)" if cfg.get("default") else ""
            print(f"  {name}{marker}: {cfg.get('description', '')}")
        print("\nTip: compose styles with '+', e.g.  --style kk+bcai")
        return

    if args.usage:
        data = load_usage_log()
        print(f"Total images generated: {data['total_images']}")
        if data["entries"]:
            print("\nRecent generations:")
            for entry in data["entries"][-5:]:
                print(f"  {entry['timestamp']}: {entry['model']} → {entry['output']}")
        return

    # ── Style resolution ─────────────────────────────────────────────────────

    style = "none" if args.no_style else args.style

    # ── Reference image helpers ───────────────────────────────────────────────

    def _resolve_ref_list(n: int) -> list[str | None]:
        if args.reference_images and args.reference_image:
            print("Error: use --reference-image OR --reference-images, not both")
            sys.exit(1)
        if args.reference_images:
            parts = [p.strip() for p in args.reference_images.split(",") if p.strip()]
            if not parts:
                print("Error: --reference-images has no paths")
                sys.exit(1)
            if len(parts) == 1:
                return parts * n
            if len(parts) != n:
                print(
                    f"Error: --reference-images has {len(parts)} paths "
                    f"but {n} prompts"
                )
                sys.exit(1)
            return parts
        single = args.reference_image
        return [single] * n if single else [None] * n

    # ── Single prompt ────────────────────────────────────────────────────────

    if args.prompt:
        if args.reference_images:
            print("Error: --reference-images is for batch mode (--prompt-file)")
            sys.exit(1)
        success = generate_image(
            prompt=args.prompt,
            output_path=args.output,
            model=args.model,
            aspect_ratio=args.aspect_ratio,
            resolution=args.resolution,
            quality=args.quality,
            style=style,
            reference_image=args.reference_image,
            reference_role=args.reference_role,
            composition_references=composition_refs,
            dry_run=args.dry_run,
        )
        if args.json_output:
            _real_stdout.write(json.dumps({
                "success": success,
                "mode": "single",
                "dry_run": args.dry_run,
                "output_path": args.output,
                "model": args.model,
                "aspect_ratio": args.aspect_ratio,
                "style": style or "none",
                "prompt_preview": args.prompt[:120],
            }, indent=2) + "\n")
        sys.exit(0 if success else 1)

    # ── Batch from prompt file ────────────────────────────────────────────────

    if args.prompt_file:
        prompts = parse_image_prompts_md(args.prompt_file)
        print(f"Found {len(prompts)} prompts in {args.prompt_file}")

        project_dir = Path(args.output_dir or Path(args.prompt_file).parent / "images")
        ref_paths = _resolve_ref_list(len(prompts))

        result = run_batch(
            prompts=prompts,
            project_dir=project_dir,
            model=args.model,
            aspect_ratio=args.aspect_ratio,
            resolution=args.resolution,
            quality=args.quality,
            style=style,
            ref_paths=ref_paths,
            reference_role=args.reference_role,
            composition_references=composition_refs,
            dry_run=args.dry_run,
            workers=args.workers,
            generate_viewer_html=not args.no_viewer,
            prompt_file=args.prompt_file,
        )

        if args.json_output:
            _real_stdout.write(json.dumps({
                "success": result.success,
                "mode": "batch",
                "dry_run": args.dry_run,
                "generated": result.success_count,
                "total": result.total,
                "project_dir": str(result.project_dir),
                "run_dir": str(result.run_dir),
                "run_id": result.run_id,
                "viewer_path": result.viewer_path,
                "model": args.model,
                "aspect_ratio": args.aspect_ratio,
                "style": style or "none",
                "images": result.images,
            }, indent=2) + "\n")

        sys.exit(0 if result.success else 1)

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()

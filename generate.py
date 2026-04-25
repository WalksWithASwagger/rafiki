#!/usr/bin/env python3
"""
Rafiki — multi-provider image generator

Providers:
  Gemini (Google)  — gemini-2.5-flash-image, gemini-3-pro-image-preview, …
  OpenAI           — gpt-image-1, gpt-image-2, dall-e-3, dall-e-2

Usage:
    python generate.py --prompt "A creative professional..." --output image.png
    python generate.py --prompt "..." --model gpt-image-2 --quality high
    python generate.py --prompt-file image-prompts.md --output-dir ./images/
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from datetime import datetime

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)


# Style configuration path
STYLES_CONFIG_PATH = Path(__file__).parent / "styles" / "styles.yaml"

# Legacy constant for backward compatibility (deprecated)
KK_STYLE_SUFFIX = """
Style guidelines: Dark background (#0f0f1a to #1a1a2e gradient), teal (#00c8b4) and purple (#9333ea) accent colors, high contrast, modern editorial illustration style, professional and polished.
"""


def load_styles() -> dict:
    """Load style definitions from YAML config."""
    if STYLES_CONFIG_PATH.exists():
        with open(STYLES_CONFIG_PATH) as f:
            config = yaml.safe_load(f)
            return config.get('styles', {})
    return {}


def get_default_style() -> str:
    """Get the default style name from config."""
    styles = load_styles()
    for name, config in styles.items():
        if config.get('default', False):
            return name
    return 'kk'  # Fallback to kk style


def get_style_suffix(style_name: str) -> str:
    """Get style suffix for a given style name."""
    styles = load_styles()
    if style_name in styles:
        return styles[style_name].get('suffix', '')
    return ''

# Default aspect ratios for different platforms
ASPECT_RATIOS = {
    "linkedin": "16:9",
    "instagram": "1:1",
    "twitter": "16:9",
    "story": "9:16",
    "square": "1:1",
}

# Cost tracking
USAGE_LOG_PATH = Path(__file__).parent / "data" / "usage-log.json"


def get_cache_key(prompt: str, aspect_ratio: str, model: str) -> str:
    """Generate content-addressed cache key."""
    content = f"{prompt}|{aspect_ratio}|{model}"
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def load_usage_log() -> dict:
    """Load usage tracking data."""
    if USAGE_LOG_PATH.exists():
        with open(USAGE_LOG_PATH) as f:
            return json.load(f)
    return {"entries": [], "total_images": 0}


def save_usage_log(data: dict):
    """Save usage tracking data."""
    USAGE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(USAGE_LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)


def log_generation(prompt: str, model: str, output_path: str, aspect_ratio: str):
    """Log image generation for tracking."""
    data = load_usage_log()
    data["entries"].append({
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "aspect_ratio": aspect_ratio,
        "output": str(output_path),
        "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt
    })
    data["total_images"] = len(data["entries"])
    save_usage_log(data)


def parse_image_prompts_md(file_path: str) -> list[dict]:
    """Parse image-prompts.md file format."""
    with open(file_path) as f:
        content = f.read()

    prompts = []
    # Split by ## numbered sections
    sections = re.split(r'^## \d+\.', content, flags=re.MULTILINE)[1:]

    for section in sections:
        lines = section.strip().split('\n')
        name = lines[0].strip() if lines else "Untitled"

        # Extract fields
        usage = ""
        prompt_text = ""

        for_match = re.search(r'\*\*For:\*\*\s*(.+)', section)
        if for_match:
            usage = for_match.group(1).strip()

        # Capture markdown blockquote line(s) after **Prompt:**. Do not use \*\* as a
        # terminator — prompts often contain **bold** markdown, which previously
        # truncated the text and sent broken fragments to the image API.
        prompt_block = re.search(
            r'\*\*Prompt:\*\*\s*\n((?:>[^\n]*(?:\n|$))+)',
            section,
            re.MULTILINE,
        )
        if prompt_block:
            raw = prompt_block.group(1)
            lines_out = []
            for line in raw.splitlines():
                if line.startswith('>'):
                    lines_out.append(line[1:].lstrip())
                elif line.strip() == '':
                    lines_out.append('')
                elif lines_out:
                    # Rare: wrapped continuation without '>' — append to previous line
                    lines_out[-1] = f"{lines_out[-1]} {line.strip()}".strip()
            prompt_text = '\n'.join(lines_out).strip()

        if prompt_text:
            prompts.append({
                "name": name,
                "usage": usage,
                "prompt": prompt_text
            })

    return prompts


def generate_image(
    prompt: str,
    output_path: str,
    model: str = "gemini-2.5-flash-image",
    aspect_ratio: str = "16:9",
    resolution: str = "1K",
    quality: str = "high",
    style: str | None = None,
    reference_image: str | None = None,
    reference_role: str = "style",
    composition_references: list[str] | None = None,
    dry_run: bool = False,
) -> bool:
    """Generate an image via the appropriate provider for the given model.

    Args:
        prompt: Text prompt for image generation.
        output_path: Where to save the generated image.
        model: Model ID — any gemini-*, gpt-image-*, or dall-e-* string.
        aspect_ratio: Aspect ratio string or preset name.
        resolution: Resolution hint (1K/2K/4K). Used by Gemini Pro.
        quality: Quality hint (low/medium/high). Used by OpenAI models.
        style: Style preset name, 'none', or None (uses default).
        reference_image: Path to a reference image for style/composition guidance.
        reference_role: 'style' (look-and-feel only) or 'mockup' (preserve garment).
        composition_references: Extra print-art ref paths (mockup mode only).
        dry_run: Preview parameters without calling any API.
    """
    if style is None:
        style = get_default_style()

    if dry_run:
        provider_name = "OpenAI" if model.startswith(("gpt-image", "dall-e")) else "Gemini"
        print("[DRY RUN] Would generate image:")
        print(f"  Provider: {provider_name}")
        print(f"  Model: {model}")
        print(f"  Aspect ratio: {aspect_ratio}")
        print(f"  Resolution: {resolution}  Quality: {quality}")
        print(f"  Style: {style}  Reference role: {reference_role}")
        if composition_references:
            print(f"  Composition refs: {len(composition_references)} image(s)")
        print(f"  Output: {output_path}")
        print(f"  Prompt: {prompt[:200]}...")
        return True

    # Apply style suffix before handing off to provider
    full_prompt = prompt
    if style and style != "none":
        suffix = get_style_suffix(style)
        if suffix:
            full_prompt = f"{prompt}\n\n{suffix}"
        else:
            print(f"Warning: Unknown style '{style}', using prompt without style suffix")

    print(f"Generating image with {model}...")
    print(f"  Aspect ratio: {aspect_ratio}")
    print(f"  Prompt: {prompt[:100]}...")

    # Route to provider
    sys.path.insert(0, str(Path(__file__).parent))
    from lib.providers import get_provider
    try:
        provider = get_provider(model)
    except ValueError as e:
        print(f"Error: {e}")
        return False

    success = provider.generate(
        prompt=full_prompt,
        output_path=output_path,
        model=model,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        quality=quality,
        reference_image=reference_image,
        reference_role=reference_role,
        composition_references=composition_references,
    )

    if success:
        log_generation(prompt, model, output_path, aspect_ratio)

    return success


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Google Nano Banana (Gemini)"
    )

    parser.add_argument(
        "--prompt", "-p",
        help="Text prompt for image generation"
    )
    parser.add_argument(
        "--prompt-file", "-f",
        help="Path to image-prompts.md file"
    )
    parser.add_argument(
        "--output", "-o",
        default="output.png",
        help="Output file path (default: output.png)"
    )
    parser.add_argument(
        "--output-dir", "-d",
        help="Output directory (for batch processing)"
    )
    parser.add_argument(
        "--model", "-m",
        default="gemini-2.5-flash-image",
        help=(
            "Model to use (default: gemini-2.5-flash-image). "
            "Gemini: gemini-2.5-flash-image, gemini-3-pro-image-preview. "
            "OpenAI: gpt-image-2, gpt-image-1, dall-e-3, dall-e-2."
        ),
    )
    parser.add_argument(
        "--quality", "-q",
        default="high",
        choices=["low", "medium", "high"],
        help=(
            "Image quality for OpenAI models (default: high). "
            "Ignored by Gemini (use --resolution instead)."
        ),
    )
    parser.add_argument(
        "--aspect-ratio", "-a",
        default="16:9",
        help="Aspect ratio (default: 16:9). Presets: linkedin, instagram, twitter, story, square"
    )
    parser.add_argument(
        "--resolution", "-r",
        default="1K",
        choices=["1K", "2K", "4K"],
        help="Resolution (default: 1K). 2K/4K only for Pro model"
    )
    parser.add_argument(
        "--style", "-s",
        default=None,
        help="Style to apply (kk, hopecode, bcai, or 'none'). Use --list-styles to see available. Default: kk"
    )
    parser.add_argument(
        "--no-style",
        action="store_true",
        help="Don't add any style suffix (same as --style=none)"
    )
    parser.add_argument(
        "--list-styles",
        action="store_true",
        help="Show available styles and exit"
    )
    parser.add_argument(
        "--reference-image", "--ref",
        help="Path to reference image file for style/composition guidance",
    )
    parser.add_argument(
        "--reference-images",
        metavar="PATHS",
        help=(
            "Comma-separated reference image paths for batch mode (--prompt-file). "
            "Must be one path per prompt, in the same order; or a single path to reuse for every prompt. "
            "Overrides --reference-image when set."
        ),
    )
    parser.add_argument(
        "--reference-role",
        choices=["style", "mockup"],
        default="style",
        help=(
            "How to use --reference-image(s): "
            "'style' = look-and-feel only (default); "
            "'mockup' = preserve a real garment photo and add the described print."
        ),
    )
    parser.add_argument(
        "--composition-references",
        metavar="PATHS",
        help=(
            "Comma-separated extra images (only with --reference-role mockup). "
            "Sent after the garment photo as print layout / art-direction references."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without calling API",
    )
    parser.add_argument(
        "--no-viewer",
        action="store_true",
        help="Skip generating viewer.html after a batch run",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Emit structured JSON result to stdout; send progress to stderr (for agents/pipelines)",
    )
    parser.add_argument(
        "--usage",
        action="store_true",
        help="Show usage statistics",
    )

    args = parser.parse_args()

    # JSON mode: redirect all print() → stderr so stdout carries only the JSON result
    _real_stdout = sys.stdout
    if args.json_output:
        sys.stdout = sys.stderr

    composition_ref_list: list[str] | None = None
    if args.composition_references:
        composition_ref_list = [
            p.strip() for p in args.composition_references.split(",") if p.strip()
        ]
        if not composition_ref_list:
            print("Error: --composition-references has no paths")
            sys.exit(1)

    # Handle aspect ratio presets
    if args.aspect_ratio in ASPECT_RATIOS:
        args.aspect_ratio = ASPECT_RATIOS[args.aspect_ratio]

    # Show available styles
    if args.list_styles:
        styles = load_styles()
        print("Available styles:")
        for name, config in styles.items():
            default_marker = " (default)" if config.get('default') else ""
            print(f"  {name}{default_marker}: {config.get('description', 'No description')}")
        return

    # Show usage stats
    if args.usage:
        data = load_usage_log()
        print(f"Total images generated: {data['total_images']}")
        if data["entries"]:
            print("\nRecent generations:")
            for entry in data["entries"][-5:]:
                print(f"  {entry['timestamp']}: {entry['model']} -> {entry['output']}")
        return

    # Determine style to use
    style = 'none' if args.no_style else args.style

    def resolve_reference_list(n_prompts: int) -> list[str | None]:
        """Return list of ref paths aligned with batch prompts (or all None)."""
        if args.reference_images and args.reference_image:
            print("Error: use either --reference-image or --reference-images, not both")
            sys.exit(1)
        if args.reference_images:
            parts = [p.strip() for p in args.reference_images.split(",") if p.strip()]
            if not parts:
                print("Error: --reference-images has no paths")
                sys.exit(1)
            if len(parts) == 1:
                return parts * n_prompts
            if len(parts) != n_prompts:
                print(
                    f"Error: --reference-images has {len(parts)} paths but "
                    f"{n_prompts} prompts (or pass exactly one path to reuse)"
                )
                sys.exit(1)
            return parts
        single = args.reference_image
        return [single] * n_prompts if single else [None] * n_prompts

    # Single prompt
    if args.prompt:
        if args.reference_images:
            print("Error: --reference-images is only for batch mode (--prompt-file)")
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
            composition_references=composition_ref_list,
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

    # Batch from file
    if args.prompt_file:
        prompts = parse_image_prompts_md(args.prompt_file)
        print(f"Found {len(prompts)} prompts in {args.prompt_file}")

        project_dir = Path(args.output_dir or Path(args.prompt_file).parent / "images")
        project_dir.mkdir(parents=True, exist_ok=True)

        # Each run gets its own timestamped subdirectory so generations are never overwritten
        run_ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        run_dir = project_dir / f"run-{run_ts}"
        run_dir.mkdir(parents=True, exist_ok=True)

        ref_paths = resolve_reference_list(len(prompts))

        run_meta = {
            "model": args.model,
            "aspect_ratio": args.aspect_ratio,
            "style": style or "none",
            "prompt_file": args.prompt_file,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "run_id": run_ts,
        }

        viewer_items: list[dict] = []
        success_count = 0
        for i, item in enumerate(prompts, 1):
            safe_name = re.sub(r'[^a-z0-9]+', '-', item['name'].lower()).strip('-')
            output_path = run_dir / f"{i:02d}-{safe_name}.png"

            print(f"\n[{i}/{len(prompts)}] {item['name']}")

            ok = generate_image(
                prompt=item["prompt"],
                output_path=str(output_path),
                model=args.model,
                aspect_ratio=args.aspect_ratio,
                resolution=args.resolution,
                quality=args.quality,
                style=style,
                reference_image=ref_paths[i - 1],
                reference_role=args.reference_role,
                composition_references=composition_ref_list,
                dry_run=args.dry_run,
            )
            if ok:
                success_count += 1
            viewer_items.append({
                "name": item["name"],
                "prompt": item["prompt"],
                "output_path": str(output_path),
            })

        # Persist run metadata so the comparison viewer can reconstruct history
        run_json_path = run_dir / "run.json"
        run_json_path.write_text(json.dumps({
            **run_meta,
            "images": [
                {
                    "name": it["name"],
                    "prompt": it["prompt"],
                    "file": Path(it["output_path"]).name,
                    "ok": Path(it["output_path"]).exists(),
                }
                for it in viewer_items
            ],
        }, indent=2, ensure_ascii=False), encoding="utf-8")

        # Keep a "latest" symlink in the project dir for easy access
        latest_link = project_dir / "latest"
        if latest_link.is_symlink() or latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(run_dir.name)

        prefix = "[DRY RUN] " if args.dry_run else ""
        print(f"\n{prefix}Generated {success_count}/{len(prompts)} images")
        print(f"{prefix}Run dir: {run_dir}")

        # Generate viewers
        viewer_path_str = ""
        if not args.no_viewer:
            from lib.renderers.viewer import generate_viewer, generate_comparison_viewer
            # Per-run viewer inside the run dir
            generate_viewer(
                output_dir=run_dir,
                items=viewer_items,
                title=Path(args.prompt_file).stem.replace("-", " ").replace("_", " ").title(),
                run_meta=run_meta,
            )
            # Project-level comparison viewer (all runs, run switcher + compare mode)
            vp = generate_comparison_viewer(project_dir)
            viewer_path_str = str(vp)
            print(f"{prefix}Viewer: {viewer_path_str}")

        if args.json_output:
            _real_stdout.write(json.dumps({
                "success": success_count == len(prompts),
                "mode": "batch",
                "dry_run": args.dry_run,
                "generated": success_count,
                "total": len(prompts),
                "project_dir": str(project_dir),
                "run_dir": str(run_dir),
                "run_id": run_ts,
                "viewer_path": viewer_path_str,
                "model": args.model,
                "aspect_ratio": args.aspect_ratio,
                "style": style or "none",
                "images": [
                    {
                        "name": it["name"],
                        "output_path": it["output_path"],
                        "ok": Path(it["output_path"]).exists(),
                    }
                    for it in viewer_items
                ],
            }, indent=2) + "\n")

        sys.exit(0 if success_count == len(prompts) else 1)

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()

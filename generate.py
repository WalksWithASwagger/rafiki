#!/usr/bin/env python3
"""
Image Generator using Google Nano Banana (Gemini Image Generation)

Usage:
    python generate.py --prompt "A creative professional..." --output image.png
    python generate.py --prompt-file image-prompts.md --output-dir ./images/
"""

import argparse
import os
import sys
import json
import hashlib
import re
from pathlib import Path
from datetime import datetime

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: google-genai not installed. Run: pip install -r requirements.txt (use a venv).")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow not installed. Run: pip install pillow")
    sys.exit(1)

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
    style: str = None,
    reference_image: str = None,
    reference_role: str = "style",
    composition_references: list[str] | None = None,
    dry_run: bool = False
) -> bool:
    """Generate image using Nano Banana (Gemini).

    Args:
        prompt: Text prompt for image generation
        output_path: Where to save the generated image
        model: Gemini model to use
        aspect_ratio: Image aspect ratio
        resolution: Image resolution (1K, 2K, 4K)
        style: Style preset to apply (kk, hopecode, bcai, or 'none'). None uses default.
        reference_image: Path to reference image for style/composition guidance
        reference_role: "style" = ref informs look only (default). "mockup" = ref is a real
            garment photo to preserve while adding a described print.
        composition_references: Extra images (mockup mode only) — print layout / art-direction refs
            while the primary reference stays the garment photo.
        dry_run: Preview without calling API
    """

    # Auto-detect default style if not specified
    if style is None:
        style = get_default_style()

    # Dry run doesn't need API key
    if dry_run:
        print(f"[DRY RUN] Would generate image:")
        print(f"  Model: {model}")
        print(f"  Aspect ratio: {aspect_ratio}")
        print(f"  Resolution: {resolution}")
        print(f"  Style: {style}")
        print(f"  Reference role: {reference_role}")
        if composition_references:
            print(f"  Composition refs: {len(composition_references)} image(s)")
        print(f"  Output: {output_path}")
        print(f"  Prompt: {prompt[:200]}...")
        return True

    # Check for API key
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set")
        print("Get your key at: https://aistudio.google.com/app/apikey")
        return False

    # Apply style if not 'none'
    full_prompt = prompt
    if style and style != 'none':
        suffix = get_style_suffix(style)
        if suffix:
            full_prompt = f"{prompt}\n\n{suffix}"
        else:
            print(f"Warning: Unknown style '{style}', using prompt without style suffix")

    try:
        client = genai.Client(api_key=api_key)

        # Build config based on model
        image_config = types.ImageConfig(aspect_ratio=aspect_ratio)

        # Pro model supports higher resolutions
        if "pro" in model.lower() and resolution in ["2K", "4K"]:
            image_config = types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=resolution
            )

        config = types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            image_config=image_config
        )

        # Build contents for API call
        contents = []

        # Add reference image if provided
        if reference_image:
            from PIL import Image as PILImage
            try:
                if composition_references and reference_role != "mockup":
                    print("Error: --composition-references only works with --reference-role mockup")
                    return False

                # Load and validate reference image
                ref_img_path = Path(reference_image)
                if not ref_img_path.exists():
                    print(f"Error: Reference image not found: {reference_image}")
                    return False

                ref_img = PILImage.open(reference_image)

                # Add to contents (Gemini expects PIL Image objects)
                contents.append(ref_img)

                comp_imgs: list = []
                if composition_references:
                    for p in composition_references:
                        cp = Path(p)
                        if not cp.exists():
                            print(f"Error: Composition reference not found: {p}")
                            return False
                        comp_imgs.append(PILImage.open(p))
                        contents.append(comp_imgs[-1])

                if reference_role == "mockup":
                    comp_note = ""
                    if comp_imgs:
                        comp_note = (
                            f"\n\nAfter the shirt photograph, the next {len(comp_imgs)} image(s) are REFERENCE ART "
                            "for the PRINT ONLY (layout, ornament density, drippy typography, cosmic/vortex motifs, "
                            "bone frames, roses, lightning, circuit accents). Synthesize ONE new original "
                            "center-chest graphic that merges the strongest qualities of those references. "
                            "All visible words on the new print must read as Vancouver AI / Vancouver AI Community "
                            "per the text brief below — do not copy unrelated band or brand names from the reference art."
                        )
                    contents.append(
                        "IMPORTANT: The FIRST image is a photograph of a REAL dyed long-sleeve shirt "
                        "(flat-lay or similar). Preserve the garment, the exact tie-dye pattern, fabric texture, "
                        "folds, collar, seams, cuffs, visible tags, sleeves, and the background (rug/floor) as "
                        "faithfully as the model allows. Do not replace the whole photo with a flat illustration.\n\n"
                        "Add ONE new original center-chest screen-print graphic as described below. The print must "
                        "look like vintage hand-pulled screen ink on cotton: thick black outlines, drippy warped "
                        "custom lettering, halftone/stipple grain, slight imperfect registration — hand-drawn 1970s "
                        "lot-tee / rock-poster energy. Avoid corporate vector, stock illustration, or clip-art polish. "
                        "The ink should subtly follow fabric contours over folds.\n\n"
                        "Any words in the new print must match the brief (Vancouver AI / Vancouver AI Community only). "
                        "Do not add other band or brand names."
                        f"{comp_note}\n\n"
                        f"{full_prompt}"
                    )
                else:
                    contents.append(
                        f"IMPORTANT: Use the provided image ONLY as a visual style reference "
                        f"(textures, grain, collage technique, color palette, layout energy). "
                        f"Do NOT copy any text, words, band names, slogans, or written content from the reference image. "
                        f"The actual text and content for the image MUST come from the prompt below.\n\n"
                        f"{full_prompt}"
                    )

                print(f"  Reference image: {reference_image}")
                if comp_imgs:
                    print(f"  Composition references: {len(comp_imgs)} image(s)")
            except Exception as e:
                print(f"Error loading reference image: {e}")
                return False
        else:
            contents.append(full_prompt)

        print(f"Generating image with {model}...")
        print(f"  Aspect ratio: {aspect_ratio}")
        print(f"  Prompt: {prompt[:100]}...")

        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=config
        )

        # Extract and save image
        for part in response.parts:
            if part.inline_data is not None:
                image = part.as_image()

                # Ensure output directory exists
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)

                image.save(output_path)
                print(f"Image saved to: {output_path}")

                # Log generation
                log_generation(prompt, model, output_path, aspect_ratio)

                return True

        print("Warning: No image in response")
        if response.text:
            print(f"Response text: {response.text}")
        return False

    except Exception as e:
        print(f"Error generating image: {e}")
        return False


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
        choices=["gemini-2.5-flash-image", "gemini-3-pro-image-preview"],
        help="Model to use (default: gemini-2.5-flash-image)"
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
        help="Show what would be generated without calling API"
    )
    parser.add_argument(
        "--usage",
        action="store_true",
        help="Show usage statistics"
    )

    args = parser.parse_args()

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
            style=style,
            reference_image=args.reference_image,
            reference_role=args.reference_role,
            composition_references=composition_ref_list,
            dry_run=args.dry_run
        )
        sys.exit(0 if success else 1)

    # Batch from file
    if args.prompt_file:
        prompts = parse_image_prompts_md(args.prompt_file)
        print(f"Found {len(prompts)} prompts in {args.prompt_file}")

        output_dir = Path(args.output_dir or Path(args.prompt_file).parent / "images")
        output_dir.mkdir(parents=True, exist_ok=True)

        ref_paths = resolve_reference_list(len(prompts))

        success_count = 0
        for i, item in enumerate(prompts, 1):
            safe_name = re.sub(r'[^a-z0-9]+', '-', item['name'].lower()).strip('-')
            output_path = output_dir / f"{i:02d}-{safe_name}.png"

            print(f"\n[{i}/{len(prompts)}] {item['name']}")

            if generate_image(
                prompt=item['prompt'],
                output_path=str(output_path),
                model=args.model,
                aspect_ratio=args.aspect_ratio,
                resolution=args.resolution,
                style=style,
                reference_image=ref_paths[i - 1],
                reference_role=args.reference_role,
                composition_references=composition_ref_list,
                dry_run=args.dry_run
            ):
                success_count += 1

        print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Generated {success_count}/{len(prompts)} images")
        sys.exit(0 if success_count == len(prompts) else 1)

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()

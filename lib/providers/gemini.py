from __future__ import annotations

import os
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

try:
    from PIL import Image as PILImage
except ImportError:
    PILImage = None


class GeminiProvider:
    def generate(
        self,
        prompt: str,
        output_path: str,
        model: str,
        aspect_ratio: str = "16:9",
        resolution: str = "1K",
        quality: str = "high",          # unused by Gemini, accepted for interface parity
        reference_image: str | None = None,
        reference_role: str = "style",
        composition_references: list[str] | None = None,
    ) -> bool:
        if genai is None:
            print("Error: google-genai not installed. Run: pip install -r requirements.txt")
            return False

        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("Error: GOOGLE_API_KEY not set. Get one at https://aistudio.google.com/app/apikey")
            return False

        try:
            client = genai.Client(api_key=api_key)

            image_config = types.ImageConfig(aspect_ratio=aspect_ratio)
            if "pro" in model.lower() and resolution in ("2K", "4K"):
                image_config = types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=resolution,
                )

            config = types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=image_config,
            )

            contents = self._build_contents(
                prompt=prompt,
                reference_image=reference_image,
                reference_role=reference_role,
                composition_references=composition_references,
            )
            if contents is None:
                return False

            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )

            for part in response.parts:
                if part.inline_data is not None:
                    image = part.as_image()
                    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                    image.save(output_path)
                    print(f"Image saved to: {output_path}")
                    return True

            print("Warning: No image in response")
            if response.text:
                print(f"Response text: {response.text}")
            return False

        except Exception as e:
            print(f"Error generating image: {e}")
            return False

    def _build_contents(
        self,
        prompt: str,
        reference_image: str | None,
        reference_role: str,
        composition_references: list[str] | None,
    ) -> list | None:
        if not reference_image:
            return [prompt]

        if PILImage is None:
            print("Error: Pillow not installed — needed for reference images.")
            return None

        if composition_references and reference_role != "mockup":
            print("Error: --composition-references only works with --reference-role mockup")
            return None

        ref_path = Path(reference_image)
        if not ref_path.exists():
            print(f"Error: Reference image not found: {reference_image}")
            return None

        contents = [PILImage.open(reference_image)]

        comp_imgs: list = []
        if composition_references:
            for p in composition_references:
                cp = Path(p)
                if not cp.exists():
                    print(f"Error: Composition reference not found: {p}")
                    return None
                comp_imgs.append(PILImage.open(p))
                contents.append(comp_imgs[-1])

        print(f"  Reference image: {reference_image}")
        if comp_imgs:
            print(f"  Composition references: {len(comp_imgs)} image(s)")

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
                f"{prompt}"
            )
        else:
            contents.append(
                "IMPORTANT: Use the provided image ONLY as a visual style reference "
                "(textures, grain, collage technique, color palette, layout energy). "
                "Do NOT copy any text, words, band names, slogans, or written content from the reference image. "
                "The actual text and content for the image MUST come from the prompt below.\n\n"
                f"{prompt}"
            )

        return contents

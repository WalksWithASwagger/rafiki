from __future__ import annotations

import base64
import os
from pathlib import Path
from contextlib import ExitStack

# Maps Rafiki aspect-ratio strings → OpenAI size strings.
# OpenAI gpt-image-* supports: 1024x1024, 1536x1024, 1024x1536, and "auto".
_SIZE_MAP: dict[str, str] = {
    "1:1": "1024x1024",
    "16:9": "1536x1024",
    "9:16": "1024x1536",
    "linkedin": "1536x1024",
    "twitter": "1536x1024",
    "instagram": "1024x1024",
    "square": "1024x1024",
    "story": "1024x1536",
}

# Maps Rafiki resolution strings → OpenAI quality strings.
# Lets callers use --resolution as a rough quality proxy when --quality is not set.
_RESOLUTION_TO_QUALITY: dict[str, str] = {
    "1K": "low",
    "2K": "medium",
    "4K": "high",
}


class OpenAIProvider:
    def generate(
        self,
        prompt: str,
        output_path: str,
        model: str = "gpt-image-1",
        aspect_ratio: str = "16:9",
        resolution: str = "1K",
        quality: str = "high",
        reference_image: str | None = None,
        reference_images: list[str] | None = None,
        reference_role: str = "style",         # unused for now
        composition_references: list[str] | None = None,  # unused for now
    ) -> bool:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY not set. Get one at https://platform.openai.com/api-keys")
            return False

        size = _SIZE_MAP.get(aspect_ratio, "1024x1024")

        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)

            # DALL-E 2/3 use response_format + different quality/size options
            if model.startswith("dall-e"):
                return self._generate_dalle(client, prompt, output_path, model, size, quality)

            # Reference image via images.edit() (gpt-image-* only)
            ref_paths = [Path(ref) for ref in [reference_image, *(reference_images or [])] if ref]
            if ref_paths:
                for ref_path in ref_paths:
                    if not ref_path.exists():
                        print(f"Error: Reference image not found: {ref_path}")
                        return False
                if reference_role == "style":
                    print(
                        "Note: OpenAI edit() uses the reference as the base canvas. "
                        "For pure style transfer, consider Gemini with --reference-role style."
                    )
                elif reference_role == "brand":
                    prompt = (
                        "Use the attached images as high-fidelity brand references. "
                        "When the prompt requests official marks, preserve their letterforms, "
                        "colors, proportions, and lockup as faithfully as possible; do not invent "
                        "alternate logos or extra typography.\n\n"
                        f"{prompt}"
                    )
                print(f"  Reference images: {len(ref_paths)} (via images.edit)")
                return self._generate_edit(client, prompt, output_path, model, size, quality, ref_paths)

            # Text-to-image: images.generate()
            response = client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=1,
            )

            return self._save_response(response.data[0], output_path)

        except Exception as e:
            print(f"Error generating image: {e}")
            return False

    def _generate_edit(
        self,
        client,
        prompt: str,
        output_path: str,
        model: str,
        size: str,
        quality: str,
        ref_paths: list[Path],
    ) -> bool:
        try:
            with ExitStack() as stack:
                img_files = [stack.enter_context(open(ref_path, "rb")) for ref_path in ref_paths]
                image_arg = img_files[0] if len(img_files) == 1 else img_files
                edit_kwargs = {
                    "model": model,
                    "image": image_arg,
                    "prompt": prompt,
                    "size": size,
                    "n": 1,
                }
                if model == "gpt-image-1":
                    edit_kwargs["input_fidelity"] = "high"
                response = client.images.edit(**edit_kwargs)
            return self._save_response(response.data[0], output_path)
        except Exception as e:
            print(f"Error in images.edit: {e}")
            return False

    def _save_response(self, img_data, output_path: str) -> bool:
        if img_data.b64_json:
            image_bytes = base64.b64decode(img_data.b64_json)
        elif img_data.url:
            import urllib.request
            with urllib.request.urlopen(img_data.url) as r:
                image_bytes = r.read()
        else:
            print("Error: No image data in response")
            return False
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(image_bytes)
        print(f"Image saved to: {output_path}")
        return True

    def _generate_dalle(
        self,
        client,
        prompt: str,
        output_path: str,
        model: str,
        size: str,
        quality: str,
    ) -> bool:
        # DALL-E 3 size options differ; clamp to supported values
        dalle3_sizes = {"1024x1024", "1792x1024", "1024x1792"}
        dalle2_sizes = {"256x256", "512x512", "1024x1024"}

        if model == "dall-e-3":
            # Map our 1536x1024 → 1792x1024 (closest DALL-E 3 landscape)
            if size == "1536x1024":
                size = "1792x1024"
            elif size == "1024x1536":
                size = "1024x1792"
            if size not in dalle3_sizes:
                size = "1024x1024"
            # DALL-E 3 quality: standard | hd
            oai_quality = "hd" if quality in ("high", "hd") else "standard"
            response = client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=oai_quality,
                response_format="b64_json",
                n=1,
            )
        else:
            # DALL-E 2
            if size not in dalle2_sizes:
                size = "1024x1024"
            response = client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                response_format="b64_json",
                n=1,
            )

        b64 = response.data[0].b64_json
        if not b64:
            print("Error: No image data in DALL-E response")
            return False

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(base64.b64decode(b64))
        print(f"Image saved to: {output_path}")
        return True

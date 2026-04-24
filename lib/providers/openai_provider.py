from __future__ import annotations

import base64
import os
from pathlib import Path

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
        reference_role: str = "style",         # unused for now
        composition_references: list[str] | None = None,  # unused for now
    ) -> bool:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY not set. Get one at https://platform.openai.com/api-keys")
            return False

        if reference_image:
            print(
                "Warning: reference images are not yet supported for OpenAI models. "
                "Generating text-only."
            )

        size = _SIZE_MAP.get(aspect_ratio, "1024x1024")

        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)

            # DALL-E 2/3 use response_format + different quality/size options
            if model.startswith("dall-e"):
                return self._generate_dalle(client, prompt, output_path, model, size, quality)

            # gpt-image-* models: use output_format, quality low/medium/high
            response = client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=1,
            )

            img_data = response.data[0]

            # gpt-image-* always returns b64_json
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

        except Exception as e:
            print(f"Error generating image: {e}")
            return False

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

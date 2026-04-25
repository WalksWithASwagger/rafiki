#!/usr/bin/env python3
"""
Streamlit batch UI for OpenAI gpt-image-1: one prompt at a time, show images as they land.
Set OPENAI_API_KEY. Run: streamlit run diagram_gen_ui.py
"""
from __future__ import annotations

import base64
import json
import io
import os
import zipfile
from pathlib import Path

import streamlit as st
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

# --- API -----------------------------------------------------------------

MODEL = "gpt-image-1"


@retry(
    wait=wait_random_exponential(min=1, max=60),
    stop=stop_after_attempt(6),
)
def generate_image(
    client: OpenAI, prompt: str, *, size: str, quality: str, moderation: str
):
    return client.images.generate(
        model=MODEL,
        prompt=prompt,
        size=size,
        quality=quality,
        moderation=moderation,
    )


def load_prompts_from_bytes(raw: bytes, name: str) -> list[str]:
    text = raw.decode("utf-8", errors="replace")
    if name.lower().endswith(".json"):
        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError("JSON prompts file must be a list of strings")
        return [str(p).strip() for p in data if str(p).strip()]
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def main() -> None:
    st.set_page_config(page_title="Diagram batch (gpt-image-1)", layout="wide")
    st.title("Batch diagram images — `gpt-image-1`")
    st.caption("Sequential requests · images appear as they return · set `OPENAI_API_KEY` in your environment")

    if not os.environ.get("OPENAI_API_KEY"):
        st.error("Missing `OPENAI_API_KEY` in the environment.")
        st.stop()

    client = OpenAI()

    with st.sidebar:
        st.subheader("Inputs")
        prompts_file = st.file_uploader("Prompts file (.txt or .json list)", type=["txt", "json"])
        style_file = st.file_uploader("Optional style guide (.txt) — prepended to each prompt", type=["txt"])

        size = st.selectbox("Size", ["1024x1024", "1024x1536", "1536x1024", "auto"], index=0)
        quality = st.selectbox("Quality", ["auto", "low", "medium", "high"], index=0)
        moderation = st.selectbox("Moderation", ["auto", "low"], index=0, help="`low` = less strict filtering (OpenAI doc)")
        out_dir = st.text_input("Output directory", value="out")
        do_zip = st.checkbox("Offer ZIP of outputs when done", value=True)
        go = st.button("Generate", type="primary")

    style_prefix = ""
    if style_file is not None:
        style_prefix = style_file.getvalue().decode("utf-8", errors="replace").strip()

    if not go:
        st.info("Upload a prompts file, set options, then **Generate**.")
        return

    if prompts_file is None:
        st.error("Please upload a prompts file.")
        st.stop()

    lines = load_prompts_from_bytes(prompts_file.getvalue(), prompts_file.name)
    n = len(lines)
    if n == 0:
        st.error("No prompts found.")
        st.stop()

    out_path = Path(out_dir).expanduser().resolve()
    out_path.mkdir(parents=True, exist_ok=True)

    progress = st.progress(0.0, text="Starting…")
    gallery = st.empty()
    thumbs: list[Path] = []

    for i, line in enumerate(lines, start=1):
        full = f"{style_prefix}\n\n{line}".strip() if style_prefix else line
        with st.spinner(f"[{i}/{n}] Generating…"):
            try:
                res = generate_image(
                    client,
                    full,
                    size=size,
                    quality=quality,
                    moderation=moderation,
                )
            except Exception as e:
                st.error(f"Failed on line {i}: {e!s}")
                st.code(line[:2000] + ("…" if len(line) > 2000 else ""))
                st.stop()

        b64 = res.data[0].b64_json
        if not b64:
            st.error(f"No b64 payload at line {i}")
            st.stop()
        data = base64.b64decode(b64)
        fname = out_path / f"diagram_{i:02d}.png"
        fname.write_bytes(data)
        thumbs.append(fname)

        progress.progress(i / n, text=f"Done {i}/{n}")
        with gallery.container():
            st.subheader("Generated so far")
            for p in thumbs:
                st.image(str(p), caption=p.name, use_container_width=True)

    progress.progress(1.0, text="Complete")
    st.success(f"Wrote {n} file(s) to `{out_path}`")

    if do_zip and thumbs:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in thumbs:
                zf.write(p, arcname=p.name)
        buf.seek(0)
        st.download_button(
            "Download ZIP",
            data=buf,
            file_name="diagrams.zip",
            mime="application/zip",
        )


if __name__ == "__main__":
    main()

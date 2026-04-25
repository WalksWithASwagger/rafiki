# Batch image generation: `gpt-image-1` + Streamlit UI

**Reference:** OpenAI Image API; model **`gpt-image-1`**. This doc preserves API notes, UI requirements, and implementation hints for a small local tool.

## API essentials

- **Endpoint:** `client.images.generate(model="gpt-image-1", prompt=..., **opts)`
- **Response:** `result.data[0].b64_json` → `base64.b64decode` → write PNG/WEBP.
- **Organization verification** may be required for `gpt-image-1` (developer console).
- **Size:** e.g. `1024x1024`, `1024x1536`, `1536x1024`, or `auto`.
- **Quality:** `low` | `medium` | `high` | `auto` (affects cost/latency; larger + higher = more image tokens).
- **Format / compression:** `png` (default), `jpeg`, `webp`; `output_compression` for jpeg/webp.
- **Background:** `transparent` (png/webp, works best with medium/high quality).
- **Moderation:** `moderation="auto"` (default) or `low` (less strict).
- **Limitations:** Complex prompts can take up to ~2 minutes; text-in-image can still drift; cross-image consistency is not guaranteed.

## Retry

Use **exponential backoff with jitter** (e.g. `tenacity`: `wait_random_exponential`, `stop_after_attempt(6)`) for rate limits. **Sequential** requests reduce parallel throttling.

## Input files

| File | Role |
|------|------|
| `gpt-image-1-prompts-one-per-line.txt` | One full prompt per line (44 lines; `create this diagram "…"`). |
| `hopecode-style-guide.txt` | Optional prefix concatenated: `{style}\n\n{line}`. |

## UI spec (no CLI required for daily use)

Single Streamlit file `diagram_gen_ui.py`:

1. **Sidebar:** Upload prompts file (.txt or .json list); optional style guide upload; select **size** and **quality**; output directory text field; **Generate** button.
2. **Main:** `st.progress`; for each prompt in order, call API with retry → decode → save `diagram_NN.png` → **`st.image` immediately** so images appear as they return.
3. **End:** success message + **zip** of output folder for download.
4. **Env:** `OPENAI_API_KEY` required.

## Python deps

```
streamlit openai tenacity pillow
```

## Run

```bash
cd tools/gpt-image-batch-ui
export OPENAI_API_KEY=sk-...
pip install -r requirements.txt
streamlit run diagram_gen_ui.py
```

## Implementation location

- App: `rafiki/tools/gpt-image-batch-ui/` (this repo)
- Prompts + HOPECODE text: `rafiki/prompts/kk-kb/gni-journalism-sovereignty/`

*Spec preserved 2026-04-26. Paths updated 2026-04-25 for Rafiki `prompts/kk-kb/` archive.*

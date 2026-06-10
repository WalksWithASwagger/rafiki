# gpt-image-1 batch UI (Streamlit)

Minimal web UI: upload prompts (one per line or JSON list), optional HOPECODE-style prefix file, pick size/quality, run **sequential** `gpt-image-1` calls, show each image as it saves to disk, optionally zip outputs.

**Location:** this folder lives in the **Rafiki** repository (`rafiki/tools/gpt-image-batch-ui/`). The `kk-ai-ecosystem` knowledge base keeps a short pointer; run the app from here.

## Setup

```bash
cd tools/gpt-image-batch-ui   # from Rafiki repo root
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
```

## Run

```bash
streamlit run diagram_gen_ui.py
```

## Prompts + style

Point the UI at a local prompt file (one prompt per line) and an optional style-guide
text file. Generated prompt packs are kept in a private knowledge base, not in the public
tool repo — supply your own local paths, e.g.:

- `<your-prompts>/gpt-image-1-prompts-one-per-line.txt` (one prompt per line)
- `<your-prompts>/style-guide.txt` (optional style preface)

## Notes

- Requires **OpenAI org verification** for `gpt-image-1` if your account is not yet enabled.
- Long or dense prompts can take up to a couple of minutes each.
- On failure, the app stops and shows the failing line; fix prompt or moderation and re-run (skip already-generated files in a follow-up if you add that feature).

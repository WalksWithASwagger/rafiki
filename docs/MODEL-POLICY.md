# Model Policy

Rafiki's v1 default image model is `gemini-2.5-flash-image`.

That default is intentionally local-first and iteration-first: it works well
for fast prompt development, supports the existing Gemini path in the CLI,
portal, and MCP tools, and keeps setup simple for users who only have a Google
API key.

## Defaults

- CLI: `generate.py` and `index.js` default to `gemini-2.5-flash-image`.
- Portal: Prompt Studio uses `gemini-2.5-flash-image` when the request does not
  include a model.
- MCP: `rafiki_generate` and `rafiki_batch` default to
  `gemini-2.5-flash-image`.
- Prompt files may override the default with `**Model:** ...` per prompt.

## When To Choose Gemini

Use Gemini when you want fast local iteration, style exploration, reference
image workflows, or higher-resolution Gemini Pro outputs via
`gemini-3-pro-image-preview`.

Useful aliases:

- `flash`, `nano`, `gemini`: `gemini-2.5-flash-image`
- `pro`: `gemini-3-pro-image-preview`

## When To Choose OpenAI

Use OpenAI when your project depends on OpenAI-specific behavior, when a prompt
set was authored and approved against OpenAI outputs, or when you are using the
separate `gpt-image-1` Streamlit workflow documented in the operator guides.

Useful aliases:

- `gpt`, `gpt2`: `gpt-image-2`
- `gpt1`: `gpt-image-1`
- `dalle3`: `dall-e-3`

Always pass OpenAI models explicitly with `--model`; do not rely on old
roadmap examples as the default policy.

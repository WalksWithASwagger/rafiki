# The New God Flow - Book Cover

Cover concepts for **THE NEW GOD FLOW** - *A walk through nineteen albums and a
tradition older than the form* - by Michael Caswell.

This prompt kit uses the `new-god-flow` style preset: industrial minimalist
luxury, matte black or matte white grounds, one iridescent foil accent,
reverent anatomical imagery, and restrained classical serif typography.

## Prompts

`image-prompts.md` contains 10 portrait book-cover concepts.

## Running Both Models

Run the same file once per model into separate output directories so the two
passes compare cleanly:

```bash
python generate.py -f prompts/the-new-god-flow/image-prompts.md \
  --style new-god-flow -m pro -a 2:3 \
  -d output/the-new-god-flow/pro

python generate.py -f prompts/the-new-god-flow/image-prompts.md \
  --style new-god-flow -m gpt2 -q high \
  -d output/the-new-god-flow/gpt2
```

Then review side by side:

```bash
python generate.py library --open
```

## Requirements

These calls need provider keys in `.env` at the repo root:

- `GOOGLE_API_KEY` for `pro`
- `OPENAI_API_KEY` for `gpt2`

Verify setup first with `npm run doctor`.

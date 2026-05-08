# Social-Post Expansion

After Rafiki generates a batch, `social-expand` runs a second LLM pass
to produce platform-specific social copy per image (LinkedIn, X,
Instagram). Output lives in `<latest-run>/social-posts.json` for
downstream tools. Presentation-viewer support for platform-specific tabs is
available when a viewer item's image directory contains `social-posts.json`.

## Constraints per platform

- **linkedin**: 150–250 words, thought-leadership tone, 3–5 hashtags, hook opener
- **x**: under 280 chars, single thought, 2–3 hashtags
- **instagram**: 3–5 sentences, evocative tone, 8–10 hashtags

## Source preference

1. `<latest-run>/social-posts.md` (PR #19)
2. `prompts/.../<project>-viewer-data.json` (PR #36)
3. `<latest-run>/run.json` (always present)

## Required env

`OPENAI_API_KEY` — the same key already used for image generation.

## Cost

Default model is `gpt-4o-mini` (~$0.15 per 1M input tokens). Each item
runs one chat completion of a few hundred tokens, so a typical batch of
40 images costs roughly **$0.04** to expand across all three platforms.

## CLI

```bash
python generate.py social-expand rap-cert
python generate.py social-expand rap-cert --platform linkedin x
python generate.py social-expand rap-cert --model gpt-4o
python generate.py social-expand rap-cert --dry-run
```

## Output format

```json
{
  "01-luma-event-banner": {
    "title": "Luma Event Banner",
    "caption": "Wide atmospheric banner: a misty BC old-growth forest...",
    "platforms": {
      "linkedin": "...",
      "x": "...",
      "instagram": "..."
    }
  }
}
```

The reusable presentation viewer reads this file directly when its
`image_dirs` entry points at the run directory. Matching is by item slug, and
the lightbox renders LinkedIn, X, and Instagram as platform tabs while keeping
any legacy single `social` string as the `Original` tab.

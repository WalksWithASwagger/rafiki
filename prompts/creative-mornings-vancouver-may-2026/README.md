# Creative Mornings Vancouver — May 2026 — “Punk Rock AI”

**Purpose:** Editable, rerunnable **image and motion** prompt set for the talk. Canonical copy for improvement passes (Gemini via Rafiki, DALL·E, Midjourney, Runway, Kling—tooling varies by file).

| File | Contents |
|------|-----------|
| [image-gen-prompts.md](./image-gen-prompts.md) | Slide deck: Midjourney + DALL·E blocks per slide; punk zine / xerox palette; text-slide notes |
| [video-gen-concepts.md](./video-gen-concepts.md) | Runway / Kling shot lists, intro reel beats, talk-loop prompts |
| [punk-zine-template-brief.md](./punk-zine-template-brief.md) | Release Day **Sniffin’ Glue 2026** / broadsheet creative brief (layout + distribution) |

**Aesthetic (from deck):** punk zine, high-contrast B/W, cut-and-paste, xerox grain — not corporate polish.

**Rafiki (Gemini) reruns:** Strip `--ar` / `--style raw` (Midjourney-only); add `--style hopecode` or `kk` if you want a packed style. Batch: `npx rafiki ./prompts/creative-mornings-vancouver-may-2026/image-gen-prompts.md --output-dir ./out-cm-2026/` (may need to split blockquotes to one prompt per section depending on `image-prompts.md` parser).

## Run command

```bash
python generate.py -f prompts/creative-mornings-vancouver-may-2026/image-gen-prompts.md \
  -d output/cm-vancouver-may-2026 \
  --style zine -m gpt-image-2 -w 2
```

Swap `--style zine` for `hopecode` or `kk` to repaint the deck in another visual system; the underlying prompts already carry the punk-zine direction in-line.

**Source in kk-ai-ecosystem (sibling):** `projects/02-bc-ai-ecosystem-nonprofit/speaking-engagements/2026/creative-mornings-vancouver-may-2026/` — the KB folder may keep a **stub** that points here.

*Imported: 2026-04-25*

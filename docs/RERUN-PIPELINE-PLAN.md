# Image prompt rerun pipeline (Rafiki)

**Goal:** When you’re ready, batch **rereads** and **regenerations** of every prompt set we’ve collected — without losing originals — using **Rafiki** (`npx rafiki`, Gemini image models) and, where noted, **OpenAI `gpt-image-1`** + [`tools/gpt-image-batch-ui/`](../tools/gpt-image-batch-ui/README.md).

**Principle:** *Edit in Rafiki; keep versions (`image-prompts.md` → `image-prompts-v2.md` or a dated block) instead of silent overwrite.*

---

## What lives where (mental map)

| Location | Role |
|----------|------|
| [`prompts/kk-kb/`](../prompts/kk-kb/README.md) | Diagrams, HOPECODE / GNI / zine / WAIFF / MAC / Wikipedia Five Futures, `hopecode-style-guide.txt`, `gpt-image-1` line list |
| [`prompts/creative-mornings-vancouver-may-2026/`](../prompts/creative-mornings-vancouver-may-2026/README.md) | CM **Punk Rock AI** deck, video shot list, Release Day zine brief |
| [`prompts/bcai/`](../prompts/bcai/README.md) | BC+AI + HOPECODE “dark aurora” compendia, ecosystem diagrams |
| [`prompts/kb-ecosystem-mirror/`](../prompts/kb-ecosystem-mirror/README.md) | **50×** files mirrored from `kk-b` `articles/` + `projects/` (thought leadership, marketing hub, cert, apparel, ed-ai, events) |

---

## Suggested phases (when you have GPU time and API budget)

1. **Smoke — Rafiki on one file**  
   `npx rafiki /path/to/one-image-prompts.md --style hopecode --dry-run`  
   Fix path/style until one section renders as expected.

2. **Strategic / editorial art — `articles/kris-krug-thought-leadership/`**  
   Usually HOPECODE / `kk` / `bcai` depending on table in each `seo.md` / `frontmatter`. Run article-by-article; curate 1–2 hero images per post.

3. **Upgrade marketing hub — 8 `upgrade-marketing-hub/**/image-prompts.md`**  
   Often diagram-forward; match [`kk-kb` style guides](IMAGE-PROMPT-ARCHIVE.md) or Blue Engine notes in `prompts/kk-kb/gni-journalism-sovereignty/`.

4. **Event / deck — WAIFF, CM, BC Festival branding**  
   WAIFF + CM: zine BWR / Gemini — see per-folder README. Festival: `bc-ai-festival-week/branding/`.

5. **Cert + infographics — Responsible AI Pro**  
   May split between Gemini (illustration) and `gpt-image-1` (precise text-in-image) per slide.

6. **Apparel + Ed AI meetup**  
   Apparel: reference images + `kk` / mockup mode (see main Rafiki README). Ed AI: small batches, four style variants are already in filenames.

7. **Wikipedia Five Futures, MAC femme (already in `kk-b`)**  
   Rerun for print / social sizes; mind tool syntax (some Midjourney `/imagine` lines need adapting for Gemini).

---

## Command cheatsheet

```bash
cd /path/to/rafiki
npx rafiki ./prompts/kb-ecosystem-mirror/articles/kris-krug-thought-leadership/01-build-tools-next-job/image-prompts.md \
  --style hopecode --output-dir ./outputs/tl-01/

# Higher fidelity final:
npx rafiki ./prompts/kk-kb/hopecode-creative-big-ideas-prompts.md \
  --model gemini-3-pro-image-preview --resolution 2K --output-dir ./out/
```

**OpenAI batch (GNI / diagram lines):** see [`tools/gpt-image-batch-ui/README.md`](../tools/gpt-image-batch-ui/README.md) and `prompts/kk-kb/gni-journalism-sovereignty/hopecode-style-guide.txt` as prefix.

---

## Housekeeping

- **Refresh the KB mirror** after you add new `image-prompts.md` files in `kk-b`: run the sync script (or re-copy) so Rafiki stays the single “prompt warehouse.”
- **Changelog** in commit messages: `chore(rafiki): refresh kb-ecosystem-mirror from kk-b @ <sha>`

*Last updated: 2026-04-26*

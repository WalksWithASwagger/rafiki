# KB Mirror Policy

## Canonical home

**Rafiki** (`prompts/kk-kb/`) is the authoritative home for KK's image and diagram prompt files. These assets were migrated from the `kk-ai-ecosystem` knowledge base on 2026-04-25.

GitHub: <https://github.com/WalksWithASwagger/rafiki>

## The stale mirror situation

`kk-ai-ecosystem/content/reference/` contains copies of these files from before the 2026-04-25 migration. Those copies are now stale mirrors — they may have diverged or fallen behind the Rafiki versions.

### Files in `kk-ai-ecosystem/content/reference/` that are stale mirrors of Rafiki `prompts/kk-kb/`

| Stale mirror path (kk-ai-ecosystem) | Canonical path (Rafiki) |
|--------------------------------------|-------------------------|
| `content/reference/ai-diagram-pipeline-teaching-kit.md` | [`prompts/kk-kb/ai-diagram-pipeline-teaching-kit.md`](https://github.com/WalksWithASwagger/rafiki/blob/main/prompts/kk-kb/ai-diagram-pipeline-teaching-kit.md) |
| `content/reference/custom-gpt-diagram-gardener-and-weaver.md` | [`prompts/kk-kb/custom-gpt-diagram-gardener-and-weaver.md`](https://github.com/WalksWithASwagger/rafiki/blob/main/prompts/kk-kb/custom-gpt-diagram-gardener-and-weaver.md) |
| `content/reference/gni-cosmic-diagram-style-guide.md` | [`prompts/kk-kb/gni-cosmic-diagram-style-guide.md`](https://github.com/WalksWithASwagger/rafiki/blob/main/prompts/kk-kb/gni-cosmic-diagram-style-guide.md) |
| `content/reference/gni-journalism-sovereignty/` | [`prompts/kk-kb/gni-journalism-sovereignty/`](https://github.com/WalksWithASwagger/rafiki/blob/main/prompts/kk-kb/gni-journalism-sovereignty/) |
| `content/reference/hopecode-creative-big-ideas-prompts.md` | [`prompts/kk-kb/hopecode-creative-big-ideas-prompts.md`](https://github.com/WalksWithASwagger/rafiki/blob/main/prompts/kk-kb/hopecode-creative-big-ideas-prompts.md) |
| `content/reference/indigenomics-diagram-style-guide.md` | [`prompts/kk-kb/indigenomics-diagram-style-guide.md`](https://github.com/WalksWithASwagger/rafiki/blob/main/prompts/kk-kb/indigenomics-diagram-style-guide.md) |
| `content/reference/README-diagram-visual-resources.md` | [`prompts/kk-kb/README-diagram-visual-resources.md`](https://github.com/WalksWithASwagger/rafiki/blob/main/prompts/kk-kb/README-diagram-visual-resources.md) |
| `content/reference/vanai-data-storytelling-hackathon-newsletter-blurb.md` | [`prompts/kk-kb/vanai-data-storytelling-hackathon-newsletter-blurb.md`](https://github.com/WalksWithASwagger/rafiki/blob/main/prompts/kk-kb/vanai-data-storytelling-hackathon-newsletter-blurb.md) |
| `content/reference/websummit-vancouver-kk-zine-image-prompts.md` | [`prompts/kk-kb/websummit-vancouver-kk-zine-image-prompts.md`](https://github.com/WalksWithASwagger/rafiki/blob/main/prompts/kk-kb/websummit-vancouver-kk-zine-image-prompts.md) |
| `content/reference/wikipedia-five-futures-image-prompts-archive.md` | [`prompts/kk-kb/wikipedia-five-futures-image-prompts-archive.md`](https://github.com/WalksWithASwagger/rafiki/blob/main/prompts/kk-kb/wikipedia-five-futures-image-prompts-archive.md) |

## Rule: don't edit the KB copies

If you need to update any of these files, edit the Rafiki version and then update the submodule reference in `kk-ai-ecosystem`. Do not edit the stale mirror directly — changes made there will be lost or create a divergence.

## Pending action in `kk-ai-ecosystem` repo

Each stale mirror listed above should become a one-line stub file pointing to Rafiki. Replace the full content with something like:

```markdown
> **Moved.** This file now lives in [Rafiki](https://github.com/WalksWithASwagger/rafiki/blob/main/prompts/kk-kb/<filename>). Do not edit here.
```

Files requiring stub replacement (10 files + 1 directory) in `kk-ai-ecosystem/content/reference/`:

1. `ai-diagram-pipeline-teaching-kit.md`
2. `custom-gpt-diagram-gardener-and-weaver.md`
3. `gni-cosmic-diagram-style-guide.md`
4. `gni-journalism-sovereignty/` — replace directory contents with a `README.md` stub
5. `hopecode-creative-big-ideas-prompts.md`
6. `indigenomics-diagram-style-guide.md`
7. `README-diagram-visual-resources.md`
8. `vanai-data-storytelling-hackathon-newsletter-blurb.md`
9. `websummit-vancouver-kk-zine-image-prompts.md`
10. `wikipedia-five-futures-image-prompts-archive.md`

This stub replacement work happens in the `kk-ai-ecosystem` repo, not here.

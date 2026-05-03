# Knowledge base (KK) — image & diagram prompt archive

**Repo:** [Rafiki](https://github.com/WalksWithASwagger/rafiki) — canonical home for these assets **moved from** the `kk-ai-ecosystem` `content/reference/` image-prompt bundle (2026-04-25).

**Start here:** [README-diagram-visual-resources.md](./README-diagram-visual-resources.md) — index of style guides, HOPECODE batches, GNI/Indigenomics, Web Summit zine prompts, WAIFF keynote slide prompts, Wikipedia “Five Futures,” BC+AI MAC femme prompts, and links to the [`gpt-image-1` Streamlit batch UI](../../tools/gpt-image-batch-ui/README.md).

**Sibling in this repo (older / alternate BC+AI set):** [../bcai/](../bcai/) — e.g. `bcai-hopecode-visual-prompts.md`, `ecosystem-diagrams.md`.

*Paths use folder name `kk-kb` (knowledge base).*

## Visual system

**Mixed styles — see individual files** (hopecode, kk, gni, indigenomics, none). This folder is a curated archive across multiple visual systems rather than a single-style library. Each prompt file declares its own `**Style:**` and aspect ratio. Style guides live in [`../../styles/`](../../styles/) (`hopecode.md`, `kk.md`, `gni.md`, `indigenomics.md`).

## Run command

Pick the file you want to generate, then pass its declared style flag:

```bash
python generate.py -f prompts/kk-kb/hopecode-big-ideas-batch.md -d output/hopecode-big-ideas \
  --style hopecode -m gpt-image-2 -w 2
```

Most files in this folder are runnable Rafiki batches. The `gni-journalism-sovereignty/` subfolder ships a `gpt-image-1`-oriented variant (one prompt per line `.txt`); see [its files](./gni-journalism-sovereignty/) and the [Streamlit batch UI](../../tools/gpt-image-batch-ui/README.md).

## Image index

| File | Concept | Style | Notes |
|------|---------|-------|-------|
| [ai-diagram-pipeline-teaching-kit.md](./ai-diagram-pipeline-teaching-kit.md) | Talk: 15-min + 10-min exercise | n/a (teaching kit) | Ethics + Google Photos links |
| [custom-gpt-diagram-gardener-and-weaver.md](./custom-gpt-diagram-gardener-and-weaver.md) | Custom GPT system prompts | n/a (system prompts) | Prompt gardener + image weaver |
| [gni-cosmic-diagram-style-guide.md](./gni-cosmic-diagram-style-guide.md) | GNI lab cosmic / editorial style | gni | Style guide + sample prompts |
| [indigenomics-diagram-style-guide.md](./indigenomics-diagram-style-guide.md) | Indigenomics style + section excerpts | indigenomics | Style guide |
| [hopecode-creative-big-ideas-prompts.md](./hopecode-creative-big-ideas-prompts.md) | HOPECODE creative stack | hopecode | Vancouver diagram batch (narrative + diagram pairs) |
| [hopecode-big-ideas-batch.md](./hopecode-big-ideas-batch.md) | Rafiki batch companion to above | hopecode | 13 prompts, 16:9 default |
| [websummit-vancouver-kk-zine-image-prompts.md](./websummit-vancouver-kk-zine-image-prompts.md) | Web Summit Van zine + resistance | kk | Articles, maps, figures |
| [vanai-data-storytelling-hackathon-newsletter-blurb.md](./vanai-data-storytelling-hackathon-newsletter-blurb.md) | Newsletter / article insert | n/a (copy, not images) | Not image prompts |
| [femme-prompts-mac-image-repository.md](./femme-prompts-mac-image-repository.md) | BC+AI MAC femme / body-compute | mixed (kk / hopecode) | Subgroup asset |
| [waiff-brazil-2026-keynote-image-prompts.md](./waiff-brazil-2026-keynote-image-prompts.md) | WAIFF Brasil 2026 keynote zine | hopecode/zine (Gemini) | Full deck + later-session adds |
| [wikipedia-five-futures-image-prompts-archive.md](./wikipedia-five-futures-image-prompts-archive.md) | Wikipedia "Five Futures" | none (Midjourney `/imagine`) | Master/subtheme + keyword lists |
| [gni-journalism-sovereignty/](./gni-journalism-sovereignty/) | GNI sovereignty diagrams | gni + hopecode | Lines, `.txt`, batch spec, Blue Engine notes |

## Related: BC+AI community theory diagrams (HOPECODE)

[prompts/bcai/bcai-hopecode-visual-prompts.md](../bcai/bcai-hopecode-visual-prompts.md) — BC+AI ecosystem researcher/subject duality, situated knowledge maps, watershed, and spore genesis prompts in the HOPECODE visual language. Different themes (community theory vs personal creative practice), same aesthetic.

Runnable batch companion: [prompts/bcai/bcai-hopecode-batch.md](../bcai/bcai-hopecode-batch.md)

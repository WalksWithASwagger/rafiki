# KB ecosystem image-prompt mirror

**What this is:** A **full copy** of every `image-prompts*.md` / `image-prompt*.md` / `image-gen-prompts.md` file under the sibling **[kk-ai-ecosystem](https://github.com/WalksWithASwagger/kk-kb)** repo (`articles/`, `projects/`), plus **overlays** where the KB only had stubs:

| Overlay | Why |
|---------|-----|
| `.../creative-mornings-.../slides/image-gen-prompts.md` | KB file is a stub; this is the **full** deck from [`../creative-mornings-vancouver-may-2026/`](../creative-mornings-vancouver-may-2026/image-gen-prompts.md) |
| `.../uai-film-festival-brazil-2026/image-prompts.md` | KB stub; same content as [`../kk-kb/waiff-brazil-2026-keynote-image-prompts.md`](../kk-kb/waiff-brazil-2026-keynote-image-prompts.md) |

**Not duplicated here (already first-class in Rafiki):** [`../kk-kb/`](../kk-kb/README.md) — HOPECODE batch, GNI, Web Summit zine, MAC femme, Wikipedia Five Futures, diagram teaching kit, etc.

**Refresh this mirror** (from a machine with both repos; default `KB_ROOT=../kk-ai-ecosystem` next to Rafiki):

```bash
cd /path/to/rafiki && chmod +x ./scripts/sync-kb-image-prompt-mirror.sh
KB_ROOT=~/Code/notion-local/kk-ai-ecosystem ./scripts/sync-kb-image-prompt-mirror.sh
```

**Mirror snapshot date:** 2026-04-26

---

## Inventory (50 files)

| Area | Path under this folder | Notes |
|------|-------------------------|--------|
| Thought leadership | `articles/kris-krug-thought-leadership/**/image-prompts.md` | 22 article packs + `your-judgment-is-the-moat` |
| BC AI website | `articles/bc-ai-website/**/image-prompts.md` | 2 |
| BC AI Festival 2026 | `projects/02-bc-ai-ecosystem-nonprofit/events/.../branding/` | 1 |
| Creative Mornings May 2026 | `projects/.../creative-mornings-.../slides/image-gen-prompts.md` | **full** punk deck |
| WAIFF Brazil 2026 | `projects/03-theupgrade-ai-training/.../uai-film-festival-brazil-2026/image-prompts.md` | **full** zine/Gemini deck |
| Responsible AI Pro (cert) | `projects/03-theupgrade-ai-training/.../responsible-ai-professional/...` | 3 (incl. infographics) |
| Upgrade marketing hub | `projects/05-marketing-and-outreach/upgrade-marketing-hub/**/images/` | 8 verticals |
| Apparel / lot tee | `projects/apparel-screen-print/image-prompt*.md` | 7 |
| Ed AI meetup | `projects/ed-ai-education-meetup/image-prompts*.md` | 4 |

Run `find . -name '*.md' | sort` from this directory for the exact list.

---

## Rerun (with Rafiki) — read this first

See **[image-pipeline-operator.md](../../docs/image-pipeline-operator.md)** for the scenario decision table, prompt-file inventory, style guidance, reference-image flow, and CLI recipes. This folder is the **raw prompt library**; [`kk-kb/`](../kk-kb/README.md) is the **curated diagram + zine** archive. Run batches when you’re ready — no need to delete anything here if you add `v2` prompts next to `v1`.

## Visual system

**Mixed styles — every prompt file declares its own `**Style:**`** (most thought-leadership articles use `kk`; Creative Mornings + WAIFF Brazil use punk-zine / hopecode; RAP marketing uses `bcai`/`upgrade`). Style guides live in [`../../styles/`](../../styles/). No single palette or reference image applies across this mirror — treat each `image-prompts.md` as self-describing.

## Run command

Pick any prompt file in the mirror and run it directly; the file's declared style flag is what matters:

```bash
# Example: regenerate a thought-leadership article's image pack
python generate.py \
  -f prompts/kb-ecosystem-mirror/articles/kris-krug-thought-leadership/01-build-tools-next-job/image-prompts.md \
  -d output/kb-mirror/01-build-tools-next-job \
  --style kk -m gpt-image-2 -w 2
```

For the punk-zine and HOPECODE overlays, swap `--style kk` for `zine` / `hopecode` — match what the file's frontmatter declares. For phased multi-file runs, follow the recipes in [image-pipeline-operator.md](../../docs/image-pipeline-operator.md) instead of invoking files one at a time.

# Image prompt archive & pipeline (where things live)

**Canonical bundle (KK knowledge base prompts, moved from `kk-ai-ecosystem`):** [`prompts/kk-kb/`](../prompts/kk-kb/README.md) — diagram index, HOPECODE / GNI / zine / WAIFF / MAC / Wikipedia Five Futures, GNI `gpt-image-1` assets, and links to the Streamlit batch UI under [`tools/gpt-image-batch-ui/`](../tools/gpt-image-batch-ui/README.md).

**BC+AI style compendia (older / alternate):** [`prompts/bcai/`](../prompts/bcai/README.md) — ecosystem diagrams, HOPECODE “dark aurora” master file, field-journal scene, RAP marketing prompts. Pairs with [`styles/bcai.md`](../styles/bcai.md) and HOPECODE style when using `--style hopecode`.

**CLI styles:** `kk`, `hopecode`, `bcai`, `upgrade` — see [`styles/`](../styles/) and the main [`README.md`](../README.md).

**Knowledge base:** the monorepo keeps **stub** pointers at old `content/reference/` paths; edit prompt **bodies** in this **Rafiki** repo.

**Next steps (operator):** analyze corpus → map repeated visual families to style flags → document “which model + which prefix + which command” in one runbook; optionally version prompt upgrades (`*-v2`) instead of silent overwrites.

*Last updated: 2026-04-25.*

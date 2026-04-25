# GNI / journalism sovereignty — `gpt-image-1` batch assets

**Context:** Google News Initiative / AI + journalism ethics / “sovereignty” talk diagrams. Batch-generate with OpenAI **`gpt-image-1`**, prepending the **HOPECODE** plain-text style guide for consistent “root-first, not reach-first” diagrams.

| File | Purpose |
|------|---------|
| [hopecode-style-guide.txt](./hopecode-style-guide.txt) | Paste or upload as **style prefix** in the Streamlit app (or concatenate in scripts). |
| [gpt-image-1-prompts-one-per-line.txt](./gpt-image-1-prompts-one-per-line.txt) | **44** lines: `create this diagram "…"`. |
| [batch-image-gen-spec.md](./batch-image-gen-spec.md) | API notes + UI spec + retry rules. |
| [blue-engine-collaborative-style-notes.md](./blue-engine-collaborative-style-notes.md) | Optional **alternate** clean/civic deck aesthetic (not default HOPECODE). |

**App (Streamlit, live image stream):** [../../tools/gpt-image-batch-ui/README.md](../../tools/gpt-image-batch-ui/README.md) in the **Rafiki** repo.

**Quick clip for any script**

```bash
# From Rafiki root — prefix every line, e.g.:
# STYLE=$(cat prompts/kk-kb/gni-journalism-sovereignty/hopecode-style-guide.txt)
# Then: full="$STYLE

$line"
```

**Related (creative / Upgrade-style big-idea pairs, Vancouver diagram series):** [../hopecode-creative-big-ideas-prompts.md](../hopecode-creative-big-ideas-prompts.md)

*Last updated: 2026-04-26*

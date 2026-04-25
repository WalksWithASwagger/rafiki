# AI diagram pipeline — teaching kit (journalists & PR / Upgrade cohorts)

**Purpose:** Preserve the live talk structure, workflow narrative, ethics, exercise, and gallery links. For **HOPECODE** plain text to prepend to prompts, use [gni-journalism-sovereignty/hopecode-style-guide.txt](./gni-journalism-sovereignty/hopecode-style-guide.txt). For **API batching**, see [batch-image-gen-spec.md](./gni-journalism-sovereignty/batch-image-gen-spec.md) and the [Streamlit batch UI](../../tools/gpt-image-batch-ui/README.md) (Rafiki repo: `rafiki/tools/gpt-image-batch-ui/`).

---

## One paragraph (everything)

About two weeks after the new ChatGPT image model shipped, it became practical to treat **infographics and diagrams** as a fast, iterative layer on top of any story: take a blog post, keynote, or article, run it through a **big-idea extractor** so each section becomes one or two **image prompts**, prepend a **diagram style guide** (e.g. HOPECODE—reverse-engineered from prior work so the machine knows your visual DNA), generate **10–20** images in a pass, skim the album for **near-perfect** frames, then **polish in Canva** (Magic Grab Text, contrast, exact wording). The result is publishable visuals in minutes—**not** to skip design judgment, but to **compost** repetitive layout time into iteration on meaning, disclosure, and accessibility—**publish with prompt + alt-text** so the lineage stays visible.

---

## Six-step process (diagram-process overview)

1. **Distill** key ideas from content (atomic statements, ~20 words).  
2. **Create image prompts** per idea (optionally two: “scene” + “diagram”).  
3. **Render** with the image model (ChatGPT / **`gpt-image-1`** / org-approved tool).  
4. **Curate** best outputs; star the 90% hits.  
5. **Polish** in Canva (text fix, labels, a11y).  
6. **Publish** with **attribution**, **alt text**, and **transparency** (AI-assisted).  

**Mantra:** Prompt boldly, audit relentlessly, publish responsibly.

---

## 15-minute talk clock + optional 10-minute sprint

| Time | Segment | You do | They see | One-liner |
|------|---------|--------|----------|-----------|
| 0:00–0:01 | Spark | Quick poll: still begging design for every graphic? | Title: “From draft to diagram in ~15 minutes” | “That pain can end.” |
| 0:01–0:03 | Why | Speed, credibility, narrative sovereignty | Old maze vs straight pipeline | “Visuals shouldn’t be a paywall on your story.” |
| 0:03–0:06 | Pipeline | Extract → Prompt → Render → Curate → Polish → Publish | Simple loop diagram | “AI as dance partner, not vending machine.” |
| 0:06–0:09 | Live mini-demo | One paragraph → prompt + one generation | Split: prompt / image | “GPU time vs. hours of chart wrestling.” |
| 0:09–0:12 | Case carousel | ~20s each: **raw** vs **polished** (repeat template) | 3-panel or side-by-side | “Same process, different missions.” |
| 0:12–0:13 | Ethics | Transparency, bias in metaphor, data sovereignty | Icons + short bullets | “Tools serve people.” |
| 0:13–0:14 | Toolkit | QR: style gist, [batch UI](../../tools/gpt-image-batch-ui/README.md), FOSS (Penpot, Inkscape) | Resource slide | “Fork, remix, gift forward.” |
| 0:14–0:15 | CTA + optional sprint | Invite hands-on; `#DIYInfogram` or cohort tag | “Your turn” | “Grow the garden together.” |

**Optional 10-minute exercise**

| Min | Activity |
|-----|----------|
| 0–1 | Pairs; each picks one paragraph of their own (or a supplied sample). |
| 1–3 | Draft one prompt using style guide one-liner. |
| 3–7 | Generate; save **raw PNG + prompt text**. |
| 7–9 | **Show & tell** (shared Miro / slide / Luma). |
| 9–10 | **Reflection:** What surprised? What would you audit before shipping? |

---

## Example gallery strategy (2 visuals × project)

| Project | What to show | Why |
|---------|--------------|-----|
| **Indigenomics Institute / AI platform** | Sovereignty + data flow; raw vs polished | Culturally specific symbolism without cliché; de/colonial data |
| **The Upgrade — tech transfer workshop** | Pipeline schematic; poster | Training + marketing loop |
| **Vancouver AI meetup recap** | Collage or quote card | Same-night recaps, momentum |
| **kriskrug.com / op-ed** | Satirical or long-form explainer | Voice + range |

**Folder pattern:** `examples/<project>/01_raw.png`, `01_final.png`, `01_prompt.txt` (optional).

**Google Photos (albums; images not in repo):**

- [Google News Initiative — AI Lab examples](https://photos.app.goo.gl/gMJbJDpNC8EAxMoC9)  
- [Indigenomics Institute — AI platform](https://photos.app.goo.gl/BENttuCuvbNakjYA9)  
- [Web Summit Vancouver takeover](https://photos.app.goo.gl/Am5NbX85rpBdPuD27)  
- [Vancouver AI Community Meetups](https://photos.app.goo.gl/eNDRP9WVdEQVCG8a8)  

---

## Ethics & power (short checklist)

- **Transparency:** Tag AI-assisted visuals; link or append **prompt** where appropriate.  
- **Bias:** Diagrams **encode worldviews**—audit icons, metaphor, who is centered.  
- **License / refs:** OpenAI output terms evolve—verify; don’t pass off **uploaded** reference art as all-generated.  
- **FOSS path:** Canva is convenient; name **Penpot / Inkscape** for orgs avoiding lock-in.  
- **Footprint:** Batch off-peak if volume is high; note carbon when relevant.  

---

## Custom GPTs (full system prompts)

See **[custom-gpt-diagram-gardener-and-weaver.md](./custom-gpt-diagram-gardener-and-weaver.md)** — *Diagram Prompt Gardener* (prompts + JSON + alt text) and *Diagram Weaver* (image generation + metadata).

**Architecture:** Gardener = linguistic layer; Weaver = render layer (swappable to API / batch script).

---

## Style guide satellites

- **HOPECODE (default KK diagrams):** [hopecode-style-guide.txt](./gni-journalism-sovereignty/hopecode-style-guide.txt)  
- **GNI “cosmic / editorial” lab:** [gni-cosmic-diagram-style-guide.md](./gni-cosmic-diagram-style-guide.md)  
- **Indigenomics (mythic + cultural care):** [indigenomics-diagram-style-guide.md](./indigenomics-diagram-style-guide.md)  
- **Blue Engine (clean civic / coaching deck):** [gni-journalism-sovereignty/blue-engine-collaborative-style-notes.md](./gni-journalism-sovereignty/blue-engine-collaborative-style-notes.md)  

---

## API reality check (2025+)

**Do not** use fictional `chat.completions` + `image_url` samples from old drafts. For **batched, scriptable** generation, use the **Image API** with **`gpt-image-1`** (or current doc model name), `images.generate`, `b64_json` or URL—see [batch-image-gen-spec.md](./gni-journalism-sovereignty/batch-image-gen-spec.md).

---

*Kit version: 2026-04-26.*

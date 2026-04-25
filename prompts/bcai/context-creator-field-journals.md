# Convergent truth — “CONTEXT CREATOR” (field journals)

Found-object field-notes aesthetic: overlapping torn journal pages, same phrase circled on each, mycelial threads and a bioluminescent node. Earth tones; glow is the only strong spectral color. *Not* punk zine / xerox — use a neutral or documentary style, or `bcai` for organic mycelial emphasis.

**Plain prompt (for tools that mangle blockquotes):** see the `**Prompt**` block below; strip `>` if pasting into a single-line field.

---

## 1. Three field journals — same phrase, one node

**For:** Keynote / article hero / narrative illustration — three independent “altitudes” landing on the same term  
**Aspect:** 16:9  
**File name:** context-creator-field-journals.png

**Prompt:**
> Three separate pages torn from three different field journals, different paper weights, different aged textures, different water stain patterns, laid overlapping on a rough wooden surface. Each page has notes in different handwriting styles, but all three pages have the same two words circled heavily in different colored ink, surrounded by underlines, arrows, and exclamation marks: CONTEXT CREATOR. The rest of each page is different: one has sustainability diagrams and food waste tallies, one has comedy sketches and Latine neighborhood maps, one has a program timeline and collaborator notes; the phrase at the center of each is identical. Between the pages, thin mycelial threads creep across the wooden surface, connecting the three circles where the phrase appears, meeting at a glowing bioluminescent node in the middle gap. Earth tones: ochre, ash, rust, muted moss. The glow at the node is the only spectral color: electric fungi green bleeding to oil-slick purple. Small monospace-style field-note annotations: "arrived independently", "three altitudes", "same word, no coordination". Coffee ring on one page, fold crease on another, tape residue on the third. The moment three separate minds landed on the same truth. Looks found, not designed.

**Rerun tips:** If the model over-punctuates the phrase, request “handwritten field notes, same two circled words on each sheet.” For stronger BC AI mycelial look, run with `--style bcai` and shorten the first sentence so the style guide can own palette.

```bash
# example single image (from kk-ai-ecosystem: cd tools/image-gen)
npx image-gen --prompt "…paste prompt…" --style bcai --aspect-ratio 16:9 --output context-creator-field-journals.png
```

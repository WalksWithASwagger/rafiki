# WAIFF keynote — complete image generation prompt archive

**Event:** WAIFF Brasil 2026 — Friday opening keynote ("How to Keep Our Souls Intact…")  
**Archive purpose:** Exact prompts used to generate zine-style slide art, plus pipeline metadata and prompt-engineering notes for reuse and replication.

| Field | Value |
|--------|--------|
| **Generation tool** | Custom `generate.py` calling **Google Gemini API** (internal / colloquial: "Nano Banana") |
| **Model** | `gemini-3-pro-image-preview` |
| **Reference image** | `reference-collage-v2.png` (style anchor; see [Prompt engineering notes](#prompt-engineering-notes) for reference-text conflicts) |
| **Aesthetic** | Black / white / blood red, halftone, xerox grain, punk zine collage, ransom-note type |
| **Ingested to KB** | 2026-04-27 |

**Related:** [SLIDE-DESIGN-BIBLE.md](./SLIDE-DESIGN-BIBLE.md), [slides/](./slides/) (deliverable PNGs), [README.md](./README.md).

---

## Table of contents

1. [Original slide prompts (deck v1 — slides 01–15)](#original-slide-prompts-deck-v1--slides-0115)  
2. [Additional slide prompts (later sessions)](#additional-slide-prompts-later-sessions)  
3. [Prompt engineering notes](#prompt-engineering-notes)  

---

*The reference collage (`reference-collage-v2.png`) was used as a style anchor across all generations. See Prompt engineering notes for guidance on reference-text conflicts.*

<!-- Reference: prompts/kk-kb/reference-collage-v2.png (see Prompt engineering notes) -->

## 1. Title slide — "How to Keep Our Souls Intact"

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Chaotic punk zine cover, dense overlapping collage with ripped magazine clippings, torn film strips, circuit boards, camera parts, newspaper fragments piled on top of each other with visible tape and glue. Halftone dots, ink smudges, coffee stains, staple holes. Black white and blood red only. Xerox grain everywhere. The following text MUST appear prominently in mixed cut-out ransom-note typography at various angles and sizes: "HOW TO KEEP OUR SOULS INTACT" as the largest text, and "WHEN THE MACHINES GET REALLY GOOD AT MAKING EVERYTHING" below it, and small stamped text "WAIFF BRASIL 2026" in a corner. Raw handmade zine energy.

## 2. Binary trap — Boosters vs doomers

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Punk zine spread ripped down the middle with torn paper edge. Left: corporate figure with exclamation marks. Right: figure with arms crossed, resistant. Both sides covered in xeroxed clippings and scratchy handwriting. Dense collage, halftone grain. Black white red. The following text MUST appear: "BOOSTERS" on the left side, "DOOMERS" on the right side, and a red banner across center reading "BOTH OF THESE ARE LAZY". Photocopied political broadsheet aesthetic.

## 3. Both hands full — Thesis

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Two photocopied hands palms up, cut from a magazine, pasted onto black background with visible tape. Surrounded by torn text fragments and handwritten scrawls. Halftone dots, ink blots, xerographic artifacts. Black white red. The following text MUST appear: Left hand area labeled "STOLEN WORK" "NO CONSENT" "REAL HARM". Right hand area labeled "TRANSFORMATION" "CAPABILITY" "AGENCY". Between the hands in large text: "BOTH THINGS ARE TRUE". Below: "walk forward holding both". Anarcho-punk zine page.

## 4. The five fears

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Punk zine list page with five numbered items in mixed media typography — stencil, typewriter, marker, cut-out letters. Margins filled with angry annotations and question marks. Red rubber stamp marks. Cheap newsprint texture, staple rust, xerox grain. Black white red. The following text MUST appear as the five items: "1. THE THEFT" "2. THE RACE TO BOTTOM" "3. THE PIPELINE COLLAPSE" "4. THE DEPENDENCY" "5. COMMODIFICATION". Corner stamp reads "DON'T DROP THIS HAND". Margin note: "I teach this for a living and I don't know".

## 5. Doing it backwards

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Stencil-sprayed text on concrete wall texture, dripping paint, photocopied badly with blown contrast. Below: torn collage of a robot painting art alongside a human doing paperwork. Taped down crooked. Ink splatters, marker scrawls. Xeroxed punk flyer aesthetic. Black white red. The following text MUST appear: Large dripping stencil text "WE'RE DOING IT BACKWARDS" at top, and annotation "automating art. keeping the drudgery." and red stamp "FLIP IT".

## 6. Better humans not better machines

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Almost entirely typographic punk zine page. Mixed media text assembled collage-style: typewriter, stencil spray, newspaper cutouts, hand-scrawled marker, all at different angles creating visual chaos. Red underlines and circles. Xerox grain, paper texture. Ransom note manifesto aesthetic. Black white red. The following text MUST appear: "THE NEXT EVOLUTION ISN'T ABOUT BEING BETTER MACHINES" at top, and larger below with red emphasis: "IT'S ABOUT BEING WORSE MACHINES AND BETTER HUMANS" with "BETTER HUMANS" biggest and in red.

## 7. Transformation stories

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Punk zine interview page. Three rough rectangular frames in a column, each with a high-contrast photocopied silhouette portrait. Typewriter text and handwritten annotations next to each. Cheap xerox paper, staple holes, tape marks. DIY music zine layout. Black white red. The following text MUST appear next to each frame: "3 WEEKS → 4 HOURS", "25 YRS VFX → VIBE LOUNGE", "2,000 PORTRAITS → OWN MODEL". Red banner at bottom: "NOT REPLACED. TRANSFORMED."

## 8. The ecosystem — Mycelium

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Hand-drawn network diagram in thick black marker on cheap paper, photocopied. Organic branching mycelium lines connecting nodes. Some nodes circled in red. Annotations in tiny handwriting. Newspaper clippings pasted around edges. Conspiracy board meets punk scene map. Xerox grain, tape marks, coffee ring. Black white red. The following text MUST appear: nodes labeled "FILM CLUB" "MIND AI" "EDUCATION" "ETHICS" "SURREY" with central node "850+". Below: "NOT A PRODUCT. AN ECOSYSTEM." Corner: "Cinema Novo did this first".

## 9. AI is a mirror

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Stark photocopied image of a hand holding a small mirror, high contrast with halftone dots breaking apart. Mirror reflection scratched over with red marker. Sparse page with breathing room — the quiet page in the zine. Xerographic artifacts, fourth-generation photocopy look. Black white red. The following text MUST appear: large stencil text below the image "SELF-KNOWLEDGE IS THE PREREQUISITE". Small annotation: "AI is a mirror". Dark, moody, intimate.

## 10. Selector — Taste is your moat

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Punk music fanzine page. A vinyl record photocopied into heavy halftone, pasted at angle. Surrounding: torn gig flyers, handwritten setlists, cut-out reviews, all layered and overlapping. Red marker highlights. Tape holding things down. Dense collage, xerox grain. Black white red. The following text MUST appear: "GENERATION IS CHEAP. TASTE IS NOT." as main text, "DJs WERE CALLED SELECTORS" nearby, margin notes "Tropicalia / Bossa Nova / Cinema Novo", red stamp "YOUR TASTE IS YOUR MOAT".

## 11. Write for the bot

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Photocopied typewriter on cheap paper, high contrast halftone. Paper emerging from typewriter with dense text. Surrounded by torn newspaper clippings taped at angles, urgent handwritten notes, red rubber stamps. Punk zine editorial page. Xerographic grain, staple holes. Black white red. The following text MUST appear: large typewriter font "IF YOUR VALUES AREN'T IN TEXT, TO AI THEY DON'T EXIST", below in red "DANGEROUSLY CLOSE TO WON'T EXIST", bottom scrawl "TONIGHT: 3 SENTENCES. WHAT YOU BELIEVE. WHY YOU MAKE FILMS." Red stamp: "CULTURAL ACTIVISM".

## 12. Ship culture not content

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Punk zine split page: left side industrial factory smokestacks in high contrast halftone. Right side organic hand-drawn garden with growing plants. Torn paper edge dividing them diagonally with red showing through. Overlapping clippings, stencil text, magazine cutouts. Xerox grain. Black white red. The following text MUST appear: "CONTENT" above factory, "CULTURE" above garden, bottom text "PRODUCTS COMMODITIZE. CULTURE COMPOUNDS."

## 13. Creative DNA — Eyes closed

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Nearly black page. Heavy xerographic grain visible like television static. Sparse typewriter text floating in the darkness. One torn paper edge along bottom showing white. The quiet breath page inside a chaotic zine. Minimal, lonely, intimate. Mostly black with grain. The following text MUST appear in white typewriter font centered: "CLOSE YOUR EYES." then "WHAT'S THE ONE THING YOU'D NEVER GIVE UP TO AI?" then "THAT'S YOUR CREATIVE DNA."

## 14. Stay in the room

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Urgent punk warning poster. Bold hand-drawn red marker border framing the page. Inside: a single empty chair at a table, high contrast halftone, slightly crooked. Newspaper fragments pasted around it. Stencil text, handwritten warnings in margins. Red X marks. Emergency broadsheet aesthetic. Xerox grain, tape, glue marks. Black white red. The following text MUST appear: "IF ALL THE ETHICAL PEOPLE OPT OUT" above, "GOVERNANCE GETS MADE BY OPPORTUNISTS" below, hand-scrawled "STAY IN THE ROOM" at bottom.

## 15. Close — Both hands full

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Final page of a punk zine. Two raised open hands cut from magazines pasted on either side with visible tape and scissor marks. Between them: dense layered text fragments in mixed typography. Red accents throughout. Defiant and invitational. Halftone dots, xerox grain, ink smudges, staple holes. Assembled on someone's bedroom floor at midnight. Black white red. The following text MUST appear: left area "NON-CONSENSUAL / UNJUST / EXTRACTIVE", right area "TRANSFORMATIVE / CAPABLE / HAPPENING", center large "BOTH HANDS FULL", bottom "YOU COMING?", corner "OBRIGADO".

---

## Additional slide prompts (later sessions)

*Slides 16–21 below are additional variants generated in later sessions. Numbering continues from the main deck for batch compatibility. Original iteration labels are preserved in each title.*

## 16. 06b — Stop saying bias

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Hardcore punk zine page in black, white, and blood red only. Heavy xerox grain, halftone dots, cut-and-paste collage aesthetic with torn paper edges, tape marks, staple holes. Ransom-note mixed typography using stencil, typewriter, marker, and magazine cutouts at chaotic angles. The following text MUST appear prominently: "STOP SAYING BIAS" as the largest text in aggressive stencil style, and below it "NAME WHAT YOU'RE SEEING:" followed by "MISOGYNY" "RACISM" "EMBEDDED IN CODE" arranged as a vertical list or scattered. Additional text: "Joy Buolamwini: 40x failure rate" as a margin annotation. Raw handmade DIY zine energy, anti-corporate, assembled at midnight.

## 17. Add-on — The 80/20 flip (Luke)

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Hardcore punk zine page, black white and blood red only. Xerox grain, halftone dots, cut-and-paste collage with torn paper, tape marks. A central silhouette figure (animator at work) made from high-contrast photocopied magazine clipping. Around it: handwritten annotations and stenciled numbers. The following text MUST appear: "80% GRIND → 80% CREATIVE" as the main headline in mixed ransom-note typography, "THE 12 YEAR OLD IS BACK" in red marker style, small annotation "Jurassic Park. 30 years later." and "Tiny Ghost Studio". Raw punk zine energy.

## 18. Add-on — The conductor (Kevin)

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Punk zine page in black white red. Xerox grain, halftone, collage aesthetic. Central image: high-contrast photocopied silhouette of a conductor with baton raised, cut from a magazine and pasted at angle with visible tape. Orchestra elements scattered around as torn fragments. The following text MUST appear: "THE ORCHESTRATION ERA" as main headline in stencil/ransom style, "25 YEARS VFX" as annotation, "85% AI — CRAFT FINISHES" in red, margin scrawl "the conductor still matters". DIY handmade aesthetic.

## 19. Add-on — Hope to exist (Belgium)

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Dark, minimal punk zine page. Mostly black with heavy xerox grain like television static. A single high-contrast photocopied silhouette of a person lying down (bedridden) in the upper portion. Sparse, lonely, intimate. The following text MUST appear in white typewriter font against the darkness: "AI FILM IS MY HOPE" then "TO BE ABLE TO CONTINUE TO EXIST" then "AND TO TELL SOMETHING" as a descending stack. Small red annotation: "18 months bedridden". The quiet page in the zine. Emotional weight.

## 20. Add-on — So what do you do

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Punk zine transition page, black white red. Explosive stencil typography fills the page at aggressive angles. Xerox grain, ink splatters, halftone interference patterns. Energy shift from emotional to practical. The following text MUST appear: "OK SO NOW WHAT?" as largest text in dripping stencil style, "WHAT DO YOU ACTUALLY DO?" below in ransom-note cutouts, small annotation "from stories to frameworks". Red arrow pointing forward. Urgent, activating energy.

## 21. 13b — Loops / intuition (Matt Lambert)

**Model:** pro
**Style:** zine
**Aspect Ratio:** 16:9

**Prompt:**
> Punk zine page in black white blood red. Xerox grain, halftone dots, torn paper collage aesthetic. Central visual: a rough hand-drawn loop or spiral in thick black marker, photocopied badly. Around it: scattered text fragments and annotations. The following text MUST appear: "INTUITION IS PATTERN RECOGNITION" as a main line in mixed typography, "BUILT THROUGH REPETITION" below it, "MAKE → EVALUATE → ADJUST → LOOP" as a sequence, and the key phrase "AI GENERATES VARIATION. YOU DECIDE WHAT PERSISTS." in red emphasis. Margin note: "Matt Lambert". Attribution: small text "the difference isn't talent — it's accumulated loops"

---

## Prompt engineering notes

### Key directives that worked

1. **Explicit text inclusion:** "The following text MUST appear prominently:"
2. **Typography style:** "mixed cut-out ransom-note typography at various angles and sizes"
3. **Color restriction:** "Black white and blood red only"
4. **Texture requirements:** "Xerox grain everywhere. Halftone dots."
5. **Physical artifacts:** "visible tape and glue, staple holes, coffee stains, torn paper edges"
6. **Mood direction:** "Raw handmade zine energy" / "anti-corporate"

### Common issues and fixes

| Issue | Mitigation |
|--------|------------|
| **Generic or wrong on-image text** | Reference images can override prompt text; prepend instructions to **ignore** text in the reference image, or reduce reference weight if the API allows. |
| **Too corporate or polished** | Add "anti-corporate" and "assembled at midnight on someone's bedroom floor." |
| **Flat contrast** | Specify "fourth-generation photocopy look" and "blown contrast." |

### Reference image (Rafiki CLI)

If `reference-collage-v2.png` is available locally, pass it as:

```
python generate.py -f prompts/kk-kb/waiff-brazil-2026-keynote-image-prompts.md --reference path/to/reference-collage-v2.png --style zine -m pro
```

---

*End of archive — prompts match production deck generation for WAIFF Brasil 2026 keynote zine slides.*

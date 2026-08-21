# Slingsby Advisors Likeness Jobs

Public-safe **job list** for authorized portraits. These prompts do not invent
hair, age, or wardrobe. They only work when you pass authorized photographs:

```bash
python3 generate.py --prompt-file examples/slingsby-advisors-likeness-jobs.md \
  --style slingsby \
  --reference-role likeness \
  --global-reference-images assets/slingsby/likeness/a.jpg,assets/slingsby/likeness/b.jpg \
  --output-dir output/slingsby-advisors \
  --dry-run --no-viewer
```

Do not run this pack without `--reference-role likeness` and the authorized
set. The default style role would treat the photos as texture, not identity.

## 1. Hero three-quarter
**For:** Proposal cover / about
**Aspect Ratio:** 4:5
**Style:** slingsby
**Prompt:**
> The woman in the attached authorized reference photographs, exact likeness, match age from the refs, do not youth-wash. Three-quarter portrait, quiet eyeline, unhurried. Photographed in a luminous modern office, soft window light, shallow depth of field. Generous negative space, no nametags, no event badges, no readable text, no logos. Do not invent a different person.

## 2. Bio still
**For:** About / bio page
**Aspect Ratio:** 4:5
**Style:** slingsby
**Prompt:**
> The woman in the attached authorized reference photographs, exact likeness, match age from the refs, do not youth-wash. Seated, rest expression, hands visible and still. Quiet advisory room, paper on the table, city soft through glass. No nametags, no event badges, no readable letterhead. Do not invent a different person.

## 3. Stewardship table
**For:** Working scene
**Aspect Ratio:** 16:9
**Style:** slingsby
**Prompt:**
> The woman in the attached authorized reference photographs, exact likeness, match age from the refs, do not youth-wash. At a table with a closed folder and a glass of water, listening more than performing. Wide editorial crop through glass or a doorway, golden-hour haze. No other people, no nametags, no event badges, no readable text. Do not invent a different person.

## 4. Studio
**For:** Painter / practice page
**Aspect Ratio:** 4:5
**Style:** slingsby
**Prompt:**
> The woman in the attached authorized reference photographs, exact likeness, match age from the refs, do not youth-wash. Standing at a sunlit window desk in a modern office, not posing like a catalogue model. Backlight, quiet labour, no other faces. No nametags, no event badges, no readable text on screens or paper. Do not invent a different person.

## 5. Counsel
**For:** Conversation / two-chair page
**Aspect Ratio:** 16:9
**Style:** slingsby
**Prompt:**
> The woman in the attached authorized reference photographs, exact likeness, match age from the refs, do not youth-wash. In a two-chair conversation room; the second chair is empty. She is present and exact, not theatrical. Through-glass crop, slow window light, no other faces, no nametags, no event badges, no logos. Do not invent a different person.

## 6. Hands and material
**For:** Detail plate
**Aspect Ratio:** 1:1
**Style:** slingsby
**Prompt:**
> Close crop of the hands of the woman in the attached authorized reference photographs — match jewelry and skin from the refs, do not invent rings or nails, do not youth-wash. Hands rest on paper or near pigment. No face required if the refs make the hands identifiable. No nametags, no event badges, no readable text.

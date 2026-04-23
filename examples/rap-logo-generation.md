# Example: Generating RAP Logo Variations with Reference Images

This example shows how to create professional logo variations for the RAP (Responsible AI Professional) certification program using the BC + AI logo as a reference.

## Goal

Create 5 logo variations for RAP that maintain BC + AI's exact visual identity (colors, typography, spacing) while adding certification-specific text.

## Reference Image

- **Source:** BC + AI ecosystem logo
- **Path:** `../../content/to-ingest/bc-ai-logo.png`
- **Colors:** Navy #0A1F3C, Mint #C5DFD5, Yellow #E8ED4F
- **Typography:** Clean sans-serif, bold letters, generous spacing
- **Aesthetic:** Professional yet organic (subtle mycelial touches)

## Prompts

See: `/tools/image-gen/prompts/bcai/rap-logo-variations.md`

5 variations designed:
1. **Stacked Certification Badge** - BC + AI at top, RAP certification below
2. **Horizontal Logo** - BC + AI left, separator, RAP text right
3. **Minimal Icon** - Circular badge with RAP monogram
4. **Text-Only Wordmark** - Clean typography stack
5. **Circular Seal** - Official certification badge with curved text

## Generation Command

```bash
cd /tools/image-gen

npx image-gen ./prompts/bcai/rap-logo-variations.md \
  --reference-image ../../content/to-ingest/bc-ai-logo.png \
  --model gemini-3-pro-image-preview \
  --resolution 2K \
  --output-dir ./outputs/rap-logos-pro/
```

## Results

- **Generated:** 5/5 logos successfully
- **Quality:** Professional (matches actual brand)
- **Ready for:** Certificates, website, Luma events, LinkedIn badges
- **Output:** `/tools/image-gen/outputs/rap-logos-pro/`

## Key Learnings

### Why Reference Images Matter

**Without reference (text descriptions only):**
- AI recreates logo from scratch based on text
- Colors are approximate, not exact
- Typography doesn't match
- Spacing and proportions are off
- Result: Amateur-looking recreations

**With reference (actual logo file):**
- AI uses actual logo as style guide
- Colors match exactly
- Typography is consistent
- Spacing and proportions maintained
- Result: Professional derivatives

### Best Settings for Logo Work

- **Model:** `gemini-3-pro-image-preview` (not flash - better quality)
- **Resolution:** `2K` or `4K` (logos need high resolution)
- **Aspect Ratio:** Varies by use case (1:1 for badges, 16:9 for banners)
- **Style:** Can use `bcai` style or `none` (reference handles style)

## Reusable Workflow for Other Projects

This approach works for any brand extension:

### Step 1: Have Reference Asset
- Logo file (PNG, JPG)
- Brand guidelines documented
- Color codes known

### Step 2: Write Variation Prompts
Create `image-prompts.md` file describing what you want:
- What to keep from reference (colors, typography, spacing)
- What to add/change (new text, layout variations)
- Use case for each variation

### Step 3: Generate with Reference
```bash
npx image-gen ./prompts/your-variations.md \
  --reference-image ./your-logo.png \
  --model gemini-3-pro-image-preview \
  --resolution 2K \
  --output-dir ./outputs/
```

### Step 4: Get Brand-Consistent Results
- Professional quality derivatives
- Exact color matching
- Consistent typography
- Ready to use

## Other Use Cases

This workflow can create:

**Event Branding:**
- Vancouver AI Meetup monthly variants
- Special event badges
- Sponsor thank-you graphics

**Program Branding:**
- TheUpgrade course logos
- Certification badges
- Workshop materials

**Community Groups:**
- Special Interest Group badges
- Chapter/location variants
- Role-specific badges (member, founder, speaker)

**Marketing Assets:**
- Social media variants
- Email header graphics
- Presentation templates

## File Locations

**RAP Project:**
- Prompts: `/tools/image-gen/prompts/bcai/rap-logo-variations.md`
- Reference: `/content/to-ingest/bc-ai-logo.png`
- Outputs: `/tools/image-gen/outputs/rap-logos-pro/`
- Landing Pages: `/content/projects/03-theupgrade-ai-training/certification-programs/responsible-ai-professional/`

---

*Created: January 2026*
*Part of BC + AI Responsible AI Professional Certification Program*

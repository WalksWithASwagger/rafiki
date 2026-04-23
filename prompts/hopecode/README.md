# HOPECODE Prompt Library

Welcome to the HOPECODE prompt library—a collection of example prompts that demonstrate how to generate images in the HOPECODE aesthetic using the Nano Banano image generator.

## What is HOPECODE?

HOPECODE is a solarpunk mycelial mapping aesthetic—organic, anti-corporate, and embodied. It's designed for personal thought leadership, alternative futures, and diagrams that breathe.

See the full [HOPECODE Style Guide](../../styles/hopecode.md) for complete aesthetic principles.

## Using These Prompts

All prompts in this library are designed to work with:

```bash
npx image-gen ./prompts/hopecode/[file].md --style hopecode
```

The `--style hopecode` flag automatically applies the HOPECODE aesthetic directives, so you don't need to include them in individual prompts.

### Single Prompt Usage

You can also extract individual prompts and use them directly:

```bash
npx image-gen --prompt "A mycelial network connecting community nodes" \
  --style hopecode \
  --aspect-ratio 16:9 \
  --output my-diagram.png
```

## Prompt Library Structure

This library is organized by use case:

### [personal-blog-examples.md](./personal-blog-examples.md)
Prompts for personal blog content:
- Journey maps showing personal transformation
- Story diagrams visualizing narrative arcs
- Concept webs exploring ideas
- Quote visualizations with organic styling

**Best for:** Blog headers, article diagrams, personal storytelling

### [thought-leadership-examples.md](./thought-leadership-examples.md)
Prompts for radical thought leadership:
- Anti-corporate framework diagrams
- Systems thinking maps showing complexity
- Future vision illustrations
- Critical analysis visualizations

**Best for:** Essays, manifestos, alternative perspectives

### [concept-mapping-examples.md](./concept-mapping-examples.md)
Prompts for mapping ideas and relationships:
- Relationship networks
- Knowledge webs
- Community maps
- Value systems diagrams

**Best for:** Planning, synthesis, understanding connections

## Writing Your Own HOPECODE Prompts

When writing prompts for HOPECODE style, focus on:

### Content Focus
- **What's being shown**: The ideas, relationships, or stories
- **Key elements**: Nodes, branches, zones, glyphs
- **Emotional tone**: Irreverent, visionary, embodied

### Let the Style Handle Aesthetics
The HOPECODE style suffix automatically adds:
- Jittered, hand-drawn linework
- Earth tones and spectral interference
- Analog texture and imperfections
- Organic, anti-corporate feel

### Example Structure

```markdown
## Title — Context

**For:** Blog post header, concept exploration
**Aspect:** 16:9
**File name:** my-diagram.png

**Prompt:**
> Describe WHAT you want to show, focusing on content and relationships.
> The HOPECODE style will handle the visual aesthetic automatically.
```

## Prompt Format

All prompts in this library follow this format:

```markdown
## N. Title — Context

**For:** Usage context (where/how it will be used)
**Aspect:** Aspect ratio (16:9, 1:1, 9:16, etc.)
**File name:** suggested-filename.png

**Prompt:**
> The actual prompt text describing what should be generated.
> Focus on content, relationships, and meaning.
> The HOPECODE aesthetic is applied automatically.
```

## Tips for Best Results

1. **Be specific about structure**: Describe nodes, branches, zones clearly
2. **Describe relationships**: How things connect matters more than what they look like
3. **Include context**: What's the story? What's the emotion?
4. **Trust the style**: Don't over-specify visual details—let HOPECODE breathe
5. **Iterate**: Try variations, see what the AI interprets

## Batch Processing

To generate all prompts from a file:

```bash
npx image-gen ./prompts/hopecode/personal-blog-examples.md \
  --style hopecode \
  --output-dir ./my-images/
```

This will create numbered output files like:
- `01-journey-map.png`
- `02-story-diagram.png`
- etc.

## Need More Examples?

Check out the KK style prompts in `/prompts/kk/` for comparison. Notice how HOPECODE prompts focus more on organic relationships and less on corporate precision.

## Contributing

These prompts are living documents. Fork them, remix them, make them your own. That's the HOPECODE way.

---

**Remember:** HOPECODE doesn't trend. It ferments. Use it to map the world you want to see, not the one you're trying to escape.

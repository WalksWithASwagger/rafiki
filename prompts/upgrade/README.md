# The Upgrade AI Prompt Library

Welcome to The Upgrade AI prompt library - example prompts for creating bold, transformation-focused training and marketing visuals.

## What is The Upgrade AI Style?

The Upgrade AI style embodies bold transformation and empowerment with an energetic, professional-yet-personable aesthetic. It's designed to make professionals feel: "I can do this. This is for me. This will change my work in real ways."

**Key characteristics:**
- Bold color palette (deep purple, bright orange, light blue)
- Transformation metaphors (upgrades, level-ups, before/after)
- Human-centered technology (AI as partner, not replacement)
- Dynamic, energetic composition
- "Creative chaos meets polished execution"

See the full [Upgrade AI Style Guide](../../styles/upgrade.md) for complete brand guidelines.

## Using These Prompts

All prompts work with:

```bash
npx image-gen ./prompts/upgrade/[file].md --style upgrade
```

The `--style upgrade` flag automatically applies The Upgrade AI aesthetic.

### Single Prompt Usage

```bash
npx image-gen --prompt "Professional transformation journey" \
  --style upgrade \
  --aspect-ratio 16:9 \
  --output hero-image.png
```

## Prompt Library Contents

### [training-marketing.md](./training-marketing.md)

Prompts for Upgrade AI training and marketing content:
- Course hero images
- Skill development diagrams
- AI + Human partnership visuals
- Professional growth graphics
- Community learning networks
- Training module headers
- Promotional CTAs

**Best for:** Course marketing, program materials, social media, email campaigns, landing pages

## Writing Upgrade AI Prompts

### Content Focus

- **Transformation Narrative**: Show the journey from current state to empowered future
- **Human Centerpiece**: People are always the focus, AI is the tool
- **Skill Growth**: Visualize capability building and expertise development
- **Community**: Learning together, collaborative growth
- **Accessibility**: This is achievable, you belong here

### Style Handles Automatically

The upgrade style suffix provides:
- Purple/orange/blue color palette
- Energetic, dynamic composition
- Transformation visual metaphors
- Empowerment tone
- Professional yet personable feel

### Prompt Structure Focus On

**WHAT to show:**
- The transformation (from → to)
- The professional (who this is for)
- The capability (what they'll gain)
- The partnership (human + AI collaboration)
- The outcome (empowered expertise)

**Let style handle HOW:**
- Color choices (purple/orange/blue)
- Energy level (dynamic, bold)
- Visual metaphors (upgrades, level-ups)
- Composition (focal points, CTAs)

## Prompt Format

```markdown
## N. Title — Purpose

**For:** Usage context (course header, social post, email, etc.)
**Aspect:** Aspect ratio (16:9, 1:1, 9:16, etc.)
**File name:** suggested-filename.png

**Prompt:**
> Describe the transformation content, focusing on who, what capability,
> and what outcome. The Upgrade AI style handles the bold aesthetic.
```

## Key Messaging to Include

When writing prompts, consider weaving in these themes:

- **"AI Mindset"** - Thinking with AI as a partner
- **"Rapid Upgrade"** - Fast, effective transformation
- **"Accelerate Your Success"** - Measurable improvement
- **"Expand Your Potential, Keep Your Spark"** - Enhancement, not replacement
- **Community & Collaboration** - Learning together
- **Practical Application** - Real-world impact

## Best Practices

1. **Show the transformation**: Always visualize change/growth/development
2. **Center the human**: People empowered by tech, not replaced
3. **Make it achievable**: Visuals should feel "I can do this"
4. **Include community**: Learning happens together
5. **Be specific about outcome**: What capability do they gain?
6. **Trust the energy**: Let the style provide boldness and dynamism

## Batch Processing

Generate all prompts:

```bash
npx image-gen ./prompts/upgrade/training-marketing.md \
  --style upgrade \
  --output-dir ./upgrade-images/
```

Creates numbered outputs like:
- `01-course-hero.png`
- `02-skill-development.png`
- etc.

## Visual Do's and Don'ts

**DO:**
- Show professionals actively engaging with AI tools
- Use upward arrows, progress bars, achievement unlocks
- Include diverse representation of learners
- Show collaborative learning environments
- Emphasize "aha!" moments and breakthroughs
- Make CTAs visually prominent

**DON'T:**
- Use robotic or dystopian AI imagery
- Show technology as threatening or replacing humans
- Create cold, alienating tech aesthetics
- Use confusing jargon or complex diagrams
- Make learning look inaccessible or elitist
- Forget the transformation narrative

## Use Cases

Perfect for:
- Course marketing landing pages
- Social media promotional graphics
- Email campaign headers
- Training module introductions
- Program overviews and pitch decks
- Success story visualizations
- Community update graphics
- Event promotion materials

## Comparison with Other Styles

**vs. kk:** Upgrade is energetic transformation, kk is polished editorial
**vs. HOPECODE:** Upgrade is empowering professionals, HOPECODE is radical critique
**vs. BC AI:** Upgrade focuses on individual growth, BC AI on ecosystem networks

## Brand Promise

Every Upgrade AI visual should communicate:
- AI amplifies human potential (never replaces it)
- Technology serves people (not the other way around)
- Expertise is accessible (you can learn this)
- Community supports growth (you're not alone)
- Transformation is achievable (start today, see results)

---

**Remember:** We're not selling hype—we're offering real transformation. Every visual should make someone lean in and say "tell me more."

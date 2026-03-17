---
name: Slide Design
description: >
  Reference-only skill providing design principles and a 100-point quality rubric
  for presentation slides — color strategy, typography hierarchy, layout rules,
  whitespace targets. This skill has no scripts and cannot take action — it is a
  knowledge base consulted by other skills (slide-generate, slide-validate,
  slide-pptx-builder) when they need design guidance. Use this skill when the user asks
  explicitly about design theory, the quality rubric scoring system, best practice
  rules, or "what are the design rules". Do NOT use for action requests like
  "make it look better" or "fix the design" — those should route to the skill
  that can act (slide-generate for regenerating, slide-validate for diagnosing,
  slide-pptx-builder for fixing layout).
---

# Slide Design Skill

This skill provides a comprehensive reference for evaluating, scoring, and improving the visual design quality of presentation slides. Use it whenever a user asks about design best practices, wants to validate slide output, or needs guidance on color, typography, layout, and visual hierarchy decisions.

## When to Use This Skill

Activate this skill when the user:

- Asks about design best practices for presentations or slide decks
- Wants to evaluate or score the visual quality of generated slides
- Requests guidance on color palettes, typography, or layout rules
- Mentions improving contrast, readability, or visual hierarchy
- Wants to validate that slides meet a quality threshold before delivery
- Asks about the design rubric or scoring criteria
- Needs to debug visual issues like overlapping elements, poor contrast, or inconsistent spacing

## What the References Contain

### design-principles.md (237 lines)

The design principles reference is the authoritative guide for all visual design decisions. Read this file when making color, typography, layout, or hierarchy decisions. It covers five major areas:

1. **Color Strategy** -- Rules for palette construction, contrast ratios (WCAG AA compliance), alpha-blending considerations for dark backgrounds, and color weight distribution. Apply these rules when choosing or validating background colors, text colors, accent colors, and shape fills.

2. **Typography** -- Font family limits, size hierarchy from title down to caption, line spacing ranges, alignment rules, and character spacing for emphasis. Apply these when setting font properties in python-pptx or evaluating extracted text formatting.

3. **Layout** -- Minimum margin requirements, whitespace ratios, element count limits, content flow patterns, and consistency rules for repeated slide types. Apply these when positioning shapes on the slide canvas or validating that generated PPTX output respects spatial constraints.

4. **Visual Hierarchy** -- Primary content placement, the one-key-message-per-slide principle, supporting detail positioning, and how size/color/position create visual weight. Apply these when reviewing slide content structure or advising on information architecture.

5. **Shapes & Containers** -- Border radius ratios for rounded rectangles, shadow parameters for cards, rules against mixing shape styles, and accent bar specifications. Apply these when constructing or validating shape properties in the PPTX builder.

### quality-rubric.md (264 lines)

The quality rubric is a machine-readable scoring system for slide validation. Read this file when scoring slides, building validation checks, or explaining pass/fail results. It defines seven categories totaling 100 points, with a pass threshold of 75. Each category specifies:

- **What to check** -- Concrete measurements and properties to inspect
- **Deduction rules** -- How many points to subtract per violation
- **Severity levels** -- Whether a violation is an error (full deduction) or warning (half deduction)
- **Examples** -- Concrete pass and fail cases for clarity

Use the rubric to build automated validation, to manually score slides during review, or to explain to users why a particular slide does or does not meet quality standards.

## How slide-validate Uses the Rubric

When validating slides, follow this procedure:

1. **Extract layout data.** Parse the JSON layout output from Chrome headless extraction or read shape properties directly from the PPTX file. Collect bounding boxes, font sizes, colors, and element counts for every slide.

2. **Run each category check.** For every slide, evaluate all seven rubric categories. Measure element positions against slide boundaries for bounds compliance. Check font sizes and contrast ratios for text readability. Calculate whitespace percentage for layout balance. Count unique colors for palette consistency. Inspect font families for typography compliance. Count top-level elements for content density. Verify no shapes extend beyond the 1280x720 canvas for visual overflow.

3. **Score and classify.** Sum the points for each slide. Flag any slide below 75 as failing. Classify individual violations as errors or warnings based on severity level definitions in the rubric.

4. **Report findings.** Present a per-slide score breakdown with specific violations listed. For each violation, reference the relevant design principle so the user understands both the rule and the rationale.

5. **Suggest fixes.** When a slide fails, recommend concrete changes. Reference the design principles to explain why the fix improves quality. Prioritize error-severity issues over warnings.

## Applying Principles During Generation

Do not treat design validation as a post-hoc step only. Apply the design principles proactively during slide generation:

- When the pptx_builder places shapes, verify margins and whitespace before finalizing positions.
- When setting text properties, enforce the font size hierarchy and line spacing ranges.
- When choosing colors for alpha-blended shapes on dark backgrounds, compute the blended result and check contrast before committing.
- When a slide has more than 6-7 elements, consider whether content should be split across multiple slides.

## Interplay with wicked-pptx

The design principles and rubric are calibrated for the wicked-pptx pipeline. The standard canvas is 1280x720 pixels (widescreen 16:9). Margin and size values in the principles reference assume this canvas size. When working with different dimensions, scale proportionally.

The alpha-blending guidance in the color strategy section directly complements the `color_utils.py` module bundled in slide-pptx-builder. The card text clamping rules in the layout section align with the card width constraints enforced by `pptx_builder.py`. Refer to both the design principles and the codebase when resolving visual quality issues.

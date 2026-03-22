---
name: generate
description: |
  Turns outlines into themed HTML slide files with optional image sourcing
  (Unsplash photos, icons, or text-only). Can work from a formal outline JSON
  or inline content.

  Use when: "generate the slides", "create the HTML", "build from the outline",
  "add photos", "use icons", "make slides from this content", "turn this into slides"
---

# Slide Generate

## Purpose

Slide Generate transforms structured outlines into individual HTML slide files
ready for the wicked-pptx conversion pipeline. Each slide is a self-contained
HTML file with inline CSS, proper viewport, and `.slide` wrapper — compatible
with standardize and chrome-extract without modification.

The skill applies the active theme's colors, fonts, and spacing to produce
visually consistent slides across the entire deck.

## When to Use

- After outline has produced an outline JSON
- When the user provides content and wants HTML slides generated
- When rebuilding slides after a theme change
- When adding slides to an existing deck

## Architecture

```
outline.json + theme → generate → 01-title.html, 02-hook.html, ... + slides.json
                                           ↓
                                    standardize → chrome-extract → pptx-builder
```

## Usage

```bash
# Generate slides from an outline
python ${CLAUDE_SKILL_DIR}/scripts/slide_generate.py --outline outline.json --output-dir ./slides/

# Generate with a specific theme (overrides outline's theme field)
python ${CLAUDE_SKILL_DIR}/scripts/slide_generate.py --outline outline.json --theme corporate-light --output-dir ./slides/

# Generate a single slide type for testing
python ${CLAUDE_SKILL_DIR}/scripts/slide_generate.py --type title --title "Test Title" --subtitle "Subtitle" --output slide-test.html

# List available slide templates
python ${CLAUDE_SKILL_DIR}/scripts/slide_generate.py --list-templates

# Generate with custom viewport
python ${CLAUDE_SKILL_DIR}/scripts/slide_generate.py --outline outline.json --output-dir ./slides/ --viewport 1920x1080
```

## Slide Templates

Each slide type has an HTML template that uses CSS custom properties from the
theme. Templates are defined in `references/templates.md` and implemented in
the generation script.

### Title Slide
- Centered title (large), subtitle below, optional accent bar
- Used for deck openers and section titles
- Design: clean, bold, minimal elements

### Content Slide — Bullets
- Assertion title top-left, bullet list below
- 3-5 bullets maximum, each under 15 words
- Left-aligned body text, generous line spacing

### Content Slide — Two Column
- Title spanning full width
- Left column: text content
- Right column: text, image placeholder, or stats
- 60/40 or 50/50 split

### Stats / Metrics Slide
- Title assertion at top
- 2-4 stat cards in a row or grid
- Each card: large number + label + optional trend indicator
- Cards use surface/card background with subtle shadow

### Comparison Slide
- Title at top
- Two columns with distinct headers
- Side-by-side content (before/after, option A/B, pros/cons)
- Visual separator between columns

### Quote Slide
- Large pull quote centered
- Attribution below in muted text
- Optional accent bar left of quote
- Minimal other elements

### Section Divider
- Large centered text (section name)
- Accent bar or shape
- Acts as visual pause between acts

### CTA / Closing Slide
- Clear call-to-action title
- Supporting points as short bullets
- Optional contact info or next-steps timeline
- Accent color used for emphasis

## HTML Output Format

Every generated slide follows this structure:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=1280">
    <style>
        /* CSS reset */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: var(--bg); font-family: var(--font-body); }

        /* Theme variables (injected from active theme) */
        :root {
            --bg: #0A0A0F;
            --surface: #13091D;
            --primary: #A100FF;
            /* ... all theme variables ... */
        }

        /* Slide container */
        .slide {
            width: 1280px; height: 720px;
            position: relative; overflow: hidden;
            background: var(--bg);
        }

        /* Slide-type-specific styles */
        /* ... */
    </style>
</head>
<body>
    <div class="slide {slide-type}">
        <!-- Slide content -->
    </div>
</body>
</html>
```

### Key HTML Requirements

1. **Self-contained** — All styles inline or in `<style>` tags. No external
   CSS or JS. No CDN dependencies.

2. **Fixed viewport** — `<meta name="viewport" content="width=1280">` ensures
   Chrome headless renders at the correct width.

3. **`.slide` wrapper** — Required by chrome-extract. Must have explicit
   `width: 1280px; height: 720px; position: relative; overflow: hidden;`.

4. **Semantic elements** — Use `h1`, `h2`, `h3`, `p` for text content.
   chrome-extract performs richtext extraction on these elements.

5. **No animations** — standardize strips them anyway. Don't add them.

6. **Theme as resolved values** — CSS custom properties are resolved to actual
   hex values in the output HTML for maximum compatibility with headless Chrome.

## Design Principles Applied

Slide generation follows design-ref principles automatically:

- **Color weight**: Background dominates (60-70%), primary/secondary for headings
  and accents (20-30%), accent sparingly (5-10%)
- **Typography hierarchy**: Title > subtitle > body > caption, using theme sizes
- **Margins**: 48px minimum from all edges (respects layout.content_start_x/y)
- **Whitespace**: Target 30%+ empty space per slide
- **Element count**: Max 6-7 top-level visual elements per slide
- **One message per slide**: Title is an assertion, body supports it
- **Contrast**: All text meets WCAG AA against its background

## Speaker Notes

When the outline includes `notes` for a slide, they are embedded as a hidden
`<div class="speaker-notes">` sibling to the `.slide` div:

```html
<div class="slide content">
    ...
</div>
<div class="speaker-notes" style="display:none">Frame the problem before presenting the solution</div>
```

Press **N** when viewing the HTML to toggle the notes panel. The pipeline reads
`.speaker-notes` and adds them as PowerPoint speaker notes. Notes are extracted
before triage/prep so they survive into the final PPTX.

## Section Dividers

By default, generate auto-inserts a **section divider slide** between
acts (starting from the second act). This creates visual breaks that signal
topic transitions in the deck.

The divider uses the act's `name` as the slide title and renders with the
`section` slide type. Dividers are skipped if:
- The act already starts with a `type: "section"` or `type: "title"` slide
- The outline sets `"auto_dividers": false`
- The act has no name

Auto-generated dividers are marked with `"auto_generated": true` in the manifest
so they can be identified and removed if not wanted.

## Naming Convention

Generated files use a **numbered slug** pattern derived from the slide title:

```
01-ai-powered-analytics.html      (title slide)
02-decision-speed-is-our-advantage.html  (content slide)
03-ai-reduced-latency-by-60.html  (stats slide)
```

The numeric prefix sets the default filesystem sort order. The slug makes each
file identifiable without opening it. Slugs are kebab-case, max 40 chars,
with duplicates disambiguated (`-2`, `-3`, etc.).

### Reordering Slides

To reorder slides, edit the `order` field in `slides.json` — do NOT rename
files. The manifest defines the canonical deck order. The numeric prefix in
filenames reflects the original generation order, not the presentation order.

A manifest file `slides.json` is generated alongside the HTML files:

```json
[
  {"file": "01-ai-powered-analytics.html", "order": 1, "slug": "ai-powered-analytics", "type": "title", "title": "AI-Powered Analytics", "act": "Setup"},
  {"file": "02-decision-speed-is-our-advantage.html", "order": 2, "slug": "decision-speed-is-our-advantage", "type": "content", "title": "Decision speed is our advantage", "act": "Setup"},
  {"file": "03-ai-reduced-latency-by-60.html", "order": 3, "slug": "ai-reduced-latency-by-60", "type": "stats", "title": "AI reduced latency by 60%", "act": "Evidence"}
]
```

This manifest is consumed by quick-convert for slide ordering and metadata.
To reorder: change `order` values in `slides.json`. To remove a slide: delete
its entry. To add a slide: create the HTML file and add a manifest entry.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Text too small in PPTX | Font sizes below design minimums | Check theme sizes; title >= 36px, body >= 18px |
| Colors don't match theme | CSS variables not resolved | Verify theme CSS is injected with actual hex values |
| Layout shifted in PPTX | Viewport mismatch | Ensure `--viewport` matches theme's layout dimensions |
| Too many elements on slide | Outline has too much content per slide | Split in the outline phase; max 6-7 elements |
| Cards overlap | Grid layout too tight | Increase gap between cards; check card padding |
| Missing speaker notes | No `notes` field in outline | Add notes to outline JSON before generating |

## Reference Files

Read these on demand — do not load all at once.

| File | Read when... |
|---|---|
| [templates.md](references/templates.md) | Slide template definitions, zone schemas, and selection logic |
| [image-sourcing.md](references/image-sourcing.md) | Image modes (Unsplash/icons/none), attribution rules, placement strategies |
| [css-constraints.md](references/css-constraints.md) | Definitive CSS contract with chrome-extract: centering rules, card flex, badges, forbidden patterns |
| [html-template.md](references/html-template.md) | Canonical HTML slide template, CSS variables, notes-data.js format, component variations |

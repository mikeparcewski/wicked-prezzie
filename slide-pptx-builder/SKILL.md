---
name: PPTX Slide Builder
description: >
  Converts extracted layout JSON into native PPTX shapes, richtext boxes, and
  images at pixel-accurate positions. Use this skill when the PPTX output has
  visual problems — text overlapping, wrong positions, shapes invisible, text
  overflowing cards, headings wrapping differently than HTML, SVG charts missing,
  wrong background colors, or colors that look wrong (too dark, too bright,
  alpha blending issues). This skill owns the full rendering pipeline including
  bundled color_utils.py for CSS-to-PPTX color translation. Also use when adjusting fonts,
  text width, margins, or the coordinate mapping between Chrome pixels and PPTX
  EMU units. If the extraction looks correct (check chrome-extract) but the PPTX
  still looks wrong, the issue is here. Consult slide-design for design
  principles and quality rubric.
---

# PPTX Slide Builder

Converts extracted layout JSON into native PowerPoint slides with shapes,
richtext boxes, and embedded images at pixel-accurate positions.

## When to Use

- Debugging layout issues in generated PPTX (overlapping text, wrong positions)
- Adjusting how specific element types render (shapes, richtext, SVGs)
- Fixing text width/clamping behavior inside cards
- Modifying font, color, or alignment handling

## Core Class: `SlideBuilder`

### Constructor

```python
SlideBuilder(slide_w_inches=13.333, slide_h_inches=7.5,
             source_w=1280, source_h=720, font="Calibri")
```

Widescreen 16:9 by default. Source dimensions must match the Chrome viewport
used during extraction.

### `build_slide(prs, layout_data, screenshot_fn, notes_text)`

Builds a single slide from layout JSON. Rendering order:

1. **Background** — Solid fill from `slideBg`, with class-based overrides
   for `section-divider` and `title-slide`
2. **Shapes** — Background/border elements sorted by DOM depth (deepest last).
   Filters out full-slide shapes and tiny elements. Supports rounded rectangles.
3. **SVG images** — Large SVGs (>60px, >10 lines) rendered via `screenshot_fn`
   callback as cropped PNGs
4. **Richtext** — `h1`-`h4`/`p`/`li` elements with inline run formatting.
   Each run preserves its own color, size, weight, style
5. **Simple text** — Leaf text nodes not covered by richtext
6. **Speaker notes** — Added to the notes slide

### Text Positioning Logic

**Card text clamping**: Text inside a card shape uses the card's full width
(minus 4px padding each side), not Chrome's tight bounding box. This prevents
text overflow since PPTX renders Calibri wider than CSS renders the web font.

**Centered headings**: `h1`/`h2`/`h3` with `text-align: center` get full-width
text boxes (48px margin each side) rather than the tight Chrome rect.

**Width multiplier**: Non-card headings get 1.15x width, other text gets 1.08x,
compensating for CSS-to-Calibri font metric differences.

## Script Location

`scripts/pptx_builder.py` — imported by `slide-html-to-pptx` skill.
`scripts/color_utils.py` — bundled CSS color parsing, alpha blending, entity decoding.

## Coordinate System

Layout JSON uses pixel coordinates in the HTML viewport space (default 1280x720).
`px2emu_x` / `px2emu_y` convert to PPTX EMU units:

```
EMU_x = px / source_w * slide_w_inches * 914400
```

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Text overlaps other text | Duplicate text extraction (richtext + simple) | Check `is_covered_by_richtext` filtering |
| Text overflows card | Card text clamping not matching | Adjust `find_parent_card` tolerance (currently 5px/30px) |
| Headings wrap differently | CSS vs Calibri font metrics | Increase width multiplier (1.15x) |
| Shapes invisible | Fill color is transparent/None | Check `parse_css_color` return and alpha threshold |
| Wrong background color | Slide class not detected | Verify `slideClasses` in layout JSON |

## Additional Resources

### Reference Files

For detailed implementation specifics, consult:
- **`references/coordinate-system.md`** — EMU conversion math, width multiplier rationale
- **`references/text-clamping.md`** — Card text clamping algorithm, tolerance values

### Related Skills

- **slide-design** — Design principles and quality rubric for evaluating output
- **`scripts/color_utils.py`** — Bundled CSS color parsing and alpha blending logic

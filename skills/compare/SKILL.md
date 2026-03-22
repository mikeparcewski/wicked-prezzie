---
name: compare
description: |
  Side-by-side visual comparison of HTML source slides vs converted PPTX output.
  Also use proactively after any conversion.

  Use when: "does it look right", "how close is it", "check fidelity", "visual diff",
  "compare HTML vs PPTX", "conversion quality", "does the PPTX match"
---

# Slide Visual Comparison

Compare original HTML slides against the converted PPTX output by rendering
both to PNG and visually inspecting them. No script — use chrome-extract and
slide-render directly.

## When to Use

- After HTML-to-PPTX conversion to verify output quality
- When debugging specific slides that look wrong
- To compare a subset of slides for targeted review

## How to Compare

### 1. Screenshot the HTML source

```bash
python skills/chrome-extract/scripts/chrome_extract.py \
  --screenshot slides/slide-01.html \
  --output ~/.something-wicked/wicked-prezzie/output/html/slide-01.png
```

### 2. Render the PPTX

```bash
python skills/slide-render/scripts/slide_render.py deck.pptx \
  -o ~/.something-wicked/wicked-prezzie/output/renders/
```

### 3. Read both images

Use the Read tool to view the HTML screenshot and the corresponding PPTX render.
Compare visually using the grading criteria in slide-pipeline.

## What to Look For

- **Missing elements** — cards, backgrounds, icons present in HTML but absent in PPTX
- **Text issues** — concatenation, missing line breaks, wrong spacing
- **Color shifts** — backgrounds missing or wrong color
- **Layout shifts** — elements present but in wrong position or size

## What to Ignore

- CSS→Calibri font metric differences
- Sub-pixel alignment
- Gradients rendered as solid colors
- Stripped animations/transitions

## Dependencies

- Google Chrome (for HTML screenshots)
- LibreOffice (for PPTX→PDF→PNG rendering)
- `pdftoppm` from poppler

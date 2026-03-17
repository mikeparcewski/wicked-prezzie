---
name: HTML to PowerPoint
description: >
  The conversion stage that batch-converts HTML slide files into editable
  PowerPoint (.pptx) with native shapes, formatted text, and accurate
  positioning. This is a single pipeline stage, not the full workflow — for
  end-to-end conversion (standardize + convert + validate + render + compare),
  use slide-pipeline instead. Use this skill only when the user explicitly wants
  just the conversion step without QA, when debugging conversion-specific issues
  (fallback slides, extraction failures, manifest ordering), or when called as
  part of a manual multi-step workflow. If the user says "just convert, skip
  validation" or "re-convert slide 5 only", use this. For general "make me a
  PowerPoint" requests, prefer slide-pipeline.
---

# HTML to PowerPoint Conversion

Convert HTML slide decks into editable PowerPoint files with native shapes,
formatted text, and accurate positioning. The conversion preserves layout
fidelity by using Chrome headless to extract computed positions from rendered HTML.

## When to Use

- Converting a directory of HTML slide files into a single .pptx deck
- Re-generating a PowerPoint after HTML slides have been edited
- Building a deck from a subset of slides via manifest or file list

## Architecture

The pipeline has three stages:

1. **Chrome headless extraction** — Renders each HTML file, injects JavaScript
   to walk the DOM, and captures computed bounding boxes, colors, fonts, and
   inline formatting as structured JSON.
2. **Layout-to-PPTX mapping** — `SlideBuilder` converts the JSON layout into
   native python-pptx shapes, richtext boxes, and embedded SVG screenshots at
   exact pixel-mapped positions.
3. **Fallback** — If extraction fails for a slide, a full-page screenshot is
   placed as an image on the slide instead.

## Usage

Run the conversion script at `scripts/html_to_pptx.py`:

```bash
# Convert all HTML files in a directory
python slide-html-to-pptx/scripts/html_to_pptx.py --input-dir ./slides --output deck.pptx

# Convert specific slides
python slide-html-to-pptx/scripts/html_to_pptx.py --slides slide-01.html,slide-02.html --output deck.pptx

# Use a JSON manifest for ordering and metadata
python slide-html-to-pptx/scripts/html_to_pptx.py --manifest slides.json --output deck.pptx
```

### Manifest Format

A JSON array where each entry has at least a `file` key:

```json
[
  {"file": "slide-01.html", "title": "Title Slide", "act": "Intro"},
  {"file": "slide-02.html", "title": "Hook Statement", "act": "Intro"}
]
```

### Options

| Flag | Default | Purpose |
|---|---|---|
| `--input-dir`, `-d` | `.` | Directory containing HTML slide files |
| `--output`, `-o` | `deck.pptx` | Output .pptx path |
| `--slides`, `-s` | (all) | Comma-separated HTML filenames |
| `--manifest`, `-m` | (none) | JSON manifest with slide ordering |
| `--hide` | `.slide-nav` | CSS selectors to hide during extraction |
| `--viewport` | `1280x720` | Browser viewport dimensions |

## Key Behaviors

- **Richtext preservation** — Headings and paragraphs retain inline formatting
  (mixed colors, bold spans within one element). Each `<h1>`/`<h2>`/`<h3>`/`<p>`
  becomes a single text box with multiple formatted runs.
- **Alpha blending** — CSS `rgba()` colors are pre-blended against the slide
  background. PPTX does not support CSS-style transparency on shape fills, so
  `rgba(161,0,255,0.06)` on a dark background becomes `#13091D`.
- **Card text clamping** — Text inside card shapes uses the card's full width,
  not Chrome's tight bounding box, preventing text overflow in PPTX.
- **SVG charts** — Large SVGs (>60px) are rendered as cropped screenshot images.
  Small decorative SVGs are skipped to avoid capturing surrounding text.
- **Speaker notes** — Extracted body text from each HTML file is added as
  speaker notes. If the manifest includes an `act` field, it prefixes the notes.

## Dependencies

Verify before running:

- `python-pptx`, `beautifulsoup4`, `lxml`, `Pillow` (pip packages)
- Google Chrome installed at `/Applications/Google Chrome.app` or set `CHROME_PATH`

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| All slides show `[fallback]` | Chrome not found | Set `CHROME_PATH` env var |
| Text overlaps in PPTX | Inline spans extracted as separate boxes | Verify richtext extraction is active (h1-h3, p tags) |
| Colors look wrong | Alpha blending against wrong background | Check `slideBg` in layout JSON |
| SVG charts missing | SVG too small or too few lines | Lower the 60px / 10-line thresholds in `slide-pptx-builder/scripts/pptx_builder.py` |

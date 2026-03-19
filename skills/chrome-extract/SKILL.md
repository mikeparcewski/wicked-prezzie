---
name: Chrome Layout Extraction
description: >
  Extracts layout data from rendered HTML slides via Chrome headless — bounding
  boxes, colors, fonts, inline formatting. Use when elements are missing or
  mispositioned in the PPTX, when screenshots of HTML slides are needed, when
  debugging extraction issues, or when the conversion looks wrong and you need
  to check whether the problem is in extraction vs PPTX building. Start here
  before checking slide-pptx-builder.
---

# Chrome Layout Extraction

Drives Chrome headless to render HTML slides, injects JavaScript to walk the
DOM, and extracts computed bounding boxes, colors, fonts, and inline formatting
as structured JSON.

## When to Use

- Debugging why elements are missing or mispositioned in extraction
- Adjusting the JavaScript DOM walker for new HTML patterns
- Fixing screenshot or cropping behavior
- Adding support for new element types

## Core Functions

### `extract_layout(html_path, tmpdir, viewport_w, viewport_h, hide_selectors)`

Renders an HTML file in Chrome headless and returns structured layout JSON:

```json
{
  "slideWidth": 1280, "slideHeight": 720,
  "slideClasses": ["slide", "section-divider"],
  "slideBg": "rgb(10, 10, 15)",
  "elements": [
    {"type": "shape", "tag": "div", "rect": {"x":0,"y":0,"w":400,"h":200}, "styles": {...}},
    {"type": "richtext", "tag": "h1", "rect": {...}, "runs": [...], "styles": {...}},
    {"type": "richtext", "tag": "span", "rect": {...}, "runs": [...], "styles": {...}}
  ],
  "svgElements": [
    {"type": "svg", "rect": {"x":100,"y":200,"w":600,"h":300}, "lines": 45}
  ]
}
```

**Element types**:
- `shape` — Elements with background color or border (cards, containers)
- `richtext` — All text elements with inline run formatting (headings, paragraphs, and leaf tags like `span`, `a`, `div`)
- `badge` — Small rounded elements with background fill (pills, chips, tags)
- `table` — Native HTML tables with per-cell run formatting
- `svg` — SVG elements with bounding rects

**How it works**: Injects CSS to hide specified selectors, injects the
`JS_EXTRACT` script that runs on page load, uses `--dump-dom` to capture the
output, then parses the JSON from a hidden `<pre>` element.

### `screenshot_html(html_path, png_path, tmpdir, viewport_w, viewport_h, scale_factor, hide_selectors)`

Captures a full-page PNG screenshot using Chrome's `--screenshot` flag.
Crops to the target aspect ratio after capture. Uses 2x scale factor for
retina quality by default.

### `crop_region(full_png_path, out_path, region_rect, source_w, source_h)`

Crops a region from a full screenshot. Used to extract SVG chart areas
as individual images for embedding in PPTX.

## Script Location

`scripts/chrome_extract.py` — imported by `slide-html-to-pptx` and `slide-compare` skills.

## Environment

Chrome path defaults to macOS location. Override with `CHROME_PATH` env var:

```bash
export CHROME_PATH="/usr/bin/google-chrome"
```

## JavaScript DOM Walker

The `JS_EXTRACT` constant in the script contains the injected JavaScript.
Key behaviors:

- Walks from `.slide` element (or `body` fallback)
- Coordinates are relative to the slide container, scaled to source dimensions
- All text elements use unified richtext extraction with per-run formatting
  (color, fontSize, fontWeight, fontStyle) — handles `<br>`, block children,
  and inline spans uniformly
- Elements inside richtext parents are excluded from deeper extraction to
  prevent duplicates
- SVGs are collected separately with line counts (used for size filtering)
- Max depth of 15 to avoid infinite recursion
- Skips `script`, `style`, `nav`, and invisible elements

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Empty layout / null return | Chrome not found or crash | Check `CHROME_PATH`, verify Chrome installed |
| Elements missing | Hidden by CSS or too small | Adjust size thresholds in JS (currently 1px visible minimum) |
| Wrong positions | Viewport mismatch | Ensure `viewport_w`/`viewport_h` match HTML design dimensions |
| JSON parse error | HTML entities in dump-dom output | Already handled by `html.unescape()` — check for new edge cases |

## Additional Resources

### Reference Files

- **`references/js-dom-walker.md`** — Detailed documentation of the JS_EXTRACT logic,
  element classification rules, coordinate system, size filters, and depth limits

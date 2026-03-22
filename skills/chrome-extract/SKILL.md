---
name: chrome-extract
description: |
  Extracts layout data from rendered HTML slides via Chrome headless — bounding
  boxes, colors, fonts, inline formatting. Start here before checking
  slide-pptx-builder when the conversion looks wrong.

  Use when: "elements missing", "wrong position", "extraction issue", "screenshot HTML",
  "debug extraction", "check extraction vs builder", "bounding boxes wrong"
---

# Chrome Layout Extraction

Drives Chrome headless to render HTML slides, injects JavaScript to walk the
DOM, and extracts **raw facts** — bounding boxes, computed styles, text runs,
and structural metadata. No classification decisions are made by the script.

## Two-Step Architecture

### Step 1: `extract_layout()` — Raw Facts from Chrome

Walks every visible DOM element and emits:
- `tag`, `classes`, `rect` (bounding box), `depth`
- `styles` (all computed CSS properties)
- `directText` (text nodes owned by this element, not children)
- `runs` (inline-formatted text with per-run color/font — only on true leaves)
- `hasBg`, `hasBorder`, `childElementCount`, `rotation`

No `type` field. No classification. Just browser-computed facts.

### Step 2: `classify_elements()` — Default Classification

Converts raw nodes into typed elements the builder expects:
- Nodes with `runs` → `type: 'richtext'`
- Nodes with `hasBg`/`hasBorder` and no text → `type: 'shape'`
- Tables → `type: 'table'`

This is the **deterministic default** for the 90% case. The model can override
any classification by looking at the HTML screenshot and the raw element list.

### When the Model Should Override

After the initial conversion, if a slide looks wrong, read the raw extraction
JSON. Common overrides:
- Element classified as richtext but it's a container → skip it
- Element classified as shape but it should have text → promote to richtext
- Element missing because it's a pseudo-element → adjust pseudo capture

## Core Functions

### `extract_layout(html_path, tmpdir, viewport_w, viewport_h, hide_selectors)`

Returns raw element tree:
```json
{
  "slideWidth": 1280, "slideHeight": 720,
  "slideBg": "rgb(10, 10, 15)",
  "elements": [
    {"tag": "div", "rect": {...}, "styles": {...}, "hasBg": true, "childElementCount": 3, "depth": 0},
    {"tag": "h1", "rect": {...}, "styles": {...}, "directText": "Title", "runs": [...], "depth": 1}
  ],
  "svgElements": [{"type": "svg", "rect": {...}, "lines": 45}]
}
```

### `classify_elements(raw_data)`

Applies default classification. Returns data in the format `pptx_builder` expects.

### `screenshot_html(html_path, png_path, ...)`

Full-page PNG screenshot via Chrome's `--screenshot` flag.

### `crop_region(full_png_path, out_path, region_rect, ...)`

Crop a region from a screenshot. Used for SVG chart extraction.

## Script Location

`scripts/chrome_extract.py` — imported by `slide-html-to-pptx`.

## Environment

Chrome path defaults to macOS location. Override with `CHROME_PATH` env var.

## JavaScript DOM Walker

The `JS_EXTRACT` constant walks every visible element and collects facts.
Key behaviors:

- Walks from `.slide` element (or `body` fallback)
- Coordinates relative to slide container, scaled to source dimensions
- `getRuns()` extracts inline-formatted text with per-run styles
- Only called on true leaf elements (no child elements)
- Tables extracted with full row/cell structure
- SVGs collected separately with line counts
- Pseudo-elements captured with geometry
- Max depth 15, skips script/style/nav/invisible

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Empty layout / null return | Chrome not found | Check `CHROME_PATH` |
| Elements missing | Hidden or too small | Check visibility and 1px minimum |
| Wrong positions | Viewport mismatch | Match `viewport_w`/`viewport_h` to HTML |

## Reference Files

- **`references/js-dom-walker.md`** — DOM walker details, coordinate system, depth limits

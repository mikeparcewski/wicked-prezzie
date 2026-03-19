# JavaScript DOM Walker (JS_EXTRACT)

## Overview

The `JS_EXTRACT` constant in `chrome_extract.py` is JavaScript that runs inside
Chrome headless after page load. It walks the DOM tree from the `.slide` element
and extracts computed positions, colors, fonts, and inline formatting.

## Element Classification

### Richtext Elements (all text)

All text elements — both block-level (`h1`-`h4`, `p`, `li`) and leaf-level
(`span`, `a`, `div`, `label`, etc.) — use unified `getRuns()` extraction.
Each child text node preserves its own color, fontSize, fontWeight, fontStyle,
and textTransform. `<br>` elements and block-level children produce line breaks.

This prevents the "Go Faster" overlap bug where inline-styled spans would
become separate text boxes, and fixes text concatenation bugs where `<br>`
or block children were dropped by the old simple-text path.

Once an element is classified as richtext, all its descendants are added to
`richTextEls` set and excluded from further extraction.

### Badge Elements (small rounded with background)

Leaf tags with a visible background and border-radius are extracted as badges
with their `textContent` rather than individual runs.

### Shape Elements

Any element with a non-transparent background color OR visible border
(width > 0.5px, non-transparent color). Excludes `body` and `html` tags.

### SVG Elements

Collected separately with bounding rect and line count. Used for size-based
filtering (skip small decorative SVGs, render large charts as images).

## Coordinate System

All coordinates are relative to the `.slide` element, not the viewport:

```javascript
function relRect(el) {
    var r = el.getBoundingClientRect();
    return {
        x: (r.left - slideRect.left) * scaleX,
        y: (r.top - slideRect.top) * scaleY,
        w: r.width * scaleX,
        h: r.height * scaleY
    };
}
```

Scale factors normalize coordinates to the slide's natural dimensions
(typically 1280x720), regardless of browser zoom or DPI.

## Size Filters

| Element Type | Minimum Size | Rationale |
|---|---|---|
| Visibility check | 1x1 px | Skip invisible elements |
| Richtext (block) | 5x3 px | Skip empty headings |
| Richtext (leaf) | 3x3 px | Skip spacer elements |
| Shapes | 8x4 px | Skip hairline dividers |
| SVGs | 20x20 px | Skip tiny icon SVGs |

## Depth Limit

Maximum recursion depth: 15 levels. This prevents infinite loops in
deeply nested DOM structures while covering all practical slide layouts.

## Skipped Elements

The walker skips: `script`, `style`, `nav`, `svg` (handled separately),
elements inside `svg`, elements with `display: none`, `visibility: hidden`,
or `opacity: 0`.

## Output Format

The walker writes JSON to a hidden `<pre id="__layout_output__">` element,
which Chrome's `--dump-dom` captures in its output. The Python side extracts
this JSON via regex and `html.unescape()` (required because `--dump-dom`
HTML-encodes the content).

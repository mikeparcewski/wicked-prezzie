---
name: prep
description: |
  Consumes triage findings and produces a fully-resolved build manifest.
  High-confidence elements are auto-resolved by applying known-pattern geometry
  transforms. Flagged elements (confidence < 0.85) are model-resolved by
  reading the HTML screenshot. The manifest is the complete, unambiguous
  instruction set for the PPTX builder — no classification logic at build time.

  Use when: "manifest issue", "prep failed", "geometry wrong", "auto-resolve problem",
  "flagged element", "build manifest", "debug prep stage"
user-invocable: false
---

# Slide Prep

Converts triage findings into a build manifest. The manifest is the contract
between model judgment and mechanical builder execution. After prep completes,
no element has an ambiguous type or unresolved geometry.

## When to Use

- Automatically invoked by `html_to_pptx.py` after triage, before build.
- Manually when a slide's manifest needs model-resolution of flagged elements.
- When editing a manifest to fix a build error (direct override path).

## Input / Output Contract

**Inputs**:
- `findings.json` — output from `slide-triage` (or `triage_slide()`)
- `classified_layout` — `classify_elements()` output dict
- HTML screenshot PNG (for model inspection of flagged elements)

**Outputs**:
- `manifest.json` written to `{slide_tmpdir}/manifest.json`
- Returns the manifest dict directly from `auto_resolve()`

## Build Manifest Schema

```json
{
  "schemaVersion": 1,
  "slideIndex": 0,
  "sourceFile": "slide-01.html",
  "slideBg": "#0A0A0F",
  "slideWidthPx": 1280,
  "slideHeightPx": 720,
  "complexity": "low",
  "triageFlags": ["PATTERN-002", "PATTERN-004"],
  "elements": [ ],
  "svgElements": [ ],
  "notes": "speaker notes text"
}
```

### Per-Element Entry (fully resolved)

Every element in `elements` is fully resolved before the builder runs.
No field is ambiguous at build time.

```json
{
  "manifestId": "e-004",
  "type": "richtext",

  "rect": {
    "x": 120, "y": 200, "w": 480, "h": 32
  },

  "resolvedRect": {
    "x": 124, "y": 200, "w": 472, "h": 32,
    "source": "card_clamp",
    "note": "clamped to parent card e-003 (480px wide)"
  },

  "styles": {
    "textAlign": "left",
    "paddingTop": 0, "paddingRight": 8, "paddingBottom": 0, "paddingLeft": 8,
    "whiteSpace": "normal",
    "letterSpacing": "normal"
  },

  "runs": [
    {
      "text": "Revenue Growth",
      "color": "#FFFFFF",
      "fontSize": 24,
      "fontWeight": "700",
      "fontStyle": "normal",
      "textTransform": "",
      "br": false
    }
  ],

  "rotation": 0,
  "tag": "h3",
  "depth": 4,

  "classificationSource": "auto",
  "confidence": 0.95,
  "flagReason": null,
  "patternMatched": "PATTERN-004",
  "skipRender": false
}
```

### Per-SVG Entry (fully resolved)

```json
{
  "manifestId": "svg-001",
  "type": "svg_image",
  "rect": { "x": 800, "y": 80, "w": 440, "h": 380 },
  "resolvedRect": {
    "x": 800, "y": 80, "w": 440, "h": 352,
    "source": "svg_bottom_clamp",
    "note": "nearest element below at y=440, cropped 28px"
  },
  "svgIndex": 0,
  "lines": 87,
  "skipRender": false,
  "classificationSource": "auto",
  "confidence": 1.0,
  "flagReason": null
}
```

### Element Types

| `type` | Builder action |
|---|---|
| `richtext` | `add_textbox` with runs, rotation, margins |
| `shape` | `add_shape` with fill, border, gradient |
| `accent_bar` | `add_shape(RECTANGLE)` — thin left-border bar |
| `badge` | `add_shape(ROUNDED_RECTANGLE)` with 50% radius, optional text |
| `table` | `add_table` with cell fills and runs |
| `svg_image` | `add_picture` from pre-rendered PNG via screenshot callback |
| `skip` | No action taken — `skipRender: true` |

### `classificationSource` Values

| Value | Meaning |
|---|---|
| `auto` | `classify_elements()` default, confidence >= 0.85 |
| `pattern` | Matched a known pattern — geometry transform applied |
| `model` | Model resolved from screenshot inspection |
| `override` | Explicit model correction of a prior `auto` result |

### `resolvedRect` — Override Geometry

When prep changes element geometry from what Chrome reported, the original `rect`
is preserved and `resolvedRect` carries the adjusted values. The builder always
uses `resolvedRect` when present, falls back to `rect`.

`resolvedRect.source` records the reason:
- `card_clamp` — width clamped to parent card bounds (PATTERN-004)
- `rotation_swap` — width/height swapped for rotated element (PATTERN-003)
- `svg_bottom_clamp` — SVG height reduced to prevent crop bleed (PATTERN-001)
- `obstacle_dodge` — x shifted right past overlapping badge/icon (PATTERN-005)
- `model` — model-specified geometry from screenshot inspection

## Auto-Resolution Path (confidence >= 0.85)

For each element with `confidence >= 0.85` and no `collisionRisk`:

1. Copy the element from classified layout into the manifest.
2. Set `classificationSource = "auto"`.
3. If `patternMatched` is set, apply the geometry transform from
   `known-patterns.md` and set `classificationSource = "pattern"`.
4. Set `skipRender = false` (or `true` for skip-type patterns).
5. Add to manifest `elements` list.

## Pattern Geometry Transforms

Apply these transforms when `patternMatched` is set:

### PATTERN-001 (SVG Crop Bleed)
Apply to SVG elements in `svgElements`:
- Set `resolvedRect.h = nearestBelowY - rect.y - 8`
- Only if `new_h > rect.h * 0.5` AND `new_h < rect.h`
- Set `resolvedRect.source = "svg_bottom_clamp"`

### PATTERN-002 (Left-Border Accent Bar)
Emit two elements from one source:
1. Original shape with `borderLeftWidth = 0` in styles (no left border)
2. New accent_bar element: `x = shape.x`, `y = shape.y`,
   `w = max(3, min(borderLeftWidth, 6))`, `h = shape.h`,
   `fill = borderLeftColor`, `manifestId = "{original_id}-accent"`

### PATTERN-003 (Rotated Text)
- Set `resolvedRect.w = rect.h`, `resolvedRect.h = rect.w` (swap)
- Set `resolvedRect.source = "rotation_swap"`
- Preserve `rotation` field on element

### PATTERN-004 (Card Text Width Overflow)
Find the tightest parent card shape that contains this richtext element.
- If `text.x > card.x + 24` (text inset past badge/icon):
  - `resolvedRect.x = text.x`
  - `resolvedRect.w = min(card.w - (text.x - card.x), text.w * 1.03)`
- Else:
  - `resolvedRect.x = card.x + 4`
  - `resolvedRect.w = card.w - 8`
- Enforce `resolvedRect.w <= card.w` (hard ceiling)
- Set `resolvedRect.source = "card_clamp"`

### PATTERN-005 (Badge/Icon Obstacle Collision)
For the richtext element overlapping a badge:
- `resolvedRect.x = obstacle.x + obstacle.w + 4`
- `resolvedRect.w = rect.w - (new_x - rect.x)`
- Skip if `new_w < 20` OR `textAlign == "center"`
- Set `resolvedRect.source = "obstacle_dodge"`

### PATTERN-006 (Small Decorative Emoji Skip)
- Set `type = "skip"`, `skipRender = true`
- Set `classificationSource = "pattern"`

### PATTERN-007 (Full-Slide Background Shape)
- Set `type = "skip"`, `skipRender = true`

### PATTERN-008 (Tiny Shape Noise)
- Set `type = "skip"`, `skipRender = true`

### PATTERN-009 (Out-of-Bounds Element)
- Set `type = "skip"`, `skipRender = true`

### PATTERN-010 (Duplicate Text from Container + Leaf)
- Set lower-depth element to `type = "skip"`, `skipRender = true`
- Keep higher-depth element (leaf) as-is

## Model-Resolution Path (confidence < 0.85 or collisionRisk set)

For each flagged element in `findings.elements` where `confidence < 0.85` or
`collisionRisk` is non-null:

1. Locate the element in the HTML screenshot by its `rect` coordinates.
2. Decide:
   - **Correct type?** Check what the element visually is vs. the `defaultType`.
   - **Correct geometry?** Does the rect match what's visible?
   - **Should it be skipped?** Is it a container whose children handle the content?
3. Set `classificationSource = "model"`.
4. Record your reasoning in `flagReason` (replace the triage reason with your conclusion).
5. Update `type`, `rect`, or `resolvedRect` as needed.

When inspecting the screenshot, use the element's `rect` (x, y, w, h) in slide
pixel coordinates (1280x720 space) to locate the element. The screenshot is
captured at 2x scale — multiply coordinates by 2 for pixel position in the PNG.

**Batch all flagged elements for one slide in a single model call.** Read the
screenshot once, then resolve all flagged elements together before writing the
manifest.

## Manifest Validation Checklist

Before writing the manifest file, assert:

1. Every element has exactly one `type` from the allowed set:
   `richtext`, `shape`, `accent_bar`, `badge`, `table`, `svg_image`, `skip`
2. Every element with `confidence < 0.60` has either:
   - `classificationSource = "model"` (model-resolved), OR
   - `skipRender = true`
3. No two elements share the same `manifestId`.
4. `resolvedRect`, when present, has a non-empty `source` field.
5. All SVG entries have `svgIndex` set to their 0-based index in
   `classified_layout.svgElements`.

If any assertion fails, resolve the element via the model-resolution path
before writing the manifest.

## Builder Rendering Order

The builder processes manifest elements in this order (within each type group,
sorted by `depth` ascending — deepest = rendered last = on top):

1. Background (from `manifest.slideBg`)
2. `shape` elements sorted by `depth` ascending
3. `accent_bar` elements (render after parent card shape)
4. `svg_image` elements
5. `table` elements
6. `badge` elements
7. `richtext` elements
8. Speaker notes (from `manifest.notes`)

Elements with `skipRender: true` are always skipped regardless of type.

## Example: Running Prep

```python
from slide_prep import auto_resolve
import json

findings = json.load(open("slide-tmpdir/findings.json"))
classified_layout = json.load(open("slide-tmpdir/classified-layout.json"))

# Auto-resolve high-confidence elements
manifest = auto_resolve(findings, classified_layout)

# Check for unresolved elements (confidence < 0.85, type = None)
unresolved = [e for e in manifest["elements"] if e.get("type") is None]
if unresolved:
    print(f"{len(unresolved)} elements need model resolution:")
    for e in unresolved:
        print(f"  {e['manifestId']}: {e['flagReason']}")
    # Model inspects screenshot and fills in type, classificationSource,
    # and optionally resolvedRect for each unresolved element.
else:
    print("All elements auto-resolved.")

json.dump(manifest, open("slide-tmpdir/manifest.json", "w"), indent=2)
```

## Example: Model-Resolving a Flagged Element

After `auto_resolve()` returns a partial manifest with `type = None` elements,
the model reads the screenshot and updates each unresolved element:

```python
# Model has inspected the screenshot and determined:
# - e-014 (small circle with emoji at x=40, y=160) is a badge, not richtext
# - e-021 (flex container at x=80, y=300) is a skip — children handle content

for e in manifest["elements"]:
    if e["manifestId"] == "e-014":
        e["type"] = "badge"
        e["classificationSource"] = "model"
        e["flagReason"] = "Small circle with emoji — classified as badge after screenshot inspection"
    elif e["manifestId"] == "e-021":
        e["type"] = "skip"
        e["skipRender"] = True
        e["classificationSource"] = "model"
        e["flagReason"] = "Flex container — children e-022 through e-025 handle content"

json.dump(manifest, open("slide-tmpdir/manifest.json", "w"), indent=2)
```

## Reference Files

| File | Read when... |
|---|---|
| [../slide-triage/references/known-patterns.md](../slide-triage/references/known-patterns.md) | Pattern treatment rules and geometry transforms |
| [../slide-pptx-builder/references/coordinate-system.md](../slide-pptx-builder/references/coordinate-system.md) | EMU conversion math |
| [../slide-pptx-builder/references/text-clamping.md](../slide-pptx-builder/references/text-clamping.md) | Card text clamping details |

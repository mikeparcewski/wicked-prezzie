---
name: slide-triage
description: |
  Reads raw extraction JSON + HTML screenshot for one slide. Scores element
  confidence, detects collision risks, checks known patterns, and emits a
  findings JSON. Pure analysis — does not modify elements or produce PPTX.
  Run immediately after chrome_extract.extract_layout() as part of the
  pipeline extraction phase.

  Use when: "triage results", "confidence scores", "collision detected",
  "debug triage", "why was this flagged", "pattern detection"
user-invocable: false
---

# Slide Triage

Analysis step that scores every extracted element and identifies risks before
the build phase. Triage runs once per slide per pipeline attempt and produces
`findings.json` — the input contract for `slide-prep`.

## When to Use

- Automatically invoked by `html_to_pptx.py` during the extraction phase.
- Manually when inspecting why a slide produced incorrect PPTX output.
- When adding a new pattern to `known-patterns.md` (run triage first to see
  what the current confidence scores are for the affected elements).

## Input / Output Contract

**Inputs**:
- `raw_layout` — raw `extract_layout()` output dict (before `classify_elements()`)
- `classified_layout` — `classify_elements()` output dict (with `confidence`, `flagReason`, `classificationSource`)
- `html_path` — path to the source HTML file (for screenshot cross-reference, optional)

**Outputs**:
- `findings.json` written to `{slide_tmpdir}/findings.json`
- Returns the findings dict directly from `triage_slide()`

## Findings JSON Schema

```json
{
  "schemaVersion": 1,
  "slideIndex": 0,
  "sourceFile": "slide-01.html",
  "complexity": "low",
  "elementCount": 24,
  "flaggedCount": 3,
  "autoResolvedCount": 21,
  "patterns": ["accent_bar", "card_text_clamp"],
  "elements": [
    {
      "rawIndex": 7,
      "manifestId": "e-007",
      "tag": "div",
      "rect": { "x": 120, "y": 200, "w": 480, "h": 32 },
      "defaultType": "richtext",
      "confidence": 0.92,
      "flagReason": null,
      "patternMatched": "PATTERN-004",
      "collisionRisk": null
    },
    {
      "rawIndex": 14,
      "manifestId": "e-014",
      "tag": "div",
      "rect": { "x": 40, "y": 160, "w": 50, "h": 50 },
      "defaultType": "richtext",
      "confidence": 0.62,
      "flagReason": "small emoji-only element adjacent to text — badge or decorative icon unclear",
      "patternMatched": null,
      "collisionRisk": "obstacle_risk"
    }
  ],
  "svgElements": [
    {
      "svgIndex": 0,
      "manifestId": "svg-000",
      "rect": { "x": 800, "y": 80, "w": 440, "h": 410 },
      "lines": 87,
      "collisionRisk": "svg_bottom_near_content",
      "nearestBelowY": 432
    }
  ]
}
```

### Field Definitions

| Field | Type | Description |
|---|---|---|
| `schemaVersion` | int | Always 1 |
| `slideIndex` | int | 0-based slide index in the deck |
| `sourceFile` | string | Original HTML filename |
| `complexity` | `"low"` \| `"high"` | From `<!-- COMPLEXITY: -->` annotation or inferred |
| `elementCount` | int | Total elements in classified layout |
| `flaggedCount` | int | Elements with `confidence < 0.85` |
| `autoResolvedCount` | int | Elements with `confidence >= 0.85` |
| `patterns` | string[] | Pattern IDs matched across all elements |
| `elements[].rawIndex` | int | Index in `classified_layout.elements` |
| `elements[].manifestId` | string | Stable ID for this element (format: `e-{rawIndex:03d}`) |
| `elements[].tag` | string | HTML tag from extraction |
| `elements[].rect` | object | `{x, y, w, h}` in slide pixels |
| `elements[].defaultType` | string | Type from `classify_elements()` |
| `elements[].confidence` | float | Confidence score from `classify_elements()` |
| `elements[].flagReason` | string\|null | Human-readable reason when `confidence < 0.85` |
| `elements[].patternMatched` | string\|null | Pattern ID if a known pattern was detected |
| `elements[].collisionRisk` | string\|null | `"obstacle_risk"`, `"svg_bottom_near_content"`, or null |
| `svgElements[].svgIndex` | int | 0-based SVG index |
| `svgElements[].manifestId` | string | Stable ID (format: `svg-{svgIndex:03d}`) |
| `svgElements[].nearestBelowY` | float\|null | Y coord of nearest non-SVG element below |

## Confidence Scoring

Confidence comes directly from `classify_elements()` — triage reads it from
`classified_layout`. The thresholds for action are:

```
confidence >= 0.85   →  auto-resolved in prep (no model inspection needed)
0.60 <= conf < 0.85  →  flagged for model inspection in prep
confidence < 0.60    →  strong flag; model must inspect; builder skips if unresolved
```

Reference scores:
- `table` tag → 1.0 (structural fact)
- `::pseudo` tag → 0.95 (CSS fact)
- `runs` + leaf (`childElementCount == 0`) → 0.90
- `hasBg` only, no runs → 0.85
- `runs` + block children → 0.70
- `hasBg` + `runs` (dual-emit) → 0.72
- Small emoji-only element → 0.65

## Pattern Detection Rules

For each element, check these patterns (in order). Set `patternMatched` to
the first matching pattern ID:

### PATTERN-001: SVG Crop Bleed
Check `svgElements` (not regular elements). For each SVG:
- `svg.lines >= 3` AND `svg.rect.w >= 30`
- Any non-SVG element has `rect.y` in range `(svg_bottom - 30, svg_bottom + 30]`

Set `collisionRisk = "svg_bottom_near_content"` on the SVG entry.

### PATTERN-002: Left-Border Accent Bar
Check shape elements:
- `styles.borderLeftWidth > 2` AND `styles.borderLeftColor` is non-transparent

Set `patternMatched = "PATTERN-002"`.

### PATTERN-003: Rotated Text
- `element.rotation != 0` AND `abs(element.rotation) >= 5`, OR
- `element.styles.writingMode in ("vertical-rl", "vertical-lr")`

Set `patternMatched = "PATTERN-003"`.

### PATTERN-004: Card Text Width Overflow
For richtext elements:
- A shape element contains it (use containment test from architecture.md)
- Shape is not full-slide (`w < 1250`, `h < 680`)
- Shape area >= 400px²
- Element tag is not `h1`

Set `patternMatched = "PATTERN-004"`.

### PATTERN-005: Badge/Icon Obstacle Collision
Check richtext elements:
- Any badge/circle OR small emoji-only richtext (`w < 60`, `h < 60`) horizontally
  overlaps this element with > 30% vertical overlap

Set `collisionRisk = "obstacle_risk"` on the richtext element.

### PATTERN-006: Small Decorative Emoji Skip
Check richtext elements where all text is emoji/symbol AND `w < 80` AND `h < 80`.
If a PATTERN-005 collision exists for an adjacent richtext:
Set `patternMatched = "PATTERN-006"`.

### PATTERN-007: Full-Slide Background Shape
Shape elements where `w > 1250` AND `h > 680`:
Set `patternMatched = "PATTERN-007"`.

### PATTERN-008: Tiny Shape Noise
Shape elements where `w * h < 16` OR (`w < 2` AND `h < 2`):
Set `patternMatched = "PATTERN-008"`.

### PATTERN-009: Out-of-Bounds Element
Any element where `x > slideWidthPx` OR `y > slideHeightPx` OR
`x + w < 0` OR `y + h < 0`:
Set `patternMatched = "PATTERN-009"`.

### PATTERN-010: Duplicate Text from Container + Leaf
Two richtext elements with > 80% area overlap where one has lower depth
(ancestor): Set `patternMatched = "PATTERN-010"` on the lower-depth element.

## Collision Risk Detection

Two collision risk categories:

**`obstacle_risk`** — A small badge/icon element overlaps a richtext element
at the same Y position. Risk: text box renders on top of badge.
- Small obstacle: `badge`, `circle`, or emoji-only richtext where `w < 60`, `h < 60`
- Overlap check: vertical overlap > 30% of shorter element's height

**`svg_bottom_near_content`** — An SVG's bottom edge is within 30px of a
non-SVG element. Risk: SVG screenshot captures content below the SVG.
- Check: any non-SVG element with `rect.y` in `(svg_bottom, svg_bottom + 30]`

## Complexity Inference

If the HTML file contains `<!-- COMPLEXITY: high -->`, set `complexity = "high"`.
Otherwise, infer from the classified layout:
- `"high"` if: `svgElements.length > 0` OR any element has `rotation != 0`
  OR any element has `styles.writingMode` set OR `flaggedCount > 3`
- `"low"` otherwise

## Example: Running Triage

```python
from slide_triage import triage_slide
import json

raw_layout = json.load(open("slide-tmpdir/raw-layout.json"))
classified_layout = json.load(open("slide-tmpdir/classified-layout.json"))

findings = triage_slide(
    raw_layout=raw_layout,
    classified_layout=classified_layout,
    slide_index=0,
    source_file="slide-01.html",
    slide_width_px=1280,
    slide_height_px=720
)

json.dump(findings, open("slide-tmpdir/findings.json", "w"), indent=2)
print(f"Flagged: {findings['flaggedCount']} / {findings['elementCount']}")
print(f"Patterns: {findings['patterns']}")
```

## Reference Files

| File | Read when... |
|---|---|
| [known-patterns.md](references/known-patterns.md) | Looking up pattern signatures, symptoms, and treatments |

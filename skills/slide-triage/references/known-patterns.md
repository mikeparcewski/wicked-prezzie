# Known Patterns

Documented failure modes in the HTML-to-PPTX conversion pipeline. Each entry
describes how to detect the pattern in raw extraction data (signature), what
goes wrong without handling (symptom), and what the prep step must do to fix
it (treatment).

Pattern IDs are stable — use them in findings JSON `patternMatched` fields
and in treatment log entries.

---

## PATTERN-001: SVG Crop Bleed

**Signature**:
- `svgElements[i].lines >= 3` and `svgElements[i].rect.w >= 30`
- A non-SVG element exists with `rect.y` within 30px below
  `svgElements[i].rect.y + svgElements[i].rect.h`

**Symptom** (without treatment):
- SVG chart screenshot bleeds content from elements below it into the chart
  image boundary. The chart image captures part of the text or shapes that
  sit just below the SVG container.

**Treatment** (prep applies this):
- Compute `nearestBelowY` = smallest `rect.y` among non-SVG elements where
  `rect.y > svgRect.y + svgRect.h * 0.5` and `rect.y <= svgRect.y + svgRect.h + 30`.
- In `resolvedRect`, set `h = nearestBelowY - rect.y - 8`.
- Only apply if `new_h > original_h * 0.5` and `new_h < original_h`.
- Set `resolvedRect.source = "svg_bottom_clamp"`.
- Record `nearestBelowY` in `resolvedRect.note`.

**Source**: Issue #19 / 2026-01-xx

---

## PATTERN-002: Left-Border Accent Bar

**Signature**:
- Element type classified as `shape` (has background)
- `styles.borderLeftWidth > 2` and `styles.borderLeftColor` is a
  non-transparent, non-background color
- Shape area > 200px² (not a tiny decorative element)

**Symptom** (without treatment):
- Left border rendered as a full rectangular outline (stroke) around the card.
  The decorative colored left bar intended as a visual accent appears as a box
  border stroke around the entire shape.

**Treatment** (prep applies this):
- Emit two separate manifest entries from one source element:
  1. The card shape (`type: "shape"`) **without** any border (`borderLeftWidth` ignored)
  2. A new `accent_bar` entry: `x = card.x`, `y = card.y`,
     `w = max(3, min(borderLeftWidth, 6))`, `h = card.h`,
     `fill = borderLeftColor`
- Assign the `accent_bar` entry a new `manifestId` (e.g., append `-accent`).
- Set `classificationSource = "pattern"` on both emitted entries.

**Source**: Issue #25 / 2026-01-xx

---

## PATTERN-003: Rotated Text

**Signature**:
- Element has `rotation != 0` and `abs(rotation) >= 5`, OR
- Element `styles.writingMode` is `"vertical-rl"` or `"vertical-lr"`

**Symptom** (without treatment):
- Rotated elements are dropped (zero-size after conversion) or rendered at
  wrong dimensions. PPTX textboxes define width as the horizontal span
  **before** rotation is applied. Passing web-layout dimensions directly
  results in collapsed or misshapen text.

**Treatment** (prep applies this):
- In `resolvedRect`, swap `w` and `h` from the original `rect`.
- Set `resolvedRect.source = "rotation_swap"`.
- Encode `rotation` in the manifest element (builder applies PPTX rotation
  after placing the shape at the swapped dimensions).

**Source**: Issue #27 / 2026-01-xx

---

## PATTERN-004: Card Text Width Overflow

**Signature**:
- Element type = `richtext` (has runs)
- A `shape` element exists where:
  - `text.x >= shape.x - 5`
  - `text.y >= shape.y - 5`
  - `text.x + text.w <= shape.x + shape.w + 30`
  - `text.y + text.h <= shape.y + shape.h + 10`
- Shape is not full-slide: `shape.w < 1250` and `shape.h < 680`
- Shape area >= 400px²
- Element tag is not `h1`

**Symptom** (without treatment):
- Text inside cards overflows the card's right edge in PPTX. Calibri renders
  ~3–5% wider than web fonts at the same point size, causing text that fit
  in the HTML card to spill past the card boundary in the PPTX slide.

**Treatment** (prep applies this):
- Find the tightest parent card shape using the containment test above.
- Compute `card_left = parentCard.x + 4` and `card_w = parentCard.w - 8`.
- If `text.x > card_left + 20` (text is inset, e.g. after a badge):
  - Set `resolvedRect.x = text.x` (preserve original x)
  - Set `resolvedRect.w = min(card_w - (text.x - card_left), text.w * 1.03)`
- Else:
  - Set `resolvedRect.x = card_left`
  - Set `resolvedRect.w = card_w`
- `resolvedRect.w` must never exceed `parentCard.w` (hard ceiling).
- Set `resolvedRect.source = "card_clamp"`.
- Record parent card `manifestId` in `resolvedRect.note`.

**Source**: Issue #29 bug 7 / 2026-01-xx

---

## PATTERN-005: Badge / Icon Obstacle Collision

**Signature**:
- A `badge` or `circle` element (or small emoji-only richtext element where
  `w < 60` and `h < 60`) horizontally overlaps a `richtext` element
- Vertical overlap between the two elements > 30% of the shorter element's height

**Symptom** (without treatment):
- Stat text or label text renders on top of the badge/icon element.
  Text appears concatenated with or visually obscured by the badge shape.

**Treatment** (prep applies this):
- For the overlapping richtext element:
  - Set `resolvedRect.x = obstacle.x + obstacle.w + 4`
  - Set `resolvedRect.w = original.w - (new_x - original.x)`
- Skip this transform if:
  - `new_w < 20` (resulting width too small)
  - `textAlign == "center"` (centered text should not be nudged)
- Set `resolvedRect.source = "obstacle_dodge"`.
- Record the obstacle element's `manifestId` in `resolvedRect.note`.

**Source**: Issue #38 / 2026-01-xx

---

## PATTERN-006: Small Decorative Emoji Skip

**Signature**:
- Element type defaults to `richtext` (has runs)
- `rect.w < 80` and `rect.h < 80`
- All non-whitespace characters in runs are emoji/symbol (Unicode ranges:
  0x1F300+, 0x2600–0x27BF, 0x2500–0x25FF, and related ranges)
- A PATTERN-005 obstacle collision is present with an adjacent richtext element

**Symptom** (without treatment):
- Small bullet/arrow/emoji icons rendered as text boxes overlapping the
  adjacent label text they were meant to decorate. The icon and the label
  both render in the same position, producing illegible concatenated output.

**Treatment** (prep applies this):
- Set `type = "skip"` (set `skipRender = true` in manifest).
- The adjacent richtext element handles its own layout via PATTERN-005
  obstacle dodging.
- Set `classificationSource = "pattern"`.

**Source**: Issue #38 / 2026-01-xx

---

## PATTERN-007: Full-Slide Background Shape

**Signature**:
- Element type classified as `shape`
- `rect.w > 1250` **and** `rect.h > 680` (effectively full-slide dimensions)

**Symptom** (without treatment):
- A full-slide colored `<div>` creates a rectangle shape that completely covers
  the PPTX slide background. Results in a solid-colored rectangle overlaid on
  the slide background color, hiding all content underneath.

**Treatment** (prep applies this):
- Set `type = "skip"` (`skipRender = true`).
- The slide background color is handled via `manifest.slideBg`.
- Set `classificationSource = "pattern"`.

**Source**: Issue #29 / 2026-01-xx

---

## PATTERN-008: Tiny Shape Noise

**Signature**:
- Element type classified as `shape`
- `rect.w * rect.h < 16` (area under 16px²), OR
- `rect.w < 2` **and** `rect.h < 2`

**Symptom** (without treatment):
- Sub-pixel shapes create invisible noise elements in the PPTX. No visual
  impact but the extra shapes confuse EDL targeting and inflate the element
  count in structural validation.

**Treatment** (prep applies this):
- Set `type = "skip"` (`skipRender = true`).
- Set `classificationSource = "pattern"`.

**Source**: Issue #29 / 2026-01-xx

---

## PATTERN-009: Out-of-Bounds Element

**Signature**:
- `rect.x > slideWidthPx` OR `rect.y > slideHeightPx`
- OR `rect.x + rect.w < 0` OR `rect.y + rect.h < 0`

**Symptom** (without treatment):
- Shape or text appears outside the slide canvas in PPTX. Visible only when
  the slide is zoomed out in PowerPoint. Causes structural validation failures
  in `slide_validate.py`.

**Treatment** (prep applies this):
- Set `type = "skip"` (`skipRender = true`).
- Set `classificationSource = "pattern"`.

**Source**: Issue #17 / 2026-01-xx

---

## PATTERN-010: Duplicate Text from Container + Leaf

**Signature**:
- Two richtext elements with overlapping rects (> 80% overlap by area)
- One has `depth` lower than the other (it is an ancestor of the other)
- Both have non-empty `runs` with similar text content

**Symptom** (without treatment):
- Text appears twice on the slide, one instance slightly offset from the
  other. The ancestor element and its descendant leaf both get rendered as
  separate text boxes with the same (or nearly the same) text.

**Treatment** (prep applies this):
- Keep the element with higher `depth` (the leaf — it has the most precise
  bounding box).
- Set the lower-depth element to `type = "skip"` (`skipRender = true`).
- Set `classificationSource = "pattern"` on the skipped element.

**Source**: Issue #32 / 2026-01-xx

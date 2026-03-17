# Card Text Clamping

## The Problem

Chrome reports tight bounding boxes for centered text — the box wraps exactly
around the rendered text width. But in PPTX, Calibri renders wider than CSS
fonts, so using Chrome's tight width causes text to wrap or overflow.

For text inside card shapes (divs with background color), the text should be
constrained to the card's width, not its own bounding box.

## The Algorithm: `find_parent_card`

For each text element, search all filtered shapes for the tightest enclosing
card that could be its parent container.

### Matching Criteria

A shape is a potential parent card if:
- Text left >= shape left - 5px (tolerance)
- Text top >= shape top - 5px
- Text right <= shape right + 30px (extra tolerance for CSS centering)
- Text bottom <= shape bottom + 10px
- Shape width > 20px and height > 20px (not a tiny decorative element)

### Selection

From all matching shapes, select the one with the smallest area. This gives
the tightest parent container.

### Application

When a parent card is found:
- Text x = card x + 4px padding
- Text width = card width - 8px (4px padding each side)
- Text y = original Chrome y (vertical position preserved)

### Exceptions

- `h1` tags are exempt from card clamping (they are typically page-level)
- Card clamping takes priority over width multipliers
- Card clamping takes priority over centered heading full-width

## Tolerance Values

| Parameter | Value | Rationale |
|---|---|---|
| Left/top tolerance | 5px | Allow for minor CSS margin/padding differences |
| Right tolerance | 30px | CSS centering can place text outside the visual card |
| Bottom tolerance | 10px | Text baseline vs card bottom |
| Horizontal padding | 4px each side | Visual breathing room inside cards |
| Minimum card size | 20x20px | Exclude tiny shapes that aren't containers |

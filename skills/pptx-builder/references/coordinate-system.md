# Coordinate System & EMU Conversion

## EMU (English Metric Units)

PowerPoint uses EMU as its internal unit. 1 inch = 914,400 EMU.

### Conversion Formula

Layout JSON uses pixel coordinates in the HTML viewport space (default 1280x720).
The `SlideBuilder` converts these to EMU:

```
EMU_x = pixel_x / source_w * slide_w_inches * 914400
EMU_y = pixel_y / source_h * slide_h_inches * 914400
```

Default values:
- `source_w` = 1280 (Chrome viewport width)
- `source_h` = 720 (Chrome viewport height)
- `slide_w_inches` = 13.333 (widescreen 16:9)
- `slide_h_inches` = 7.5

### Why Widescreen 13.333 x 7.5

Standard PowerPoint widescreen is 13.333" x 7.5" (not 10" x 5.625" which is
PptxGenJS's default). This maps cleanly to a 1280x720 viewport:
- 1px = 13.333/1280 inches = 0.01042" = ~9,524 EMU

## Width Multipliers

CSS and Calibri have different font metrics. Text that fits perfectly in a
CSS-rendered box often wraps in PowerPoint because Calibri renders wider.

### Compensating Multipliers

| Element Type | Multiplier | Rationale |
|---|---|---|
| h1, h2, h3 headings | 1.15x | Large text shows the biggest CSS→Calibri difference |
| Body text, spans | 1.08x | Smaller text has less deviation |
| Card-clamped text | 1.0x (card width) | Already constrained to card bounds |
| Centered headings | Full slide width | Uses 48px margin each side instead of Chrome's tight rect |

### When Multipliers Apply

Multipliers apply only to text that is NOT inside a card shape. Card text uses
the parent card's width (minus 4px padding each side) to prevent overflow.

The priority order:
1. Text inside a card shape → use card width (find_parent_card)
2. Centered h1/h2/h3 → use full slide width with margins
3. Other text → apply multiplier to Chrome's bounding box width

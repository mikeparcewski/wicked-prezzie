# python-pptx Fix Recipes

Tested code patterns for surgically editing PPTX slides after conversion.
Use these when the pipeline gets the slide 90% right but a specific element
needs a targeted fix. Prefer EDL specs (edl_apply.py) for simple parametric
edits. Use these recipes for structural changes.

## When to use recipes vs EDL vs script fixes

| Situation | Approach |
|---|---|
| Move, resize, crop, recolor a shape | **EDL spec** → `edl_apply.py` |
| Replace an element with a different shape type | **Recipe** (below) |
| Add a missing decorative element | **EDL** `add_shape` or **recipe** |
| Issue affects 2+ distinct decks | **Script fix** in `pptx_builder.py` |

## Safe API Surface

These python-pptx APIs are stable and safe to use in fix scripts:

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree
```

## Recipe 1: Re-crop an SVG screenshot image

When an SVG screenshot includes content below/beside the chart.

```python
from pptx import Presentation
from pptx.util import Emu

prs = Presentation('deck.pptx')
slide = prs.slides[5]  # 0-based

# Find the image shape (usually the SVG screenshot)
for shape in slide.shapes:
    if shape.shape_type == 13:  # Picture
        # Crop 30px from bottom (in EMU)
        crop_emu = int(30 / 720 * 7.5 * 914400)
        shape.height -= crop_emu
        break

prs.save('deck.pptx')
```

## Recipe 2: Replace vertical text with horizontal badge row

When badge containers collapse to vertical text stacking.

```python
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

prs = Presentation('deck.pptx')
slide = prs.slides[6]

# Delete the broken vertical text box
for shape in list(slide.shapes):
    if shape.has_text_frame and 'Badge1' in shape.text_frame.text:
        sp = shape._element
        sp.getparent().remove(sp)
        break

# Add horizontal badges
badges = [('Active', '#22c55e'), ('Review', '#f59e0b'), ('Closed', '#ef4444')]
start_x = 100  # px from left
y = 400  # px from top

def px2emu_x(px): return int(px / 1280 * 13.333 * 914400)
def px2emu_y(px): return int(px / 720 * 7.5 * 914400)

for i, (text, color) in enumerate(badges):
    x = start_x + i * 120
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        px2emu_x(x), px2emu_y(y),
        px2emu_x(100), px2emu_y(28)
    )
    shape.adjustments[0] = 0.5  # pill shape
    shape.fill.solid()
    h = color.lstrip('#')
    shape.fill.fore_color.rgb = RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = False
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Emu(0)
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    run = tf.paragraphs[0].add_run()
    run.text = text
    run.font.name = 'Calibri'
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(255, 255, 255)

prs.save('deck.pptx')
```

## Recipe 3: Add a missing progress bar

When a CSS gradient progress bar didn't convert.

```python
from pptx import Presentation
from pptx.util import Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation('deck.pptx')
slide = prs.slides[7]

def px2emu_x(px): return int(px / 1280 * 13.333 * 914400)
def px2emu_y(px): return int(px / 720 * 7.5 * 914400)

# Track (background)
track = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE,
    px2emu_x(100), px2emu_y(350),
    px2emu_x(600), px2emu_y(8)
)
track.adjustments[0] = 0.5
track.fill.solid()
track.fill.fore_color.rgb = RGBColor(30, 30, 40)
track.line.fill.background()

# Fill (65% progress)
fill_w = int(600 * 0.65)
fill = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE,
    px2emu_x(100), px2emu_y(350),
    px2emu_x(fill_w), px2emu_y(8)
)
fill.adjustments[0] = 0.5
fill.fill.solid()
fill.fill.fore_color.rgb = RGBColor(34, 197, 94)
fill.line.fill.background()

prs.save('deck.pptx')
```

## Recipe 4: Add a left-border accent bar

When the accent bar was lost or rendered as a full outline.

```python
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation('deck.pptx')
slide = prs.slides[3]

def px2emu_x(px): return int(px / 1280 * 13.333 * 914400)
def px2emu_y(px): return int(px / 720 * 7.5 * 914400)

# Find the card shape to attach the accent to
for shape in slide.shapes:
    if not shape.has_text_frame:
        continue
    if 'target card text' in shape.text_frame.text:
        # Add accent bar at the card's left edge
        accent = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            shape.left, shape.top,
            px2emu_x(4), shape.height
        )
        accent.fill.solid()
        accent.fill.fore_color.rgb = RGBColor(34, 197, 94)  # green
        accent.line.fill.background()
        accent.text_frame.clear()
        break

prs.save('deck.pptx')
```

## Recipe 5: Replace a broken element with an HTML screenshot crop

When extraction fails for a complex element, screenshot just that region.

```python
import sys, tempfile
sys.path.insert(0, 'skills/chrome-extract/scripts')
from chrome_extract import screenshot_html, crop_region
from pptx import Presentation

# Screenshot the HTML source
with tempfile.TemporaryDirectory() as tmpdir:
    screenshot_html(
        'slides/slide-07.html',
        f'{tmpdir}/full.png', tmpdir,
        viewport_w=1280, viewport_h=720
    )

    # Crop just the chart region (x, y, w, h in CSS pixels)
    crop_region(
        f'{tmpdir}/full.png',
        f'{tmpdir}/chart.png',
        {'x': 48, 'y': 162, 'w': 1184, 'h': 350}
    )

    # Insert into PPTX
    prs = Presentation('deck.pptx')
    slide = prs.slides[6]

    def px2emu_x(px): return int(px / 1280 * 13.333 * 914400)
    def px2emu_y(px): return int(px / 720 * 7.5 * 914400)

    # Delete the broken shape first
    for shape in list(slide.shapes):
        if shape.shape_type == 13:  # Picture
            sp = shape._element
            sp.getparent().remove(sp)
            break

    # Add the clean crop
    slide.shapes.add_picture(
        f'{tmpdir}/chart.png',
        px2emu_x(48), px2emu_y(162),
        px2emu_x(1184), px2emu_y(350)
    )
    prs.save('deck.pptx')
```

## Recipe 6: Fix text box that overflows its card

When text wraps differently in Calibri vs the CSS font.

```python
from pptx import Presentation
from pptx.util import Pt

prs = Presentation('deck.pptx')
slide = prs.slides[2]

for shape in slide.shapes:
    if shape.has_text_frame and 'overflowing text' in shape.text_frame.text:
        # Option A: Widen the text box
        shape.width = int(shape.width * 1.15)

        # Option B: Reduce font size
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                current = run.font.size
                if current:
                    run.font.size = Pt(current.pt * 0.9)
        break

prs.save('deck.pptx')
```

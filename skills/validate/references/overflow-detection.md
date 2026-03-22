# Overflow Detection: The Pad+Render+Check Pattern

## Why Static Bounds Checking Is Not Enough

Static validation opens the PPTX with python-pptx and compares each shape's bounding box against the slide dimensions. If a shape's right edge exceeds the slide width, it is flagged as overflow. This catches placement errors where the conversion pipeline positions a shape partially outside the slide rectangle.

However, static bounds checking cannot detect content overflow within a correctly-placed shape. The most important case is text reflow. When Chrome renders an HTML slide, it uses the system's font metrics for whatever typeface the CSS specifies. When python-pptx creates the PPTX, the text is placed inside a text box with dimensions matching the Chrome bounding box. But LibreOffice uses its own font metrics, typically Calibri as the default. A heading that fits on one line in Chrome at 28px may wrap to two lines in LibreOffice at the equivalent size, because Calibri characters are slightly wider than the CSS font's characters. The second line pushes below the text box boundary, but the text box dimensions in the XML remain unchanged. The shape is "within bounds" according to python-pptx, yet the rendered slide shows text bleeding past the bottom of the box.

Other cases that static checking misses include images that are scaled or cropped differently by LibreOffice's rendering engine, shapes with auto-grow behavior that expand based on content, and grouped shapes whose children overflow the group boundary after LibreOffice recalculates layout.

To catch these problems, the validator needs to inspect the actual rendered output of the PPTX file. This is what the visual overflow detector does.

## The Padding Approach Step by Step

The core idea is simple: add a known-color margin around the slide, render the result, and check whether any content appears in the margin. If it does, something overflowed.

### Step 1: Create a Padded Copy

Open the original PPTX with python-pptx. Increase the slide width and height by twice the padding amount (once for each side). The default padding is 50 pixels, converted to EMU at 96 DPI (approximately 476,250 EMU per side). Shift every shape on every slide by the padding offset in both X and Y, so that the original content occupies the center of the enlarged slide. Save the modified PPTX to a temporary file.

The padding value is a tradeoff. Larger padding makes detection more robust (a few stray anti-aliased pixels at the edge are less likely to trigger a false positive), but it changes the aspect ratio more and may cause LibreOffice to render at a different effective resolution. Fifty pixels provides enough margin to detect meaningful overflow without distorting the layout.

### Step 2: Paint the Background Grey

Before saving the padded PPTX, set each slide's background fill to solid grey (RGB 128, 128, 128). This establishes the expected color for the margin regions. Grey is chosen because it is distinct from both white (common slide backgrounds) and black (common text colors), which minimizes false positives from anti-aliasing artifacts. A white margin would be indistinguishable from a white slide background that bleeds into the padding. A black margin would blend with dark text or borders.

The grey background is applied to the slide background element in the PPTX XML. It does not affect shape backgrounds. The original slide content retains its own colors and backgrounds; only the exposed margin area around the content renders as grey.

### Step 3: Render to PNG

Pass the padded PPTX to LibreOffice (via the slide-render skill's `render_pptx_to_pngs` function) to produce one PNG per slide. LibreOffice performs the definitive text reflow and layout calculations, so the rendered output reflects the actual appearance of the deck. The PNGs are written to a temporary directory.

Since LibreOffice is the target renderer, the visual check is an exact representation of what the recipient will see — unlike Chrome's CSS metrics which differ significantly.

### Step 4: Scan the Margins

For each rendered PNG, calculate the expected margin width in pixels. The margin size depends on the ratio of the padding to the total padded slide dimensions, scaled to the rendered image resolution. The calculation accounts for the possibility that LibreOffice renders at a different resolution than the nominal 96 DPI.

Crop four regions from the image: top margin, bottom margin, left margin, and right margin. Each region spans the full length of its respective edge but excludes the corners (to avoid double-counting). For each region, iterate over every pixel and compare it to the expected grey (128, 128, 128) with a tolerance of 15 per channel. This tolerance accommodates JPEG compression artifacts, anti-aliasing, and minor color-space differences in the rendering pipeline.

If more than 1% of the pixels in a margin region differ from grey beyond the tolerance, that edge is flagged as having overflow. The 1% threshold filters out isolated anti-aliased pixels at the boundary between content and margin, which are visually insignificant.

## Edge Detection Logic

The detector reports which specific edges have overflow: top, bottom, left, right, or any combination. This information is useful for diagnosing the root cause. Right-edge overflow typically indicates text that is wider than expected (font metrics difference). Bottom-edge overflow typically indicates text wrapping to additional lines. Left-edge or top-edge overflow is less common and usually indicates a shape positioning bug in the conversion pipeline.

Each overflowing edge produces a separate error in the issue list for the affected slide. The slide score is reduced by 10 points per visual overflow error, which means a slide with all four edges overflowing loses 40 points and will fail the 75-point threshold.

## When to Use Visual Overflow Detection

Enable visual overflow detection with the `--render` flag. It requires:

- **LibreOffice** installed. macOS: `brew install --cask libreoffice`. Linux: `apt install libreoffice`.
- **The slide-render skill** present at `slide-render/scripts/slide_render.py` relative to the project root. This provides the `render_pptx_to_pngs` function that wraps LibreOffice.
- **Pillow** (`pip install Pillow`) for image loading and pixel inspection.

Visual detection adds several seconds per slide (LibreOffice startup, rendering, pixel scanning), so it is not suitable for tight iteration loops during development. Use static validation for rapid feedback. Reserve visual validation for final QA passes, CI pipelines, or when static validation passes but the rendered output looks wrong.

If LibreOffice or the slide-render skill is not available, the detector emits an info-level message and skips the visual check rather than failing. The static checks still run and produce a report. This allows the same script to be used in environments with and without LibreOffice installed.

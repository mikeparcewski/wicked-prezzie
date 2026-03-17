# Slide Quality Rubric

This rubric provides a machine-readable scoring system for evaluating presentation slide quality. Each slide is scored independently. The total possible score is 100 points. A slide must score at or above the quality threshold to pass (default: 85, configurable via slide-config).

---

## Scoring Summary

| Category | Points | Criteria |
|---|---|---|
| Bounds compliance | 20 | All elements within slide boundaries |
| Text readability | 20 | Font sizes >= minimums, contrast ratios met |
| Layout balance | 15 | Whitespace >= 30%, elements aligned |
| Color consistency | 15 | Palette <= 5 colors, contrast ratios met |
| Typography | 10 | <= 2 font families, clear size hierarchy |
| Content density | 10 | <= 7 top-level elements per slide |
| Visual overflow | 10 | No content extends beyond slide edges |

**Pass threshold:** 85 / 100 (configurable via `slide-config`)

---

## Category Details

### 1. Bounds Compliance (20 points)

**What to check:**

- Every shape, text box, and image has a bounding box defined by (x, y, width, height).
- Compute the right edge as `x + width` and the bottom edge as `y + height`.
- The slide canvas is 1280x720 pixels. Minimum margins are 48px from each edge, giving a safe zone of x:[48, 1232], y:[48, 672].
- Check that every element's bounding box falls entirely within the safe zone.

**Deduction rules:**

- Each element with any edge inside the 0-48px margin zone: -4 points (error).
- Each element partially outside the 0-1280 or 0-720 canvas entirely: -6 points (error).
- Elements within 48-64px of an edge (close to margin but not violating): -1 point (warning).

**Severity levels:**

- Error: Element extends into margin zone (< 48px from edge) or beyond canvas. Full deduction per element.
- Warning: Element is within 48-64px of edge. Half deduction per element.

**Cap:** Deductions in this category cannot exceed 20 points total.

**Examples:**

- PASS: A title text box at (80, 60, 1120, 50). Right edge = 1200 (within 1232). Bottom = 110 (within 672). All edges respect 48px margins.
- FAIL: A shape at (20, 100, 400, 200). Left edge = 20, which is inside the 48px margin zone. Deduct 4 points.
- FAIL: An image at (900, 500, 400, 300). Right edge = 1300, which exceeds the 1280 canvas width. Deduct 6 points.

---

### 2. Text Readability (20 points)

**What to check:**

- Extract the font size of every text run on the slide.
- Body text must be >= 16pt. Title text must be >= 28pt. Caption text must be >= 11pt.
- Compute the contrast ratio between each text run's color and its immediate background color using the WCAG relative luminance formula.
- Body text (< 24pt) requires >= 4.5:1 contrast. Large text (>= 24pt) requires >= 3:1 contrast.

**Deduction rules:**

- Each text run below minimum font size: -3 points (error).
- Each text run failing contrast ratio by less than 1.0: -2 points (warning).
- Each text run failing contrast ratio by 1.0 or more: -4 points (error).
- Title text below 28pt: -4 points (error).

**Severity levels:**

- Error: Font size below minimum, or contrast fails by >= 1.0. Full deduction.
- Warning: Contrast fails by < 1.0 (close to threshold). Half deduction.

**Cap:** Deductions in this category cannot exceed 20 points total.

**Examples:**

- PASS: Body text at 18pt, color #FFFFFF on background #1A1A2E. Contrast ratio = 15.3:1 (exceeds 4.5:1). Font size exceeds 16pt minimum.
- FAIL: Body text at 14pt. Below the 16pt minimum. Deduct 3 points.
- FAIL: Body text color #777777 on background #FFFFFF. Contrast ratio = 4.48:1, which is below 4.5:1 by 0.02. Deduct 2 points (warning, close miss).
- FAIL: Body text color #AAAAAA on background #FFFFFF. Contrast ratio = 2.32:1, which fails by 2.18. Deduct 4 points (error).

---

### 3. Layout Balance (15 points)

**What to check:**

- Render the slide and compute the percentage of pixels occupied only by the background (no foreground elements overlapping). This is the whitespace ratio.
- Whitespace must be >= 30% of total slide area.
- Check alignment: elements that appear to share a vertical or horizontal axis should be within 4px of true alignment.
- Verify consistent spacing: gaps between adjacent elements should not vary by more than 20% from the average gap on that slide.

**Deduction rules:**

- Whitespace below 30%: -8 points (error).
- Whitespace between 25-30%: -4 points (warning).
- Each pair of visually aligned elements misaligned by > 4px: -2 points (warning).
- Inconsistent inter-element spacing (variance > 20%): -3 points (warning).

**Severity levels:**

- Error: Whitespace below 25%. Full deduction.
- Warning: Whitespace 25-30%, or alignment/spacing issues. Half deduction.

**Cap:** Deductions in this category cannot exceed 15 points total.

**Examples:**

- PASS: Slide with 3 text boxes and 1 image, whitespace = 45%. All elements left-aligned at x=80 (within 1px). Gaps between elements are 30px, 32px, 28px (variance < 10%).
- FAIL: Slide with 5 large shapes, whitespace = 22%. Deduct 8 points.
- FAIL: Two headings that should be left-aligned, but one is at x=80 and the other at x=92 (12px difference). Deduct 2 points.

---

### 4. Color Consistency (15 points)

**What to check:**

- Extract all unique colors used on the slide (text colors, shape fills, border colors). Exclude pure white, pure black, and grayscale tones (where R=G=B) from the count.
- Count unique chromatic colors. There should be <= 5.
- For every chromatic color, verify it appears on at least 2 slides in the deck (palette consistency check). One-off colors on a single slide are violations.
- Check that the dominant color covers 50-70% of the total chromatic area.

**Deduction rules:**

- More than 5 unique chromatic colors on a single slide: -3 points per extra color (error).
- A color appearing on only one slide in the deck: -2 points per orphan color (warning).
- No clear dominant color (largest color < 40% of chromatic area): -4 points (warning).
- Any text-to-background pair failing WCAG AA (redundant with readability, but checked here for non-text elements): -3 points (error).

**Severity levels:**

- Error: Too many colors or contrast failure. Full deduction.
- Warning: Orphan colors or weak dominance. Half deduction.

**Cap:** Deductions in this category cannot exceed 15 points total.

**Examples:**

- PASS: Slide uses #6B2FA0 (primary), #A855F7 (secondary), #F59E0B (accent). Three chromatic colors, all present across the deck. Primary covers 65% of chromatic area.
- FAIL: Slide uses 7 distinct chromatic colors. Two extra beyond the 5-color limit. Deduct 6 points.
- FAIL: Slide introduces #FF6347 that appears nowhere else in the deck. Deduct 2 points.

---

### 5. Typography (10 points)

**What to check:**

- Extract all font family names used on the slide.
- Count unique font families. There should be <= 2.
- Verify a clear size hierarchy exists: the largest text should be the title, the next largest should be subtitles or section headers, and body text should be uniformly sized.
- Check that no more than 4 distinct font sizes appear on the slide.
- Verify line spacing is between 1.2x and 1.5x the font size for multi-line text blocks.

**Deduction rules:**

- More than 2 font families: -4 points per extra family (error).
- More than 4 distinct font sizes: -2 points per extra size (warning).
- No clear size hierarchy (body text same size as title): -3 points (error).
- Line spacing outside 1.0-1.6x range: -2 points per offending text block (warning).

**Severity levels:**

- Error: Too many fonts or no hierarchy. Full deduction.
- Warning: Too many sizes or spacing out of range. Half deduction.

**Cap:** Deductions in this category cannot exceed 10 points total.

**Examples:**

- PASS: Slide uses Calibri for headings and body, differentiated by weight and size. Title at 40pt bold, body at 18pt regular, caption at 13pt regular. Three sizes, one family. Line spacing 1.3x.
- FAIL: Slide uses Arial, Georgia, and Courier New. Three families. Deduct 4 points.
- FAIL: Title at 20pt and body at 19pt. No meaningful hierarchy. Deduct 3 points.

---

### 6. Content Density (10 points)

**What to check:**

- Count top-level visual elements on the slide. A top-level element is any independently positioned shape, text box, image, or group. Children within a group count as one collective element.
- The count should be <= 7.
- Also check for text volume: no single text box should contain more than 75 words.

**Deduction rules:**

- 8-9 top-level elements: -3 points (warning).
- 10+ top-level elements: -6 points (error).
- Each text box exceeding 75 words: -2 points (warning).
- A slide with both > 7 elements and a text box > 75 words: apply both deductions.

**Severity levels:**

- Error: 10+ elements. Full deduction.
- Warning: 8-9 elements, or text box over 75 words. Half deduction.

**Cap:** Deductions in this category cannot exceed 10 points total.

**Examples:**

- PASS: Slide with 1 title, 1 body text box, 1 image, 2 accent shapes. Total: 5 elements. Longest text box is 40 words.
- FAIL: Slide with 11 shapes (ungrouped icons, multiple text boxes, several decorative elements). Deduct 6 points.
- FAIL: A body text box containing 120 words. Deduct 2 points. The content should be split across slides.

---

### 7. Visual Overflow (10 points)

**What to check:**

- For every element, verify that no rendered pixels extend beyond the 1280x720 canvas.
- This differs from bounds compliance: bounds compliance checks margins, while visual overflow checks the hard canvas edge.
- Check for text overflow within text boxes: if a text box has `autofit=off` or `shrink_text=off`, verify that the text does not exceed the box height. Measure by computing the total line height (line count multiplied by font size multiplied by line spacing) and comparing to the box height.
- Check for image cropping: if an image shape's aspect ratio differs from the source image, verify the crop region is intentional and does not cut off essential content.

**Deduction rules:**

- Each element extending beyond the canvas: -5 points (error).
- Each text box with text overflowing its container: -3 points (error).
- Each image with unintentional cropping (aspect ratio mismatch > 10% without explicit crop settings): -2 points (warning).

**Severity levels:**

- Error: Canvas overflow or text overflow. Full deduction.
- Warning: Suspect image cropping. Half deduction.

**Cap:** Deductions in this category cannot exceed 10 points total.

**Examples:**

- PASS: All elements within canvas. Text boxes sized to fit content. Images match their containers' aspect ratios within 5%.
- FAIL: A text box at (100, 600, 1100, 200). Bottom edge = 800, which exceeds the 720 canvas height by 80px. Deduct 5 points.
- FAIL: A text box with 6 lines of 20pt text (total height ~180px) inside a 100px-tall container. Text overflows by 80px. Deduct 3 points.

---

## Scoring Procedure

1. Start each slide at 100 points.
2. Evaluate all seven categories. Apply deductions per the rules above, respecting per-category caps.
3. Sum remaining points. This is the slide's quality score.
4. A slide scoring >= 75 passes. Below 75 is a failure.
5. For deck-level scoring, compute the average across all slides. The deck passes if the average is >= 75 and no individual slide scores below 60.

## Reporting Format

When reporting results, use this structure per slide:

```
Slide N: SCORE/100 [PASS|FAIL]
  Bounds compliance:  XX/20  [violations...]
  Text readability:   XX/20  [violations...]
  Layout balance:     XX/15  [violations...]
  Color consistency:  XX/15  [violations...]
  Typography:         XX/10  [violations...]
  Content density:    XX/10  [violations...]
  Visual overflow:    XX/10  [violations...]
```

List specific violations with their severity (error/warning) and the measured value versus the threshold. This enables targeted fixes rather than vague quality complaints.

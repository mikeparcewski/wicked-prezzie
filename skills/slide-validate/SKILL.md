---
name: Slide Validate
description: >
  Quality assurance for slide decks — layout validation, content lint, deck
  audit, and consistency checks. Use when the user says "is it good?", "audit
  my deck", "check for problems", "lint content", "check consistency", or
  "any issues?". Also use proactively after any conversion run. Catches
  overflow, empty slides, bullet overload, title issues, and cross-slide
  inconsistencies.
---

# Slide Validate

## Purpose

Slide Validate is a quality assurance tool for PowerPoint files produced by the wicked-pptx conversion pipeline. It inspects `.pptx` files for layout defects, content overflow, empty slides, and structural problems that arise when HTML slide decks are converted to native PowerPoint shapes. Run it after every conversion to catch issues before the deck reaches a human reviewer.

The tool operates in two modes: static validation (fast, no external dependencies beyond python-pptx) and visual validation (slower, requires LibreOffice for rendering). Static validation catches most structural problems. Visual validation catches problems that only manifest after the renderer reflows text using its own font metrics.

## Validation Modes

### Static Mode (default)

Static mode opens the `.pptx` file with python-pptx and inspects every shape on every slide. It checks bounding boxes against the slide dimensions, flags negative coordinates, detects empty slides, and estimates text overflow using character-count heuristics. No rendering step is involved, so it completes in under a second for most decks.

Use static mode for rapid feedback during development or when LibreOffice is not available.

### Visual Mode (--render)

Visual mode extends static mode with a pixel-level overflow detection pass. It creates a padded copy of the PPTX (grey margins added around each slide), renders the padded slides to PNG using LibreOffice via the slide-render skill, then scans the margin regions for non-grey pixels. Any content that bleeds into the padding area is reported as a visual overflow error.

Use visual mode for final QA before delivering a deck. It catches text reflow overflow, image bleed, and shape clipping that static heuristics miss. See `references/overflow-detection.md` for a detailed explanation of the pad+render+check algorithm.

## Usage

Run the script directly from the command line.

```bash
# Static validation (fast)
python ${CLAUDE_SKILL_DIR}/scripts/slide_validate.py output.pptx

# Static + visual overflow detection
python ${CLAUDE_SKILL_DIR}/scripts/slide_validate.py output.pptx --render

# JSON output for programmatic consumption
python ${CLAUDE_SKILL_DIR}/scripts/slide_validate.py output.pptx --json

# Custom rubric (reserved for future use)
python ${CLAUDE_SKILL_DIR}/scripts/slide_validate.py output.pptx --rubric my_rubric.json
```

### Arguments

| Argument | Description |
|---|---|
| `pptx_path` | Path to the `.pptx` file to validate. Required. |
| `--render` | Enable visual overflow detection. Requires LibreOffice and the slide-render skill. |
| `--json` | Output results as JSON instead of the human-readable summary. |
| `--rubric` | Path to a custom rubric JSON file. Reserved for future scoring customization. |

## Validation Checks

The validator runs the following checks on every slide.

### Bounds Check (`check_bounds`)

Iterate over all shapes on the slide. For each shape, compute the right edge (`left + width`) and bottom edge (`top + height`). If either exceeds the slide dimensions by more than 50,000 EMU (approximately 0.055 inches), report a bounds error. The tolerance accounts for minor rounding in the conversion pipeline. Shapes that extend past the right or bottom edge are reported separately, with the overflow distance in inches.

This is the most common defect in converted slides. It happens when Chrome reports a bounding box that extends to the edge of the viewport but the PPTX slide dimensions are slightly smaller, or when a shape is placed correctly but its content causes it to grow.

### Negative Coordinates Check (`check_negative_coords`)

Shapes with negative `left` or `top` values are partially off-slide. This usually indicates a conversion bug where an element was positioned relative to a container that was not properly accounted for. The tolerance is -50,000 EMU; anything further off-slide triggers a warning. These shapes may be invisible in the final presentation or may cause unexpected clipping.

### Empty Slide Check (`check_empty_slide`)

A slide with zero shapes is flagged as empty. A slide with shapes but no text content and no images is also flagged, since it likely represents a failed extraction. Both cases produce warnings rather than errors, since intentionally blank slides do exist (though they are rare in converted decks).

### Text Overflow Check (`check_text_overflow`)

For every shape with a text frame, estimate whether the text fits inside the shape. The heuristic computes an approximate character capacity based on the shape width (assuming roughly 12 characters per inch at 12pt) and height (assuming roughly 4 lines per inch). If the actual character count exceeds 1.5 times the estimated capacity, report a warning.

This is a rough heuristic. It does not account for font size, bold/italic metrics, or word wrapping. For precise overflow detection, use visual mode instead.

### Visual Overflow Check (`detect_visual_overflow`)

Only runs when `--render` is specified. Creates a padded copy of the PPTX with grey margins, renders to PNG, and checks the margin pixels for content bleed. Reports the specific edges (top, bottom, left, right) where overflow is detected. Each overflowing edge is an error.

This catches overflow that static checks miss: text that reflows differently in PowerPoint than in Chrome, images that extend past their containers after rasterization, and shapes that are technically within bounds but whose rendered content is not.

## Scoring

Each slide starts at 100 points. Points are deducted per issue:

| Issue Type | Severity | Deduction |
|---|---|---|
| Bounds overflow | Error | -10 |
| Visual overflow | Error | -10 |
| Empty slide | Error | -15 |
| Other errors | Error | -5 |
| Any warning | Warning | -3 |

A slide passes if its score is 75 or above. The overall deck score is the average of all slide scores.

## Report Format

### Human-Readable (default)

The default output prints a summary header with the file name, total slides, pass/fail counts, and overall score. Below the header, each failing slide is listed with its index, score, and the list of issues. Passing slides are omitted for brevity.

```
=== Slide Validation Report ===
File:   output.pptx
Slides: 12 total, 10 passed, 2 failed
Score:  87/100 (threshold: 75)

Slide 3 [FAIL] score=65
  [ERROR] bounds: Shape 'TextBox 7' extends 0.42in past right edge
  [ERROR] bounds: Shape 'TextBox 7' extends 0.15in past bottom edge
  [WARNING] text_overflow: Text in 'TextBox 7' may overflow (312 chars in 2.1in wide box)

Slide 9 [FAIL] score=70
  [ERROR] visual_overflow: Content overflows on right, bottom edge(s)
```

### JSON (--json)

The JSON output contains the full results dictionary as returned by `validate_pptx()`. It includes every slide (passing and failing), all issues with type, severity, and description, and the summary statistics. Pipe it to `jq` or consume it from another script.

## Overflow Detection Details

Static bounds checking catches shapes that are placed outside the slide rectangle, but it cannot detect content that overflows within a shape. The most common case is text reflow: Chrome renders text with one set of font metrics, and PowerPoint uses different metrics (typically Calibri). A heading that fits in one line in Chrome may wrap to two lines in PowerPoint, pushing content below the shape boundary.

The visual overflow detector solves this by rendering the actual PPTX output and checking for pixel-level bleed. See `references/overflow-detection.md` for the full algorithm description.

## Troubleshooting

### "Visual overflow check skipped: slide-render or Pillow not available"

The `--render` flag requires the slide-render skill to be present at `../slide-render/scripts/slide_render.py` relative to this skill, and Pillow must be installed. Install Pillow with `pip install Pillow` and verify the slide-render skill exists.

### "Visual overflow check failed: rendering error"

LibreOffice must be installed. macOS: `brew install --cask libreoffice`. Linux: `apt install libreoffice`. Verify with `soffice --version`.

### False positives on bounds checks

The 50,000 EMU tolerance handles minor rounding, but some slides have intentional bleed (e.g., full-bleed background images). If a shape is meant to extend to the edge, you can ignore bounds warnings for that shape. Future rubric support will allow whitelisting specific shape names.

### Low scores on slides with many small shapes

Each issue deducts points independently. A slide with 10 shapes that each overflow by 0.06 inches will lose 100 points and score 0, even though the overflow is barely visible. Inspect the issue list to determine whether the failures are cosmetically significant. Adjust the tolerance in `check_bounds` if your pipeline consistently produces minor overflows.

### Text overflow false positives

The character-count heuristic is deliberately conservative. It will flag text boxes that are actually fine because it cannot account for font size or auto-shrink settings. Use `--render` for definitive overflow detection, or ignore text_overflow warnings when the visual output looks correct.

## Extended Validation: Deck Audit

Beyond layout validation, slide-validate supports comprehensive deck quality auditing through
its reference files. These provide content-level and structural quality analysis.

## Reference Files

Read these on demand — do not load all at once.

| File | Read when... |
|---|---|
| [overflow-detection.md](references/overflow-detection.md) | Understanding the pad+render+check visual overflow algorithm |
| [deck-audit.md](references/deck-audit.md) | Running a full 5-category quality audit (structure, content, layout, consistency, lint) |
| [content-lint.md](references/content-lint.md) | Checking content quality: bullets, titles, stats, quotes, passive voice, CTAs |
| [consistency-checks.md](references/consistency-checks.md) | Within-deck and cross-deck consistency: heading sizes, palette adherence, section cadence |

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

Structural QA for PowerPoint files. Fast checks that catch shape overflow,
negative coordinates, empty slides, and text overflow heuristics. Visual
fidelity is judged by Claude comparing screenshots — not by this script.

## Usage

```python
from slide_validate import validate_pptx
results = validate_pptx("deck.pptx")
for slide in results:
    if slide["issues"]:
        print(f"Slide {slide['index']}: {len(slide['issues'])} issues")
        for issue in slide["issues"]:
            print(f"  [{issue['severity']}] {issue['type']}: {issue['description']}")
```

## Checks

### Bounds (`check_bounds`)
Shapes extending past right/bottom edge by >50,000 EMU (~0.055in). Most common
defect — happens when Chrome bounding boxes exceed PPTX slide dimensions.

### Negative Coordinates (`check_negative_coords`)
Shapes with negative left/top — partially off-slide, usually a conversion bug.

### Empty Slides (`check_empty_slide`)
No shapes, or shapes with no text and no images. Likely failed extraction.

### Text Overflow (`check_text_overflow`)
Character-count heuristic: ~12 chars/inch width, ~4 lines/inch height. Flags
text exceeding 1.5x estimated capacity. Rough — use visual comparison for
definitive overflow detection.

## Script Location

`scripts/slide_validate.py` — imported by the pipeline workflow.

## Reference Files

Read on demand — do not load all at once.

| File | Read when... |
|---|---|
| [overflow-detection.md](references/overflow-detection.md) | Understanding visual overflow patterns |
| [deck-audit.md](references/deck-audit.md) | Full 5-category quality audit |
| [content-lint.md](references/content-lint.md) | Content quality checks |
| [consistency-checks.md](references/consistency-checks.md) | Within-deck and cross-deck consistency |
| [validation-lenses.md](references/validation-lenses.md) | Four parallel validation agents: POV Clarity, RFP Coverage, Making It Real, Know Them |
| [balance-audit.md](references/balance-audit.md) | Content ratio (30/40/30), redundancy clusters, flow cohesion, council punch list format |

---
name: Slide Compare
description: >
  Side-by-side visual comparison of HTML source slides vs converted PPTX output.
  Use when checking conversion quality, doing a visual diff, reviewing fidelity,
  or verifying the PPTX matches the original. Also use proactively after any
  conversion — "does it look right?", "how close is it?", "check fidelity",
  "visual diff".
---

# Slide Visual Comparison

Generate side-by-side comparison images of original HTML slides versus the
converted PPTX output. Essential for verifying conversion fidelity and
identifying layout differences.

## When to Use

- After running HTML-to-PPTX conversion to verify output quality
- When debugging specific slides that look wrong in PowerPoint
- To compare a subset of slides for targeted review

## Architecture

1. **HTML screenshots** — Chrome headless captures each HTML slide as PNG
2. **PPTX rendering** — LibreOffice exports the .pptx to PDF via headless mode,
   then `pdftoppm` converts PDF pages to PNG
3. **Output** — Paired PNG files in `html/` and `pptx/` subdirectories for
   manual or automated visual comparison

## Usage

Run the comparison script at `scripts/slide_compare.py`:

```bash
# Compare all slides
python ${CLAUDE_SKILL_DIR}/scripts/slide_compare.py \
  --html-dir ./slides --pptx deck.pptx --output-dir ./compare

# Compare specific slides (1-based indices)
python ${CLAUDE_SKILL_DIR}/scripts/slide_compare.py \
  --html-dir ./slides --pptx deck.pptx --slides 1,5,10
```

### Options

| Flag | Default | Purpose |
|---|---|---|
| `--html-dir`, `-d` | (required) | Directory with HTML slide files |
| `--pptx`, `-p` | (required) | PPTX file to compare against |
| `--output-dir`, `-o` | `./compare` | Output directory for comparison images |
| `--slides`, `-s` | (all) | Comma-separated 1-based slide indices |
| `--hide` | `.slide-nav` | CSS selectors to hide in HTML screenshots |

### Output Structure

```
compare/
  html/         # PNG screenshots of original HTML slides
  pptx/         # PNG renders of PPTX slides (via PDF)
  deck.pdf      # Intermediate PDF export
```

## Dependencies

Verify before running:

- Google Chrome (for HTML screenshots)
- **LibreOffice** (exports PPTX to PDF via headless mode)
- `pdftoppm` from poppler (`brew install poppler`)

## Reviewing Results

After running, open the `html/` and `pptx/` directories side by side.
Common differences to look for:

- **Text wrapping** — Calibri font metrics differ from CSS; headings may wrap differently
- **Color shifts** — Alpha-blended colors may appear slightly different
- **Missing elements** — SVGs below the size threshold are intentionally skipped
- **Fallback slides** — Screenshot-only slides indicate extraction failures to investigate

---
name: Slide Pipeline
description: >
  End-to-end orchestrator that chains all wicked-pptx stages: standardize HTML,
  convert to PPTX, validate quality, render to PNG, and compare visually. This
  is the DEFAULT entry point for any ambiguous conversion request — use it when
  the user says "convert these slides", "make a PowerPoint from this HTML",
  "turn these into a deck", or wants the full workflow including quality checks.
  Always prefer this over slide-html-to-pptx unless the user explicitly asks to
  skip validation/rendering or is debugging a single conversion step. Especially
  important for AI-generated HTML (ChatGPT, Claude, Gemini) which needs
  standardization before extraction will work. If unsure whether to use this or
  slide-html-to-pptx, use this — it includes everything slide-html-to-pptx does
  plus QA, rendering, and comparison.
---

# Slide Pipeline

End-to-end orchestrator that chains all wicked-pptx skills into a single
pipeline: standardize HTML, convert to PPTX, validate, render, and compare.

## When to Use

- Running the full conversion workflow from raw AI HTML to validated PPTX
- Automating the iterate-until-quality loop
- Processing a batch of slides through all stages at once

## Pipeline Stages

```
1. standardize  →  Normalize HTML (viewport, .slide wrapper, strip animations)
2. convert      →  HTML → PPTX via Chrome extraction + slide-pptx-builder
3. validate     →  Bounds checking, overflow detection, quality scoring
4. render       →  PPTX → PNG via LibreOffice for visual review
5. compare      →  Side-by-side HTML vs PPTX comparison images
```

Each stage is optional and can be skipped via flags.

## Usage

```bash
# Full pipeline
python skills/slide-pipeline/scripts/slide_pipeline.py --input-dir ./slides --output deck.pptx

# Skip standardization (HTML already clean)
python skills/slide-pipeline/scripts/slide_pipeline.py --input-dir ./slides --output deck.pptx --no-standardize

# Convert + validate only (no render/compare)
python skills/slide-pipeline/scripts/slide_pipeline.py --input-dir ./slides --output deck.pptx --no-render --no-compare

# Full pipeline with visual overflow detection
python skills/slide-pipeline/scripts/slide_pipeline.py --input-dir ./slides --output deck.pptx --visual-overflow

# Full pipeline with montage
python skills/slide-pipeline/scripts/slide_pipeline.py --input-dir ./slides --output deck.pptx --montage montage.png
```

### Options

| Flag | Default | Purpose |
|---|---|---|
| `--input-dir`, `-d` | `.` | Directory containing HTML slide files |
| `--output`, `-o` | `deck.pptx` | Output PPTX path |
| `--slides`, `-s` | (all) | Comma-separated HTML filenames |
| `--manifest`, `-m` | (none) | JSON manifest for slide ordering |
| `--viewport` | `1280x720` | Browser viewport dimensions |
| `--hide` | `.slide-nav` | CSS selectors to hide |
| `--no-standardize` | | Skip HTML standardization |
| `--no-validate` | | Skip PPTX validation |
| `--no-render` | | Skip PPTX→PNG rendering |
| `--no-compare` | | Skip HTML vs PPTX comparison |
| `--visual-overflow` | | Enable visual overflow detection (requires LibreOffice) |
| `--montage` | | Create contact sheet montage at given path |
| `--render-dir` | `./renders` | Output directory for rendered PNGs |
| `--compare-dir` | `./compare` | Output directory for comparison images |

## Output

```
./
  deck.pptx              — Generated PowerPoint
  validation-report.json — Per-slide quality scores and issues
  renders/               — PNG per slide (if --no-render not set)
    slide-01.png
    slide-02.png
  compare/               — Side-by-side comparison (if --no-compare not set)
    html/
    pptx/
  montage.png            — Contact sheet (if --montage set)
```

## Exit Codes

| Code | Meaning |
|---|---|
| 0 | Pipeline complete, all slides pass validation (score >= 75) |
| 1 | Pipeline complete but some slides failed validation |
| 2 | Pipeline error (missing files, Chrome/LibreOffice not found) |

## Iteration Loop

When slides fail validation, fix the HTML source and re-run. The pipeline
supports incremental runs — only re-process changed files by specifying
`--slides` with the filenames that need fixing.

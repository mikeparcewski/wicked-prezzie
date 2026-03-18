---
name: Slide Pipeline
description: >
  End-to-end orchestrator that chains all wicked-pptx stages with three fidelity
  tiers (best/draft/rough), dual-format output (PPTX + self-contained Reveal.js
  HTML), non-destructive versioning ({slug}_v{N}.pptx), and session-scoped edit
  coordination. This is the DEFAULT entry point for any ambiguous conversion or
  generation request — use it when the user says "convert these slides", "make a
  PowerPoint from this HTML", "turn these into a deck", "best fidelity", "draft
  quality", "render as HTML", "both formats", "show version history", "diff v1
  and v2", "re-render as html", or wants the full workflow including quality
  checks. Always prefer this over slide-html-to-pptx unless the user explicitly
  asks to skip validation or is debugging a single conversion step. Especially
  important for AI-generated HTML (ChatGPT, Claude, Gemini) which needs
  standardization before extraction will work. Fidelity tiers: best (multi-pass
  verification), draft (single clean pass, default), rough (structure only).
  REVIEW flags embedded in speaker notes when human judgment is needed.
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
python ${CLAUDE_SKILL_DIR}/scripts/slide_pipeline.py --input-dir ./slides --output deck.pptx

# Skip standardization (HTML already clean)
python ${CLAUDE_SKILL_DIR}/scripts/slide_pipeline.py --input-dir ./slides --output deck.pptx --no-standardize

# Convert + validate only (no render/compare)
python ${CLAUDE_SKILL_DIR}/scripts/slide_pipeline.py --input-dir ./slides --output deck.pptx --no-render --no-compare

# Full pipeline with visual overflow detection
python ${CLAUDE_SKILL_DIR}/scripts/slide_pipeline.py --input-dir ./slides --output deck.pptx --visual-overflow

# Full pipeline with montage
python ${CLAUDE_SKILL_DIR}/scripts/slide_pipeline.py --input-dir ./slides --output deck.pptx --montage montage.png
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

## Reference Files

Read these on demand — do not load all at once.

| File | Read when... |
|---|---|
| [fidelity-tiers.md](references/fidelity-tiers.md) | Quality tiers (best/draft/rough), multi-pass render loops, visual QA checks |
| [versioning.md](references/versioning.md) | Deck versioning, naming conventions, version metadata, diff operations |
| [output-formats.md](references/output-formats.md) | Dual-format rendering: PPTX (python-pptx) + HTML (Reveal.js), format comparison |
| [edit-coordination.md](references/edit-coordination.md) | Session locks and render guards for concurrent edit coordination |

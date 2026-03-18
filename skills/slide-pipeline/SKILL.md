---
name: Slide Pipeline
description: >
  End-to-end orchestrator that chains all wicked-pptx stages with iterative
  visual verification. This is the DEFAULT entry point for any conversion or
  generation request — use it when the user says "convert these slides", "make
  a PowerPoint from this HTML", "turn these into a deck", or wants the full
  workflow including quality checks. Always prefer this over slide-html-to-pptx
  unless the user explicitly asks to skip validation or is debugging a single
  conversion step. Especially important for AI-generated HTML (ChatGPT, Claude,
  Gemini) which needs standardization before extraction will work.
  REVIEW flags embedded in speaker notes when human judgment is needed.
---

# Slide Pipeline

End-to-end orchestrator for HTML → PPTX conversion with iterative visual
verification. Converts, then verifies each slide visually, then fixes and
re-converts until output matches source — or until diminishing returns.

## Workflow Overview

1. **Convert** — Run the single-pass pipeline (standardize → extract → build PPTX)
2. **Render** — Render PPTX to PNG via PowerPoint
3. **Verify** — Screenshot each source HTML and visually compare against the PPTX render
4. **Fix** — For each slide with issues, diagnose the root cause and fix the HTML or conversion parameters
5. **Repeat** — Re-convert only the fixed slides, re-render, re-verify. Stop when all slides pass or no further improvement is possible.

## Step 1: Convert

Run the single-pass pipeline to produce the initial PPTX:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/slide_pipeline.py \
  --input-dir ./slides --output deck.pptx
```

### Options

| Flag | Default | Purpose |
|---|---|---|
| `--input-dir`, `-d` | `.` | Directory containing HTML slide files |
| `--output`, `-o` | `deck.pptx` | Output PPTX path (delivered to project directory) |
| `--slides`, `-s` | (all) | Comma-separated HTML filenames |
| `--manifest`, `-m` | (none) | JSON manifest for slide ordering |
| `--viewport` | `1280x720` | Browser viewport dimensions |
| `--hide` | `.slide-nav` | CSS selectors to hide |
| `--workers`, `-w` | auto | Max parallel Chrome workers |
| `--no-standardize` | | Skip HTML standardization |
| `--no-validate` | | Skip structural validation |
| `--no-render` | | Skip PPTX→PNG rendering |
| `--no-compare` | | Skip HTML vs PPTX comparison |
| `--visual-overflow` | | Enable visual overflow detection (requires PowerPoint) |
| `--montage` | | Create contact sheet montage at given path |

## Step 2: Render + Screenshot

After conversion, produce comparison images:

1. **Render PPTX slides to PNG** using slide-render:
```bash
python skills/slide-render/scripts/slide_render.py deck.pptx -o ~/.something-wicked/wicked-prezzie/output/renders/
```

2. **Screenshot each HTML source** using chrome-extract:
```bash
python skills/chrome-extract/scripts/chrome_extract.py --screenshot slides/slide-01.html --output ~/.something-wicked/wicked-prezzie/output/html-screenshots/slide-01.png
```

Or use the compare skill to do both at once:
```bash
python skills/slide-compare/scripts/slide_compare.py --html-dir ./slides --pptx deck.pptx
```

## Step 3: Verify (Visual Comparison)

**This is the critical step.** Use the Read tool to view both images side by side for each slide:

1. Read the HTML screenshot (source of truth)
2. Read the PPTX render (conversion output)
3. Grade the slide on these criteria:

### Per-Slide Grading Checklist

For each slide, check ALL of the following. A slide PASSES only if all critical checks pass.

**Critical (must pass):**
- [ ] **Text readable** — All text visible, not clipped, not overlapping other elements
- [ ] **Layout match** — Elements in approximately the same positions as the HTML source
- [ ] **Colors correct** — Background, text, and accent colors match the source
- [ ] **No missing elements** — All headings, bullets, cards, stats, images present
- [ ] **No phantom elements** — No extra shapes, text boxes, or artifacts not in the source

**Important (should pass):**
- [ ] **Font sizes proportional** — Heading/body hierarchy preserved (doesn't need to be pixel-exact)
- [ ] **Spacing reasonable** — Margins and gaps between elements are proportional to source
- [ ] **Cards/shapes correct** — Background fills, border radius, shadows approximate the source
- [ ] **Text wrapping** — Long text wraps similarly to source (no single-line overflow)

**Nice to have:**
- [ ] **Exact font match** — Fonts render identically (usually impossible due to CSS→Calibri mapping)
- [ ] **Pixel alignment** — Sub-pixel positioning matches (not expected)

### Grading Output

For each slide, produce a verdict:

- **PASS** — Slide looks correct. No changes needed.
- **FIX** — Slide has specific fixable issues. List them.
- **REVIEW** — Slide has issues that can't be fixed automatically. Flag for human review.

Example:
```
Slide 1 (title): PASS
Slide 2 (content): FIX — heading text clipped on right, card backgrounds too dark
Slide 3 (stats): FIX — stat values overlapping labels, missing bottom card
Slide 4 (section): PASS
Slide 5 (cta): REVIEW — complex gradient background can't be reproduced in PPTX
```

## Step 4: Fix

For each slide marked FIX, diagnose the root cause and apply the correction:

### Common Issues and Fixes

| Issue | Root Cause | Fix |
|---|---|---|
| Text clipped/overflow | Text box too narrow or too short | Edit `pptx_builder.py` width clamping or font size scaling |
| Elements overlapping | Chrome extraction returned overlapping bounding boxes | Check `chrome_extract.py` DOM walker — elements may need z-ordering |
| Wrong background color | Alpha blending computed against wrong base color | Check `color_utils.py` blend target — verify `slideBg` in layout JSON |
| Missing elements | Element filtered out by size threshold or selector | Check `hide_selectors` and the 60px SVG threshold |
| Cards too dark/light | Card background alpha not blended correctly | Fix alpha blending in `color_utils.py` |
| Text wrapping different | PPTX uses Calibri metrics, CSS used different font | Adjust width multiplier in `pptx_builder.py` |
| Fallback slide (screenshot) | Chrome extraction failed entirely | Fix the HTML source — likely missing `.slide` wrapper or bad viewport |

### Fixing HTML Source

If the issue is in the source HTML (bad structure, missing wrappers):
1. Edit the HTML file directly
2. Re-standardize if needed: `python skills/slide-html-standardize/scripts/html_standardize.py <file>`

### Fixing Conversion Code

If the issue is in the extraction or building logic:
1. Read the relevant skill's SKILL.md for context
2. Edit the Python script
3. Re-run conversion on just the affected slides

## Step 5: Re-Convert and Re-Verify

After fixing, re-convert ONLY the affected slides:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/slide_pipeline.py \
  --input-dir ./slides --output deck.pptx \
  --slides slide-02.html,slide-03.html
```

Then repeat Steps 2-3: render, screenshot, compare, grade.

### Stop Conditions

Stop iterating when ANY of these is true:

1. **All slides PASS** — Every slide passes the grading checklist. Done.
2. **No improvement** — Re-conversion produces the same visual issues. The problem is a fundamental limitation (gradients, fonts, complex CSS). Mark remaining issues as REVIEW.
3. **4 passes reached** — After 4 conversion attempts on the same slide, stop. Mark as REVIEW with a note explaining what couldn't be fixed.
4. **User says stop** — User is satisfied or wants to manually fix remaining issues.

### REVIEW Flags

When a slide is marked REVIEW, add a note to the PPTX speaker notes:
```
[REVIEW] This slide has known visual differences from the HTML source:
- Gradient background approximated with solid color
- Font metrics differ (Calibri vs CSS font)
```

## Output

```
./
  deck.pptx                — Final PowerPoint (project directory)
~/.something-wicked/wicked-prezzie/output/
  renders/                 — PPTX → PNG renders
  compare/                 — Side-by-side HTML vs PPTX comparisons
```

## Reference Files

Read these on demand — do not load all at once.

| File | Read when... |
|---|---|
| [fidelity-tiers.md](references/fidelity-tiers.md) | Quality tiers (best/draft/rough), visual QA checks |
| [versioning.md](references/versioning.md) | Deck versioning, naming conventions, version metadata, diff operations |
| [output-formats.md](references/output-formats.md) | Dual-format rendering: PPTX (python-pptx) + HTML (Reveal.js) |
| [edit-coordination.md](references/edit-coordination.md) | Session locks and render guards for concurrent edit coordination |

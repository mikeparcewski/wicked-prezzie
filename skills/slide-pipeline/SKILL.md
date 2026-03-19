---
name: Slide Pipeline
description: >
  DEFAULT entry point for all slide conversion. Converts HTML to PPTX, then
  iterates per-slide — rendering, visually comparing against the source, fixing
  issues, and re-converting each slide until it matches or converges. Use for
  "convert these slides", "make a PowerPoint", "turn these into a deck", or any
  conversion request. Handles AI-generated HTML (ChatGPT, Claude, Gemini)
  automatically. Always prefer this over slide-html-to-pptx.
---

# Slide Pipeline

End-to-end orchestrator for HTML → PPTX conversion with **per-slide** iterative
visual verification. Each slide is individually refined until it matches the
source, converges, or regresses — then move on to the next slide.

## Workflow Overview

```
For each slide in the deck:
  1. Convert the slide (standardize → extract → build PPTX)
  2. Render: screenshot the HTML source + render the PPTX slide to PNG
  3. Visually compare: grade the PPTX against the HTML source
  4. If PASS → move to next slide
  5. If FIX → diagnose, fix, re-convert THIS slide only, go to step 2
  6. Stop this slide when:
     a. It passes (output matches source)
     b. Output matches the previous attempt (converged — no point continuing)
     c. Score drops vs previous attempt (pick the previous version, that was peak)
     d. 4 attempts reached (mark REVIEW, move on)
```

**Key principle:** Process slide-by-slide, not whole-deck passes. Don't waste
time re-processing slides that are already good.

## Step 1: Initial Full-Deck Conversion

Run the single-pass pipeline to produce the initial PPTX with all slides:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/slide_pipeline.py \
  --input-dir ./slides --output deck.pptx --no-render --no-compare
```

This gives you the baseline deck. Now iterate per-slide.

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

## Step 2: Per-Slide Verification Loop

For each slide (1 through N), run this loop:

### 2a. Render Both Versions

Screenshot the HTML source and render the PPTX slide:

```bash
# Screenshot HTML source
python skills/chrome-extract/scripts/chrome_extract.py \
  --screenshot slides/slide-01.html \
  --output ~/.something-wicked/wicked-prezzie/output/html/slide-01.png

# Render PPTX (all slides at once, then look at the one you care about)
python skills/slide-render/scripts/slide_render.py deck.pptx \
  -o ~/.something-wicked/wicked-prezzie/output/renders/
```

Or use the compare skill for batch rendering:
```bash
python skills/slide-compare/scripts/slide_compare.py \
  --html-dir ./slides --pptx deck.pptx
```

### 2b. Visual Comparison

Use the Read tool to view BOTH images for the current slide:

1. Read the HTML screenshot (source of truth)
2. Read the PPTX render (conversion output)
3. Grade using the checklist below

### Per-Slide Grading Checklist

**Critical (must pass):**
- [ ] **Text readable** — All text visible, not clipped, not overlapping
- [ ] **Layout match** — Elements in approximately the same positions as HTML
- [ ] **Colors correct** — Background, text, and accent colors match
- [ ] **No missing elements** — All headings, bullets, cards, stats, images present
- [ ] **No phantom elements** — No extra shapes or artifacts not in the source

**Important (should pass):**
- [ ] **Font sizes proportional** — Heading/body hierarchy preserved
- [ ] **Spacing reasonable** — Margins and gaps proportional to source
- [ ] **Cards/shapes correct** — Background fills, borders approximate the source
- [ ] **Text wrapping** — Long text wraps similarly (no single-line overflow)

**Known limitations (do not fail for these):**
- Exact font match (CSS → Calibri mapping is inherently different)
- Sub-pixel alignment
- Gradient backgrounds (approximated with solid blended color)
- CSS animations/transitions (stripped during standardization)

### 2c. Verdict

- **PASS** — Move to next slide.
- **FIX** — List the specific issues. Proceed to Step 3.
- **REVIEW** — Issue can't be fixed (fundamental limitation). Add REVIEW flag to speaker notes, move to next slide.

### 2d. Stop Conditions (Per Slide)

Before attempting a fix, check these. If any is true, stop working on this slide:

1. **Output matches source** → PASS. Done.
2. **Output matches previous attempt** → Converged. No point re-trying. Accept current version.
3. **Score dropped vs previous attempt** → Regression. **Use the previous version** (the one that scored higher). Mark REVIEW if still not passing.
4. **4 attempts on this slide** → Max tries. Mark REVIEW, move on.

## Step 3: Fix the Current Slide

### Decision Framework — Script Fix vs Direct Fix

**Before writing any fix, decide which path:**

| Condition | Fix path | Why |
|---|---|---|
| Issue appears in 2+ distinct decks | **Script fix** in `pptx_builder.py` or `chrome_extract.py` | Systemic pattern — fix once for everyone |
| Issue affects >15% of slides in this deck | **Script fix** | General enough to warrant a heuristic |
| Issue is specific to this slide's CSS layout | **Direct fix** via EDL or recipe | No general heuristic will cover it |
| Element needs repositioning, resizing, recoloring | **EDL spec** → `edl_apply.py` | Safe, declarative, no code |
| Element needs structural replacement (wrong shape type, new shapes) | **Recipe** from `pptx-recipes.md` | Requires python-pptx code |

**Promotion rule:** If a recipe or EDL pattern gets used 3+ times across sessions,
it should graduate to a script heuristic.

### Step 3a: Script Fix (systemic issues)

For patterns that affect many slides:

| Issue | Root Cause | Fix |
|---|---|---|
| Text clipped/overflow | Text box too narrow or short | Edit `pptx_builder.py` width clamping or font size scaling |
| Elements overlapping | Overlapping bounding boxes from Chrome | Check `chrome_extract.py` DOM walker — z-ordering or dedup |
| Wrong background color | Alpha blending against wrong base | Check `color_utils.py` blend target, verify `slideBg` in layout JSON |
| Missing elements | Filtered by size threshold or selector | Check `hide_selectors` and size thresholds |
| Fallback slide (screenshot) | Chrome extraction failed | Fix HTML — likely missing `.slide` wrapper or bad viewport |

After fixing the script, re-convert ONLY the affected slide:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/slide_pipeline.py \
  --input-dir ./slides --output deck.pptx \
  --slides slide-03.html --no-render --no-compare
```

### Step 3b: Direct Fix — EDL (parametric edits)

For slide-specific positioning, sizing, or color issues. Write a JSON edit spec
and apply it — no python-pptx API knowledge needed:

```bash
python skills/slide-pptx-builder/scripts/edl_apply.py deck.pptx edits.json -o deck.pptx
```

Example EDL spec:
```json
{
  "edits": [
    {
      "slide": 7,
      "target": "image:0",
      "ops": [{"action": "crop_bottom", "pixels": 30}]
    },
    {
      "slide": 7,
      "target": "shape:0",
      "ops": [
        {"action": "add_shape", "shape": "rounded_rectangle",
         "x": 100, "y": 350, "width": 390, "height": 8, "fill": "#22c55e"}
      ]
    }
  ]
}
```

**EDL actions:** `move`, `resize`, `crop_bottom`, `crop_top`, `set_text`,
`set_fill`, `set_font_size`, `set_rotation`, `delete`, `add_shape`, `add_textbox`

**Targets:** `shape:N` (by index), `text:substring` (by content), `image:N` (Nth picture)

### Step 3c: Direct Fix — Recipes (structural edits)

For complex fixes that need python-pptx code (replacing shapes, adding
composite elements). See `slide-pptx-builder/references/pptx-recipes.md`:

- **Re-crop SVG screenshot** — trim bleed from chart images
- **Replace vertical badges with horizontal row** — fix collapsed badge containers
- **Add missing progress bar** — draw track + fill shapes
- **Add left-border accent** — separate thin shape at card edge
- **Screenshot crop replacement** — replace broken element with HTML crop
- **Fix text overflow** — widen box or reduce font size

### After Any Fix

Go back to Step 2a: re-render, re-compare, re-grade this one slide.

### Complexity Routing

The standardize step annotates each slide with `<!-- COMPLEXITY: high|low -->`.
Use this to prioritize:

- **Low complexity slides** — expect the pipeline to get these right in 1-2 passes.
  If not, it's likely a script bug.
- **High complexity slides** — expect to use EDL or recipes for the last mile.
  SVGs, gradients, pseudo-elements, rotated text are inherently harder to convert.

## Step 4: Finalize

After all slides have been processed through the per-slide loop:

1. **Render final deck** for review:
```bash
python skills/slide-render/scripts/slide_render.py deck.pptx \
  -o ~/.something-wicked/wicked-prezzie/output/renders/ \
  --montage ~/.something-wicked/wicked-prezzie/output/montage.png
```

2. **Report** which slides passed, which have REVIEW flags:
```
Slide 1 (title): PASS (attempt 1)
Slide 2 (content): PASS (attempt 3 — fixed text overflow, card colors)
Slide 3 (stats): REVIEW (attempt 4 — gradient background can't be reproduced)
Slide 4 (section): PASS (attempt 1)
Slide 5 (cta): PASS (attempt 2 — fixed missing accent bar)
```

3. **REVIEW flags** — For any REVIEW slides, add to speaker notes:
```
[REVIEW] This slide has known visual differences from the HTML source:
- Gradient background approximated with solid color
- Custom font replaced with Calibri
```

## Output

```
./
  deck.pptx                — Final PowerPoint (project directory)
~/.something-wicked/wicked-prezzie/output/
  renders/                 — PPTX → PNG renders
  html/                    — HTML source screenshots
  compare/                 — Side-by-side comparisons
  montage.png              — Contact sheet (if requested)
```

## Reference Files

Read these on demand — do not load all at once.

| File | Read when... |
|---|---|
| [fidelity-tiers.md](references/fidelity-tiers.md) | Quality tiers, visual QA checks |
| [versioning.md](references/versioning.md) | Deck versioning, naming, metadata, diff |
| [output-formats.md](references/output-formats.md) | PPTX + Reveal.js dual-format output |
| [edit-coordination.md](references/edit-coordination.md) | Session locks for concurrent edits |
| [pptx-recipes.md](../slide-pptx-builder/references/pptx-recipes.md) | python-pptx fix recipes for direct PPTX edits |

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

This skill has no script — it's a workflow that chains the other skills.
Claude orchestrates the loop directly using vision to judge quality.

## Two-Phase Quality Model

**Phase 1 — Conversion + Structural Checks** (automated, fast)
: Converts all slides and runs structural validation: shapes in bounds, no empty
slides, no text overflow. A clean structural check means the PPTX is well-formed.
**It does NOT mean the slides look correct.**

**Phase 2 — Per-Slide Visual Comparison** (model-driven, thorough)
: For each slide, render both HTML source and PPTX output to PNG, then visually
compare. This is where actual quality is measured. **Never skip this phase.**

## Workflow

```
Step 1: Convert all slides (produces deck.pptx + raw extraction JSON)
        Run structural checks. Fix any bounds/overflow issues.

Step 1b (optional): Vision classification
        For slides that look wrong, read the HTML screenshot + raw extraction
        JSON. Reclassify elements using vision, rebuild that slide.

Step 2: For each slide:
  a. Screenshot HTML source + render PPTX slide to PNG
  b. Read both images. Grade PPTX against HTML source.
  c. If PASS → next slide
  d. If FIX → diagnose, fix, re-convert, go to (a)
  e. Stop when: passes, converged, regressed, or 4 attempts

Step 3: Render final montage, report results
```

## Step 1: Convert All Slides

```bash
python skills/slide-html-to-pptx/scripts/html_to_pptx.py \
  --input-dir ./slides --output deck.pptx
```

Then run structural checks:
```python
from slide_validate import validate_pptx
issues = validate_pptx("deck.pptx")
```

Fix any structural issues (bounds overflow, negative coords) before Phase 2.

## Step 1b: Vision Classification (when needed)

When the default `classify_elements()` produces wrong results for a slide,
use vision to reclassify. This replaces heuristic classification with
model judgment.

### When to Use

- After Step 2 identifies a slide with `missing_element` or `text_error`
- When the raw extraction JSON has elements that the default classifier
  put in the wrong category
- For complex slides with unusual HTML patterns

### How It Works

1. Read the HTML screenshot for the slide
2. Read the raw extraction JSON (saved in the output dir during Step 1)
3. For each raw element, decide:
   - **richtext** — this element should be a text box with its runs
   - **shape** — this element should be a rectangle/rounded rect
   - **skip** — this element is a container; its children handle the content
4. Rebuild the classified element list
5. Re-run the builder for just that slide

### Classification Prompt

When looking at the screenshot + raw elements, answer for each element:

```
Element [index]: tag={tag} rect=({x},{y},{w},{h}) hasBg={bool} runs={count} directText="{text}"
→ Type: richtext | shape | skip
→ Reason: (one line)
```

**Rules:**
- If an element has `runs` and you can see its text in the screenshot → **richtext**
- If an element has `hasBg` and you can see a colored rectangle → **shape**
- If an element is a container whose children are separately extracted → **skip**
- If you can see content in the screenshot that no element captures → flag as **missing**
- Low confidence? Mark it. The render-compare loop will catch it.

## Step 2: Per-Slide Verification Loop

For each slide (1 through N):

### 2a. Render Both Versions

```bash
# Screenshot HTML source
python skills/chrome-extract/scripts/chrome_extract.py \
  --screenshot slides/slide-01.html \
  --output ~/.something-wicked/wicked-prezzie/output/html/slide-01.png

# Render PPTX (all slides)
python skills/slide-render/scripts/slide_render.py deck.pptx \
  -o ~/.something-wicked/wicked-prezzie/output/renders/
```

### 2b. Visual Comparison

Read BOTH images with the Read tool. Grade using two questions:

**Q1: Are any elements clearly broken?**

Broken means: missing entirely, concatenated text, wrong/missing background,
collapsed layout (>20% off), navigation artifacts that shouldn't be there.

Tag issues: `missing_element`, `text_error`, `layout_shift`, `wrong_color`, `artifact`

**Q2: Does the PPTX convey the same structure and content as the HTML?**

Same sections, hierarchy, reading order, all text present and readable.

Ignore only: CSS→Calibri font differences, sub-pixel alignment, gradients
rendered as solid colors, stripped animations.

### 2c. Verdict

- **PASS** — Both questions passed. Next slide.
- **FIX** — Issues found. List category tags. Proceed to Step 2d.
- **REVIEW** — Inherent format limitation. Must justify why no fix is possible.

### 2d. Stop Conditions (Per Slide)

1. Output matches source → PASS
2. Output matches previous attempt → Converged, accept
3. Score dropped vs previous → Regression, use previous version
4. 4 attempts → Max tries, mark REVIEW, move on

## Step 2e: Fix the Current Slide

### Decision Framework

| Condition | Fix path | Why |
|---|---|---|
| Issue in 2+ distinct decks | **Script fix** in `pptx_builder.py` or `chrome_extract.py` | Systemic |
| Affects >15% of slides | **Script fix** | General enough |
| Specific to this slide's CSS | **Direct fix** via EDL or recipe | No general heuristic |
| Reposition, resize, recolor | **EDL spec** → `edl_apply.py` | Declarative, safe |
| Structural replacement | **Recipe** from `pptx-recipes.md` | Needs python-pptx code |

After fixing, re-convert only the affected slide and go back to 2a.

### Complexity Routing

The standardize step annotates each slide with `<!-- COMPLEXITY: high|low -->`.
- **Low complexity** — expect 1-2 passes. If not, likely a script bug.
- **High complexity** — expect EDL or recipes for the last mile.

## Step 3: Finalize

```bash
python skills/slide-render/scripts/slide_render.py deck.pptx \
  -o ~/.something-wicked/wicked-prezzie/output/renders/ \
  --montage ~/.something-wicked/wicked-prezzie/output/montage.png
```

Report which slides passed, which have REVIEW flags.

## Reference Files

Read on demand — do not load all at once.

| File | Read when... |
|---|---|
| [fidelity-tiers.md](references/fidelity-tiers.md) | Quality tiers, visual QA checks |
| [versioning.md](references/versioning.md) | Deck versioning, naming, metadata, diff |
| [output-formats.md](references/output-formats.md) | PPTX + Reveal.js dual-format output |
| [edit-coordination.md](references/edit-coordination.md) | Session locks for concurrent edits |
| [pptx-recipes.md](../slide-pptx-builder/references/pptx-recipes.md) | python-pptx fix recipes |

---
name: convert
description: |
  DEFAULT entry point for all slide conversion. Converts HTML to PPTX, then
  iterates per-slide — rendering, visually comparing against the source, fixing
  issues, and re-converting each slide until it matches or converges. Handles
  AI-generated HTML (ChatGPT, Claude, Gemini) automatically. Always prefer this
  over slide-html-to-pptx.

  Use when: "convert these slides", "make a PowerPoint", "turn these into a deck",
  "HTML to PPTX", "convert to PowerPoint", "export as PPTX", "make me a PowerPoint"
---

# Slide Pipeline

End-to-end orchestrator for HTML → PPTX conversion with **per-slide** iterative
visual verification. Each slide is individually refined until it matches the
source, converges, or regresses — then move on to the next slide.

This skill has no script — it's a workflow that chains the other skills.
Claude orchestrates the loop directly using vision to judge quality.

## Two-Phase Quality Model

**Phase 1 — Triage + Prep + Build** (structured, deterministic baseline)
: For each slide: score element confidence, detect known-pattern risks, apply
geometry transforms, build PPTX. A clean build means the manifest was fully
resolved and no elements were skipped unexpectedly.

**Phase 2 — Per-Slide Visual Comparison** (model-driven, thorough)
: For each slide, render both HTML source and PPTX output to PNG, then visually
compare. This is where actual quality is measured. **Never skip this phase.**

## Workflow

```
Step 0:  Triage all slides
Step 0b: Prep manifests (auto + model for flagged)
Step 1:  Build PPTX (manifest-driven) + structural checks
Step 2+: Per-slide render-compare loop
Step N:  Treatment log entry
Step Final: Render montage, report
```

## Step 0: Triage All Slides

During extraction (`html_to_pptx.py` Phase 1), triage runs automatically
alongside Chrome extraction. For each slide, `triage_slide()` is called and
`findings.json` is written to `{cache_dir}/slide-{N:03d}/`.

```python
# Findings are produced automatically. To run triage manually:
from slide_triage import triage_slide
import json

raw_layout = json.load(open("slide-000/raw-layout.json"))
classified_layout = json.load(open("slide-000/classified-layout.json"))
findings = triage_slide(raw_layout, classified_layout, slide_index=0,
                        source_file="01-ai-powered-analytics.html")
```

Each findings JSON records:
- `flaggedCount`: elements with `confidence < 0.85`
- `patterns`: known patterns detected (e.g. `["PATTERN-002", "PATTERN-004"]`)
- `complexity`: `"low"` | `"high"`

Slides with `flaggedCount == 0` proceed directly to Step 1 (no model needed).

## Step 0b: Prep Manifests

For each slide, `auto_resolve()` runs automatically in Phase 1 and writes
`manifest.json`. High-confidence elements (>= 0.85) are fully resolved with
geometry transforms applied. Flagged elements (< 0.85) are left as stubs with
`type = None`.

**If manifest has unresolved elements** (`type = None`): read the HTML
screenshot and resolve them before Step 1.

```python
from slide_prep import auto_resolve
import json

findings = json.load(open("slide-000/findings.json"))
classified_layout = json.load(open("slide-000/classified-layout.json"))
manifest = auto_resolve(findings, classified_layout)

# Check for unresolved stubs
unresolved = [e for e in manifest["elements"] if e.get("type") is None]
```

### Resolving Flagged Elements (model step)

1. Read `findings.json` for the slide — note `flaggedCount` and `flagReason` for each element.
2. Read the HTML screenshot PNG for the slide.
3. For each element with `type = None`:
   - Locate it in the screenshot using `rect` coordinates (1280x720 space).
   - Decide: correct type? skip? needs geometry adjustment?
   - Update `type`, `classificationSource = "model"`, and `flagReason` with your conclusion.
   - If geometry differs, set `resolvedRect` with `source = "model"`.
4. Write the updated manifest back to `manifest.json`.
5. Run manifest validation checklist (see `slide-prep/SKILL.md`).

## Step 1: Build PPTX

```bash
python skills/slide-html-to-pptx/scripts/html_to_pptx.py \
  --input-dir ./slides --output deck.pptx
```

The pipeline automatically uses `build_slide_from_manifest()` when all elements
are resolved. Falls back to legacy `build_slide()` if manifest has unresolved
elements (with a warning).

Then run structural checks:
```python
from slide_validate import validate_pptx
issues = validate_pptx("deck.pptx")
```

Fix any structural issues (bounds overflow, negative coords) before Phase 2.
To diagnose a structural issue, read the slide's `manifest.json` — the
`resolvedRect` fields show exactly what geometry was used.

## Step 2: Per-Slide Verification Loop

For each slide (1 through N):

### 2a. Render Both Versions

```bash
# Screenshot HTML source
python skills/chrome-extract/scripts/chrome_extract.py \
  --screenshot slides/01-ai-powered-analytics.html \
  --output ~/.something-wicked/wicked-prezzie/output/html/01-ai-powered-analytics.png

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
| Issue in 2+ distinct decks | Update `known-patterns.md` + `classify_elements()` confidence score | Systemic — improve triage |
| Affects >15% of slides | Add to `known-patterns.md`, update triage confidence thresholds | General pattern |
| Wrong manifest classification for this slide | Edit `manifest.json`, set `classificationSource = "override"`, rebuild slide | Prep missed it — model override |
| Specific geometry off for this slide | **EDL spec** → `edl_apply.py` | Slide-specific — no general pattern |
| Structural replacement needed | **Recipe** from `pptx-recipes.md` | Needs python-pptx code |

### How to Fix via Manifest Override

When the manifest has a wrong classification for a specific slide:

1. Read `{cache_dir}/slide-{N:03d}/manifest.json`.
2. Find the element by `manifestId`.
3. Update `type`, `resolvedRect`, or `skipRender` as needed.
4. Set `classificationSource = "override"`.
5. Re-run the builder for this slide only using `build_slide_from_manifest()`.

### Complexity Routing

The standardize step annotates each slide with `<!-- COMPLEXITY: high|low -->`.
- **Low complexity** — expect 1-2 passes. If not, likely a manifest classification error.
- **High complexity** — expect EDL or recipes for the last mile.

## Step N: Treatment Log

After each slide completes (PASS or converge), record a treatment log entry:

```python
import json
from datetime import datetime, timezone

entry = {
    "schemaVersion": 1,
    "deckSlug": "my-deck",
    "slideIndex": slide_index,
    "sourceFile": source_file,
    "attempt": attempt_number,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "triageSummary": findings_summary,
    "prepSummary": prep_summary,
    "buildSummary": build_counts,
    "renderCompareVerdict": verdict,
    "issueCategories": issue_tags,
    "issueDescription": issue_text,
    "fixApplied": {"type": "edl", "description": "..."},
    "nextAttemptVerdict": next_verdict,
    "promotionCandidate": {"recommend": False}
}
log_path = f"{slide_tmpdir}/treatment-{slide_index:03d}-attempt-{attempt}.json"
json.dump(entry, open(log_path, 'w'), indent=2)
```

If `promotionCandidate.recommend = True`, update `known-patterns.md` with the
new pattern entry. See `slide-treatment-log/SKILL.md` for the full schema and
promotion process.

## Step Final: Finalize

```bash
python skills/slide-render/scripts/slide_render.py deck.pptx \
  -o ~/.something-wicked/wicked-prezzie/output/renders/ \
  --montage ~/.something-wicked/wicked-prezzie/output/montage.png
```

Report which slides passed, which have REVIEW flags, and which patterns were
detected by triage (from each slide's `findings.json`).

## Cache Files (per slide)

Each slide writes to `{cache_dir}/slide-{N:03d}/`:

| File | Contents |
|---|---|
| `raw-layout.json` | Raw `extract_layout()` output (before classification) |
| `classified-layout.json` | `classify_elements()` output (with confidence scores) |
| `findings.json` | Triage output (flagged elements, patterns, collision risks) |
| `manifest.json` | Fully-resolved build manifest (input to builder) |
| `treatment-{N:03d}-attempt-{M}.json` | Treatment log entry per attempt |

## Reference Files

Read on demand — do not load all at once.

| File | Read when... |
|---|---|
| [fidelity-tiers.md](references/fidelity-tiers.md) | Quality tiers, visual QA checks |
| [versioning.md](references/versioning.md) | Deck versioning, naming, metadata, diff |
| [output-formats.md](references/output-formats.md) | PPTX + Reveal.js dual-format output |
| [edit-coordination.md](references/edit-coordination.md) | Session locks for concurrent edits |
| [export-safety.md](references/export-safety.md) | Version bumping, visual verification protocol, no-tmp rule, path audit, rollback, PDF and bundled HTML |
| [constraint-persistence.md](references/constraint-persistence.md) | constraints.json schema, injection protocol, Learn Constraint protocol, severity levels, lifecycle |
| [../slide-triage/SKILL.md](../slide-triage/SKILL.md) | Triage: findings JSON schema, pattern detection |
| [../slide-prep/SKILL.md](../slide-prep/SKILL.md) | Prep: manifest schema, auto + model resolution |
| [../slide-treatment-log/SKILL.md](../slide-treatment-log/SKILL.md) | Treatment log: schema, promotion process |
| [../slide-triage/references/known-patterns.md](../slide-triage/references/known-patterns.md) | All documented patterns with signatures + treatments |
| [../slide-pptx-builder/references/pptx-recipes.md](../slide-pptx-builder/references/pptx-recipes.md) | python-pptx fix recipes |

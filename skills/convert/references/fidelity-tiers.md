# Fidelity — Layout Quality Tiers

Fidelity controls how much effort the pipeline invests in layout correctness. Three tiers.
Higher fidelity takes more render passes; lower fidelity produces output faster.

---

## The Three Tiers

### `best` — Client-Ready
**Motto:** *Don't stop until it looks right.*

Multiple render passes. After each pass, verify layout against a checklist. Re-render any
slide that fails. Iterate until all slides pass or the pass limit is reached.

Use when: presenting to a client, executive, or external audience. When the deck needs to be
handed off as-is. When polish matters more than speed.

**What gets verified per slide:**
- No text overflow — all copy fits within its content zone without clipping
- No element overlap — text boxes, images, and shapes don't collide
- Consistent heading sizes across slides of the same type
- Consistent margin/padding
- Stat values are visually dominant — larger than labels
- Bullet lists don't exceed 6 items (split to new slide if needed)
- Section dividers are visually distinct from content slides
- Title slide and closing slide have strong visual weight

**Render loop:**
```
Pass 1: Generate all slides (standardize → extract → build)
Pass 2: Run slide-validate (static + visual) on each slide
        → Flag any slides that fail
Pass 3: Regenerate flagged slides with corrective adjustments
Pass 4: Re-validate. If still failing: apply conservative fallback, flag as REVIEW.
        Stop after pass 4 — don't loop forever.
```

**Time expectation:** Communicate before starting on large decks:
> *"Best fidelity on an 18-slide deck typically takes 3–4 passes. Starting now..."*
> Show progress: *"Pass 1 complete. 4 slides flagged. Running pass 2..."*

**Output note:**
```
Fidelity: best (3 passes, 2 slides corrected, 1 REVIEW flag remaining)
```

---

### `draft` — First Draft
**Motto:** *Clean enough to present with minor edits.*

Single render pass with layout-aware generation. Content zones are respected, templates are
applied correctly, obvious problems avoided. Minor imperfections are expected — uneven spacing,
slightly tight text, image not perfectly cropped.

Use when: working session, internal review, iteration stage. Default for most flows.

**What's enforced in a single pass:**
- Content placed in correct zones
- Heading and body font sizes from theme applied
- Theme colors applied to backgrounds, text, and accents
- Images sourced and placed per template
- No content placed off-slide or outside margins
- Bullet lists capped at 7 items (warns but doesn't split)

**What may need user attention:**
- Text that's slightly tight may not wrap perfectly
- Image aspect ratios may not be ideal
- Spacing between elements may be uneven
- Some stat values may not achieve full visual dominance

**Output note:**
```
Fidelity: draft (1 pass — minor layout cleanup may be needed)
```

---

### `rough` — Structural Pass
**Motto:** *Content in, structure right, layout TBD.*

One pass. Content placed, slide order correct, speaker notes written. Layout is intentionally
not optimized — elements exist in approximately the right positions.

Use when: you need the text and structure immediately, you're comfortable editing slides
yourself, or this is input to another workflow (a designer will take it from here).

**What's included:**
- All slide content (titles, body, stats, quotes, etc.)
- Correct slide type applied
- Theme colors applied to backgrounds and primary text
- Speaker notes written
- REVIEW flags preserved

**What's explicitly skipped:**
- Image sourcing (image zones left as placeholders: `[IMAGE: query]`)
- Fine-grained sizing and positioning
- Font size hierarchy tuning
- Spacing and margin consistency
- Any multi-pass correction

**Output note:**
```
Fidelity: rough (1 pass — layout needs user attention, images not sourced)
```

---

## Fidelity Defaults by Mode

| Entry point | Default fidelity | Rationale |
|---|---|---|
| Full pipeline (default) | `draft` | Balance of speed and quality |
| "quick deck" / fast path | `draft` | Speed is the point |
| "skeleton deck" / overview | `rough` | Structure only |
| HTML-to-PPTX conversion | `draft` | Source HTML already has layout |
| Re-render / upgrade | Explicit or `best` | Intentional quality lift |

User can always specify fidelity upfront or per request.

---

## Fidelity Configuration

Set in `~/.something-wicked/wicked-prezzie/config.json` under `default_fidelity` (user-level,
shared across projects). Options: `best`, `draft`, `rough`. If not set, defaults to `draft`.

---

## Visual QA Checks (best fidelity)

Three checks run after each render pass during best fidelity:

### Check 1 — Zone Overflow
Detects content overflowing its zone boundary via Chrome extraction:
- `scrollHeight > clientHeight` or `scrollWidth > clientWidth`
- Severity: FAIL

### Check 2 — Zone Overlap
Pairwise `getBoundingClientRect()` intersection test on zone elements:
- Any two zones overlapping → FAIL

### Check 3 — Stat Dominance
Stat font-size / label font-size must be ≥ 1.5:
- Ratio < 1.5 → WARN

### Conservative Fallback
If a slide has FAIL status after pass 3, apply conservative fallback layout
(see css-contract.md in slide-design) and mark `status: REVIEW`.

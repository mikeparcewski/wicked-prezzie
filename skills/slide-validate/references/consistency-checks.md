# Consistency — Cross-Deck and Within-Deck Consistency Checks

Checks that slide elements are visually and structurally consistent within a deck, or across
two decks being compared. Called by the audit flow and directly on request.

---

## Invocation

| Trigger | Source |
|---|---|
| Audit runs consistency category | Called by deck-audit.md |
| "compare [deck-a] and [deck-b]" | Comparison mode with two PPTX files or HTML directories |
| "check consistency" | Direct invocation, single-deck mode |

---

## Single-Deck Consistency Rules

### Rule 1 — Heading Size Consistency

Slides using the same template type should use the same heading font-size.

| Condition | Severity |
|---|---|
| Variance ≤ 2px across same-type slides | PASS |
| Variance > 2px across same-type slides | WARN |

Corrective: *"Normalize heading to [modal_size]px across all [N] slides of this type."*

---

### Rule 2 — Template Distribution

No single slide type (excluding section dividers) should account for more than 50%
of non-divider slides.

| Condition | Severity |
|---|---|
| No template > 50% of non-dividers | PASS |
| One template 51–65% | WARN |
| One template > 65% | FAIL |

Corrective: *"[N] of [total] slides use [type] ([pct]%). Consider varying with [alternatives]
for visual rhythm."*

---

### Rule 3 — Color Palette Adherence

All color values used in the deck should match the active theme's palette within
a luminance tolerance of ±5.

| Condition | Severity |
|---|---|
| All colors within ±5 luminance of a palette color | PASS |
| 1–3 off-palette colors | WARN |
| > 3 off-palette colors | FAIL |

Luminance delta: `|L(used_color) − L(palette_color)|` using relative luminance (WCAG formula).

Corrective: *"Slide [N] uses [hex] — nearest palette match is [palette_hex] (ΔL = [delta]).
Replace with [palette_hex] or add to palette."*

---

### Rule 4 — Section Divider Cadence

At least one section divider must appear within every run of 6 consecutive content slides.

| Condition | Severity |
|---|---|
| No run of content slides exceeds 6 without a divider | PASS |
| A run of 7–9 content slides without a divider | WARN |
| A run of ≥ 10 content slides without a divider | FAIL |

Corrective: *"Slides [N]–[M] form a run of [run] content slides. Insert a section divider
around slide [midpoint]."*

---

### Rule 5 — Speaker Notes Presence

All non-divider slides should have speaker notes (via `data-notes` attribute or notes slide).

| Condition | Severity |
|---|---|
| All non-divider slides have notes | PASS |
| 1–2 slides missing notes | WARN |
| > 2 slides missing notes | FAIL |

Corrective: *"Slide [N] '[title]' has no speaker notes. Add talking points."*

---

## Consistency Score (single-deck)

```
score = 100
for each FAIL finding: score -= 20
for each WARN finding: score -= 8
floor score at 0
```

Returns integer 0–100.

---

## Cross-Deck Comparison Mode

Run all single-deck rules on each deck independently, then add cross-deck checks:

### Cross-Deck Check 1 — Brand Alignment

Compare color palettes between the two decks.

| Condition | Severity |
|---|---|
| Both decks use compatible palettes (all colors within ±5 luminance) | PASS |
| 1–3 palette color divergences | WARN |
| > 3 divergences or incompatible palettes | FAIL |

### Cross-Deck Check 2 — Typography Alignment

Compare heading font-sizes for the same slide types across two decks.

| Condition | Severity |
|---|---|
| Same-type heading sizes match within ±2px | PASS |
| Variance > 2px for any type | WARN |

### Cross-Deck Check 3 — Template Set Coverage

Report which slide types appear in Deck A but not B and vice versa. Informational only (INFO).

---

## Comparison Report Format

```
Deck Comparison: [deck-a] vs. [deck-b]
────────────────────────────────────────────────────────
                          [deck-a]     [deck-b]
Consistency score:          82           74
Heading size variance:      0px          4px  ← WARN
Template distribution:      PASS         PASS
Color palette:              PASS         3 off-palette  ← WARN
Section divider cadence:    PASS         FAIL (run of 11)
Speaker notes:              PASS         2 missing  ← WARN

Cross-deck
  Brand alignment:    compatible (same theme)
  Typography:         2px heading variance on content slides  ← WARN
  Template coverage:  [deck-b] missing: quote-pull, team-grid

Top cross-deck findings:
  [FAIL] deck-b: 11-slide run without section divider (slides 4–14)
  [WARN] deck-b: 3 off-palette colors (slides 3, 7, 12)
  [WARN] cross-deck: content heading 28px in deck-a, 30px in deck-b
```

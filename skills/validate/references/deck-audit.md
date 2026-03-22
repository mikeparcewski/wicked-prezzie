# Deck Audit — Comprehensive Quality Scoring

Full quality scoring for a completed deck. Runs in three modes: full, targeted, or comparison.
Produces a weighted score, quality band, and prioritized remediation list.

This extends validate's existing bounds/overflow checks with content-level and
structural quality analysis.

---

## Invocation

| User says | Mode | Behavior |
|---|---|---|
| "audit my deck" / "audit [deck-name]" | full | All five categories scored |
| "audit the content of [deck]" | targeted | User selects one or more categories |
| "compare [deck-a] and [deck-b]" | comparison | Delegates to consistency-checks.md |
| "quick audit" | full | Same as full, briefer output |

---

## Scoring Model

Five weighted categories. Aggregate score determines the quality band.

| Category | Weight | What it measures |
|---|---|---|
| Structure | 25% | Slide type appropriateness, slide count, section cadence, logical flow |
| Content | 30% | Clarity, density, title hygiene, stat formatting, quote attribution |
| Layout | 20% | Bounds compliance, overflow, element overlap, visual fidelity |
| Consistency | 15% | Heading sizes, color palette, template distribution, speaker notes |
| Lint | 10% | Bullet count, word count, passive voice, CTA completeness |

**Aggregate score** = sum of (category_score × weight). Integer 0–100.

### Quality Bands

| Band | Score range | Meaning |
|---|---|---|
| PASS | ≥ 80 | Deck is presentation-ready with minor polish optional |
| REVIEW | 60–79 | Presentable but has issues worth addressing before external use |
| FAIL | < 60 | Significant problems — remediate before presenting |

---

## Full Audit Flow

```
1. Load deck (PPTX file or HTML slide directory)
2. For each category: run checks → collect findings → compute category score
3. Apply weights → compute aggregate score → assign band
4. Sort findings by severity (FAIL > WARN > INFO)
5. Output: score card + top 10 prioritized findings + remediation suggestions
```

### Score Card Output

```
Deck: [deck-name]  Slides: [N]
──────────────────────────────────────────────
Structure    [score]/100  weight 25%  → [weighted]
Content      [score]/100  weight 30%  → [weighted]
Layout       [score]/100  weight 20%  → [weighted]
Consistency  [score]/100  weight 15%  → [weighted]
Lint         [score]/100  weight 10%  → [weighted]
──────────────────────────────────────────────
TOTAL        [score]/100  Band: [PASS|REVIEW|FAIL]
```

---

## Category: Structure (25%)

| Check | Pass condition | Severity if fail |
|---|---|---|
| Slide type matches content | Type fits content per outline | WARN |
| Slide count | 8–30 slides for a full deck | INFO |
| Section divider cadence | At least one divider per 6 content slides | WARN |
| Opener + closer | First slide is title, last slide is CTA/closing | WARN |
| Logical flow | Section order follows a recognizable narrative arc | INFO |
| No orphan sections | Every section has ≥ 2 content slides | WARN |

Scoring: Start at 100. Deduct per finding: FAIL −20, WARN −10, INFO −3.

---

## Category: Content (30%)

Runs content lint checks (see content-lint.md) and maps findings to scores.

| Finding type | Points deducted per instance |
|---|---|
| FAIL finding | −15 |
| WARN finding | −7 |
| INFO finding | −2 |

Cap deductions at −100 (floor at 0).

---

## Category: Layout (20%)

Runs validate's existing checks (bounds, overflow, empty slides) and maps findings.

| Finding type | Points deducted per instance |
|---|---|
| Bounds overflow (each edge) | −10 |
| Visual overflow (each edge) | −10 |
| Empty slide | −15 |
| Text overflow (estimate) | −3 |

This category directly leverages validate's static and visual validation modes.

---

## Category: Consistency (15%)

Delegates checks to consistency-checks.md. Receives a consistency score (0–100) directly.

---

## Category: Lint (10%)

Runs content-lint checks and computes a lint-specific score.

| Finding count | Score |
|---|---|
| 0 | 100 |
| 1–2 | 85 |
| 3–5 | 65 |
| 6–10 | 40 |
| > 10 | 15 |

---

## Findings Schema

```json
{
  "slide_index": 3,
  "slide_title": "Q1 Results",
  "slide_file": "slide-03.html",
  "category": "content",
  "type": "bullet_overload",
  "element": "body content",
  "detail": "9 bullets found — limit is 7",
  "severity": "FAIL",
  "corrective": "Split into two slides or reduce to 7 bullets."
}
```

---

## Remediation Output Format

After the score card, list the top 10 findings:

```
Top Findings (sorted by severity)
──────────────────────────────────
[FAIL] Slide 3 "Q1 Results" — 9 bullets in body
       → Split into two slides or reduce to 7 bullets.

[FAIL] Slide 7 "Process Overview" — title missing
       → Add a descriptive title to this slide.

[WARN] Slide 5 "Team Intro" — heading size variance 4px across same-type slides
       → Normalize h1 to a consistent px value.

[INFO] Slides 2, 4, 6 — passive voice density > 40%
       → Review body copy for active-voice alternatives.
```

---

## Re-audit After Fix

After a remediation pass, say "re-audit" to run again. Produces a diff summary:

```
Re-audit vs. prior run
──────────────────────
Structure:   88 → 92  (+4)
Content:     72 → 85  (+13) ← 3 FAIL findings resolved
Layout:      95 → 95  (no change)
Consistency: 81 → 81  (no change)
Lint:        90 → 95  (+5)
──────────────────────
TOTAL:       82 → 88  (+6)  Band: PASS (was PASS)
```

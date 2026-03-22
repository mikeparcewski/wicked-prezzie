# Content Lint — Slide Content Quality Checks

Rule-based checks for content quality issues in generated HTML slides or outline JSON. Produces
structured findings with severity levels. Called by the audit flow and available standalone.

---

## Invocation

| Trigger | Behavior |
|---|---|
| Audit runs content/lint categories | Called by deck-audit.md with slide files |
| "lint my deck" / "check content" | Standalone run, all six categories |
| "check bullets" / "check titles" | Targeted run, named category only |

---

## Lint Categories

Six categories. Each produces FAIL, WARN, or INFO findings per slide.

---

### Category 1 — Bullet Overload

Excessive bullet count reduces readability and forces cognitive overload.

| Condition | Severity | Threshold |
|---|---|---|
| > 7 bullets on a slide | FAIL | Hard limit |
| > 6 bullets on a slide | WARN | Soft limit |
| > 12 words in a single bullet | FAIL | Per-bullet hard limit |

Corrective (count): *"Split into two slides or trim to [limit] bullets."*
Corrective (word count): *"Shorten '[bullet text]' to ≤ 12 words. Consider moving detail to
speaker notes."*

---

### Category 2 — Title Hygiene

Slide titles anchor navigation, presenter confidence, and audience comprehension.

| Condition | Severity |
|---|---|
| Slide has no title (no h1/h2) | FAIL |
| Title exceeds 10 words | WARN |
| Duplicate title appears 2+ times in the deck | WARN |

Corrective (missing): *"Add a descriptive title — even a placeholder helps navigation."*
Corrective (too long): *"Trim to ≤ 10 words."*
Corrective (duplicate): *"Differentiate slide titles to aid navigation and speaker recall."*

---

### Category 3 — Stat Formatting

Statistics are high-value content. They must be immediately scannable and clearly attributed.

| Condition | Severity |
|---|---|
| Stat value contains unexpected characters (excluding %, $, ×, K, M, B, +, −) | WARN |
| Stat value has no accompanying label | WARN |
| Stat value string exceeds 8 characters | WARN |

Corrective (non-numeric): *"Use a clean numeric format: e.g., '47%', '$2.3M', '12×'."*
Corrective (no label): *"Add a brief label beneath the stat to explain what it measures."*
Corrective (too long): *"Shorten — e.g., '1,234,567' → '1.2M'."*

---

### Category 4 — Quote Attribution

Unattributed quotes erode credibility and remove social proof value.

| Condition | Severity |
|---|---|
| Quote slide has no attribution at all | FAIL |
| Attribution is present but lacks name AND role/company | WARN |

`has_name`: attribution contains ≥ 1 capitalized word (heuristic for proper name).
`has_role_or_company`: attribution contains a comma, a title keyword, or parenthetical.

Corrective (missing): *"Add attribution: '— [Name], [Role], [Company]'."*
Corrective (incomplete): *"Expand attribution to include full name and role or company."*

---

### Category 5 — Passive Voice Density

High passive voice density makes content feel abstract and less direct. Informational only —
does not affect audit scoring but surfaces as an editing opportunity.

| Condition | Severity |
|---|---|
| Passive voice > 40% of sentences in body text | INFO |

Passive voice heuristic: sentence contains a form of "to be" (is, are, was, were, been, being)
followed within 3 words by a past participle (ends in -ed or irregular).

Corrective: *"[N]% of sentences are passive. Review for active-voice alternatives."*

---

### Category 6 — CTA Completeness

Closing slides must direct the audience to a clear next action.

| Condition | Severity |
|---|---|
| Closing/CTA slide has no action items | WARN |
| Action items present but none begins with an imperative verb | INFO |

Imperative verb heuristic: first word matches a common CTA verb list:
Book, Schedule, Visit, Download, Register, Contact, Email, Call, Sign up, Start, Join, Try,
Request, Submit, Apply, Learn, Get, Explore, Review, Reach out.

Corrective (no actions): *"Add 1–3 clear next steps to the closing slide."*
Corrective (no verbs): *"Lead each action with an imperative verb: 'Schedule a demo'."*

---

## Findings Schema

```json
{
  "slide_index": 4,
  "slide_title": "Key Metrics",
  "slide_file": "slide-04.html",
  "category": "content",
  "lint_category": "stat_formatting",
  "type": "stat_no_label",
  "element": "stat value",
  "detail": "Stat '47%' has no label",
  "severity": "WARN",
  "corrective": "Add a brief label beneath '47%' to explain what it measures."
}
```

---

## Severity Summary Output

When run standalone:

```
Content Lint — [deck-name]
────────────────────────────────
Bullet overload:    0 FAIL, 1 WARN
Title hygiene:      1 FAIL, 0 WARN
Stat formatting:    0 FAIL, 2 WARN
Quote attribution:  0 FAIL, 1 WARN
Passive voice:      —       3 INFO
CTA completeness:   0 FAIL, 1 WARN

Total: 1 FAIL, 4 WARN, 3 INFO
```

---
name: slide-treatment-log
description: >
  Records per-slide fix history after each render-compare attempt. Provides
  the audit trail that closes the feedback loop from render-compare failures
  back to known-patterns.md. Identifies fix candidates for promotion to
  known-patterns.md to prevent the same issue on future decks.
---

# Slide Treatment Log

After each slide completes the render-compare loop (either PASS or converge),
record a treatment log entry. The log is both an audit trail and a learning
signal — it identifies recurring patterns that should be added to
`known-patterns.md` to prevent the issue on future decks.

## When to Record

Record one log entry:
- After each render-compare attempt for a slide (win, loss, or converge).
- After applying an EDL or recipe fix (record the fix in `fixApplied`).
- After the final attempt for a slide (record `nextAttemptVerdict`).

## Log Entry Schema

One JSON object per slide per attempt.

```json
{
  "schemaVersion": 1,
  "deckSlug": "sales-kickoff",
  "slideIndex": 2,
  "sourceFile": "slide-03.html",
  "attempt": 1,
  "timestamp": "2026-03-20T14:32:00Z",

  "triageSummary": {
    "flaggedCount": 2,
    "patterns": ["PATTERN-002"],
    "complexity": "low"
  },

  "prepSummary": {
    "autoResolved": 18,
    "modelResolved": 2,
    "modelReasonings": [
      "Element e-014: classified as badge (not richtext). Small circle with emoji, sits left of stat text.",
      "Element e-021: classified as skip. Flex container — children handle content."
    ]
  },

  "buildSummary": {
    "shapesBuilt": 12,
    "richtextBuilt": 8,
    "svgsBuilt": 1,
    "tablesBuilt": 0
  },

  "renderCompareVerdict": "FIX",
  "issueCategories": ["text_error"],
  "issueDescription": "Stat number '42%' rendered in wrong position, overlapping badge icon.",

  "fixApplied": {
    "type": "edl",
    "description": "Moved stat text box 54px right to clear badge"
  },

  "nextAttemptVerdict": "PASS",

  "promotionCandidate": {
    "recommend": true,
    "patternName": "stat_badge_text_offset",
    "signature": "richtext with numeric content adjacent to badge element, same row",
    "suggestedFix": "shift text x to badge right + 8px; reduce width by same amount"
  }
}
```

### Field Definitions

| Field | Type | Description |
|---|---|---|
| `schemaVersion` | int | Always 1 |
| `deckSlug` | string | Short identifier for the deck (e.g. `"sales-kickoff"`) |
| `slideIndex` | int | 0-based slide index |
| `sourceFile` | string | Original HTML filename |
| `attempt` | int | 1-based attempt number |
| `timestamp` | string | ISO 8601 timestamp when this entry was recorded |
| `triageSummary.flaggedCount` | int | Elements flagged by triage |
| `triageSummary.patterns` | string[] | Pattern IDs matched during triage |
| `triageSummary.complexity` | string | `"low"` or `"high"` |
| `prepSummary.autoResolved` | int | Elements auto-resolved in prep |
| `prepSummary.modelResolved` | int | Elements requiring model inspection |
| `prepSummary.modelReasonings` | string[] | One-line rationale per model-resolved element |
| `buildSummary.*` | int | Count of each shape type built |
| `renderCompareVerdict` | `"PASS"` \| `"FIX"` \| `"REVIEW"` | Outcome of this render-compare attempt |
| `issueCategories` | string[] | Issue tags: `missing_element`, `text_error`, `layout_shift`, `wrong_color`, `artifact` |
| `issueDescription` | string | Human-readable description of the issue |
| `fixApplied.type` | `"edl"` \| `"recipe"` \| `"manifest"` \| `"none"` | What fix was applied |
| `fixApplied.description` | string | Brief description of the fix |
| `nextAttemptVerdict` | `"PASS"` \| `"FIX"` \| `"REVIEW"` \| `null` | Outcome after fix; null if no next attempt |
| `promotionCandidate.recommend` | bool | Whether this fix should be promoted to `known-patterns.md` |
| `promotionCandidate.patternName` | string | Proposed pattern name if promoting |
| `promotionCandidate.signature` | string | Observable facts that identify this pattern |
| `promotionCandidate.suggestedFix` | string | Proposed treatment (geometry transform or type override) |

### `fixApplied.type` Values

| Value | Meaning |
|---|---|
| `edl` | Declarative JSON edits applied via `edl_apply.py` |
| `recipe` | python-pptx code from `pptx-recipes.md` |
| `manifest` | Direct edit to `manifest.json` before rebuild |
| `none` | No fix applied (PASS on first attempt, or REVIEW acceptance) |

## Storage Location

```
{slide_tmpdir}/treatment-{index:03d}-attempt-{n}.json
```

Where:
- `{slide_tmpdir}` is the per-slide cache directory (e.g. `{cache_dir}/slide-002/`)
- `{index:03d}` is the 0-based slide index zero-padded to 3 digits
- `{n}` is the 1-based attempt number

Example: `{cache_dir}/slide-002/treatment-002-attempt-1.json`

## Promotion Criteria

A fix is a **promotion candidate** (`promotionCandidate.recommend = true`) if:

1. The fix was required on **2 or more distinct decks**, OR
2. The triage finding had `confidence < 0.75` AND the model-resolved type
   differed from the `classify_elements()` default type.

A fix is **not** a promotion candidate if:
- It was an EDL geometry tweak unique to this deck's specific layout
- It addressed a typo or content error in the source HTML
- It was marked REVIEW (no fix possible — inherent format limitation)

## Promotion Process

Promotion is a **manual step** — the model reads treatment log entries and
updates `known-patterns.md` with a new entry.

To promote a candidate:

1. Read all treatment log entries for the candidate pattern (across decks).
2. Identify the common observable signature (CSS class, rect dimensions,
   relative position, element relationship).
3. Verify the fix is deterministic: the same geometry transform should apply
   to any future occurrence of the signature.
4. Write a new entry in `known-patterns.md` following the entry format.
5. Update the `PATTERN-NNN` ID (next sequential ID after existing entries).
6. Optionally update `classify_elements()` confidence scores if the pattern
   indicates the classifier is systematically wrong about element type.
7. Update the treatment log entry with `promotionCandidate.promote = true`
   (to distinguish "recommended" from "completed").

## Example: Recording a Treatment Log Entry

After render-compare attempt 1 on slide 2:

```python
import json
from datetime import datetime, timezone

entry = {
    "schemaVersion": 1,
    "deckSlug": "sales-kickoff",
    "slideIndex": 2,
    "sourceFile": "slide-03.html",
    "attempt": 1,
    "timestamp": datetime.now(timezone.utc).isoformat(),

    "triageSummary": {
        "flaggedCount": 2,
        "patterns": ["PATTERN-002"],
        "complexity": "low"
    },

    "prepSummary": {
        "autoResolved": 18,
        "modelResolved": 2,
        "modelReasonings": [
            "e-014: badge (not richtext) — small emoji circle",
            "e-021: skip — flex container"
        ]
    },

    "buildSummary": {
        "shapesBuilt": 12,
        "richtextBuilt": 8,
        "svgsBuilt": 1,
        "tablesBuilt": 0
    },

    "renderCompareVerdict": "FIX",
    "issueCategories": ["text_error"],
    "issueDescription": "Stat '42%' overlaps badge icon at x=40",

    "fixApplied": {
        "type": "edl",
        "description": "Moved stat text box 54px right to clear badge"
    },

    "nextAttemptVerdict": "PASS",

    "promotionCandidate": {
        "recommend": True,
        "patternName": "stat_badge_text_offset",
        "signature": "numeric richtext adjacent to small badge, same row",
        "suggestedFix": "shift x to badge.right + 8; reduce w by same amount"
    }
}

log_path = f"{slide_tmpdir}/treatment-002-attempt-1.json"
with open(log_path, 'w') as f:
    json.dump(entry, f, indent=2)
```

## Reference Files

| File | Read when... |
|---|---|
| [../slide-triage/references/known-patterns.md](../slide-triage/references/known-patterns.md) | Pattern entry format for promotion |
| [../slide-pptx-builder/references/pptx-recipes.md](../slide-pptx-builder/references/pptx-recipes.md) | Recipe fix types |
| [../slide-pptx-builder/scripts/edl_apply.py](../slide-pptx-builder/scripts/edl_apply.py) | EDL applicator for `fixApplied.type = "edl"` |

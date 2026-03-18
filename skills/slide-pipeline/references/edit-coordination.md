# Edit Coordination — Session Locks and Render Guards

Lightweight advisory coordination for concurrent or sequential edit operations within a single
session. Prevents conflicting writes and avoids re-rendering stale content.

---

## Overview

Two session-scoped flags protect the edit workflow:

| Flag | Purpose | Scope |
|---|---|---|
| `css_lock` | Signals that CSS/template edits are in progress | Advisory — checked before CSS changes |
| `render_guard` | Signals that a render/conversion is in progress | Advisory — checked before starting a new render |

Both flags are **transient**: they exist only within the current session. On session start, both
are absent (unlocked).

Advisory means: checks surface a warning rather than hard-blocking. The user can override by
saying "proceed anyway" or "force render."

---

## css_lock

### What it protects

Signals that a CSS or template modification is actively in progress. Other operations that
would write to the same HTML slide files should check before proceeding.

### Setting and clearing

Track in a session state file or in-memory during pipeline runs:

```json
{
  "locked_by": "theme-update",
  "template": "stat-callout",
  "started_at": "2025-03-15T10:14:00Z",
  "reason": "Updating heading font-size across stat-callout slides"
}
```

Set when beginning a CSS or template edit that spans multiple slides.
Clear immediately after the edit completes or fails.

### Check before proceeding

Before any CSS or template write:
```
if css_lock is set:
  WARN "A CSS edit is in progress (started [time], reason: [reason]). Proceed anyway?"
  → Wait for user confirmation
```

---

## render_guard

### What it protects

Signals that a render/conversion pass is actively running. Starting a second conversion while
one is in progress would produce race conditions on the output file.

### Key structure

```json
{
  "deck_name": "q1-results",
  "version": "v3",
  "pass": 2,
  "total_passes": 3,
  "started_at": "2025-03-15T10:18:00Z"
}
```

### Check before proceeding

Before starting any conversion:
```
if render_guard is set:
  WARN "A conversion is in progress for [deck_name] [version], pass [pass]/[total_passes].
        Proceed anyway?"
  → Wait for user confirmation
```

---

## Handling Stale Flags

A stale flag (set but never cleared due to an interrupted session) should not block permanently.

**Stale detection heuristic**: If `started_at` is > 10 minutes ago, treat as stale.

```
if flag is set and (now - started_at) > 600 seconds:
  WARN "[flag] appears stale (started [time]). Clearing and proceeding."
  clear flag
  continue without advisory check
```

---

## Coordinating Audit + Edit Flows

When the audit identifies issues and the user requests an inline fix:

```
1. Check css_lock → clear to proceed
2. Set css_lock
3. Apply CSS / template correction to HTML slides
4. Clear css_lock
5. Check render_guard → clear to proceed
6. Set render_guard for re-conversion
7. Run slide-html-to-pptx
8. Run slide-validate
9. Clear render_guard
10. Report corrected slide status
```

For bulk remediation ("fix all issues"):
- Process FAIL findings first, then WARN, then INFO
- Set css_lock once for the batch — do not toggle per slide
- Clear css_lock after all corrections applied
- Then run a single re-conversion pass with render_guard

# Constraint Persistence

How constraints survive session boundaries and are injected into every agent
prompt. Constraints are structural (file-based, hook-enforced), not behavioral
(instruction-based, memory-dependent).

## constraints.json Location

Per-project constraints live in the deck directory:

```
/path/to/deck/constraints.json
```

This file persists on disk between sessions. An agent cannot forget a constraint
that is injected into its prompt and enforced by a hook.

## constraints.json Format and Schema

```json
{
  "constraints": [
    {
      "id": "css-vertical-centering",
      "phase_added": "build",
      "severity": "blocking",
      "rule": "Slide main content container: display:flex; flex-direction:column; justify-content:center; align-items:center. Cards inside: never align-items:stretch, never height:100% on card body. Use flex-grow:1 with width:0 on cards.",
      "reason": "7 recurrences, 22 CSS edits in prior sessions",
      "applies_to": ["build", "validate", "export"]
    },
    {
      "id": "notes-inline-only",
      "phase_added": "default",
      "severity": "blocking",
      "rule": "Speaker notes in notes-data.js as window.SLIDE_NOTES[slideNumber]. Never fetch() — fails on file:// protocol.",
      "reason": "Broke identically in v1 and v3",
      "applies_to": ["build", "export"]
    }
  ]
}
```

### Field Definitions

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique kebab-case identifier. Must be stable across sessions. |
| `phase_added` | string | Phase when constraint was created: `"default"`, `"build"`, `"validate"`, `"export"` |
| `severity` | string | `"blocking"` or `"recommended"` (see Severity Levels below) |
| `rule` | string | The constraint text injected into agent prompts. Must be actionable. |
| `reason` | string | Why this constraint exists. Reference the bug or session where it was needed. |
| `applies_to` | array of strings | Phases where this constraint applies. Options: `"brainstorm"`, `"build"`, `"validate"`, `"export"` |

### Optional Fields (for per-slide overrides)

| Field | Type | Description |
|---|---|---|
| `slide_override` | object | Per-slide exception. Key is slide number (string), value is modified rule or `"skip"`. |
| `expires_after` | string | ISO date after which constraint is no longer active (for temporary exceptions). |

Example with per-slide override:

```json
{
  "id": "card-flex-rule",
  "severity": "blocking",
  "rule": "Cards must use width:0;flex-grow:1, never flex:1",
  "reason": "flex:1 causes card overflow in extraction",
  "applies_to": ["build"],
  "slide_override": {
    "12": "skip — slide 12 uses a fixed-width sidebar layout, flex:1 is intentional"
  }
}
```

## Injection Protocol

The orchestrator reads `constraints.json` and appends all applicable constraints
to every agent prompt before dispatch.

Format injected into every agent prompt:

```
## Constraints (MANDATORY)

The following constraints apply to the [PHASE] phase. Violations will be caught
by automated hooks and will require rework.

[BLOCKING]
1. [css-vertical-centering] Slide main content container: display:flex; flex-direction:column; justify-content:center; align-items:center. Cards inside: never align-items:stretch, never height:100% on card body.
   Reason: 7 recurrences, 22 CSS edits in prior sessions

[RECOMMENDED]
4. [mechanism-before-outcome] Every slide that makes a capability claim must show the mechanism before stating the outcome.
   Reason: v3 had 5/6 core concepts rated ASPIRATIONAL
```

The `constraint-injection-check` PreToolUse hook verifies that any agent
dispatch during a pipeline workflow includes `## Constraints (MANDATORY)` in
the prompt. If missing, it blocks the dispatch.

## "Learn Constraint" Protocol

When a bug requires more than one attempt to fix, write a constraint before
moving on. This prevents the same bug from recurring in future sessions.

**Trigger**: User says "wrong", "broken", "doesn't work", "try again", or any
correction message after a fix attempt.

**Steps**:
1. Fix the bug
2. Identify the root cause (what assumption was wrong?)
3. Write a new constraint to `constraints.json`:
   - `id`: descriptive kebab-case name
   - `phase_added`: current phase
   - `severity`: `"blocking"` if the bug caused visible failure, `"recommended"` otherwise
   - `rule`: what to do differently
   - `reason`: reference this session and the bug description
   - `applies_to`: phases where this pattern could recur
4. Confirm the constraint was written before moving to the next task

The `constraint-persistence` Stop hook checks: if user corrections were made
in this session and no new constraint was written, it warns before the session ends.

## Severity Levels

### blocking
- Must be followed without exception
- Violation will cause visible failure or rework
- Hook-enforced where possible
- A slide cannot be marked PASS if a blocking constraint is violated
- Example: `align-items:stretch` causes layout collapse

### recommended
- Should be followed; deviation requires documented justification
- Violation degrades quality but does not cause hard failure
- Per-slide overrides are acceptable with documented reason
- Example: `mechanism-before-outcome` — a proof slide may legitimately lead with outcome

## applies_to Phase Filtering

The orchestrator filters constraints by phase before injecting:

```python
def get_constraints_for_phase(constraints_json, phase):
    return [
        c for c in constraints_json["constraints"]
        if phase in c.get("applies_to", [])
    ]
```

A build agent receives only constraints where `"build"` is in `applies_to`.
A validate agent receives only constraints where `"validate"` is in `applies_to`.

## Constraint Lifecycle

```
created → active → (optionally) overridden per-slide → (optionally) retired
```

- **created**: Written to `constraints.json` during the session when the bug was found
- **active**: Injected into every applicable agent prompt, enforced by hooks
- **overridden per-slide**: `slide_override` field documents exceptions for specific slides
- **retired**: Remove from `constraints.json` only if the underlying pattern is no longer
  possible (e.g., the code was refactored to prevent the violation structurally)

Do not remove constraints because "we'll remember this time." File-based
persistence is the point — constraints survive any agent, any session, any
model version.

## Default Constraints

The skill ships with a pre-populated `constraints.json` containing lessons from
prior sessions. See `skill-architecture.md` Section 7 for the full default set.
These defaults cover: CSS centering rules, notes-inline-only, visual verification
required, no-tmp-for-html, mechanism-before-outcome, client-specificity, and
navigation-in-every-slide.

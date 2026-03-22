# Constraint Registry — deck-pipeline

Cross-phase constraint format, 10 default constraints, and the Learn Constraint
protocol. Constraints are the mechanism by which session lessons survive across
sessions and across agents.

---

## Constraint JSON Schema

Constraints live in `{deck_dir}/state/constraints.json`. The file is read by
the orchestrator before every agent dispatch. New constraints are written during
the Learn Constraint protocol.

```json
{
  "constraints": [
    {
      "id": "constraint-id-kebab-case",
      "phase_added": "build | validate | export | default",
      "severity": "blocking | recommended",
      "rule": "Exact, actionable rule text. Should be specific enough that a build agent can apply it without interpretation.",
      "reason": "Why this constraint exists. Reference the session, bug count, or failure mode that created it.",
      "applies_to": ["source-inventory | personas | brainstorm | architecture | build | validate | polish | export"]
    }
  ]
}
```

**Field definitions**:

- `id` — unique kebab-case identifier, human-readable
- `phase_added` — the phase when the constraint was discovered, or "default" for
  pre-populated constraints
- `severity` — `blocking` constraints must be followed exactly; `recommended`
  constraints should be followed unless there is a documented reason not to
- `rule` — the actionable rule text injected into agent prompts
- `reason` — the historical reason; shown to agents so they understand the
  consequence of violating the rule
- `applies_to` — array of phase names; the orchestrator injects this constraint
  only into agents running in a listed phase

**Severity behavior**:
- `blocking`: if the constraint is violated, stop and fix before proceeding. The
  css-violation-detector hook will flag blocking constraint violations in HTML.
- `recommended`: if the constraint cannot be met for a specific slide, document
  the exception in deck-state.json open_issues and proceed.

---

## Constraint Lifecycle

```
CREATED (written to constraints.json by Learn Constraint protocol)
    |
    v
ACTIVE (injected into all agent prompts for applicable phases)
    |
    v
OVERRIDDEN (per-slide exception, logged in deck-state.json open_issues)
    (constraint remains active for all other slides)
```

Constraints are never deleted. If a constraint becomes obsolete, add a
`"retired": true` field and a `"retired_reason"`. The orchestrator filters out
retired constraints from injection.

---

## Learn Constraint Protocol

**Trigger**: After any user correction that required more than one fix attempt.
"More than one fix attempt" means the user reported a bug, a fix was applied, and
the user reported the same or related bug again.

**Procedure**:
1. Identify the root cause of the repeated failure
2. Formulate a rule that, if present in the agent's prompt, would have prevented it
3. Write a new constraint entry to constraints.json with:
   - A unique id derived from the failure type
   - `phase_added` set to the current phase
   - `severity` as `blocking` if the bug caused visible output failure, `recommended`
     if it caused quality degradation
   - The exact rule text — specific enough to be actionable without interpretation
   - The reason, referencing this session explicitly
   - The phases where it should apply
4. Confirm to the user: "Constraint '{id}' written to constraints.json. It will
   apply to all future sessions."

**When NOT to write a constraint**: One-off user preference changes (e.g. "make
this slide's heading larger") do not become constraints. Constraints encode
systematic failure patterns, not individual style choices.

---

## 10 Default Constraints

These constraints ship with the skill in a pre-populated constraints.json. They
encode the highest-rework failures from prior sessions. Every new project starts
with these active.

---

### 1. css-vertical-centering

```json
{
  "id": "css-vertical-centering",
  "phase_added": "default",
  "severity": "blocking",
  "rule": "Slide main content container: display:flex; flex-direction:column; justify-content:center; align-items:center. Cards inside: never align-items:stretch, never height:100% or min-height:100% on card body. Use flex:1 ONLY on the main slide content div, never on cards.",
  "reason": "7 recurrences, 22 CSS edits, 1 dedicated 783KB cleanup agent in prior session. align-items:stretch was independently chosen by every build agent that did not have this constraint.",
  "applies_to": ["build", "validate", "export"]
}
```

**Context**: This is the single highest-rework constraint in the dataset. Every
build agent, when not constrained, defaults to `align-items: stretch`. The
PostToolUse hook `css-violation-detector` will flag violations in written HTML.

---

### 2. notes-inline-only

```json
{
  "id": "notes-inline-only",
  "phase_added": "default",
  "severity": "blocking",
  "rule": "Speaker notes must be stored in notes-data.js as window.SLIDE_NOTES[slideNumber]. Never use fetch() to load notes — fails on file:// protocol. Notes content (delivery instructions, RFP citations, talking points) must never appear in the slide HTML body.",
  "reason": "Broke identically in both v1 and v3 sessions. fetch() fails silently on file:// protocol, causing notes to be unavailable during presentation without any visible error.",
  "applies_to": ["build", "export"]
}
```

**Context**: The css-violation-detector hook also watches for `fetch(` in script
tags referencing notes or JSON files.

---

### 3. visual-verification-required

```json
{
  "id": "visual-verification-required",
  "phase_added": "default",
  "severity": "blocking",
  "rule": "No build batch, validation pass, or export operation is declared complete without visual verification. Take screenshots of representative slides (1, N/4, N/2, 3N/4, N) and read them with vision. CLI output alone is never sufficient.",
  "reason": "PPTX export declared success ('41 slides, zero fallbacks') from stdout. The deck was unreadable. Visual verification was skipped. This constraint exists because CLI output cannot detect rendering failures.",
  "applies_to": ["build", "validate", "export"]
}
```

**Context**: The Stop hook `export-visual-verification` catches cases where this
constraint was skipped during export.

---

### 4. source-before-brainstorm

```json
{
  "id": "source-before-brainstorm",
  "phase_added": "default",
  "severity": "blocking",
  "rule": "All source documents must be read and the facts manifest must be complete before any brainstorming begins. If a user references a document not in the facts manifest during brainstorm or build, pause and incorporate it before continuing.",
  "reason": "Multiple mid-session source discoveries caused content rework in both v1 and v3. Critical data (named systems, financial figures, union sensitivity flags) was discovered after brainstorming was already complete.",
  "applies_to": ["brainstorm", "architecture", "build"]
}
```

**Context**: Phase 1 is a hard gate. The orchestrator will not advance to Phase 2
until facts-manifest.json exists and the user has confirmed completeness.

---

### 5. no-tmp-for-html

```json
{
  "id": "no-tmp-for-html",
  "phase_added": "default",
  "severity": "blocking",
  "rule": "Never write HTML files to /tmp/ for processing. Use a subdirectory within the deck directory. All relative CSS/JS paths must be audited after any file copy or move operation. Use absolute paths for CSS references in any generated temp files.",
  "reason": "PDF export lost all styling because temp files in /tmp/ broke relative CSS references. Chrome rendered unstyled pages. The CLI reported success.",
  "applies_to": ["export"]
}
```

**Context**: The PreToolUse hook `prevent-tmp-html` will block Bash commands that
write HTML to /tmp/.

---

### 6. mechanism-before-outcome

```json
{
  "id": "mechanism-before-outcome",
  "phase_added": "default",
  "severity": "recommended",
  "rule": "Every slide that makes a capability claim must show the mechanism (how it works) before stating the outcome (what it delivers). A concept that is named but not explained is a label, not a capability. Target: 30-37% of slides should be mechanism slides.",
  "reason": "v3 had 5/6 core concepts rated ASPIRATIONAL — named correctly, explained insufficiently. The validation-reality lens flagged them as PARTIAL or ASPIRATIONAL because the mechanism was absent.",
  "applies_to": ["brainstorm", "architecture", "build", "validate"]
}
```

**Context**: Applied by the `brainstorm-skeptic` as the primary challenge test.
Applied by the `validation-lens` (Making It Real) during Phase 6.

---

### 7. client-specificity

```json
{
  "id": "client-specificity",
  "phase_added": "default",
  "severity": "recommended",
  "rule": "Every slide must pass the client specificity test: does it contain a named system, a dollar figure, or a named metric specific to this client? Slides that could be reused for another client without changes are incomplete.",
  "reason": "Validation found Acts 1-2 were 'indistinguishable from a capable-but-generic AI delivery proposal'. Named systems from the facts manifest must appear in slides, not generic platform names.",
  "applies_to": ["build", "validate"]
}
```

**Context**: The facts manifest's `named_systems` and `named_programs` arrays are
the source of truth for client-specific terminology.

---

### 8. slide-count-discipline

```json
{
  "id": "slide-count-discipline",
  "phase_added": "default",
  "severity": "recommended",
  "rule": "Set a hard slide cap during architecture phase (recommended: 26-32 main slides). Every slide addition must justify a corresponding removal. If the deck exceeds the cap, run a balance audit before proceeding.",
  "reason": "v3 expanded from 20 to 41+51=92 slides. Flow cohesion rated 6.5/10. 'Acts 2 and 3 are overweight.' Unbounded slide addition destroyed the narrative arc.",
  "applies_to": ["architecture", "build"]
}
```

**Context**: The slide cap is set in slide-plan.md during Phase 4. The orchestrator
checks it during Phase 5 — any build agent batch that would exceed the cap triggers
a balance audit prompt before the agent is dispatched.

---

### 9. navigation-in-every-slide

```json
{
  "id": "navigation-in-every-slide",
  "phase_added": "default",
  "severity": "blocking",
  "rule": "Every slide HTML file must include navigation elements (prev/next links or navigation pill). Navigation is a baseline requirement, not a post-build addition. Build agents must include navigation in their initial output, not as a second pass.",
  "reason": "v1 initial build had no navigation. Treated as an afterthought, then required retrofitting all slides — equivalent extra work to building the navigation correctly the first time.",
  "applies_to": ["build"]
}
```

**Context**: The css-violation-detector hook can be extended to check for absence
of navigation elements in written slide HTML.

---

### 10. content-balance-ratio

```json
{
  "id": "content-balance-ratio",
  "phase_added": "default",
  "severity": "recommended",
  "rule": "Target content ratio: 30% client proof / 40% solution mechanism / 30% both. If proof exceeds 40%, identify redundancy clusters and replace with mechanism slides. Run balance audit at 80% build completion.",
  "reason": "v3 was 55% proof, 30% solution. Seven solution concepts had zero slides. The deck told the client what Accenture had done, not how the proposed solution would work.",
  "applies_to": ["validate"]
}
```

**Context**: The `balance-auditor` agent enforces this ratio during Phase 6. The
`flow-reviewer` checks that the ratio imbalance does not create act-level pacing
problems.

---

## Initializing constraints.json for a New Project

When starting a new project without an existing constraints.json, initialize it
with all 10 default constraints above. Copy the JSON blocks verbatim into the
new file under the `"constraints"` array key.

Command to initialize (run from the deck directory):
```bash
mkdir -p state
```

Then write state/constraints.json with all 10 defaults. The orchestrator will
read and inject them from the first agent dispatch onward.

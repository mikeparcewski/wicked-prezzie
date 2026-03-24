---
name: workflow
description: |
  Methodology-only orchestrator for the full deck-building workflow. Manages
  phase state, gate conditions, constraint injection, and subagent dispatch.
  No script — Claude drives the loop directly from this SKILL.md.
  NOT for converting existing HTML slides to PPTX — that is convert.

  Loads phase definitions from the active workflow template YAML (templates/*.yaml)
  instead of hardcoded phases. Template selection happens in start, stored in
  deck-state.json as template: "template-name".

  Use when: "build a full deck", "build me a deck about X", "create a presentation from scratch",
  "run the deck workflow", "start the deck pipeline", "make a deck from these documents"
---

# workflow — Orchestrator

This skill owns the phase state machine for the full deck-building workflow. It
does not write slides, run brainstorms, or build exports — it dispatches
phase-specific agents to do that work and manages transitions between phases.

**Template-driven phases**: The phase sequence, gate conditions, personas, and
validation lenses are loaded from the active workflow template YAML file, not
hardcoded. The template is selected by `start` and stored in `deck-state.json`.

**Relationship to convert**: `workflow` is the content workflow
(topic to approved deck). `convert` is the conversion workflow (HTML to
PPTX). workflow runs first; convert runs after build is complete.

## Reference Files

| File | Purpose | Load When |
|------|---------|-----------|
| `references/phase-definitions.md` | Default phase definitions, gate conditions, agent definitions per phase | Phase transition or gate check (supplementary to template) |
| `references/constraint-registry.md` | Constraint JSON schema, 10 default constraints, Learn Constraint protocol | Constraint read/write or new constraint registration |
| `references/agent-catalog.md` | Prompt templates for all agents, parallelism rules, output contracts | Before dispatching any agent |
| `references/deck-claude-md.md` | Per-deck CLAUDE.md generation: sections, derivation sources, agent consumption, update protocol | Phase 1 completion or when updating editorial directives |

---

## Hub-and-Spoke Model

One orchestrator (this skill) owns phase transitions. Phase-specific skills
load on demand. This keeps the orchestrator context lean regardless of which
phase is active. Each phase gets its own context budget.

The user invokes `/workflow`. The orchestrator reads `deck-state.json`,
determines the current phase, and loads the relevant phase skill. It enforces
gate conditions before advancing.

Phase skills live as sibling skills in `skills/`. They are NOT loaded into the
orchestrator's context permanently — only the active phase skill is loaded.

---

## Template-Driven Phase Machine

### Loading the Template

On session start or first invocation:

1. Read `deck-state.json` → get `template` field (e.g., `"training-workshop"`)
2. Load `templates/{template}.yaml` from the project root
3. Extract `phases` array — this defines the phase sequence for this deck
4. Extract `personas`, `validation.lenses`, `validation.pass_threshold`, `notes`,
   and `export` configuration
5. The template YAML is the authoritative source for phase sequence and gate
   conditions

If `deck-state.json` has no `template` field, default to `"general"`.

### Phase State Machine

The phase sequence is defined by the template's `phases` array. Each phase has:

- `id` — unique identifier (used in deck-state.json)
- `name` — human-readable name
- `purpose` — what this phase accomplishes
- `gate.condition` — what must be true to advance
- `gate.artifacts` — files that must exist
- `agents` — agent roles to dispatch
- `skippable` — whether the user can skip this phase

**Transition rules** (same regardless of template):
- **Linear by default**: phases execute in template-defined order
- **Skip-back allowed**: any phase may trigger a return to an earlier phase when
  a gap is discovered
- **Skip-forward requires approval**: jumping past a gate requires explicit user
  confirmation and a logged warning entry in deck-state.json
- **Skippable phases**: if `skippable: true`, the user can elect to skip the phase.
  The orchestrator notes this in deck-state.json but does not warn.
- **Phase completion is gated**: the orchestrator checks the gate condition before
  advancing. A phase is not complete because the agent says it is — it is
  complete when the artifacts exist and meet the gate condition.

### Phase Tracking in deck-state.json

```json
{
  "template": "training-workshop",
  "deck_directory": "/path/to/deck",
  "current_phase": "learning-design",
  "phase_history": [
    {"id": "source-inventory", "status": "complete", "completed_at": "..."},
    {"id": "learning-design", "status": "in-progress", "started_at": "..."}
  ],
  "skipped_phases": [],
  "open_issues": [],
  "build_progress": {}
}
```

---

## Per-Deck CLAUDE.md Generation (First Phase Exit)

After the first phase's gate condition is satisfied (regardless of which template
is active — every template starts with a source/inventory/story-arc phase) and
the workflow template is confirmed, the orchestrator generates
`{deck_dir}/CLAUDE.md` — a per-deck editorial context file that all subsequent
agents consume.

This file captures six sections: Audience, Tone, Key Themes, Terminology, Brand
Constraints, and Editorial Preferences. It is derived from three sources:
user-stated directives (highest priority), source document signals extracted
during the first phase, and template editorial defaults (lowest priority).

**Generation is a first-phase exit task.** The orchestrator writes CLAUDE.md,
presents it to the user for review, and incorporates feedback before advancing
to the next phase.

**After the first phase, every agent prompt must include `## Deck Editorial Context`
populated from the per-deck CLAUDE.md.** This is mandatory — same enforcement
level as constraint injection (Guard 1). An agent prompt dispatched after the
first phase without this section is malformed and must not be sent.

**CLAUDE.md is updated incrementally** throughout the session as the user provides
editorial feedback. It is not a static artifact — it grows as preferences are
discovered. Terminology corrections, tone adjustments, and theme refinements are
written to CLAUDE.md immediately, not deferred to a phase boundary.

**CLAUDE.md vs constraints.json**: CLAUDE.md handles editorial and design
directives (how the deck should sound and look). constraints.json handles
runtime-learned rules (what breaks during production). They are complementary.
See `references/deck-claude-md.md` for the full specification.

---

## Template Override

The user can switch templates mid-workflow under these conditions:

1. **Before build phase**: Template switch is safe. The orchestrator:
   - Reads the new template YAML
   - Maps completed phases to the new template's phase sequence (by `id` match)
   - Any completed phase that exists in the new template keeps its `complete` status
   - Any completed phase that does not exist in the new template is noted but
     does not block progress
   - The current phase resets to the first incomplete phase in the new template
   - Updates `template` in deck-state.json

2. **During or after build phase**: Template switch is warned. Slides have been
   generated against the old template's personas, validation lenses, and notes
   schema. The orchestrator warns:
   "You have slides built against the {old} template. Switching to {new} means
   validation will use different lenses and the notes tab structure will change.
   Continue anyway?"

3. **Template switch never deletes artifacts.** Completed work is preserved.
   Only the phase sequence, validation lenses, and personas change.

To switch: the user says "switch to {template-name}" or "change template to
{template-name}" at any point during the workflow.

---

## Constraint Injection Rule

**Before dispatching any agent, read `constraints.json` and include all active
constraints in the agent prompt. This is not optional.**

Procedure:
1. Read `deck-state.json` to determine current phase
2. Read `constraints.json` to get all constraint entries
3. Filter constraints where `applies_to` includes the current phase id
4. Inject filtered constraints into the agent prompt under `## Constraints (MANDATORY)`
5. If constraints.json does not exist, initialize it from the defaults in
   `references/constraint-registry.md` before proceeding

An agent prompt without a `## Constraints (MANDATORY)` section is malformed and
must not be dispatched.

---

## Subagent Dispatch Protocol

**Max 4 agents in parallel.** Parallelism rules per agent type are defined in
`references/agent-catalog.md`.

Every agent prompt must follow this structure:

```
## Your Role
[Role-specific instructions from the phase skill or agent catalog]

## Project Context
[Compressed facts manifest: key facts, named systems, key figures,
 sensitivity flags. Not the full manifest — the summary fields only.]

## Deck Editorial Context
[From per-deck CLAUDE.md — audience, tone, themes, terminology, brand.
 Mandatory after first phase completion.]

## Constraints (MANDATORY)
[All constraints from constraints.json where applies_to includes current phase.
 Injected by the orchestrator. Never omit this section.]

## Your Task
[Specific task for this agent instance, including which slides or sections]

## Output Format
[Exact file paths to write, schema to follow]
```

**When to dispatch subagents** (production work):
- Building slides (1 agent per 3-5 slides, batched by act)
- Running brainstorm teams (1 agent per team, up to 3 parallel)
- Running validation lenses (1 agent per lens, up to 4 parallel — lenses come
  from the active template's `validation.lenses` array)
- Running review teams (1 agent per team, 3 parallel)
- Export operations (1 agent per format — formats come from template `export`)

**When to work inline** (no subagent — orchestrator handles directly):
- Reading deck-state.json and determining current phase
- Gate condition checks (does the file exist? does it meet schema?)
- User interaction (asking for approval, presenting options)
- Small edits to 1-2 slides after user feedback (threshold: 1-2 inline, 3+ dispatch)
- Constraint registration (Learn Constraint protocol)
- Template override handling

---

## Template-Specific Behavior

The orchestrator adapts its behavior based on template configuration:

### Personas
The template's `personas.brainstorm` array defines the dreamer-skeptic teams
used during brainstorm phases. The orchestrator passes these to the brainstorm
skill instead of using hardcoded personas.

### Validation Lenses
The template's `validation.lenses` array defines what validation checks run.
Each lens has a `name` and `checks` list. The orchestrator dispatches one agent
per lens during the validate phase.

### Pass Threshold
The template's `validation.pass_threshold` (default 75) determines the minimum
score for validation to pass. Higher thresholds (executive-briefing: 85) require
more rigorous validation. Lower thresholds (project-status: 70) allow faster
iteration.

### Notes Schema
The template's `notes` configuration defines speaker notes tab labels. Tab 3
varies by template (References, Decision Points, Learning Objectives, Timing
Notes, Data Sources, Metrics). This is passed to the build agents so they
generate notes with the correct tab structure.

### Export Formats
The template's `export` configuration defines available formats and the default.
The orchestrator uses this during the export phase to determine which format
agents to dispatch.

---

## Anti-Pattern Guards

These six rules are always active, regardless of phase or template. They encode
lessons from prior session analysis.

**Guard 1 — Constraint inheritance**: Never dispatch a build agent without
reading constraints.json first. The constraint injection rule above is the fix.

**Guard 2 — Visual verification is not optional**: No build batch, validation
pass, or export is declared complete on CLI output alone. Screenshots of
representative slides (1, N/4, N/2, 3N/4, N) must be read with vision before
declaring any phase complete. "Zero fallbacks" is not verification.

**Guard 3 — Cross-session persistence**: When a user correction requires more
than one fix attempt, write a new constraint to constraints.json before ending
the session. Bugs fixed without being written to constraints.json will recur in
future sessions.

**Guard 4 — Spacing negotiation**: When a spacing request is ambiguous, ask for
a target measurement or reference element before editing. After any spacing edit,
offer three options with specific pixel values. Batch related spacing changes.
Do not make single-value blind edits in response to vague feedback.

**Guard 5 — Source-before-brainstorm**: Do not advance past the first phase until
the user explicitly confirms all source documents are captured. If a source
document is referenced in brainstorm or build that is not in the facts manifest,
pause and incorporate it before continuing.

**Guard 6 — No HTML to /tmp/**: HTML files written to /tmp/ break relative CSS
paths. All temp files must be created within the deck directory. Audit all
href/src paths after any file copy or move operation.

---

## State File Locations

All state files live relative to the deck project directory set in the first phase.

| File | Location | Purpose |
|------|----------|---------|
| `deck-state.json` | `{deck_dir}/state/deck-state.json` | Phase history, current phase, template, slide plan, build progress, open issues |
| `constraints.json` | `{deck_dir}/state/constraints.json` | Accumulated constraints, carries across sessions |
| `facts-manifest.json` | `{deck_dir}/state/facts-manifest.json` | Structured digest of all source documents |
| `CLAUDE.md` | `{deck_dir}/CLAUDE.md` | Per-deck editorial context: audience, tone, themes, terminology, brand, preferences |

If the deck directory has not been set yet (new project), prompt the user for it
during the first phase initialization and write it as `deck_directory` in
deck-state.json.

On session start: read deck-state.json → load template YAML → determine current
phase → load phase skill → continue. Do not re-read full conversation history.

---

## Invocation Patterns

```
/workflow                    # Start or resume at current phase
/workflow status             # Show current phase, template, blockers, progress
/workflow skip-to build      # Jump to phase (warns about skipped gates)
/workflow switch-template X  # Switch to template X (see Template Override rules)
```

Direct phase invocation is also supported (phase skills are sibling skills).
They will warn if prerequisites are unmet.

---

## Session Start Procedure

1. Check if `deck-state.json` exists in any likely location (ask user if not found)
2. If exists: read current_phase, template, open_issues, build_progress
3. If not exists: initialize first phase of the selected template (or prompt for
   template selection if none recorded — normally handled by `start`)
4. Load the template YAML from `templates/{template}.yaml`
5. Read constraints.json (initialize from defaults if missing)
6. Report current state to user: template, phase, progress, any blocking issues
7. Prompt for next action or auto-advance if gate is already satisfied

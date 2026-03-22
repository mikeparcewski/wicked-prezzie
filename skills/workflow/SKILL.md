---
name: workflow
description: |
  Methodology-only orchestrator for the full deck-building workflow. Manages
  phase state, gate conditions, constraint injection, and subagent dispatch.
  No script — Claude drives the loop directly from this SKILL.md.
  NOT for converting existing HTML slides to PPTX — that is slide-pipeline.

  Use when: "build a full deck", "build me a deck about X", "create a presentation from scratch",
  "run the deck workflow", "start the deck pipeline", "make a deck from these documents"
---

# deck-pipeline — Orchestrator

This skill owns the phase state machine for the full deck-building workflow. It
does not write slides, run brainstorms, or build exports — it dispatches
phase-specific agents to do that work and manages transitions between phases.

**Relationship to slide-pipeline**: `deck-pipeline` is the content workflow
(topic to approved deck). `slide-pipeline` is the conversion workflow (HTML to
PPTX). deck-pipeline runs first; slide-pipeline runs after build is complete.

## Reference Files

| File | Purpose | Load When |
|------|---------|-----------|
| `references/phase-definitions.md` | 8-phase state machine, gate conditions, agent definitions per phase | Phase transition or gate check |
| `references/constraint-registry.md` | Constraint JSON schema, 10 default constraints, Learn Constraint protocol | Constraint read/write or new constraint registration |
| `references/agent-catalog.md` | Prompt templates for all agents, parallelism rules, output contracts | Before dispatching any agent |

---

## Hub-and-Spoke Model

One orchestrator (this skill) owns phase transitions. Phase-specific skills
load on demand. This keeps the orchestrator context lean (~180 lines) regardless
of which phase is active. Each phase gets its own context budget.

The user invokes `/deck-pipeline`. The orchestrator reads `deck-state.json`,
determines the current phase, and loads the relevant phase skill. It enforces
gate conditions before advancing.

Phase skills live as sibling skills in `skills/`. They are NOT loaded into the
orchestrator's context permanently — only the active phase skill is loaded.

---

## Phase State Machine

Eight phases, each with a gate condition that must pass before advancing.
Phase history and current state persist in `deck-state.json`.

```
Phase 1: Source Inventory
  Gate: facts-manifest.json exists + user confirms source list complete
  |
Phase 2: Personas
  Gate: persona-map.md written with full evaluation committee coverage
  |
Phase 3: Brainstorm
  Gate: synthesized-architecture.md approved by user (not auto-advanced)
  |
Phase 4: Architecture
  Gate: three-team review returns CONDITIONAL APPROVE on all lenses
  |
Phase 5: Build
  Gate: all slides per approved plan built + visual verification passed
  |
Phase 6: Validate
  Gate: council punch list complete, zero blocking items
  |
Phase 7: Polish
  Gate: flow review passed + balance audit within target ratios
  |
Phase 8: Export
  Gate: visual verification of export artifacts passed
```

Linear by default. Phases may skip back (e.g. build agent discovers architecture
gap — return to Phase 4). Never skip forward past a gate without explicit user
approval and a logged warning in deck-state.json.

See `references/phase-definitions.md` for full gate conditions, context budgets,
and phase-specific agent definitions.

---

## Constraint Injection Rule

**Before dispatching any agent, read `constraints.json` and include all active
constraints in the agent prompt. This is not optional.**

Procedure:
1. Read `deck-state.json` to determine current phase
2. Read `constraints.json` to get all constraint entries
3. Filter constraints where `applies_to` includes the current phase
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
[Compressed facts manifest: client name, named systems, key financial figures,
 sensitivity flags. Not the full manifest — the summary fields only.]

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
- Running validation lenses (1 agent per lens, up to 4 parallel)
- Running review teams (1 agent per team, 3 parallel)
- Export operations (1 agent per format)

**When to work inline** (no subagent — orchestrator handles directly):
- Reading deck-state.json and determining current phase
- Gate condition checks (does the file exist? does it meet schema?)
- User interaction (asking for approval, presenting options)
- Small edits to 1-2 slides after user feedback (threshold: 1-2 inline, 3+ dispatch)
- Constraint registration (Learn Constraint protocol)

---

## Anti-Pattern Guards

These six rules are always active, regardless of phase. They encode lessons from
the prior session analysis (32% rework rate, 18-hour session).

**Guard 1 — Constraint inheritance**: Never dispatch a build agent without
reading constraints.json first. The centering constraint was violated 7 times in
one session because agents received instructions without the constraint. The
constraint injection rule above is the fix.

**Guard 2 — Visual verification is not optional**: No build batch, validation
pass, or export is declared complete on CLI output alone. Screenshots of
representative slides (1, N/4, N/2, 3N/4, N) must be read with vision before
declaring any phase complete. "Zero fallbacks" is not verification.

**Guard 3 — Cross-session persistence**: When a user correction requires more
than one fix attempt, write a new constraint to constraints.json before ending
the session. Bugs fixed without being written to constraints.json will recur in
future sessions. The notes-on-file:// bug recurred identically across two
sessions because no constraint was written.

**Guard 4 — Spacing negotiation**: When a spacing request is ambiguous, ask for
a target measurement or reference element before editing. After any spacing edit,
offer three options with specific pixel values. Batch related spacing changes.
Do not make single-value blind edits in response to vague feedback.

**Guard 5 — Source-before-brainstorm**: Do not advance past Phase 1 until the
user explicitly confirms all source documents are captured. If a source document
is referenced in brainstorm or build that is not in the facts manifest, pause and
incorporate it before continuing.

**Guard 6 — No HTML to /tmp/**: HTML files written to /tmp/ break relative CSS
paths. All temp files must be created within the deck directory. Audit all
href/src paths after any file copy or move operation.

---

## State File Locations

All state files live relative to the deck project directory set in Phase 1.

| File | Location | Purpose |
|------|----------|---------|
| `deck-state.json` | `{deck_dir}/state/deck-state.json` | Phase history, current phase, slide plan, build progress, open issues |
| `constraints.json` | `{deck_dir}/state/constraints.json` | Accumulated constraints, carries across sessions |
| `facts-manifest.json` | `{deck_dir}/state/facts-manifest.json` | Structured digest of all source documents |

If the deck directory has not been set yet (new project), prompt the user for it
during Phase 1 initialization and write it as `deck_directory` in deck-state.json.

On session start: read deck-state.json → determine current phase → load phase
skill → continue. Do not re-read full conversation history.

---

## Invocation Patterns

```
/deck-pipeline                    # Start or resume at current phase
/deck-pipeline status             # Show current phase, blockers, progress
/deck-pipeline skip-to build      # Jump to phase (warns about skipped gates)
```

Direct phase invocation is also supported (phase skills are sibling skills).
They will warn if prerequisites are unmet.

---

## Session Start Procedure

1. Check if `deck-state.json` exists in any likely location (ask user if not found)
2. If exists: read current_phase, open_issues, build_progress
3. If not exists: initialize Phase 1 (Source Inventory)
4. Read constraints.json (initialize from defaults if missing)
5. Report current state to user: phase, progress, any blocking issues
6. Prompt for next action or auto-advance if gate is already satisfied

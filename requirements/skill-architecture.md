# Skill Architecture: Progressive-Loading Deck Builder

## Overview

A Claude Code skill suite that orchestrates the full deck-building workflow — from source inventory through final export — using progressive disclosure to keep context lean and constraints persistent. Designed to prevent the six process anti-patterns identified in the [CLIENT] session analysis (32% rework rate) while preserving the workflow patterns that worked (dreamer-skeptic brainstorms, multi-lens validation, council punch lists).

The architecture uses a **hub-and-spoke model**: one orchestrator skill owns the phase state machine, and phase-specific skills load on demand. Constraints that caused the most rework (CSS centering, notes placement, visual verification) are enforced via hooks, not via instructions that agents can forget.

---

## 1. Skill Structure

### Decision: Hub-and-Spoke, Not Monolith

One orchestrator skill (`deck-pipeline`) plus seven phase skills. Not a monolith because the [CLIENT] session hit context limits at ~18 hours. Not fully independent skills because phase transitions need a shared state contract.

```
.claude/skills/
  deck-pipeline/
    SKILL.md                    # Orchestrator (~180 lines)
    refs/
      phase-definitions.md      # Phase state machine, gate conditions
      constraint-registry.md    # Cross-phase constraint format
      agent-catalog.md          # All agent definitions
    state/
      deck-state.json           # Persisted between phases/sessions
      constraints.json          # Accumulated constraints
      facts-manifest.json       # Source material digest

  deck-source-inventory/
    SKILL.md                    # Phase 1 (~150 lines)
    refs/
      document-types.md         # How to handle PDFs, XLSX, DOCX, HTML decks
      manifest-format.md        # Facts manifest schema

  deck-personas/
    SKILL.md                    # Phase 2 (~120 lines)
    refs/
      persona-template.md       # 12-persona framework with pass/fail criteria
      dreamer-skeptic-pairing.md

  deck-brainstorm/
    SKILL.md                    # Phase 3 (~160 lines)
    refs/
      brainstorm-teams.md       # Three-team structure + synthesis rules
      content-principles.md     # Mechanism-before-outcome, two-layer proof, etc.

  deck-architecture/
    SKILL.md                    # Phase 4 (~180 lines)
    refs/
      three-team-review.md      # Narrative / Commercial / Technical lenses
      conflict-resolution.md    # How to reconcile brainstorm outputs
      slide-plan-format.md      # The approved plan schema

  deck-build/
    SKILL.md                    # Phase 5 (~180 lines)
    refs/
      html-template.md          # Slide HTML structure, CSS variables, card patterns
      css-constraints.md        # THE centering rules, flex rules, spacing rules
      notes-format.md           # notes-data.js schema, RFP mapping format

  deck-validate/
    SKILL.md                    # Phase 6 (~170 lines)
    refs/
      four-lens-validation.md   # POV clarity, RFP coverage, making-it-real, know-them
      council-punch-list.md     # Council composition, punch list format
      balance-audit.md          # Content ratio analysis, redundancy detection

  deck-export/
    SKILL.md                    # Phase 7-8 (~160 lines)
    refs/
      bundled-html.md           # Single-file HTML bundling recipe
      pdf-generation.md         # Chrome headless PDF with path audit
      pptx-strategy.md          # PPTX as handout format, not pixel replica
      visual-verification.md    # Screenshot + vision verification protocol
```

### How They Chain Together

The orchestrator (`deck-pipeline`) owns phase transitions. The user invokes `/deck-pipeline` and the orchestrator determines the current phase from `deck-state.json`, loads the relevant phase skill, and enforces the gate condition before advancing.

```
User: /deck-pipeline
  |
  v
deck-pipeline reads deck-state.json
  |
  +--> Phase not started? Load deck-source-inventory
  |
  +--> Phase 1 complete? Gate: facts-manifest.json exists
  |    Load deck-personas
  |
  +--> Phase 2 complete? Gate: persona-map written
  |    Load deck-brainstorm
  |
  +--> Phase 3 complete? Gate: synthesized architecture approved
  |    Load deck-architecture
  |
  +--> Phase 4 complete? Gate: three-team review CONDITIONAL APPROVE
  |    Load deck-build
  |
  +--> Phase 5 complete? Gate: all slides built per plan
  |    Load deck-validate
  |
  +--> Phase 6 complete? Gate: council punch list, zero blocking items
  |    Load deck-export
  |
  +--> Phase 7 complete? Gate: visual verification passed
       Done. Export artifacts available.
```

The user can also invoke any phase skill directly (`/deck-build`) for targeted work, but the skill will warn if prerequisites are unmet.

### Invocation Patterns

```
/deck-pipeline                    # Start or resume the full workflow
/deck-pipeline status             # Show current phase, blockers, progress
/deck-pipeline skip-to build      # Jump to build (warns about skipped gates)

/deck-build                       # Direct phase invocation
/deck-validate                    # Run validation independently
/deck-export pdf                  # Export specific format
```

---

## 2. Progressive Loading Strategy

### Tier 1: Always Visible (Orchestrator SKILL.md)

The orchestrator SKILL.md is always in context. It contains:

1. **Phase state machine** — the eight phases, their gate conditions, and transition rules
2. **Constraint injection rule** — "Before dispatching any agent, read `constraints.json` and include all active constraints in the agent prompt"
3. **Subagent dispatch protocol** — max 4 parallel agents, each gets constraints + facts-manifest summary
4. **Anti-pattern guards** — the six rules that are always active (see section 4)
5. **State file locations** — where to find/write deck-state.json, constraints.json, facts-manifest.json

This is approximately 150-180 lines. It does not contain any phase-specific instructions.

### Tier 2: Phase-Specific (Loaded Per Phase)

When a phase activates, the orchestrator loads that phase's SKILL.md. Each phase SKILL.md contains:

- **Purpose** — what this phase produces
- **Inputs required** — what must exist before this phase runs
- **Agent definitions** — which agents to dispatch, their prompts, their constraints
- **Output format** — what files this phase writes
- **Gate condition** — what must be true for this phase to be considered complete
- **Common patterns** — the 80% case for this phase

Phase SKILL.md files are 120-180 lines each. They reference `refs/` for deep-dive content.

### Tier 3: Reference Files (Loaded on Demand)

Reference files load only when a specific situation requires them. Examples:

- `html-template.md` loads when a build agent needs to create a slide
- `four-lens-validation.md` loads when validation agents are being dispatched
- `pdf-generation.md` loads only during export phase, only if PDF is requested
- `dreamer-skeptic-pairing.md` loads only during brainstorm setup

Each ref file is 200-300 lines, single-topic, self-contained.

### What Never Loads Unless Needed

- Export recipes (bundled HTML, PDF, PPTX) — only during export phase
- Deep-dive content principles (hallway line, protagonist arc, [union-agreement] audit) — only during brainstorm or validation
- Design system CSS variables and card patterns — only during build phase
- Conflict resolution rules — only during architecture phase when brainstorm outputs disagree

### Context Budget Per Phase

| Phase | Orchestrator | Phase SKILL | Refs Loaded | Constraints | Total Est. |
|-------|-------------|-------------|-------------|-------------|-----------|
| Source Inventory | 180 lines | 150 lines | 1 (document-types) | 0 | ~530 lines |
| Personas | 180 lines | 120 lines | 1 (persona-template) | ~20 lines | ~520 lines |
| Brainstorm | 180 lines | 160 lines | 2 (teams + content) | ~20 lines | ~860 lines |
| Architecture | 180 lines | 180 lines | 2 (review + conflict) | ~30 lines | ~890 lines |
| Build | 180 lines | 180 lines | 3 (template + CSS + notes) | ~50 lines | ~1110 lines |
| Validate | 180 lines | 170 lines | 3 (4-lens + council + balance) | ~50 lines | ~1100 lines |
| Export | 180 lines | 160 lines | 2 (format + verification) | ~50 lines | ~890 lines |

Build and Validate are the heaviest, which matches reality — they need the most context. But even at peak, total skill context is approximately 1100 lines, well under the point where context pollution causes drift.

### How Constraints Carry Across Phases

Constraints are persisted in `state/constraints.json`, not in conversation context. The format:

```json
{
  "constraints": [
    {
      "id": "css-vertical-centering",
      "phase_added": "build",
      "severity": "blocking",
      "rule": "Slide main content must use display:flex; flex-direction:column; justify-content:center; align-items:center. Never use align-items:stretch. Never set height:100% on card body.",
      "reason": "Caused 7 recurrences and 22 CSS edits in [CLIENT] v3 session",
      "applies_to": ["build", "validate", "export"]
    },
    {
      "id": "notes-inline-only",
      "phase_added": "build",
      "severity": "blocking",
      "rule": "Speaker notes must use inline window.SLIDE_NOTES in notes-data.js. Never use fetch() for notes — it fails on file:// protocol.",
      "reason": "Broke in both v1 and v3 sessions via identical root cause",
      "applies_to": ["build", "export"]
    }
  ]
}
```

The orchestrator's dispatch protocol requires: "Before creating any agent prompt, read constraints.json. Append all constraints where `applies_to` includes the current phase. This is not optional."

New constraints are added when a bug is fixed during a session. The build skill includes a "Learn Constraint" step: after any user correction that required more than one fix attempt, write a new constraint to constraints.json.

---

## 3. Context Management

### Problem Statement

The [CLIENT] v3 session ran 18 hours, dispatched 53 subagents, and accumulated enough context that later agents lost earlier constraints. The architecture must keep the main orchestrator context lean while ensuring every subagent has the constraints it needs.

### Strategy 1: Subagents for All Production Work

The orchestrator never writes slide HTML, never edits CSS, never creates brainstorm documents. It dispatches agents for all production work. This keeps the orchestrator's context clean — it only tracks phase state, dispatches agents, and evaluates their output.

**When to use subagents:**
- Building slides (1 agent per 3-5 slides, batched by act)
- Running brainstorm teams (1 agent per team, 3 parallel)
- Running validation lenses (1 agent per lens, 4 parallel)
- Running review teams (1 agent per team, 3 parallel)
- Export operations (1 agent per format)

**When to work inline (no subagent):**
- Reading deck-state.json and determining current phase
- Gate condition checks (does the file exist? does it meet the schema?)
- User interaction (asking for approval, presenting options)
- Small edits to 1-2 slides after user feedback
- Constraint registration

### Strategy 2: Facts Manifest as Context Proxy

The source inventory phase reads all reference documents and produces `facts-manifest.json` — a structured digest of every key fact, figure, app name, persona detail, and RFP requirement. Subsequent phases read the manifest, not the original documents.

```json
{
  "client": {
    "name": "...",
    "named_systems": ["ECHO", "CONNECT", "[System-C]", "NTAS", "vRepair"],
    "named_programs": ["Cheetah", "FIM-to-3GIS", "Visible"],
    "leadership": ["Villanueva", "Tenorio"],
    "ai_ecosystem": "GCP, Vertex AI, Gemini",
    "portfolio_size": "323 applications",
    "contract_value": "[total-value] total, [fee-value] annual"
  },
  "rfp_requirements": [
    {
      "section": "Section 3.1",
      "requirement": "...",
      "key_metrics": ["..."],
      "quoted_text": "..."
    }
  ],
  "financial_figures": {
    "total_contract": "[total-value]",
    "annual_value": "[fee-value]",
    "savings_target": "25% YoY",
    "fee_at_risk": "25% of fees"
  },
  "sensitivity_flags": {
    "sensitivity_unionized": true,
    "sensitivity_trigger_words": ["leaner teams", "headcount reduction", "right-sizing", "Role Transformation"],
    "sensitivity_safe_alternatives": ["workforce effectiveness", "team throughput", "Expanded Capability Model"]
  },
  "source_documents": [
    {
      "path": "...",
      "type": "RFP|prior-deck|exec-summary|reference-implementation",
      "summary": "...",
      "key_facts_extracted": 12
    }
  ]
}
```

This manifest is approximately 200-400 lines of JSON. Every build and brainstorm agent receives a compressed version (client name, named systems, financial figures, sensitivity flags) rather than the full source documents. The full manifest is available if an agent needs to drill deeper.

### Strategy 3: State File as Session Bridge

`deck-state.json` persists the full project state across sessions:

```json
{
  "project_name": "...",
  "deck_directory": "...",
  "current_phase": "build",
  "phase_history": [
    {"phase": "source-inventory", "completed": "2026-03-21T14:00:00Z", "artifacts": ["facts-manifest.json"]},
    {"phase": "personas", "completed": "2026-03-21T14:30:00Z", "artifacts": ["persona-map.md"]},
    {"phase": "brainstorm", "completed": "2026-03-21T16:00:00Z", "artifacts": ["brainstorm-synthesis.md"]},
    {"phase": "architecture", "completed": "2026-03-21T17:00:00Z", "artifacts": ["slide-plan.md"]}
  ],
  "slide_plan": {
    "total_slides": 28,
    "acts": [
      {"name": "The Weight", "slides": [1, 2, 3, 4, 5], "status": "built"},
      {"name": "The Proof", "slides": [6, 7, 8, 9, 10, 11], "status": "building"}
    ]
  },
  "build_progress": {
    "slides_built": [1, 2, 3, 4, 5, 6, 7],
    "slides_validated": [1, 2, 3, 4, 5],
    "slides_with_notes": [1, 2, 3, 4, 5, 6, 7]
  },
  "open_issues": [
    {"slide": 8, "issue": "two-column layout needs balance check", "severity": "recommended"}
  ]
}
```

When a new session starts, the orchestrator reads deck-state.json and constraints.json. It knows exactly where work left off without needing to re-read the full conversation history.

### Strategy 4: Agent Prompt Templates with Constraint Injection

Every agent prompt follows this structure:

```
## Your Role
[Role-specific instructions from the phase skill]

## Project Context
[Compressed facts manifest: client name, named systems, key figures]

## Constraints (MANDATORY)
[All constraints from constraints.json where applies_to includes this phase]

## Your Task
[Specific task for this agent instance]

## Output Format
[What to produce, where to write it]
```

The constraints section is injected by the orchestrator, not by the phase skill. This means a phase skill author cannot accidentally omit constraints. The orchestrator reads constraints.json and appends them to every agent prompt as a non-optional section.

---

## 4. Anti-Pattern Prevention

### Anti-Pattern 1: Build Without Constraint Inheritance

**What happened**: Build agents in both v1 and v3 created slides without the centering constraint. Each agent independently chose `align-items: stretch`, causing 22 CSS edits and a dedicated 783KB cleanup agent.

**Architectural prevention**:
- Constraints live in `constraints.json`, not in conversation memory
- The orchestrator's dispatch protocol injects constraints into every agent prompt
- The `css-constraints.md` ref file is loaded for every build agent, every time
- A `PostToolUse` hook on the Write tool checks any `.html` file write for `align-items: stretch` and `height: 100%` violations (see section 6)
- The deck ships with a pre-populated constraints.json containing the centering rules as defaults

**Why this works**: Constraints are structural (file-based, hook-enforced), not behavioral (instruction-based, memory-dependent). An agent cannot forget a constraint that is injected into its prompt and validated by a hook.

### Anti-Pattern 2: Validating by CLI Output, Not Visual Inspection

**What happened**: PPTX export reported "41 slides, zero fallbacks" from stdout. The deck was unreadable. Visual verification was skipped.

**Architectural prevention**:
- The `deck-export` skill has a hard rule: "No export is declared complete until visual verification passes"
- Visual verification is a distinct step in the export workflow, not an optional add-on
- The export skill dispatches a `visual-reviewer` agent after every export operation
- The `visual-verification.md` ref defines the protocol: screenshot slides 1, N/4, N/2, 3N/4, N. Read each screenshot with vision. Check for: dark background present, text readable, no content overflow, styling intact
- A `Stop` hook checks: if the conversation includes an export tool call but no subsequent Read of a screenshot file, warn before stopping

**Why this works**: The verification step is architecturally required, not just recommended. The Stop hook catches cases where it was skipped.

### Anti-Pattern 3: Same Bug Across Sessions (Notes on file://)

**What happened**: `fetch('notes.json')` fails on `file://` protocol. Fixed in v1. Recurred in v3 because the fix was not persisted as a constraint.

**Architectural prevention**:
- The "Learn Constraint" protocol: when a bug is fixed, the orchestrator writes it to constraints.json before moving on
- constraints.json persists on disk, surviving session boundaries
- The `notes-inline-only` constraint is a default constraint shipped with the skill
- Build agents receive this constraint in their prompt, every time

**Why this works**: Cross-session persistence is file-based, not memory-based. The constraint outlives any single session.

### Anti-Pattern 4: Micro-Iteration Loops on Spacing

**What happened**: Slide 20 went through 6 user messages in 4 minutes for spacing adjustments. Each was a single-value blind edit.

**Architectural prevention**:
- The `deck-build` skill includes a "Spacing Negotiation" protocol: when a spacing request is ambiguous, ask for the target measurement or reference element before editing
- After any spacing edit, offer three options with specific pixel values
- For pure visual adjustments, prompt the user to open the slide in browser during edits: "Open [path] in your browser. I will make three spacing options — tell me which looks right."
- Batch related spacing changes (if the user mentions multiple elements, fix all in one pass)
- A `PostToolUse` hook on Edit counts consecutive edits to the same file within 3 minutes. After 3 edits to the same file, it suggests: "We have made 3 edits to this slide. Would you like to open it in browser to review before we continue?"

**Why this works**: The protocol breaks the blind iteration loop by introducing visual feedback and batching.

### Anti-Pattern 5: Building Before Reading All Sources

**What happened**: Critical source documents were discovered mid-session after brainstorming and building were already underway, requiring content rework.

**Architectural prevention**:
- Phase 1 (Source Inventory) is a hard gate. The orchestrator will not advance to Phase 2 until `facts-manifest.json` exists and the user has confirmed the source list is complete
- The source inventory skill scans the project directory, lists all documents found, and asks: "Are there additional source documents I should read? List any file paths or directories."
- The facts manifest includes a `source_documents` array. During brainstorm and build, if a user references a document not in this array, the skill flags it: "This document is not in the facts manifest. Should I add it and re-run source inventory for this document?"
- The gate condition includes a confirmation prompt: "I found N source documents. Have I captured all available reference materials?"

**Why this works**: The gate forces completeness before forward progress. The flag catches mid-session discovery.

### Anti-Pattern 6: CSS Path Breaks When Files Move

**What happened**: Temp copies of slides in `/tmp/` broke relative CSS references. Chrome rendered unstyled pages.

**Architectural prevention**:
- The `deck-export` skill has an explicit rule: "All temp files must be created within the deck directory, not in /tmp/. Relative paths must remain valid."
- The `pdf-generation.md` ref includes a path audit step: "After creating any temp HTML file, read it with the Read tool and verify that all href/src paths resolve relative to the temp file location"
- The export skill uses absolute paths for CSS references in any generated temp files
- A `PreToolUse` hook on Bash checks: if the command writes an HTML file to `/tmp/`, warn: "Writing HTML to /tmp/ will break relative CSS paths. Use a subdirectory within the deck directory instead."

**Why this works**: The hook prevents the bad pattern before it executes. The ref file documents the correct approach.

---

## 5. Agent Definitions

### Orchestrator Agents (Dispatched by deck-pipeline)

These are not persistent agents — they are prompt templates that the orchestrator uses when dispatching subagents via the Agent tool.

#### source-scanner
- **Role**: Read all source documents and produce the facts manifest
- **Dispatched during**: Phase 1 (Source Inventory)
- **Parallelism**: 1-3 agents, one per document type (text docs, spreadsheets, prior decks)
- **Output**: Writes sections of facts-manifest.json
- **Key constraint**: Must extract exact figures, not approximate. Must flag any figure that appears inconsistent across sources.

#### persona-architect
- **Role**: Build the persona map with pass/fail criteria, must-hit slides, and hardest questions
- **Dispatched during**: Phase 2 (Personas)
- **Parallelism**: 1 agent (personas need to be internally consistent)
- **Output**: persona-map.md
- **Key constraint**: Must cover the full evaluation committee. Must include dreamer-skeptic pairing recommendations.

#### brainstorm-dreamer
- **Role**: The visionary half of a dreamer-skeptic pair. Generates the aspirational narrative for their angle.
- **Dispatched during**: Phase 3 (Brainstorm)
- **Parallelism**: 3 dreamers + 3 skeptics = 3 parallel pairs
- **Output**: Team brainstorm document (narrative/proof/commercial)
- **Key constraint**: Must ground every aspiration in a named client system or specific figure from the facts manifest. "Proof not pitch."

#### brainstorm-skeptic
- **Role**: The load-bearing skeptic. Challenges every claim, demands mechanisms, forces specificity.
- **Dispatched during**: Phase 3 (Brainstorm)
- **Parallelism**: Paired 1:1 with a dreamer
- **Output**: Annotated team brainstorm with skeptic challenges resolved
- **Key constraint**: Must apply the "mechanism before outcome" test. Any claim without a named mechanism is flagged as ASPIRATIONAL.

#### brainstorm-synthesizer
- **Role**: Reconcile 3 team brainstorm outputs into a single unified architecture
- **Dispatched during**: Phase 3 (Brainstorm), after all teams complete
- **Parallelism**: 1 agent (synthesis requires seeing all inputs)
- **Output**: synthesized-architecture.md with conflict resolution table, threading map, slide plan
- **Key constraint**: Must explicitly list every conflict between team outputs and document the resolution rationale.

#### review-narrative / review-commercial / review-technical
- **Role**: Three-team review with distinct lenses
- **Dispatched during**: Phase 4 (Architecture)
- **Parallelism**: 3 agents, one per lens
- **Output**: Review document with conditional approval, blocking conditions, reorder recommendations
- **Key constraints**:
  - Narrative: flow, emotional arc, audience engagement, protagonist continuity
  - Commercial: financial accuracy, legal exposure, [union-agreement]-safe language
  - Technical: data integrity, production feasibility, version audits

#### slide-builder
- **Role**: Build slide HTML per the approved plan
- **Dispatched during**: Phase 5 (Build)
- **Parallelism**: 3-4 agents, one per act
- **Output**: Individual slide HTML files + notes-data.js entries
- **Key constraints**: ALL constraints from constraints.json. CSS centering rules. Notes in notes-data.js not on slide body. Navigation pill present. Named systems from facts manifest, not generic terms.

#### validation-lens (x4)
- **Role**: Run one of the four validation lenses
- **Dispatched during**: Phase 6 (Validate)
- **Parallelism**: 4 agents, one per lens
- **Output**: Rated gap list with slide-level fixes
- **Lenses**:
  1. POV Clarity — are mechanisms visible, not just named?
  2. RFP Coverage — does every requirement have a slide?
  3. Making It Real — rate each concept as CONCRETE/PARTIAL/ASPIRATIONAL/MISSING
  4. Know Them — named systems, operational history, leadership awareness

#### council-reviewer
- **Role**: Final quality gate. Produces the punch list.
- **Dispatched during**: Phase 6 (Validate), after four lenses complete
- **Parallelism**: 1 agent (council needs all lens outputs as input)
- **Output**: Prioritized punch list with blocking/non-blocking classification, 3 deal-losers, 3 deal-winners
- **Key constraint**: Every item must specify exact slide number, exact fix instruction, source document, and blocking status.

#### balance-auditor
- **Role**: Check content ratio and redundancy clusters
- **Dispatched during**: Phase 6 (Validate)
- **Parallelism**: 1 agent
- **Output**: Ratio analysis (proof/solution/both), redundancy clusters, cut/add recommendations
- **Key constraint**: Target ratio 30% proof / 40% solution / 30% both. If proof exceeds 40%, must identify specific cuts.

#### flow-reviewer
- **Role**: Check deck flow as a presentation, not just a document
- **Dispatched during**: Phase 6 or 7 (Validate/Polish)
- **Parallelism**: 1 agent
- **Output**: Per-act ratings by persona, reorder recommendations, missing transitions, one-line-per-act summary test
- **Key constraint**: Rate each act through 5 persona lenses. If any act cannot be stated in one sentence, flag as unfocused.

#### visual-reviewer
- **Role**: Screenshot and verify slide rendering
- **Dispatched during**: Phase 5 (after build batches), Phase 7 (polish), Phase 8 (export)
- **Parallelism**: 1 agent (needs sequential screenshot access)
- **Output**: Pass/fail per slide with specific issues
- **Key constraint**: Must use vision to read screenshots. Cannot declare pass based on file existence or CLI output alone.

#### export-bundler
- **Role**: Produce export artifacts (PDF, bundled HTML, optionally PPTX)
- **Dispatched during**: Phase 8 (Export)
- **Parallelism**: 1 agent per format
- **Output**: Export files in the deck directory
- **Key constraints**: Temp files within deck directory, not /tmp/. Path audit before rendering. Visual verification before declaring success.

---

## 6. Hook Integration

### PreToolUse Hooks

#### `prevent-tmp-html`
- **Trigger**: Bash tool, when command writes `.html` to `/tmp/`
- **Action**: Block with message: "HTML files must not be written to /tmp/ — relative CSS paths will break. Use a subdirectory within the deck directory."
- **Pattern match**: Command contains `/tmp/` AND (contains `.html` OR contains `>` redirect to a path containing `/tmp/`)

#### `gate-enforcement`
- **Trigger**: Agent tool, when dispatching a build agent
- **Action**: Check that `deck-state.json` shows architecture phase complete. If not, warn: "Build agents should not be dispatched before the architecture phase is complete. The slide plan has not been approved."
- **Scope**: Only fires during deck-pipeline workflow (check for deck-state.json existence)

#### `constraint-injection-check`
- **Trigger**: Agent tool, any agent dispatch during deck-pipeline workflow
- **Action**: Verify that the agent prompt contains the string "## Constraints (MANDATORY)". If missing, block with: "Agent prompt is missing the mandatory constraints section. Read constraints.json and inject all applicable constraints."
- **Scope**: Only fires when deck-state.json exists in the working project

### PostToolUse Hooks

#### `css-violation-detector`
- **Trigger**: Write tool or Edit tool, when target is an `.html` file within a deck directory
- **Action**: Read the written/edited content. Check for:
  - `align-items: stretch` (or `align-items:stretch`) — flag as constraint violation
  - `height: 100%` on any element inside `.slide` — flag as constraint violation
  - `flex: 1` on card elements (not on main container) — flag as warning
  - `fetch(` in a `<script>` tag referencing notes or JSON — flag as constraint violation
- **Response**: If any violation found, warn: "CSS constraint violation detected in [file]. [specific violation]. This pattern caused [X] rework instances in prior sessions. Fix before proceeding."

#### `notes-content-detector`
- **Trigger**: Write tool or Edit tool, when target is an `.html` slide file
- **Action**: Check if the slide body (outside of `<div class="notes">` or speaker-notes section) contains phrases that belong in notes:
  - "Directly answers the RFP"
  - "This table was built from"
  - "Source:" followed by a document reference
  - RFP section citations
- **Response**: If detected, warn: "Content that appears to be speaker notes or source citations was written to the slide body. Move to notes-data.js."

#### `micro-iteration-detector`
- **Trigger**: Edit tool, any file
- **Action**: Track edits to the same file. If 3+ edits to the same file occur within a 5-minute window (tracked via timestamps in a temp state file), suggest: "Multiple edits to the same file detected. Consider opening the slide in browser for live review, or batch remaining changes into a single edit."
- **Scope**: Only fires during deck-pipeline workflow

### Stop Hooks

#### `export-visual-verification`
- **Trigger**: Stop (conversation ending or user saying "done")
- **Action**: Check if the current phase is "export" AND any export tool calls were made in this session AND no screenshot Read calls followed the export. If so, warn: "Export artifacts were produced but visual verification was not performed. Run visual verification before declaring export complete."

#### `constraint-persistence`
- **Trigger**: Stop
- **Action**: Check if any user corrections were made in this session (heuristic: user messages containing "wrong", "broken", "fix", "doesn't work", "not working", "try again"). If corrections were made and no new constraint was written to constraints.json, suggest: "User corrections were detected in this session. Consider adding a constraint to constraints.json to prevent recurrence in future sessions."

---

## 7. Default Constraints (Ship With the Skill)

The skill ships with a pre-populated `constraints.json` containing the lessons learned from the [CLIENT] project. These are the constraints that caused the most rework and should never be re-learned:

```json
{
  "constraints": [
    {
      "id": "css-vertical-centering",
      "phase_added": "default",
      "severity": "blocking",
      "rule": "Slide main content container: display:flex; flex-direction:column; justify-content:center; align-items:center. Cards inside: never align-items:stretch, never height:100% or min-height:100% on card body. Use flex:1 ONLY on the main slide content div, never on cards.",
      "reason": "7 recurrences, 22 CSS edits, 1 dedicated 783KB cleanup agent in [CLIENT] v3",
      "applies_to": ["build", "validate", "export"]
    },
    {
      "id": "notes-inline-only",
      "phase_added": "default",
      "severity": "blocking",
      "rule": "Speaker notes must be stored in notes-data.js as window.SLIDE_NOTES[slideNumber]. Never use fetch() to load notes — fails on file:// protocol. Notes content (delivery instructions, RFP citations, talking points) must never appear in the slide HTML body.",
      "reason": "Broke identically in both v1 and v3 sessions",
      "applies_to": ["build", "export"]
    },
    {
      "id": "visual-verification-required",
      "phase_added": "default",
      "severity": "blocking",
      "rule": "No build batch, validation pass, or export operation is declared complete without visual verification. Take screenshots of representative slides (1, N/4, N/2, 3N/4, N) and read them with vision. CLI output alone is never sufficient.",
      "reason": "PPTX declared success with 'zero fallbacks' — deck was unreadable",
      "applies_to": ["build", "validate", "export"]
    },
    {
      "id": "source-before-brainstorm",
      "phase_added": "default",
      "severity": "blocking",
      "rule": "All source documents must be read and the facts manifest must be complete before any brainstorming begins. If a user references a document not in the facts manifest during brainstorm or build, pause and incorporate it.",
      "reason": "Multiple mid-session source discoveries caused content rework in both v1 and v3",
      "applies_to": ["brainstorm", "architecture", "build"]
    },
    {
      "id": "no-tmp-for-html",
      "phase_added": "default",
      "severity": "blocking",
      "rule": "Never write HTML files to /tmp/ for processing. Use a subdirectory within the deck directory. All relative CSS/JS paths must be audited after any file copy or move operation.",
      "reason": "PDF export lost all styling because temp files in /tmp/ broke relative CSS references",
      "applies_to": ["export"]
    },
    {
      "id": "mechanism-before-outcome",
      "phase_added": "default",
      "severity": "recommended",
      "rule": "Every slide that makes a capability claim must show the mechanism (how it works) before stating the outcome (what it delivers). A concept that is named but not explained is a label, not a capability. Target: 30-37% of slides should be mechanism slides.",
      "reason": "v3 had 5/6 core concepts rated ASPIRATIONAL — named correctly, explained insufficiently",
      "applies_to": ["brainstorm", "architecture", "build", "validate"]
    },
    {
      "id": "client-specificity",
      "phase_added": "default",
      "severity": "recommended",
      "rule": "Every slide must pass the client specificity test: does it contain a named system, a dollar figure, or a named metric specific to this client? Slides that could be reused for another client without changes are incomplete.",
      "reason": "Validation found Acts 1-2 were 'indistinguishable from a capable-but-generic AI delivery proposal'",
      "applies_to": ["build", "validate"]
    },
    {
      "id": "slide-count-discipline",
      "phase_added": "default",
      "severity": "recommended",
      "rule": "Set a hard slide cap during architecture phase (recommended: 26-32 main slides). Every slide addition must justify a corresponding removal. If the deck exceeds the cap, run a balance audit before proceeding.",
      "reason": "v3 expanded from 20 to 41+51=92 slides. Flow cohesion rated 6.5/10. 'Acts 2 and 3 are overweight.'",
      "applies_to": ["architecture", "build"]
    },
    {
      "id": "navigation-in-every-slide",
      "phase_added": "default",
      "severity": "blocking",
      "rule": "Every slide HTML file must include navigation elements (prev/next links or navigation pill). Navigation is a baseline requirement, not a post-build addition.",
      "reason": "v1 initial build had no navigation. Treated as afterthought, then required retrofitting all slides.",
      "applies_to": ["build"]
    },
    {
      "id": "content-balance-ratio",
      "phase_added": "default",
      "severity": "recommended",
      "rule": "Target content ratio: 30% client proof / 40% solution mechanism / 30% both. If proof exceeds 40%, identify redundancy clusters and replace with mechanism slides. Run balance audit at 80% completion.",
      "reason": "v3 was 55% proof, 30% solution. Seven solution concepts had zero slides.",
      "applies_to": ["validate"]
    }
  ]
}
```

---

## 8. Installation and Usage

### For a Plugin Developer

The skill suite installs as a set of markdown files in `.claude/skills/`. No build step, no dependencies beyond Claude Code itself.

```bash
# Install into a project
cp -r deck-pipeline/ .claude/skills/deck-pipeline/
cp -r deck-source-inventory/ .claude/skills/deck-source-inventory/
cp -r deck-personas/ .claude/skills/deck-personas/
cp -r deck-brainstorm/ .claude/skills/deck-brainstorm/
cp -r deck-architecture/ .claude/skills/deck-architecture/
cp -r deck-build/ .claude/skills/deck-build/
cp -r deck-validate/ .claude/skills/deck-validate/
cp -r deck-export/ .claude/skills/deck-export/

# Initialize state directory with default constraints
mkdir -p .claude/skills/deck-pipeline/state
cp deck-pipeline/state/constraints-default.json .claude/skills/deck-pipeline/state/constraints.json
```

### For a User Building a Deck

```
User: /deck-pipeline

Claude: Starting deck pipeline. No existing state found — beginning new project.

Phase 1: Source Inventory
I need to read all reference documents before we begin. Please provide:
1. The project/deck directory path (where slides will be built)
2. Any source documents — RFPs, prior decks, exec summaries, reference implementations
3. Any specific constraints (brand guidelines, slide count limits, sensitivity topics)

User: Build in ~/Projects/client-deck/
Source docs are in ~/Projects/client-materials/
This is for Acme Corp, unionized workforce, 30 slide max.

Claude: [Dispatches source-scanner agents, builds facts manifest]
Found 8 source documents. Key facts extracted:
- Client: Acme Corp (unionized — [union-agreement] language audit will apply)
- Contract value: $150M
- Named systems: [list]
- [etc.]

Are there additional source documents I should read?

User: That's everything.

Claude: Source inventory complete. Advancing to Phase 2: Personas.
[Loads deck-personas skill, dispatches persona-architect]
...
```

Each phase loads its skill, does its work, checks its gate, and advances. The user can interrupt, leave, come back tomorrow, and `/deck-pipeline` picks up where it left off because deck-state.json persists.

### For Someone Modifying the Skills

Each skill is a self-contained markdown file with refs/. To modify the brainstorm process:
1. Edit `.claude/skills/deck-brainstorm/SKILL.md` for the main flow
2. Edit `.claude/skills/deck-brainstorm/refs/brainstorm-teams.md` for team structure details
3. Edit `.claude/skills/deck-brainstorm/refs/content-principles.md` for content rules

To add a new constraint:
1. Edit `.claude/skills/deck-pipeline/state/constraints.json`
2. Add a new entry with id, rule, reason, and applies_to phases

To add a new agent type:
1. Define it in `.claude/skills/deck-pipeline/refs/agent-catalog.md`
2. Reference it from the appropriate phase skill

---

## 9. Architecture Decisions

### ADR-001: Hub-and-Spoke Over Monolith

**Context**: The [CLIENT] session showed that a single long-running session accumulates context until constraints drift. A monolithic skill would load all phase instructions at once, wasting context on irrelevant phases.

**Decision**: One orchestrator skill with seven phase skills loaded on demand.

**Consequences**: Phase transitions require state file reads (minor overhead). Each phase gets a fresh context budget. Constraints must be file-persisted rather than conversation-persisted. The orchestrator stays lean (~180 lines) regardless of which phase is active.

### ADR-002: Hooks Over Instructions for Critical Constraints

**Context**: The [CLIENT] session proved that instruction-based constraints ("do not use align-items: stretch") are forgotten by agents. The centering constraint was stated and broken 7 times.

**Decision**: The six highest-impact constraints are enforced via PostToolUse and PreToolUse hooks, not just instructions. Instructions remain as documentation; hooks provide enforcement.

**Consequences**: Hooks add processing overhead to every tool call. False positives are possible (a legitimate use of `align-items: stretch` would be flagged). But the cost of a false positive (a warning message) is far lower than the cost of a missed violation (22 CSS edits).

### ADR-003: Facts Manifest as Context Proxy

**Context**: Build agents need client-specific data (names, figures, systems) but should not read entire source documents. The [CLIENT] session had agents hallucinating figures because they were working from incomplete context.

**Decision**: Phase 1 produces a structured JSON manifest. Subsequent agents receive the manifest, not raw documents.

**Consequences**: The manifest must be accurate — a wrong figure in the manifest propagates to all agents. The source inventory phase is therefore critical path and must be thorough. But the payoff is that every agent has access to exact figures without consuming context on full document reads.

### ADR-004: Subagents for Production, Inline for Coordination

**Context**: The orchestrator's context must stay lean. But small edits (fix one slide after user feedback) should not require a full agent dispatch.

**Decision**: Production work (building slides, running brainstorms, running validations) uses subagents. Coordination work (gate checks, state updates, user interaction) and small edits (1-2 slides) happen inline.

**Consequences**: The threshold is fuzzy — "how many slides is a small edit?" Guideline: 1-2 slides inline, 3+ slides dispatch an agent. The orchestrator must track which approach was used to maintain state consistency.

### ADR-005: Default Constraints Ship With the Skill

**Context**: Every new project should not have to re-learn the centering bug, the notes-on-file:// bug, or the /tmp/ path bug. These are universal to HTML slide building.

**Decision**: The skill ships with 10 default constraints derived from the [CLIENT] session analysis. Users can remove or modify defaults for their project.

**Consequences**: New projects get protection from day one. The defaults may not apply to every project (e.g., a project using a build system with absolute paths would not need the no-tmp-for-html constraint). But having unnecessary constraints is cheaper than missing necessary ones.

---

## 10. Open Questions

1. **Hook implementation**: Claude Code hooks are currently script-based (Python/Bash). The CSS violation detector needs to parse HTML content. Should this be a Python script that receives the file content, or should it use a simpler grep-based approach?

2. **Constraint conflict resolution**: What happens when a user explicitly asks to violate a default constraint? ("I want cards to stretch vertically on this slide.") The hook should warn but not block indefinitely. Proposal: warn once, and if the user confirms, add a per-slide override to constraints.json.

3. **Facts manifest freshness**: If source documents change mid-project, when should the manifest be regenerated? Proposal: the orchestrator checks source file modification times against manifest generation time at phase transitions.

4. **Agent prompt size limits**: The constraint injection approach adds ~50-100 lines to every agent prompt. For phases with many constraints (build phase has 6+ applicable constraints), does this meaningfully reduce the agent's working context? Need to measure.

5. **Visual verification tooling**: The visual-reviewer agent needs screenshot capability. In the [CLIENT] project, this was Chrome headless + the Read tool's vision mode. Should the skill include a screenshot script, or assume the user's environment has one?

6. **PPTX strategy**: The [CLIENT] analysis concluded PPTX should be a "handout format" — simplified layouts, not pixel-perfect conversion. Should the skill even include PPTX export, or should it be a separate optional skill that the user can install?

7. **Skill discovery**: When a user types `/deck-pipeline`, how does Claude Code discover all seven phase skills? Do they need to be registered in a manifest, or does the orchestrator's SKILL.md reference them by path?

---

## 11. Migration Path

### From the Current [CLIENT] Workflow

The [CLIENT] project used ad-hoc agent dispatch with manual constraint management. To migrate:

1. Extract the existing brainstorm outputs (19 brainstorm documents) into the facts manifest format
2. Populate constraints.json from the session-log-analysis recommendations
3. Set deck-state.json to reflect the current phase (the deck is built; state would be post-build)
4. Use deck-validate and deck-export skills for any future validation or export work

### From the Presentations Project

The presentations project already has a viewer engine, deck structure, and skill system. To integrate:

1. The deck-build skill's HTML template would reference the presentations project's slide format (bare HTML fragments, not standalone files)
2. The facts manifest would pull from the RAW/ directory via the existing add-raw-content skill
3. Visual verification would use the existing screenshot-slides.js tooling
4. The deck-export skill would use the existing generate-manifests workflow for deck registration

### For a Net-New Project

1. Install the skill suite into `.claude/skills/`
2. Run `/deck-pipeline` to start
3. The orchestrator walks through all phases from source inventory to export
4. State persists in `.claude/skills/deck-pipeline/state/`
5. Constraints accumulate as the project progresses

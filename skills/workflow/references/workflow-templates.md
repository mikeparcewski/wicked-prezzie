# Workflow Templates — Registry and Schema

Workflow templates define the phase sequence, gate artifacts, and feature flags
for different types of deck-building projects. The `start` skill selects a
template; `workflow` executes it.

---

## Template Schema

Every workflow template conforms to this schema:

```yaml
name: string                    # Unique template identifier (kebab-case)
description: string             # One-sentence purpose
phases:                         # Ordered list of phases
  - name: string                # Phase name (must match a phase definition)
    skill: string               # Skill that owns execution
    gate_artifact: string       # File that must exist to pass the gate
    gate_condition: string      # Human-readable gate rule
    requires_approval: boolean  # Does the gate require explicit user approval?
required_artifacts:             # Artifacts that must exist at workflow completion
  - string                      # File path relative to {deck_dir}/state/
feature_flags:                  # Template-specific behavior toggles
  key: value
```

### Schema Rules

- **phases** is an ordered list. Phases execute in the order listed.
- **gate_artifact** is the primary artifact checked at the gate. Additional
  conditions may be defined in `gate_condition`.
- **requires_approval** defaults to `false`. When `true`, the orchestrator must
  get explicit user confirmation before advancing past this phase.
- **feature_flags** are key-value pairs that modify behavior in phase skills.
  Phase skills check for flags and adjust their behavior accordingly.

---

## Template: `general`

The standard 8-phase deck-building workflow. Suitable for keynotes, internal
presentations, sales pitches, thought leadership, training decks, and any
presentation that does not involve a formal procurement process.

```yaml
name: general
description: Standard deck-building workflow for general presentations
phases:
  - name: source-inventory
    skill: workflow
    gate_artifact: facts-manifest.json
    gate_condition: >-
      facts-manifest.json exists with at least 1 source document entry
      AND user has confirmed source list is complete
    requires_approval: false

  - name: personas
    skill: workflow
    gate_artifact: persona-map.md
    gate_condition: >-
      persona-map.md exists AND covers all named stakeholders from
      the facts manifest
    requires_approval: false

  - name: brainstorm
    skill: brainstorm
    gate_artifact: synthesized-architecture.md
    gate_condition: >-
      synthesized-architecture.md exists AND user has reviewed
      and approved it
    requires_approval: true

  - name: architecture
    skill: workflow
    gate_artifact: slide-plan.md
    gate_condition: >-
      All three review documents exist (narrative, commercial, technical)
      AND each contains CONDITIONAL APPROVE status
    requires_approval: false

  - name: build
    skill: workflow
    gate_artifact: slides/
    gate_condition: >-
      All slides in slide-plan.md are built AND visual verification
      of representative slides passed AND zero blocking issues
    requires_approval: false

  - name: validate
    skill: workflow
    gate_artifact: council-punch-list.md
    gate_condition: >-
      council-punch-list.md exists AND contains zero blocking items
    requires_approval: false

  - name: polish
    skill: workflow
    gate_artifact: flow-review.md
    gate_condition: >-
      flow-review.md exists AND all non-blocking punch list items
      addressed or explicitly deferred with user approval
    requires_approval: false

  - name: export
    skill: workflow
    gate_artifact: null
    gate_condition: >-
      Export artifacts exist AND visual verification passed
    requires_approval: false

required_artifacts:
  - facts-manifest.json
  - persona-map.md
  - synthesized-architecture.md
  - slide-plan.md
  - council-punch-list.md
  - flow-review.md

feature_flags:
  exec_summary_required: false
  persona_depth: standard
```

---

## Template: `rfp-exec`

Extended workflow for formal proposal and RFP responses. Inserts an executive
summary phase between brainstorm and architecture. The exec summary serves as
the strategic contract — slides are generated from the approved summary, not
directly from brainstorm outputs.

This template is recommended when the `start` skill detects RFP/proposal signals
in the user's brief or source documents.

```yaml
name: rfp-exec
description: Proposal workflow with executive summary approval gate
phases:
  - name: source-inventory
    skill: workflow
    gate_artifact: facts-manifest.json
    gate_condition: >-
      facts-manifest.json exists with at least 1 source document entry
      AND user has confirmed source list is complete
    requires_approval: false

  - name: personas
    skill: workflow
    gate_artifact: persona-map.md
    gate_condition: >-
      persona-map.md exists AND covers all named stakeholders from
      the facts manifest AND includes evaluation committee coverage
    requires_approval: false

  - name: brainstorm
    skill: brainstorm
    gate_artifact: synthesized-architecture.md
    gate_condition: >-
      synthesized-architecture.md exists AND user has reviewed
      and approved it
    requires_approval: true

  - name: exec-summary
    skill: exec-summary
    gate_artifact: exec-summary.md
    gate_condition: >-
      exec-summary.md exists AND all 8 sections contain substantive
      content AND user has explicitly approved
    requires_approval: true

  - name: architecture
    skill: workflow
    gate_artifact: slide-plan.md
    gate_condition: >-
      All three review documents exist (narrative, commercial, technical)
      AND each contains CONDITIONAL APPROVE status AND slide plan
      maps to approved exec-summary.md sections
    requires_approval: false

  - name: build
    skill: workflow
    gate_artifact: slides/
    gate_condition: >-
      All slides in slide-plan.md are built AND visual verification
      of representative slides passed AND zero blocking issues
    requires_approval: false

  - name: validate
    skill: workflow
    gate_artifact: council-punch-list.md
    gate_condition: >-
      council-punch-list.md exists AND contains zero blocking items
    requires_approval: false

  - name: polish
    skill: workflow
    gate_artifact: flow-review.md
    gate_condition: >-
      flow-review.md exists AND all non-blocking punch list items
      addressed or explicitly deferred with user approval
    requires_approval: false

  - name: export
    skill: workflow
    gate_artifact: null
    gate_condition: >-
      Export artifacts exist AND visual verification passed
    requires_approval: false

required_artifacts:
  - facts-manifest.json
  - persona-map.md
  - synthesized-architecture.md
  - exec-summary.md
  - slide-plan.md
  - council-punch-list.md
  - flow-review.md

feature_flags:
  exec_summary_required: true
  persona_depth: evaluation-committee
```

---

## Key Differences: `general` vs `rfp-exec`

| Aspect | `general` | `rfp-exec` |
|--------|-----------|------------|
| Phase count | 8 | 9 (adds exec-summary) |
| Exec summary | Not produced | Required, user-approved gate |
| Persona depth | Standard (audience-appropriate) | Evaluation committee coverage required |
| Architecture input | synthesized-architecture.md | exec-summary.md + synthesized-architecture.md |
| Approval gates | 1 (brainstorm) | 2 (brainstorm + exec-summary) |
| Slide plan mapping | Maps to brainstorm themes | Maps to exec summary sections |

---

## Adding New Templates

To add a new workflow template:

1. Define the template in this file following the schema above
2. Add detection signals to `auto-detection.md`
3. Update the `start` skill to recognize the new template
4. If the template introduces a new phase, create a corresponding skill under
   `skills/`

Templates should only be added when a workflow is structurally different — not
just thematically different. A "sales pitch" and a "keynote" both use the
`general` template. An RFP response uses `rfp-exec` because it has a
structurally different approval flow.

---

## Template Storage

The selected template name is stored in `deck-state.json`:

```json
{
  "template": "rfp-exec",
  "current_phase": "exec-summary",
  "phases_completed": ["source-inventory", "personas", "brainstorm"],
  ...
}
```

The orchestrator reads the template name from deck-state.json and looks up the
phase sequence from this file. Phase transitions follow the template's phase
order, not a hardcoded sequence.

---
name: exec-summary
description: >-
  Synthesize brainstorm outputs into a structured 8-section executive summary
  for proposal decks. Produces exec-summary.md and requires explicit user
  approval before slide building begins. Used in the rfp-exec workflow template.
triggers:
  - "executive summary"
  - "exec summary"
  - "write the exec summary"
  - "summarize the brainstorm"
  - "proposal summary"
  - "rfp summary"
phase: exec-summary
pipeline_position: 3.5
---

# exec-summary — Executive Summary Phase

Runs after the brainstorm phase in the `rfp-exec` workflow template. Synthesizes
brainstorm team outputs into a structured 8-section executive summary document
that serves as the contract between strategic thinking and slide production.

No slides are built until the executive summary is approved.

---

## When to Use

- After Phase 3 (Brainstorm) completes in the rfp-exec template
- When `synthesized-architecture.md` exists and has been approved
- Before Phase 4 (Architecture) begins

This phase is only active in the `rfp-exec` workflow template. The `general`
template skips it entirely — brainstorm flows directly to architecture.

---

## Reference Files

| File | Purpose | Load When |
|------|---------|-----------|
| `references/sections.md` | 8-section schema with required content, quality criteria, prohibited patterns | Always — defines the output structure |
| `references/word-export.md` | Word export formatting conventions and customization guide | When exporting to .docx |

---

## Inputs Required

- `{deck_dir}/state/synthesized-architecture.md` — approved brainstorm synthesis
- `{deck_dir}/state/facts-manifest.json` — source document digest
- `{deck_dir}/state/persona-map.md` — evaluation committee personas
- `{deck_dir}/state/constraints.json` — active constraints

All brainstorm team outputs should also be available for reference:
- `{deck_dir}/state/brainstorm-narrative.md`
- `{deck_dir}/state/brainstorm-proof.md`
- `{deck_dir}/state/brainstorm-commercial.md`

---

## Output Artifact

**File**: `{deck_dir}/state/exec-summary.md`

The executive summary follows the 8-section schema defined in
`references/sections.md`. Each section must contain substantive content — no
placeholders, no "TBD", no empty sections.

---

## Synthesis Procedure

### 1. Map Brainstorm Outputs to Sections

Read all three brainstorm team outputs and the synthesized architecture. For each
of the 8 sections, identify which brainstorm content maps to it:

| Section | Primary Source | Supporting Sources |
|---------|---------------|-------------------|
| Executive Framing | Narrative team (arc, governing principle) | Facts manifest (business drivers) |
| Key Messaging | Narrative team (hallway line, themes) | All teams (recurring themes) |
| What We Commit To | Commercial team (SLAs, pricing) | Proof team (deliverables) |
| What We Know | Facts manifest (client environment) | All teams (client-specific references) |
| How We Deliver | Proof team (methodology, team structure) | Commercial team (governance) |
| How We Scale | Proof team (capacity, growth) | Commercial team (pricing tiers) |
| What the Client Gets | Commercial team (outcomes, ROI) | Proof team (measurable results) |
| Why Us | All teams (differentiators) | Facts manifest (relevant experience) |

### 2. Apply Quality Criteria

For each section, verify against the quality criteria in `references/sections.md`.
Every claim must be grounded in the facts manifest or a specific brainstorm
output. Apply the "mechanism before outcome" test: claims without a named
mechanism are flagged and must be strengthened before approval.

### 3. Cross-Reference Against Personas

For each section, verify that at least one persona's pass criteria is addressed.
The full persona map should be covered across all 8 sections. If a persona has
no section addressing their primary concern, flag this as a gap.

### 4. Constraint Check

Read `constraints.json` and verify the executive summary does not violate any
active constraints. Common constraint violations to check:
- Client specificity (named systems, not generic references)
- Financial accuracy (figures match facts manifest exactly)
- Sensitivity flags (no disclosure of flagged information)

---

## Approval Gate

The executive summary requires **explicit user approval** before the workflow
advances. This is not auto-gated.

### Presentation Protocol

1. Present the complete executive summary to the user
2. Highlight any sections where confidence is lower or content is thinner
3. Note any persona gaps (personas whose primary concerns are not addressed)
4. Ask explicitly: "Does this executive summary accurately capture the proposal
   strategy? Should I adjust any sections before we move to slide architecture?"

### Revision Cycle

If the user requests changes:
1. Apply the requested changes
2. Re-run quality criteria checks on affected sections
3. Re-present the updated summary
4. Ask for approval again

There is no limit on revision cycles. The user controls when the summary is
approved.

### After Approval

1. Write the final version to `{deck_dir}/state/exec-summary.md`
2. Update `deck-state.json` to record:
   - `exec_summary_approved: true`
   - `exec_summary_approved_at: {timestamp}`
   - `current_phase: "architecture"` (advance to next phase)
3. The architecture phase now uses `exec-summary.md` as its primary input
   alongside the synthesized architecture

---

## Gate Condition

**Gate passes when**: `exec-summary.md` exists AND all 8 sections contain
substantive content AND user has explicitly approved.

**Gate fails when**: Any section is empty, contains placeholder text ("TBD",
"TODO", "to be determined"), or user has not approved.

---

## Relationship to Architecture Phase

In the `rfp-exec` template, the approved executive summary becomes the primary
input for slide architecture. The architecture phase structures slides around
the 8 sections — each section may map to 1-4 slides depending on content depth.

The exec summary is the "what we want to say." The architecture phase determines
"how we say it slide by slide."

---

## Anti-Pattern Guards

**Guard 1 — No premature slides**: Do not generate any slide content during this
phase. The exec summary is a prose document, not a slide outline. Slide structure
comes in the architecture phase.

**Guard 2 — No hollow sections**: Every section must contain at least one
specific, verifiable claim grounded in the facts manifest. "We will deliver
excellent service" is hollow. "We will maintain 99.95% uptime across the 47
branch network, backed by our 24/7 NOC in Melbourne" is substantive.

**Guard 3 — No orphaned personas**: If a persona from the persona map has no
section addressing their primary concern, the summary is incomplete. Flag the
gap before presenting for approval.

**Guard 4 — Constraint inheritance**: Read constraints.json before writing the
summary. All active constraints apply to executive summary content, not just to
slides.

---

## Word Export

After the executive summary is approved and before distributing for team review,
export the summary to a formatted Word document using `exec_summary_export.py`.

### When to Export

- After explicit user approval of the exec summary
- Before circulating for stakeholder review or tracked-changes feedback
- When a printable or emailable format is needed

### Usage

```bash
# Basic export
python skills/exec-summary/scripts/exec_summary_export.py state/exec-summary.md \
    --output deliverables/exec-summary.docx \
    --title "Project Alpha"

# Draft watermark for internal review
python skills/exec-summary/scripts/exec_summary_export.py state/exec-summary.md \
    --output deliverables/exec-summary-draft.docx \
    --title "Project Alpha" \
    --draft
```

### What the Export Produces

- Title page with deck title and "Executive Summary" subtitle
- Table of contents (updates when opened in Word)
- All 8 sections as Heading 1 entries with formatted body content
- Professional typography (Calibri, proper heading hierarchy, paragraph spacing)
- Page numbers in the footer
- Optional "DRAFT — For Review" diagonal watermark

### Programmatic Use

```python
from exec_summary_export import export_exec_summary

path = export_exec_summary(
    md_path="state/exec-summary.md",
    output_path_str="deliverables/exec-summary.docx",
    title="Project Alpha — Executive Summary",
    draft=True,
)
```

The Word export is a one-way snapshot. If the summary is revised after export,
re-run the export. Edits should flow back into `exec-summary.md`, not the .docx.

See `references/word-export.md` for formatting conventions and customization.

# Agent Catalog — deck-pipeline

All agent definitions for the deck-pipeline workflow. Each entry includes role,
dispatch phase, parallelism rules, output contract, and key constraints. The
orchestrator uses these as prompt templates — it reads the relevant entry, injects
project context and constraints, and dispatches via the Agent tool.

Every agent prompt must include `## Constraints (MANDATORY)` populated from
constraints.json. This is enforced by the `constraint-injection-check` PreToolUse
hook.

---

## Agent Prompt Template (required structure for all agents)

```
## Your Role
[Role-specific instructions — from the entry below]

## Project Context
[Compressed facts manifest fields: client.name, client.named_systems,
 client.named_programs, financial_figures, sensitivity_flags.
 NOT the full manifest — summary fields only. If the agent needs a specific
 figure, it should read facts-manifest.json directly.]

## Constraints (MANDATORY)
[All constraints from constraints.json where applies_to includes the current
 phase. Injected by the orchestrator. Do not omit or abbreviate.]

## Your Task
[Specific task for this agent instance — which slides, which sections, etc.]

## Output Format
[Exact file paths to write, schema or format to follow, what "done" means]
```

---

## source-scanner

**Role**: Read all source documents and produce sections of the facts manifest.
Extract exact figures, named systems, named programs, financial data, and
sensitivity flags. Flag any figure that appears inconsistently across sources.

**Dispatch phase**: Phase 1 (Source Inventory)

**Parallelism**: 1-3 agents. Split by document type: one agent for text documents
(RFPs, exec summaries), one for spreadsheets (financial data, timelines), one for
prior decks (reference implementations, prior presentations). If all documents are
the same type, use 1 agent.

**Output**: Writes sections to `state/facts-manifest.json`. Each agent writes to
a non-overlapping section (text-docs agent writes `source_documents` and
`rfp_requirements`; spreadsheet agent writes `financial_figures`; deck agent
writes `reference_implementations`). Orchestrator merges after all agents complete.

**Key constraints**:
- Must extract exact figures, not approximations. "[total-value]" not "approximately $800M"
- Must flag any figure that appears differently across two sources with
  `"conflict": true` and both values
- Must include the source document path for every extracted fact
- Named systems, named programs, and leadership names are required extractions —
  do not skip if not prominently featured

**"Done" means**: Every source document has a `source_documents` entry, key facts
are extracted, conflicts are flagged, sensitivity flags are populated.

---

## persona-architect

**Role**: Build the full persona map for the evaluation committee. Define each
persona's role, primary concern, hardest question, must-hit slides (by topic),
pass criteria, and fail criteria. Include dreamer-skeptic pairing recommendations
for Phase 3.

**Dispatch phase**: Phase 2 (Personas)

**Parallelism**: 1 agent. Personas must be internally consistent — parallel agents
would produce duplicate or conflicting personas.

**Output**: `persona-map.md` in the deck directory.

**Key constraints**:
- Must cover the full evaluation committee — every named stakeholder from the
  facts manifest has a persona entry
- Must include dreamer-skeptic pairing recommendations: which persona pairs create
  productive dreamer-skeptic dynamics
- Personas must be grounded in the facts manifest — named individuals, not generic
  "CTO" archetypes
- Each persona must list at least 3 "must-hit" slide topics and 2 "deal-breaker"
  failure modes

**"Done" means**: persona-map.md exists with an entry for every named stakeholder
from facts-manifest.json.

---

## brainstorm-dreamer

**Role**: The visionary half of a dreamer-skeptic pair. Generate the aspirational
narrative for your team's angle (narrative, proof, or commercial). Push the
ambition ceiling. Propose the most compelling version of the story.

**Dispatch phase**: Phase 3 (Brainstorm) — Wave 1

**Parallelism**: 3 dreamers, one per team angle. Always paired with a
brainstorm-skeptic. Dispatch dreamer + skeptic as a pair (dreamer first, skeptic
reviews the dreamer's output).

**Output**: Team brainstorm document (e.g. `brainstorm-narrative.md`). The skeptic
will annotate this document in their pass.

**Key constraints**:
- Must ground every aspiration in a named client system or specific figure from
  the facts manifest. Aspiration without grounding is aspirational, not narrative.
- "Proof not pitch" — every claim must have a specific, citable basis
- Must identify 3-5 key slides for their team angle
- Must not overlap with the other teams' primary angles (check facts manifest for
  team angle definitions)

**"Done" means**: Team brainstorm document written with 3-5 slide proposals,
each grounded in a named system or figure.

---

## brainstorm-skeptic

**Role**: The load-bearing challenger. Read the dreamer's output for your team
angle. Challenge every claim that lacks a named mechanism. Force specificity.
Annotate the brainstorm document with skeptic challenges and mark each claim as:
GROUNDED (mechanism named, figure cited) / PARTIAL (mechanism implied, not named)
/ ASPIRATIONAL (outcome stated, mechanism absent).

**Dispatch phase**: Phase 3 (Brainstorm) — Wave 1, second half of each pair

**Parallelism**: 1:1 with a dreamer. 3 skeptics total. Dispatched after the
paired dreamer's output is written.

**Output**: Annotated version of the dreamer's team brainstorm document, with
skeptic challenges resolved (either upgrading to GROUNDED with specific
mechanisms, or flagging as items needing architecture phase resolution).

**Key constraints**:
- Apply the "mechanism before outcome" test to every claim. A claim without a
  named mechanism is flagged ASPIRATIONAL regardless of how compelling it sounds.
- Every ASPIRATIONAL flag must include a specific question: "What is the mechanism
  that delivers [outcome]?"
- Do not remove dreamer content — annotate it. Synthesizer reconciles.

**"Done" means**: All dreamer claims annotated with GROUNDED/PARTIAL/ASPIRATIONAL,
skeptic questions documented for each PARTIAL and ASPIRATIONAL item.

---

## brainstorm-synthesizer

**Role**: Read all 3 team brainstorm documents (with skeptic annotations) and
produce a single unified architecture. Resolve conflicts between team outputs.
Map content to persona coverage. Propose the slide plan structure.

**Dispatch phase**: Phase 3 (Brainstorm) — Wave 2, after all 3 teams complete

**Parallelism**: 1 agent. Synthesis requires seeing all inputs simultaneously.

**Output**: `synthesized-architecture.md` containing:
- Conflict resolution table (every disagreement between teams, with resolution rationale)
- Threading map (how narrative, proof, and commercial angles weave together)
- Proposed act structure with slide topics
- Persona coverage map (which persona's must-hit topics are covered by which slides)
- Unresolved items flagged for Architecture phase review

**Key constraints**:
- Must explicitly list every conflict between team outputs in a table — do not
  silently resolve conflicts
- Must document the rationale for each resolution decision
- Must not drop ASPIRATIONAL-flagged items silently — either escalate to
  Architecture phase or propose a mechanism slide to address them

**"Done" means**: synthesized-architecture.md written, conflict resolution table
populated, persona coverage map included.

---

## review-narrative

**Role**: Apply the narrative lens to the synthesized architecture and slide plan.
Evaluate: flow, emotional arc, audience engagement, protagonist continuity. Produce
a review document with conditional approval or rejection.

**Dispatch phase**: Phase 4 (Architecture)

**Parallelism**: 3 review agents run in parallel (narrative, commercial, technical)

**Output**: `review-narrative.md` with: overall status (CONDITIONAL APPROVE or
REJECT), blocking conditions (must be resolved before advancing), non-blocking
recommendations, reorder suggestions.

**Key constraints**:
- Narrative lens scope: flow between acts, emotional arc (tension → proof →
  resolution), one-sentence per-act clarity test, protagonist continuity
- A REJECT requires specific blocking conditions that, when addressed, would
  produce CONDITIONAL APPROVE
- Reorder recommendations must specify the exact slide move (slide X moves to
  position Y, reason)

**"Done" means**: review-narrative.md written with clear CONDITIONAL APPROVE or
REJECT status and actionable conditions.

---

## review-commercial

**Role**: Apply the commercial lens to the synthesized architecture and slide plan.
Evaluate: financial accuracy, legal exposure, [union-agreement]-safe language, specificity of
financial claims.

**Dispatch phase**: Phase 4 (Architecture)

**Parallelism**: 3 parallel (with narrative and technical)

**Output**: `review-commercial.md` with status, blocking conditions, recommendations.

**Key constraints**:
- Commercial lens scope: all financial figures must match facts manifest exactly,
  [union-agreement] trigger words must be absent (check sensitivity_flags in facts manifest),
  legal exposure from overcommitment or unqualified claims
- Flag any figure that is not in the facts manifest as UNVERIFIED
- Flag any [union-agreement] trigger word with the safe alternative from sensitivity_flags

**"Done" means**: review-commercial.md written with clear status and all financial
claims verified against facts manifest.

---

## review-technical

**Role**: Apply the technical lens to the synthesized architecture and slide plan.
Evaluate: data integrity, production feasibility, version audits, correctness of
technical claims.

**Dispatch phase**: Phase 4 (Architecture)

**Parallelism**: 3 parallel (with narrative and commercial)

**Output**: `review-technical.md` with status, blocking conditions, recommendations.

**Key constraints**:
- Technical lens scope: are named systems accurately described, are version claims
  auditable, are production feasibility claims realistic
- Flag any technical claim that cannot be verified against the facts manifest
- Rate each core technical concept as FEASIBLE / NEEDS QUALIFICATION / INFEASIBLE

**"Done" means**: review-technical.md written with all core technical concepts rated.

---

## slide-builder

**Role**: Build slide HTML files per the approved slide plan. One agent per act
(3-5 slides). Include navigation, notes entries in notes-data.js, and full CSS
compliance.

**Dispatch phase**: Phase 5 (Build)

**Parallelism**: 3-4 agents, one per act. Up to 4 in parallel.

**Output**: Individual slide HTML files + notes-data.js entries for the assigned
act's slides. Write slides to the deck directory.

**Key constraints** (ALL of the following, plus all constraints from constraints.json):
- `css-vertical-centering` — main container flex column centered, no stretch on cards
- `notes-inline-only` — notes in notes-data.js window.SLIDE_NOTES, never in body
- `navigation-in-every-slide` — navigation pill in every slide, first pass
- `client-specificity` — every slide has a named system, dollar figure, or named metric
- `visual-verification-required` — visual reviewer must verify before act is declared done
- All named systems must use exact names from facts manifest, not generic alternatives

**"Done" means**: All assigned slides written, notes-data.js entries added for
each slide, navigation present in each slide.

---

## validation-lens

**Role**: Run one of the four validation lenses on the complete deck. Produce a
rated gap list with slide-level findings.

**Dispatch phase**: Phase 6 (Validate) — Wave 1

**Parallelism**: 4 agents, one per lens. All 4 run in parallel.

**Lenses** (assign one per agent):

**Lens 1 — POV Clarity**: Are mechanisms visible, not just named? For each slide
claiming a capability, is the mechanism shown? Rate each mechanism-bearing slide
as VISIBLE / NAMED-ONLY / MISSING.

**Lens 2 — RFP Coverage**: Does every RFP requirement have a slide? Cross-reference
facts-manifest.json `rfp_requirements` array against slide plan. Flag requirements
with no corresponding slide as UNCOVERED.

**Lens 3 — Making It Real**: Rate each content concept as CONCRETE (specific,
measurable, verifiable) / PARTIAL (some specificity) / ASPIRATIONAL (named, not
explained) / MISSING (required concept absent from deck).

**Lens 4 — Know Them**: Named systems usage, operational history awareness,
leadership awareness. Check: are the client's named systems used throughout, or
replaced with generic terms? Is operational history reflected in proof slides?

**Output**: One validation document per lens (`validation-pov.md`,
`validation-rfp.md`, `validation-reality.md`, `validation-know-them.md`).
Each contains: per-slide ratings, gap list, fix recommendations (slide number,
specific fix instruction, severity: blocking/recommended).

---

## council-reviewer

**Role**: Read all four lens documents and produce the final punch list. This is
the final quality gate before Polish.

**Dispatch phase**: Phase 6 (Validate) — Wave 2, after all lenses complete

**Parallelism**: 1 agent. Council review needs all lens outputs as simultaneous input.

**Output**: `council-punch-list.md` containing:
- Prioritized punch list ordered by blocking status then severity
- Each item: slide number, exact fix instruction, source lens, blocking/non-blocking
- 3 deal-losers (blocking items that would cause the audience to disengage or distrust)
- 3 deal-winners (existing strengths to protect in polish)

**Key constraints**:
- Every item must specify exact slide number, exact fix instruction, source
  document or lens, and blocking status
- Deal-losers and deal-winners must be named specifically, not as general categories

**"Done" means**: council-punch-list.md written with zero ambiguous items (every
item has a clear, actionable fix instruction).

---

## balance-auditor

**Role**: Check content ratio across the full deck. Identify redundancy clusters.
Recommend specific cuts and additions.

**Dispatch phase**: Phase 6 (Validate) — Wave 1 (parallel with validation lenses)

**Parallelism**: 1 agent (runs parallel with the 4 validation lenses, not in sequence)

**Output**: `balance-audit.md` containing:
- Ratio analysis: percentage of slides that are proof-only, solution-mechanism-only,
  both
- Redundancy clusters: groups of slides that cover the same ground
- Cut/add recommendations: specific slides to cut, specific topics to add

**Key constraints**:
- Target ratio: 30% client proof / 40% solution mechanism / 30% both
- If proof exceeds 40%: identify specific redundancy clusters and recommend cuts
- If mechanism is below 30%: identify which solution concepts have no mechanism slide

**"Done" means**: balance-audit.md written with ratio breakdown and specific
cut/add recommendations.

---

## flow-reviewer

**Role**: Check deck flow as a presentation, not just as a document. Rate each
act through persona lenses. Identify missing transitions. Verify each act can be
stated in one sentence.

**Dispatch phase**: Phase 7 (Polish), or Phase 6 if balance-auditor flags flow
problems

**Parallelism**: 1 agent

**Output**: `flow-review.md` containing:
- Per-act rating through 5 persona lenses (from persona-map.md)
- Acts that fail the one-sentence clarity test (flagged as UNFOCUSED)
- Missing transition slides (where the audience has no bridge between topics)
- Reorder recommendations (specific slide moves)

**Key constraints**:
- Rate each act through 5 persona lenses from persona-map.md
- If any act cannot be stated in one sentence, flag as UNFOCUSED with the specific
  focus problem
- Reorder recommendations must be specific: "Slide 14 moves to position 8, between
  slides 7 and 9. Reason: [specific reason]."

**"Done" means**: flow-review.md written with per-act ratings for all personas.

---

## visual-reviewer

**Role**: Screenshot representative slides and verify rendering with vision.
Declare pass or fail per slide. Never declare pass based on file existence or
CLI output.

**Dispatch phase**: Phase 5 (after each build batch), Phase 7 (Polish), Phase 8 (Export)

**Parallelism**: 1 agent (needs sequential screenshot access)

**Output**: Visual review report — pass/fail per slide with specific issues.
Written inline in the build or export log, or as `visual-review-{batch}.md`.

**Key constraints**:
- Must use vision to read screenshots. Cannot declare pass based on file size,
  file existence, or CLI output.
- Representative slide set: slide 1, slide N/4, slide N/2, slide 3N/4, slide N
  (minimum 5 slides for a 20+ slide deck; all slides for a deck under 10 slides)
- For each screenshot: check dark background present, text readable, no content
  overflow, navigation present, styling intact
- If any slide fails: provide specific issue description and fix instruction

**"Done" means**: All representative slides screenshotted and read with vision.
Explicit pass or fail for each, with fix instructions for failures.

---

## export-bundler

**Role**: Produce export artifacts — PDF, bundled HTML, or optionally PPTX.
Run path audit before rendering. Coordinate visual-reviewer after export.

**Dispatch phase**: Phase 8 (Export)

**Parallelism**: 1 agent per format. Multiple formats may run in parallel.

**Output**: Export files in the deck directory:
- `{deck-name}.pdf` — Chrome headless PDF
- `{deck-name}-bundle.html` — single-file bundled HTML with inlined assets
- `{deck-name}.pptx` (optional, via slide-pipeline skill)

**Key constraints**:
- `no-tmp-for-html` — all temp files within deck directory, never /tmp/
- After any file copy or move, audit all href/src paths to verify they resolve
- Use absolute paths for CSS references in generated temp files
- `visual-verification-required` — dispatch visual-reviewer after export; do
  not declare export complete until visual-reviewer passes
- PDF export: run path audit step before Chrome headless call, read the first
  page screenshot to verify styling survived the headless render

**"Done" means**: Export artifact exists, path audit passed, visual-reviewer
has declared pass on the export artifact.

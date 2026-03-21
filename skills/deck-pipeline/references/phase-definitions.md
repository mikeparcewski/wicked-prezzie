# Phase Definitions — deck-pipeline

8-phase state machine for the full deck-building workflow. Each phase has a
defined purpose, gate condition, key artifacts, context budget, and agent set.

---

## Transition Rules

- **Linear by default**: phases execute in order 1 → 8
- **Skip-back allowed**: any phase may trigger a return to an earlier phase when
  a gap is discovered (e.g. build agent finds a missing source → return to Phase 1)
- **Skip-forward requires approval**: jumping past a gate requires explicit user
  confirmation and a logged warning entry in deck-state.json
- **Phase completion is gated**: the orchestrator checks the gate condition before
  advancing. A phase is not complete because the agent says it is complete — it is
  complete when the artifact exists and meets the gate condition.

---

## Context Budget Per Phase

| Phase | Orchestrator | Phase SKILL | Refs Loaded | Constraints | Total Est. |
|-------|-------------|-------------|-------------|-------------|-----------|
| Source Inventory | 180 lines | 150 lines | 1 (document-types) | 0 | ~530 lines |
| Personas | 180 lines | 120 lines | 1 (persona-template) | ~20 lines | ~520 lines |
| Brainstorm | 180 lines | 160 lines | 2 (teams + content) | ~20 lines | ~860 lines |
| Architecture | 180 lines | 180 lines | 2 (review + conflict) | ~30 lines | ~890 lines |
| Build | 180 lines | 180 lines | 3 (template + CSS + notes) | ~50 lines | ~1110 lines |
| Validate | 180 lines | 170 lines | 3 (4-lens + council + balance) | ~50 lines | ~1100 lines |
| Polish | 180 lines | 160 lines | 2 (flow + balance) | ~50 lines | ~890 lines |
| Export | 180 lines | 160 lines | 2 (format + verification) | ~50 lines | ~890 lines |

Build and Validate are the heaviest. Even at peak, total skill context is
approximately 1100 lines — well under the drift threshold.

---

## Phase 1 — Source Inventory

**Purpose**: Read all source documents and produce the facts manifest. Establish
the complete information baseline before any creative work begins.

**Inputs required**: Project directory path, source document paths (or directory
to scan).

**Key artifacts**:
- `facts-manifest.json` — structured digest of all source material

**Gate condition**: `facts-manifest.json` exists AND user has confirmed: "Are
there additional source documents I should read?" has been asked and answered.

**Gate check procedure**:
1. Verify facts-manifest.json exists and is valid JSON
2. Verify `source_documents` array has at least 1 entry
3. Confirm user responded to the completeness question
4. Log gate passage to deck-state.json with timestamp

**Agents dispatched**:
- `source-scanner` — 1-3 agents, one per document type (text, spreadsheets, prior decks)
- Parallelism: up to 3 parallel

**Refs loaded during this phase**:
- `document-types.md` (from deck-source-inventory skill) — how to handle PDFs,
  XLSX, DOCX, HTML decks
- `manifest-format.md` — facts manifest schema

**Phase-specific rules**:
- Every figure extracted must cite its source document
- Figures that appear inconsistently across sources must be flagged in the manifest
  with a `"conflict": true` field and all values listed
- Named systems, named programs, leadership names, financial figures, and
  sensitivity flags are required manifest fields — not optional

---

## Phase 2 — Personas

**Purpose**: Build the full persona map for the evaluation committee. Define
pass/fail criteria, must-hit slides, and the hardest question each persona will
ask. Set up dreamer-skeptic pairings for Phase 3.

**Inputs required**: `facts-manifest.json` (Phase 1 artifact)

**Key artifacts**:
- `persona-map.md` — full evaluation committee coverage

**Gate condition**: `persona-map.md` exists AND covers the full evaluation
committee (all named stakeholders from the facts manifest have a persona entry).

**Agents dispatched**:
- `persona-architect` — 1 agent (personas must be internally consistent)
- Parallelism: 1

**Refs loaded during this phase**:
- `persona-template.md` (from deck-personas skill) — 12-persona framework with
  pass/fail criteria
- `dreamer-skeptic-pairing.md` — pairing recommendations

**Phase-specific rules**:
- Every persona must include: role, primary concern, hardest question, must-hit
  slides (by topic), pass criteria, fail criteria
- Dreamer-skeptic pairing recommendations must be written — used in Phase 3
- Personas must be grounded in the facts manifest (named individuals, not generic
  "decision maker" archetypes)

---

## Phase 3 — Brainstorm

**Purpose**: Generate the raw content architecture through a three-team
dreamer-skeptic process. Produce a synthesized architecture document that
resolves conflicts and maps content to personas.

**Inputs required**: `facts-manifest.json`, `persona-map.md`

**Key artifacts**:
- `brainstorm-narrative.md` — narrative team output
- `brainstorm-proof.md` — proof/evidence team output
- `brainstorm-commercial.md` — commercial/financial team output
- `synthesized-architecture.md` — reconciled output with conflict resolution table

**Gate condition**: `synthesized-architecture.md` exists AND user has reviewed
and approved it. This gate requires explicit user approval — it is not
auto-advanced.

**Agents dispatched** (in two waves):
- Wave 1 (parallel): `brainstorm-dreamer` x3 + `brainstorm-skeptic` x3
  — 3 dreamer-skeptic pairs, one per team angle (narrative/proof/commercial)
  — Up to 3 pairs = 6 agents, but dispatch as 3 sequential pairs, not 6 at once
  — Parallelism: 3 pairs in parallel
- Wave 2 (sequential): `brainstorm-synthesizer` x1
  — Dispatched after all 3 teams complete
  — Parallelism: 1

**Refs loaded during this phase**:
- `brainstorm-teams.md` (from deck-brainstorm skill) — three-team structure +
  synthesis rules
- `content-principles.md` — mechanism-before-outcome, two-layer proof, etc.

**Phase-specific rules**:
- Each dreamer must ground every aspiration in a named client system or specific
  figure from the facts manifest
- Each skeptic must apply the "mechanism before outcome" test — claims without a
  named mechanism are flagged ASPIRATIONAL
- The synthesizer must explicitly list every conflict between team outputs and
  document the resolution rationale

---

## Phase 4 — Architecture

**Purpose**: Apply three-team review (narrative, commercial, technical) to the
synthesized architecture. Resolve conflicts. Produce the approved slide plan.

**Inputs required**: `synthesized-architecture.md`, `facts-manifest.json`,
`persona-map.md`

**Key artifacts**:
- `review-narrative.md` — narrative lens review
- `review-commercial.md` — commercial lens review
- `review-technical.md` — technical lens review
- `slide-plan.md` — approved slide plan with act structure, slide topics,
  persona coverage map, hard slide cap

**Gate condition**: All three review documents exist AND each contains
CONDITIONAL APPROVE status. If any review returns REJECT, the synthesized
architecture must be revised before advancing.

**Agents dispatched**:
- `review-narrative`, `review-commercial`, `review-technical` — 3 agents parallel
- Parallelism: 3

**Refs loaded during this phase**:
- `three-team-review.md` (from deck-architecture skill) — review lens definitions
- `conflict-resolution.md` — how to reconcile brainstorm outputs
- `slide-plan-format.md` — approved plan schema

**Phase-specific rules**:
- Narrative lens: flow, emotional arc, audience engagement, protagonist continuity
- Commercial lens: financial accuracy, legal exposure, [union-agreement]-safe language,
  specificity of financial claims
- Technical lens: data integrity, production feasibility, version audits
- Slide plan must include a hard slide cap (recommended: 26-32 slides). Every
  addition after the cap is set requires a corresponding removal.

---

## Phase 5 — Build

**Purpose**: Build all HTML slide files per the approved slide plan. One agent
per act (3-5 slides each). Visual verification after each act batch.

**Inputs required**: `slide-plan.md`, `facts-manifest.json`, `constraints.json`

**Key artifacts**:
- Individual slide HTML files (e.g. `slide-01.html` through `slide-28.html`)
- `notes-data.js` — speaker notes for all slides (inline, not fetch-based)
- Updated `deck-state.json` with `build_progress` entries

**Gate condition**: All slides in `slide-plan.md` are built, visual verification
of representative slides (1, N/4, N/2, 3N/4, N) has passed, and zero blocking
issues are listed in deck-state.json open_issues.

**Agents dispatched**:
- `slide-builder` — 3-4 agents, one per act, dispatched in parallel
- `visual-reviewer` — 1 agent, dispatched after each act batch
- Parallelism: up to 4 (builder agents), 1 (visual reviewer)

**Refs loaded during this phase**:
- `html-template.md` (from deck-build skill) — slide HTML structure, CSS vars
- `css-constraints.md` — THE centering rules, flex rules, spacing rules
- `notes-format.md` — notes-data.js schema, RFP mapping format

**Phase-specific rules**:
- ALL constraints from constraints.json apply — especially css-vertical-centering,
  notes-inline-only, navigation-in-every-slide
- Every slide must pass the client specificity test (named system or figure)
- Notes must be in notes-data.js, never in slide body
- Navigation pill must be present in every slide

---

## Phase 6 — Validate

**Purpose**: Four-lens validation + council punch list + balance audit. Identify
all blocking issues before polish begins.

**Inputs required**: All slide HTML files, `slide-plan.md`, `facts-manifest.json`,
`constraints.json`

**Key artifacts**:
- `validation-pov.md` — POV clarity lens findings
- `validation-rfp.md` — RFP coverage lens findings
- `validation-reality.md` — Making It Real lens findings (CONCRETE/PARTIAL/ASPIRATIONAL/MISSING)
- `validation-know-them.md` — Know Them lens findings
- `council-punch-list.md` — prioritized punch list, blocking/non-blocking, deal-losers/winners
- `balance-audit.md` — content ratio analysis

**Gate condition**: `council-punch-list.md` exists AND contains zero blocking
items. Non-blocking items may remain; they are addressed in Phase 7.

**Agents dispatched** (in two waves):
- Wave 1 (parallel): `validation-lens` x4 + `balance-auditor` x1
  — Parallelism: up to 4
- Wave 2 (sequential): `council-reviewer` x1
  — Dispatched after all lens outputs are complete
  — Parallelism: 1

**Refs loaded during this phase**:
- `four-lens-validation.md` (from deck-validate skill) — lens definitions
- `council-punch-list.md` ref — council composition, punch list format
- `balance-audit.md` ref — content ratio analysis, redundancy detection

---

## Phase 7 — Polish

**Purpose**: Address non-blocking punch list items. Verify flow through persona
lenses. Balance audit if not already at target ratio. Final visual review.

**Inputs required**: `council-punch-list.md`, all slide HTML files

**Key artifacts**:
- `flow-review.md` — per-act ratings by persona, reorder recommendations
- Updated slides (after punch list fixes)
- Updated `deck-state.json` open_issues cleared

**Gate condition**: `flow-review.md` exists AND all non-blocking punch list items
are addressed OR explicitly deferred with user approval. Visual verification
passed.

**Agents dispatched**:
- `flow-reviewer` — 1 agent
- `visual-reviewer` — 1 agent (after flow fixes)
- `slide-builder` — inline for small fixes, subagent for 3+ slides
- Parallelism: 1 (sequential — flow review informs fixes)

**Refs loaded during this phase**:
- Same as Validate phase refs, loaded on demand

---

## Phase 8 — Export

**Purpose**: Produce delivery artifacts — PDF, bundled HTML, optionally PPTX.
Path audit, visual verification, final sign-off.

**Inputs required**: All slide HTML files, `notes-data.js`, completed deck-state.json

**Key artifacts**:
- `{deck-name}.pdf` — Chrome headless PDF
- `{deck-name}-bundle.html` — single-file bundled HTML
- `{deck-name}.pptx` (optional) — via slide-pipeline skill

**Gate condition**: Export artifacts exist AND visual verification of the PDF or
bundled HTML has passed (screenshots read with vision, not just file size check).

**Agents dispatched**:
- `export-bundler` — 1 agent per format
- `visual-reviewer` — 1 agent (mandatory, after every export)
- Parallelism: 1 per format (formats may run in parallel)

**Refs loaded during this phase**:
- `bundled-html.md` (from deck-export skill) — single-file HTML bundling recipe
- `pdf-generation.md` — Chrome headless PDF with path audit
- `visual-verification.md` — screenshot + vision verification protocol

**Phase-specific rules**:
- Temp files must be created within the deck directory, not in /tmp/
- All href/src paths must be audited after any file copy or move
- No export is declared complete until visual-reviewer agent passes the artifacts

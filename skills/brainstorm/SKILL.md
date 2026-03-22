---
name: brainstorm
description: |
  Run a structured dreamer-skeptic brainstorm session across three teams to produce
  a conflict-resolved, synthesized deck architecture. Methodology-only skill — no script.
  Claude orchestrates the session directly using persona pairs and synthesis rules.

  Use when: "brainstorm deck ideas", "dreamer-skeptic session", "ideation session",
  "run a brainstorm", "set up brainstorm teams", "explore deck angles",
  "what should the deck cover", "narrative arc ideas"
phase: ideate
pipeline_position: 3
---

# deck-brainstorm

Structured ideation methodology for proposal and presentation decks. Runs three parallel
dreamer-skeptic teams, then synthesizes their outputs into a single approved architecture
before any slide building begins.

---

## When to Use

At the start of any deck project, after the clarify phase has locked scope, and before
any slide-by-slide production begins. Do not run brainstorm while building. Do not build
while brainstorming. The gate between these phases is the single most important process
control in the pipeline.

**Prerequisite**: The clarify phase must produce a signed-off objective, acceptance
criteria, and source material list before the brainstorm begins.

---

## The Dreamer-Skeptic Methodology

Each team pairs one dreamer persona with one skeptic persona. The dreamer provides the
frame — the aspiration, the narrative arc, the emotional argument. The skeptic provides
the load-bearing structure — the mechanism, the evidence, the enforceability. Neither
dominates. The tension between them produces content that satisfies both.

**Core principle from Team 1**: "The deck is structured as a proof, not a pitch. Every
aspirational claim is immediately followed by a concrete mechanism."

**Why this works**: The dreamer in each pair represents the persona most likely to
champion the proposal. The skeptic represents the persona most likely to vote NO. If the
pair can agree on a narrative direction, that direction will survive the real committee.

**Pair interaction**: Dreamers and skeptics work as pairs, not sequentially. The skeptic
does not wait for the dreamer to finish — they challenge each claim in real time. This
produces a tighter output than sequential handoff.

---

## Three-Team Structure

The brainstorm runs three teams in parallel, each owning a distinct angle. Teams are
independent during ideation; they are synthesized after all three complete.

### Team 1 — Narrative and Story

**Dreamer**: CIO / CTO (visionary, transformation mandate)
**Skeptic**: VP Enterprise Architecture / Principal Engineer (structural rigor)

**What they own**:
- Overall narrative arc (the acts, the emotional journey, the opening and close)
- Governing principles for the deck (proof not pitch, mechanism before outcome)
- The protagonist story (who is the human in Act 1, what changes for them in Act 5)
- The hallway line (10-15 words, surprising, teaching, differentiating, repeatable)

**Their output**: A narrative arc document with act titles, emotional beats, the governing
principle, and a candidate hallway line. The skeptic must sign off on every claim.

### Team 2 — Operational Proof

**Dreamer**: VP Network Engineering (domain visionary, operational scale)
**Skeptic**: Principal Engineer (artifact-level rigor, failure mode awareness)

**What they own**:
- Proof slide requirements for every major capability claim
- The two-layer proof pattern (operational scenario + execution evidence)
- Domain-specific gates and SLA criteria
- Named systems, named metrics — no averages, no ranges without base/expected/upside

**Their output**: A proof slide specification listing every capability claim that needs
a mechanism slide, and the two-layer proof pattern that applies to all of them.

### Team 3 — Commercial Threading

**Dreamer**: SVP Finance / CFO Proxy (commercial differentiation, financial narrative)
**Skeptic**: Sr Director Strategic Sourcing (enforceability, procurement scrutiny)

**What they own**:
- Commercial threading concept (the commitment that builds throughout the deck)
- Financial bridge methodology (year-by-year, category-by-category)
- KPI definitions, trigger conditions, measurement methodology, cure periods
- Discussion questions that earn the meeting back at the close

**Their output**: A commercial threading plan mapping the commitment across all acts,
plus the financial model structure the deck must support.

---

## Synthesis Rules

After all three teams complete, the outputs are synthesized into a single approved
architecture. Do not begin building until this synthesis document is approved.

### Conflict Resolution Table

Every conflict between team outputs must be listed explicitly with a decision and
rationale. Common conflict types:

- **Slide count conflicts**: Teams may propose different totals. Resolve by adopting
  the narrative structure that most supports the commercial threading.
- **Act structure conflicts**: Teams may define act boundaries differently. The narrative
  arc (Team 1) takes precedence unless an act break serves the commercial culmination.
- **Claim-level conflicts**: Where Team 1 wants an aspiration and Team 2 demands proof,
  the proof requirement wins. No aspirational claims in the main deck.

### Threading Map

Map the top 3-5 key points to specific slide numbers. For each key point, state:
- Plant slide (introduce the concept, create the question)
- Build slides (brief callback per section, never more than 3 slides apart)
- Mechanics slide (full reveal — triggers, measurement, methodology)
- Culmination slide (resolution, what happens if wrong)

A key point that appears on fewer than 5 slides or has a gap larger than 3 consecutive
slides without mention is a threading failure. Fix before the architecture is approved.

### Slide-by-Slide Plan

For every slide in the synthesized architecture, document:
- Source: which team's output it came from
- Reuse decision: copy / edit / merge / new
- Key edits required: specific changes if not new

### Production Estimate

Include a production estimate (hours by category):
- New build
- Edit from source
- Merge (two sources into one slide)
- Theme convert
- Copy and proofread

**The gate rule**: Do not begin building until the synthesized architecture is approved
by the project owner. Building before brainstorming is complete is the single largest
source of rework. "No slide should exist before its purpose in the narrative is agreed."

---

## Integration with deck-pipeline

Brainstorm is Phase 3 in the hub-and-spoke pipeline:

```
Phase 1: Source Inventory    — read all sources, build facts manifest (orchestrator inline + slide-learn)
Phase 2: Personas            — build persona map with pass/fail criteria (orchestrator inline)
Phase 3: Brainstorm          — dreamer-skeptic ideation → synthesized architecture (deck-brainstorm)
Phase 4: Architecture Review — three-team review, validation, council punch list (orchestrator inline)
Phase 5: Build               — produce slides per approved plan (slide-generate + slide-pipeline)
Phase 6: Validate            — 4-lens validation + council punch list (slide-validate)
Phase 7: Polish              — flow cohesion + balance audit (orchestrator inline)
Phase 8: Export              — PDF, bundled HTML, PPTX (slide-pipeline + slide-render)
```

Phases without dedicated skills (1, 2, 4, 7) are orchestrated inline by Claude using
the methodology documented in deck-pipeline's references. The synthesized architecture
produced in Phase 3 becomes the production plan for Phase 5. Phase 4 review teams
check the architecture against persona pass/fail criteria before any slides are built.

The brainstorm does not produce slides. It produces the approved plan from which slides
are built. Treat the synthesized architecture document as a contract.

---

## Reference Files

| File | Purpose |
|------|---------|
| `references/brainstorm-teams.md` | Detailed team structure, persona pairs, interaction protocol, synthesis rules with examples |
| `references/content-principles.md` | 8 content patterns (mechanism before outcome, two-layer proof, protagonist arc, threading, client specificity, assertion titles, language sensitivity, speaker notes) + review scoring |
| `references/persona-framework.md` | Full 12-persona system with pass/fail criteria, dreamer-skeptic pairing recommendations, tier rankings, and usage across phases |

---

## Session Output Checklist

Before marking the brainstorm phase complete, verify:

- [ ] Team 1 narrative arc document complete and signed off by the skeptic
- [ ] Team 2 proof slide specification complete with named systems and metrics
- [ ] Team 3 commercial threading plan complete with KPI definitions
- [ ] Conflict resolution table explicit with all three teams' conflicts addressed
- [ ] Threading map covers all key concepts across all acts
- [ ] Slide-by-slide plan with reuse decisions for every slide
- [ ] Production estimate complete
- [ ] Architecture approved before any slide building begins

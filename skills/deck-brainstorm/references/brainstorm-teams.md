# Brainstorm Teams — Detailed Structure and Synthesis Protocol

Reference for `deck-brainstorm` skill. Documents the three-team structure, persona pairs,
interaction protocol, and synthesis rules with examples from the [CLIENT] session.

---

## Overview

Three teams run in parallel during the ideation phase. Each team owns a distinct angle
and produces an independent output. The outputs are then synthesized — never averaged —
into a unified architecture. The tension between teams is the point: if a claim survives
all three team lenses, it will survive the real evaluation committee.

---

## Team 1 — Narrative and Story

### Persona Pair

**Dreamer**: CIO or CTO — holds the transformation mandate, has board-level visibility,
speaks in terms of outcomes, portfolio evolution, and strategic positioning. Tends toward
aspiration. Does not naturally reach for mechanism.

**Skeptic**: VP Enterprise Architecture or Principal Engineer — holds the load-bearing
function. Evaluates every claim against: "How does this actually work? What are the
failure modes? Can we prove it?" Prevents the vision from becoming vaporware.

### What This Team Produces

1. **Narrative arc** — The act structure with titles, emotional beats, and transitions.
   Example from [CLIENT] session:
   - Act 1: Weight (the cost of the status quo)
   - Act 2: Architecture (how we solve it)
   - Act 3: Proof (operational evidence)
   - Act 4: Commitment (commercial structure)
   - Act 5: Resolution (what changes for you)

2. **Governing principles** — The rules every slide must obey. Team 1 produced:
   "The deck is structured as a proof, not a pitch. Every aspirational claim is
   immediately followed by a concrete mechanism."

3. **Protagonist story** — The human scenario that opens Act 1 and closes Act 5.
   Example from [CLIENT] session: "The last time [System-A] triggered a P1 at 2am, someone
   in this room was on the phone for six hours." Act 5 must return to that person
   transformed: "That engineer at 2am — this is what changes for them."
   The deck has a protagonist. It cannot abandon the protagonist.

4. **Hallway line** — A 10-15 word sentence that is surprising, teaches immediately,
   differentiates, and is repeatable in conversation. Team 1 generates 3-5 candidates;
   the synthesis selects one.
   Example from [CLIENT] session: "Don't give an agent a task. Give it a world to work in."

### Team 1 Skeptic's Role

The VP EA skeptic applies three tests to every claim the CIO dreamer makes:
1. "What is the mechanism?" — If there is no mechanism, the claim is aspirational and
   cannot appear in the main deck.
2. "Which specific systems does this apply to?" — No averages across all apps. Show
   variance at the tail.
3. "What is the failure mode?" — If the team cannot name a failure mode, they do not
   understand the mechanism well enough to claim it.

---

## Team 2 — Operational Proof

### Persona Pair

**Dreamer**: VP Network Engineering — operates at scale, knows the portfolio intimately,
can narrate the operational scenario with authority. Tends toward the comprehensive view.
Has seen transformation programs succeed and fail.

**Skeptic**: Principal Engineer / Engineering Director — lives in the artifact layer.
Reviews code changes, reads monitoring dashboards, handles incidents. Evaluates claims
against: "Show me the artifact. Show me the actual decision log. What does the output
look like at 2am?" Refuses to accept category-level claims.

### What This Team Produces

1. **Proof slide requirements** — A list of every major capability claim in the deck
   that requires a mechanism slide. For each claim: what the two layers are, what
   specific artifact or metric constitutes evidence.

2. **Two-layer proof pattern** — The standard that applies to every proof slide:
   - Layer 1: The operational scenario. What happens at 2am? What does the engineer
     experience? What does the [network-event] event look like from inside the system?
     This layer makes the claim feel real.
   - Layer 2: The execution evidence. The specific artifact, metric, decision log,
     or audit trail. This layer makes the claim defensible.
   You cannot have one layer without the other. A scenario without evidence is a story.
   Evidence without scenario is a data table. Neither is a proof slide.

3. **Domain-specific gates** — SLA thresholds, criticality tiers, escalation paths
   specific to the client's environment. Example from [CLIENT] session: governance tiers
   for all 323 apps, with variance shown at the tail (not averages).

### Team 2 Skeptic's Role

The Principal Engineer skeptic asks one question per claim: "If I were the engineer
reviewing this at 2am, what exactly would I see?" If the answer is "a dashboard showing
improvement," that is insufficient. The answer must name the specific output, the
specific metric, and the specific decision the artifact supports.

### Example from [CLIENT] Session

V2 slide 08 (Pillar 1: Know Portfolio) used the "2:47am scenario":
- Layer 1: [System-A] degradation event, criticality correctly identified despite no explicit
  SLA tag (scenario — operational context, human reality)
- Layer 2: Scored governance output showing the rationale, the override decision, and
  the audit trail (evidence — artifact + metric)

The Operators team principle: "Every proof slide has two layers. You cannot have one
without the other."

---

## Team 3 — Commercial Threading

### Persona Pair

**Dreamer**: SVP Finance / CFO Proxy — sees the commercial structure as the differentiator.
Understands that a fee-at-risk commitment changes the evaluation dynamic. Tends toward
the bold financial position. Has board-level exposure.

**Skeptic**: Sr Director Strategic Sourcing — evaluates every commercial claim against
enforceability. Asks: "What is the trigger? How is it measured? What is the cure period?
If I have to enforce this, can I?" Prevents the CFO from making commitments that cannot
be operationalized.

### What This Team Produces

1. **Commercial threading plan** — Maps the central commercial concept (e.g., fee-at-risk)
   across all acts of the deck:
   - **Plant** (Act 1): State the commitment as a headline. Create the question. Do not
     elaborate. The audience should leave Act 1 wondering: "How does that actually work?"
   - **Build** (Acts 2-3): Brief callback per section ("This pillar's KPI: [metric]").
     Never more than 3 slides apart without a mention. The LONGEST gap must not exceed
     15 minutes of presentation time.
   - **Mechanics** (Act 3): Full reveal. Triggers, non-triggers, measurement methodology,
     quarterly cadence, cure periods. This is where the skeptic's enforceability work lives.
   - **Culminate** (Act 4/5): Resolution. "What happens if we're wrong?" as the emotional
     peak. The commitment comes full circle.

2. **Financial bridge** — The methodology for connecting the commercial commitment to
   year-by-year, category-by-category savings. Must be specific enough that a CFO proxy
   can validate it. Named figures, not ranges. If a range, provide base/expected/upside.

3. **KPI definitions** — For each pillar or workstream in the deck, the specific KPI
   that measures it, the trigger condition, and the measurement period.

4. **Discussion questions** — The 2-3 questions the presenter asks at the close to earn
   the meeting back. Questions must reveal client knowledge and create a natural follow-on.

### Team 3 Skeptic's Role

The Sourcing skeptic applies enforceability tests to every commercial claim:
1. "What is the trigger?" — If the trigger is vague, the commitment is unenforceable.
2. "How is it measured?" — If the measurement methodology is undefined, it will be
   disputed in year two.
3. "What is the cure period?" — Sourcing needs to know what remediation looks like
   before they recommend the contract.

### Example from [CLIENT] Session

V2 fee-at-risk threading:
- Slide 3 PLANT: "[total-value] savings exposure at [fee-value] fee-at-risk" — creates the question
- Slides 8-11 BUILD: Each pillar callback ("This pillar's KPI: [metric]")
- Slide 12 MECHANICS: Full reveal — triggers, non-triggers, measurement methodology,
  quarterly cadence
- Slide 13 AI connection: Bridge from mechanism to intelligence layer
- Slide 20 CULMINATION: "What happens if we're wrong?" — emotional peak
- Slide 21 RESOLUTION: The answer to Act 1's question
- Slide 22 INVITATION: Discussion questions

Team B caught that slides 10-18 (15 minutes of presentation time) had no fee-at-risk
reference. Fixed by adding a bridge sentence to slide 13.

---

## Interaction Protocol

The dreamer and skeptic work as a pair throughout the session, not sequentially. The
skeptic does not wait for the dreamer to finish a narrative before challenging it. This
is not a review — it is a live negotiation.

Session structure for each team:
1. **Dreamer opens** with the narrative direction (15 minutes)
2. **Skeptic challenges** each claim in real time — "What is the mechanism? What is
   the evidence? What is the failure mode?" (20 minutes of live negotiation)
3. **Pair agrees** on what survives the challenge — only surviving claims enter the output
4. **Pair documents** the output in the standard format (15 minutes)

Teams do not observe each other's sessions. Cross-pollination happens in synthesis, not
during ideation. If teams influence each other during ideation, the outputs will converge
before synthesis, eliminating the productive tension.

---

## Synthesis Protocol

After all three teams complete, the synthesis produces a single architecture document.

### Step 1 — Conflict Resolution Table

List every conflict between team outputs. For each conflict:
- State the conflict explicitly (not "there was disagreement about act structure" but
  "Team 1 proposed 5 acts / 38 slides; Team 3 proposed 4 acts / 42 slides")
- State the decision
- State the rationale

Common conflict types and resolution heuristics:

| Conflict Type | Resolution |
|---------------|-----------|
| Slide count | Adopt the narrative structure that most supports commercial threading |
| Act structure | Team 1 narrative logic takes precedence unless a break serves Team 3 culmination |
| Claim-level | Proof requirement (Team 2) wins over aspiration (Team 1) always |
| Commercial position | Team 3 enforceability requirement wins over Team 1 boldness |
| Sequence | The sequence that best builds the protagonist arc (Team 1) wins |

Example from [CLIENT] session: B1's 5-act/38-slide plan vs. B4's 4-act/42-slide plan.
Decision: 5 acts/40 slides. Rationale: "B1's 5-act narrative logic is stronger — the
separation of 'Proof in 90 Days' from 'The Commitment' matters for CFO and CIO personas."

### Step 2 — Threading Map

Map the top 3-5 key points to specific slide numbers. For each key point, document
the plant / build / mechanics / culmination slides. Verify:
- No key point has fewer than 5 slide mentions
- No gap of more than 3 consecutive slides without a mention
- Mechanics slide exists for every key point (full reveal, not just callbacks)

### Step 3 — Slide-by-Slide Plan

For every slide in the synthesized architecture:

| Slide # | Title | Source | Reuse Decision | Key Edits |
|---------|-------|--------|----------------|-----------|
| 1 | [Title] | Team 1 | New | n/a |
| 2 | [Title] | Team 2 + B3 | Merge | Combine operational scenario with financial bridge |
| ... | ... | ... | ... | ... |

Reuse decisions: copy (no changes), edit (specific changes listed), merge (two sources),
new (no prior source). For edits and merges, list the specific changes required.

### Step 4 — Production Estimate

| Category | Hours |
|----------|-------|
| New build | |
| Edit from source | |
| Merge (two sources into one) | |
| Theme convert | |
| Copy and proofread | |
| **Total** | |

### Step 5 — Approval Gate

The synthesized architecture must be approved before any slide building begins. This is
not optional. It is the process control that prevents the most expensive failure mode:
reworking slides when the narrative changes after building starts.

Approval criteria:
- All three teams have signed off on the conflict resolution decisions
- Threading map is verified (no gaps, no key points with fewer than 5 mentions)
- Slide-by-slide plan is complete for every slide
- Production estimate is complete
- Project owner has explicitly approved

The gate statement: "Do not begin building until this document is approved."

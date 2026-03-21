# Persona Framework — 12-Persona Evaluation Committee System

Reference for `deck-brainstorm` skill. Documents the complete persona system, pass/fail
criteria, dreamer-skeptic pairing recommendations, tier rankings, and usage across
pipeline phases.

---

## Purpose

The 12-persona system models the full evaluation committee for a proposal deck. Each
persona is characterized by their primary concern (what they evaluate on), their biggest
fear (what causes a NO vote), and how to win their support. Personas are used across
all pipeline phases: brainstorm pairing, review validation, council punch list, and
slide-level targeting.

---

## Full Persona Table

| # | Persona | Role | Primary Concern | Biggest Fear | How We Win |
|---|---------|------|----------------|-------------|------------|
| 1 | Network Continuity Owner | VP Network Systems Engineering | Network stability and delivery of the right thing | AI accelerates delivery of the wrong thing | Network-domain-specific SDLC gates with criticality tiers |
| 2 | Cost Transformation Sponsor | SVP Finance / CFO Proxy | Contractual savings with financial specificity | Savings are year-3 only, hidden change orders | Financial bridge doc with quarterly savings and clawback |
| 3 | Strategic Sourcing Architect | Sr Dir Strategic Sourcing | Vendor selection defensibility | Recommending the wrong vendor to leadership | Tangible IP artifacts, named references, enforceability |
| 4 | Incumbent Relationship Manager | VP Vendor Management | Continuity through transition | Chaotic handover, delivery gaps during transition | Structured transition playbook with day-by-day handover |
| 5 | Principal Engineer in Trenches | Principal Engineer / Eng Director | Artifact-level proof, real operational evidence | AI-generated noise, inherited tech debt | Working session with real artifacts; two-layer proof |
| 6 | CISO / Carrier Compliance | CISO / VP Cybersecurity | Data security, regulatory compliance | Data egress, regulatory exposure from AI | Full AI security architecture; [regulatory-data], Model Cards treatment |
| 7 | Workforce Strategy Director | VP HR / Workforce Strategy | Workforce impact and union relations | "Client cuts jobs via AI" headline | Contractual retraining program; [union-agreement]-safe language throughout |
| 8 | App Rationalization Skeptic | VP Enterprise Architecture | System interdependencies and migration risk | Retiring apps with hidden dependencies | Discovery-first methodology; dependency mapping before commitment |
| 9 | Business Unit Sponsor | SVP Network Operations | Speed to value, operational outcomes | Another multi-year consulting engagement | "Day 90" narrative with specific, named outcomes |
| 10 | Board-Level Risk Lens | CRO / Board Audit Committee | Enterprise risk and AI governance | AI incident without due diligence on record | AI risk allocation framework; documented governance |
| 11 | Internal IT Champion | CIO / SVP Technology Delivery | Strategic program success and career exposure | Program fails, career risk | Co-designed governance; CIO photographs this slide standard |
| 12 | Existing Vendor Insider | Incumbent program director | Account retention | Losing the account | Pre-answer their objections; position continuity not displacement |

---

## Pass/Fail Criteria Per Persona

Each persona evaluates the deck through a specific lens. Understanding the lens, pass
condition, fail condition, and hardest question makes slide validation concrete.

### P1 — Network Continuity Owner

**Lens**: Does the proposal demonstrate domain-native understanding of network delivery
risk? Not general software delivery — specifically telecom network operations.

**Pass condition**: Every major claim has a network-specific SDLC gate, named system,
and criticality tier assigned. The proposal shows variance at the tail of the portfolio,
not averages across all applications. The 2am scenario is named and the system response
is shown.

**Fail condition**: Generic delivery methodology without network-specific gates.
Averages across all 323 applications without showing variance. Claims about AI that
apply equally well to any software portfolio.

**Hardest question**: "Which of our 323 applications would your governance system
score differently than our current classification, and why?"

---

### P2 — Cost Transformation Sponsor

**Lens**: Is the financial model contractually specific with quarterly visibility?
Can savings be tracked and audited?

**Pass condition**: Financial bridge document exists with year-by-year, category-by-category
savings. Clawback mechanism is defined. Quarterly savings schedule is visible. Named
figure, not a range. If a range, base/expected/upside are all stated.

**Fail condition**: Year-3 heavy savings profile. Savings attributed to "AI efficiency"
without named mechanism. No clawback mechanism. Range without anchors.

**Hardest question**: "25% of fees at risk at $1B = [risk-exposure]. What happens to your firm
if you miss every quarter for two years? Walk me through your financial exposure."

---

### P3 — Strategic Sourcing Architect

**Lens**: Is the proposal defensible to a sourcing committee? Is IP tangible and auditable?

**Pass condition**: Tangible IP artifacts are named and described. Reference program
names are provided. Methodology is described with enough specificity that sourcing
can write evaluation criteria from it.

**Fail condition**: "Proprietary methodology" without description. Reference clients
named but not described in relevant terms. Claims that a sourcing committee cannot score.

**Hardest question**: "If we request a proof-of-concept engagement before contract
signature, what would you deliver and in what timeframe?"

---

### P4 — Incumbent Relationship Manager

**Lens**: Is the transition plan structured enough to protect continuity?
What does the handover actually look like?

**Pass condition**: Structured transition playbook exists with day-by-day handover
milestones. Knowledge transfer methodology is named. Communication plan for incumbent
teams is described.

**Fail condition**: "Seamless transition" language without a plan. Handover described
as discovery (signals chaos). No methodology for knowledge transfer from incumbent systems.

**Hardest question**: "What happens to the 47 people who currently operate these systems?
Who calls them on day one?"

---

### P5 — Principal Engineer in Trenches

**Lens**: Are claims artifact-level defensible? Will the proposed systems create
technical debt?

**Pass condition**: Two-layer proof on every capability claim (scenario + evidence artifact).
Named systems, named outputs, named metrics. No averages. Working session is offered
to validate claims in context.

**Fail condition**: Capability named but not explained (label not capability).
Generic AI claims without client-specific grounding. "We will assess in Phase 1"
language for any core technical claim.

**Hardest question**: "Show me the actual output your governance system produces for
an [System-A] criticality assessment. Not a mockup — the real output."

---

### P6 — CISO / Carrier Compliance

**Lens**: Binary pass/fail. Either the AI security architecture is complete and
addresses carrier-grade compliance, or it is not. No partial credit.

**Pass condition**: Full AI security architecture slide. [regulatory-data] treatment documented.
Model Cards described. Data egress controls named. Architecture-agnostic hosting
treatment (not locked to one cloud provider's security posture).

**Fail condition**: Security described as "enterprise-grade" without carrier specifics.
[regulatory-data] not addressed. Data residency not addressed. AI model provenance not addressed.
Any security claim that requires follow-up to answer.

**Hardest question**: "What data transits your AI systems? Where does it reside?
What happens if there is a [regulatory-data] violation in an AI-generated log?"

---

### P7 — Workforce Strategy Director

**Lens**: Will this create a labor relations problem?
Does the proposal pass a union representative's reading?

**Pass condition**: [union-agreement]-safe language throughout. Workforce narrative is affirmative
(capacity expansion, not reduction). Contractual retraining program is named.
Capacity data labeled as redeployment, not headcount. The workforce slide makes
a union representative nod, not pick up the phone.

**Fail condition**: Any use of: leaner teams, headcount reduction, labor savings,
right-sizing, role elimination, offshore substitution. Workforce data presented as
headcount without redeployment framing. No retraining commitment.

**Hardest question**: "If I show this deck to the [union-agreement] local, what will they flag?
Walk me through every workforce commitment in this proposal."

---

### P8 — App Rationalization Skeptic

**Lens**: Does the methodology protect against retiring systems with undiscovered
dependencies?

**Pass condition**: Discovery-first methodology. Dependency mapping before any
rationalization commitments. Assessment phase with explicit go/no-go gate before
retirement planning.

**Fail condition**: Retirement recommendations before discovery. Rationalization
commitments based on surface-level app inventory. "We will assess in Phase 1"
without describing the assessment methodology.

**Hardest question**: "Which of the 11 elimination candidates has the highest hidden
dependency risk, and how would your methodology surface that before we act on it?"

---

### P9 — Business Unit Sponsor

**Lens**: Is there a concrete outcome visible within 90 days? Or is this another
multi-year consulting engagement?

**Pass condition**: "Day 90" narrative with named, specific outcome. Not "we will
have completed Phase 1" but "by day 90, [specific system] will be running [specific
process] with [specific metric] visible."

**Fail condition**: Multi-year roadmap without near-term milestones. Outcomes that
require 18 months of discovery before being defined. The answer to "what do we see
in 90 days?" is "it depends on what we find."

**Hardest question**: "I have been on the call when a program like this is announced.
Two years later, the team is still in discovery. What makes this different? Name one
thing I can show my CFO in 90 days."

---

### P10 — Board-Level Risk Lens

**Lens**: Is there a documented AI risk allocation framework? Has due diligence been
performed?

**Pass condition**: AI risk allocation framework is named and described. Governance
model is documented. Incident response process for AI decisions is described.
Board-level visibility into AI governance is addressed.

**Fail condition**: No AI risk allocation framework. "We follow industry best practices"
without description. No incident response process described for AI-influenced decisions.
AI governance described as a Phase 2 deliverable.

**Hardest question**: "If your AI system influences a network routing decision that
causes a service outage affecting 1M customers, who is accountable and what is the
documentation trail?"

---

### P11 — Internal IT Champion

**Lens**: Will this program succeed? Is it co-designed with enough governance that
the CIO can defend it internally?

**Pass condition**: Co-designed governance. CIO has visible ownership of key decisions.
The "CIO photographs this slide" standard: slide 7 (the architecture) and slide 33
(the commitment) must be compelling enough that the CIO wants to share them. The
hardest governance questions are answered in the deck, not deferred.

**Fail condition**: Governance described as vendor-managed. CIO role in decision-making
is advisory only. Fee-at-risk mechanics are vague enough that a CFO challenge would
expose them. "We will work with your team to design governance" language.

**Hardest question**: "If this program fails — and I define failure as missing the
committed savings target for two consecutive quarters — what exactly happens? Walk me
through the contract mechanics and the internal accountability chain."

---

### P12 — Existing Vendor Insider

**Lens**: This persona is not an evaluator in the traditional sense. They are in the
room representing the incumbent. Their concern is retention; their behavior is to find
gaps that justify the status quo.

**Pass condition**: Pre-answer their objections before they can raise them. Position
the proposal as evolution, not displacement. Use language that acknowledges the
incumbent's contributions and frames the proposal as a continuation.

**Fail condition**: Language that sounds like a critique of the current state
(implies criticism of the incumbent). Transition plan that is vague (creates fear).
"Starting from scratch" framing. No acknowledgment of existing knowledge.

**Hardest question** (they will ask): "Our team has been operating these systems for
eight years. What is your plan to capture that institutional knowledge, and what
happens if we're not cooperative during the transition?"

---

## Three Make-or-Break Evaluation Criteria

Three personas represent binary gates. Fail any one of these and the proposal does
not advance regardless of performance on other criteria.

### 1. Security Gate — CISO (P6)

Binary pass/fail. The CISO does not give partial credit. Either the AI security
architecture is complete and carrier-grade, or the proposal is disqualified before
a committee vote. This gate must be addressed first — before narrative polish,
before financial modeling. A beautiful deck that fails the security gate does not advance.

What "complete" means:
- [regulatory-data] treatment documented
- Data egress controls named
- Model Cards described or referenced
- Architecture-agnostic hosting treatment
- Incident response for AI-influenced decisions described

### 2. Financial Model Specificity — CFO Proxy (P2)

Contractual savings with clawback. The CFO proxy does not vote for a savings claim
without a measurement mechanism. Quarterly visibility, named figures, defined triggers.
A financial model that cannot be audited is not a financial model.

What "specific" means:
- Year-by-year savings schedule (not year-3 backloaded)
- Category-by-category breakdown
- Measurement methodology named
- Trigger conditions for fee-at-risk defined
- Cure period defined

### 3. Domain Credibility — Network Continuity Owner (P1)

Telecom-native proof, not generic AI delivery methodology. The Network Continuity Owner
will reject a proposal that treats network delivery like enterprise software delivery.
Named systems, named criticality tiers, named SDLC gates specific to telecom.

What "domain credible" means:
- Named client systems ([System-A], CONNECT, [System-C] — not "mission-critical applications")
- Criticality tiers described for the client's specific portfolio
- Network-specific SDLC gates described
- Operational scenarios drawn from the client's actual environment

---

## Dreamer-Skeptic Pairing Recommendations

### Recommended Pairs by Session Type

| Session | Dreamer | Skeptic | Productive Tension |
|---------|---------|---------|-------------------|
| Narrative brainstorm | P11 (CIO) | P8 (VP EA) | Vision vs. structural rigor |
| Operational proof | P1 (VP Network Eng) | P5 (Principal Eng) | Scale vs. artifact-level evidence |
| Commercial threading | P2 (SVP Finance) | P3 (Sr Dir Sourcing) | Bold position vs. enforceability |
| Validation review | P9 (BU Sponsor) | P5 (Principal Eng) | Speed vs. mechanism depth |
| Council punch list | P11 (CIO) | P5 + P2 | Multiple skeptics for final gate |

### Why These Pairs Work

**CIO (P11) + VP EA (P8)**: The CIO holds the transformation mandate and speaks in
outcomes. The VP EA holds the structural constraint — every claim that cannot be
supported by a named mechanism is rejected. The CIO's vision survives this pair only
if it has a mechanism. The result: aspirational claims that are defensible.

**VP Network Eng (P1) + Principal Eng (P5)**: The VP operates at scale and narrates
the operational landscape. The Principal Engineer lives in the artifact layer and
refuses to accept category-level claims. The result: operational scenarios backed by
specific artifacts. The two-layer proof pattern emerged from this pair.

**SVP Finance (P2) + Sr Dir Sourcing (P3)**: The SVP Finance sees the commercial
structure as the differentiator and pushes for bold positioning. The Sourcing Director
evaluates every commitment against enforceability. The result: commercial structures
that are aggressive and contractually defensible.

### Pairs That Do Not Work

**Two dreamers**: Without a skeptic, the pair produces aspirational content with no
mechanism. Every claim sounds compelling; none is defensible. The deck becomes a pitch.

**Two skeptics**: Without a dreamer, the pair produces a risk register, not a proposal.
Every claim is hedged; none is compelling. The deck becomes a set of caveats.

**Wrong pair for the content area**: Pairing a commercial dreamer (P2) with a technical
skeptic (P5) produces financial claims tested against technical reality — useful for
mechanism validation, not for commercial structure design. Match the dreamer to the
domain and the skeptic to the most likely NO vote.

---

## Persona Usage Across Pipeline Phases

### Phase 1 — Clarify

Define the evaluation committee composition. Identify which of the 12 personas are
present (some projects have 7; others have all 12). Identify which personas are Tier 1
for this project (will drive the most material changes). Set pass/fail criteria for
each present persona before any brainstorming begins.

### Phase 3 — Brainstorm

Assign personas to dreamer-skeptic pairs. Dreamers are selected from personas who
champion the proposal; skeptics are selected from personas most likely to vote NO.
Use the persona's primary concern to drive the dreamer's direction; use the persona's
biggest fear to drive the skeptic's challenges. The pair's output must satisfy both.

### Phase 4 — Review (Three-Team Review)

Each review team adopts a persona blend for their lens:
- Team A (Narrative/Story): P11 (CIO) and P9 (BU Sponsor) — audience engagement
- Team B (Commercial/Legal): P2 (CFO), P3 (Sourcing), P4 (Vendor Mgmt) — financial accuracy
- Team C (Technical/Production): P5 (Principal Eng), P6 (CISO), P8 (VP EA) — data integrity

### Phase 4 — Validation Brainstorms

Each validation lens adopts specific personas:
- POV Clarity: P11 (CIO) and P8 (VP EA) — does the mechanism show?
- RFP Coverage: P3 (Sourcing) and P1 (Network Owner) — are requirements addressed?
- Making It Real: P5 (Principal Eng) — is each concept CONCRETE/PARTIAL/ASPIRATIONAL?
- Know Them: P5 (Principal Eng) and P12 (Existing Vendor) — is client specificity real?

### Phase 4 — Council Punch List

Council composition: Skeptic + Buyer + Operator. In persona terms:
- Skeptic: P5 (Principal Eng) or P8 (VP EA)
- Buyer: P11 (CIO) or P2 (CFO)
- Operator: P1 (Network Owner) or P9 (BU Sponsor)

All three must agree before the punch list is finalized. A punch list that one council
member would reject is not ready.

---

## Tier Rankings

Not all personas drive equal change. Based on the [CLIENT] session, personas ranked by
impact on final deck:

### Tier 1 — Drove the Most Material Changes

**P11 — CIO / SVP Technology Delivery**
- Drove the "CIO photographs this" standard for key slides (the architecture slide and
  the commitment slide must be compelling enough to share)
- The hardest CIO question forced fee-at-risk mechanics to be concrete: "25% of fees
  at risk at $1B = [risk-exposure]. What happens to your firm if you miss every quarter for two years?"
- Governance co-design requirement emerged from CIO validation

**P5 — Principal Engineer / Eng Director**
- Drove the two-layer proof pattern: operational scenario plus execution evidence
- Drove the "mechanism before outcome" principle
- Forced every capability claim to have operational evidence — no category claims
- Every slide that passed the Principal Engineer test passed all downstream technical review

**Frontier Integration PM (project-specific, analogous to P9 / P1 blend)**
- Was rated RED in both V1 and V3, forcing addition of a dedicated slide
- The fail condition eliminated discovery-as-strategy language: "'We will assess in
  Phase 1' = DISQUALIFYING"
- Most underweighted persona in early versions; most structurally impactful when addressed

**P2 — SVP Finance / CFO Proxy**
- Drove the fee-at-risk drumbeat threading pattern
- Drove the savings bridge methodology (year-by-year, category-by-category)
- KPI definition requirement for every pillar emerged from CFO validation

### Tier 2 — Drove Specific Critical Fixes

**P6 — CISO / VP Cybersecurity**
- Binary pass/fail gate that forced [regulatory-data], Model Cards, and architecture-agnostic hosting
- Forced the AI security architecture slide to be specific and complete
- Zero partial credit — either the security architecture was complete or it was not

**P7 — VP HR / Workforce Strategy**
- Forced the [union-agreement]-safe language audit across all slides
- "Expanded Capability Model" reframing emerged from HR validation
- Workforce slide rewrite from defensive to affirmative

### Tier 3 — Provided Useful Validation, Fewer Structural Changes

The remaining personas (P3, P4, P8, P9, P10, P12) confirmed adequacy or flagged
incremental improvements, but did not drive structural changes to the deck architecture.
This does not mean they are unimportant — P4's transition playbook requirement and
P10's AI risk framework are both critical to the final product. They did not drive
the structural and narrative decisions that Tier 1 personas drove.

**Implication for resource allocation**: In a time-constrained project, prioritize
satisfying Tier 1 personas first. Build slides for Tier 1 pass conditions before
addressing Tier 2 and Tier 3. Do not let a Tier 3 persona's preferences override a
Tier 1 pass condition.

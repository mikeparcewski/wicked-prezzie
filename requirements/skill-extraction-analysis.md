# [CLIENT] Deck Project — Skill Extraction Analysis
## Patterns, Anti-Patterns, and Reusable Skills from v1/v2/v3

---

## 1. TOP 10 WORKFLOW SKILLS

### Skill 1: Run Dreamer-Skeptic Brainstorm

**When to use**: At the start of any proposal or deck project, during ideation phase, before any slide architecture is locked.

**What it produces**: A converged narrative direction that balances aspiration with rigor. Three team outputs that can be synthesized into a unified architecture.

**Key rules/constraints**:
- Pair one "dreamer" persona (CIO, CTO, visionary) with one "skeptic" persona (Principal Engineer, Procurement, Finance) per brainstorm team
- Each team owns a distinct angle: Team 1 = narrative/story, Team 2 = operational proof, Team 3 = commercial threading
- Dreamer provides the frame; skeptic provides the load-bearing structure
- The core principle from Team 1: "The deck is structured as a proof, not a pitch. Every aspirational claim is immediately followed by a concrete mechanism."

**Example**: V2 used three teams — Visionaries (CIO dreamer + VP EA skeptic), Operators (VP Network Eng dreamer + Principal Eng skeptic), Commercials (SVP Finance dreamer + Sr Dir Sourcing skeptic). Each produced an independent narrative arc that was then synthesized into the unified 22-slide architecture. The Operators team surfaced the "two-layer proof" pattern (operational scenario + execution evidence) that became the standard for every proof slide.

---

### Skill 2: Synthesize Multi-Source Brainstorms into Unified Architecture

**When to use**: After 3+ brainstorm outputs exist and before slide-by-slide building begins.

**What it produces**: A single, conflict-resolved slide plan with exact slide numbers, reuse decisions, key point threading, and production estimates.

**Key rules/constraints**:
- Explicitly list every conflict between brainstorm outputs in a conflict resolution table (decision + rationale)
- Map top key points to specific slide numbers (threading map)
- For each slide: source, reuse decision (copy/edit/merge/new), key edits required
- Include a production estimate (hours by category: new build, edit, merge, theme convert, copy)
- Do not begin building until this document is approved

**Example**: Brainstorm 05 (synthesized-proposal.md) reconciled B1's 5-act/38-slide plan with B4's 4-act/42-slide plan, landing on 5 acts/40 slides. It resolved the slide count conflict, act structure conflict, reuse decisions, and threading map in a single document. Key decision: "B1's 5-act narrative logic is stronger — the separation of 'Proof in 90 Days' from 'The Commitment' matters for CFO and CIO personas."

---

### Skill 3: Run Three-Team Review (Narrative / Commercial / Technical)

**When to use**: After the synthesized architecture is complete but before production begins.

**What it produces**: Conditional approvals with specific blocking/standing conditions, reorder recommendations, and legal review gates.

**Key rules/constraints**:
- Three teams review in parallel, each with a defined lens:
  - Team A (Narrative/Story): flow, ordering, emotional arc, audience engagement
  - Team B (Commercial/Legal): financial accuracy, legal exposure, IP language, distribution gates
  - Team C (Technical/Production): data integrity, production feasibility, [union-agreement]-safe language, version audits
- Each team produces: question decisions (from open questions), reorder proposals, additional recommendations, blocking requirements
- All three must reach "CONDITIONAL APPROVE" before production starts
- Conditions are deduped and reconciled in a final agreed plan

**Example**: In V2, Team A caught that Act 1 should end on weight not solution (moved Pathfinder from slide 9 to Act 4), Team B caught that case study names needed sanitization for main deck, Team C caught [union-agreement]-trigger language ("Role Transformation" renamed to "Expanded Capability Model"). The reconciled plan had 26 conditions, 15 blocking.

---

### Skill 4: Run Validation Brainstorms (4 Lenses)

**When to use**: After the agreed plan is complete, before or during production, to catch gaps the review teams missed.

**What it produces**: Specific blocking gaps with fix instructions, rated at BLOCKING / RECOMMENDED / APPENDIX priority.

**Key rules/constraints**:
- Four distinct validation lenses, each asking one question:
  1. **POV Clarity**: "Are we providing our point of view clearly?" — Checks that named concepts actually have visible mechanisms
  2. **RFP Coverage**: "Does the deck cover the RFP requirements?" — Checks every metric, SLA, and requirement against slide content
  3. **Making It Real**: "Is the solution actually explained, not just named?" — Rates each concept as CONCRETE / PARTIAL / ASPIRATIONAL / MISSING
  4. **Know Them**: "Have we made it clear how well we know this client?" — Checks for named systems, operational history, leadership awareness
- Each lens produces a rated gap list with specific slide-level fixes and source references
- Concepts rated ASPIRATIONAL or MISSING are blocking gaps

**Example**: Validation 3 ("Making It Real") rated 5 of 9 major concepts as ASPIRATIONAL or MISSING in v3 — Scored Governance had no rubric, Knowledge Layer had no retrieval mechanism, IQ Accelerators had no descriptions. This produced the key insight: "The deck names the right concepts but leaves the mechanisms inside those concepts unexplained. Slides 19-24 in Act 3 are where the deck lives or dies."

---

### Skill 5: Run Council Punch List (Critical Council)

**When to use**: As the final quality gate before production is considered complete. After validation brainstorms have been processed.

**What it produces**: A prioritized punch list of 10-15 specific edits with exact slide numbers, exact language to add/change, source references, and blocking/non-blocking classification. Plus "3 things that will lose the deal" and "3 things that will win the deal."

**Key rules/constraints**:
- Council composition: Skeptic + Buyer + Operator (all three must agree)
- Every item in the punch list must specify: priority number, slide number, gap description, exact fix instruction, source document, action type (edit/new), blocking status
- The "3 things that will lose/win" must be specific enough to guide prioritization when time is short
- New slides identified in punch list must have a title, content spec, and blocking justification

**Example**: The v3 council punch list (brainstorm 14) identified 15 items, 11 blocking. The verdict: "The deck is structurally sound and commercially differentiated — but it is not yet a winning deck. It names the right concepts and buries the mechanisms." Three deal-losers: (1) Frontier PM has zero coverage, (2) fee-at-risk has no calibration mechanism, (3) five of six core concepts in slides 19-24 are aspirational.

---

### Skill 6: Run Content Balance Audit

**When to use**: After a deck is near-complete, to check whether the slide mix actually supports the narrative strategy.

**What it produces**: A ratio analysis (client proof vs. solution depth vs. both), redundancy cluster identification, missing concept list, and proposed restructuring plan.

**Key rules/constraints**:
- Categorize every slide as: Client Proof only, Solution Mechanism only, or Both
- Target ratio: ~30% proof, ~40% solution, ~30% both (not 55% proof / 30% solution as v3 had)
- Identify redundancy clusters (multiple slides saying the same thing)
- List solution concepts with ZERO slides
- Propose specific cuts and additions that maintain slide count but shift the ratio

**Example**: Brainstorm 15 found v3 was 55% client proof and only 30% solution. Four redundancy clusters were identified: "We know your portfolio" (3 slides), "We understand urgency" (3 slides), "Five pillars" (named then re-named), "Trust us" (4 slides in Act 5). Seven solution concepts had zero slides, including Scoring Engine, Predictive Quality Engine, Self-Healing Pipeline, and Security Automation. The fix: cut 6 redundant slides, add 6 mechanism slides, same total count.

---

### Skill 7: Run Flow Cohesion Review

**When to use**: After content is near-final, to check whether the deck flows as a presentation (not just as a document).

**What it produces**: Per-act ratings by persona, reorder recommendations, missing transitions, slides to compress/cut, and an ideal one-sentence-per-act summary.

**Key rules/constraints**:
- Rate each act through 5 persona lenses (CIO, VP Ops, CFO, Engineer, VP EA) as STRONG / ADEQUATE / WEAK
- Identify the 3-5 biggest flow problems
- Propose specific reorders with rationale
- Write 1-line transition sentences for the 4 biggest seams
- Identify slides that can be compressed or moved to appendix without losing the narrative

**Example**: Brainstorm 19 rated the deck 6.5/10 overall. Key finding: "Act 2 is 9 slides of philosophy when audience is already sold on AI." Five problems identified, five reorder recommendations, four missing transitions. The ideal one-line summary for each act proved to be a powerful test: if you cannot state the act's purpose in one sentence, the act is unfocused.

---

### Skill 8: Build Persona Review Framework

**When to use**: At project start, during clarify phase, before any brainstorming begins.

**What it produces**: A per-persona review criteria document with pass/fail conditions, must-hit slides, and hardest questions.

**Key rules/constraints**:
- For each persona: lens (what they evaluate), pass criteria, fail criteria, must-hit slide numbers, and the single hardest question they will ask
- Personas should cover the full evaluation committee, not just the buyer
- Include structural tests for the full deck: narrative flow, recurring threads (like fee-at-risk), sensitivity audits ([union-agreement], security)
- Include insider language checklist (specific numbers, initiatives, terminology the client uses)

**Example**: V1 defined 12 personas with pass/fail criteria. The Frontier Integration PM's fail condition was devastating: "'We will assess in Phase 1' = DISQUALIFYING." The hardest question for the CIO: "'25% of fees at risk at $1B = [risk-exposure]. What happens to your firm if you miss every quarter for two years?'" These criteria were used to validate every slide after building.

---

### Skill 9: Build Slide Reuse Inventory

**When to use**: When creating a new version of an existing deck, or when multiple source decks exist.

**What it produces**: A categorized inventory of every slide across all source decks: REUSE AS-IS, REUSE WITH EDITS (specific edits listed), SKIP (with reason), and coverage gaps.

**Key rules/constraints**:
- For each reuse decision, state the specific reason (not just "keep" or "skip")
- For edits, list the exact changes needed
- Identify coverage gaps: concepts that appear in one source but not others
- Rate gaps as HIGH / MEDIUM / LOW priority
- This inventory becomes the source of truth for the synthesized architecture

**Example**: Brainstorm 03 inventoried 42 slides across v1 and v2: 22 reuse as-is, 14 reuse with edits, 6 skip. The coverage gap analysis was critical — it identified 9 concepts from v1 that v2 lacked (macro context, savings bridge, bottleneck shift, SDLC swim lanes, modernization 75/25 model, etc.), all rated HIGH priority.

---

### Skill 10: Sequence: Clarify, Ideate, Design, Build, Review

**When to use**: As the master workflow for any deck project.

**What it produces**: A phased delivery with explicit gates between phases.

**Key rules/constraints**:
- **Clarify**: Define objective, acceptance criteria, complexity rating, source materials, constraints. Do NOT begin ideation until scope is locked.
- **Ideate**: Run dreamer-skeptic brainstorms (3 teams), then synthesize into unified architecture. Do NOT begin building until architecture is approved.
- **Design**: Run three-team review, validation brainstorms, council punch list. Resolve all blocking conditions.
- **Build**: Build slides per the agreed plan, one refinement loop per slide. Do NOT iterate indefinitely.
- **Review**: Final flow cohesion review, balance audit, presenter guide.
- The most critical gate: between Ideate and Build. Building before brainstorming is complete was the single largest source of rework.

**Example**: V1 started building early (during clarify phase, before ideate completed). This led to slides that had to be substantially reworked when the narrative direction changed. V2 enforced the gate: "Unified narrative document produced and approved before slide building begins" was acceptance criterion #9.

---

## 2. TOP 10 CONTENT SKILLS

### Skill 1: Mechanism Before Outcome

**When to use**: Every slide that makes a claim about results or capabilities.

**What it produces**: Slides where the audience understands HOW something works before being told WHAT it delivers.

**Key rules/constraints**:
- Show the mechanism first, then state the outcome
- "Proof not pitch": every aspirational claim immediately followed by a concrete mechanism
- Name the specific components, not just the category
- If a concept is named but not explained, it is a label, not a capability

**Example**: V1 slide 10 (Scoring Engine) showed 4 scoring dimensions, routing logic, and the dashboard BEFORE stating the 25% YoY savings claim. The council punch list caught when v3 reversed this: "V1 built mechanism first, then asserted outcomes. V3 reversed this." V3 had 5 of 6 core concepts rated ASPIRATIONAL because they were named but not explained.

---

### Skill 2: Two-Layer Proof Slides

**When to use**: Every slide that claims domain knowledge or operational capability.

**What it produces**: Slides with both an operational scenario (domain context) AND execution evidence (artifact/metric).

**Key rules/constraints**:
- Layer 1: The operational scenario — what happens at 2am, what the engineer experiences, what the [network-event] event looks like
- Layer 2: The execution evidence — the specific artifact, metric, decision log, or audit trail
- You cannot have one without the other
- The scenario makes it feel real; the evidence makes it defensible

**Example**: V2 slide 08 (Pillar 1: Know Portfolio) used the "2:47am scenario" (Layer 1: [System-A] degradation, criticality correctly identified) combined with scored governance output with rationale and override decision (Layer 2: mechanism + metric). The Operators team established: "Every proof slide has two layers: operational scenario + execution evidence. You cannot have one without the other."

---

### Skill 3: Fee-at-Risk Drumbeat Threading

**When to use**: Any proposal with a commercial differentiator that needs to build throughout the deck.

**What it produces**: A single commercial concept that builds from plant to mechanics to culmination across the full deck, never appearing as a one-time mention.

**Key rules/constraints**:
- **Plant** (Act 1): State the commitment as a headline. Create the question. Do not elaborate.
- **Build** (Act 2): Brief callback per section ("This pillar's KPI: [metric]")
- **Mechanics** (Act 3): Full reveal — triggers, non-triggers, measurement methodology, quarterly cadence
- **Culminate** (Act 4/5): Resolution — "What happens if we're wrong?" as the emotional peak
- Must appear in at least 5 slides, never more than 3 slides apart
- The LONGEST gap without a mention should not exceed 15 minutes of presentation time

**Example**: V2's threading: Slide 3 PLANT ([total-value]/[fee-value] exposure) -> Slides 8-11 each pillar callbacks -> Slide 12 FULL MECHANICS -> Slide 13 AI connection -> Slide 20 culmination -> Slide 21 resolution -> Slide 22 invitation. Team B caught that slides 10-18 (15 min) had no fee reference — fixed by adding a bridge sentence to slide 13.

---

### Skill 4: The "Hallway Line" Pattern

**When to use**: At the close of the methodology/architecture section (typically end of Act 2).

**What it produces**: A single sentence that is surprising, teaches immediately, differentiates, and is short enough to repeat in a hallway conversation.

**Key rules/constraints**:
- Must be 10-15 words maximum
- Must be surprising (not a restatement of what they already believe)
- Must teach something (not just inspire)
- Must differentiate (a competitor cannot say the same thing)
- Test: "Would a committee member repeat this sentence in their debrief?"

**Example**: "Don't give an agent a task. Give it a world to work in." — Marketing/Messaging brainstorm (17). The team also generated: "Your engineers aren't the bottleneck. Your ability to give AI the right context is." Both satisfy the criteria: surprising, teaching, differentiating, repeatable.

---

### Skill 5: Protagonist Arc (Open and Close)

**When to use**: When the deck opens with a human scenario or provocation.

**What it produces**: An emotional arc that begins with a human moment and returns to it in the close, transformed.

**Key rules/constraints**:
- Open with a specific human scenario (not an abstraction)
- The protagonist (the engineer at 2am, the PM on the phone) must be revisited at the close
- The close shows what changes for THEM, not just for the organization
- If you open with a person, you must close with that person — abandoning the protagonist is the biggest missed opportunity

**Example**: V1 opened with "The last time [System-A] triggered a P1 at 2am, someone in this room was on the phone for six hours." Marketing brainstorm (17) caught: "The P1 story opens the deck and is never closed. That engineer at 2am — what happens to them? Act 5 should return: 'That engineer at 2am. This is what changes for them.' The deck has a protagonist it abandons."

---

### Skill 6: Proof Not Pitch Principle

**When to use**: As the governing principle for every slide in the deck.

**What it produces**: Slides that earn credibility instead of asserting it.

**Key rules/constraints**:
- "Incumbents with real data don't pitch transformation. They demonstrate it." (Team 1 verdict)
- Every performance claim must specify which governance tier it applies to — no averages across all 323
- Every AI claim must have a [CLIENT]-specific example (not "AI reviews code" but "Our agents review code changes to YOUR provisioning system")
- Named systems, not categories. [System-A], CONNECT, [System-C] — not "mission-critical applications"
- Named metrics, not ranges. If you must use a range, provide base/expected/upside — not just the range

**Example**: V1 slide 3 was rated "moat slide" — it named 31 platforms, 9 personas with headcount, 11 elimination candidates, specific programs (Cheetah, FIM-to-3GIS, Visible). The validation brainstorm caught when v3 weakened this: "NorthStar authorship is buried in a legal caveat. 'We built this assessment' is not stated."

---

### Skill 7: Client Specificity Test

**When to use**: Review every slide against this test before the deck ships.

**What it produces**: Slides that could not be reused for another client without substantial changes.

**Key rules/constraints**:
- "Every slide that does not have an app name, a dollar figure, or a named metric should be considered incomplete"
- Acts 1-2 are most vulnerable to genericness — they need the same named-system medicine as Acts 3-4
- Test: "Could a competitor reading this slide list for Acts 1-2 distinguish this from a capable-but-generic AI delivery proposal?"
- Must name the client's AI ecosystem (e.g., "Vertex AI and Gemini native — we work in your stack")
- Must name operational history with specific programs

**Example**: Validation 4 ("Know Them") found that Acts 1-2 named [System-A] but missed CONNECT, Omega, NTAS, vRepair. Operational history (Cheetah, FIM-3GIS, Visible) was absent. The client's leadership (Villanueva, Tenorio) was absent from discussion questions. GCP/Vertex ecosystem had no slide reference. Fix: 3 non-negotiable additions and 5 additional slide edits.

---

### Skill 8: Redundancy Cluster Detection

**When to use**: After the deck reaches 80%+ completion, before final review.

**What it produces**: Identification of 3-5 slide clusters that repeat the same claim, with specific cut/merge recommendations.

**Key rules/constraints**:
- A redundancy cluster = 3+ slides making the same core claim
- Common clusters: "we know your portfolio," "we understand urgency," "trust us"
- Each cluster should be reduced to 1-2 slides maximum
- The freed positions should be used for missing solution mechanism slides
- Redundancy is the #1 sign that the deck was built sequentially without stepping back to review holistically

**Example**: Balance audit (15) found 4 clusters in v3: "We know your portfolio" (slides 4, 18, 24 — three slides, one claim), "We understand urgency" (slides 2, 3, 5 — three slides, two would suffice), "Five pillars" (slide 7 names them, 18-22 name them again individually), "Trust us" (slides 34, 36, 37, 39 — four slides). Cutting 6 redundant slides and replacing with 6 mechanism slides shifted the ratio from 55/30 to 30/37.

---

### Skill 9: [union-agreement]-Safe Language Audit

**When to use**: For any deck involving workforce transformation at a unionized client.

**What it produces**: A slide-by-slide audit identifying trigger words and replacement language.

**Key rules/constraints**:
- NEVER say: leaner teams, fewer people, headcount reduction, labor savings, offshore substitution, right-sizing
- ALWAYS say: workforce effectiveness, team throughput, capacity for sophisticated work, engineer productivity, expanded capability, delivery model evolution
- "Role Transformation" is a [union-agreement] trigger — use "Expanded Capability Model"
- Capacity data (847/724/123/8) must be labeled as capacity redeployment, not headcount
- [union-agreement]-impacted workflows must be explicitly routed to full-board review
- Workforce slide must feel affirmative, not defensive

**Example**: Review Team C (08) flagged 5 slides for [union-agreement] sensitivity: slide 18 ("Role Transformation" renamed), slide 37 (data labeling), C2 appendix (framing), slide 7 ("right-sizing" check), slide 10 ("Agile-era" replacement). The workforce framing principle: "AI handles volume, repetition, and low-judgment triage. Humans handle complexity, judgment, and high-stakes decisions."

---

### Skill 10: Speaker Notes with RFP Mapping

**When to use**: Every slide in an RFP-response deck.

**What it produces**: Speaker notes that enable an unprepared presenter to deliver confidently, with explicit RFP traceability.

**Key rules/constraints**:
- Three sections per slide's notes: `notes` (delivery instructions), `rfp` (array of section citations with exact quotes), `talking_points` (substantive points, not bullet restatements)
- Notes must NOT simply restate slide text — they provide delivery guidance ("Make eye contact before speaking. Read the quote slowly. Let two full seconds of silence land.")
- RFP citations must include section name and exact quote from the RFP
- Talking points must include "anticipate the objection" framing ("If challenged on the [revenue-figure] figure: 'Source is [CLIENT]'s published IT spend disclosures...'")
- A slide-to-RFP mapping summary should exist on the final slide or as a notes appendix

**Example**: V1 slide 1 notes included: delivery instructions ("Pause after 'that's the last time.' Let two full seconds of silence land"), 6 RFP citations with exact section quotes, 6 talking points including objection handlers. The format was codified in `notes-data.js` as a structured JSON object.

---

## 3. TOP 5 ANTI-PATTERNS

### Anti-Pattern 1: Building Before Brainstorming Is Complete

**What happened**: V1 started building slides during the clarify phase, before ideation was complete. Slides were built against a narrative that later shifted, requiring substantial rework.

**Cost**: Slides had to be rewritten when the narrative direction changed. The "Proof not Pitch" principle emerged mid-build, invalidating slides that led with outcomes instead of mechanisms.

**Prevention**: Enforce the gate between Ideate and Build. V2 acceptance criteria explicitly required: "Unified narrative document produced and approved before slide building begins." The synthesized architecture must be approved by all three review teams before any production starts.

**Reusable rule**: "No slide should exist before its purpose in the narrative is agreed. Building early feels productive. Reworking late is expensive."

---

### Anti-Pattern 2: Naming Concepts Without Showing Mechanisms

**What happened**: V3 expanded from 20 to 41 slides, adding many concept slides that named capabilities (Scored Governance, Knowledge Layer, IQ Accelerators) without showing how they work. The deck became a taxonomy, not a demonstration.

**Cost**: The council punch list found that 5 of 6 core concepts in slides 19-24 were ASPIRATIONAL — named correctly, explained insufficiently. "A competitor who copies the names and adds the mechanisms will outscore this deck on technical evaluation criteria."

**Prevention**: Apply the "Making It Real" validation lens. Rate every concept as CONCRETE / PARTIAL / ASPIRATIONAL / MISSING. Target: 70%+ concepts at CONCRETE or PARTIAL. Any concept rated ASPIRATIONAL in the main deck is a blocking gap.

**Reusable rule**: "A concept that is named but not explained is a label, not a capability. V1 had 5 consecutive mechanism slides (25% of 20 slides). V3 had ~4 mechanism slides in 40 (10% density). Target: 30-37% mechanism density."

---

### Anti-Pattern 3: Over-Indexing on Client Proof vs. Solution Explanation

**What happened**: V3 allocated 55% of slides to client proof and only 30% to solution explanation. The balance audit found: "A brochure that proves we did homework does not prove we have a working system."

**Cost**: Seven solution concepts had zero slides (Scoring Engine, Predictive Quality Engine, Self-Healing Pipeline, Security Automation, Compliance Stage Gates, Code Graph architecture, Agentic authority boundaries). A technically sophisticated evaluator would find the deck unscoreable on methodology criteria.

**Prevention**: Run the balance audit (Skill 6 above) at 80% completion. Target ratio: 30% proof / 40% solution / 30% both. If proof exceeds 40%, identify redundancy clusters and replace with mechanism slides.

**Reusable rule**: "V1 pattern: mechanism before outcome. V3 inverted this. The inversion felt like more work (more slides, more client specificity) but produced less evaluatability."

---

### Anti-Pattern 4: Slide Sprawl Through Additive Expansion

**What happened**: V1 had 20 slides. V2 had 22. V3 exploded to 41 main + 51 appendix = 92 total. Each brainstorm round added slides without removing enough. The council added a Frontier slide (N4), Override Rate appendix (E11), and additional appendix sections — pushing total to 92.

**Cost**: The flow cohesion review rated the deck 6.5/10. Act 2 became "9 slides of philosophy." Act 3 became "a catalog." By Act 4 (the most compelling content), audience attention was depleted. Marketing brainstorm: "Acts 2 and 3 are overweight."

**Prevention**: Set a hard cap early and enforce it. V2 acceptance criteria specified 26-32 slides. When expansion is proposed, require a corresponding cut. The balance audit's "cut 6, add 6" approach maintained the count while improving the ratio.

**Reusable rule**: "Quality over compression — if a concept needs two slides to land cleanly it gets two slides. But if the deck exceeds 30 main slides, every addition must justify a removal."

---

### Anti-Pattern 5: Generic Content That Could Be Any Vendor

**What happened**: Several slides in Acts 1-2 of v3 read as generic AI delivery positioning that any vendor could present. The validation brainstorm found: "A competitor reading the slide list for Acts 1-2 could not distinguish this from a capable-but-generic AI delivery proposal."

**Cost**: The deck's strongest competitive asset — incumbent advantage — was implied rather than stated. "There is no handover. We operate [System-A] today." appeared nowhere in plain language. Operational history (Cheetah, FIM-3GIS, Visible) was absent. The client's AI ecosystem (GCP/Vertex/Gemini) had no slide reference.

**Prevention**: Apply the Client Specificity Test (Content Skill 7) to every slide. The test: "Every slide that does not have an app name, a dollar figure, or a named metric should be considered incomplete." Acts 1-2 need the same level of specificity as Acts 3-4.

**Reusable rule**: "The win themes document established: 'The Old Framing (Cold Vendor): We have a great model. The New Framing (Incumbent Evolving): We already operate 100+ of your golden source systems.' Every slide must pass the incumbent test."

---

## 4. PERSONA FRAMEWORK

### The 12-Persona System

The project defined 12 stakeholder personas covering the full evaluation committee. Each persona was characterized by:
- **Role** (title and function)
- **Primary Concern** (what they evaluate on)
- **Biggest Fear** (what causes a NO vote)
- **How We Win** (the specific argument or artifact that satisfies them)

### Persona Map (from V1 clarify phase)

| # | Persona | Role | Biggest Fear | How We Win |
|---|---------|------|-------------|------------|
| 1 | Network Continuity Owner | VP Network Systems Engineering | AI accelerates delivery of the wrong thing | Network-domain-specific SDLC gates |
| 2 | Cost Transformation Sponsor | SVP Finance / CFO Proxy | Savings are year-3 only, hidden change orders | Financial bridge doc with quarterly savings |
| 3 | Strategic Sourcing Architect | Sr Dir Strategic Sourcing | Recommending the wrong vendor | Tangible IP artifacts, named reference |
| 4 | Incumbent Relationship Manager | VP Vendor Management | Chaotic handover, delivery gaps | Structured transition playbook |
| 5 | Principal Engineer in Trenches | Principal Engineer / Eng Director | AI-generated noise, inherited tech debt | Working session with real artifacts |
| 6 | CISO / Carrier Compliance | CISO / VP Cybersecurity | Data egress, regulatory exposure from AI | Full AI security architecture |
| 7 | Workforce Strategy Director | VP HR / Workforce Strategy | "[CLIENT] cuts jobs via AI" headline | Contractual retraining program |
| 8 | App Rationalization Skeptic | VP Enterprise Architecture | Retiring apps with hidden dependencies | Discovery-first methodology |
| 9 | Business Unit Sponsor | SVP Network Operations | Another multi-year consulting engagement | "Day 90" narrative with specific outcome |
| 10 | Board-Level Risk Lens | CRO / Board Audit Committee | AI incident without due diligence | AI risk allocation framework |
| 11 | Internal IT Champion | CIO / SVP Technology Delivery | Program fails = career risk | Co-designed governance |
| 12 | Existing Vendor Insider | Incumbent program director | Losing the account | Pre-answer their objections |

### Three Make-or-Break Evaluation Criteria

1. **Security gate (CISO)** — binary pass/fail, must be addressed first
2. **Financial model specificity (CFO Proxy)** — contractual savings with clawback
3. **Domain credibility (Network Continuity Owner)** — telecom-native, not generic

### How Personas Were Used

**In Brainstorming**: Dreamer-skeptic pairs drawn from persona map. Each pair represented a real committee dynamic (visionary CIO vs. skeptical VP EA; operational VP Eng vs. demanding Principal Eng; CFO proxy vs. procurement skeptic).

**In Review**: Per-persona review criteria with pass/fail conditions, must-hit slides, and hardest questions (see Persona Review Framework). Each slide validated against 3 primary persona targets; full deck validated against all 12.

**In Validation**: Four validation lenses each adopted a persona blend — the "Know Them" validation adopted the most skeptical personas (Principal Engineer, Frontier PM) to stress-test specificity.

**In Council**: The council punch list explicitly called out RED personas (Frontier PM with zero coverage) and used persona satisfaction as the pass/fail criterion.

### Which Personas Were Most Useful

**Tier 1 (drove the most material changes)**:
- **CIO (P11)**: Drove the "CIO photographs this" standard for key slides (slide 7, slide 33). The hardest question forced fee-at-risk mechanics to be concrete.
- **Principal Engineer (P5)**: Drove the "two-layer proof" pattern and the "mechanism before outcome" principle. Forced every claim to have operational evidence.
- **Frontier Integration PM (P7)**: Was rated RED in both V1 and V3, forcing addition of a dedicated Frontier slide. The fail condition ("'We will assess in Phase 1' = DISQUALIFYING") eliminated discovery-as-strategy language.
- **SVP Finance (P2)**: Drove the fee-at-risk drumbeat threading pattern and the savings bridge methodology.

**Tier 2 (drove specific critical fixes)**:
- **CISO (P6)**: Binary pass/fail gate that forced [regulatory-data], Model Cards, and architecture-agnostic hosting treatment.
- **VP HR (P7/P9)**: Forced the [union-agreement]-safe language audit and "Expanded Capability Model" reframing.

**Tier 3 (provided useful validation but fewer changes)**:
- The remaining 6 personas validated existing content rather than driving structural changes. Board Audit, Procurement, Enterprise Sales, OSS/BSS Engineering, CTO Network, and Incumbent Vendor personas confirmed adequacy or flagged incremental improvements.

### Dreamer-Skeptic Pairing Outcomes

The dreamer-skeptic pairing produced three distinct and non-redundant outputs:

1. **Visionaries (CIO + VP EA)**: Produced the narrative arc and the "proof not pitch" governing principle. The VP EA skeptic prevented the CIO's vision from becoming aspirational — forcing every claim to have a named mechanism.

2. **Operators (VP Network Eng + Principal Eng)**: Produced the proof slide requirements and the two-layer proof pattern. The Principal Engineer skeptic forced operational specificity — no averages across all 323 apps, show variance at the tail.

3. **Commercials (SVP Finance + Sr Dir Sourcing)**: Produced the fee-at-risk threading pattern and the discussion questions. The Sourcing skeptic prevented the CFO's commercial structure from being unenforceable — forcing KPI definitions, cure periods, and measurement methodology.

The pairing worked because the skeptic in each pair represented the persona most likely to vote NO, while the dreamer represented the persona most likely to champion the proposal. The tension between them produced content that satisfied both.

---

## 5. TECHNICAL RECIPES

### Recipe 1: HTML Slide Template Structure

**Pattern**: Each slide is a standalone HTML file that links to shared `styles.css` and `nav.js`.

```
slide-XX.html structure:
- DOCTYPE html
- <head>: charset, viewport width=1280, title, link to styles.css
- <body class="standalone">
  - <div class="slide" style="width:1280px;height:720px">
    - <div class="red-bar"></div> (4px top accent)
    - <div class="slide-header"> (section label + slide number)
    - <div> (main content area, flex column, centered)
  - <nav class="slide-nav"> (prev/next links)
  - <script src="notes-data.js">
  - <script src="nav.js">
```

**Key CSS variables** (from styles.css):
- `--vz-red: #D52B1E` (primary accent)
- `--vz-bg: #0A0A0A` (dark background)
- `--vz-bg-card: #141414` (card background)
- `--vz-bg-elevated: #1A1A1A` (elevated surface)
- `--slide-width: 1280px; --slide-height: 720px`
- Font stack: `'Helvetica Neue', Helvetica, Arial, sans-serif`

**Index navigator**: A grid of clickable cards (4 columns) with act dividers, color-coded for mechanism slides (green left border) and turning points (red background tint).

### Recipe 2: notes-data.js Format

```javascript
window.SLIDE_NOTES = {
  "1": {
    "notes": "Delivery instructions for the presenter...",
    "rfp": [
      "Section: [Name] -- '[exact RFP quote]'",
      ...
    ],
    "talking_points": [
      "Substantive point with objection handler...",
      ...
    ]
  },
  "2": { ... }
};
```

Each slide key is a string number. Three fields: `notes` (delivery instructions), `rfp` (array of section citations), `talking_points` (array of substantive points). The nav.js reads this and renders a notes panel toggled by pressing N.

### Recipe 3: Bundled Single-File HTML

**Purpose**: Create a self-contained HTML file for email distribution / offline viewing.

**Method**: Inline all CSS, all slide HTML, all JavaScript into a single file. The bundled file includes:
- All CSS from styles.css inlined in a `<style>` block
- All slide content as sequential divs (or fetched via JS)
- Navigation JS inlined
- Notes data inlined

**Files observed**:
- `[CLIENT]-deck-v3-bundled.html` (360KB — all slides + nav + notes)
- `[CLIENT]-deck-v3-complete.html` (329KB — similar, different bundling)
- `[CLIENT]-deck-v3-print.html` (292KB — print-optimized version)

### Recipe 4: PDF Generation via Chrome Headless

**Pattern**: Generate PDF from the print-optimized HTML using Chrome's headless mode.

**Output**: `[CLIENT]-deck-v3.pdf` (2.8MB for 41 slides)

**Key consideration**: The print HTML variant strips navigation, notes panels, and interactive elements. Slides are laid out as sequential pages at 1280x720 with page breaks.

### Recipe 5: PPTX Conversion

**Observed**: `[CLIENT]-ns-v3.pptx` exists (197KB) alongside the HTML deck.

**What failed**: The PPTX is significantly smaller than the HTML (197KB vs 2.8MB PDF), suggesting it is a simplified/lossy conversion. Complex CSS layouts (flex, grid, CSS variables, gradients, card borders) do not translate cleanly to PowerPoint's layout model. The HTML-first approach means PPTX is always a degraded derivative, not a peer output.

**Recommendation**: Treat PPTX as a "handout format" — simplified layouts, larger text, fewer visual flourishes. Do not attempt pixel-perfect HTML-to-PPTX conversion. Instead, build a separate PPTX template that captures the key content with PowerPoint-native layouts.

### Recipe 6: Design Rules That Emerged

From the actual slide HTML and the review process:

1. **Vertical centering**: Main content uses `display:flex; flex-direction:column; justify-content:center` — never top-aligned
2. **No flex:1 on cards**: Cards use `width:0; flex-grow:1` instead of `flex:1` to avoid overflow issues
3. **Card pattern**: `background: var(--vz-bg-card); border: 1px solid var(--vz-border); border-radius: 8px; padding: 16px 18px`
4. **Highlighted cards**: Red-tinted with `background: rgba(213,43,30,0.06); border: 2px solid rgba(213,43,30,0.35)`
5. **Sub-items in cards**: `background: var(--vz-bg-elevated); border-radius: 6px; padding: 8px 12px`
6. **Badge pattern**: `.badge-red`, `.badge-green`, `.badge-gold` for metric callouts
7. **Section header**: 11px uppercase with 2px letter-spacing in `var(--vz-gray-300)`
8. **Slide number**: 11px in `var(--vz-red)` with `font-weight: 700`
9. **Content padding**: `padding: 24px 48px 20px` for main content area
10. **Divider**: `.divider` class with `width: 120px; margin: 20px auto`

### Recipe 7: Deep-Dive Deck Organization

**Structure**: 11 topic-specific deck directories under `~/Projects/presentations/decks/`, each containing:
- `index.html` (navigator)
- `styles.css` (shared theme)
- Individual slide HTML files
- Some have `notes-data.js`

**Topics observed**: architecture, business-transformation, compliance, delivery-transformation, dev, devsecops, paclife-transformation, product, qe, security, stage-0

**Usage pattern**: These deep-dive decks served as a "content library" that the mega-deck brainstorms pulled from. Brainstorm 15 (balance audit) proposed pulling specific slides from `devsecops/slides 7-8, 12-13` (Self-Healing Pipeline, Predictive Quality Engine), `compliance/slides 3, 7, 26, 27` (Governance), `security/slides 5-6` (Defense in Depth), and `architecture/slides 9, 10, 11, 28` (Knowledge Layer internals).

**Key insight**: Building topic-specific deep-dive decks FIRST, then composing the client-facing deck from them, is the correct order. The deep-dive decks are the "mechanism library." The client deck is the "narrative wrapper" that selects and sequences mechanisms for a specific audience.

---

## SUMMARY: The Master Pattern

The [CLIENT] deck project revealed a clear meta-pattern:

**What worked**: Structured brainstorming with persona-driven tension (dreamer/skeptic pairs), multi-team review with distinct lenses (narrative/commercial/technical), validation brainstorms with specific questions (POV clarity / RFP coverage / making it real / know them), council punch list as final gate, and explicit balance audits.

**What failed**: Building before brainstorming was complete, naming concepts without showing mechanisms, over-indexing on client proof at the expense of solution explanation, slide sprawl through additive expansion, and generic content that could apply to any vendor.

**The governing principle**: "Proof not pitch." Every claim earns its right to exist through a concrete mechanism. The mechanism is shown before the outcome is stated. The client's own systems, data, and language are the proof — not generic frameworks or aspirational positioning.

**The workflow sequence**: Clarify (scope + personas + constraints) -> Ideate (3 dreamer-skeptic teams -> synthesized architecture) -> Review (3-team conditional approve -> 4 validation lenses -> council punch list) -> Build (per agreed plan, one refinement loop per slide) -> Polish (balance audit + flow cohesion + presenter guide).

**The critical gate**: Between Ideate and Build. The single largest source of rework was building before the narrative was locked. Every hour invested in brainstorming before building saved 3-5 hours of rework during building.

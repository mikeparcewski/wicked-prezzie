# Validation Lenses

Four complementary perspectives applied in parallel during the validate phase.
Each lens is dispatched as a separate agent and produces a rated gap list with
slide-level fix instructions.

## Dispatch Protocol

Run all four lenses in parallel. Do not wait for one to complete before
starting another. After all four complete, dispatch a council-reviewer agent
to synthesize findings into a final punch list.

```
validation-lens-1 (POV Clarity)    ─┐
validation-lens-2 (RFP Coverage)    ├─→ council-reviewer → punch list
validation-lens-3 (Making It Real)  │
validation-lens-4 (Know Them)      ─┘
```

---

## Lens 1: POV Clarity

**Question**: Are mechanisms visible, not just named?

**What to check**:
- Every named concept (capability, system, methodology) must show HOW it works
- A concept that is named but not explained is a label, not a capability
- Look for slides that title a capability and then list sub-capabilities without
  explaining any of them
- Mechanism density target: 30-37% of slides should be mechanism slides

**Check for each concept**:
1. Is the concept named? (necessary but not sufficient)
2. Is the mechanism shown — components, routing logic, decision steps?
3. Is the outcome stated AFTER the mechanism, not before it?

**Rating scale**:
- MECHANISM — the slide shows how it works
- NAMED — the concept is named but not explained
- ABSENT — the concept is referenced elsewhere but has no dedicated slide

**Output format**:
```
Slide 12 — NAMED: "Scored Governance" names 4 tiers but shows no scoring logic.
  Fix: Add a flow diagram showing how the score is computed. Show inputs → formula → output tier.
  Blocking: YES — technical evaluators cannot score this criterion.

Slide 15 — MECHANISM: Scoring Engine shows dimensions, routing, dashboard. PASS.
```

---

## Lens 2: RFP Coverage

**Question**: Does every RFP requirement have a slide?

**What to check**:
- Read the RFP (or requirements source) before running this lens
- Map every explicit requirement to one or more slides
- Flag requirements with no coverage (MISSING) or weak coverage (MENTIONED ONLY)
- Pay special attention to: metrics, SLAs, technical requirements, compliance
  mandates, and evaluation criteria

**Check for each requirement**:
1. Is there at least one slide dedicated to this requirement?
2. Does the slide address the requirement with specificity (named metrics, named
   systems, concrete commitments)?
3. Are SLAs and contractual commitments stated explicitly?

**Rating scale**:
- COVERED — dedicated slide with specific treatment
- MENTIONED — referenced in passing, not addressed
- MISSING — no slide addresses this requirement

**Output format**:
```
RFP Section 4.2 (Security Architecture) — MISSING
  No slide addresses regulatory compliance handling, data residency, or model cards.
  Fix: Add security architecture slide covering regulatory compliance, residency policy, Model Card.
  Blocking: YES — security evaluator is binary pass/fail.

RFP Section 3.1 (Transition Plan) — COVERED: Slide 22. PASS.
```

---

## Lens 3: Making It Real

**Question**: Are concepts concrete or aspirational?

**What to check**:
- Rate each major concept on the CONCRETE/PARTIAL/ASPIRATIONAL/MISSING scale
- Target: 70%+ of concepts at CONCRETE or PARTIAL
- Any concept rated ASPIRATIONAL in the main deck is a blocking gap
- A competitor who names the same concepts and adds mechanisms will outscore
  this deck on technical evaluation

**Rating definitions**:
- **CONCRETE**: Named mechanism + specific metric + named system. Fully defensible.
- **PARTIAL**: Named mechanism + either metric or named system, but not both.
- **ASPIRATIONAL**: Named correctly, explained insufficiently. Could be said by any vendor.
- **MISSING**: Concept referenced in outline or RFP but absent from deck.

**Test for each concept**:
1. Does it name the specific system or component (not a category)?
2. Does it include a specific metric, figure, or named output?
3. Does it show the mechanism (how it works)?

**Output format**:
```
Concept: Knowledge Layer — ASPIRATIONAL
  Named on slide 19, referenced on slides 7 and 23. No slide shows the architecture,
  data sources, or retrieval mechanism. Any vendor can claim "knowledge layer."
  Fix: Slide 19 must show: data sources → ingestion → graph structure → retrieval → output.
  Blocking: YES — 5 of 6 core concepts rated ASPIRATIONAL = unscoreable on methodology.

Concept: Scoring Engine — CONCRETE: Slide 15. PASS.
```

---

## Lens 4: Know Them

**Question**: Does the deck demonstrate deep client knowledge?

**What to check**:
- Named systems (not categories): named client systems — not "mission-critical applications"
- Operational history with specific programs and dates
- Client's AI/technology ecosystem (named platforms, not generic)
- Leadership awareness: named individuals, their stated priorities, their hardest questions
- Client specificity test: "Could a competitor present this slide for a different client?"

**Check for each slide in Acts 1-2** (most vulnerable to genericness):
1. Does it contain a named system, a dollar figure, or a named metric specific to this client?
2. Does it reference the client's specific technology stack?
3. Could it be reused for another client without changes? If yes — incomplete.

**Rating scale**:
- SPECIFIC — client-specific systems, figures, or named history
- GENERIC — could apply to any enterprise client in this industry
- ABSENT — a client system or program that should be referenced has no mention

**Output format**:
```
Slide 5 — GENERIC: Names AI transformation benefits but no client systems.
  Missing: named client systems, cloud/AI ecosystem references.
  Fix: Replace "mission-critical applications" with the client's specific system names.
       Add: reference to the client's specific cloud/AI platform stack.
  Blocking: NO — but Acts 1-2 collectively feel like a generic proposal.

Slide 3 — SPECIFIC: Names 31 platforms, 9 personas, 11 elimination candidates. PASS.
```

---

## Output Format (All Lenses)

Each lens produces:

1. **Rated gap list** — every concept/requirement/slide rated on the lens scale
2. **Slide-level fix instructions** — exact fix per gap (slide number, what to add/change)
3. **Blocking classification** — YES (must fix before deck ships) or NO (recommended)
4. **Summary counts** — how many PASS, how many gaps, how many blocking

## Blocking Criteria

A gap is **blocking** if:
- It is a binary evaluator requirement (security evaluator security, financial specificity)
- The deck cannot be scored on a technical criterion because the mechanism is absent
- An entire act fails the client specificity test
- The concept density is below 70% CONCRETE/PARTIAL

A gap is **recommended** if:
- The content is present but could be strengthened
- It improves competitive differentiation but is not a scoring criterion
- It addresses a Tier 2-3 persona concern

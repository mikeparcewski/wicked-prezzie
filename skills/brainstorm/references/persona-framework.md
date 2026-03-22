# Persona Framework — 12-Archetype Evaluation Committee

Reference for `brainstorm` skill. Documents the persona generation system,
archetype slots, pass/fail criteria structure, dreamer-skeptic pairing, and
tier ranking methodology.

Personas are **generated per deck** from the outline's `target_audience`, industry,
and topic — not hardcoded. The 12 archetypes below are slots to fill, not fixed roles.

---

## How Persona Generation Works

1. Read the outline's `target_audience`, `key_message`, and section structure
2. Identify the **decision context**: who approves this? who can kill it? who implements it?
3. Fill the 12 archetype slots with roles appropriate to the context
4. Generate pass/fail criteria from the deck's claims and the persona's lens
5. Assign dreamer-skeptic pairs based on productive tension

The model generates personas — the framework provides the structure.

---

## 12 Archetype Slots

Each archetype represents a **perspective in the room**, not a specific job title.
The same archetype manifests differently depending on the audience.

| # | Archetype | Perspective | Example: Tech Startup | Example: Enterprise RFP | Example: Board Update |
|---|-----------|-------------|----------------------|------------------------|----------------------|
| 1 | **Domain Expert** | Deepest technical knowledge in the subject area | Lead Engineer | VP Network Engineering | CTO |
| 2 | **Budget Owner** | Controls or influences the money | CFO / Finance Lead | SVP Finance / CFO Proxy | CFO |
| 3 | **Procurement Gate** | Evaluates vendor/option defensibility | Head of Partnerships | Sr Dir Strategic Sourcing | General Counsel |
| 4 | **Continuity Guardian** | Protects existing operations during change | Ops Manager | VP Vendor Management | COO |
| 5 | **Hands-on Builder** | Will implement or live with the result daily | Senior Developer | Principal Engineer | Engineering Manager |
| 6 | **Risk/Compliance** | Binary pass/fail on security, legal, regulatory | Security Lead | CISO / VP Cybersecurity | Chief Risk Officer |
| 7 | **People Impact** | Workforce, culture, change management | People Ops Lead | VP HR / Workforce Strategy | CHRO |
| 8 | **Systems Skeptic** | Worries about hidden dependencies and complexity | Staff Engineer | VP Enterprise Architecture | VP Infrastructure |
| 9 | **Impatient Sponsor** | Wants visible results fast, hates long timelines | CEO / Founder | SVP Business Unit | Board Member |
| 10 | **Governance Lens** | Enterprise risk, audit trail, accountability | Advisor / Board Observer | CRO / Board Audit Committee | Audit Committee Chair |
| 11 | **Internal Champion** | Needs the project to succeed for career/org reasons | VP Product | CIO / SVP Technology | Division President |
| 12 | **Contrarian/Incumbent** | Represents the status quo or competing option | Team lead who likes current approach | Incumbent vendor PM | The exec who championed the last initiative |

---

## Generating Personas from Context

### Input Required

From the outline JSON:
- `target_audience` — who is in the room
- `key_message` — the central claim
- Section titles and content themes — what's being argued

From the user (if available):
- Industry / domain
- Decision type (buy, build, fund, approve, inform)
- Known objections or sensitivities

### Generation Prompt Structure

For each archetype slot, generate:

```
Persona: [Name — a descriptive title, not a proper name]
Role: [Job title appropriate to this audience]
Primary Concern: [What they evaluate on — one sentence]
Biggest Fear: [What causes a NO — one sentence]
How We Win: [What satisfies them — one sentence]
Hardest Question: [The question they will ask that we must answer]
```

### Generation Rules

1. **Every persona must be distinct** — no two personas should have the same primary concern
2. **At least 3 personas should be potential NO votes** — if everyone is friendly, the framework isn't useful
3. **The contrarian (slot 12) represents the strongest argument against the proposal** — not a strawman
4. **Personas should reflect the actual room** — if presenting to a 5-person team, map those 5 to archetypes and fill remaining slots with absent-but-influential stakeholders
5. **Industry language matters** — a healthcare compliance persona speaks differently than a fintech one

---

## Pass/Fail Criteria Structure

Each generated persona gets pass/fail criteria:

```
### P[N] — [Persona Name]

**Lens**: [What this persona evaluates — their filter for every slide]

**Pass condition**: [Specific, testable criteria — what makes them say YES]

**Fail condition**: [What makes them say NO — specific language or gaps that trigger rejection]

**Hardest question**: "[The exact question they will ask — in quotes, in their voice]"
```

### Quality Bar for Generated Criteria

- Pass conditions must be **testable against the deck** — not aspirational
- Fail conditions must name **specific language or omissions** — not vague
- Hardest questions must be **in character** — the kind of thing this person actually says
- Every criterion should connect to a specific slide or section in the deck

---

## Three Make-or-Break Gates

Of the 12 personas, identify the **3 binary gates** — personas whose NO kills the proposal
regardless of all other scores. These are typically:

1. **Compliance/Security Gate** (usually Archetype 6) — binary pass/fail, no partial credit
2. **Financial Gate** (usually Archetype 2) — numbers must be specific and auditable
3. **Domain Credibility Gate** (usually Archetype 1) — must demonstrate real expertise, not generic claims

The specific personas filling these gates change per deck. A product launch might have
Customer Safety, Unit Economics, and Technical Feasibility as its three gates.

---

## Dreamer-Skeptic Pairing

### Pairing Rules

| Session Type | Dreamer Archetype | Skeptic Archetype | Productive Tension |
|-------------|-------------------|-------------------|-------------------|
| Narrative/Story | Internal Champion (11) | Systems Skeptic (8) | Vision vs. structural rigor |
| Evidence/Proof | Domain Expert (1) | Hands-on Builder (5) | Scale vs. artifact-level evidence |
| Commercial/Value | Budget Owner (2) | Procurement Gate (3) | Bold position vs. enforceability |
| Validation | Impatient Sponsor (9) | Hands-on Builder (5) | Speed vs. depth |
| Final Review | Internal Champion (11) | Builder (5) + Budget (2) | Multiple skeptics for final gate |

### Why Pairs Work

- **Dreamer** holds the aspiration — what should be true, what would be compelling
- **Skeptic** holds the constraint — what must be provable, what breaks under scrutiny
- The pair's output must **satisfy both** — aspirational claims that are defensible

### Pairs That Fail

- **Two dreamers**: produces compelling claims with no mechanism
- **Two skeptics**: produces a risk register, not a proposal
- **Wrong domain**: pairing a financial dreamer with a technical skeptic tests the wrong dimension

---

## Tier Ranking

After personas are generated and the brainstorm completes, rank personas by impact:

### Tier 1 — Drove Structural Changes
Personas whose feedback changed the deck's architecture, not just individual slides.
These are the personas to satisfy first in a time-constrained project.

### Tier 2 — Drove Critical Fixes
Personas whose feedback fixed specific critical gaps (security architecture, legal
language, financial model) but didn't change the overall structure.

### Tier 3 — Validated and Refined
Personas who confirmed adequacy or suggested incremental improvements.

**Resource allocation**: In a time-constrained project, build for Tier 1 pass conditions
first. Address Tier 2 gates. Polish for Tier 3 last. Never let a Tier 3 preference
override a Tier 1 pass condition.

---

## Persona Usage Across Pipeline Phases

### Phase 1 — Source Inventory
Not yet active. Personas are generated in Phase 2.

### Phase 2 — Persona Generation
Generate the 12-persona committee from the outline context. Identify which
archetypes are present in the actual audience, which are absent-but-influential,
and which three are the make-or-break gates.

### Phase 3 — Brainstorm
Assign personas to dreamer-skeptic pairs. Use primary concern to drive the
dreamer's direction; use biggest fear to drive the skeptic's challenges.

### Phase 4 — Architecture Review
Each review team adopts a persona blend:
- Team A (Narrative): Champion (11) + Sponsor (9)
- Team B (Commercial): Budget (2) + Procurement (3) + Continuity (4)
- Team C (Technical): Builder (5) + Compliance (6) + Skeptic (8)

### Phase 6 — Validate
Run each slide through the relevant persona's pass/fail criteria.
Flag any slide that fails a Tier 1 persona's test.

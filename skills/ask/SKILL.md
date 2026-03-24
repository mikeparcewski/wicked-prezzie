---
name: ask
description: |
  Four-stage Q&A pipeline over indexed documents. Dispatches specialist personas
  to research different angles, then validates and packages the answer.
  Specialist personas adapt to the workflow template being used.

  Use when: "what should we say about", "how do we address", "what's our position on",
  "find the answer to", "what do the sources say about"
---

# ask — Query Sources with Specialist Perspectives

Four-stage pipeline that answers questions by dispatching specialist personas to
research indexed source documents from different angles. Each specialist runs
an independent search with its own scope and evaluation lens. Results are
validated for traceability and packaged into a scannable output format.

Unlike `wicked-prezzie:search` (single-pass lookup), ask runs a full research
pipeline: classify the question, dispatch two specialists in parallel, validate
their findings, then synthesize a packaged answer. Use search when you need raw
chunks. Use ask when you need a defensible, multi-angle answer.

---

## When to Use

- When the user asks a question that requires judgment, not just retrieval.
- When the answer needs to be traced back to source documents.
- When multiple perspectives (audience vs. content creator) would improve the answer.
- When building slide content that makes claims requiring evidence.
- When the user says "what should we say about X" or "how do we address Y".

**Prerequisite**: Source documents must be indexed via `wicked-prezzie:learn`. If no
index exists, warn the user and recommend running learn first.

---

## Four-Stage Pipeline

### Stage 1: Intent Classifier

Runs inline (no subagent). Analyzes the user's question and produces:

1. **Domain classification** — What subject area does this question touch?
   (financial, technical, operational, strategic, organizational, competitive)
2. **Specialist selection** — Which two specialist personas are needed?
   (default: Audience Advocate + Content Lead; overridable per workflow template)
3. **Scoped search queries** — 2-3 targeted queries per specialist, each with
   a scope prefix (`facts:`, `narrative:`, `evidence:`, `context:`)

The classifier reads `deck-state.json` for context: deck type, audience profile,
current phase, and workflow template. If context is unavailable, it uses defaults.

**Output**: Internal routing object (never shown to user).

### Stage 2a: Audience Advocate (Parallel)

**Persona**: Skeptical evaluator. Represents the most critical member of the
target audience. Asks: "Does this answer what the audience actually needs?
Would this survive scrutiny in the room?"

**Search scopes**: `facts` + `context`

**Procedure**:
1. Run the scoped search queries from Stage 1
2. Evaluate each result through the audience lens
3. Identify what the audience would challenge or find insufficient

**Output** (internal, never shown to user):
- **Audience need**: What the audience actually wants to know (may differ from
  what was asked)
- **Potential objection**: The strongest counterargument or gap the audience
  would raise
- **Supporting evidence**: Chunks that directly address the audience need,
  with source attribution

### Stage 2b: Content Lead (Parallel)

**Persona**: Bold content creator. Sees the narrative opportunity in the question.
Asks: "What's the strongest position we can take, and where does it land in the
deck?"

**Search scopes**: `narrative` + `evidence`

**Procedure**:
1. Run the scoped search queries from Stage 1
2. Find the strongest proof points and narrative angles
3. Identify where this content belongs in the deck structure

**Output** (internal, never shown to user):
- **Position**: The strongest defensible answer, stated as an assertion
- **Proof point**: The single best piece of evidence supporting the position
- **Slide location**: Where in the deck this content should appear (if a slide
  plan exists)
- **Open items**: What is missing from the sources that would strengthen the answer

### Stage 3: Reviewer

Runs inline after both specialists complete. Validates the combined output:

| Check | What It Catches |
|-------|----------------|
| **Traceability** | Every claim must trace to a specific chunk ID and source document |
| **Unattributed claims** | Assertions not grounded in source material — flag for user confirmation |
| **Placeholder risk** | Vague language ("significant improvement", "industry-leading") without specific data |
| **Search gaps** | Topics mentioned by specialists but not found in the index — recommend additional searches |
| **Consistency** | Advocate and Lead should not contradict each other on facts (opinions may differ) |

The reviewer does not add content. It flags problems and passes validated
output to Stage 4.

### Stage 4: Facilitator

Packages the validated output into the final user-facing format. This is the
only stage whose output the user sees.

---

## Output Format

```
AUDIENCE NEED
{What the audience actually needs to know — reframed from the original question
if the Advocate identified a deeper need}

OUR ANSWER
{The strongest defensible position, stated as a clear assertion.
Supported by: [source document, chunk ID]}

VALIDATION
{Reviewer assessment: traceability status, any unattributed claims,
placeholder risks flagged}

OPEN ITEMS
{What's missing from sources, what needs user confirmation,
recommended follow-up searches}

SOURCES
- {source 1}: {chunk ID} — {brief excerpt}
- {source 2}: {chunk ID} — {brief excerpt}
```

---

## Workflow

```
User question
    │
    ▼
Stage 1: Intent Classifier (inline)
    │  → domain, specialists, scoped queries
    │
    ├──────────────────┐
    ▼                  ▼
Stage 2a:          Stage 2b:
Audience Advocate  Content Lead
(parallel)         (parallel)
    │                  │
    ├──────────────────┘
    ▼
Stage 3: Reviewer (inline)
    │  → traceability, gaps, consistency
    ▼
Stage 4: Facilitator (inline)
    │  → packaged output
    ▼
User sees: AUDIENCE NEED / OUR ANSWER / VALIDATION / OPEN ITEMS / SOURCES
```

**Critical rule**: Intermediate stage outputs are never shown to the user.
The user sees only the Stage 4 packaged output. If the user asks to see
intermediate work, show it on request — but the default is the clean output.

---

## Specialist Persona Configuration

The default specialists (Audience Advocate + Content Lead) work for most deck
types. Workflow templates can override these with domain-specific personas:

| Template | Specialist A | Specialist B |
|----------|-------------|-------------|
| **general** (default) | Audience Advocate (skeptical evaluator) | Content Lead (bold creator) |
| **rfp-exec** | Evaluation Committee Proxy (scores against rubric) | Solution Architect (technical depth) |

Custom personas follow the same contract: each produces a structured output
with need/objection/evidence (Specialist A) or position/proof/location/gaps
(Specialist B). The Reviewer and Facilitator stages are universal.

To add a custom persona configuration, define it in the workflow template's
phase definitions. The ask skill reads the active template from `deck-state.json`
and loads the corresponding persona pair.

---

## Invocation Examples

```
"What should we say about our uptime track record?"
  → Classifier: technical domain, default specialists
  → Advocate searches facts: uptime metrics, SLA data
  → Lead searches narrative: reliability story, competitive positioning
  → Output: defensible uptime claim with source attribution

"How do we address the cost concern?"
  → Classifier: financial domain, default specialists
  → Advocate searches facts: pricing data, TCO analysis
  → Lead searches evidence: ROI proof points, cost comparisons
  → Output: cost position with evidence and open items

"What do the sources say about their evaluation criteria?"
  → Classifier: strategic domain, rfp-exec specialists if template active
  → Committee Proxy searches context: evaluation matrix, scoring weights
  → Solution Architect searches facts: compliance requirements, technical criteria
  → Output: evaluation framework summary with source mapping
```

---

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| **search** | Ask dispatches search internally for each specialist's queries. Search is the retrieval layer; ask is the analysis layer. |
| **brainstorm** | Teams may invoke ask to answer specific questions during ideation rather than making assumptions. |
| **workflow** | Build agents use ask when populating slides that require defensible claims. |
| **generate** | Slide generation can invoke ask to find the right content for a specific slide's assertion title. |

---

## Limitations

- Four-stage pipeline is heavier than a simple search. For quick lookups, use
  `wicked-prezzie:search` instead.
- Specialist quality depends on index depth. Sparse indexes produce thin answers.
  Check `_manifest.json` chunk count before relying on ask for critical content.
- The Reviewer catches structural issues (traceability, placeholders) but does not
  verify factual accuracy. Source documents are assumed to be authoritative.
- Custom specialist personas require a workflow template definition. Ad-hoc persona
  changes within a session are not persisted.

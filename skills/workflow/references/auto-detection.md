# Auto-Detection — Workflow Template Selection

How the `start` skill automatically detects which workflow template to recommend
based on the user's input and source documents.

---

## Detection Pipeline

```
User input (brief + documents)
  │
  ├─ Check learn indexes (if available)
  │    └─ Scan YAML frontmatter: tags, themes, entities
  │
  ├─ Scan raw documents (fallback if no indexes)
  │    └─ Read first 2-3 pages per document
  │
  └─ Scan user's brief text
       └─ Keyword and pattern matching
  │
  ▼
Signal aggregation → Confidence score → Recommendation
```

### Source Priority

1. **learn indexes** — Preferred. Already structured with YAML frontmatter
   containing tags, document type, key entities, and themes. Fastest to scan and
   most reliable for signal detection. Check the index directory configured in
   `config` (project-level `index_dirs` setting).

2. **Raw document scanning** — Fallback when indexes do not exist. Read the first
   2-3 pages of each document to extract signals. Do not read entire large
   documents — detection is a lightweight operation, not a deep analysis.

3. **User's brief text** — Always scanned regardless of whether documents or
   indexes are available. Even a short sentence can contain strong signals
   ("we need to respond to the RFP by Friday").

---

## Signal Categories

### Keyword Signals

Case-insensitive string matching. Each match counts as one signal point.

| Signal | Weight | Patterns |
|--------|--------|----------|
| RFP identifier | 1.0 | "request for proposal", "RFP", "RFQ", "RFI" |
| Tender identifier | 1.0 | "invitation to tender", "ITT", "tender response" |
| Evaluation language | 0.8 | "evaluation criteria", "scoring rubric", "evaluation matrix", "weighted criteria" |
| Requirement language | 0.8 | "mandatory requirements", "must requirements", "compliance matrix", "mandatory/desirable" |
| Deadline language | 0.6 | "response required by", "submission deadline", "closing date", "lodgement date" |
| Committee language | 0.6 | "evaluation committee", "evaluation panel", "selection committee", "assessment panel" |
| Competitive language | 0.4 | "incumbent", "competitive", "bid", "tender", "proposal response", "shortlisted" |
| Procurement language | 0.4 | "procurement", "sourcing", "vendor selection", "panel arrangement" |

### Structural Signals

Pattern-based detection requiring document structure analysis.

| Signal | Weight | Detection Method |
|--------|--------|-----------------|
| Numbered requirements | 1.0 | Sequences of numbered items with "shall", "must", "will" language |
| Compliance tables | 1.0 | Tables with columns like "Requirement", "Response", "Compliant" |
| Evaluation weightings | 0.8 | Percentage allocations (e.g., "Technical 40%, Price 30%, Experience 30%") |
| Named committee members | 0.6 | Names with roles containing "evaluator", "assessor", "panel member" |
| Formal procurement refs | 0.4 | Reference numbers, contract IDs, procurement system identifiers |

### Audience Signals

Inferred from the nature of the target audience.

| Signal | Weight | Detection Method |
|--------|--------|-----------------|
| Multiple decision-makers | 0.6 | 3+ named individuals with different roles/concerns |
| Formal governance | 0.4 | References to board, committee, panel, council structures |
| Regulatory stakeholders | 0.4 | References to compliance officers, regulators, audit requirements |

### Architecture Signals (→ `architecture`)

Keyword and structural signals indicating a technical architecture presentation.

| Signal | Weight | Patterns |
|--------|--------|----------|
| Architecture identifier | 1.0 | "architecture", "system design", "ADR", "architecture decision record" |
| Migration language | 0.8 | "migration", "migration plan", "cutover", "lift and shift", "re-platform" |
| Infrastructure language | 0.8 | "infrastructure", "microservices", "API", "schema", "database", "deployment" |
| Component language | 0.6 | "component", "service mesh", "event bus", "message queue", "load balancer" |
| Diagram language | 0.4 | "diagram", "sequence diagram", "C4 model", "topology", "data flow" |

### Board Strategy Signals (→ `board-strategy`)

Keyword and structural signals indicating a board or strategic review presentation.

| Signal | Weight | Patterns |
|--------|--------|----------|
| Board identifier | 1.0 | "board", "board meeting", "board deck", "board presentation" |
| Quarterly identifier | 1.0 | "quarterly", "Q1", "Q2", "Q3", "Q4", "QBR", "quarterly review" |
| Investor language | 0.8 | "investor", "investment case", "shareholder", "fundraise", "series" |
| Strategy language | 0.8 | "strategy", "strategic review", "ROI", "revenue", "market", "growth" |
| Financial language | 0.6 | "budget", "forecast", "P&L", "EBITDA", "margin", "ARR", "MRR" |
| Stakeholder language | 0.4 | "stakeholder", "executive team", "C-suite", "leadership team" |

### Training Signals (→ `training`)

Keyword and structural signals indicating a training or enablement presentation.

| Signal | Weight | Patterns |
|--------|--------|----------|
| Training identifier | 1.0 | "training", "onboarding", "enablement", "certification" |
| Workshop identifier | 1.0 | "workshop", "course", "bootcamp", "masterclass" |
| Module language | 0.8 | "module", "lesson", "unit", "chapter", "curriculum" |
| Exercise language | 0.8 | "exercise", "hands-on", "lab", "practice", "drill" |
| Instructional language | 0.6 | "runbook", "how-to", "step-by-step", "walkthrough", "tutorial" |
| Assessment language | 0.4 | "quiz", "assessment", "knowledge check", "competency", "learning objective" |

---

## Confidence Calculation

### Scoring Formula

```
raw_score = sum(signal_weight for each matched signal)
confidence = min(1.0, raw_score / 4.0)
```

The denominator (4.0) is calibrated so that 4 weighted signal points produce
confidence = 1.0. This means:
- 1 RFP keyword alone = 0.25 (low confidence)
- 1 RFP keyword + 1 evaluation keyword = 0.45 (low-medium)
- 2 keywords + 1 structural signal = 0.65 (medium)
- 3 keywords + 1 structural signal = 0.85 (high)

### Confidence Levels

| Level | Range | Behavior |
|-------|-------|----------|
| **High** | >= 0.8 | Present recommendation with confidence. "This looks like an RFP response." |
| **Medium** | 0.5 - 0.8 | Present recommendation but explicitly invite override. "I see proposal language — would you like the RFP template or the general one?" |
| **Low** | < 0.5 | Default to `general`. Mention the alternative only briefly. "I'll use the standard workflow. Let me know if this is actually an RFP response." |

---

## Recommendation Protocol

### What to Present

Every recommendation must include:

1. **Signals found** — List the specific signals detected, with source
   (brief text, document name, or index). Do not just say "I detected RFP
   signals" — name them.

2. **Template recommendation** — Name the template and explain in one sentence
   what it adds or changes compared to the default.

3. **Confidence level** — State whether confidence is high, medium, or low.

4. **Override offer** — Always give the user the option to choose a different
   template. The recommendation is a suggestion, not a decision.

### Presentation Format

```
Signals detected:
  - "request for proposal" in your brief (keyword, weight 1.0)
  - "evaluation criteria" in source-doc-3.pdf (keyword, weight 0.8)
  - Numbered requirements table in source-doc-1.pdf (structural, weight 1.0)

Confidence: high (0.85)

Recommendation: rfp-exec template
This adds an executive summary approval gate between brainstorm and slide
building. You review and approve the strategic summary before any slides
are created.

Proceed with rfp-exec, or use the general template instead?
```

### Edge Cases

**No signals detected**: Default to `general` without extensive explanation.
"I'll use the standard workflow. If you need the proposal template, just say so."

**Mixed signals**: If signals point to different templates, present all matched
options with their signal counts and confidence levels, and let the user choose.
For example, a "board training workshop" could match both `board-strategy` and
`training` — present both with their respective scores.

**User overrides**: Accept immediately. Do not argue or re-present the
recommendation. Record the override in deck-state.json for future reference:
```json
{
  "template": "general",
  "template_auto_detected": "rfp-exec",
  "template_override": true
}
```

---

## Default Behavior

When confidence is low (< 0.5), the system defaults to the `general` template.
This is intentional — the general template is the safe choice. It produces a
complete deck through the standard 8-phase flow. The rfp-exec template adds
process overhead (an extra approval gate) that is only valuable when the content
genuinely requires strategic alignment before slide production.

**Defaulting to general is always safe.** The user can switch to rfp-exec at any
point before the brainstorm phase completes. After brainstorm, switching
templates would require re-running the brainstorm with the exec-summary phase
in mind, which is wasteful.

---

## Detection Timing

Auto-detection runs once, during the `start` skill's template selection step.
It does not run continuously or re-evaluate during the workflow. The template
is locked once the user confirms (or the default is accepted) and recorded in
`deck-state.json`.

If the user realizes mid-workflow that the wrong template was selected:
- Before brainstorm completes: switch templates, no rework needed
- After brainstorm completes: switching to rfp-exec adds the exec-summary phase
  but uses existing brainstorm outputs — manageable
- After architecture completes: switching templates is not recommended — the
  slide plan would need to be rebuilt

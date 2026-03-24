---
name: validation-lenses
description: |
  Pluggable validation framework with universal and template-specific quality lenses.
  Each lens runs as a parallel agent evaluating the deck from a specific angle.
  Produces a consolidated punch list with blocking/recommended findings.

  Use when: "validate the deck", "quality check", "run validation", "check quality",
  "are the slides good", "review for quality", "lens check"
---

# Validation Lenses

Pluggable quality validation framework. Each lens is a focused evaluation agent
that examines the deck from a single angle. Four universal lenses run on every
deck. Additional lenses activate based on the workflow template. All lenses run
in parallel and their findings are merged into a consolidated punch list.

This skill provides the lens definitions and aggregation logic. The structural
checks (bounds, overflow, empty slides) remain in the validate skill. Validation
lenses evaluates content quality and narrative coherence — what the slides say,
not how the shapes are positioned.

---

## When to Use

- After the build phase, before polish
- When the user asks "is the deck good?" or "run quality checks"
- During the validate phase of any workflow template
- When the user wants to check specific quality dimensions

---

## Universal Lenses

These four lenses run on every deck, regardless of template.

### Lens 1: Clarity

**Question**: Is each slide's message immediately clear?

**Checks**:
- Every slide title is an assertion (contains a verb or number), not a topic
  label ("Revenue Update" fails, "Revenue grew 40% YoY" passes)
- Each slide communicates exactly one message (no split attention)
- Jargon is either defined on first use or absent
- Body text supports the title assertion — no tangential content
- Reading order is unambiguous (visual hierarchy guides the eye)

**Output per slide**:
```json
{
  "lens": "clarity",
  "slide_index": 3,
  "status": "fail",
  "finding": "Title is a topic label, not an assertion",
  "current": "Market Overview",
  "suggestion": "Our addressable market grew to $4.2B in 2025",
  "severity": "blocking"
}
```

### Lens 2: Evidence

**Question**: Is every claim backed by verifiable evidence?

**Checks**:
- Statistics have a named source (not "industry data shows")
- Claims are specific (not "significant improvement" but "40% reduction")
- Comparative claims state the baseline ("faster than" — faster than what?)
- No orphaned assertions — every claim slide has supporting data within 2 slides
- Anecdotes are attributed (named person, named situation)

**Output per slide**: Same schema as Clarity, with `"lens": "evidence"`.

### Lens 3: Flow

**Question**: Does the deck progress logically from start to finish?

**Checks**:
- The narrative follows a recognizable pattern (one of the six story-arc patterns
  or a clear custom structure)
- No orphan slides (slides that do not connect to what comes before or after)
- Section transitions are smooth (the last slide of section N sets up section N+1)
- The opening establishes context before presenting arguments
- The closing resolves the narrative (call to action, recommendation, or summary)
- No repeated content across slides (two slides making the same point)

**Output**: Findings reference slide pairs (transitions) rather than individual slides.

### Lens 4: Audience Fit

**Question**: Is the content appropriate for the intended audience?

**Checks**:
- Tone matches the audience (executive = concise and outcome-focused, technical =
  precise and mechanism-focused, general = accessible and jargon-free)
- Complexity level is appropriate (no deep technical detail for executives, no
  oversimplification for experts)
- The "so what" is framed from the audience's perspective, not the presenter's
- Assumed knowledge is calibrated (no unexplained acronyms for general audiences,
  no over-explanation for domain experts)

**Requires**: Audience description from outline JSON or workflow state. If no
audience is specified, this lens asks for clarification before running.

---

## Template-Specific Lenses

These lenses activate only when the corresponding workflow template is active.
Templates declare their lenses in the `validation_lenses` field.

### Executive Readiness (board-strategy, rfp-exec)

**Question**: Can a decision-maker act on this deck?

**Checks**:
- At least one slide frames a clear decision or recommendation
- Action items have owners and timelines (not "we should consider")
- Financial figures are internally consistent across slides
- Risk/downside is acknowledged (not a one-sided pitch)
- The deck can stand alone without the presenter (self-explanatory)

### Knowledge Check (training)

**Question**: Will the learner achieve the stated learning objectives?

**Checks**:
- Learning objectives stated early (first 2 slides)
- Each objective is addressed by at least one content slide
- Practice activities or knowledge checks present (not all passive content)
- Concepts build sequentially (no forward references to undefined terms)
- Summary/recap slide at the end maps back to objectives

### Engagement (general, training)

**Question**: Will the audience stay attentive throughout?

**Checks**:
- Slide type variety (no more than 3 consecutive bullet slides)
- Visual elements present (not a wall of text)
- Deck length appropriate for stated time slot
- Opening slide creates curiosity or urgency (not a title-only slide)
- No "data dump" sequences (3+ consecutive stats slides without interpretation)

### Objectivity (board-strategy, architecture)

**Question**: Is the presentation balanced and fair?

**Checks**:
- Trade-offs acknowledged (not just advantages)
- Counter-arguments addressed or pre-empted
- Data presented without misleading framing (no cherry-picked baselines)
- Alternatives considered (not a false binary)
- Limitations stated explicitly

### Accuracy (rfp-exec, board-strategy)

**Question**: Are the facts correct and current?

**Checks**:
- Data freshness — dates on statistics (no undated claims)
- Citation quality — primary sources preferred over secondary
- Internal consistency — the same metric is not cited with different values
- No extrapolation presented as fact
- Named sources for all quantitative claims

### Actionability (general, rfp-exec)

**Question**: Does the audience know what to do next?

**Checks**:
- Clear next steps on the closing slide
- Owners assigned to action items (not "the team will")
- Timeline for follow-up actions
- Decision requested is specific (not "let us know your thoughts")
- Contact information or follow-up mechanism provided

---

## Lens Configuration in Templates

Workflow templates declare which lenses to run:

```yaml
# In workflow-templates.md template definition
validation_lenses:
  universal: true                    # Always true — cannot disable universal lenses
  template_lenses:
    - executive-readiness
    - accuracy
    - actionability
```

If no template is active, only the four universal lenses run.

---

## Parallel Execution

All active lenses run simultaneously as parallel agents. Each lens receives:
- The full set of slide HTML files
- The outline JSON (for narrative context)
- The audience description
- The active template name

Each lens returns its findings independently. There is no cross-lens
communication during execution.

---

## Punch List Aggregation

After all lenses complete, their findings are merged into a consolidated
punch list:

```markdown
# Validation Punch List

## Blocking Issues (must fix before export)

1. **[Clarity] Slide 3**: Title is a topic label, not an assertion
   - Current: "Market Overview"
   - Suggested: "Our addressable market grew to $4.2B in 2025"

2. **[Evidence] Slide 7**: Statistic has no named source
   - Current: "Studies show a 60% improvement"
   - Suggested: Add source attribution or remove the claim

## Recommended Improvements (should fix)

3. **[Flow] Slides 4→5**: Abrupt transition — no bridge between problem and solution
   - Suggested: Add a transition sentence in slide 4 notes or a brief bridge slide

4. **[Audience Fit] Slide 9**: Technical jargon without definition
   - Current: "The API gateway handles mTLS termination"
   - Suggested: Add a parenthetical definition or simplify

## Pass Summary

| Lens | Status | Findings |
|------|--------|----------|
| Clarity | 8/10 pass | 2 blocking |
| Evidence | 9/10 pass | 1 blocking |
| Flow | Pass | 1 recommended |
| Audience Fit | 9/10 pass | 1 recommended |
| Executive Readiness | Pass | 0 findings |
| Accuracy | Pass | 0 findings |
```

### Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| `blocking` | Must fix before export | Deck should not leave the build phase |
| `recommended` | Should fix for quality | Fix during polish phase if time allows |
| `info` | Observation, no action needed | Logged but does not appear in punch list |

---

## Integration with Other Skills

### Reads From

| Skill | What | Why |
|-------|------|-----|
| generate | HTML slide files | Content to evaluate |
| outline | `outline.json` | Narrative intent, audience description |
| workflow | `deck-state.json` | Active template, active lenses |
| notes | `notes.json` | Speaker notes for flow evaluation |

### Produces For

| Skill | What | Why |
|-------|------|-----|
| validate | Punch list | Merged with structural validation findings |
| workflow | Gate artifact | Blocking count determines gate pass/fail |
| checkpoint | Validation status | Session state tracking |
| convert | Quality signal | Zero-blocking punch list enables export |

---

## How Claude Should Use This Skill

1. **Run all active lenses** — never skip the universal lenses. Template-specific
   lenses run only when the template declares them.
2. **Present blocking issues first** — the user needs to see what must be fixed
   before seeing recommendations.
3. **Be specific in suggestions** — every finding must include a concrete
   suggestion, not just a diagnosis. "Title is a topic label" is a diagnosis.
   "Change to: Our addressable market grew to $4.2B" is a suggestion.
4. **Merge with structural validation** — if the validate skill has also run,
   combine both punch lists into a single document. Structural issues (bounds,
   overflow) and content issues (clarity, evidence) appear together.
5. **Respect the gate** — if any blocking issue exists, do not advance the
   workflow past the validate phase. The user must fix or explicitly waive
   each blocking finding.

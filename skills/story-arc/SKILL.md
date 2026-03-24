---
name: story-arc
description: |
  Lightweight single-agent narrative advisor. Recommends narrative structure
  from six proven patterns and maps it to a slide sequence. Alternative to
  full brainstorm for simpler presentations.

  Use when: "what's the story", "narrative arc", "how should I structure this",
  "story structure", "presentation flow", "what order should the slides go",
  "improve the narrative", "the flow feels off"
---

# Story Arc — Narrative Advisor

Lightweight single-agent narrative design tool. Analyzes a topic, brief, or
existing outline and recommends a narrative structure from six proven patterns.
Maps the chosen pattern to a concrete slide sequence with transition moments,
emotional arc, and evidence placement.

This is the fast alternative to brainstorm. One agent, no persona teams, no
multi-round discussion. Use when the deck is straightforward and the user
needs structure, not ideation.

---

## When to Use

- User has a topic but no structure ("how should I organize this?")
- User has an outline that feels flat or disjointed ("the flow is off")
- User wants a quick narrative recommendation before generating slides
- The deck is 5-15 slides and does not require the full brainstorm methodology
- User explicitly asks for "story structure" or "narrative arc"

**When NOT to use**: For complex proposals, RFP responses, or decks requiring
multi-stakeholder alignment, use brainstorm instead. Story-arc is a compass,
not a construction crew.

---

## Six Narrative Patterns

### 1. Setup - Tension - Resolution

**Best for**: Conference talks, keynotes, thought leadership

The classic three-act structure. Establish the world, introduce a disruption
or challenge, then show how the disruption is resolved.

```
Setup (2-3 slides)     → Tension (3-5 slides)     → Resolution (2-3 slides)
Context, status quo       Challenge, stakes,          Answer, evidence,
                          what's at risk              call to action
```

**Emotional arc**: Comfort → Discomfort → Relief
**Evidence placement**: Concentrated in Resolution to prove the answer works
**Opening hook**: A surprising fact that disrupts the assumed status quo

### 2. Problem - Solution - Impact

**Best for**: Pitches, proposals, budget requests

Lead with the pain, present the remedy, prove it works. Direct and persuasive.

```
Problem (2-3 slides)   → Solution (3-5 slides)    → Impact (2-3 slides)
Pain, cost of inaction    How it works, why this      Results, ROI, next
                          approach, differentiation   steps, the ask
```

**Emotional arc**: Urgency → Hope → Confidence
**Evidence placement**: Split — data on the problem's severity, then data on
the solution's effectiveness
**Opening hook**: The cost of doing nothing (quantified)

### 3. Situation - Complication - Resolution (SCR)

**Best for**: Executive briefings, board updates, McKinsey-style

The Pyramid Principle's narrative backbone. State the situation factually,
introduce what changed or what's wrong, then present the recommendation.

```
Situation (1-2 slides) → Complication (2-3 slides) → Resolution (3-5 slides)
Where we are today        What changed, what's          Recommendation,
                          broken, what's new            supporting arguments
```

**Emotional arc**: Neutral → Concern → Clarity
**Evidence placement**: Heavy in Resolution — each supporting argument needs
its own evidence slide
**Opening hook**: A single declarative sentence stating the recommendation
(answer first, then prove it)

### 4. What - So What - Now What

**Best for**: Status updates, data presentations, quarterly reviews

Present the facts, interpret their meaning, then recommend action. Works for
any data-driven deck where the audience needs to understand implications.

```
What (2-3 slides)      → So What (3-4 slides)     → Now What (2-3 slides)
Data, metrics, facts      Interpretation, trends,     Actions, owners,
                          implications, risks         timelines, decisions
```

**Emotional arc**: Information → Insight → Agency
**Evidence placement**: Front-loaded in "What" — the data speaks first
**Opening hook**: The single most surprising data point

### 5. Before - Journey - After

**Best for**: Transformation stories, case studies, change management

Show the starting state, walk through the transformation process, then reveal
the outcome. Powerful for demonstrating change.

```
Before (2-3 slides)    → Journey (4-6 slides)     → After (2-3 slides)
Pain state, old way,      Steps taken, challenges     New state, results,
why change was needed     overcome, key decisions     lessons learned
```

**Emotional arc**: Dissatisfaction → Effort → Triumph
**Evidence placement**: Distributed — "Before" data sets the baseline,
"Journey" shows progress, "After" shows the delta
**Opening hook**: A vivid before/after comparison (the transformation in one image)

### 6. Hook - Build - Payoff

**Best for**: Persuasive presentations, sales decks, fundraising

Open with something irresistible, build the case methodically, then deliver
the payoff that makes the ask feel inevitable.

```
Hook (1-2 slides)      → Build (4-6 slides)       → Payoff (2-3 slides)
Surprising fact, bold      Layer evidence, build       The ask, made
claim, provocative         credibility, address        inevitable by the
question                   objections                  evidence
```

**Emotional arc**: Curiosity → Conviction → Commitment
**Evidence placement**: Concentrated in Build — each slide adds one layer
of proof that makes the payoff undeniable
**Opening hook**: A bold claim or provocative question the audience cannot ignore

---

## Output Format

Story-arc produces a narrative recommendation document:

```markdown
## Recommended Pattern: [Pattern Name]

**Why this pattern**: [1-2 sentences explaining the fit]

### Slide Sequence

| # | Phase | Slide Purpose | Key Content |
|---|-------|--------------|-------------|
| 1 | Setup | Opening hook | [specific suggestion] |
| 2 | Setup | Context | [what to establish] |
| 3 | Tension | The challenge | [what to introduce] |
| ... | ... | ... | ... |

### Transition Moments

- Slide 2 → 3: [how to bridge from context to challenge]
- Slide 5 → 6: [how to pivot from problem to solution]
- Slide N-1 → N: [how to land the closing]

### Emotional Arc

[One-line description of the emotional journey]

### Evidence Placement

- Slide X: [what data/proof goes here and why]
- Slide Y: [what data/proof goes here and why]

### Opening Hook Suggestion

[Specific, concrete opening — not a template, but a real suggestion
based on the topic]

### Closing Call-to-Action

[Specific closing that follows from the narrative arc]
```

---

## Critique Mode

Story-arc can also evaluate an existing outline's narrative flow:

1. Read the outline JSON
2. Identify which pattern the outline most closely follows (or none)
3. Flag narrative gaps:
   - Missing setup (jumps straight to content)
   - No tension/complication (flat sequence of facts)
   - Weak transitions (slides that don't connect to neighbors)
   - Missing close (deck ends without resolution or call-to-action)
   - Evidence bunching (all data on one slide instead of distributed)
4. Recommend specific improvements with slide numbers

---

## Integration with Other Skills

### Reads From

| Skill | What | Why |
|-------|------|-----|
| outline | `outline.json` | Existing structure to critique or build from |
| workflow | `deck-state.json` | Template context for audience expectations |
| learn | Index files | Source material for evidence placement suggestions |

### Produces For

| Skill | What | Why |
|-------|------|-----|
| outline | Narrative framework | Story-arc output feeds into outline as the structural backbone |
| brainstorm | N/A — story-arc is an alternative, not a feeder | Choose one or the other |
| notes | Transition moments | Speaker notes reference transition cues from the arc |

---

## Story-Arc vs Brainstorm

| Dimension | story-arc | brainstorm |
|-----------|-----------|------------|
| Agents | 1 (narrative advisor) | 6+ (three dreamer-skeptic pairs) |
| Duration | 1-2 minutes | 10-20 minutes |
| Output | Narrative recommendation | Full synthesized architecture |
| Slide count sweet spot | 5-15 slides | 10-30 slides |
| Best for | Clear topic, known audience | Complex or contested content |
| Ideation depth | Pattern matching | Generative exploration |

**Rule of thumb**: If the user can state their key message in one sentence and
the audience is well-understood, use story-arc. If the user is still
discovering what the deck should say, use brainstorm.

---

## How Claude Should Use This Skill

1. **Ask for the topic and audience** — both are required to recommend a pattern.
   The same topic may use different patterns for different audiences.
2. **Recommend one pattern** — do not present all six and ask the user to choose.
   Make a recommendation with a rationale. Offer alternatives only if asked.
3. **Be concrete** — the slide sequence should have real content suggestions,
   not placeholders. "Slide 3: Show the 40% cost reduction metric" not
   "Slide 3: Present key data."
4. **Feed into outline** — if the user approves the arc, convert the slide
   sequence into outline JSON format and hand off to the outline skill.
5. **Know when to escalate** — if the user's needs are more complex than a
   single pattern can serve, recommend brainstorm instead of forcing a fit.

---
name: checkpoint
description: |
  Synthesizes what happened in a brainstorm or riffing session into a durable
  checkpoint — decisions made, work completed, open questions, and concrete
  next steps. Prevents losing context between sessions.

  Use when: "where were we", "what did we decide", "summarize the session",
  "what's next", "checkpoint this", "wrap up", "pick up where we left off",
  "what's the status of the deck", "sync me up"
---

# Deck Checkpoint

Captures the state of a deck project after a brainstorm, riffing session, or
build sprint so the next session can resume without loss. The output is a
checkpoint file that serves as the single source of truth for project state.

## When to Use

- After a brainstorm or ideation session (deck-brainstorm output → checkpoint)
- After a riffing/iteration session where decisions were made informally
- When resuming work and needing to reconstruct context
- Before ending a session to preserve state
- When the user says "where were we" or "what's next"

## Checkpoint Format

Write the checkpoint to `{project-dir}/deck-checkpoint.md`. This file is
overwritten each time — it represents current state, not history.

```markdown
---
project: {project name or slug}
phase: {current deck-pipeline phase, or "pre-pipeline" if informal}
updated: {ISO 8601 timestamp}
session: {session ID if available}
---

# Deck Checkpoint: {project name}

## Decisions Made
- {decision 1 — what was decided and why}
- {decision 2}

## Work Completed
- {artifact 1 — what exists now, where it lives}
- {artifact 2}

## Open Questions
- {question 1 — what still needs resolution, who owns it}
- {question 2}

## Constraints Established
- {constraint 1 — rules or guardrails agreed on}
- {constraint 2}

## Next Steps
1. {concrete action 1 — specific enough to start without re-reading the session}
2. {concrete action 2}
3. {concrete action 3}

## Source Material Referenced
- {file or document 1}
- {file or document 2}
```

## How to Build the Checkpoint

### From a Brainstorm Session

1. Read the brainstorm output (team outputs, synthesis, threading map).
2. Extract decisions from the synthesis — anything that narrows the option space.
3. List artifacts produced (narrative arc, proof specs, commercial threading plan).
4. Identify open questions — anything the skeptics flagged but didn't resolve.
5. Convert the brainstorm output into next steps for the build phase.

### From a Riffing/Iteration Session

1. Review the conversation for decisions — look for agreement, pivots, or
   "let's go with X" moments.
2. Check for any files created or modified during the session.
3. Note any constraints that emerged ("keep it under 15 slides", "no stock photos").
4. Identify what the user was working toward when the session ended.
5. Write next steps that continue from that momentum.

### When Resuming

1. Read `deck-checkpoint.md` if it exists.
2. Verify artifacts still exist (files may have been moved or deleted).
3. Present the checkpoint to the user: decisions, open questions, next steps.
4. Ask: "Does this match where you are? Anything changed?"
5. Proceed from next steps.

## Integration with deck-pipeline

If the project is using deck-pipeline, the checkpoint should align with
`deck-state.json`:

- `phase` in the checkpoint matches the current pipeline phase
- Constraints from the checkpoint should be cross-checked against `constraints.json`
- Next steps should reference the gate conditions for the current phase

If the project is informal (no pipeline), the checkpoint stands alone.

## Integration with wicked-garden Memory

When available, persist key decisions to wicked-garden memory for cross-session
recall. The checkpoint file is the detailed record; memory entries are the
searchable summaries.

Store to memory:
- Major architectural decisions (narrative arc, slide count, key themes)
- User preferences discovered during the session
- Constraints that should survive project boundaries

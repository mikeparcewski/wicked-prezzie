---
name: add-notes
description: |
  Saves freeform notes, decisions, or captured session context to the project
  sources as structured markdown. Auto-indexes for searchability.

  Use when: "note this", "remember that", "save this decision", "capture this",
  "add a note", "record this constraint", "log this feedback"
---

# add-notes — Freeform Notes Capture

Saves freeform notes, decisions, stakeholder input, and session context as
structured markdown files in the project source library. Each note gets YAML
frontmatter with category tags and importance, then is auto-indexed so the
content becomes searchable alongside formal source documents.

---

## When to Use

- When the user shares a decision, constraint, or stakeholder input that should
  be preserved as a searchable source.
- When capturing session context that future sessions need to recall.
- When the user says "note this", "remember that", or "save this decision".
- During brainstorm or build phases when informal inputs need to be formalized.
- When capturing audience insights or content direction that emerged in conversation.

---

## Category Tags

Every note is assigned one or more category tags that determine how it is
indexed and surfaced during search:

| Category | Meaning | Default Importance | Examples |
|----------|---------|-------------------|----------|
| `decision` | A choice that narrows the option space | high | "We're going with the 3-act structure" |
| `stakeholder-input` | Direct input from a named person | high | "CFO wants ROI on slide 3" |
| `constraint` | A rule or guardrail that must be respected | high | "No more than 20 slides" |
| `positioning` | How we frame or position a topic | standard | "Lead with reliability, not cost" |
| `proof-point` | A specific fact or data point worth preserving | standard | "99.99% uptime last 12 months" |
| `open-question` | Something unresolved that needs an answer | low | "Do we include the Q4 forecast?" |
| `session-notes` | General session context and observations | standard | "User prefers visual-heavy slides" |
| `audience-insight` | Something learned about the target audience | high | "Board members care most about risk" |
| `content-direction` | Guidance on tone, style, or narrative approach | standard | "Keep it conversational, not formal" |

If the user does not specify a category, infer from the content:
- Statements with "we decided" or "let's go with" → `decision`
- Statements with "they said" or "she wants" → `stakeholder-input`
- Statements with "must", "never", "always", "no more than" → `constraint`
- Questions → `open-question`
- Everything else → `session-notes`

---

## Note File Format

Notes are written to `sources/notes/` as dated markdown files:

```markdown
---
category: [decision, constraint]
importance: high
created: 2026-03-23T14:45:00Z
source: session
title: Three-act structure with max 20 slides
tags: [structure, slide-count, narrative]
---

# Three-act structure with max 20 slides

We decided on a three-act narrative structure. The deck must not exceed
20 slides total, including the title slide and closing slide.

Act 1: Set the stage (slides 1-5)
Act 2: Build the case (slides 6-15)
Act 3: Call to action (slides 16-20)

This was driven by the stakeholder feedback that the prior deck was too long
and lost the audience's attention after slide 15.
```

**Filename convention**: `YYYY-MM-DD-{slug}.md` where slug is derived from
the title (lowercase, hyphens, max 50 characters).

Example: `2026-03-23-three-act-structure-max-20-slides.md`

---

## Importance Inference

When the user does not specify importance, derive it from the category:

| Category | Default Importance |
|----------|-------------------|
| `decision` | high |
| `stakeholder-input` | high |
| `constraint` | high |
| `audience-insight` | high |
| `positioning` | standard |
| `proof-point` | standard |
| `session-notes` | standard |
| `content-direction` | standard |
| `open-question` | low |

The user can override by saying "this is critical" or "just for reference".

---

## Workflow

```
User provides freeform text
    │
    ▼
Classify category (user-specified or inferred)
    │
    ▼
Assign importance (from category defaults or user override)
    │
    ▼
Generate title (from content, max 60 characters)
    │
    ▼
Write note to sources/notes/YYYY-MM-DD-{slug}.md
    │
    ▼
Check gaps.md for items this note may resolve
    │  ├─ match found → report to user
    │  └─ no match → continue
    │
    ▼
Indexing decision
    │  ├─ open-question + reference importance → skip indexing
    │  └─ all other combinations → auto-invoke wicked-prezzie:learn
    │       ├─ Pass 1: index the new note
    │       └─ Pass 2: full rebuild of cross-document synthesis
    │
    ▼
Report: note saved, location, category, importance, index status
```

---

## Indexing Exception

Notes with category `open-question` AND importance `reference` (or `low`) skip
automatic indexing. These are parking-lot items that are not yet resolved and
would add noise to the index. They remain in `sources/notes/` and will be
indexed if their importance is later upgraded or if the user explicitly requests
reindexing.

All other notes are auto-indexed immediately via `wicked-prezzie:learn` (Pass 1
for the new note, Pass 2 for full synthesis rebuild).

---

## Gap Resolution

Same mechanism as `wicked-prezzie:add-doc`. After writing the note, check
`index/_insights/gaps.md` for coverage gaps that the note's content may address.

Common matches:
- A `proof-point` note may resolve a "missing data" gap
- A `stakeholder-input` note may resolve a "unclear audience need" gap
- A `decision` note may resolve an "unresolved direction" gap

Report matches to the user. Do not auto-remove gaps from the file — learn
Pass 2 handles that during re-synthesis.

---

## Invocation Examples

```
"Note that the CFO wants ROI data on every section slide"
  → category: stakeholder-input, importance: high
  → file: 2026-03-23-cfo-wants-roi-on-section-slides.md
  → auto-indexed

"Remember: no stock photography, only custom diagrams"
  → category: constraint, importance: high
  → file: 2026-03-23-no-stock-photography-custom-diagrams.md
  → auto-indexed

"Save this: our uptime was 99.97% last quarter"
  → category: proof-point, importance: standard
  → file: 2026-03-23-uptime-99-97-last-quarter.md
  → auto-indexed

"Open question: should we include the competitive comparison?"
  → category: open-question, importance: low
  → file: 2026-03-23-include-competitive-comparison.md
  → skipped indexing (open-question + low importance)

"The audience cares most about risk mitigation and compliance"
  → category: audience-insight, importance: high
  → file: 2026-03-23-audience-cares-risk-mitigation-compliance.md
  → auto-indexed

"Just a note for reference: prior deck used blue theme"
  → category: session-notes, importance: reference
  → file: 2026-03-23-prior-deck-used-blue-theme.md
  → auto-indexed (session-notes, not open-question)
```

---

## Batch Notes

When the user provides multiple notes in one message (e.g., a bulleted list
of decisions), process each as a separate note file:

1. Split by logical boundary (one decision/constraint/insight per file)
2. Each file gets its own category, importance, and frontmatter
3. Run learn Pass 1 for each note
4. Run learn Pass 2 once after all notes are written
5. Report summary: notes saved, categories, any gaps resolved

---

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| **learn** | add-notes invokes learn for automatic indexing of new notes |
| **search** | Indexed notes appear in search results alongside formal documents |
| **ask** | Specialist agents can find decisions, constraints, and proof points from notes |
| **checkpoint** | Checkpoint reads notes to reconstruct session state; add-notes is the write side |
| **workflow** | Constraints captured as notes should also be written to `constraints.json` via the orchestrator |
| **brainstorm** | Decisions from brainstorm synthesis can be captured as notes for cross-session persistence |

---

## Relationship to checkpoint

`checkpoint` captures a snapshot of the full session state (decisions, open items,
next steps) as a single overwritten file. `add-notes` captures individual pieces
of information as permanent, indexed, searchable records. They are complementary:

- Use `checkpoint` for "where are we right now" (ephemeral, overwritten each time)
- Use `add-notes` for "this specific fact/decision matters" (permanent, accumulated)

---

## Limitations

- Notes are plain markdown and do not support embedded images or attachments.
  For documents with images, use `wicked-prezzie:add-doc` instead.
- Category inference is keyword-based. Ambiguous notes may be miscategorized.
  The user can always override by specifying a category explicitly.
- Duplicate detection is not performed. If the same decision is noted twice,
  both files exist in the index. This is acceptable — learn Pass 2 synthesis
  handles deduplication at the insight level.

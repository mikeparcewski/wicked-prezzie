---
name: start
description: >-
  Single entry point for wicked-prezzie. Detects what the user has (topic, source
  docs, HTML slides, reviewed Word doc), auto-detects the best workflow template,
  explains the recommendation with confidence level, and routes to the appropriate
  skill after user confirmation or override.
triggers:
  - "start"
  - "new deck"
  - "new presentation"
  - "build a deck"
  - "build me a presentation"
  - "create a deck"
  - "I have a topic"
  - "I have slides"
  - "I have documents"
  - "I have source docs"
  - "I have an RFP"
  - "proposal deck"
  - "help me build"
  - "where do I start"
  - "what should I do"
---

# start — Entry Point

The single entry point for wicked-prezzie. This skill figures out what the user
has, what they need, and routes them to the right workflow. Users should never
need to know the internal skill topology — `start` handles all routing.

---

## Step 1 — Detect What the User Has

Ask the user what they are working with, or infer from context. Classify into
exactly one of these input types:

| Input Type | Signals | Route Target |
|------------|---------|--------------|
| **Topic or brief** | Plain text description, a few sentences or paragraphs, no files | Workflow selection (Step 2) |
| **Source documents** | PDFs, DOCX, PPTX, spreadsheets — raw material not yet indexed | `wicked-prezzie:learn` first, then workflow selection |
| **HTML slides** | `.html` files with slide content, already generated | `wicked-prezzie:convert` (slide-pipeline) |
| **Reviewed Word doc** | `.docx` with inline comments from reviewers | `wicked-prezzie:feedback` (deck-feedback) |

If the user provides **source documents alongside a topic**, recommend running
`wicked-prezzie:learn` first to index the documents, then returning here to
select the workflow template. The learn step is not mandatory but significantly
improves brainstorm and build quality.

If the input type is ambiguous, ask one clarifying question. Do not guess.

---

## Step 2 — Auto-Detect Workflow Template

When the input type is **topic or brief** (with or without source docs), run
template auto-detection to recommend the best workflow.

### Detection Procedure

1. Scan available text: the user's brief, any indexed source documents (check
   `slide-learn` indexes if they exist), or the raw documents if indexes are not
   yet built.

2. Score each template by counting signal matches:

#### `rfp-exec` signals (bid/proposal workflow with executive summary gate)

**Keyword signals** (case-insensitive, match in brief or source docs):
- "request for proposal" / "RFP"
- "invitation to tender" / "ITT"
- "evaluation criteria"
- "mandatory requirements"
- "response required by" / "submission deadline"
- "scoring rubric" / "evaluation matrix"
- "evaluation committee" / "evaluation panel"
- "compliance matrix"
- "bid" / "tender" / "proposal response"
- "incumbent" / "competitive"

**Structural signals**:
- Documents with numbered requirements or compliance tables
- References to specific evaluation weightings or scoring methodology
- Named evaluation committee members or roles
- Documents that reference a formal procurement process

**Audience signals**:
- Multiple named decision-makers with different concerns
- Formal governance structure (board, committee, panel)
- Regulatory or compliance stakeholders

#### `general` signals (default — standard presentation workflow)

Everything that is not `rfp-exec`. General purpose presentations, keynotes,
internal updates, training decks, thought leadership, sales pitches without
formal procurement process.

### Confidence Scoring

- **High (>= 0.8)**: 3+ keyword signals AND 1+ structural signal. Present the
  recommendation with high confidence. Example: "This looks like an RFP response.
  I recommend the rfp-exec template, which adds an executive summary approval
  gate before slide building."

- **Medium (0.5 - 0.8)**: 2+ keyword signals OR 1 keyword + 1 structural signal.
  Present the recommendation but explicitly invite override. Example: "I see some
  proposal language. The rfp-exec template might be a good fit, but the general
  template would also work. Which do you prefer?"

- **Low (< 0.5)**: 0-1 signals. Default to `general`. Example: "I'll use the
  standard workflow. If this is actually an RFP response, let me know and I'll
  switch to the proposal template."

### Recommendation Protocol

Always present:
1. The signals found (or absence of signals)
2. The recommended template with a one-sentence explanation of what it adds
3. Confidence level (high / medium / low)
4. An explicit offer to override

Example output:

```
I found the following signals in your brief:
  - "request for proposal" (keyword)
  - "evaluation criteria" (keyword)
  - Named evaluation committee members (structural)

Recommendation: **rfp-exec** template (high confidence)
This adds an executive summary approval gate between brainstorm and architecture.
You'll review and approve the exec summary before any slides are built.

Want to proceed with rfp-exec, or switch to the general template?
```

---

## Step 3 — Confirm and Route

After the user confirms (or overrides) the template choice:

- **general** → Start `deck-pipeline` with the standard 8-phase flow (source
  inventory, personas, brainstorm, architecture, build, validate, polish, export)

- **rfp-exec** → Start `deck-pipeline` with the rfp-exec template, which inserts
  the `exec-summary` phase between brainstorm and architecture. The phase
  sequence becomes: source inventory, personas, brainstorm, **exec-summary**,
  architecture, build, validate, polish, export.

Pass the template name to deck-pipeline so it can load the correct phase
sequence. Record the template choice in `deck-state.json` under `template`.

---

## Quick-Route Paths (No Template Selection Needed)

These input types bypass template selection entirely:

- **HTML slides** → Route directly to `wicked-prezzie:convert`. Tell the user:
  "You have HTML slides ready for conversion. I'll start the slide-to-PPTX
  pipeline." No template detection needed.

- **Reviewed Word doc** → Route directly to `wicked-prezzie:feedback`. Tell the
  user: "I see a Word document with reviewer comments. I'll parse the feedback
  and generate an analysis report." No template detection needed.

---

## Source Doc Recommendation

When the user has source documents that have not been indexed:

1. Recommend running `wicked-prezzie:learn` first
2. Explain why: "Indexing your source documents first lets the brainstorm and
   build phases pull specific facts, figures, and named systems from them. Without
   indexing, the workflow still runs but relies on you providing details manually."
3. If the user declines, proceed with template selection anyway — indexing is
   recommended, not required
4. If the user accepts, run learn, then return to this skill for template
   selection

---

## Detection Source Priority

When running auto-detection:

1. **slide-learn indexes** (if they exist) — fastest, already structured with
   YAML frontmatter containing tags, themes, and key entities
2. **Raw document scanning** (fallback) — read the first 2-3 pages of each
   document to extract signals. Do not read entire large documents for detection
   purposes.
3. **User's brief text** — always scanned, even when documents are also available

---

## Session Resume

If `deck-state.json` already exists in the working directory (or a known deck
directory), this skill detects it and offers to resume:

"I found an existing deck project at `{deck_dir}` (currently in Phase {N}:
{phase_name}). Resume where you left off, or start a new project?"

If resuming, route directly to `deck-pipeline` which handles phase resumption.

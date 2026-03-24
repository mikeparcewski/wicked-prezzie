---
name: start
description: >-
  Single entry point for wicked-prezzie. Detects what the user has (topic, source
  docs, HTML slides, reviewed Word doc, document/response task), auto-detects the
  best workflow template from templates/*.yaml signal lists, explains the
  recommendation with confidence level, and routes to the appropriate skill after
  user confirmation or override.
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
  - "write a proposal"
  - "draft a report"
  - "write a response"
  - "build a document"
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
| **Topic or brief** | Plain text description, a few sentences or paragraphs, no files | Template selection (Step 2) → workflow |
| **Source documents** | PDFs, DOCX, PPTX, spreadsheets — raw material not yet indexed | `wicked-prezzie:learn` first, then template selection |
| **HTML slides** | `.html` files with slide content, already generated | `wicked-prezzie:convert` (convert) |
| **Reviewed Word doc** | `.docx` with inline comments from reviewers | `wicked-prezzie:feedback` (feedback) |
| **Document/response task** | User wants a structured document (proposal, report, assessment), not a slide deck | `wicked-prezzie:structured-response` |

**Distinguishing deck vs. document tasks**: If the user says "presentation",
"deck", "slides", "keynote" — it is a deck task (template selection → workflow).
If the user says "proposal document", "write a report", "draft a response",
"build a submission", "Word document" — it is a document task (structured-response).
If ambiguous, ask: "Are you building a slide deck or a written document?"

If the user provides **source documents alongside a topic**, recommend running
`wicked-prezzie:learn` first to index the documents, then returning here to
select the workflow template. The learn step is not mandatory but significantly
improves brainstorm and build quality.

If the input type is ambiguous, ask one clarifying question. Do not guess.

---

## Step 2 — Auto-Detect Workflow Template

When the input type is **topic or brief** (with or without source docs), run
template auto-detection to recommend the best workflow template.

### Dynamic Template Loading

Templates are YAML files in the `templates/` directory at the project root.
**Do not hardcode template names or signals.** Instead:

1. Read all `*.yaml` files from `templates/`
2. For each template, extract:
   - `name` — template identifier
   - `display_name` — human-readable name
   - `description` — one-line summary
   - `signals` — list of detection keywords
   - `phases` — phase sequence (show count to user)
3. Build the signal-matching table dynamically from loaded templates

This means adding a new template is a single YAML file — no code changes needed.

### Detection Procedure

1. Scan available text: the user's brief, any indexed source documents (check
   `learn` indexes if they exist), or the raw documents if indexes are not
   yet built.

2. Score each template by counting signal matches against its `signals` list:
   - Case-insensitive keyword matching against brief text and source documents
   - Each matching signal keyword scores 1 point
   - Structural signals (numbered requirements, compliance tables, formal
     procurement language) score 2 points for templates whose signals include
     related terms

3. Rank templates by total score. The highest-scoring template is the
   recommendation.

### Confidence Scoring

- **High (>= 3 signal matches)**: Present the recommendation with high
  confidence. Example: "This looks like a training workshop. I recommend the
  training-workshop template (6 phases including Learning Design and Practice
  Activities)."

- **Medium (2 signal matches)**: Present the recommendation but explicitly
  invite override. Example: "I see some competitive analysis language. The
  competitive-analysis template might fit, but other templates could work too."

- **Low (0-1 signal matches)**: Default to `general`. Example: "I'll use the
  General Presentation template. Let me know if another template fits better."

### Recommendation Protocol

Always present:
1. The signals found (or absence of signals)
2. The recommended template with a one-sentence description (from YAML `description`)
3. The phase sequence for the recommended template (names only, from YAML)
4. Confidence level (high / medium / low)
5. A list of all available templates (name + description) so the user can override
6. An explicit offer to override

Example output:

```
I found the following signals in your brief:
  - "training" (keyword match)
  - "workshop" (keyword match)
  - "learning" (keyword match)

Recommendation: **Training Workshop** template (high confidence)
6 phases: Source Inventory → Learning Design → Build → Practice Activities → Validate → Export

Available templates:
  - General Presentation — Default workflow for standard presentations
  - Executive Briefing — Board and C-suite presentations
  - Training Workshop — Training and education decks (recommended)
  - Conference Talk — Conference and keynote presentations
  - Competitive Analysis — Market and competitive analysis decks
  - Project Status — Status updates, sprint reviews, retrospectives

Want to proceed with Training Workshop, or switch to a different template?
```

---

## Step 3 — Confirm and Route

After the user confirms (or overrides) the template choice:

1. Record the template choice in `deck-state.json` under `template`
2. Route to `wicked-prezzie:workflow` with the selected template name
3. Workflow loads the phase sequence from the template YAML

The workflow orchestrator reads the template YAML to determine phases, gate
conditions, personas, and validation lenses. The template name in deck-state.json
is the source of truth for which template is active.

---

## Quick-Route Paths (No Template Selection Needed)

These input types bypass template selection entirely:

- **HTML slides** → Route directly to `wicked-prezzie:convert`. Tell the user:
  "You have HTML slides ready for conversion. I'll start the slide-to-PPTX
  pipeline." No template detection needed.

- **Reviewed Word doc** → Route directly to `wicked-prezzie:feedback`. Tell the
  user: "I see a Word document with reviewer comments. I'll parse the feedback
  and generate an analysis report." No template detection needed.

- **Document/response task** → Route directly to `wicked-prezzie:structured-response`.
  Tell the user: "You need a structured document. I'll help you configure and
  generate it with multi-agent review." If the user has source documents, recommend
  `wicked-prezzie:learn` first, then return to structured-response with
  `--generate-config`.

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

1. **learn indexes** (if they exist) — fastest, already structured with
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
{phase_name}, template: {template_name}). Resume where you left off, or start
a new project?"

If resuming, route directly to `workflow` which handles phase resumption.

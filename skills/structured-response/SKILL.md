---
name: structured-response
description: |
  Config-driven structured document generator with multi-agent review.
  Produces any structured document (proposals, reports, assessments) with
  parallel drafting and review agents. Exports to Word with inline comments.

  Use when: "write a proposal", "draft a report", "generate a response",
  "write the document", "build the submission", "structured document"
triggers:
  - "write a proposal"
  - "draft a report"
  - "generate a response"
  - "write the document"
  - "build the submission"
  - "structured document"
  - "response document"
  - "proposal document"
  - "write the report"
  - "RFP response"
  - "bid response"
  - "submission document"
---

# structured-response — Structured Document Generator

Config-driven document generator that produces structured prose documents
(proposals, reports, assessments, responses) using a 4-agent parallel review
pattern. All section definitions, format rules, messaging discipline, and
reviewer personas are defined in a project-level `response-config.md` file.

The output is a clean Word document with reviewer findings encoded as inline
comment bubbles — not embedded in the body text.

---

## Modes

### `--generate-config` — Generate Response Configuration

Reads source documents (indexed via `wicked-prezzie:learn` or raw files) and
generates a `response-config.md` file that defines:

1. **Document Structure**: Sections, ordering, page limits, required subsections
2. **Format Rules**: Heading styles, numbering scheme, citation format, tone
3. **Messaging Discipline**: Key themes to reinforce, language to avoid, positioning
4. **Reviewer Personas**: Who reviews each section and what they evaluate
5. **Source Mapping**: Which source documents feed which sections

Procedure:
1. Read all available source documents (or learn indexes if they exist)
2. Identify the document type (proposal, report, assessment, response)
3. Extract structural requirements (if responding to a formal request, extract
   the required sections, evaluation criteria, and compliance requirements)
4. Draft `response-config.md` with all sections populated
5. Present to user for review and modification
6. Save to project directory

The config file is plain markdown with YAML frontmatter. It is human-readable
and human-editable. Users can modify it directly between runs.

### `--section <section-id>` — Generate One Section

Generates a single section using the 4-agent pattern:

#### Agent 1: Drafter
- Reads source documents mapped to this section (from response-config.md)
- Writes first-draft prose following format rules and messaging discipline
- Inserts `[PLACEHOLDER: description]` markers where source material is
  insufficient or a specific detail is needed from the user
- Writes to `sections/{section-id}/draft.md`

#### Agent 2: Audience Reviewer
- Reads the draft from the audience's perspective (as defined in config)
- Evaluates: completeness, clarity, persuasiveness, appropriate detail level
- Outputs findings as `[COMMENT: reviewer=Audience | finding text]` markers
- Writes to `sections/{section-id}/audience-review.md`

#### Agent 3: Technical Reviewer
- Reads the draft for technical accuracy and feasibility
- Evaluates: accuracy against sources, overstatement, feasibility of claims,
  technical depth appropriate for audience
- Flags conflicts: `[CONFLICT: claim X in draft vs. source Y says Z]`
- Writes to `sections/{section-id}/technical-review.md`

#### Agent 4: Business Reviewer
- Reads the draft for messaging discipline and commercial accuracy
- Evaluates: alignment with positioning themes, pricing/commercial accuracy,
  competitive differentiation, no unauthorized commitments
- Writes to `sections/{section-id}/business-review.md`

#### Synthesis
After all 4 agents complete:
1. Read all review files for the section
2. Resolve non-conflicting feedback (incorporate directly)
3. For conflicts: present to user with both sides and a recommendation
4. Produce `sections/{section-id}/final.md` — clean prose only, no markers
5. Encode unresolved items as structured comment metadata in
   `sections/{section-id}/comments.json` for Word export

The reviewer personas (names, focus areas, evaluation criteria) are defined in
`response-config.md`. The 4-agent pattern is fixed, but who each reviewer
"is" and what they care about is fully configurable.

### `--all` — Generate All Sections

Runs `--section` for every section defined in `response-config.md`, respecting
the ordering. Sections without dependencies can run in parallel (up to 3
concurrent section generations). Sections that reference earlier sections
(e.g., an executive summary that synthesizes all other sections) run after
their dependencies complete.

Procedure:
1. Read `response-config.md` to get section list and dependency graph
2. Topologically sort sections by dependencies
3. Run independent sections in parallel (max 3 concurrent)
4. Run dependent sections after their inputs are ready
5. After all sections complete, run a cross-section consistency check:
   - Terminology consistent across sections
   - No contradictions between sections
   - Messaging discipline maintained throughout
   - Page/word limits respected

### `--build-doc` — Assemble Final Word Document

Assembles all `sections/{section-id}/final.md` files into a single Word
document using `scripts/build_response_docx.py`.

The script:
1. Reads `response-config.md` for section ordering, heading levels, and styles
2. Reads each `sections/{section-id}/final.md` in order
3. Reads each `sections/{section-id}/comments.json` for inline comments
4. Builds a `.docx` with:
   - Proper heading hierarchy (H1, H2, H3)
   - Formatted body text with styles from config
   - Table of contents (if config specifies)
   - Inline comment bubbles from reviewer findings
   - `[PLACEHOLDER: ...]` markers highlighted in yellow
   - Page breaks between major sections
5. Writes to `output/{document-name}.docx`

---

## Response Config Schema

The `response-config.md` file has this structure:

```markdown
---
document_type: proposal          # proposal | report | assessment | response
document_name: "Document Title"
tone: professional               # professional | conversational | academic | technical
numbering: decimal               # decimal (1.1, 1.2) | alpha | none
citation_format: inline          # inline | footnote | endnote
page_limit: null                 # null for no limit, or integer
---

## Messaging Discipline

### Key Themes
- Theme 1: description of how to reinforce
- Theme 2: description of how to reinforce

### Language to Avoid
- Avoid: "cutting-edge" → Use: "proven" or "established"
- Avoid: "leverage" → Use: "use" or "apply"

### Positioning
One paragraph describing the overall positioning strategy.

## Sections

### 1. Executive Summary
- **id**: exec-summary
- **page_limit**: 2
- **sources**: [all sections — synthesized after other sections complete]
- **depends_on**: [all other sections]
- **subsections**: none
- **guidance**: Summarize key points from all sections. Lead with the
  strongest differentiator.

### 2. Section Title
- **id**: section-id
- **page_limit**: 5
- **sources**: ["source-doc-1.pdf", "source-doc-2.pdf"]
- **depends_on**: []
- **subsections**: ["2.1 Sub A", "2.2 Sub B"]
- **guidance**: Specific instructions for this section's content and approach.

## Reviewers

### Audience Reviewer
- **name**: "Target Reader"
- **perspective**: "Non-technical decision-maker evaluating proposals"
- **evaluates**: completeness, clarity, persuasiveness

### Technical Reviewer
- **name**: "Technical Evaluator"
- **perspective**: "Domain expert checking claims and feasibility"
- **evaluates**: accuracy, feasibility, technical depth

### Business Reviewer
- **name**: "Commercial Lead"
- **perspective**: "Business stakeholder ensuring commercial discipline"
- **evaluates**: messaging alignment, commercial accuracy, competitive positioning
```

---

## File Structure

All working files live under the project directory:

```
{project_dir}/
  response-config.md           — Document configuration (user-editable)
  sections/
    {section-id}/
      draft.md                 — Agent 1 output (first draft)
      audience-review.md       — Agent 2 findings
      technical-review.md      — Agent 3 findings
      business-review.md       — Agent 4 findings
      final.md                 — Synthesized clean prose
      comments.json            — Structured reviewer comments for Word export
  output/
    {document-name}.docx       — Final assembled Word document
```

---

## Marker Syntax

Markers appear in draft and review files. They are never present in final.md.

| Marker | Meaning | Resolution |
|--------|---------|------------|
| `[PLACEHOLDER: description]` | Content gap — needs user input or additional source | Highlighted yellow in Word export until resolved |
| `[COMMENT: reviewer=Name \| finding]` | Reviewer observation — non-blocking | Becomes Word comment bubble |
| `[CONFLICT: claim vs. source]` | Factual conflict — must be resolved | Presented to user for resolution before final |

---

## Integration with Other Skills

- **wicked-prezzie:learn** — Index source documents before running generate-config.
  Indexed sources produce better section-to-source mapping.
- **wicked-prezzie:start** — Routes here when it detects a document/response task
  rather than a presentation task.
- **wicked-prezzie:workflow** — Workflow orchestrator may invoke structured-response
  during the Build phase when the deliverable is a document rather than slides.

---

## Script: build_response_docx.py

Located at `skills/structured-response/scripts/build_response_docx.py`.

Dependencies: `python-pptx` is already installed; this script also requires
`python-docx` (same ecosystem). Uses `docx.Document`, `docx.oxml` for comment
insertion.

Invocation:
```bash
python3 skills/structured-response/scripts/build_response_docx.py \
  --config response-config.md \
  --sections-dir sections/ \
  --output output/document.docx
```

The script is a mechanical assembler — it does not make content decisions. All
content decisions are made by Claude during the section generation and synthesis
steps. The script reads markdown, applies Word styles, and inserts comments.

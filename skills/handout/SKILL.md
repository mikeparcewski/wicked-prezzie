---
name: handout
description: |
  Generates attendee takeaway documents from slides and speaker notes.
  Produces readable prose (not slide dumps) in markdown, PDF, or Word format
  at three detail levels. Respects per-deck editorial context.

  Use when: "create a handout", "make a takeaway", "attendee document",
  "leave-behind", "post-presentation document", "share the content",
  "readable version", "export as document", "print version"
---

# handout — Takeaway Document Generator

Transforms a slide deck into a readable document for attendees. Not a slide
printout — a prose document that expands slide content into full sentences,
adds context from speaker notes, and includes source citations from the index.
Three detail levels, three output formats.

## When to Use

- After a deck is finalized and you need a document for attendees
- When stakeholders who missed the presentation need the content
- For compliance or record-keeping — a readable artifact alongside the PPTX
- When the deck content needs to be shared as a standalone document (email, intranet)
- For pre-read documents sent before the presentation

---

## Inputs

| Input | Required | Source |
|-------|----------|--------|
| Slide HTML files | Yes | `{deck_dir}/slides/` |
| Speaker notes | Recommended | Embedded in slide HTML or separate notes files |
| Outline JSON | Recommended | `{deck_dir}/state/outline.json` — provides narrative arc and key messages |
| Source index | Optional | `index/_insights/` — for citations and expanded evidence |
| Per-deck CLAUDE.md | Optional | `{deck_dir}/CLAUDE.md` — for tone, terminology, audience context |
| Theme JSON | Optional | Active theme — for document styling cues |

---

## Detail Levels

### `summary` — Executive Briefing

One paragraph per slide. Key takeaways only. No citations, no appendix.
Suitable for: executive pre-reads, email summaries, quick recaps.

**Target length**: 1-2 pages for a 15-slide deck.

**Per-slide output**:
- Section header (slide title or key message)
- Single paragraph synthesizing the slide's core point
- No bullet lists — prose only

### `standard` — Full Handout (default)

Expanded prose with evidence for each slide. Includes all key data points
and supporting arguments. Suitable for: attendee takeaways, post-meeting
distribution, reference documents.

**Target length**: 4-8 pages for a 15-slide deck.

**Per-slide output**:
- Section header with key message
- 1-3 paragraphs expanding the slide content into readable prose
- Data points and statistics preserved with context
- Speaker note content woven into the narrative (not dumped verbatim)
- Inline source references where available

### `detailed` — Complete Reference

Everything in `standard` plus full citations, appendix, and optional Q&A
section. Suitable for: compliance records, deep-dive reference, due diligence.

**Target length**: 8-15 pages for a 15-slide deck.

**Per-slide output**:
- Everything from `standard`
- Full source citations with document name, page/chunk reference
- Extended evidence from source index (not just what's on the slide)
- Footnotes for data points

**Appendix sections**:
- Source bibliography — all documents referenced, with dates and descriptions
- Additional reading — related source chunks not directly cited in the handout
- Q&A section — anticipated questions and answers derived from speaker notes'
  talking points and objection handlers (if available)
- Glossary — key terms and definitions from the per-deck CLAUDE.md terminology
  section (if available)

---

## Output Formats

### Markdown (default)

Plain markdown file. Clean typography, heading hierarchy, standard formatting.
Readable in any text editor, version-controllable, easy to share.

```
{deck_dir}/deliverables/{deck-slug}-handout.md
```

### PDF

Markdown rendered to HTML with clean print-optimized CSS, then printed to PDF
via Chrome headless. Professional typography: proper margins, page numbers,
headers/footers, table of contents for `detailed` level.

```bash
# Render flow: markdown → HTML (with print CSS) → Chrome --print-to-pdf
python skills/chrome-extract/scripts/chrome_extract.py \
  --print-pdf handout.html \
  --output {deck_dir}/deliverables/{deck-slug}-handout.pdf
```

```
{deck_dir}/deliverables/{deck-slug}-handout.pdf
```

### Word (.docx)

Generated via python-docx. Heading hierarchy, paragraph styles, proper page
breaks between major sections. Compatible with corporate templates.

```
{deck_dir}/deliverables/{deck-slug}-handout.docx
```

---

## Generation Procedure

### Step 1: Gather Inputs

1. Read slide HTML files in order.
2. Extract text content and speaker notes from each slide.
3. Read outline.json for narrative arc, act structure, and key messages.
4. Read per-deck CLAUDE.md for editorial context (tone, audience, terminology).
5. If source index exists, load `_insights/key-facts.md` for citation material.

### Step 2: Build Document Structure

```
Title Page
  - Deck title (from outline or first slide)
  - Date
  - Audience (from CLAUDE.md or outline)
  - Detail level indicator

Table of Contents (detailed level only)

Body (per slide, in deck order)
  - Section header: slide key message or title
  - Prose content: expanded from slide text + speaker notes
  - Data callouts: stats and figures preserved with context
  - Citations: inline references to source material (standard + detailed)

Appendix (detailed level only)
  - Source bibliography
  - Additional reading
  - Q&A section
  - Glossary
```

### Step 3: Transform Slide Content to Prose

For each slide, apply these transformations:

1. **Bullets to prose** — convert bullet lists into flowing paragraphs. Preserve
   the logical relationship between points (sequence, comparison, cause-effect).
2. **Stats with context** — don't just state "34% growth." Write "Revenue grew
   34% year-over-year, driven by expansion into three new markets."
3. **Speaker notes integration** — weave speaker note content into the prose
   naturally. Notes often contain the "why" that slides lack.
4. **Heading hierarchy** — map slide structure to document headings. Act dividers
   become H1, slide titles become H2, sub-sections become H3.
5. **Visual descriptions** — for slides with charts or diagrams, describe the
   visual content in words (e.g., "The trend line shows steady growth from
   Q1 through Q3, with a sharp acceleration in Q4").

### Step 4: Editorial Polish

1. **Tone alignment** — match the tone specified in per-deck CLAUDE.md. A
   technical audience gets precise language; an executive audience gets concise
   strategic framing.
2. **Terminology consistency** — use the terminology map from CLAUDE.md. Don't
   mix "customers" and "clients" if the deck uses one consistently.
3. **Transition sentences** — add brief transitions between sections to maintain
   narrative flow. The document should read as a coherent piece, not a sequence
   of disconnected summaries.
4. **Remove presentation artifacts** — strip "as you can see on the left,"
   "next slide," and other presentation-specific language.

### Step 5: Generate Output

1. Write the markdown version (always generated as intermediate step).
2. If PDF requested: render markdown to HTML with print CSS, use Chrome headless
   to print to PDF.
3. If Word requested: generate .docx via python-docx with proper styles.

---

## Integration with Other Skills

| Skill | Integration Point |
|-------|-------------------|
| **generate** | Reads slide HTML files produced by generate |
| **learn** | Pulls citations and extended evidence from the source index |
| **workflow** | Can be triggered in Phase 8 (Export) alongside PPTX export |
| **chrome-extract** | PDF output uses Chrome headless for HTML-to-PDF rendering |
| **theme** | Theme colors can inform document accent colors in Word/PDF output |
| **exec-summary** | Handout can incorporate or reference the executive summary |
| **outline** | Reads outline.json for narrative structure and key messages |
| **collaborate** | Handout can be included in review sessions as supplementary material |

---

## Invocation Examples

```
"Create a handout for this deck"
  → handout --level standard --format markdown

"Make a PDF leave-behind for the attendees"
  → handout --level standard --format pdf

"I need a detailed reference document with citations"
  → handout --level detailed --format docx

"Quick summary for the exec team"
  → handout --level summary --format pdf

"Export a handout in all formats"
  → handout --level standard --format markdown,pdf,docx
```

---

## Dependencies

- **python-docx** — for Word output (already a project dependency)
- **Google Chrome** — for PDF rendering via headless print
- **beautifulsoup4** — for HTML slide content extraction (already a project dependency)

---

## Limitations

- Speaker notes quality directly affects handout quality. Slides with no speaker
  notes produce thinner handout sections — Claude fills in from slide content
  and source index, but the result is less rich.
- Chart and diagram descriptions are generated by Claude's vision. Complex
  multi-axis charts may lose nuance in the text description.
- PDF rendering uses Chrome's print engine. Page breaks may not always fall
  at ideal positions for very long sections.
- The Q&A section in `detailed` level is generated from talking points and
  objection handlers. If speaker notes lack these, the Q&A section is omitted
  rather than fabricated.

# Chunk Strategy

Rules for splitting source documents into indexable chunks. The goal is chunks
that are semantically coherent (one idea or section), small enough to search
precisely, and large enough to give useful context.

---

## PDF

**Method**: Page-based chunking with section detection.

**Target size**: 3–6 pages per chunk.

**Boundaries**: Prefer breaking at section headings, chapter titles, or
horizontal rule elements visible in the page content. Never break mid-paragraph.

**Rules**:

1. Start with pages 1–4 as the first chunk (cover + executive summary often
   span 2–3 pages, keep together).
2. For subsequent chunks, target 3–6 pages. Expand to 6 when a section clearly
   continues; compress to 3 when a new heading appears.
3. If a single page contains only a large figure or chart, treat it as its own
   chunk with `content_type: [visual]`.
4. For large documents (> 20 pages): use 4-page chunks with 1-page overlap.
   Overlap means the last page of chunk N is repeated as the first page of
   chunk N+1 to preserve context across boundaries.
5. Set `pages: "{start}-{end}"` in frontmatter.

**Vision guidance**: For each page range, read the pages and describe:
- Text content: summarize key points, extract metrics verbatim.
- Figures: apply the appropriate template from `vision-templates.md`.
- Tables: extract headers and key data rows.

---

## PPTX

**Method**: Per-slide chunking with optional section summaries.

**Target size**: 1 slide per chunk (always).

**Section summaries**: When the deck has explicit section divider slides
(slides with only a title and no body content), also create a section-summary
chunk covering all slides in that section. Add `"section_summary": true` to
its frontmatter.

**Rules**:

1. One chunk file per slide, numbered sequentially (`chunk-001.md` = slide 1).
2. Set `slide_number: {N}` in frontmatter.
3. For title slides (slide 1 or slides with `content_type: [cover]`): set
   `slide_relevance: [title]`.
4. For agenda slides (bullet list of 4+ items on a single text box): set
   `slide_relevance: [agenda]`.
5. For section dividers (full-bleed image or single large title, no body):
   set `slide_relevance: [section]`.

**Vision guidance**: For each slide, describe:
- Title and subtitle text (verbatim if short, summarized if long).
- Body content: key bullets, call-outs, statistics.
- Visual elements: apply templates from `vision-templates.md`.
- Speaker notes: include verbatim in the content body under a `## Notes`
  heading.

---

## DOCX

**Method**: Section-heading chunking.

**Target size**: 400–800 words per chunk.

**Boundaries**: Split at H1 (`#`) and H2 (`##`) headings. If a section is
> 800 words, split further at H3 headings or every 600 words (whichever comes
first).

**Rules**:

1. The document title and abstract (if present before the first H1) form
   chunk 1.
2. Each H1 section starts a new chunk. If the section body is > 800 words,
   split at H2 sub-headings.
3. If a section has no sub-headings and exceeds 800 words, split at paragraph
   breaks nearest to the 600-word mark.
4. Appendices and bibliography are low-priority: chunk as a single block even
   if they exceed 800 words, but set `content_type: [appendix]`.
5. Tables within a section should be extracted as their own chunk (see Tables
   section below).

**Text extraction**: DOCX is a ZIP of XML. The agent reads the file content
directly and extracts text in reading order. Preserve heading levels, bullet
indentation, and table structure.

---

## HTML

**Method**: Per-slide div chunking.

**Target size**: 1 slide div per chunk.

**Boundaries**: Each top-level `<div>` element with a class containing `slide`
is one chunk. If no slide divs are present, treat the whole file as one chunk.

**Rules**:

1. Extract text content in DOM reading order (title → subtitle → body).
2. Preserve bullet structure as Markdown lists.
3. Strip style attributes and script content.
4. If a div contains an `<svg>`, note it in `figures` using the Diagrams
   template from `vision-templates.md`.
5. Set `slide_number` to the 1-based index of the div within the file.

**Text extraction**: The script extracts slide divs with a regex pattern.
The agent may refine the extraction by reading the raw HTML for complex layouts.

---

## Images

**Method**: Single chunk per image file.

**Rules**:

1. Always one chunk per image file.
2. The entire chunk content is the vision description.
3. Apply the appropriate template from `vision-templates.md` based on what the
   image shows:
   - Chart → Chart template
   - Diagram/flowchart → Diagrams template
   - Infographic → Infographics template
   - Org chart → Org Charts template
   - Screenshot → Screenshots template
   - Table (as image) → Tables template
   - Photo/illustration → describe subject, setting, and mood in 2–3 sentences.
4. Set `content_type: [visual]`.
5. Set `confidence` based on how clearly the image content is readable:
   - Clear, high-resolution → 0.90–1.0
   - Moderate quality, readable → 0.70–0.89
   - Low quality or unclear → 0.50–0.69

---

## Tables

**Method**: Extract tables as standalone chunks, separate from surrounding text.

**When to apply**: Any table with ≥ 3 columns OR ≥ 5 rows.

**Rules**:

1. Create a dedicated chunk for the table with `content_type: [table]`.
2. In the chunk body, render the table as Markdown (`| col | col | col |`).
3. Extract key data points (max/min values, totals, notable rows) and list them
   in the frontmatter `entities.metrics` array.
4. If the table has a caption or header row, use it as the `narrative_theme`.
5. Reference the table in the parent text chunk's `figures` field:
   `"Table: {caption or description}. See chunk-{NNN}.md."`

---

## Large Documents (> 20 Pages)

**Progressive chunking with overlap**:

1. Chunk size: 4 pages (PDF) or 1 slide (PPTX) — same as standard.
2. Overlap: last page of chunk N is also the first page of chunk N+1.
3. For very long documents (> 100 pages), prioritize the first 20 pages and the
   last 10 pages for deep extraction. Middle sections may use lighter extraction
   (headings + metrics only, `confidence: 0.5`).
4. Always extract executive summary, conclusions, and any pages with large
   standalone figures regardless of their position.

**Hint in frontmatter**: Add `"overlap_with_prev": "{chunk_id}"` to any chunk
that was created with overlap to allow deduplication in pass 2.

---

## Chunk Naming

```
index/{source-name}/chunk-{NNN}.md
```

- `{source-name}` matches `_safe_source_name(path)` from `slide_learn.py`.
- `{NNN}` is zero-padded to 3 digits: `001`, `002`, `003`, ...
- Section summary chunks use the last slide number of the section:
  `chunk-{last-slide-NNN}-summary.md`.

---

## Summary Table

| Format | Split at | Target size | Overlap |
|---|---|---|---|
| PDF | Page boundaries (prefer headings) | 3–6 pages | 1 page for docs > 20 pages |
| PPTX | Per slide | 1 slide | None |
| DOCX | H1/H2 headings | 400–800 words | None |
| HTML | Slide divs | 1 div | None |
| Image | Whole file | 1 image | N/A |
| Table | Table element | 1 table | None |

---
name: Slide Learn
description: >
  Indexes source documents (PDF, PPTX, DOCX, HTML, images) into a structured
  chunk store. Two-pass pipeline: pass 1 extracts per-document chunks with YAML
  frontmatter; pass 2 synthesizes cross-document tags, relationships, and
  insights. The index is consumed by slide-outline, slide-generate, and
  slide-pipeline to ground slide content in source material.
triggers:
  - "index this document"
  - "learn from this deck"
  - "extract from this PDF"
  - "build an index of these files"
  - "index these files"
  - "learn from these documents"
  - "add to the index"
  - "update the index"
---

# Slide Learn

Converts source documents into a queryable chunk store that other skills can
search when building slides. The output lives under an `index/` directory
(configurable via `index_dirs` in slide-config) and is plain files — grep-able,
git-committable, human-readable.

## When to Use

- Before running slide-pipeline on a topic backed by internal documents.
- When a user says "learn from this deck", "index this PDF", or similar.
- When `slide-outline` needs source-grounded facts rather than model-only recall.
- When re-indexing after source documents are updated.

## Two-Pass Indexing

### Pass 1: Per-Document Extraction

For each document in the source directory (or a single `--doc` path):

1. **Detect type** — `pdf | pptx | docx | html | image` based on file extension.
2. **Chunk** — Split according to the rules in `chunk-strategy.md`. Each chunk
   is a logical unit (page range, slide, section, or whole image).
3. **Extract** — For text-based formats, extract text directly. For binary
   content (PDF images, PPTX slide screenshots, standalone images), describe
   content using the vision templates in `vision-templates.md`.
4. **Write chunks** — Each chunk is a Markdown file under
   `index/{source-name}/chunk-NNN.md` with YAML frontmatter matching the schema
   in `index-schema.md`.

Pass 1 output for a source named `q3-review.pdf`:

```
index/
  q3-review.pdf/
    chunk-001.md
    chunk-002.md
    chunk-003.md
    ...
```

### Pass 2: Cross-Document Synthesis

After all documents are chunked, read every chunk's YAML frontmatter and
synthesize aggregated artifacts:

| Output file | Content |
|---|---|
| `index/_tags/{tag}.md` | All chunks that carry this tag, with source and snippet |
| `index/_relationships/systems.md` | Systems cross-referenced across documents |
| `index/_relationships/people.md` | People/roles cross-referenced across documents |
| `index/_insights/key-facts.md` | Top facts and figures with source attribution |
| `index/_insights/narrative-themes.md` | Recurring themes suitable for slide narratives |
| `index/_insights/gaps.md` | Topics mentioned but not elaborated — coverage gaps |
| `index/_manifest.json` | Freshness record: timestamps, doc count, chunk count |

Pass 2 is re-run whenever chunks change (tracked via `_manifest.json`).

## Invocation Examples

```
"Index this document" → learn(source_dir=".", single_doc="path/to/file.pdf")
"Learn from this deck" → learn(source_dir=".", single_doc="path/to/slides.pptx")
"Extract from this PDF" → learn(source_dir=".", single_doc="path/to/report.pdf")
"Build an index of these files" → learn(source_dir="/path/to/docs/")
"Update the index" → learn(source_dir=config["index_dirs"][0])
```

## Workflow

```
detect doc type
    │
    ├─ pdf  → page-based chunking (3-6 pages) → text extraction + vision for embedded images
    ├─ pptx → per-slide chunking + section summaries → vision description per slide
    ├─ docx → section-heading chunking (H1/H2, 400-800 words) → text extraction
    ├─ html → per-slide div → structured content extraction
    └─ image → single chunk → full vision description
         │
         ▼
    write chunks with YAML frontmatter → index/{source-name}/chunk-NNN.md
         │
         ▼
    cross-doc synthesis
         │
         ├─ aggregate tags → index/_tags/
         ├─ extract relationships → index/_relationships/
         ├─ surface insights → index/_insights/
         └─ update manifest → index/_manifest.json
```

## Generated Output Structure

```
index/
  _manifest.json               — freshness record, document list, chunk counts
  _tags/
    financial.md               — all chunks tagged "financial"
    systems.md                 — all chunks tagged "systems"
    ...
  _relationships/
    systems.md                 — system names cross-referenced across docs
    people.md                  — people/roles cross-referenced across docs
  _insights/
    key-facts.md               — top facts with source attribution
    narrative-themes.md        — recurring themes for slide narratives
    gaps.md                    — coverage gaps (mentioned but not elaborated)
  .cache/
    {source-name}.hash         — content hash for change detection
  {source-name}/               — one directory per source document
    chunk-001.md
    chunk-002.md
    ...
```

## Configuration

`index_dirs` is an array key in slide-config (project-level). If set, the
pipeline will automatically read `_insights/` before building outlines.

```bash
python skills/slide-config/scripts/slide_config.py set index_dirs /path/to/docs
```

Multiple directories are comma-separated. The first entry is the default target
for new indexing runs.

## Integration with Other Skills

See `integration.md` for the full consumption protocol. Short summary:

- **slide-outline**: queries `_insights/key-facts.md` and `_tags/` to ground
  outline bullets in source material. Adds `source_chunks` to outline JSON.
- **slide-generate**: enriches slide content with indexed facts and figures.
- **slide-pipeline**: checks `index_dirs` at start; reads `_insights/` if set.

## Reference Files

| File | Read when... |
|---|---|
| [references/index-schema.md](references/index-schema.md) | Writing or validating chunk YAML frontmatter |
| [references/chunk-strategy.md](references/chunk-strategy.md) | Deciding how to split a document into chunks |
| [references/vision-templates.md](references/vision-templates.md) | Writing standardized descriptions for charts, diagrams, images |
| [references/search-patterns.md](references/search-patterns.md) | Querying the index to find relevant chunks |
| [references/integration.md](references/integration.md) | Wiring the index into slide-outline, slide-generate, or slide-pipeline |

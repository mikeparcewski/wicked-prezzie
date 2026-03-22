# Word Export — Formatting Conventions and Customization

Reference for the `exec_summary_export.py` script that converts exec-summary
markdown files to formatted Word (.docx) documents.

---

## When to Use

Export to Word **after** the executive summary has been approved and **before**
distributing for team review. The Word format is useful when:

- Stakeholders need to add tracked-changes comments
- The summary must be attached to an email or uploaded to a document portal
- Print formatting matters (page breaks, margins, headers)
- A draft watermark is needed for internal circulation

The Word export is a one-way snapshot. Edits should flow back into the source
`exec-summary.md`, not the other way around. If the summary is revised after
export, re-run the export to produce an updated .docx.

---

## Document Structure

The exported Word document contains:

1. **Title page** — Deck title centered with accent line and "Executive Summary"
   subtitle.
2. **Table of contents** — Field-based TOC that populates when opened in Word
   (right-click > Update Field). Covers headings at levels 1-3.
3. **Section content** — Each of the 8 exec-summary sections rendered as Heading 1
   with body text, bullet lists, and numbered lists preserved.

---

## Typography

| Element | Font | Size | Color |
|---------|------|------|-------|
| Body text | Calibri | 11pt | #1A1A1A |
| Heading 1 | Calibri Bold | 22pt | #1A1A2E (dark navy) |
| Heading 2 | Calibri Bold | 16pt | #1A1A2E |
| Heading 3 | Calibri Bold | 13pt | #1A1A2E |
| Title page title | Calibri Bold | 32pt | #1A1A2E |
| Inline code | Consolas | 10pt | #404040 |
| Page numbers | Calibri | 9pt | #808080 |

---

## Page Layout

- **Paper size**: US Letter (8.5 x 11 inches)
- **Margins**: 1" top/bottom, 1.25" left/right
- **Line spacing**: 16pt for body paragraphs
- **Paragraph spacing**: 6pt after body, 2pt after list items

---

## Markdown Support

The exporter handles these markdown constructs:

- **Headings** (# through ######) — mapped to Word heading styles
- **Bold** (`**text**`) — rendered as bold run
- **Italic** (`*text*`) — rendered as italic run
- **Bold-italic** (`***text***`) — rendered as bold + italic run
- **Inline code** (`` `text` ``) — rendered in Consolas with gray color
- **Bullet lists** (`- item` or `* item`) — Word "List Bullet" style
- **Numbered lists** (`1. item`) — Word "List Number" style
- **Horizontal rules** (`---`) — skipped (section separation handled by headings)

Not supported (intentionally excluded for a professional document):
- Images and links (not relevant to exec-summary content)
- Tables (exec-summary sections are prose, not tabular)
- Code blocks (no fenced code in exec-summary content)

---

## Draft Watermark

The `--draft` flag adds a diagonal "DRAFT — For Review" watermark to every page.
The watermark is rendered as a VML text shape in the document header with 30%
opacity in gray (#C0C0C0). It appears behind all content.

Use the draft watermark when:
- Circulating for internal review before final approval
- Sharing with a subset of stakeholders for early feedback
- The summary has been approved but slides are not yet built

Remove the watermark by re-exporting without `--draft` when the document is
ready for final distribution.

---

## Customization

### Changing Colors

Edit the constants at the top of `exec_summary_export.py`:

```python
HEADING_COLOR = RGBColor(0x1A, 0x1A, 0x2E)  # Dark navy
ACCENT_COLOR = RGBColor(0x2E, 0x5C, 0x8A)   # Steel blue
```

### Changing Fonts

Update `FONT_NAME` and the size constants:

```python
FONT_NAME = "Calibri"
BODY_SIZE = Pt(11)
H1_SIZE = Pt(22)
```

### Changing Page Layout

Modify the page setup block in `export_exec_summary()`. The values use
`docx.shared.Inches` for margins and page dimensions.

### Programmatic Use

The export function can be called directly from other skills:

```python
from exec_summary_export import export_exec_summary

path = export_exec_summary(
    md_path="state/exec-summary.md",
    output_path_str="deliverables/exec-summary.docx",
    title="Project Alpha — Executive Summary",
    draft=True,
)
```

---

## Dependencies

- `python-docx` — Word document generation (already in project dependencies)
- No other external dependencies required

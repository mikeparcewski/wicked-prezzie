---
name: presenter-pdf
description: |
  Generates a clean slides-only PDF at exact PPT widescreen dimensions via Chrome
  headless print. For sharing or printing without notes.

  Use when: "export PDF", "print slides", "PDF version", "share as PDF",
  "slides to PDF", "printable version"
---

# PDF Export

Generates a clean, slides-only PDF from HTML slide files using Chrome headless
print-to-PDF. Each page is rendered at exact PowerPoint widescreen dimensions
(16:9 aspect ratio). No speaker notes, no navigation chrome, no build
artifacts — just clean slides ready for sharing or printing.

---

## When to Use

- User wants to share slides without giving away the editable source
- User needs a printable version of the deck
- User wants a PDF for email attachment or file sharing
- Before a meeting where slides will be projected from PDF
- User explicitly asks for "PDF" or "print"

---

## Page Dimensions

Each slide is rendered as one PDF page at exact PPT widescreen dimensions:

| Property | Value |
|----------|-------|
| Page width | 1280 px (CSS) / 960 pt (PDF) |
| Page height | 720 px (CSS) / 540 pt (PDF) |
| Aspect ratio | 16:9 |
| Margins | 0 (edge to edge) |
| Scale | 1:1 with Chrome viewport |

These dimensions match PowerPoint's default widescreen layout. When printed
on A4 or Letter paper, the slide content scales proportionally with margins.

---

## Rendering Pipeline

```
HTML slides → Chrome headless print-to-PDF → Individual PDFs → pypdf merge → Final PDF
     │                    │                        │                │
     │              @page CSS injection      One PDF per slide    Ordered merge
     │              Remove nav/scripts       Exact 16:9 dims     Single output
     │              Resolve file:// paths
     └──────────────────────────────────────────────────────────────────────────┘
```

### Step 1: Prepare Each Slide

For each slide HTML file:
1. Read the HTML content
2. Inject `@page` CSS rule: `@page { size: 1280px 720px; margin: 0; }`
3. Resolve all CSS `url()` and `<link>` paths to absolute `file://` URIs
4. Remove `<nav>`, `<script>`, and any elements with `data-no-print` attribute
5. Strip CSS animations and transitions (static snapshot)
6. Write a temporary prepared HTML file

### Step 2: Chrome Headless Print

For each prepared slide:
```bash
chrome --headless --disable-gpu \
  --print-to-pdf=slide-001.pdf \
  --no-pdf-header-footer \
  --print-to-pdf-no-header \
  file:///tmp/prepared-slide-001.html
```

Chrome path resolution follows the same logic as `chrome-extract`:
- macOS: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- Linux: `google-chrome` or `chromium-browser` on PATH
- Windows: `C:\Program Files\Google\Chrome\Application\chrome.exe`

### Step 3: Merge PDFs

Individual slide PDFs are merged in order using pypdf:

```python
from pypdf import PdfWriter

writer = PdfWriter()
for pdf_path in sorted(slide_pdfs):
    writer.append(pdf_path)
writer.write(output_path)
```

---

## Slide Ordering

Same ordering logic as presenter-html:
1. `slides.json` manifest if it exists
2. Alphabetical filename sort (numeric prefixes)
3. `--subset` flag for partial export

---

## Usage

```bash
# Export all slides to PDF
python ${CLAUDE_SKILL_DIR}/scripts/build_presenter_pdf.py \
  --slides-dir ./slides \
  --output deck.pdf

# Export specific slides
python ${CLAUDE_SKILL_DIR}/scripts/build_presenter_pdf.py \
  --slides-dir ./slides \
  --subset 1,2,3,7,12 \
  --output highlights.pdf

# Custom output directory
python ${CLAUDE_SKILL_DIR}/scripts/build_presenter_pdf.py \
  --slides-dir ./slides \
  --output ~/.something-wicked/wicked-prezzie/output/deck.pdf
```

---

## Dependencies

| Package | Purpose | Install |
|---------|---------|---------|
| pypdf | PDF merging | `pip install pypdf` |
| Google Chrome | Headless PDF rendering | Already required by chrome-extract |

No Pillow, no LibreOffice, no poppler. Chrome does the rendering directly
to PDF.

---

## Integration with Other Skills

### Reads From

| Skill | What | Why |
|-------|------|-----|
| generate | HTML slide files | Source content to render |
| outline | `outline.json` or `slides.json` | Slide ordering |
| theme | Theme CSS | Styling for slides |
| standardize | Normalized HTML | Clean input for Chrome |

### Produces For

| Skill | What | Why |
|-------|------|-----|
| convert | N/A — PDF is a delivery artifact | End of pipeline |
| checkpoint | Export status | Session state tracking |

---

## Comparison with Other Export Formats

| Format | Editable | Notes | Animations | Dependencies |
|--------|----------|-------|------------|-------------|
| PPTX (convert) | Yes | In speaker notes | No (stripped) | python-pptx, Chrome, LibreOffice |
| PDF (this skill) | No | No | No (stripped) | Chrome, pypdf |
| HTML (presenter-html) | View only | Three-tab panel | Yes (preserved) | None |

Choose PDF when the recipient should not edit, does not need notes, and you
want universal compatibility.

---

## Limitations

- No speaker notes — this is intentional. PDF export is for clean sharing.
  Use presenter-html for a notes-enabled format.
- No animations — Chrome captures a static snapshot. CSS transitions and
  keyframe animations are stripped.
- No incremental builds — every export re-renders all slides (or the subset).
  Caching is not implemented because Chrome print-to-PDF is fast enough for
  typical deck sizes (< 30 slides).
- Fonts must be installed locally — Chrome uses system fonts. If the theme
  specifies a font not installed on the build machine, Chrome falls back to
  its default serif/sans-serif.

---

## How Claude Should Use This Skill

1. **Confirm the purpose** — if the user says "export", ask whether they want
   PPTX (editable), PDF (sharing), or HTML (presenting). Do not assume PDF.
2. **Check slide quality first** — if the slides have not been validated, suggest
   running validate before exporting. A PDF locks in any defects.
3. **Verify Chrome is available** — if Chrome is not found, report the error
   clearly. Do not fall back to a different rendering engine.
4. **Report the output path** — after building, tell the user exactly where
   the PDF was written and its file size.

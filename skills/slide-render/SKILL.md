---
name: slide-render
description: |
  Renders PPTX slides to PNG images via LibreOffice headless, with optional
  contact sheet montage. Also used by the validation and comparison workflows.

  Use when: "show me the slides", "what does it look like", "preview the PPTX",
  "create thumbnails", "export slides as images", "render to PNG", "screenshot slides"
---

# Slide Render

Render PowerPoint (.pptx) files into PNG images for visual review, comparison,
and quality assurance. Converts slide decks into individual per-slide PNGs and
optional contact-sheet montages using LibreOffice headless PDF export.

## When to Use

- Convert a .pptx file into PNG images for visual inspection
- Generate slide thumbnails at a specific DPI
- Create a contact sheet (montage) tiling all slides into one overview image
- Rasterize a subset of slides for targeted comparison
- Produce PNG output for the slide-compare visual diff workflow
- Verify that a generated PPTX renders correctly before delivering

## Usage

```bash
# Render all slides to PNG
python ${CLAUDE_SKILL_DIR}/scripts/slide_render.py deck.pptx -o ./renders/

# Render specific slides at high DPI
python ${CLAUDE_SKILL_DIR}/scripts/slide_render.py deck.pptx --slides 1,5,10 --dpi 300

# Create a contact sheet montage
python ${CLAUDE_SKILL_DIR}/scripts/slide_render.py deck.pptx --montage montage.png

# Custom montage grid
python ${CLAUDE_SKILL_DIR}/scripts/slide_render.py deck.pptx --montage overview.png --cols 3 --thumb-width 640
```

### Options

| Flag | Default | Description |
|---|---|---|
| `-o`, `--output-dir` | `./slide-renders/` | Directory for per-slide PNG output |
| `--dpi` | `150` | Resolution for rasterization |
| `--slides` | all | Comma-separated 1-based slide numbers |
| `--montage` | none | Path for contact-sheet output image |
| `--cols` | `4` | Number of columns in montage grid |
| `--thumb-width` | `480` | Thumbnail width in pixels for montage |

## How Rendering Works

### Stage 1: PPTX to PDF

LibreOffice headless exports the .pptx to PDF:

```bash
soffice --headless --convert-to pdf --outdir <tmpdir> <pptx_path>
```

Runs without GUI, permission dialogs, or automation consent. Handles sandboxed
macOS environments automatically by detecting and using the correct binary path.

### Stage 2: PDF to PNG

`pdftoppm` from Poppler splits the PDF into individual page images:

```
pdftoppm -png -r <dpi> <pdf_path> <output_prefix>
```

150 DPI for screen review, 300 DPI for print-quality comparison. Output files
are named `slide-01.png`, `slide-02.png`, etc.

### Montage

Loads all rendered PNGs, resizes to thumbnail width (preserving aspect ratio),
tiles into a grid using Pillow. White background, configurable columns.

## Dependencies

- **LibreOffice** (macOS: `brew install --cask libreoffice`, Linux: `apt install libreoffice`)
- **pdftoppm** from poppler (macOS: `brew install poppler`, Linux: `apt install poppler-utils`)
- **Pillow** (for montage creation)

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| PDF export fails | LibreOffice not installed or not in PATH | Install LibreOffice; check `soffice --version` |
| pdftoppm not found | Poppler not installed | macOS: `brew install poppler` |
| Missing fonts in render | Fonts not on system | Install .ttf/.otf to system fonts dir |
| Montage too large | Too many slides / high thumb width | Reduce `--thumb-width` or increase `--cols` |

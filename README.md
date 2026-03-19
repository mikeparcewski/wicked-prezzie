# wicked-prezzie

HTML slides to editable PowerPoint. Native shapes and formatted text, not screenshots.

A Claude Code plugin that handles the full presentation lifecycle — plan content, generate themed slides, convert existing HTML, validate output, and iterate until it matches.

## Quick start

```bash
git clone https://github.com/mikeparcewski/wicked-prezzie.git
cd wicked-prezzie
claude
```

That's it. Claude discovers all 13 skills automatically. Then just talk to it:

```
"Make me a presentation about our Q1 results"
"Convert the HTML slides in my-deck/ to PowerPoint"
"Use our brand — navy and gold, dark background"
"Check my deck for layout issues"
```

## What it does

**Plan** — Structure content using the Pyramid Principle. One message per slide, narrative arc, speaker notes.

**Generate** — Turn outlines into themed HTML with proper typography, whitespace, and contrast. Eight slide types, three built-in themes, or extract a theme from your existing brand assets.

**Convert** — Chrome headless extracts every element's computed position, color, and formatting. The builder maps that to native PPTX shapes. Slides extract in parallel (~8s for a 10-slide deck).

**Validate** — Five-category deck audit (structure, content, layout, consistency, lint) with automatic remediation. Visual diff compares HTML source against PPTX output.

Works with HTML from anywhere — ChatGPT, Claude, Gemini, reveal.js, or hand-coded.

## How it works

```
Topic → slide-outline → slide-generate → standardize → chrome-extract → pptx-builder → validate
         Pyramid         themed HTML       fix viewport    Chrome headless   native PPTX     5-category
         Principle        + images          strip anim      bounding boxes    shapes+text     deck audit
```

Each stage is independent. Jump in anywhere — bring your own HTML, start from an outline, or go from a blank page.

**[Pipeline architecture →](PIPELINE.md)** · **[Use cases & examples →](USE-CASES.md)**

## Prerequisites

```bash
pip install python-pptx beautifulsoup4 lxml Pillow
```

- **Google Chrome** — headless layout extraction
- **LibreOffice** — PPTX rendering (`brew install --cask libreoffice` / `apt install libreoffice`)
- **poppler** — PDF to PNG (`brew install poppler` / `apt install poppler-utils`)

Missing dependencies are auto-detected and installed on first run.

## Themes

Three built-in. Create your own. Extract from existing PPTX, PDF, or brand guides. Share via `.pptprofile` files.

| Theme | Background | Primary | Accent |
|---|---|---|---|
| midnight-purple | `#0A0A0F` | `#A100FF` | amber |
| corporate-light | white | `#1E3A5F` | teal |
| warm-dark | `#1A1A2E` | `#FF6B6B` | gold |

```
"Learn my brand from ./assets/brand-guide.pdf"
"Describe a vibe — clean, minimal, executive"
"Export my theme to share with the team"
```

## Known tradeoffs

- Gradients become solid blended colors (PPTX gradient support is limited)
- Animations are stripped (static snapshot of the final state)
- Font metrics differ between CSS and Calibri (compensated, not perfect)
- Small decorative SVGs under 30px are skipped

## Project layout

```
skills/
  slide-outline/           Topic → structured outline
  slide-generate/          Outline → themed HTML slides
  slide-theme/             Brand palettes, fonts, profiles
  slide-html-standardize/  Normalize AI-generated HTML
  chrome-extract/          Chrome headless → layout JSON
  slide-pptx-builder/      Layout JSON → native PPTX
  slide-html-to-pptx/      Parallel batch conversion
  slide-validate/          Quality scoring, audit, lint
  slide-render/            PPTX → PNG rendering
  slide-compare/           HTML vs PPTX visual diff
  slide-pipeline/          End-to-end orchestrator
  slide-design/            Design principles (reference)
  slide-config/            Project + user settings
```

## License

MIT

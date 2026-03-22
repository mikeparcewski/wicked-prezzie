# wicked-prezzie

HTML slides to editable PowerPoint. Native shapes and formatted text, not screenshots.

A Claude Code / Gemini CLI plugin that handles the full presentation lifecycle — index source documents, plan content with structured brainstorming, generate themed slides, convert HTML to native PPTX, validate output, iterate until it matches, and analyze team feedback from Word review comments.

## Quick start

### Claude Code

```bash
git clone https://github.com/mikeparcewski/wicked-prezzie.git
cd wicked-prezzie
claude
```

Claude discovers all skills automatically.

### Gemini CLI

```bash
git clone https://github.com/mikeparcewski/wicked-prezzie.git
cd wicked-prezzie
gemini
```

Gemini uses the same skills with its own tool names (see [GEMINI.md](GEMINI.md) for the mapping).

### Prerequisites

```bash
pip install python-pptx beautifulsoup4 lxml Pillow
```

- **Google Chrome** — headless layout extraction
- **LibreOffice** — PPTX rendering (`brew install --cask libreoffice` / `apt install libreoffice`)
- **poppler** — PDF to PNG (`brew install poppler` / `apt install poppler-utils`)

Missing dependencies are auto-detected on first run.

21 skills cover the full pipeline. Just talk to it:

```
"Make me a presentation about our Q1 results"
"Convert the HTML slides in my-deck/ to PowerPoint"
"Use our brand — navy and gold, dark background"
"Check my deck for layout issues"
"Index the RFP documents in ./source-materials/"
"Run a brainstorm for the client deck — use dreamer-skeptic teams"
"Analyze the team's feedback comments from the Word doc"
```

## What it does

**Plan** — Structure content using the Pyramid Principle. One message per slide, narrative arc, speaker notes.

**Generate** — Turn outlines into themed HTML with proper typography, whitespace, and contrast. Eight slide types, three built-in themes, or extract a theme from your existing brand assets.

**Convert** — Chrome headless extracts every element's computed position, color, and formatting. The builder maps that to native PPTX shapes. Slides extract in parallel (~8s for a 10-slide deck).

**Validate** — Five-category deck audit (structure, content, layout, consistency, lint) with automatic remediation. Visual diff compares HTML source against PPTX output.

**Learn** — Index source documents (PDFs, PPTX, DOCX, images) into searchable markdown with YAML frontmatter. Two-pass architecture: per-document extraction with vision, then cross-document synthesis of themes, relationships, and key facts.

**Orchestrate** — Full deck-building methodology with dreamer-skeptic brainstorming, generative persona validation, constraint persistence, and phased gate reviews. Hub-and-spoke architecture with section-based grouping keeps context lean across long sessions.

**Analyze feedback** — Parse inline comments from Word documents reviewed by your team. Detect where reviewers align, where they diverge, and what it means for the narrative. Generate prioritized action items as markdown or a Word report to share back.

Works with HTML from anywhere — ChatGPT, Claude, Gemini, reveal.js, or hand-coded.

## How it works

```
Topic → slide-outline → slide-generate → standardize → chrome-extract → pptx-builder → validate
         Pyramid         themed HTML       fix viewport    Chrome headless   native PPTX     5-category
         Principle        + images          strip anim      bounding boxes    shapes+text     deck audit
```

Each stage is independent. Jump in anywhere — bring your own HTML, start from an outline, or go from a blank page.

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
  slide-outline/           Topic → structured outline (Pyramid Principle)
  slide-generate/          Outline → themed HTML slides (8 types, images)
  slide-theme/             Brand palettes, fonts, profiles, vibe matching
  slide-html-standardize/  Normalize AI-generated HTML + complexity routing
  chrome-extract/          Chrome headless → layout JSON + screenshots
  slide-triage/            Confidence scoring + known-pattern detection
  slide-prep/              Auto-resolve findings → build manifests
  slide-pptx-builder/      Layout JSON → native PPTX shapes + text
  slide-html-to-pptx/      Parallel batch conversion
  slide-validate/          5-category deck audit, content lint, consistency
  slide-render/            PPTX → PNG rendering (LibreOffice headless)
  slide-compare/           HTML vs PPTX visual diff
  slide-pipeline/          End-to-end conversion orchestrator
  slide-treatment-log/     Per-slide fix history + pattern promotion
  slide-design/            Design principles + quality rubric (reference)
  slide-config/            Project + user settings
  slide-learn/             Source document indexing (two-pass, vision)
  deck-pipeline/           Full deck orchestrator (8-phase methodology)
  deck-brainstorm/         Dreamer-skeptic teams + generative personas
  deck-checkpoint/         Session synthesis: decisions, artifacts, next steps
  deck-feedback/           Word comment parsing → alignment/divergence report
```

## Documentation

- **[Pipeline architecture](PIPELINE.md)** — Stage-by-stage technical breakdown with Mermaid diagram
- **[Use cases & examples](USE-CASES.md)** — Practical paths from simplest to most involved
- **[How it works](ARCHITECTURE.md)** — Technical deep-dive: extraction, building, triage, indexing
- **[Gemini CLI](GEMINI.md)** — Tool name mapping for Gemini users

## License

MIT

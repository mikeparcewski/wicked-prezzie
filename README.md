# wicked-prezzie

HTML slide decks to editable PowerPoint, powered by Claude Code skills.

Give it a topic, a set of bullet points, or AI-generated HTML slides and get back a native `.pptx` with real shapes, formatted text, and accurate positioning. Not screenshots pasted onto slides.

## What it does

```
Topic or brief
    |
    v
slide-outline          Structure content using the Pyramid Principle
    |
    v
slide-generate         Produce themed HTML slide files
    |
    v
slide-html-standardize Normalize viewport, wrappers, strip animations
    |
    v
chrome-extract         Chrome headless extracts computed layout as JSON
    |
    v
slide-pptx-builder     Map layout JSON to native PPTX shapes + richtext
    |
    v
slide-validate         Score output against a 100-point quality rubric
    |
    v
slide-render           PPTX to PNG via PowerPoint for visual review
    |
    v
slide-compare          Side-by-side HTML vs PPTX fidelity check
```

Each stage is a standalone Claude Code skill with its own `SKILL.md`, scripts, and reference docs. You can run the full pipeline or any stage independently.

## Quick start

### Prerequisites

```bash
pip install python-pptx beautifulsoup4 lxml Pillow
brew install poppler                    # for pdftoppm (PDF to PNG)
```

You also need:
- **Google Chrome** (for headless layout extraction)
- **Microsoft PowerPoint** (for high-fidelity PPTX rendering to PDF)

### Convert HTML slides to PowerPoint

The most common workflow. Point the pipeline at a directory of HTML files:

```bash
python slide-pipeline/scripts/slide_pipeline.py \
  --input-dir ./slides \
  --output deck.pptx
```

This runs all five stages: standardize, convert, validate, render, compare.

### Convert without QA (just the PPTX)

```bash
python slide-html-to-pptx/scripts/html_to_pptx.py \
  --input-dir ./slides \
  --output deck.pptx
```

### Start from a topic

Ask Claude to plan and generate slides from scratch:

```
"Make me a 10-slide presentation about AI-powered analytics for the board"
```

Claude will use `slide-outline` to structure the narrative, `slide-theme` to apply brand colors, and `slide-generate` to produce the HTML files before converting.

## Skills

### Content creation

| Skill | What it does |
|---|---|
| **slide-theme** | Define brand colors, fonts, spacing as reusable theme JSON. Ships with 3 built-in themes. |
| **slide-outline** | Structure a topic into a presentation outline using the Pyramid Principle. Produces JSON consumed by slide-generate. |
| **slide-generate** | Turn an outline into individual themed HTML slide files. 8 slide types: title, content, stats, comparison, quote, section divider, CTA, blank. |

### Conversion

| Skill | What it does |
|---|---|
| **slide-html-standardize** | Normalize AI-generated HTML: add viewport meta, wrap in `.slide` div, strip CSS animations, remove external CDN dependencies. |
| **chrome-extract** | Drive Chrome headless to render HTML and extract computed bounding boxes, colors, fonts, and inline formatting as structured JSON. |
| **slide-pptx-builder** | Convert layout JSON into native PPTX shapes, richtext boxes, and embedded SVG screenshots at pixel-mapped positions. Includes bundled color utilities for CSS-to-PPTX alpha blending. |
| **slide-html-to-pptx** | Orchestrate the conversion stage: Chrome extraction + PPTX building + screenshot fallback for failed slides. |

### Quality assurance

| Skill | What it does |
|---|---|
| **slide-validate** | Post-conversion QA: bounds checking, text overflow estimation, visual overflow detection (pad+render+check), 100-point scoring per slide. |
| **slide-render** | Render PPTX to PNG via PowerPoint PDF export + pdftoppm. Contact-sheet montage generation. |
| **slide-compare** | Generate paired HTML/PPTX screenshots for side-by-side fidelity review. |
| **slide-design** | Reference-only skill with design principles and quality rubric. Consulted by other skills for typography, color, and layout rules. |

### Configuration

| Skill | What it does |
|---|---|
| **slide-pipeline** | End-to-end orchestrator chaining all stages. The default entry point for conversion requests. |
| **slide-config** | Project-level settings: quality threshold, viewport dimensions, hide selectors, default font. Persists in `config.json`. |

## How conversion works

1. **Chrome does the layout.** Every HTML slide is rendered in Chrome headless at 1280x720. JavaScript walks the DOM and extracts computed bounding boxes, background colors, fonts, and inline text formatting as structured JSON.

2. **Native shapes, not screenshots.** Headings, paragraphs, cards, and containers become real PPTX text boxes and shapes. Text is editable. Colors are accurate. Positions are pixel-mapped from CSS coordinates to PowerPoint EMU units.

3. **Alpha blending.** CSS `rgba()` transparency is pre-blended against the slide background since PPTX doesn't support CSS-style opacity on shape fills. `rgba(161,0,255,0.06)` on a `#0A0A0F` background becomes `#13091D`.

4. **Richtext preservation.** Inline formatting within `h1`/`h2`/`h3`/`p` elements is preserved as multi-run text boxes. A heading with mixed colors and bold spans stays as one text box with formatted runs, not separate overlapping shapes.

5. **Fallback safety.** If extraction fails for a slide (malformed HTML, Chrome crash), a full-page screenshot is placed as an image instead. The deck always builds.

## Pipeline options

```bash
python slide-pipeline/scripts/slide_pipeline.py \
  --input-dir ./slides \
  --output deck.pptx \
  --viewport 1920x1080 \          # Custom viewport (default: 1280x720)
  --hide ".nav,.footer" \          # CSS selectors to hide during extraction
  --no-standardize \               # Skip if HTML is already clean
  --no-validate \                  # Skip quality scoring
  --no-render \                    # Skip PPTX to PNG
  --no-compare \                   # Skip HTML vs PPTX comparison
  --visual-overflow \              # Pixel-level overflow detection
  --montage montage.png \          # Contact sheet of all slides
  --slides slide-01.html,slide-03.html  # Process specific files only
```

## Themes

Three built-in themes in `slide-theme/themes/`:

- **midnight-purple** (default) - Dark bg `#0A0A0F`, purple primary `#A100FF`, amber accent
- **corporate-light** - White bg, navy primary `#1E3A5F`, teal accent
- **warm-dark** - Charcoal bg `#1A1A2E`, coral primary `#FF6B6B`, gold accent

Create your own:

```bash
python slide-theme/scripts/slide_theme.py create my-brand
python slide-theme/scripts/slide_theme.py activate my-brand
```

Or tell Claude: "Use our brand colors: primary #2563EB, accent #F59E0B, dark background."

## Validation

Every slide is scored on a 100-point rubric:

| Check | Deduction |
|---|---|
| Shape extends past slide edge | -10 |
| Visual overflow (pixel-level) | -10 |
| Empty slide | -15 |
| Text overflow estimate | -3 |

Slides below 75 are flagged. The overall deck score is the average.

```bash
# Fast static check
python slide-validate/scripts/slide_validate.py deck.pptx

# With pixel-level overflow detection
python slide-validate/scripts/slide_validate.py deck.pptx --render
```

## Project structure

```
wicked-prezzie/
  slide-theme/               Brand/style definitions
  slide-outline/             Topic to structured outline
  slide-generate/            Outline to themed HTML slides
  slide-html-standardize/    Normalize AI-generated HTML
  chrome-extract/            Chrome headless layout extraction
  slide-pptx-builder/        Layout JSON to native PPTX shapes
  slide-html-to-pptx/        Batch HTML to PPTX conversion
  slide-validate/            Post-conversion quality assurance
  slide-render/              PPTX to PNG rendering
  slide-compare/             HTML vs PPTX visual comparison
  slide-design/              Design principles (reference only)
  slide-pipeline/            End-to-end orchestrator
  slide-config/              Project settings
  tests/                     Test fixtures and trigger evals
```

Each skill directory contains:
- `SKILL.md` - Skill metadata, instructions, and documentation
- `scripts/` - Python scripts for the skill's functionality
- `references/` - Additional docs loaded on demand

## Known limitations

- Gradient backgrounds are approximated with solid blended colors
- CSS animations and transitions are stripped (static snapshot only)
- Font metrics differ between CSS and Calibri (compensated with width multipliers)
- Small decorative SVGs under 60px are skipped
- Requires Google Chrome and Microsoft PowerPoint installed locally

## Using with Claude Code

This project is designed as a set of Claude Code skills. Clone the repo, open it in Claude Code, and Claude will automatically pick up the skills from each `SKILL.md` file.

```bash
git clone https://github.com/mikeparcewski/wicked-prezzie.git
cd wicked-prezzie
claude
```

Then just tell Claude what you need:

- "Make me a presentation about Q1 results"
- "Convert the HTML slides in my-deck/ to PowerPoint"
- "Check my deck for layout issues"
- "Show me what the slides look like"

# wicked-prezzie

**Your HTML slides deserve better than screenshots glued to PowerPoint.**

wicked-prezzie takes HTML slide decks and converts them into *actually editable* PowerPoint files. Real shapes. Real text boxes. Real formatting. The kind of `.pptx` where your boss can change the title without calling IT.

It's also a Claude Code plugin, so you can just *tell it what you want*.

---

## The 30-second version

```
"Hey Claude, make me a board deck about AI-powered analytics.
 Use our brand colors. Make it look sharp."
```

That's it. Claude plans the narrative, generates themed HTML slides, runs them through Chrome headless to extract pixel-perfect layout data, builds native PPTX shapes, validates the output, and hands you a polished deck. If a slide looks off, it tells you which ones and why.

## Or bring your own HTML

Already have slides from ChatGPT, Claude, Gemini, or your own tooling?

```bash
python skills/slide-pipeline/scripts/slide_pipeline.py \
  --input-dir ./my-slides \
  --output deck.pptx
```

Five stages run automatically: **standardize** (clean up AI quirks) **convert** (Chrome extraction + PPTX building) **validate** (quality scoring) **render** (PPTX to PNG) **compare** (side-by-side fidelity check).

---

## How it actually works

Most HTML-to-PPTX tools take a screenshot and call it a day. This one doesn't.

1. **Chrome does the hard part.** Each slide renders in Chrome headless at 1280x720. JavaScript walks the DOM and captures every element's computed position, color, font, and inline formatting as structured JSON.

2. **Shapes become shapes.** That JSON maps to native python-pptx objects. Headings are text boxes with formatted runs. Cards are rectangles with fills. SVG charts get cropped as images. Everything is editable in PowerPoint.

3. **Colors stay honest.** CSS `rgba(161,0,255,0.06)` on a dark background? That gets pre-blended to `#13091D` because PowerPoint doesn't do CSS-style transparency. The math is handled so the output matches what you see in the browser.

4. **If extraction fails, you still get a deck.** Bad HTML? Chrome crash? The fallback drops a full-page screenshot onto the slide. The deck always builds. Always.

---

## The pipeline

```
  Your topic          "AI reduced decision latency by 60%"
       |
  slide-outline       Pyramid Principle narrative structure
       |
  slide-generate      Themed HTML files (8 slide types)
       |
  slide-html-         Strip animations, fix viewports,
  standardize         remove CDN deps
       |
  chrome-extract      Headless Chrome -> layout JSON
       |
  slide-pptx-         JSON -> native PPTX shapes + richtext
  builder
       |
  slide-validate      100-point quality rubric per slide
       |
  slide-render        PPTX -> PNG via PowerPoint
       |
  slide-compare       HTML vs PPTX side-by-side
```

Every box is an independent skill. Run the full chain or pick the one you need.

---

## Install as a Claude Code plugin

```bash
git clone https://github.com/mikeparcewski/wicked-prezzie.git
cd wicked-prezzie
claude
```

Claude discovers all 13 skills automatically. Then just talk to it:

- *"Make me a presentation about Q1 results"*
- *"Convert the HTML slides in my-deck/ to PowerPoint"*
- *"The headings are wrapping weird in the PPTX"*
- *"Check my deck for layout issues"*
- *"Does the PowerPoint match the original HTML?"*
- *"Use our brand colors: navy primary, gold accent"*

---

## Themes

Three built-in, create your own, or let Claude extract one from your brand assets.

| Theme | Vibe |
|---|---|
| **midnight-purple** | Dark `#0A0A0F` + purple `#A100FF` + amber accent |
| **corporate-light** | Clean white + navy `#1E3A5F` + teal |
| **warm-dark** | Charcoal `#1A1A2E` + coral `#FF6B6B` + gold |

```bash
# Roll your own
python skills/slide-theme/scripts/slide_theme.py create my-brand
python skills/slide-theme/scripts/slide_theme.py activate my-brand
```

Or just: *"Use our brand colors: primary #2563EB, accent #F59E0B, dark background."*

---

## Quality gate

Every slide gets scored out of 100:

| What went wrong | Points lost |
|---|---|
| Shape bleeds past slide edge | -10 |
| Visual overflow (pixel check) | -10 |
| Empty slide | -15 |
| Text probably overflows its box | -3 |

Below 75? Flagged. The validator tells you *which* slides and *what's wrong* so you can fix and re-run.

```bash
# Quick check
python skills/slide-validate/scripts/slide_validate.py deck.pptx

# Pixel-level overflow detection (renders through PowerPoint)
python skills/slide-validate/scripts/slide_validate.py deck.pptx --render
```

---

## All the knobs

```bash
python skills/slide-pipeline/scripts/slide_pipeline.py \
  --input-dir ./slides \
  --output deck.pptx \
  --viewport 1920x1080 \          # Default: 1280x720
  --hide ".nav,.footer" \          # CSS selectors to hide
  --no-standardize \               # HTML already clean
  --no-validate \                  # Skip quality scoring
  --no-render \                    # Skip PNG output
  --no-compare \                   # Skip fidelity check
  --visual-overflow \              # Pixel-level overflow detection
  --montage montage.png \          # Contact sheet of all slides
  --slides slide-01.html,slide-03.html  # Just these ones
```

---

## Prerequisites

```bash
pip install python-pptx beautifulsoup4 lxml Pillow
brew install poppler    # pdftoppm for PDF->PNG
```

Plus:
- **Google Chrome** (headless layout extraction)
- **Microsoft PowerPoint** (the definitive renderer -- AppleScript on macOS, COM on Windows)

---

## Project layout

```
wicked-prezzie/
  .claude-plugin/              Plugin manifest
  skills/
    slide-theme/               Brand palettes + fonts
    slide-outline/             Pyramid Principle outlines
    slide-generate/            Outline -> themed HTML
    slide-html-standardize/    Clean up AI-generated HTML
    chrome-extract/            Chrome headless -> layout JSON
    slide-pptx-builder/        Layout JSON -> native PPTX
    slide-html-to-pptx/        Batch conversion orchestrator
    slide-validate/            Quality scoring + overflow detection
    slide-render/              PPTX -> PNG rendering
    slide-compare/             HTML vs PPTX visual diff
    slide-design/              Design principles (reference)
    slide-pipeline/            End-to-end orchestrator
    slide-config/              Project settings
  tests/                       Fixtures + trigger evals
```

---

## Known tradeoffs

These are deliberate, not bugs:

- **Gradients** become solid blended colors (PPTX gradient support is... limited)
- **Animations** are stripped (we capture the final state, not the journey)
- **Font metrics** differ between CSS and Calibri (compensated with width multipliers, but not perfect)
- **Small SVGs** under 60px are skipped (they're decorative noise that captures surrounding text)
- **You need Chrome and PowerPoint** installed locally (no way around the definitive renderers)

---

## License

MIT. Do whatever you want with it.

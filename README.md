# wicked-prezzie

**From blank page to polished PowerPoint. Or from messy HTML to clean PPTX. Or anything in between.**

wicked-prezzie is a Claude Code plugin that handles the entire presentation lifecycle — brainstorm an idea, build a branded deck, convert existing HTML slides, validate the output, and iterate until it's right. Every slide produces *native, editable* PowerPoint with real shapes and formatted text. Not screenshots. Not images. The real thing. Also renders to self-contained Reveal.js HTML for zero-install browser presentations.

---

## Three ways to use it

### 1. Ideation — start from nothing

Got a topic, a meeting, a vague idea? Just say what you need.

```
"I'm presenting to the board next week about our AI platform.
 15 minutes. They care about ROI and timeline. Help me plan it."
```

Claude structures your content using the **Pyramid Principle** — lead with the conclusion, group by argument, one message per slide. You get a narrative arc (setup → evidence → close) with speaker notes, not a pile of bullet points.

```
"Now generate the slides. Use our brand colors — navy and gold."
```

Themed HTML slides appear, ready for conversion. Each slide follows design principles: proper typography hierarchy, 30%+ whitespace, WCAG-compliant contrast, max 6-7 elements per slide.

### 2. Creation — build from content

Have bullet points, a doc, or talking points? Skip the blank page.

```
"Here are my Q4 results. Turn these into a deck."

"I have an outline.json — generate slides from it with the corporate-light theme."

"Create a stats slide with these three metrics: revenue $4.2M, growth 23%, retention 91%."
```

Eight slide types out of the box: **title, content, stats, comparison, quote, section divider, CTA, blank.** Each one follows the active theme's colors, fonts, and spacing. Images sourced from Unsplash or icon sets, with attribution handled automatically.

### 3. Migration — convert existing HTML

Already have slides from ChatGPT, Claude, Gemini, reveal.js, or your own tooling? Bring them.

```
"Convert the HTML slides in my-deck/ to PowerPoint."
```

The pipeline handles the ugly parts automatically:
- **Standardize** — fix viewports, add `.slide` wrappers, strip animations and CDN dependencies
- **Extract** — Chrome headless captures every element's computed position, color, and formatting
- **Build** — layout JSON maps to native PPTX shapes, richtext, and embedded SVG images
- **Validate** — 5-category deck audit (structure, content, layout, consistency, lint)
- **Render** — PPTX to PNG via PowerPoint for visual review
- **Compare** — side-by-side HTML vs PPTX fidelity check

Slides extract in **parallel** — one Chrome instance per slide, all concurrent. A 10-slide deck that took 30 seconds now takes ~8.

---

## What makes it different

**Native shapes, not screenshots.** Most HTML-to-PPTX tools paste an image and call it done. wicked-prezzie extracts every heading, paragraph, card, and container as a real PowerPoint object. Your boss can select the title and change it. As intended.

**Dual format output.** Same source HTML renders to both PPTX (editable in PowerPoint) and self-contained Reveal.js HTML (present from any browser, no install needed). Generate one, the other, or both.

**Parallel extraction.** Each slide gets its own Chrome headless process running concurrently. Screenshots are cached once — reused for SVG cropping and fallback slides. No duplicate Chrome launches.

**Quality gate built in.** Five-category deck audit scores structure, content, layout, consistency, and lint. Content lint catches bullet overload, missing titles, unformatted stats, unattributed quotes, and passive voice. Consistency checks catch palette drift, heading variance, and missing section dividers. Below 80? REVIEW. Below 60? FAIL.

**Three fidelity tiers.** `best` runs multi-pass verification loops — fix, re-render, re-validate. `draft` gives you a clean single pass. `rough` drops in structure fast for human polish later.

**Always builds.** Bad HTML? Chrome crash? Malformed CSS? The fallback drops a full-page screenshot onto the slide. You get a deck every time, even if some slides need manual attention.

**Brand-aware.** Themes aren't cosmetic — they drive the entire generation pipeline. Colors, fonts, spacing, contrast ratios. Three built-in themes, or extract one from existing PPTX, PDF, or brand assets. Profiles are portable — share `.pptprofile` files across teams. A git-backed design registry keeps palettes and strategies consistent across projects.

**Versioned output.** Every generation produces `{slug}_v{N}.pptx` — never overwrites. Track version history, diff between versions, and build from prior versions.

**REVIEW flags.** When the AI makes a judgment call or can't find source material, it flags the slide in speaker notes: `[REVIEW: reason]`. A summary slide lists all flags when count exceeds 3. Strict mode pauses for resolution instead of flagging.

---

## Install

```bash
git clone https://github.com/mikeparcewski/wicked-prezzie.git
cd wicked-prezzie
claude
```

Claude discovers all 13 skills automatically. Then talk to it:

- *"Make me a presentation about Q1 results"*
- *"I have bullet points — turn them into slides"*
- *"Convert the HTML in slides/ to PowerPoint"*
- *"Use our brand: primary #2563EB, accent #F59E0B, dark bg"*
- *"The headings are wrapping weird in the PPTX"*
- *"Check my deck for layout issues"*
- *"Does the PowerPoint match the original HTML?"*
- *"Show me what the slides look like"*
- *"Lower the quality threshold to 70 for this project"*

---

## The full pipeline

**[View pipeline architecture diagram →](PIPELINE.md)** | **[Browse use cases →](USE-CASES.md)**

> 13 independent skills across four stages: **Ideation** → **Creation** → **Migration** → **Quality**. Jump in at any stage — bring your own HTML, start from an outline, or go from blank page to polished deck.

---

## Themes & profiles

Three built-in. Create your own. Extract from existing assets. Share across projects.

| Theme | Vibe |
|---|---|
| **midnight-purple** | Dark `#0A0A0F` + purple `#A100FF` + amber accent |
| **corporate-light** | Clean white + navy `#1E3A5F` + teal |
| **warm-dark** | Charcoal `#1A1A2E` + coral `#FF6B6B` + gold |

```
"Learn my brand from ./assets/brand-guide.pdf and last-quarter.pptx"
"Describe a vibe — clean, minimal, executive"
"Export my theme as a .pptprofile to share with the team"
```

Themes live in `~/.something-wicked/wicked-prezzie/themes/` — shared across all your projects. Per-project overrides (active theme, viewport, quality threshold) stay in the project's `slide-config`.

Themes validate automatically — contrast ratios, palette size, font limits, size hierarchy.

---

## Quality gate

Two levels of validation — fast layout checks and comprehensive deck audit.

### Layout validation (fast)

| Issue | Deduction |
|---|---|
| Shape bleeds past slide edge | -10 |
| Visual overflow (pixel check) | -10 |
| Empty slide | -15 |
| Text overflow estimate | -3 |

### Deck audit (comprehensive)

| Category | Weight | Checks |
|---|---|---|
| Structure | 25% | Slide type fit, count, section cadence, opener/closer |
| Content | 30% | Bullet overload, title hygiene, stat formatting, quotes, CTAs |
| Layout | 20% | Bounds, overflow, element overlap |
| Consistency | 15% | Heading sizes, palette adherence, template distribution, speaker notes |
| Lint | 10% | Word count, passive voice, CTA verbs |

**PASS** ≥ 80 | **REVIEW** 60–79 | **FAIL** < 60

```
"Audit my deck"                    # Full 5-category audit with remediation
"Lint my deck"                     # Content quality only
"Check consistency"                # Within-deck or cross-deck comparison
"Compare sales-v1.pptx and v2"    # Cross-deck brand alignment
```

---

## Pipeline options

```bash
python skills/slide-pipeline/scripts/slide_pipeline.py \
  --input-dir ./slides \
  --output deck.pptx \
  --viewport 1920x1080 \          # Default: 1280x720
  --hide ".nav,.footer" \          # CSS selectors to hide
  --workers 8 \                    # Parallel Chrome instances
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
- **Google Chrome** — headless layout extraction
- **Microsoft PowerPoint** — the definitive renderer (AppleScript on macOS, COM on Windows)

---

## Project layout

```
wicked-prezzie/
  .claude-plugin/              Plugin manifest
  skills/
    slide-theme/               Brand palettes, fonts, style learning, profiles, registry
    slide-outline/             Pyramid Principle outlines
    slide-generate/            Outline → themed HTML + image sourcing
    slide-html-standardize/    Clean up AI-generated HTML
    chrome-extract/            Chrome headless → layout JSON
    slide-pptx-builder/        Layout JSON → native PPTX
    slide-html-to-pptx/        Parallel batch conversion
    slide-validate/            Quality scoring, audit, content lint, consistency
    slide-render/              PPTX → PNG rendering
    slide-compare/             HTML vs PPTX visual diff
    slide-design/              Design principles, CSS contract, hints (reference)
    slide-pipeline/            Orchestrator + fidelity, versioning, dual-format output
    slide-config/              Project + user settings
  tests/                       Fixtures + trigger evals

~/.something-wicked/wicked-prezzie/    Shared across projects
  themes/                      Theme JSON files
  profiles/                    Exported .pptprofile files
  registry/                    Shared design asset registry
  versions/                    Deck version history
  config.json                  User-level defaults
```

---

## Known tradeoffs

These are deliberate:

- **Gradients** become solid blended colors (PPTX gradient support is limited)
- **Animations** are stripped (we capture the final state, not the journey)
- **Font metrics** differ between CSS and Calibri (compensated with width multipliers, not perfect)
- **Small SVGs** under 60px are skipped (decorative noise that captures surrounding text)
- **Chrome + PowerPoint required** locally (no substitute for the definitive renderers)

---

## License

MIT. Do whatever you want with it.

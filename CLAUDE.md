# wicked-pptx

HTML slide decks → editable PowerPoint conversion toolkit.

## Architecture

**Full pipeline**: Topic → outline → generate → standardize → convert → validate → render → compare

```
Topic/brief → slide-outline → slide-generate → slide-html-standardize → chrome-extract → slide-pptx-builder → slide-validate
               Pyramid          outline→HTML       normalize          DOM walk        layout→PPTX     bounds+overflow
               Principle         + theme            viewport          bounding boxes                        |
               narrative arc     CSS vars           strip anim        colors/fonts                    slide-render
                    ↑                                                                                (PPTX→PNG)
              slide-theme                                                                                  |
              (brand/colors/                                                                         slide-compare
               fonts/spacing)                                                                       (HTML vs PPTX)
```

## Project Structure

All skills live under `skills/`. Each has SKILL.md + optional scripts/ and references/.

```
skills/
  shared/                  — Shared utilities (paths, constants)
    __init__.py
    paths.py                     (output_path, ensure_output_dir → ~/.something-wicked/wicked-prezzie/output/)
  slide-theme/             — Brand/style definitions: colors, fonts, layout tokens
    SKILL.md
    scripts/slide_theme.py
    themes/                      (auto-created: midnight-purple, corporate-light, warm-dark)
    references/style-learning.md   (extract styles from PPTX/PDF/images)
    references/profiles.md         (portable style profiles, vibe matching)
    references/design-registry.md  (git-backed shared design assets)
  slide-outline/           — Topic → structured outline (Pyramid Principle)
    SKILL.md
    scripts/slide_outline.py
    references/pyramid-principle.md
  slide-generate/          — Outline → themed HTML slides
    SKILL.md
    scripts/slide_generate.py    (imports: slide-theme)
    references/templates.md
    references/image-sourcing.md   (Unsplash/icons/none modes, attribution)
  chrome-extract/          — Chrome headless layout extraction + screenshots
    SKILL.md
    scripts/chrome_extract.py
    references/js-dom-walker.md
  slide-pptx-builder/      — Layout JSON → native PPTX shapes/text + color utils
    SKILL.md
    scripts/pptx_builder.py
    scripts/color_utils.py       (CSS color parsing, alpha blending)
    references/coordinate-system.md
    references/text-clamping.md
  slide-html-standardize/  — Normalize AI-generated HTML before conversion
    SKILL.md
    scripts/html_standardize.py
  slide-html-to-pptx/      — Batch convert HTML slides to PPTX (conversion stage)
    SKILL.md
    scripts/html_to_pptx.py      (imports: chrome-extract, slide-pptx-builder)
  slide-validate/          — Post-conversion QA: bounds, overflow, scoring, audit
    SKILL.md
    scripts/slide_validate.py    (imports: slide-render)
    references/overflow-detection.md
    references/deck-audit.md       (5-category weighted quality audit)
    references/content-lint.md     (bullets, titles, stats, quotes, passive voice, CTAs)
    references/consistency-checks.md (within-deck + cross-deck consistency)
  slide-render/            — PPTX → PNG via PowerPoint headless
    SKILL.md
    scripts/slide_render.py
  slide-design/            — Design principles + quality rubric (reference only)
    SKILL.md
    references/design-principles.md
    references/quality-rubric.md
    references/css-contract.md     (zone CSS naming, type rules, fallback layout)
    references/hints.md            (contextual hints + REVIEW flags in speaker notes)
  slide-compare/           — Visual comparison: HTML screenshots vs PPTX renders
    SKILL.md
    scripts/slide_compare.py     (imports: chrome-extract)
  slide-pipeline/          — End-to-end orchestrator (chains all stages)
    SKILL.md
    scripts/slide_pipeline.py    (imports: all skills)
    references/fidelity-tiers.md   (best/draft/rough quality tiers, multi-pass loops)
    references/versioning.md       (deck versioning, naming, metadata, diff)
    references/output-formats.md   (PPTX + Reveal.js HTML dual-format output)
    references/edit-coordination.md (session locks for concurrent operations)
  slide-config/            — User-configurable settings (quality threshold, viewport, etc.)
    SKILL.md
    scripts/slide_config.py
    config.json                  (auto-created on first `set`)

tests/                     — Test fixtures, evals, and trigger-evals
  test-slide-01.html       — Title slide (heading, subtitle, accent bar)
  test-slide-02.html       — Content slide (card grid with stats)
  test-slide-03.html       — Section divider (CTA, inline color spans)
  evals.json               — End-to-end evaluation prompts
  trigger-evals/           — Per-skill triggering accuracy tests
```

## Cross-Skill Import Pattern

Skills import from sibling skills via sys.path (all skills are siblings under `skills/`):

```python
_root = Path(__file__).parent.parent.parent  # skills/ directory
sys.path.insert(0, str(_root / "chrome-extract" / "scripts"))
from chrome_extract import extract_layout
```

## Storage Architecture

User-level data lives in `~/.something-wicked/wicked-prezzie/` (shared across projects).
Project-level config stays in `skills/slide-config/config.json` (per-project overrides).

```
~/.something-wicked/wicked-prezzie/
  config.json              — User defaults (default_font, default_fidelity, unsplash_api_key)
  themes/                  — Theme JSON files (learned, imported, built-in seeds)
  profiles/                — Exported .pptprofile files
  registry/                — Shared design registry cache + config
    config.json            — Registry remote URL, sync status
    palettes/
    strategies/
    iconsets/
  versions/                — Deck version metadata (per slug)
    sales-kickoff.json
  output/                  — Default output directory for intermediate artifacts
    outline.json           — Default outline output
    slides/                — Generated HTML slides
    renders/               — PPTX→PNG renders
    compare/               — HTML vs PPTX comparison images
```

**Resolution order**: defaults → user config → project config (project wins).

**User-level keys**: `default_font`, `default_fidelity`, `unsplash_api_key`
**Project-level keys**: `quality_threshold`, `viewport`, `hide_selectors`, `active_theme`, `slide_width_inches`, `slide_height_inches`

## Key Design Decisions

1. **Let the browser do layout** — Chrome resolves all cascading styles, flexbox, grid, absolute positioning. We just read the computed result.

2. **Richtext extraction** — h1/h2/h3/p elements are extracted with inline run formatting. Prevents the "Go Faster" overlap bug where inline-styled spans became separate text boxes.

3. **Alpha blending** — CSS rgba colors are pre-blended against the slide background since PPTX shapes don't support CSS-style transparency.

4. **Card text clamping** — text inside card shapes is constrained to the card's width (not Chrome's tight bounding box).

5. **SVG handling** — large SVG charts rendered as cropped screenshot images. Small decorative SVGs (<60px) skipped.

6. **PowerPoint for rendering** — PPTX→PDF via PowerPoint (AppleScript on macOS, COM on Windows), then pdftoppm for PDF→PNG. Highest fidelity since PowerPoint is the definitive renderer.

7. **Iterative visual verification** — After conversion, render both HTML (Chrome) and PPTX (PowerPoint) to PNG, then visually compare each slide. Fix issues and re-convert until all slides pass or no further improvement is possible. This is a Claude-in-the-loop pattern (like literal-extractor): Claude uses its vision to judge quality, not pixel math. The scripts are single-pass tools; the iteration logic lives in the SKILL.md workflow.

8. **Overflow detection** — pad+render+check pattern: enlarge PPTX with grey padding, render via PowerPoint, check margins for non-grey pixels indicating content overflow.

## Dependencies

- python-pptx, beautifulsoup4 + lxml, Pillow
- Google Chrome (for headless extraction)
- Microsoft PowerPoint (macOS via AppleScript, Windows via COM automation)
- pdftoppm from poppler (`brew install poppler` on macOS)

## Known Limitations

- Gradient backgrounds approximated with solid blended colors
- CSS animations/transitions stripped during standardization (static snapshot)
- Font metrics differ between CSS and Calibri (compensated with width multipliers)
- Small decorative SVGs skipped

# wicked-pptx

HTML slide decks → editable PowerPoint conversion toolkit.

## Architecture

**Full pipeline**: Topic → outline → generate → standardize → triage → prep → build → validate → render → compare

```
Topic/brief → outline → generate → standardize → chrome-extract → triage → prep → pptx-builder → validate
               Pyramid          outline→HTML       normalize          DOM walk         confidence    manifest      layout→PPTX     bounds+overflow
               Principle         + theme            viewport          bounding boxes   scoring +     JSON with                           |
               narrative arc     CSS vars           strip anim        colors/fonts     pattern       resolvedRect              render
                    ↑                                                                  detection      geometry                 (PPTX→PNG)
              theme                                                              (findings                                      |
              (brand/colors/                                                            JSON)                               compare
               fonts/spacing)                                                                                               (HTML vs PPTX)
                                                                                         ↓ fix history
                                                                               treatment-log
                                                                               (known-patterns.md feedback)

Offline utility (not an inline pipeline step):
  learn             Source docs → two-pass index → markdown indexes with YAML frontmatter
                    (PDFs, PPTX,    per-doc + cross-doc    _insights/ fast-path,
                     DOCX, HTML)    extraction + synthesis  _tags/, _relationships/)

Feedback analysis (post-review):
  feedback          Word .docx inline comments → alignment/divergence analysis → feedback report
                    (parse comments,    sentiment classification,    narrative implications,
                     section mapping)    cluster detection             action items)

Deck-level methodology (Claude-orchestrated, no scripts):
  workflow          Hub-and-spoke orchestrator: phase state machine, constraint injection, gate conditions
  brainstorm        Dreamer-skeptic teams, 12-persona framework, synthesis rules, content principles
```

## Project Structure

All skills live under `skills/`. Each has SKILL.md + optional scripts/ and references/.

```
skills/
  shared/                  — Shared utilities (paths, constants)
    __init__.py
    paths.py                     (output_path, ensure_output_dir → ~/.something-wicked/wicked-prezzie/output/)
  theme/                   — Brand/style definitions: colors, fonts, layout tokens
    SKILL.md
    scripts/slide_theme.py
    themes/                      (auto-created: midnight-purple, corporate-light, warm-dark)
    references/style-learning.md   (extract styles from PPTX/PDF/images)
    references/profiles.md         (portable style profiles, vibe matching)
    references/design-registry.md  (git-backed shared design assets)
  outline/                 — Topic → structured outline (Pyramid Principle)
    SKILL.md
    scripts/slide_outline.py
    references/pyramid-principle.md
  generate/                — Outline → themed HTML slides
    SKILL.md
    scripts/slide_generate.py    (imports: theme)
    references/templates.md
    references/image-sourcing.md   (Unsplash/icons/none modes, attribution)
  chrome-extract/          — Chrome headless layout extraction + screenshots
    SKILL.md
    scripts/chrome_extract.py
    references/js-dom-walker.md
  pptx-builder/            — Layout JSON → native PPTX shapes/text + color utils
    SKILL.md
    scripts/pptx_builder.py
    scripts/color_utils.py       (CSS color parsing, alpha blending)
    scripts/edl_apply.py         (EDL applicator for declarative PPTX edits)
    references/coordinate-system.md
    references/text-clamping.md
    references/pptx-recipes.md   (python-pptx fix recipes for direct edits)
  standardize/             — Normalize AI-generated HTML before conversion
    SKILL.md
    scripts/html_standardize.py  (+ complexity annotation for pipeline routing)
  quick-convert/           — Batch convert HTML slides to PPTX (conversion stage)
    SKILL.md
    scripts/html_to_pptx.py      (imports: chrome-extract, pptx-builder, triage, prep)
  triage/                  — Confidence scoring + pattern detection per slide (model-driven pipeline)
    SKILL.md
    scripts/slide_triage.py      (triage_slide() → findings JSON with confidence scores + collision risks)
    references/known-patterns.md (10 seed patterns: SVG bleed, accent bar, rotation, card overflow, badge collision...)
  prep/                    — Auto-resolve triage findings into build manifests
    SKILL.md
    scripts/slide_prep.py        (auto_resolve() → manifest JSON with resolvedRect geometry transforms)
  treatment-log/           — Per-slide fix history + promotion candidates for known-patterns.md
    SKILL.md
  validate/                — Structural QA: bounds, overflow, empty slides
    SKILL.md
    scripts/slide_validate.py    (structural checks only — no visual/scoring)
    references/overflow-detection.md
    references/deck-audit.md       (5-category weighted quality audit)
    references/content-lint.md     (bullets, titles, stats, quotes, passive voice, CTAs)
    references/consistency-checks.md (within-deck + cross-deck consistency)
  render/                  — PPTX → PNG via LibreOffice headless
    SKILL.md
    scripts/slide_render.py
  design-ref/              — Design principles + quality rubric (reference only)
    SKILL.md
    references/design-principles.md
    references/quality-rubric.md
    references/css-contract.md     (zone CSS naming, type rules, fallback layout)
    references/hints.md            (contextual hints + REVIEW flags in speaker notes)
  compare/                 — Visual comparison workflow (no script — uses chrome-extract + render)
    SKILL.md
  convert/                 — End-to-end workflow (no script — Claude orchestrates directly)
    SKILL.md
    references/fidelity-tiers.md   (best/draft/rough quality tiers, multi-pass loops)
    references/versioning.md       (deck versioning, naming, metadata, diff)
    references/output-formats.md   (PPTX + Reveal.js HTML dual-format output)
    references/edit-coordination.md (session locks for concurrent operations)
  config/                  — User-configurable settings (quality threshold, viewport, etc.)
    SKILL.md
    scripts/slide_config.py
    config.json                  (auto-created on first `set`)
  learn/                   — Source document indexing (offline utility, not inline pipeline)
    SKILL.md
    scripts/slide_learn.py       (two-pass indexing orchestrator)
    references/
      index-schema.md            (markdown index format, YAML frontmatter schema)
      chunk-strategy.md          (document chunking rules by type)
      vision-templates.md        (vision extraction prompts for images/charts)
      search-patterns.md         (how to query indexes efficiently)
      integration.md             (how pipeline skills consume indexes)
  workflow/                — Deck-building orchestrator (methodology only, no script)
    SKILL.md
    references/
      phase-definitions.md       (8-phase state machine, gate conditions)
      constraint-registry.md     (constraint format + 10 default constraints)
      agent-catalog.md           (agent definitions with prompt templates)
  brainstorm/              — Dreamer-skeptic brainstorm methodology (no script)
    SKILL.md
    references/
      brainstorm-teams.md        (3-team structure, roles, interaction protocol)
      content-principles.md      (8 content skills: mechanism-before-outcome, etc.)
      persona-framework.md       (12-persona system, pass/fail criteria, pairing)
  checkpoint/              — Session synthesis: decisions, artifacts, next steps (no script)
    SKILL.md
  feedback/                — Word comment parsing + feedback alignment analysis
    SKILL.md
    scripts/parse_word_comments.py   (extract inline comments from .docx XML)
    scripts/analyze_feedback.py      (sentiment, clustering, alignment/divergence)
    scripts/generate_report.py       (markdown or .docx feedback report)
  start/                   — Universal entry point: auto-detects intent and routes to workflow/convert/feedback
    SKILL.md
  exec-summary/            — Generate executive summary document from deck content
    SKILL.md

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
Project-level config stays in `skills/config/config.json` (per-project overrides).

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
**Project-level keys**: `quality_threshold`, `viewport`, `hide_selectors`, `active_theme`, `slide_width_inches`, `slide_height_inches`, `index_dirs`

## Entry Point

One entry point: `wicked-prezzie:start`. It detects what the user has and routes accordingly:

- **Topic or brief** → auto-detect workflow template (general or rfp-exec) → run workflow
- **Source documents** → index first, then recommend workflow template
- **HTML slides** → route to `wicked-prezzie:convert`
- **Reviewed Word doc** → route to `wicked-prezzie:feedback`

`wicked-prezzie:workflow` is the internal orchestrator. `wicked-prezzie:convert` handles HTML→PPTX conversion. Users don't need to know the difference — `wicked-prezzie:start` handles routing.

## Key Design Decisions

1. **Let the browser do layout** — Chrome resolves all cascading styles, flexbox, grid, absolute positioning. We just read the computed result.

2. **Model-driven triage pipeline** — After extraction, `classify_elements()` adds confidence scores (0.0–1.0) and `flagReason` to every element. `triage` checks each element against 10 known-pattern signatures and detects collision risks. `prep` auto-resolves high-confidence elements (>= 0.85) with geometry transforms, and flags low-confidence elements for model inspection. The builder receives a fully-resolved manifest with no ambiguous types.

3. **Alpha blending** — CSS rgba colors are pre-blended against the slide background since PPTX shapes don't support CSS-style transparency.

4. **Card text clamping** — text inside card shapes is constrained to the card's width (not Chrome's tight bounding box). Encoded as PATTERN-004 in `known-patterns.md`; applied as `resolvedRect` in the manifest.

5. **SVG handling** — SVG charts rendered via isolated screenshot (hide all non-SVG content, screenshot, crop). Small decorative SVGs (<30px) skipped. PATTERN-001 (SVG crop bleed) clamps SVG height when content is within 30px below the SVG boundary.

6. **LibreOffice for rendering** — PPTX→PDF via `soffice --headless`, then pdftoppm for PDF→PNG. No Microsoft PowerPoint required — runs headless without GUI, permission dialogs, or automation consent. Handles sandboxed environments automatically.

7. **Iterative visual verification** — After conversion, render both HTML (Chrome) and PPTX (LibreOffice) to PNG, then Claude visually compares each slide. Fix issues and re-convert until all slides pass or no further improvement is possible. Claude uses its vision to judge quality, not pixel math. Scripts are single-pass tools; the iteration logic lives in `convert/SKILL.md`. There is no orchestrator script — Claude drives the loop directly.

8. **Structural validation only** — `slide_validate.py` checks shape bounds, negative coords, empty slides, and text overflow heuristics. Visual fidelity is judged by Claude comparing rendered images, not by automated pixel scanning.

9. **Manifest-based build** — `pptx_builder.build_slide_from_manifest()` reads a fully-resolved manifest and executes PPTX API calls mechanically with no classification logic. The manifest is the contract between model judgment (prep) and builder execution. All geometry transforms are pre-resolved as `resolvedRect` fields before the builder runs. `build_slide()` is a legacy wrapper that converts layout_data to a manifest via triage+prep before delegating.

10. **Enriched IR** — Extraction includes `layoutRole` (inferred from CSS class patterns like `card`, `stat`, `badge`, `progress`, `chart`) and full `classes` on every element. The builder can dispatch by semantic role instead of guessing from pixel geometry.

11. **Complexity routing** — `html_standardize.py` annotates each slide with `<!-- COMPLEXITY: high|low -->` by scanning for SVGs, gradients, pseudo-elements, rotated text. The pipeline uses this to set expectations: low-complexity slides should pass in 1-2 attempts, high-complexity slides may need direct fixes.

12. **Two-pass indexing** — `learn` separates per-document extraction (parallelizable, stateless) from cross-document synthesis (sequential, requires full corpus). Pass 1 can be run incrementally as new documents arrive. Pass 2 rebuilds `_insights/` and `_relationships/` from the full set.

13. **Hub-and-spoke deck orchestration** — `workflow` owns the phase state machine and constraint injection; phase-specific skills (`brainstorm`, `generate`, `validate`) own execution. Constraints persist in `constraints.json` on disk, not in conversation context, surviving session boundaries.

## Dependencies

- python-pptx, beautifulsoup4 + lxml, Pillow
- Google Chrome (for headless extraction)
- LibreOffice (`brew install --cask libreoffice` on macOS, `apt install libreoffice` on Linux)
- pdftoppm from poppler (`brew install poppler` on macOS)

## Known Limitations

- Gradient backgrounds approximated with solid blended colors
- CSS animations/transitions stripped during standardization (static snapshot)
- Font metrics differ between CSS and Calibri (compensated with width multipliers)
- Small decorative SVGs skipped

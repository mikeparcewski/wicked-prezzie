# wicked-prezzie

General-purpose presentation toolkit: topic → slides → PowerPoint, with content grounding, collaborative review, and multiple export formats.

## Architecture

### Content Creation Pipeline
```
Topic/brief → search/ask (grounded) → outline → generate → standardize → convert → validate → export
                    ↑                    ↑           ↑                                    ↓
              learn + add-doc       story-arc     theme                              render + compare
              (source indexing)     (narrative)   (brand/style)                      (visual QA)
```

### HTML→PPTX Conversion Pipeline
```
HTML slides → standardize → chrome-extract → triage → prep → pptx-builder → validate
               normalize      DOM walk        confidence  manifest   layout→PPTX    bounds+overflow
               viewport       bounding boxes  scoring +   JSON with                      |
               strip anim     colors/fonts    pattern     resolvedRect            render (PPTX→PNG)
                                              detection    geometry                      |
                                             (findings                             compare
                                              JSON)                              (HTML vs PPTX)
                                                ↓ fix history
                                          treatment-log
                                          (known-patterns.md feedback)
```

### Supporting Systems
```
Content grounding:
  learn             Source docs → two-pass index → markdown chunks with YAML frontmatter
  search            Context-aware search: adapts strategy to deck type, audience, phase
  ask               Four-stage Q&A: specialist personas → reviewer → facilitator
  add-doc           Source management: importance tagging, auto-indexing
  add-notes         Freeform notes capture: decisions, constraints, session context

Deck methodology (Claude-orchestrated, no scripts):
  workflow          Hub-and-spoke orchestrator: template-driven phases, constraint injection
  brainstorm        Dreamer-skeptic teams, persona framework, synthesis rules
  story-arc         Lightweight narrative advisor: 6 patterns, single-agent alternative to brainstorm

Output & presentation:
  notes             Speaker notes: 3-field structure, template-configurable tab 3
  presenter-html    Self-contained presenter view: embedded slides, tabbed notes, keyboard nav
  presenter-pdf     Clean slides-only PDF via Chrome headless
  handout           Attendee takeaway: slides → readable prose in markdown/PDF/Word

Quality & validation:
  validation-lenses Pluggable quality lenses: 4 universal + template-specific
  validate          Structural QA: bounds, overflow, empty slides
  compare           Visual comparison: HTML source vs PPTX output

Collaboration:
  collaborate       Multi-person review: inline annotations, per-slide verdicts, file-based
  feedback          Word .docx comment parsing + alignment/divergence analysis

Library & versioning:
  deck-library      Index completed decks, search past work, extract reusable slides
  deck-diff         Visual + structural comparison of deck versions

Structured documents:
  structured-response  Config-driven document generator with 4-agent review pattern
  exec-summary         Executive summary synthesis from brainstorm outputs
```

## Project Structure

Skills live under `skills/`. Workflow templates live under `templates/`. Each skill has SKILL.md + optional scripts/ and references/.

```
templates/                   — Workflow templates (project-level, collaborative)
  general.yaml               — Default 6-phase workflow
  executive-briefing.yaml    — C-suite presentations (7 phases, higher threshold)
  training-workshop.yaml     — Training/education decks (learning design focus)
  conference-talk.yaml       — Keynotes/talks (lighter 5-phase process)
  competitive-analysis.yaml  — Market/competitive decks (7 phases, evidence focus)
  project-status.yaml        — Status updates (minimal 4-phase process)

skills/
  shared/                  — Shared utilities (paths, constants)
    __init__.py
    paths.py                     (output_path, ensure_output_dir → ~/.something-wicked/wicked-prezzie/output/)

  # --- Content Grounding ---
  search/                  — Context-aware search across indexed sources
    SKILL.md
  ask/                     — Four-stage Q&A with specialist personas
    SKILL.md
  add-doc/                 — Source document management with importance tagging
    SKILL.md
  add-notes/               — Freeform notes, decisions, session context capture
    SKILL.md
  learn/                   — Source document indexing (two-pass pipeline)
    SKILL.md
    scripts/slide_learn.py
    references/
      index-schema.md, chunk-strategy.md, vision-templates.md,
      search-patterns.md, integration.md

  # --- Content Creation ---
  theme/                   — Brand/style definitions: colors, fonts, layout tokens
    SKILL.md
    scripts/slide_theme.py
    themes/                      (auto-created: midnight-purple, corporate-light, warm-dark)
    references/style-learning.md, profiles.md, design-registry.md
  outline/                 — Topic → structured outline (Pyramid Principle)
    SKILL.md
    scripts/slide_outline.py
    references/pyramid-principle.md
  generate/                — Outline → themed HTML slides
    SKILL.md
    scripts/slide_generate.py    (imports: theme)
    references/templates.md, image-sourcing.md
  story-arc/               — Lightweight narrative advisor (6 patterns)
    SKILL.md
  diagram/                 — Text → SVG diagrams (Mermaid/D2 or direct SVG)
    SKILL.md
  notes/                   — Speaker notes generator (3-field, template-configurable)
    SKILL.md

  # --- HTML Normalization ---
  standardize/             — Normalize AI-generated HTML before conversion
    SKILL.md
    scripts/html_standardize.py

  # --- Conversion Pipeline ---
  chrome-extract/          — Chrome headless layout extraction + screenshots
    SKILL.md
    scripts/chrome_extract.py
    references/js-dom-walker.md
  triage/                  — Confidence scoring + pattern detection per slide
    SKILL.md
    scripts/slide_triage.py
    references/known-patterns.md
  prep/                    — Auto-resolve triage findings into build manifests
    SKILL.md
    scripts/slide_prep.py
  pptx-builder/            — Layout JSON → native PPTX shapes/text + color utils
    SKILL.md
    scripts/pptx_builder.py, color_utils.py, edl_apply.py
    references/coordinate-system.md, text-clamping.md, pptx-recipes.md
  quick-convert/           — Single-stage HTML→PPTX (no iterative QA)
    SKILL.md
    scripts/html_to_pptx.py
  convert/                 — End-to-end HTML→PPTX with iterative visual verification
    SKILL.md
    references/fidelity-tiers.md, versioning.md, output-formats.md, edit-coordination.md
  treatment-log/           — Per-slide fix history + pattern promotion candidates
    SKILL.md

  # --- Quality & Validation ---
  validate/                — Structural QA: bounds, overflow, empty slides
    SKILL.md
    scripts/slide_validate.py
    references/overflow-detection.md, deck-audit.md, content-lint.md, consistency-checks.md
  validation-lenses/       — Pluggable quality lenses (universal + template-specific)
    SKILL.md
  render/                  — PPTX → PNG via LibreOffice headless
    SKILL.md
    scripts/slide_render.py
  compare/                 — Visual comparison: HTML vs PPTX renders
    SKILL.md
  design-ref/              — Design principles + quality rubric (reference only)
    SKILL.md
    references/design-principles.md, quality-rubric.md, css-contract.md, hints.md

  # --- Output & Presentation ---
  presenter-html/          — Self-contained HTML presenter view
    SKILL.md
    scripts/build_presenter_html.py
  presenter-pdf/           — Clean slides-only PDF via Chrome headless
    SKILL.md
    scripts/build_presenter_pdf.py
  handout/                 — Attendee takeaway document (markdown/PDF/Word)
    SKILL.md

  # --- Collaboration ---
  collaborate/             — Multi-person file-based review workflow
    SKILL.md
  feedback/                — Word comment parsing + feedback analysis
    SKILL.md
    scripts/parse_word_comments.py, analyze_feedback.py, generate_report.py

  # --- Library & Versioning ---
  deck-library/            — Deck gallery: index, search, extract, browse
    SKILL.md
  deck-diff/               — Deck version comparison (outline, theme, visual)
    SKILL.md

  # --- Structured Documents ---
  structured-response/     — Config-driven document generator with multi-agent review
    SKILL.md
    scripts/build_response_docx.py
  exec-summary/            — Executive summary synthesis from brainstorm outputs
    SKILL.md

  # --- Orchestration ---
  workflow/                — Template-driven deck-building orchestrator
    SKILL.md
    references/phase-definitions.md, constraint-registry.md, agent-catalog.md, deck-claude-md.md
  brainstorm/              — Dreamer-skeptic brainstorm methodology
    SKILL.md
    references/brainstorm-teams.md, content-principles.md, persona-framework.md
  checkpoint/              — Session synthesis: decisions, artifacts, next steps
    SKILL.md
  start/                   — Universal entry point: auto-detects intent and routes
    SKILL.md
  config/                  — User-configurable settings
    SKILL.md
    scripts/slide_config.py, config.json

tests/                     — Test fixtures, evals, and trigger-evals
  test-slide-01.html       — Title slide (heading, subtitle, accent bar)
  test-slide-02.html       — Content slide (card grid with stats)
  test-slide-03.html       — Section divider (CTA, inline color spans)
  evals.json               — End-to-end evaluation prompts
  trigger-evals/           — Per-skill triggering accuracy tests
```

## Workflow Templates

Templates are YAML files at project level (`templates/`), designed for collaborative teams on shared drives. Each template defines: phases, gate conditions, persona sets, validation lenses, notes schema, and export formats.

The `start` skill dynamically reads `templates/*.yaml` signal lists for auto-detection. The `workflow` skill loads phase definitions from the active template.

| Template | Phases | Audience | Tab 3 | Pass Threshold |
|----------|--------|----------|-------|---------------|
| general | 6 | General | References | 75 |
| executive-briefing | 7 | C-suite | Decision Points | 85 |
| training-workshop | 6 | Learners | Learning Objectives | 75 |
| conference-talk | 5 | Conference | Timing Notes | 75 |
| competitive-analysis | 7 | Strategy | Data Sources | 75 |
| project-status | 4 | Stakeholders | Metrics | 70 |

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
  versions/                — Deck version metadata (per slug)
  library/                 — Deck library catalog + thumbnails
    catalog.json           — Master index of all indexed decks
    {deck-slug}/           — Per-deck metadata + slide thumbnails
  output/                  — Default output directory for intermediate artifacts
    outline.json, slides/, renders/, compare/, diagrams/

project-level/
  templates/               — Workflow template YAML files (collaborative, version-controlled)
  sources/                 — Team's shared source documents
    documents/             — PDFs, PPTX, DOCX, spreadsheets
    images/                — Photos, screenshots, logos
    data/                  — CSVs, spreadsheets
    notes/                 — Freeform notes and decisions
  index/                   — Generated chunk store (from learn)
  decks/                   — Completed decks (indexed by deck-library)
  .prezzie/
    deck-state.json        — Active deck state + template selection
    constraints.json       — Persisted constraints
    CLAUDE.md              — Per-deck editorial context (auto-generated)
  .reviews/                — Collaborative review sessions (from collaborate)
```

**Resolution order**: defaults → user config → project config (project wins).

## Entry Point

One entry point: `wicked-prezzie:start`. It detects what the user has and routes accordingly:

- **Topic or brief** → auto-detect workflow template from `templates/*.yaml` signals → run workflow
- **Source documents** → `learn` to index, then recommend workflow template
- **HTML slides** → route to `wicked-prezzie:convert`
- **Reviewed Word doc** → route to `wicked-prezzie:feedback`
- **Document/response requirements** → route to `wicked-prezzie:structured-response`

`wicked-prezzie:workflow` is the internal orchestrator. `wicked-prezzie:convert` handles HTML→PPTX conversion. Users don't need to know the difference — `wicked-prezzie:start` handles routing.

## Key Design Decisions

1. **Let the browser do layout** — Chrome resolves all cascading styles, flexbox, grid, absolute positioning. We just read the computed result.

2. **Model-driven triage pipeline** — After extraction, `classify_elements()` adds confidence scores (0.0–1.0) and `flagReason` to every element. `triage` checks each element against 10 known-pattern signatures and detects collision risks. `prep` auto-resolves high-confidence elements (>= 0.85) with geometry transforms, and flags low-confidence elements for model inspection. The builder receives a fully-resolved manifest with no ambiguous types.

3. **Alpha blending** — CSS rgba colors are pre-blended against the slide background since PPTX shapes don't support CSS-style transparency.

4. **Card text clamping** — text inside card shapes is constrained to the card's width (not Chrome's tight bounding box). Encoded as PATTERN-004 in `known-patterns.md`; applied as `resolvedRect` in the manifest.

5. **SVG handling** — SVG charts rendered via isolated screenshot (hide all non-SVG content, screenshot, crop). Small decorative SVGs (<30px) skipped. PATTERN-001 (SVG crop bleed) clamps SVG height when content is within 30px below the SVG boundary.

6. **LibreOffice for rendering** — PPTX→PDF via `soffice --headless`, then pdftoppm for PDF→PNG. No Microsoft PowerPoint required.

7. **Iterative visual verification** — After conversion, render both HTML (Chrome) and PPTX (LibreOffice) to PNG, then Claude visually compares each slide. Fix issues and re-convert until all slides pass or no further improvement is possible.

8. **Structural validation only** — `slide_validate.py` checks shape bounds, negative coords, empty slides, and text overflow heuristics. Visual fidelity is judged by Claude comparing rendered images.

9. **Manifest-based build** — `pptx_builder.build_slide_from_manifest()` reads a fully-resolved manifest and executes PPTX API calls mechanically with no classification logic.

10. **Enriched IR** — Extraction includes `layoutRole` (inferred from CSS class patterns) and full `classes` on every element.

11. **Complexity routing** — `html_standardize.py` annotates each slide with `<!-- COMPLEXITY: high|low -->`.

12. **Two-pass indexing** — `learn` separates per-document extraction (parallelizable) from cross-document synthesis (sequential).

13. **Template-driven orchestration** — `workflow` loads phases from YAML templates at project level. Templates define phases, personas, validation lenses, notes schema, and export formats. Teams customize templates on shared drives.

14. **Context-aware search** — `search` reads `deck-state.json` to adapt strategy by deck type. Board decks search for metrics; training decks search for examples; competitive decks search for differentiators.

15. **File-based collaboration** — `collaborate` uses flat files (JSON + markdown) in `.reviews/` for multi-person review. No server required — works on shared drives.

16. **Pluggable validation lenses** — 4 universal lenses (Clarity, Evidence, Flow, Audience Fit) always run. Templates add domain-specific lenses (Executive Readiness, Knowledge Check, etc.).

17. **Deck library for reuse** — Completed decks indexed into `~/.something-wicked/wicked-prezzie/library/` with slide-level metadata and layout pattern classification.

## Dependencies

- python-pptx, beautifulsoup4 + lxml, Pillow, pypdf
- Google Chrome (for headless extraction + PDF export)
- LibreOffice (`brew install --cask libreoffice` on macOS, `apt install libreoffice` on Linux)
- pdftoppm from poppler (`brew install poppler` on macOS)
- Optional: mermaid-cli (`npm install -g @mermaid-js/mermaid-cli`) for diagram generation

## Known Limitations

- Gradient backgrounds approximated with solid blended colors
- CSS animations/transitions stripped during standardization (static snapshot)
- Font metrics differ between CSS and Calibri (compensated with width multipliers)
- Small decorative SVGs skipped
- Diagram generation falls back to direct SVG if mermaid-cli not installed

# Architecture

Technical deep-dive into how wicked-prezzie works. For the high-level overview, see [README.md](README.md). For the pipeline diagram, see [PIPELINE.md](PIPELINE.md).

## How HTML-to-PPTX conversion works

The core problem: HTML slides use CSS layout (flexbox, grid, absolute positioning, cascading styles) that has no equivalent in the PPTX shape model. PPTX shapes are absolutely positioned rectangles with fixed coordinates. The conversion bridges these two worlds in five steps.

**Step 1 -- Chrome headless extraction.** `chrome-extract` launches headless Chrome, renders the HTML slide at the configured viewport size, and walks the DOM. For every visible element, it reads the computed bounding box (`getBoundingClientRect`), computed colors, font properties, text content, and CSS classes. The output is a flat JSON array of elements with pixel-precise geometry. SVG elements get special handling: all non-SVG content is hidden, then the SVG is screenshot and cropped in isolation.

**Step 2 -- Triage.** `slide-triage` scores each element with a confidence value (0.0-1.0) and checks it against 10 known-pattern signatures defined in `known-patterns.md`. Patterns include SVG crop bleed (PATTERN-001), accent bar positioning (PATTERN-002), rotation (PATTERN-003), card text overflow (PATTERN-004), badge collision (PATTERN-005), and others. Each pattern has a detection predicate and a geometry correction rule. Triage also detects collision risks between overlapping elements. The output is a findings JSON with per-element confidence scores and `flagReason` annotations.

**Step 3 -- Prep.** `slide-prep` reads the triage findings and auto-resolves high-confidence elements (>= 0.85) by computing geometry transforms. Each resolved element gets a `resolvedRect` field with exact PPTX coordinates (in EMUs). Low-confidence elements are flagged for model inspection -- Claude reviews them and decides the correct placement. The output is a fully-resolved manifest: every element has a final position, no ambiguity remains.

**Step 4 -- Build.** `pptx_builder.build_slide_from_manifest()` reads the manifest and mechanically creates python-pptx shapes. It does zero classification -- the manifest is the contract. Text shapes get font properties mapped from CSS. Background rectangles get fill colors. Images get placed at exact coordinates. The builder is intentionally dumb: all intelligence lives in triage and prep.

**Step 5 -- Alpha blending.** CSS `rgba()` colors with transparency are pre-blended against the slide background color before being applied to PPTX shapes. PPTX shapes support opacity but not CSS-style alpha compositing, so `color_utils.py` resolves the final solid color at build time.

The key insight: let the browser do layout. Chrome resolves all cascading styles, flexbox, grid, and absolute positioning. We read the computed result rather than re-implementing CSS layout in Python.

## How slide-learn indexing works

`slide-learn` converts source documents (PDF, PPTX, DOCX, HTML, images) into a grep-able, git-committable chunk store that other skills query when building slides.

**Pass 1 -- Per-document extraction (parallelizable, stateless).** For each source file:

1. Detect type from file extension (pdf, pptx, docx, html, image)
2. Chunk by type-specific rules: PDFs by page ranges (3-6 pages), PPTX by slide, DOCX by heading boundaries (H1/H2, 400-800 words), HTML by slide div, images as single chunks
3. Extract text directly for text-based formats. For binary content (embedded images, slide screenshots), run vision extraction using standardized prompts from `vision-templates.md`
4. Write each chunk as a Markdown file at `index/{source-name}/chunk-NNN.md` with YAML frontmatter containing 12 fields: `source`, `source_type`, `chunk_id`, `content_type`, `contains`, `entities`, `figures`, `narrative_theme`, `slide_relevance`, `confidence`, `indexed_at`

Pass 1 is incremental: SHA-256 hashes per source file are stored in `index/.cache/`. Unchanged files are skipped on re-index.

**Pass 2 -- Cross-document synthesis (sequential, requires full corpus).** Scans all chunk frontmatter and builds aggregated artifacts:

- `index/_tags/{tag}.md` -- faceted lookup by tag, listing all chunks with that tag plus snippets
- `index/_relationships/systems.md` and `people.md` -- entity cross-references across documents
- `index/_insights/key-facts.md` -- top facts and figures with source attribution
- `index/_insights/narrative-themes.md` -- recurring themes suitable for slide narratives
- `index/_insights/gaps.md` -- topics mentioned but not elaborated (coverage gaps)
- `index/_manifest.json` -- freshness record with timestamps, document count, chunk count

**Search pattern**: Start with `_insights/` for high-level overview. Use `_tags/` for faceted lookup. Read specific chunk files for detailed content. Check `.cache/` hashes to determine if re-processing is needed.

## How deck-pipeline orchestration works

`deck-pipeline` is a hub-and-spoke orchestrator. It owns the phase state machine; phase-specific skills own execution. There is no orchestrator script -- Claude drives the loop directly from `deck-pipeline/SKILL.md`.

**Eight phases with gate conditions:**

| Phase | Skill | Gate condition |
|-------|-------|----------------|
| 1. Source Inventory | (inline) | `facts-manifest.json` exists + user confirms completeness |
| 2. Personas | (inline) | `persona-map.md` written with full evaluation committee |
| 3. Brainstorm | deck-brainstorm | `synthesized-architecture.md` approved by user |
| 4. Architecture | (review teams) | Three-team review returns CONDITIONAL APPROVE on all lenses |
| 5. Build | slide-generate + slide-pipeline | All slides built + visual verification passed |
| 6. Validate | slide-validate | Council punch list complete, zero blocking items |
| 7. Polish | (inline) | Flow review + balance audit within target ratios |
| 8. Export | slide-pipeline | Visual verification of export artifacts passed |

**Constraint injection is mandatory.** Before dispatching any agent, the orchestrator reads `constraints.json` and injects all applicable constraints into the agent prompt under a `## Constraints (MANDATORY)` section. An agent prompt without this section is malformed and must not be dispatched. Ten default constraints ship with the skill to encode known failure modes. Constraints persist on disk in `{deck_dir}/state/constraints.json` -- they survive session boundaries.

**The "Learn Constraint" protocol:** After any bug fix that required more than one attempt, the orchestrator writes a new constraint to `constraints.json` before ending the session. This prevents the same bug from recurring in future sessions.

**Six anti-pattern guards** are always active, encoding lessons from production sessions: constraint inheritance (never dispatch without reading constraints), visual verification (screenshots required before declaring any phase complete), cross-session persistence (write constraints for recurring bugs), spacing negotiation (ask for measurements before editing), source-before-brainstorm (confirm sources before Phase 2), no HTML to /tmp/ (breaks relative CSS paths).

## How the brainstorm methodology works

`deck-brainstorm` runs structured ideation using three parallel dreamer-skeptic teams. Each team pairs a visionary (dreamer) with a demanding challenger (skeptic). The tension between aspiration and rigor produces content that survives real evaluation committees.

**Three teams, three angles:**

- **Team 1 -- Narrative and Story.** Dreamer: CIO/CTO (transformation mandate). Skeptic: VP Enterprise Architecture (structural rigor). Owns the narrative arc, governing principles, protagonist story, and hallway line.
- **Team 2 -- Operational Proof.** Dreamer: VP Network Engineering (domain scale). Skeptic: Principal Engineer (failure mode awareness). Owns proof slide requirements, two-layer proof patterns, named systems and metrics.
- **Team 3 -- Commercial Threading.** Dreamer: SVP Finance/CFO Proxy (financial narrative). Skeptic: Sr Director Strategic Sourcing (procurement scrutiny). Owns commercial threading, financial bridge methodology, KPI definitions.

**Synthesis reconciles conflicts.** After all three teams complete, their outputs are merged into a single architecture. Conflict resolution rules: proof requirements (Team 2) override aspirational claims (Team 1). Narrative structure (Team 1) takes precedence on act boundaries unless a break serves commercial culmination (Team 3). The threading map ensures each key concept appears on at least 5 slides with no gap larger than 3 consecutive slides.

**12-persona framework** provides pass/fail criteria for every slide. Personas are paired as dreamer-skeptic duos based on their evaluation tendencies.

**8 content principles** guide quality: mechanism-before-outcome, two-layer proof, drumbeat threading, hallway line, protagonist arc, proof not pitch, client specificity, [union-agreement]-safe language.

**Hard gate:** No slide building until the synthesized architecture is approved. Building before brainstorming is complete is the single largest source of rework.

## Skill architecture

Every skill follows the same structure:

- `SKILL.md` -- YAML frontmatter (name, description, triggers) + workflow documentation. This is the skill's interface contract.
- `scripts/` -- Python scripts that do mechanical work. Scripts are thin; the AI does the heavy lifting (classification, judgment, quality assessment).
- `references/` -- Detailed reference docs loaded on demand. Keeps the active context lean -- only load what the current task needs.

**Cross-skill imports** use sys.path manipulation. All skills are siblings under `skills/`, so any skill can import from any other:

```python
_root = Path(__file__).parent.parent.parent  # skills/ directory
sys.path.insert(0, str(_root / "chrome-extract" / "scripts"))
from chrome_extract import extract_layout
```

**Configuration** uses a two-tier resolution order: user-level defaults in `~/.something-wicked/wicked-prezzie/config.json`, then project-level overrides in `skills/slide-config/config.json`. Project wins. User-level keys: `default_font`, `default_fidelity`, `unsplash_api_key`. Project-level keys: `quality_threshold`, `viewport`, `hide_selectors`, `active_theme`, `slide_width_inches`, `slide_height_inches`, `index_dirs`.

## Storage layout

```
~/.something-wicked/wicked-prezzie/          # User-level, shared across projects
  config.json                                # User defaults
  themes/                                    # Theme JSON files (learned, imported, built-in seeds)
  profiles/                                  # Exported .pptprofile files
  registry/                                  # Shared design registry cache
    config.json                              # Registry remote URL, sync status
    palettes/
    strategies/
    iconsets/
  versions/                                  # Deck version metadata (per slug)
  output/                                    # Default output directory
    outline.json                             # Outline output
    slides/                                  # Generated HTML slides
    renders/                                 # PPTX-to-PNG renders
    compare/                                 # HTML vs PPTX comparison images

skills/slide-config/config.json              # Project-level overrides

index/                                       # Generated by slide-learn (alongside source files)
  _manifest.json                             # Freshness record
  _tags/                                     # Faceted tag lookup
  _relationships/                            # Entity cross-references
  _insights/                                 # Key facts, themes, gaps
  .cache/                                    # SHA-256 hashes for incremental indexing
  {source-name}/                             # Per-document chunk directories
    chunk-001.md ... chunk-NNN.md

{deck_dir}/state/                            # Deck pipeline state (per project)
  deck-state.json                            # Phase history, current phase, build progress
  constraints.json                           # Accumulated constraints, survives sessions
  facts-manifest.json                        # Structured digest of source documents
```

## Key design decisions

1. **Let the browser do layout.** Chrome resolves all CSS -- flexbox, grid, absolute positioning, cascading styles. We read computed results instead of re-implementing CSS layout.

2. **Model-driven triage pipeline.** Elements are scored with confidence values and checked against known patterns. High-confidence elements are auto-resolved; low-confidence elements get model inspection. The builder receives a fully-resolved manifest with no ambiguity.

3. **Alpha blending.** CSS rgba colors are pre-blended against the slide background because PPTX shapes don't support CSS-style alpha compositing.

4. **Card text clamping.** Text inside cards is constrained to the card's width, not Chrome's tight bounding box. Encoded as PATTERN-004 in known-patterns.md.

5. **SVG handling.** SVG charts are screenshot in isolation (hide non-SVG content, screenshot, crop). Small decorative SVGs (<30px) are skipped. PATTERN-001 clamps SVG height when content is within 30px below the boundary.

6. **LibreOffice for rendering.** PPTX-to-PDF via `soffice --headless`, then pdftoppm for PDF-to-PNG. No Microsoft PowerPoint required. Runs headless without GUI or permission dialogs.

7. **Iterative visual verification.** After conversion, both HTML and PPTX are rendered to PNG. Claude visually compares each slide and drives fix-and-recheck loops. Scripts are single-pass tools; iteration logic lives in skill definitions.

8. **Structural validation only.** `slide_validate.py` checks shape bounds, negative coordinates, empty slides, and text overflow. Visual fidelity is judged by Claude's vision, not automated pixel scanning.

9. **Manifest-based build.** The manifest is the contract between model judgment (prep) and builder execution. All geometry transforms are pre-resolved as `resolvedRect` fields. The builder does zero classification.

10. **Enriched IR.** Extraction includes `layoutRole` (inferred from CSS class patterns like `card`, `stat`, `badge`) and full `classes` on every element, enabling semantic dispatch instead of pixel-geometry guessing.

11. **Complexity routing.** `html_standardize.py` annotates slides with `COMPLEXITY: high|low` by scanning for SVGs, gradients, pseudo-elements, rotated text. Low-complexity slides should pass in 1-2 attempts; high-complexity slides may need direct fixes.

12. **Two-pass indexing.** Per-document extraction (parallelizable, stateless) is separated from cross-document synthesis (sequential, requires full corpus). Pass 1 runs incrementally via SHA-256 change detection.

13. **Hub-and-spoke deck orchestration.** The orchestrator owns the phase state machine and constraint injection. Phase-specific skills own execution. Constraints persist on disk, not in conversation context, surviving session boundaries.

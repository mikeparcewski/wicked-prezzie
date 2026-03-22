# Pipeline Architecture

```mermaid
graph TD
    subgraph Ideation["💡 Ideation"]
        A[Topic / Brief] --> B[slide-outline]
        B -->|Pyramid Principle| C[Structured Outline JSON]
    end

    subgraph Creation["🎨 Creation"]
        C --> D[slide-theme]
        D -->|Colors, fonts, spacing| E[slide-generate]
        E -->|8 slide types + images| F[Themed HTML Files]
        LEARN[Existing Assets] -.->|style learning| D
        REGISTRY[Design Registry] -.->|palettes, strategies| D
    end

    subgraph Migration["⚡ Migration — parallel"]
        F --> G[slide-html-standardize]
        G -->|Fix viewports, strip animations| H[chrome-extract]
        H -->|One Chrome instance per slide| I[Layout JSON + cached screenshots]
        I --> TRIAGE[slide-triage]
        TRIAGE -->|Confidence scores + pattern detection| PREP[slide-prep]
        PREP -->|Fully-resolved manifest| J[slide-pptx-builder]
        J -->|Native shapes + richtext| K[deck.pptx]
        I --> REVEAL[Reveal.js bundler]
        REVEAL --> HTML[deck.html]
    end

    subgraph Quality["✅ Quality"]
        K --> L[slide-validate]
        L -->|Deck audit: 5 categories| M{Pass?}
        M -->|≥ 80 PASS| N[slide-render]
        M -->|< 80 REVIEW/FAIL| O[Fix + re-run]
        O --> G
        N -->|PPTX → PNG| P[slide-compare]
        P -->|HTML vs PPTX diff| Q[✔ Ship it]
        L -.->|content lint| LINT[Bullets, titles, stats, quotes, CTAs]
        L -.->|consistency| CONSIST[Palette, headings, cadence, notes]
    end

    subgraph Versioning["📋 Versioning"]
        K --> VER["{slug}_v{N}.pptx"]
        HTML --> VER2["{slug}_v{N}.html"]
    end

    style Ideation fill:#1a1a2e,stroke:#a100ff,color:#fff
    style Creation fill:#1a1a2e,stroke:#f59e0b,color:#fff
    style Migration fill:#1a1a2e,stroke:#0891b2,color:#fff
    style Quality fill:#1a1a2e,stroke:#10b981,color:#fff
    subgraph Feedback["💬 Feedback"]
        K -.->|Export to Word| WORD[Executive Summary .docx]
        WORD -.->|Team reviews with inline comments| FB[deck-feedback]
        FB -->|Alignment + divergence report| ACTIONS[Prioritized Action Items]
        ACTIONS -.->|Revise narrative| E
    end

    style Feedback fill:#1a1a2e,stroke:#e879f9,color:#fff
    style Versioning fill:#1a1a2e,stroke:#6b6b80,color:#fff
```

## Stages

### Ideation

| Skill | Purpose |
|---|---|
| **slide-outline** | Structures a topic into a Pyramid Principle narrative — setup, evidence, close. Produces outline JSON with slide types, titles as assertions, and speaker notes. |

### Creation

| Skill | Purpose |
|---|---|
| **slide-theme** | Defines brand identity as structured JSON — colors, fonts, spacing, layout tokens. Validates contrast ratios and hierarchy. Three built-in themes. Extracts styles from existing PPTX/PDF/images. Manages portable profiles and a git-backed shared design registry. |
| **slide-generate** | Transforms outline JSON into individual themed HTML slide files. 8 slide types: title, content, stats, comparison, quote, section divider, CTA, blank. Sources images from Unsplash or icon sets with attribution. |

### Migration

| Skill | Purpose |
|---|---|
| **slide-html-standardize** | Normalizes HTML for Chrome extraction — adds viewport meta, wraps in `.slide` div, strips CSS animations and external CDN dependencies. Annotates complexity (high/low) for pipeline routing. |
| **chrome-extract** | Drives Chrome headless to render each slide and extract computed bounding boxes, colors, fonts, and inline formatting as structured JSON. Runs in parallel — one Chrome instance per slide. |
| **slide-triage** | Scores each element with confidence (0.0–1.0) and checks against 10 known-pattern signatures (SVG bleed, accent bars, rotation, card overflow, badge collision). Detects collision risks. Outputs findings JSON. |
| **slide-prep** | Auto-resolves high-confidence elements (>= 0.85) with geometry transforms. Flags low-confidence elements for model inspection. Produces a fully-resolved manifest with `resolvedRect` coordinates — no ambiguity at build time. |
| **slide-pptx-builder** | Maps manifest to native python-pptx objects — shapes, richtext boxes, embedded SVG screenshots. Handles alpha blending, card text clamping, and coordinate mapping. Zero classification — the manifest is the contract. |
| **slide-html-to-pptx** | Orchestrates parallel extraction + sequential PPTX assembly. Caches screenshots for SVG cropping and fallback slides. |

### Quality

| Skill | Purpose |
|---|---|
| **slide-validate** | 5-category deck audit (structure 25%, content 30%, layout 20%, consistency 15%, lint 10%). Content lint catches bullet overload, title hygiene, stat formatting, quote attribution, passive voice, CTA completeness. Consistency checks heading sizes, palette adherence, template distribution, section cadence, speaker notes. Layout checks bounds, overflow, and element overlap. Scoring: PASS ≥ 80, REVIEW 60–79, FAIL < 60. Supports re-audit with delta tracking. |
| **slide-render** | Renders PPTX to PNG via LibreOffice headless PDF export + pdftoppm. Generates contact-sheet montages for quick visual review. |
| **slide-compare** | Produces paired HTML/PPTX screenshots for side-by-side fidelity comparison. Catches visual regressions after conversion. |

### Supporting

| Skill | Purpose |
|---|---|
| **slide-design** | Reference-only skill with design principles, quality rubric, CSS contract (zone naming conventions and fallback layout), and contextual hints + REVIEW flagging system. |
| **slide-config** | Two-tier configuration — user-level (`~/.something-wicked/wicked-prezzie/config.json`) for defaults shared across projects, project-level (`skills/slide-config/config.json`) for per-project overrides. |
| **slide-pipeline** | End-to-end orchestrator. Three fidelity tiers (best/draft/rough) with multi-pass verification loops. Dual-format output (PPTX + Reveal.js HTML). Non-destructive versioning (`{slug}_v{N}.pptx`). Session-scoped edit coordination locks. |

### Source Intelligence

| Skill | Purpose |
|---|---|
| **slide-learn** | Indexes source documents (PDF, PPTX, DOCX, HTML, images) into searchable markdown with YAML frontmatter. Two-pass: per-document extraction (parallelizable, uses vision for binaries) then cross-document synthesis (`_insights/`, `_tags/`, `_relationships/`). Hash-based incremental re-indexing. |

### Deck Methodology

| Skill | Purpose |
|---|---|
| **deck-pipeline** | Hub-and-spoke orchestrator for full deck-building workflows. 8-phase state machine (source inventory → personas → brainstorm → architecture → build → validate → polish → export) with constraint injection, gate conditions, and 10 default constraints derived from production session analysis. |
| **deck-brainstorm** | Dreamer-skeptic brainstorm methodology with 3-team structure (narrative/operational/commercial). Generative persona framework with pass/fail criteria. 8 reusable content principles (mechanism-before-outcome, two-layer proof, hallway line, etc.). Synthesis rules with conflict resolution. |
| **deck-checkpoint** | Session synthesis — captures decisions, artifacts produced, and next steps. Preserves continuity across sessions. |

### Feedback

| Skill | Purpose |
|---|---|
| **deck-feedback** | Parses inline comments from Word (.docx) documents reviewed by team members. Classifies sentiment (endorsement, concern, suggestion), clusters comments by passage, detects alignment (multiple reviewers agree) vs divergence (reviewers disagree), and generates prioritized action items. Output as markdown, JSON, or Word report. |
| **slide-treatment-log** | Records per-slide fix history after each render-compare attempt. Provides the audit trail that closes the feedback loop from visual comparison failures back to known-patterns.md. Identifies fix candidates for promotion to permanent patterns. |

## Storage

```
~/.something-wicked/wicked-prezzie/     User-level (shared across projects)
  config.json                           Defaults: font, fidelity, API keys
  themes/                               Theme JSON files
  profiles/                             Exported .pptprofile files
  registry/                             Shared design asset cache
  versions/                             Deck version metadata
  index/                              Generated document indexes (per source dir)
    _manifest.json                    Index metadata and freshness
    _insights/                        Fast-path summaries (key-facts, themes, gaps)
    _tags/                            Content-type cross-references
    _relationships/                   Cross-document entity links

skills/slide-config/config.json         Project-level overrides
  quality_threshold, viewport, active_theme, slide dimensions
```

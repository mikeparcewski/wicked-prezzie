# wicked-prezzie

HTML slides to editable PowerPoint. Native shapes and formatted text, not screenshots.

A Claude Code / Gemini CLI plugin that builds presentations the way you actually work — start with an idea, refine it, generate slides, refine with your team, and export a polished deck. Jump in at any stage, go back when something's off, and iterate until it's right.

## Quick start

### Claude Code

Add the marketplace, then install:

```
/plugin marketplace add mikeparcewski/wicked-prezzie
/plugin install wicked-prezzie
```

Or for local development:

```bash
git clone https://github.com/mikeparcewski/wicked-prezzie.git
claude --plugin-dir ./wicked-prezzie
```

### Gemini CLI

Install the extension directly:

```bash
gemini extensions install https://github.com/mikeparcewski/wicked-prezzie
```

Verify it's loaded:

```bash
gemini extensions list
```

See [GEMINI.md](GEMINI.md) for tool name mappings.

### Prerequisites

```bash
pip install python-pptx beautifulsoup4 lxml Pillow
```

- **Google Chrome** — headless layout extraction
- **LibreOffice** — PPTX rendering (`brew install --cask libreoffice` / `apt install libreoffice`)
- **poppler** — PDF to PNG (`brew install poppler` / `apt install poppler-utils`)

Missing dependencies are auto-detected on first run.

---

## How you use it

```
Idea → Refine → Generate → Refine with your team → Final Output
          ↑                        |
          └────────────────────────┘
```

You can start anywhere, skip steps you don't need, and loop back whenever something changes. The whole point is iteration — with yourself, with your content, and with your team.

### 1. Start with an idea

You have a topic, a brief, a pile of documents, or just a rough notion of what you need to present.

```
"I need a board deck about our platform strategy. 15 minutes.
 They care about ROI, timeline, and risk."
```

```
"I have RFP documents in ./source-materials/ — index them so we
 can build a response deck."
```

```
"Run a brainstorm — I want dreamer-skeptic teams to explore
 different angles before we commit to a narrative."
```

Behind the scenes: source documents get indexed into a searchable knowledge base. Brainstorm teams generate competing perspectives. The Pyramid Principle structures your argument — lead with the conclusion, group by evidence, build a narrative arc.

### 2. Refine the plan

Before any slides exist, you shape the story. Review the outline, challenge the structure, reorder sections, sharpen the message.

```
"Move the risk section before the timeline — they'll want to
 hear about risks early."
```

```
"The opening is too generic. Make it specific to our Q1 results."
```

```
"Add a comparison slide: our approach vs. the two alternatives."
```

This is where most of the thinking happens. The outline is cheap to change — slides are not. Get the narrative right here.

### 3. Generate slides

Turn the refined outline into actual slides. Pick a theme, add images, choose your slide types.

```
"Generate the slides with the corporate-light theme"
"Add Unsplash photos for the market opportunity slides"
"Use our brand — learn it from ./brand-guide.pdf"
"Make it feel dark and techy with purple accents"
```

Eight slide types (title, content, stats, comparison, quote, section divider, CTA, blank), three built-in themes, or extract one from your existing brand assets.

Already have HTML slides from ChatGPT, Claude, Gemini, or reveal.js? Skip straight here:

```
"Convert the slides in ./my-deck/ to PowerPoint"
```

### 4. Refine — on your own and with your team

This is where the real iteration happens, and it works at two levels.

**Refine it yourself** — check quality, fix issues, re-generate specific slides.

```
"Audit the deck"
"The card grid on slide 4 is overlapping — fix it"
"Re-convert just slides 3 and 7"
"The CTA slide needs a stronger closing — rework it"
```

The plugin runs a 5-category quality audit, renders the PPTX to PNG for visual comparison, and iterates on problem slides until they pass.

**Refine it with your team** — export the narrative as a Word document for group review. Everyone adds inline comments using normal Word functionality. Then bring the feedback back in.

```
"Analyze the feedback in ./exec-summary-reviewed.docx"
```

The plugin parses every comment, maps it to the document section, and tells you:

- **Where reviewers agree** — aligned concerns are your highest-priority changes
- **Where reviewers diverge** — these need a conversation before you can edit
- **What it means for the narrative** — which sections are hot, which were skipped, whether the overall direction holds

```
"Generate the feedback report as a Word doc to share back"
"Address the aligned concerns, then regenerate those slides"
```

This is the group refinement loop: generate → share for review → analyze feedback → refine → share again. Each round tightens the narrative based on real input from your stakeholders.

You can also loop back further — change the outline, swap the theme, re-run the brainstorm — at any point.

### 5. Final output

Export as PPTX, HTML (Reveal.js), or both. Versioned automatically.

```
"Export as both PPTX and HTML"
"Render the final version to PNG so I can preview"
```

---

## What you can do

21 skills grouped by what you're trying to accomplish. You don't need to remember skill names — just say what you want.

### Deck strategy and planning

| Skill | What it does | Say... |
|---|---|---|
| **deck-brainstorm** | Dreamer-skeptic brainstorm — generates and pressure-tests deck architecture | "brainstorm deck ideas" / "run a brainstorm" |
| **deck-pipeline** | Full 8-phase orchestrator from source material to finished export | "build a full deck about X" |
| **deck-checkpoint** | Synthesize a session into a durable checkpoint with decisions + next steps | "checkpoint this" / "where were we" |
| **deck-feedback** | Parse Word comment annotations; synthesize reviewer alignment and divergence | "analyze feedback" / "parse comments" |

### Content generation

| Skill | What it does | Say... |
|---|---|---|
| **slide-learn** | Index source docs (PDF, PPTX, DOCX, HTML, images) into searchable chunks | "index this document" / "learn from this" |
| **slide-outline** | Plan presentation structure using the Pyramid Principle | "outline a deck" / "make a presentation about X" |
| **slide-generate** | Generate themed HTML slides from an outline with optional images | "generate the slides" / "build from the outline" |
| **slide-config** | View and set project settings (viewport, fonts, quality thresholds) | "change settings" / "configure viewport" |

### Design and theme

| Skill | What it does | Say... |
|---|---|---|
| **slide-theme** | Set colors, fonts, spacing; extract brand from assets; share via profiles | "set colors" / "apply a theme" / "dark theme" |
| **slide-design** | Design principles and quality rubric (reference only — no actions) | "design rules" / "quality rubric" |

### Conversion to PowerPoint

| Skill | What it does | Say... |
|---|---|---|
| **slide-pipeline** | End-to-end HTML → PPTX with iterative visual verification (default path) | "convert these slides" / "make a PowerPoint" |
| **slide-html-to-pptx** | Quick HTML → PPTX without the full QA loop | "just convert" / "skip validation" |
| **slide-html-standardize** | Normalize AI-generated HTML before conversion (viewports, animations, wrappers) | "standardize these slides" |
| **chrome-extract** | Chrome headless extraction of computed layout, colors, and fonts | *(runs automatically during conversion)* |
| **slide-triage** | Confidence scoring and known-pattern detection per element | *(runs automatically during conversion)* |
| **slide-prep** | Auto-resolve triage findings into a fully-resolved build manifest | *(runs automatically during conversion)* |
| **slide-pptx-builder** | Map the manifest to native PPTX shapes with alpha blending and clamping | *(runs automatically during conversion)* |

### Quality and iteration

| Skill | What it does | Say... |
|---|---|---|
| **slide-validate** | 5-category deck audit — structure, content, layout, consistency, lint | "audit my deck" / "validate the deck" |
| **slide-render** | Render PPTX to PNG for visual review via LibreOffice headless | "show me the slides" / "preview the PPTX" |
| **slide-compare** | Side-by-side visual diff of HTML source vs PPTX output | "does it look right" / "check fidelity" |
| **slide-treatment-log** | Track per-slide fix history; promote fixes to permanent patterns | *(runs automatically during iteration)* |

---

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

---

## Known tradeoffs

- Gradients become solid blended colors (PPTX gradient support is limited)
- Animations are stripped (static snapshot of the final state)
- Font metrics differ between CSS and Calibri (compensated, not perfect)
- Small decorative SVGs under 30px are skipped

## Documentation

- **[Pipeline architecture](PIPELINE.md)** — Stage-by-stage technical breakdown with Mermaid diagram
- **[Use cases & examples](USE-CASES.md)** — Practical paths from simplest to most involved
- **[How it works](ARCHITECTURE.md)** — Technical deep-dive: extraction, building, triage, indexing
- **[Gemini CLI](GEMINI.md)** — Tool name mapping for Gemini users

## License

MIT

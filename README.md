# wicked-prezzie

HTML slides to editable PowerPoint. Native shapes and formatted text, not screenshots.

A Claude Code / Gemini CLI plugin that builds presentations the way you actually work — start with an idea, refine it, generate slides, refine with your team, and export a polished deck. Jump in at any stage, go back when something's off, and iterate until it's right.

## Quick start

### Claude Code

Add the marketplace, then install the plugin:

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

Clone the repo and run Gemini inside it — it auto-discovers the extension via `gemini-extension.json`:

```bash
git clone https://github.com/mikeparcewski/wicked-prezzie.git
cd wicked-prezzie
gemini
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

## What's under the hood

21 skills handle the mechanics. You don't need to know these — just describe what you want and the plugin routes to the right tools.

| Stage | Skills | What they do |
|---|---|---|
| **Idea** | slide-learn, deck-brainstorm | Index source docs, run structured brainstorms with dreamer-skeptic teams |
| **Refine (plan)** | slide-outline, deck-pipeline | Pyramid Principle structure, 8-phase orchestration with constraint persistence |
| **Generate** | slide-theme, slide-generate, slide-html-standardize | Themed HTML slides, brand extraction, normalize AI-generated HTML |
| **Convert** | chrome-extract, slide-triage, slide-prep, slide-pptx-builder, slide-html-to-pptx | Chrome headless extraction → confidence scoring → manifest → native PPTX |
| **Refine (you)** | slide-validate, slide-render, slide-compare, slide-treatment-log | 5-category audit, PPTX→PNG rendering, visual diff, fix history |
| **Refine (team)** | deck-feedback | Parse Word comments → alignment/divergence → prioritized actions |
| **Support** | slide-pipeline, slide-design, slide-config, deck-checkpoint | Orchestration, design reference, settings, session continuity |

Works with HTML from anywhere — ChatGPT, Claude, Gemini, reveal.js, or hand-coded.

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

# wicked-prezzie

HTML slides to editable PowerPoint. Native shapes and formatted text, not screenshots.

A Claude Code / Gemini CLI plugin that builds presentations the way you actually work — start with an idea, refine it, generate slides, refine again, and export a polished deck. Jump in at any stage, go back when something's off, and iterate until it's right.

## Quick start

### Claude Code

```bash
git clone https://github.com/mikeparcewski/wicked-prezzie.git
cd wicked-prezzie
claude
```

### Gemini CLI

```bash
git clone https://github.com/mikeparcewski/wicked-prezzie.git
cd wicked-prezzie
gemini
```

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

The workflow follows a natural progression. You can start anywhere, skip steps you don't need, and go back to any earlier stage when things change.

```
Idea → Refine → Generate → Refine → Final Output
```

### 1. Start with an idea

You have a topic, a brief, a pile of documents, or just a rough notion of what you need to present. Tell the plugin what you're working with.

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

What happens behind the scenes: source documents get indexed into a searchable knowledge base. Brainstorm teams generate competing perspectives. The Pyramid Principle structures your argument — lead with the conclusion, group by evidence, build a narrative arc.

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

The plugin generates themed HTML slides with proper typography, spacing, and contrast. Eight slide types (title, content, stats, comparison, quote, section divider, CTA, blank), three built-in themes, or extract one from your existing brand assets.

Already have HTML slides from ChatGPT, Claude, Gemini, or reveal.js? Skip straight here:

```
"Convert the slides in ./my-deck/ to PowerPoint"
```

### 4. Refine the output

This is where you iterate. Check quality, fix issues, re-generate specific slides, compare versions.

```
"Audit the deck"
"The card grid on slide 4 is overlapping — fix it"
"Re-convert just slides 3 and 7"
"Compare the HTML originals against the PPTX"
"The CTA slide needs a stronger closing — rework it"
```

The plugin runs a 5-category quality audit (structure, content, layout, consistency, lint), renders the PPTX to PNG for visual comparison, and iterates on problem slides until they match. You can also go back — change the outline, regenerate a section, swap the theme.

### 5. Get team feedback

Export the deck as a Word document for team review. Everyone adds inline comments using normal Word functionality. Then parse the feedback.

```
"Analyze the feedback in ./exec-summary-reviewed.docx"
```

The plugin extracts every comment, maps it to the document section, and produces a feedback report:
- **Where reviewers agree** — aligned concerns are your highest-priority changes
- **Where reviewers diverge** — these need a conversation, not just an edit
- **What it means for the narrative** — hotspots, blind spots, structural signals

```
"Generate the feedback report as a Word doc to share with the team"
"Address the aligned concerns first, then regenerate those slides"
```

Then loop back to step 2 or 3 with the feedback incorporated.

### 6. Final output

Export as PPTX, HTML (Reveal.js), or both. Versioned automatically.

```
"Export as both PPTX and HTML"
"Render the final version to PNG so I can preview"
```

---

## The key idea: go back anytime

This isn't a one-way pipeline. At any point you can:

- **Go back to the outline** when the narrative isn't landing
- **Swap the theme** after seeing the generated slides
- **Regenerate specific slides** without rebuilding the whole deck
- **Re-run the brainstorm** if the direction feels off
- **Incorporate feedback** and regenerate only what changed

```
"Actually, rethink the structure — lead with the customer story instead"
"Change the theme to warm-dark and regenerate"
"Just redo slides 5-8 with the updated messaging"
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
| **Refine (output)** | slide-validate, slide-render, slide-compare, slide-treatment-log | 5-category audit, PPTX→PNG rendering, visual diff, fix history |
| **Feedback** | deck-feedback | Parse Word comments → alignment/divergence → prioritized actions |
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

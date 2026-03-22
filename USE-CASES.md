# Use Cases

Practical paths through wicked-prezzie, from simplest to most involved. Every path produces native, editable PowerPoint — real shapes and formatted text, not screenshots.

---

## Quick wins (under 5 minutes)

### "I need a deck for a meeting tomorrow"

Start with nothing. Describe your audience and topic, and the plugin structures your content, generates themed slides, and converts to PPTX.

```
"I'm presenting our Q1 results to the leadership team.
 10 minutes. They want revenue, growth drivers, and what's next."
```

What happens: **slide-outline** builds a Pyramid Principle narrative (lead with the conclusion, group by argument), **slide-generate** produces themed HTML, and the pipeline converts to PPTX. You get a versioned deck with speaker notes.

### "Convert these HTML slides to PowerPoint"

Bring HTML from anywhere — ChatGPT, Claude, Gemini, reveal.js, hand-coded. Drop the files in a directory and point the plugin at them.

```
"Convert the slides in ./my-deck/ to PowerPoint"
```

The pipeline standardizes the HTML (fixes viewports, strips animations, adds wrappers), extracts layout via Chrome headless in parallel, and builds native PPTX shapes. Slides extract concurrently — a 10-slide deck finishes in ~8 seconds.

### "Make it match our brand"

Apply your company's visual identity without rebuilding slides.

```
"Use these colors: primary #2563EB, accent #F59E0B, dark backgrounds"
"Learn our brand from ./brand-guide.pdf"
"Make it feel clean and minimal"
```

Themes drive the entire pipeline — colors, fonts, spacing, contrast ratios. Three built-in themes are included, or extract one from existing PPTX, PDF, or brand images.

---

## Content workflows

### Board presentation from a brief

For high-stakes presentations where narrative structure matters.

```
1. "I'm presenting our AI platform strategy to the board.
    They care about ROI, timeline, and risk. 15 minutes."
2. "Generate the slides with the corporate-light theme"
3. "Add Unsplash photos for the market opportunity slides"
4. "Audit the deck"
5. "The CTA slide needs a stronger closing — rework it"
```

**Skills used**: slide-outline → slide-theme → slide-generate → slide-pipeline → slide-validate

### Sales deck from bullet points

Skip the blank page when you already have content.

```
1. "Here are my talking points for the customer pitch: [paste bullets]"
2. "Turn these into a deck — use stats slides for the metrics"
3. "Add a comparison slide: us vs competitor on these 4 dimensions"
4. "Export as both PPTX and HTML so I can present from the browser too"
```

**Skills used**: slide-generate → slide-pipeline (dual-format output)

### Training deck with many slides

For longer decks where consistency across 20+ slides matters.

```
1. "Create an onboarding deck for new engineers. Cover: architecture,
    dev workflow, deployment, monitoring, and team norms. ~25 slides."
2. "Use section dividers between each topic"
3. "Check consistency across the whole deck"
4. "The heading sizes are drifting after slide 15 — fix them"
```

**Skills used**: slide-outline → slide-generate → slide-pipeline → slide-validate (consistency checks)

---

## Migration workflows

### AI-generated HTML from another tool

HTML from ChatGPT, Claude, or Gemini often has inconsistent viewports, CDN dependencies, and CSS animations that break extraction. The standardizer handles all of this.

```
"I generated these slides in ChatGPT. Convert them to PowerPoint."
```

**What the pipeline fixes**: missing viewport meta, missing `.slide` wrappers, external font/CSS references, CSS animations and transitions, inconsistent dimensions.

### Reveal.js deck to PowerPoint

Existing reveal.js presentations convert directly. The standardizer strips the framework scaffolding and extracts individual slides.

```
"Convert my reveal.js presentation at ./talk/index.html to PPTX"
```

### Batch conversion with selective re-processing

When only some slides need attention after conversion.

```
1. "Convert all slides in ./deck/"
2. "Slides 3 and 7 have layout issues — just re-convert those two"
3. "Render the PPTX to PNG so I can review"
4. "Compare the HTML originals against the PPTX output"
```

**Pipeline flags**: `--slides slide-03.html,slide-07.html` for selective processing, `--no-standardize` when HTML is already clean.

---

## Source intelligence workflows

### "Index my reference materials before we start"

Feed source documents to slide-learn before building a deck. The index becomes a searchable knowledge base that deck-building agents query instead of re-reading raw files.

```
1. "Index the RFP documents in ./source-materials/"
2. "What financial figures did you find?"     → grep _insights/key-facts.md
3. "Which documents mention their AI strategy?" → grep _tags/technical.md
4. "Now build a deck using those materials"    → deck-pipeline reads the index
```

**Skills used**: slide-learn → deck-pipeline

### "Brainstorm before building"

Run structured ideation with dreamer-skeptic teams before committing to slide architecture. Three teams generate independent perspectives, then synthesis resolves conflicts into an approved plan.

```
1. "Run a brainstorm for the proposal deck — dreamer-skeptic teams"
2. "Synthesize the three team outputs into a slide plan"
3. "Run the three-team review — narrative, commercial, technical"
4. "All three teams approve. Now build the slides."
```

**Skills used**: deck-brainstorm → deck-pipeline (architecture phase) → slide-generate

### "I keep fixing the same bugs across sessions"

Constraints persist in `constraints.json` — learned once, enforced everywhere. After fixing a recurring issue, the pipeline writes a constraint that every future build agent receives.

```
"The centering keeps breaking — add a constraint for that"
→ constraint written to constraints.json
→ every future build agent receives it in their prompt
→ the bug never recurs
```

**Skills used**: deck-pipeline (constraint persistence)

---

## Theming workflows

### Extract brand from existing assets

Already have a branded deck or design guide? Extract the theme automatically.

```
"Learn my brand from last-quarter.pptx and our-brand.pdf"
"How confident are you in the extracted colors?"
"Adjust the accent — make it warmer"
```

The style learning system extracts colors, fonts, and layout patterns with confidence scores. Low-confidence extractions are flagged for review.

### Share themes across a team

Themes are portable. Export to a `.pptprofile` file and share it.

```
"Export my theme as a .pptprofile"
"Import the profile my designer sent me"
"Push our palette to the design registry"
```

Profiles live in `~/.something-wicked/wicked-prezzie/profiles/`. The git-backed design registry keeps palettes, strategies, and icon sets consistent across projects and team members.

### Vibe-based theming

Don't know your hex codes? Describe the feeling.

```
"Make it dark and techy with purple accents"
"I want something clean and executive — think McKinsey"
"Warm and approachable, not corporate"
```

The theme skill matches vibe descriptions against existing themes and registry palettes using delta-E color comparison.

---

## Quality and iteration

### Full deck audit

Run the 5-category quality gate after any conversion or generation.

```
"Audit my deck"
```

Returns scores for structure (25%), content (30%), layout (20%), consistency (15%), and lint (10%). PASS at 80+, REVIEW at 60-79, FAIL below 60. Each finding includes specific remediation.

### Content lint only

Quick pass on content quality without layout analysis.

```
"Lint my deck"
```

Catches: bullet overload (>5 per slide), missing titles, unformatted statistics, unattributed quotes, passive voice, incomplete CTAs.

### Visual fidelity check

Compare the original HTML against the converted PPTX, side by side.

```
"Compare the HTML originals against the PowerPoint"
"Render the PPTX to PNG so I can see what it looks like"
"Create a montage of all slides"
```

**slide-render** uses LibreOffice headless for rendering — no GUI or automation consent needed. Runs on macOS, Linux, and Windows.

### Cross-deck consistency

Compare two versions of a deck, or check brand alignment across multiple decks.

```
"Compare sales-v1.pptx and sales-v2.pptx"
"Check that all three regional decks use the same palette"
```

### Iterative fix loop

The pipeline supports a fix-verify cycle at any fidelity tier.

```
1. "Convert my slides" (draft fidelity — single clean pass)
2. "The card grid on slide 4 is overlapping"
3. "Re-convert slide 4 and validate"
4. "Now run best fidelity on the whole deck" (multi-pass verification)
```

**Fidelity tiers**: `best` runs multi-pass verify loops, `draft` does a single clean pass (default), `rough` drops structure fast for human polish.

---

## Configuration

### Per-project settings

```
"Set quality threshold to 70 for this project"
"Use 1920x1080 viewport instead of 1280x720"
"Hide .nav and .footer elements during extraction"
"Set slide dimensions to 16:9 widescreen"
```

Project settings live in `skills/slide-config/config.json` and override user defaults.

### User-level defaults

```
"Set my default font to Inter"
"Always use draft fidelity unless I say otherwise"
"Store my Unsplash API key"
```

User settings live in `~/.something-wicked/wicked-prezzie/config.json` and apply across all projects.

---

## Feedback and iteration with your team

### "The team reviewed the exec summary — what did they say?"

After distributing a Word document for team review (using standard inline comments), parse all comments and generate a structured feedback report.

```
1. "Analyze the feedback in ./exec-summary-reviewed.docx"
2. "Where do the reviewers agree?"
3. "Show me the divergence points — where do people disagree?"
4. "Generate the feedback report as a Word doc to share with the team"
```

**Skills used**: deck-feedback (parse → analyze → report)

The report shows:
- **Alignment** — where multiple reviewers raised the same concern (high-priority changes)
- **Divergence** — where reviewers disagree on the same passage (needs a conversation, not just an edit)
- **Narrative implications** — attention hotspots, silent sections, overall direction
- **Prioritized action items** — ranked by severity and number of reviewers

### "Close the feedback loop"

Combine feedback analysis with deck iteration for a complete review cycle.

```
1. "Build the exec summary deck from these documents"    → deck-pipeline
2. "Export the key narrative as a Word doc for review"    → generate_report (docx)
3. "The team has reviewed it — analyze their comments"   → deck-feedback
4. "Address the aligned concerns first"                   → targeted edits
5. "Regenerate the slides that changed"                   → slide-generate + pipeline
6. "Send out the updated version for final review"
```

**Skills used**: deck-pipeline → deck-feedback → slide-generate → slide-pipeline

---

## Combining paths

Most real work combines multiple paths. A typical end-to-end session:

```
1. "Learn our brand from the attached PDF"          → theme extraction
2. "I need a board deck about our platform roadmap"  → outline + generate
3. "Add comparison slides for build vs buy"          → generate additional slides
4. "Convert everything to PPTX"                      → full pipeline
5. "Audit it"                                        → quality gate
6. "Fix the overflow on slide 8"                     → targeted re-conversion
7. "Render the final version and give me both        → dual-format output
    PPTX and HTML"
8. "Export as sales-kickoff_v1.pptx"                 → versioned output
```

Each step is independent — jump in anywhere, skip what you don't need, repeat what matters.

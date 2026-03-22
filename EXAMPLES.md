# Examples

Deeper scenarios beyond the basics in [README.md](README.md). Each shows a multi-step workflow you can adapt.

---

## Source-grounded decks

### Index → brainstorm → build

Feed source documents first, then let the brainstorm teams work from real content instead of hallucinating.

```
1. "Index the RFP documents in ./source-materials/"
2. "What financial figures did you find?"
3. "Which documents mention their AI strategy?"
4. "Run a brainstorm — dreamer-skeptic teams"
5. "Synthesize the three team outputs into a slide plan"
6. "All three teams approve. Now build the slides."
```

The index becomes a searchable knowledge base. Brainstorm teams and generation agents query `_insights/key-facts.md` and `_tags/` instead of re-reading raw files.

### Constraint persistence across sessions

After fixing a recurring issue, the pipeline writes a constraint that every future build agent receives. Constraints survive session boundaries.

```
"The centering keeps breaking — add a constraint for that"
→ constraint written to constraints.json
→ every future build agent receives it in their prompt
→ the bug never recurs
```

---

## Migration scenarios

### AI-generated HTML (ChatGPT, Claude, Gemini)

AI-generated HTML often has inconsistent viewports, CDN dependencies, and CSS animations that break extraction. The standardizer handles all of this automatically.

```
"I generated these slides in ChatGPT. Convert them to PowerPoint."
```

What the pipeline fixes: missing viewport meta, missing `.slide` wrappers, external font/CSS references, CSS animations and transitions, inconsistent dimensions.

### Reveal.js to PowerPoint

```
"Convert my reveal.js presentation at ./talk/index.html to PPTX"
```

The standardizer strips the framework scaffolding and extracts individual slides.

### Selective re-processing

When only some slides need attention after conversion.

```
1. "Convert all slides in ./deck/"
2. "Slides 3 and 7 have layout issues — just re-convert those two"
3. "Render the PPTX to PNG so I can review"
4. "Compare the HTML originals against the PPTX output"
```

---

## Theming deep-dives

### Extract brand from existing assets

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

The git-backed design registry keeps palettes, strategies, and icon sets consistent across projects and team members.

### Vibe-based theming

Don't know your hex codes? Describe the feeling.

```
"Make it dark and techy with purple accents"
"I want something clean and executive — think McKinsey"
"Warm and approachable, not corporate"
```

Matches vibe descriptions against existing themes and registry palettes using delta-E color comparison.

---

## Quality deep-dives

### Full deck audit breakdown

```
"Audit my deck"
```

Returns scores for structure (25%), content (30%), layout (20%), consistency (15%), and lint (10%). PASS at 80+, REVIEW at 60-79, FAIL below 60. Each finding includes specific remediation.

### Content lint

Quick pass on content quality without layout analysis.

```
"Lint my deck"
```

Catches: bullet overload (>5 per slide), missing titles, unformatted statistics, unattributed quotes, passive voice, incomplete CTAs.

### Fidelity tiers

The pipeline supports three quality levels:

- **best** — multi-pass verify loops, visual comparison on every slide
- **draft** — single clean pass (default)
- **rough** — drops structure fast for human polish

```
1. "Convert my slides"                              → draft
2. "The card grid on slide 4 is overlapping"
3. "Re-convert slide 4 and validate"
4. "Now run best fidelity on the whole deck"         → best
```

### Cross-deck consistency

Compare versions or check brand alignment across multiple decks.

```
"Compare sales-v1.pptx and sales-v2.pptx"
"Check that all three regional decks use the same palette"
```

---

## Team feedback loop

### Full review cycle

```
1. "Build the exec summary deck from these documents"
2. "Export the key narrative as a Word doc for review"
3. "The team has reviewed it — analyze their comments"
4. "Where do the reviewers agree?"
5. "Show me the divergence points"
6. "Generate the feedback report as a Word doc to share back"
7. "Address the aligned concerns first"
8. "Regenerate the slides that changed"
9. "Send out the updated version for final review"
```

Each round tightens the narrative based on real input from your stakeholders.

---

## Configuration

### Per-project settings

```
"Set quality threshold to 70 for this project"
"Use 1920x1080 viewport instead of 1280x720"
"Hide .nav and .footer elements during extraction"
"Set slide dimensions to 16:9 widescreen"
```

### User-level defaults

```
"Set my default font to Inter"
"Always use draft fidelity unless I say otherwise"
"Store my Unsplash API key"
```

User settings apply across all projects. Project settings override user defaults.

---

## End-to-end session

A typical session combining multiple workflows:

```
1. "Learn our brand from the attached PDF"              → theme
2. "I need a board deck about our platform roadmap"     → outline + generate
3. "Add comparison slides for build vs buy"             → generate more
4. "Convert everything to PPTX"                         → pipeline
5. "Audit it"                                           → quality gate
6. "Fix the overflow on slide 8"                        → targeted fix
7. "The team reviewed the exec summary — analyze it"    → feedback
8. "Address the aligned concerns, regenerate"           → iterate
9. "Export as sales-kickoff_v1.pptx and HTML"           → ship
```

Each step is independent — jump in anywhere, skip what you don't need, repeat what matters.

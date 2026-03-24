---
name: deck-diff
description: |
  Visual and structural comparison of deck versions. Diffs outlines, themes,
  and rendered slides with highlighted changes. Works across versions of the
  same deck or between two different decks.

  Use when: "what changed", "compare versions", "diff the deck", "before and after",
  "what's different", "show me the changes", "version comparison", "diff these decks"
---

# deck-diff — Deck Version Comparison

Structural and visual diff for deck versions. Compares outlines, themes, slide
HTML, and rendered output — producing a markdown report and optional HTML visual
diff page. Works on two versions of the same deck or two entirely different decks.

## When to Use

- After editing a deck — see what changed since the last version
- Before finalizing — compare current state against the approved outline
- When reviewing someone else's changes to a shared deck
- To compare two different decks structurally (e.g., "how does deck A differ from deck B")
- After a review round — see what was changed in response to feedback

---

## Diff Modes

### `--outline` — Outline Diff

Compares two outline JSON files and reports structural changes.

**Input**: Two outline.json paths (or a single deck directory if version history exists).

**Detection**:
- Added slides (present in B, absent in A)
- Removed slides (present in A, absent in B)
- Reordered slides (same content, different position)
- Changed slide titles or key messages
- Modified narrative arc or act structure
- Added/removed bullet points within slides

**Output**: Markdown report with change annotations.

```markdown
## Outline Diff: v1 → v2

### Slide Order Changes
- Slide "Key Metrics" moved from position 4 → position 3
- Slide "Team Structure" removed

### New Slides
- [+] Slide 8: "Customer Testimonials" (added to Act 3)

### Modified Slides
- Slide 2: "Our Approach"
  - Title changed: "Our Approach" → "How We Deliver"
  - Bullet added: "24/7 monitoring with automated escalation"
  - Bullet removed: "Best-in-class tools and processes"

### Summary
- 1 slide added, 1 removed, 2 modified, 1 reordered
- Net slide count: 12 → 12
```

### `--theme` — Theme Diff

Compares two theme JSON files and reports design token changes.

**Detection**:
- Color changes (primary, accent, background, text, each named token)
- Font changes (family, size, weight)
- Spacing changes (margins, padding, gap tokens)
- Layout token changes (slide dimensions, viewport)

**Output**: Markdown report with before/after values.

```markdown
## Theme Diff: midnight-purple → corporate-light

### Colors
| Token       | Before    | After     |
|-------------|-----------|-----------|
| primary     | #6B21A8   | #1E40AF   |
| accent      | #F59E0B   | #059669   |
| background  | #1A0533   | #FFFFFF   |
| text        | #F8FAFC   | #1F2937   |

### Fonts
| Token       | Before         | After          |
|-------------|----------------|----------------|
| heading     | Inter Bold     | Calibri Bold   |
| body        | Inter Regular  | Calibri        |

### Summary
- 4 color tokens changed, 2 font tokens changed, 0 spacing tokens changed
```

### `--visual` — Visual Slide Diff

Renders both versions to PNG and produces a side-by-side comparison.

**Procedure**:
1. Render version A slides to PNG (via render skill or chrome-extract for HTML).
2. Render version B slides to PNG.
3. Match slides by index (sequential) or by title (fuzzy match for reordered decks).
4. For each slide pair, present side-by-side with a border indicating status:
   - **Green border** — new slide (only in B)
   - **Red border** — removed slide (only in A)
   - **Yellow border** — changed slide (both exist, visual differences detected)
   - **No border** — unchanged
5. Claude visually inspects each changed pair and describes what differs.

**Output**: Markdown report with per-slide comparison notes + optional HTML page
with side-by-side image pairs.

```markdown
## Visual Diff: v1 → v2

### Slide 1: Title Slide — UNCHANGED

### Slide 2: Our Approach — CHANGED
- Background color shifted from purple to blue
- Subtitle text updated
- Icon in top-right corner is new

### Slide 8: Customer Testimonials — NEW
- Full-bleed image with quote overlay
- Not present in v1
```

### `--slides` — Structural HTML Diff

Compares specific slide HTML files at the DOM level.

**Detection**:
- Elements added or removed (by tag + class)
- Text content changes
- CSS class changes (style shifts)
- Attribute changes (colors, dimensions, data attributes)
- Structure changes (nesting depth, container reorganization)

**Output**: Per-element change list, grouped by slide region.

```markdown
## Slide Diff: slide-03-v1.html → slide-03-v2.html

### Added Elements
- <div class="stat-card"> at position 3 (new metric card)
- <span class="badge"> inside card-2 header

### Removed Elements
- <div class="footnote"> at bottom of slide

### Changed Elements
- <h2 class="slide-title">: text "Q3 Results" → "Q3 Performance"
- <div class="card-1">: background-color #6B21A8 → #1E40AF

### Structure
- Card container changed from 2-column to 3-column grid
```

---

## Auto-Detection from Version History

If the deck uses the versioning system (see `convert/references/versioning.md`),
deck-diff can automatically compare the current version against the previous one
without the user specifying two paths.

1. Read `~/.something-wicked/wicked-prezzie/versions/{deck-slug}.json`.
2. Identify the two most recent version entries.
3. Locate the artifacts for each version.
4. Run the appropriate diff mode.

```
"What changed in the latest version?"
  → Auto-detect deck slug → read version history → diff latest vs previous
```

---

## Cross-Deck Comparison

To compare two different decks (not versions of the same deck):

```
"How does the sales deck differ from the marketing deck?"
  → --outline sales-kickoff/outline.json marketing-launch/outline.json
  → --visual (render both, match by slide type or position)
```

Cross-deck comparison uses slide-type matching (title vs title, stats vs stats)
rather than index matching, since the decks may have different structures.

---

## Output Formats

| Format | When | How |
|--------|------|-----|
| **Markdown report** | Default — in-conversation review | Written to `{deck_dir}/diff-report.md` |
| **HTML visual diff** | When `--html` flag is passed | Self-contained HTML with side-by-side images, written to `{deck_dir}/diff-visual.html` |
| **JSON structured** | When `--json` flag is passed | Machine-readable diff for programmatic consumption |

---

## Integration with Other Skills

| Skill | Integration Point |
|-------|-------------------|
| **render** | Visual diff renders both versions via render skill |
| **chrome-extract** | HTML source screenshots for visual comparison |
| **compare** | Reuses compare skill's side-by-side methodology |
| **convert** | After re-conversion, diff against previous PPTX to verify improvements |
| **workflow** | Track changes across build iterations within a workflow session |
| **collaborate** | After applying review feedback, diff to show what changed |
| **deck-library** | Compare a new deck against a library deck for structural similarity |

---

## Invocation Examples

```
"What changed since the last version?"
  → deck-diff (auto-detect from version history)

"Compare these two outlines"
  → deck-diff --outline v1/outline.json v2/outline.json

"Show me the theme differences"
  → deck-diff --theme midnight-purple.json corporate-light.json

"Visual before and after"
  → deck-diff --visual --v1 old-deck.pptx --v2 new-deck.pptx

"What's different about slide 3?"
  → deck-diff --slides slide-03-old.html slide-03-new.html

"How does the sales deck compare to the marketing deck?"
  → deck-diff --outline sales/outline.json marketing/outline.json --visual
```

---

## Limitations

- Visual diff relies on Claude's vision — no automated pixel-diff scoring.
- Slide matching across reordered decks uses title fuzzy match, which may
  misalign slides with similar titles. Verify matches in the report.
- Theme diff only compares JSON token values. Visual impact of token changes
  (e.g., how a color shift affects readability) requires visual diff.
- Cross-deck comparison works best when both decks use the same template.
  Decks with fundamentally different structures produce noisy diffs.

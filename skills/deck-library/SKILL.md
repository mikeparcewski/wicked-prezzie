---
name: deck-library
description: |
  Indexes completed decks into a searchable library. Browse past work, search by
  topic or layout pattern, and extract reusable slides for new projects.
  User-level storage shared across all projects.

  Use when: "save to library", "search past decks", "find a slide like",
  "browse library", "reuse that layout", "slide bank", "deck gallery",
  "what decks have I built", "library", "past presentations"
---

# deck-library — Deck Gallery & Reuse

A personal library of completed decks. Index finished work, search by topic or
layout pattern, extract individual slides for reuse, and browse a visual gallery.
Storage is user-level (`~/.something-wicked/wicked-prezzie/library/`) — shared
across all projects on the machine.

## When to Use

- After completing a deck — index it for future reference
- When starting a new deck — search for similar past work to reuse layouts
- When looking for a specific slide type (e.g., "a 3-stat card layout")
- To browse all past decks visually
- To identify recurring patterns across your work

---

## Storage Structure

```
~/.something-wicked/wicked-prezzie/library/
  catalog.json                     — master index of all decks
  {deck-slug}/
    metadata.json                  — deck-level metadata
    contact-sheet.png              — thumbnail overview (grid of all slides)
    slides/
      slide-01.json                — per-slide metadata + layout pattern
      slide-01-thumb.png           — individual slide thumbnail
      slide-02.json
      slide-02-thumb.png
      ...
```

### catalog.json Schema

```json
{
  "version": 1,
  "updatedAt": "2026-03-23T10:00:00Z",
  "decks": [
    {
      "slug": "q4-sales-kickoff",
      "title": "Q4 Sales Kickoff",
      "indexedAt": "2026-03-15T14:00:00Z",
      "slideCount": 18,
      "template": "general",
      "theme": "midnight-purple",
      "tags": ["sales", "quarterly", "kickoff"],
      "audience": "Sales team",
      "sourcePath": "/Users/me/Projects/sales-kickoff/"
    }
  ]
}
```

### metadata.json Schema (per deck)

```json
{
  "slug": "q4-sales-kickoff",
  "title": "Q4 Sales Kickoff",
  "indexedAt": "2026-03-15T14:00:00Z",
  "sourcePath": "/Users/me/Projects/sales-kickoff/",
  "slideCount": 18,
  "template": "general",
  "theme": "midnight-purple",
  "themeColors": {"primary": "#6B21A8", "accent": "#F59E0B"},
  "tags": ["sales", "quarterly", "kickoff"],
  "audience": "Sales team",
  "createdAt": "2026-03-10T09:00:00Z",
  "pptxPath": "deliverables/q4-sales-kickoff.pptx",
  "slideTypes": {
    "title": 1,
    "content": 10,
    "divider": 3,
    "stats": 2,
    "closing": 1,
    "other": 1
  }
}
```

### Per-Slide Metadata Schema

```json
{
  "slideIndex": 3,
  "sourceFile": "slide-03.html",
  "slideType": "stats",
  "keyMessage": "Revenue grew 34% year-over-year",
  "layoutPattern": "3-stat-card-grid",
  "elements": ["heading", "stat-card", "stat-card", "stat-card", "footer-text"],
  "colors": ["#6B21A8", "#F59E0B", "#FFFFFF"],
  "hasImages": false,
  "hasSVG": true,
  "complexity": "low",
  "tags": ["revenue", "growth", "metrics"]
}
```

---

## Operations

### `--index` — Index a Completed Deck

1. **Locate deck** — use the current project directory or a specified path.
2. **Extract metadata** — read outline.json, deck-state.json, theme config, and slide files.
3. **Generate thumbnails** — render each slide to PNG via the render skill. Produce individual thumbnails (640x360) and a contact sheet grid.
4. **Classify slides** — for each slide, detect:
   - Slide type: title, content, divider, stats, chart, closing, Q&A, agenda
   - Layout pattern: freeform name describing the arrangement (e.g., "2-column-text-image", "3-stat-card-grid", "full-bleed-image-with-overlay")
   - Key message: the primary takeaway from the slide content
   - Element inventory: what shapes/types are present
5. **Generate slug** — from deck title, deduplicated against existing catalog entries.
6. **Write files** — metadata.json, per-slide JSONs, thumbnails to the library directory.
7. **Update catalog.json** — add or replace the deck entry.

### `--search` — Search the Library

Search across all indexed decks. Supports multiple filter dimensions:

| Filter | Example | Searches |
|--------|---------|----------|
| Topic/tags | `--search "sales quarterly"` | Deck tags and slide tags |
| Slide type | `--search --type stats` | Per-slide slideType field |
| Layout pattern | `--search --pattern "card-grid"` | Per-slide layoutPattern field |
| Audience | `--search --audience "executive"` | Deck-level audience field |
| Template | `--search --template rfp-exec` | Deck-level template field |
| Theme | `--search --theme midnight-purple` | Deck-level theme field |

Results return matching decks and/or individual slides with:
- Deck title, date, slide count
- Matching slide thumbnails (if searching at slide level)
- Relevance ranking (number of matching dimensions)

### `--extract` — Extract a Slide for Reuse

1. **Specify source** — deck slug + slide index, or a search result reference.
2. **Copy slide** — copies the HTML slide file to the current project's slides directory.
3. **Theme adaptation** (optional) — if `--adapt-theme` is passed and the source theme differs from the active theme, recolor the slide:
   - Map source theme colors to active theme colors by role (primary, accent, background, text)
   - Update CSS custom properties in the slide HTML
   - Preserve layout and structure, change only color values
4. **Report** — print the extracted slide path and any theme adaptations made.

### `--browse` — Generate a Visual Gallery

1. **Read catalog.json** — get all indexed decks.
2. **Generate HTML gallery page** — a single self-contained HTML file with:
   - Deck cards showing contact sheet thumbnail, title, date, slide count, tags
   - Filter sidebar: by tag, template, theme, date range
   - Click-to-expand: shows individual slide thumbnails for the deck
   - Search box for full-text search across deck and slide metadata
3. **Write to** `~/.something-wicked/wicked-prezzie/library/gallery.html`.
4. **Open** — optionally open in browser for browsing.

### `--patterns` — Identify Recurring Layout Patterns

1. **Scan all per-slide metadata** across the entire library.
2. **Cluster by layoutPattern** — group slides with identical or similar patterns.
3. **Report recurring patterns**:

```markdown
## Recurring Layout Patterns

### 3-stat-card-grid (found in 12 decks, 18 slides)
Used for: key metrics, performance summaries, comparison highlights
Example decks: q4-sales-kickoff (slide 4), product-launch (slide 7)

### 2-column-text-image (found in 9 decks, 24 slides)
Used for: feature explanations, case studies, before/after
Example decks: brand-refresh (slide 3), annual-review (slide 11)
```

4. **Suggest template extraction** — for patterns appearing in 3+ decks, suggest creating a reusable template in the generate skill's template library.

---

## Integration with Other Skills

| Skill | Integration Point |
|-------|-------------------|
| **render** | Thumbnails generated via render skill (PPTX to PNG) |
| **generate** | `--patterns` feeds template suggestions back to generate's template library |
| **theme** | `--extract --adapt-theme` uses theme color mapping for recoloring |
| **outline** | When building a new outline, search library for similar past decks to reference |
| **workflow** | Phase 8 (Export) can auto-index the completed deck into the library |
| **start** | Entry point can suggest "You built a similar deck last month — reuse slides?" |

---

## Invocation Examples

```
"Save this deck to the library"
  → deck-library --index

"Find me a stats slide layout"
  → deck-library --search --type stats

"What decks have I built about sales?"
  → deck-library --search "sales"

"Reuse slide 4 from the Q4 kickoff"
  → deck-library --extract q4-sales-kickoff --slide 4

"Reuse that slide but match my current theme"
  → deck-library --extract q4-sales-kickoff --slide 4 --adapt-theme

"Show me all my past decks"
  → deck-library --browse

"What layout patterns do I use most?"
  → deck-library --patterns
```

---

## Catalog Maintenance

- **Re-index** — re-running `--index` on an already-indexed deck updates in place (slug match).
- **Remove** — delete a deck's directory from the library and remove its catalog entry.
- **Stale detection** — if `sourcePath` no longer exists, mark the entry as `"stale": true` in the catalog. Stale decks still appear in search but with a warning.
- **Backup** — the library is plain files. Copy or git-init the directory for backup.

---

## Anti-Pattern Guards

**Guard 1 — No duplicate slugs**: If a deck title generates a slug that already
exists, append a numeric suffix. Never overwrite an existing deck entry silently.

**Guard 2 — No source mutation**: `--extract` copies slides, never moves or
modifies the source deck in the library. The library is read-only during extract.

**Guard 3 — No stale thumbnails**: When re-indexing, always regenerate thumbnails.
Cached thumbnails from a previous version are replaced, not reused.

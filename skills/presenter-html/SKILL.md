---
name: presenter-html
description: |
  Generates a self-contained single-file HTML presenter view with embedded slides,
  navigation, and a three-tab notes panel. Pure Python — no external dependencies.

  Use when: "presenter view", "presentation mode", "build presenter",
  "present the slides", "speaker view", "practice mode"
---

# HTML Presenter View

Builds a self-contained single-file HTML presenter view that embeds all slide
content directly, with keyboard navigation and a three-tab notes panel. The
output file can be opened in any browser — no server, no dependencies, no
network connection required.

---

## When to Use

- User wants to present or rehearse their slides
- User asks for a "speaker view" or "presenter mode"
- After notes are written and the deck is ready for delivery
- User needs an offline presentation format (conference, travel)

---

## Output Architecture

The presenter view is a single `.html` file containing:

1. **All slide content** — each slide's HTML is embedded in a `<section>` element
   with `display: none` toggled by JavaScript. Same rendering as source slides,
   not screenshots.

2. **Three-tab notes panel** — slides in from the right edge when activated:
   - Tab 1: **Notes** (always labeled "Notes")
   - Tab 2: **Talking Points** (always labeled "Talking Points")
   - Tab 3: **Configurable** (label read from `notes.json` `tab3_field`, default "References")

3. **Navigation controls** — bottom bar with slide counter, prev/next buttons,
   and keyboard shortcut hints.

4. **All CSS inlined** — no external stylesheets. Slide styles are scoped per
   section to prevent conflicts.

---

## Keyboard Navigation

| Key | Action |
|-----|--------|
| Right Arrow / Space / Enter | Next slide |
| Left Arrow / Backspace | Previous slide |
| N | Toggle notes panel |
| F | Toggle fullscreen |
| Home | First slide |
| End | Last slide |
| Escape | Exit fullscreen / close notes panel |
| 1 / 2 / 3 | Switch notes tab (when panel is open) |

---

## Notes Panel Behavior

- Panel slides in from the right edge (300px wide, dark background)
- Tab selection persists via `localStorage` — reopening the panel restores the
  last active tab
- Notes content is loaded from `notes.json` at build time and embedded in the
  HTML as a JavaScript object
- If `notes.json` is missing, the notes panel is omitted entirely (no empty panel)
- Talking points render as a bulleted list with "If asked:" items highlighted
- Tab 3 content renders based on type: lists for references/sources, paragraphs
  for objectives/decision points

---

## Slide Rendering

Slides are embedded as full HTML, not images. This preserves:
- All text (selectable, accessible)
- CSS animations if present (not stripped like in PPTX conversion)
- SVG charts and diagrams at full resolution
- Responsive layout within the viewport

Each slide is wrapped in a container that enforces 16:9 aspect ratio (1280x720
logical pixels) and scales to fit the browser window via CSS transform.

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   ┌─────────────────────────────────┐  ┌────────────┐  │
│   │                                 │  │ Notes      │  │
│   │         Slide Content           │  │ Tab 1 | 2 │  │
│   │         (16:9 scaled)           │  │            │  │
│   │                                 │  │ Walk the   │  │
│   │                                 │  │ audience   │  │
│   │                                 │  │ through... │  │
│   └─────────────────────────────────┘  └────────────┘  │
│                                                         │
│   ◄  Slide 3 of 12  ►          [N]otes [F]ullscreen    │
└─────────────────────────────────────────────────────────┘
```

---

## Build Process

### Input Files

| File | Required | Description |
|------|----------|-------------|
| Slide HTML files | Yes | Individual `.html` files in `--slides-dir` |
| `notes.json` | No | Speaker notes from the notes skill |
| Slide manifest | No | `slides.json` or file list for ordering |

### Slide Ordering

The script determines slide order by:
1. Reading `slides.json` manifest if it exists (explicit order)
2. Falling back to alphabetical filename sort (numeric prefixes sort correctly)
3. Honoring `--subset` flag to include only specific slide numbers

### CSS Isolation

Each slide's CSS is scoped to prevent cross-slide style bleed:
- All slide styles are prefixed with a slide-specific selector (`.slide-N`)
- Global resets are applied once at the document level
- The notes panel has its own isolated style scope

### Script

`scripts/build_presenter_html.py` — pure Python stdlib. No Chrome, no Pillow,
no third-party packages.

---

## Usage

```bash
# Build presenter view from slides directory
python ${CLAUDE_SKILL_DIR}/scripts/build_presenter_html.py \
  --slides-dir ./slides \
  --output presenter.html

# Include speaker notes
python ${CLAUDE_SKILL_DIR}/scripts/build_presenter_html.py \
  --slides-dir ./slides \
  --notes-json notes.json \
  --output presenter.html

# Subset of slides (e.g., for a shortened version)
python ${CLAUDE_SKILL_DIR}/scripts/build_presenter_html.py \
  --slides-dir ./slides \
  --notes-json notes.json \
  --subset 1,2,3,7,8,12 \
  --output presenter-short.html
```

---

## Integration with Other Skills

### Reads From

| Skill | What | Why |
|-------|------|-----|
| generate | HTML slide files | Slide content to embed |
| notes | `notes.json` | Three-tab notes panel content |
| workflow | `deck-state.json` | Template name for tab3 label |
| outline | `outline.json` | Slide ordering and section breaks |

### Produces For

| Skill | What | Why |
|-------|------|-----|
| convert | N/A — presenter view is a delivery artifact | End of pipeline |
| checkpoint | Build status | Session state tracking |

---

## Limitations

- File size scales with slide count — a 20-slide deck with embedded images may
  produce a 5-10 MB HTML file. This is intentional (self-contained).
- CSS animations play on slide entry but do not reset on revisit without a
  page reload.
- The notes panel overlaps the slide area when open. On narrow screens, the
  slide content compresses. Designed for laptop/desktop, not mobile.

---

## How Claude Should Use This Skill

1. **Check for notes first** — if `notes.json` does not exist, suggest running
   the notes skill before building the presenter view.
2. **Verify slide order** — if the user has reordered or removed slides, confirm
   the intended order before building.
3. **Open the output** — after building, suggest the user open the file in their
   browser and test keyboard navigation.
4. **No server needed** — the file works with `file://` protocol. Do not suggest
   running a local server.

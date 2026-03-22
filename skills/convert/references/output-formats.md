# Output Formats — PPTX and HTML Rendering

The pipeline can produce output in two formats from the same HTML source slides: native PPTX
(via Chrome extraction + python-pptx) and self-contained HTML (via Reveal.js). Content is
authored once as HTML slides; rendered to any requested format.

---

## Architecture

```
HTML slides (from slide-generate or user-provided)
       ↓ slide-html-standardize
Normalized HTML
      /                \
[Chrome extract        [Reveal.js bundle]
 + python-pptx]              ↓
      ↓              .html file
  .pptx file       (self-contained, browser)
(editable in PPT)
```

The HTML slides are the canonical source. Both renderers consume them.

---

## Supported Formats

### `pptx` — PowerPoint (default)
Generated via Chrome headless extraction + python-pptx builder. Native OOXML. Opens in
PowerPoint, Keynote, Google Slides. Fully editable after delivery. Best for decks that need
post-generation polish or client handoff.

### `html` — Reveal.js Presentation
Self-contained single `.html` file. No server, no build step, no dependencies — open in any
browser. Best for sharing as a link, embedding in pages, or presenting without PowerPoint.

### `both`
Generates both files from the same HTML source in a single run. Both versioned together.

---

## Format Selection

**Per run:** Specify format: "convert to pptx", "create html presentation", or "both formats."

**Config default:** Set `output_format` in project config (`skills/slide-config/config.json`). Options: `pptx`,
`html`, `both`. Defaults to `pptx`.

---

## Reveal.js Renderer

### Self-contained output
All Reveal.js CSS and JS is inlined. Images are base64-encoded and embedded. The output is a
single `.html` file with zero external dependencies. Open it offline, email it, host it anywhere.

### HTML slide → Reveal.js section mapping
Each source HTML slide becomes a `<section>` element. The slide content is preserved with
Reveal.js wrapper and navigation.

```html
<!-- title slide -->
<section data-background-color="#0A0A0F">
  <h1>Slide Title</h1>
  <p class="subtitle">Subtitle text</p>
</section>

<!-- stat-callout -->
<section>
  <h2>The Baseline</h2>
  <div class="stat-row">
    <div class="stat"><span class="value">73%</span><span class="label">Coverage</span></div>
  </div>
</section>
```

### Keyboard shortcuts
Arrow keys and Space advance slides. S opens speaker notes window. O shows slide overview grid.
F enters fullscreen. B blacks the screen.

### PDF export from HTML
Append `?print-pdf` to the file URL in Chrome, then use browser print (Ctrl/Cmd+P) → Save as PDF.

### Transitions
Default: `slide` (horizontal). Override in config under `html_transition`.
Options: `none`, `fade`, `slide`, `convex`, `concave`, `zoom`.

---

## Format Capability Comparison

| Feature | PPTX | HTML (Reveal.js) |
|---|---|---|
| Editable in PowerPoint | Yes | No |
| Editable post-generation | Yes (full) | Yes (HTML/CSS knowledge) |
| Animations / transitions | Basic | Rich (fade, zoom, etc.) |
| Presenter mode | Via PowerPoint | Built-in (press S) |
| Slide overview | Via PowerPoint | Built-in (press O) |
| PDF export | Via PowerPoint | Via Chrome print |
| Share as URL | No | Yes (host the .html file) |
| Offline use | Yes | Yes (self-contained) |
| Zero install to present | No (needs PPT) | Yes (any browser) |
| Speaker notes | Notes pane | Press S — separate window |
| Client edits after | Easy | Requires HTML knowledge |
| File size | Medium | Larger if many images (base64) |

---

## Version Naming with Format

Both format outputs share the same version number and label:
```
deck-name_v2-client-review.pptx
deck-name_v2-client-review.html
```

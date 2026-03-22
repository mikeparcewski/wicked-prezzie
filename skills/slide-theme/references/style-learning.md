# Style Learning — Extraction from Existing Assets

Extracts a reusable style fingerprint from existing assets. Saves as a named theme JSON in
`~/.something-wicked/wicked-prezzie/themes/`. Accepts PPTX files, PDF files, and images
(screenshots, mood boards, brand assets).

---

## Invocation

Say "learn my brand from ./assets", "extract styles from brand.pdf and logo.png", or
"learn and save as my-brand." Produces a theme JSON compatible with `slide-theme`.

---

## Input Types

### PPTX Files
Primary source. Extract from slide XML and theme definitions:
- **Color palette**: pull from theme colors (`dk1`, `dk2`, `lt1`, `lt2`, `accent1`–`accent6`)
  plus computed dominant colors from slide backgrounds and shapes
- **Typography**: font families from theme (`majorFont`, `minorFont`), sizes from title/body
  placeholders across all slide layouts, weight conventions
- **Layout patterns**: analyze all slide layouts in slide master; count usage frequency across
  slides; identify top 5 most-used compositions
- **Content alignment**: detect vertical centering (flexbox center, margin auto, absolute
  transform centering) and horizontal justification. Record as `vertical_align` and
  `content_justify` in the layout section. This is commonly missed — check the `.slide`
  container's `display`, `align-items`, `justify-content`, and any wrapper `margin: auto`
- **Spacing/density**: average text-to-whitespace ratio, margin conventions, object padding
- **Logo/brand placement**: detect recurring small images in consistent positions (header/footer/corner)
- **Icon usage**: detect small SVG or EMF shapes; classify style if possible

### PDF Files
Secondary source. Useful for brand guides, style documents, lookbooks:
- Render each page to image
- Extract dominant colors per page (k-means, k=6)
- Detect layout geometry: column structure, margin widths, text block positions
- Infer typography from text rendering (approximate — flag as "inferred, verify")
- Note visual language: photo-heavy vs. diagram-heavy vs. text-heavy

### Images (PNG, JPG, screenshots)
Tertiary source. Best for mood boards and brand references:
- Extract dominant color palette (k-means, k=5)
- Detect image style: photographic / illustrative / diagrammatic / typographic
- Infer density preference from visual complexity
- Cannot extract font information — flag as missing

### Mixed Input
When multiple file types provided: merge extractions, weight PPTX data highest, flag conflicts.
Example conflict: PPTX theme says navy primary, PDF brand guide shows purple primary →
`[REVIEW: conflicting primary colors — PPTX: #1C2B5E, PDF: #6B2D8B. Which is authoritative?]`

---

## Output: Theme JSON

Extracted data maps directly to the slide-theme schema:

```json
{
  "name": "my-brand",
  "source_files": ["q3-deck.pptx", "brand-guide.pdf"],
  "extracted_at": "2025-03-05T14:22:00Z",
  "colors": {
    "background": "#1A1A1A",
    "surface": "#2A2A2A",
    "primary": "#CC0000",
    "accent": "#F5F5F5",
    "text": "#FFFFFF",
    "textSecondary": "#CCCCCC",
    "heading": "#FFFFFF",
    "border": "#333333",
    "cardBg": "#2A2A2A",
    "cardBorder": "#444444",
    "highlight": "#CC0000"
  },
  "fonts": {
    "heading": "Helvetica Neue",
    "body": "Helvetica Neue",
    "mono": "SF Mono"
  },
  "sizes": { ... },
  "spacing": { ... },
  "layout": { ... },
  "extraction_metadata": {
    "confidence": {
      "colors": "high",
      "typography": "medium",
      "layout": "high",
      "imagery": "low"
    },
    "inferred_flags": [],
    "review_flags": []
  }
}
```

---

## Storage

Save to `~/.something-wicked/wicked-prezzie/themes/{name}.json`. After extraction, prompt:
> "Theme saved as '[name]'. Want to set this as your active theme?"

If a theme with this name already exists:
> "A theme named '[name]' already exists. Overwrite, rename, or cancel?"

---

## Matching Against Existing Themes

After extraction, compare against existing themes in `~/.something-wicked/wicked-prezzie/themes/`:
- Compare extracted primary color against existing theme palettes (delta-E color distance)
- If close match found (delta-E < 10): suggest
  > "This looks close to '[existing-theme]'. Use that as a base and override with learned values?"

---

## Extraction Quality Indicators

Report after extraction:

```
✓ Style extracted from 3 files (1 PPTX, 1 PDF, 1 image)
  Colors:     high confidence (from PPTX theme + PDF)
  Typography: medium confidence (PPTX confirmed, PDF inferred)
  Layouts:    high confidence (14 unique slide layouts analyzed)
  Imagery:    low confidence (1 image source only)
  ⚠ 1 conflict found — see REVIEW flag in theme
```

Low confidence fields are marked in the theme JSON and surfaced during theme selection.

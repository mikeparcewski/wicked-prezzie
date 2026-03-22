# Image Sourcing — Modes & Attribution

Three image modes for slide generation: Unsplash (photography), Icon/UI Illustration (from icon
sets), and None (text-only). Mode is set in the active profile/theme, selectable per deck, and
overridable per slide.

---

## Image Mode Selection

Set in profile under `imagery.default_mode`. Options:
- `unsplash` — real photography via Unsplash API
- `icons` — icon/UI illustration style from registered iconsets
- `none` — no images; layouts adapt to text-only

Per-deck override: specify during generation setup.
Per-slide override: say *"use an icon on this slide instead of a photo"* at any point.

---

## Unsplash Mode

### How it works
For each image-bearing slide, generate a search keyword from the slide's content. Query the
Unsplash API. Select the most visually appropriate result (composition, color match to palette,
subject relevance). Download and embed in the slide HTML.

### Keyword generation
Derive from slide title + primary content. Keep keywords concrete and visual:
- "quarterly results" → `"growth graph upward"` or `"business momentum"`
- "team introduction" → `"professional team collaboration"`
- "migration risk" → `"bridge construction"` or `"pathway forward"`
Avoid abstract queries that return random stock images.

### Attribution
Unsplash requires attribution. Add automatically based on profile setting:

| Attribution setting | Behavior |
|---|---|
| `notes` (default) | Photo credit in `data-notes` attribute: `Photo by [Name] on Unsplash` |
| `footer` | Small text in slide footer: `Photo: [Name] / Unsplash` |
| `none` | No attribution (only for non-public decks) |

### API configuration
Store API key in `~/.something-wicked/wicked-prezzie/config.json` under `unsplash_api_key`
(user-level, shared across projects). If not configured:
> *"Unsplash mode requires an API key. Get a free key at unsplash.com/developers."*

Fallback if API unavailable: switch to icons mode for that slide, note in summary.

### Image placement
Follow the active profile's `imagery.placement` setting:
- `full-bleed` — image fills entire slide background; text overlaid with contrast overlay
- `right-panel` — image occupies right 40–50%; text on left
- `inset` — image as a contained element within a content zone
- `none` — no images (some templates skip images regardless)

Template determines valid placements. Title slides always use full-bleed. Two-column uses
right-panel. Stat-callout ignores image mode.

---

## Icon / UI Illustration Mode

### How it works
Select icons from registered iconsets (see design-registry.md). Map slide content to icon
categories. Compose icon clusters or single hero icons as visual elements.

### Icon selection logic
Map slide topic → icon category → specific icon:
```
"security" → tech category → shield icon
"growth" → data category → trending-up icon
"team" → people category → users icon
"timeline" → actions category → calendar icon
"warning / risk" → actions category → alert-triangle icon
```

### Icon composition styles
| Style | Description | Best for |
|---|---|---|
| `hero-single` | One large icon, centered, colored background | section dividers, concept slides |
| `cluster-3` | Three icons in a row with labels | three-point lists, comparisons |
| `inline` | Small icons inline with bullet points | agenda, process slides |
| `background-ghost` | Large low-opacity icon as background texture | stat-callout, quote slides |

### Icon style (line vs. filled)
Set in profile. Options: `line`, `filled`, `flat`. Must be consistent across the deck.

### Color application
Icons inherit palette colors. Primary icon color = profile's accent or primary.
On dark backgrounds: use light icon color. On light backgrounds: use primary or secondary.

---

## No Images Mode

When `imagery.default_mode = "none"`:
- All templates adapt to text/data-only layouts
- Title slides use solid color background instead of image
- Two-column becomes full-width text
- Speaker notes do not include attribution lines

---

## Post-Generation Image Summary

Always include in the generation summary:
```
Images: Unsplash (12 photos, attribution in speaker notes)
  — 2 slides fell back to icons (no good Unsplash match)
  — 1 slide has no image (stat-callout template)
```

Or:
```
Images: Icon/UI illustration (lucide-line iconset)
  — 14 slides with icons, 4 slides no image (stat-callout)
```

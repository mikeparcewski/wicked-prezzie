# Profiles — Style Profile Management

A style profile extends a theme with layout preferences, image mode, template preferences, and
density settings. Profiles are the bridge between themes (color/font definitions) and a specific
deck's visual identity.

---

## Profile Types

### Learned Profiles
Created by the learn flow (see style-learning.md). Extracted from existing PPTX, PDF, or image
assets. Stored in `~/.something-wicked/wicked-prezzie/themes/` as theme JSON with extended metadata.

### Assembled Profiles
Built interactively by combining components:
- Pick a theme (or registry palette)
- Pick layout preferences (density, margins, template bias)
- Pick image mode default
- Save as a named profile

### Imported Profiles
Pulled from `.pptprofile` JSON files shared by teammates.

### Built-in Themes
Always available. Seeded to `~/.something-wicked/wicked-prezzie/themes/` on first use.

| Name | Character |
|---|---|
| `midnight-purple` | Dark background, purple primary, gold accent |
| `corporate-light` | White background, navy primary, teal accent |
| `warm-dark` | Charcoal background, coral primary, gold accent |

---

## Profile Operations

- "list profiles" → show all available themes/profiles with source and date
- "show profile [name]" → display full theme JSON
- "export profile [name]" → produce a `.pptprofile` file for sharing
- "import profile [file]" → register an imported profile as a theme
- "set active theme [name]" → set the active theme via config (project-level)
- "assemble a profile" → interactive component assembly flow

---

## Profile Selection During Generation

When starting deck generation, present available profiles:

```
Style profile:

  Learned (from your assets):
    • my-brand           [high confidence] — extracted 2025-03-01
    • team-clinical      [medium confidence] — extracted 2025-02-15

  Built-in:
    • midnight-purple  •  corporate-light  •  warm-dark

  Or: describe a vibe →
```

**Vibe matching:**
If user describes a vibe (e.g., "clean and modern", "dark executive"), map to closest theme
plus override suggestions:

| Vibe phrase | Maps to | Suggested overrides |
|---|---|---|
| "clean", "minimal", "airy" | corporate-light | large margins, no icons |
| "dark", "premium", "executive" | midnight-purple | stat-heavy templates |
| "bold", "colorful", "energetic" | warm-dark | high-saturation accent |
| "warm", "human", "story-driven" | corporate-light | photographic images, pull quotes |

---

## .pptprofile Format

Portable, shareable JSON for exchanging style configurations:

```json
{
  "format": "pptprofile-v1",
  "name": "my-brand",
  "description": "Engineering team deck style — Q1 2025",
  "exported_at": "2025-03-05T14:00:00Z",
  "colors": {
    "primary": "#CC0000",
    "background": "#1A1A1A",
    "accent": "#F5F5F5",
    "text": "#FFFFFF"
  },
  "typography": {
    "heading_font": "Helvetica Neue",
    "body_font": "Helvetica Neue",
    "heading_size_pt": 36,
    "body_size_pt": 16
  },
  "layout": {
    "density": "moderate",
    "margin_convention": "generous",
    "image_treatment": "full-bleed",
    "icon_style": "filled"
  },
  "imagery": {
    "default_mode": "unsplash",
    "attribution": "notes",
    "icon_style": "filled"
  },
  "template_preferences": {
    "preferred": ["two-column", "stat-callout", "title-hero"],
    "avoid": ["team-grid", "quote-pull"]
  }
}
```

---

## Profile Assembly (Interactive)

The assembly flow walks through:

1. Name this profile
2. Color palette — pick from existing themes, enter hex values, or extract from an asset
3. Typography — specify font families
4. Layout strategy — density, margins, image treatment
5. Template preferences — which templates to favor/avoid
6. Image mode default — unsplash / icons / none
7. Save and optionally set as active theme

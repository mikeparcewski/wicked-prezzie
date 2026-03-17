---
name: Slide Theme
description: >
  Brand and style definitions for slide decks — color palettes, font stacks,
  layout patterns, and reusable design tokens. Use this skill whenever the user
  wants to define a brand, set colors, choose fonts, create a theme, customize
  the look and feel, or says "use my brand colors" or "learn my brand". Also use
  when generating slides and no theme exists yet — a default dark theme is
  provided. If the user says "make it match our brand", "change the palette",
  "use these colors", or "create a theme from this PDF/website", start here.
  This skill produces theme JSON files consumed by slide-generate and
  slide-outline for consistent visual identity across decks.
---

# Slide Theme

## Purpose

Every slide deck needs a consistent visual identity — colors, fonts, spacing, and
layout patterns. Without a defined theme, each deck reinvents its palette and
every slide-generate call produces visually inconsistent output.

The Slide Theme skill defines reusable theme files that capture brand identity as
structured data. Themes are consumed by slide-generate to produce HTML with
consistent styling, and by slide-outline to inform color-coded section planning.

## When to Use

- Creating a new theme from scratch for a project or brand
- Importing brand identity from existing assets (colors from a logo, website, or PDF)
- Viewing or modifying an existing theme
- Setting the active theme for subsequent slide generation
- Listing available themes

## Theme File Format

Themes are stored as JSON files in `slide-theme/themes/`. Each theme file follows
this structure:

```json
{
  "name": "midnight-purple",
  "display_name": "Midnight Purple",
  "description": "Dark theme with purple accents",
  "colors": {
    "background": "#0A0A0F",
    "surface": "#13091D",
    "primary": "#A100FF",
    "secondary": "#6B2FA0",
    "accent": "#F59E0B",
    "text_primary": "#FFFFFF",
    "text_secondary": "#A0A0B0",
    "text_muted": "#6B6B80",
    "border": "#2A2A3D",
    "success": "#10B981",
    "warning": "#F59E0B",
    "error": "#EF4444"
  },
  "fonts": {
    "heading": "Calibri",
    "body": "Calibri",
    "mono": "Consolas"
  },
  "sizes": {
    "title": "48px",
    "subtitle": "28px",
    "heading": "36px",
    "subheading": "24px",
    "body": "18px",
    "caption": "13px",
    "small": "11px"
  },
  "spacing": {
    "margin": "48px",
    "gap_large": "32px",
    "gap_medium": "24px",
    "gap_small": "16px",
    "gap_xs": "8px"
  },
  "layout": {
    "viewport_width": 1280,
    "viewport_height": 720,
    "content_width": 1184,
    "content_start_x": 48,
    "content_start_y": 48
  },
  "card": {
    "background": "#1A1A2E",
    "border_radius": "12px",
    "padding": "24px",
    "shadow": "0 2px 6px rgba(0,0,0,0.15)"
  }
}
```

## Usage

```bash
# List available themes
python ${CLAUDE_SKILL_DIR}/scripts/slide_theme.py list

# Show theme details
python ${CLAUDE_SKILL_DIR}/scripts/slide_theme.py show midnight-purple

# Create a new theme interactively (outputs JSON to edit)
python ${CLAUDE_SKILL_DIR}/scripts/slide_theme.py create my-brand

# Set the active theme (writes to slide-config)
python ${CLAUDE_SKILL_DIR}/scripts/slide_theme.py activate midnight-purple

# Show the currently active theme
python ${CLAUDE_SKILL_DIR}/scripts/slide_theme.py active

# Export theme as CSS variables (for HTML slide generation)
python ${CLAUDE_SKILL_DIR}/scripts/slide_theme.py css midnight-purple

# Validate a theme against design principles
python ${CLAUDE_SKILL_DIR}/scripts/slide_theme.py validate midnight-purple
```

## Built-in Themes

### midnight-purple (default)
Dark background (#0A0A0F) with purple primary (#A100FF) and amber accent (#F59E0B).
High contrast white text. Matches the existing test slide examples.

### corporate-light
Light background (#FFFFFF) with navy primary (#1E3A5F) and teal accent (#0891B2).
Professional look for business presentations.

### warm-dark
Dark charcoal background (#1A1A2E) with coral primary (#FF6B6B) and gold accent (#FFD93D).
Warmer feel than midnight-purple.

## CSS Variable Export

The `css` command outputs a complete `<style>` block with CSS custom properties
that slide-generate templates consume:

```css
:root {
  --bg: #0A0A0F;
  --surface: #13091D;
  --primary: #A100FF;
  --secondary: #6B2FA0;
  --accent: #F59E0B;
  --text-primary: #FFFFFF;
  --text-secondary: #A0A0B0;
  --text-muted: #6B6B80;
  --border: #2A2A3D;
  --font-heading: Calibri, sans-serif;
  --font-body: Calibri, sans-serif;
  --title-size: 48px;
  --subtitle-size: 28px;
  --body-size: 18px;
  --margin: 48px;
  --gap: 24px;
  --card-bg: #1A1A2E;
  --card-radius: 12px;
  --card-padding: 24px;
}
```

## Theme Validation

The `validate` command checks a theme against slide-design principles:

- **Contrast ratios**: text_primary vs background meets WCAG AA (4.5:1 body, 3:1 large)
- **Palette size**: colors section has <= 5 chromatic colors (excluding grayscale)
- **Font limit**: <= 2 font families
- **Size hierarchy**: title > subtitle > heading > body > caption
- **Margin compliance**: margin >= 48px for 1280x720 viewport

## How Other Skills Use Themes

### slide-generate
Reads the active theme and injects CSS variables into generated HTML. The
theme's colors, fonts, and spacing are applied to every slide template.

### slide-outline
References the theme's color palette when assigning section colors in the
outline structure. Ensures the outline's visual plan matches the final output.

### slide-config
The active theme name is stored as `active_theme` in `skills/slide-config/config.json`.
If no theme is activated, `midnight-purple` is used as the default.

## Creating Themes from Existing Assets

When the user provides brand assets (logo, website URL, existing slides), extract
the visual identity:

1. **From colors**: Map provided hex/rgb values to the theme's color roles
   (background, primary, secondary, accent, text).
2. **From a logo**: Identify the dominant and accent colors. Use the dominant as
   primary and a contrasting color as accent.
3. **From a website**: Extract the CSS color palette and font stack.
4. **From existing slides**: Sample background colors, heading colors, and body
   text colors from representative slides.

Always validate the extracted theme against contrast requirements before saving.

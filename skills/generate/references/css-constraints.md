# CSS Constraints for Clean Chrome-Extract Output

This is the definitive CSS contract between generate and chrome-extract.
Every generated slide must conform to these rules. Violations cause layout
failures downstream that require 22+ CSS edits to clean up.

## Non-Negotiable Rules

### Viewport and Sizing

```css
/* Required viewport meta tag */
<meta name="viewport" content="width=1280">

/* Slide container — exact dimensions, no exceptions */
.slide {
    width: 1280px;
    height: 720px;
    position: relative;
    overflow: hidden;
}
```

- Fixed viewport at 1280px width. Chrome headless will not scale.
- No external fonts (Google Fonts, Typekit, CDN). Font requests fail in headless.
- No CSS animations or transitions. They produce mid-animation screenshots.
- No `@import` rules. Use inline `<style>` blocks only.

### Vertical Centering (Main Content Container)

The main content area MUST use flex column centering:

```css
.slide-content {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 24px 48px 20px;
}
```

**Never** use `align-items: stretch` on the main content container. This was
the single most frequent constraint violation — 7 recurrences, 22 CSS edits,
and a dedicated 783KB cleanup in prior sessions.

### Card Flex Rules

Cards inside the content area must follow these rules:

```css
/* CORRECT — use width:0 + flex-grow:1 instead of flex:1 */
.card {
    width: 0;
    flex-grow: 1;
}

/* WRONG — causes card overflow issues */
.card {
    flex: 1;         /* DO NOT USE on card elements */
    height: 100%;    /* DO NOT USE on card body */
    min-height: 100%; /* DO NOT USE on card body */
}
```

### Card Pattern

```css
.card {
    background: var(--vz-bg-card);
    border: 1px solid var(--vz-border);
    border-radius: 8px;
    padding: 16px 18px;
}

/* Highlighted card variant */
.card.highlight {
    background: rgba(213, 43, 30, 0.06);
    border: 2px solid rgba(213, 43, 30, 0.35);
}

/* Sub-items inside cards */
.card-item {
    background: var(--vz-bg-elevated);
    border-radius: 6px;
    padding: 8px 12px;
}
```

### Badge and Accent Bar Patterns

```css
/* Accent bar — 4px top stripe */
.red-bar {
    width: 100%;
    height: 4px;
    background: var(--vz-red);
}

/* Badge variants */
.badge {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.badge-red   { background: rgba(213, 43, 30, 0.15); color: #FF6B5E; }
.badge-green { background: rgba(34, 197, 94, 0.15);  color: #4ADE80; }
.badge-gold  { background: rgba(251, 191, 36, 0.15); color: #FCD34D; }
```

### Content Area Padding

```css
/* Standard content padding — do not reduce below these values */
.slide-content {
    padding: 24px 48px 20px;
}

/* Minimum margin from all edges */
/* 48px — enforced by content padding above */
```

### Section Header

```css
.section-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--vz-gray-300);
    font-weight: 600;
}

.slide-number {
    font-size: 11px;
    color: var(--vz-red);
    font-weight: 700;
}
```

## CSS Custom Properties Reference

All generated slides must define these variables in `:root`:

```css
:root {
    --vz-red: #D52B1E;
    --vz-bg: #0A0A0A;
    --vz-bg-card: #141414;
    --vz-bg-elevated: #1A1A1A;
    --vz-border: rgba(255, 255, 255, 0.08);
    --vz-gray-300: rgba(255, 255, 255, 0.5);
    --slide-width: 1280px;
    --slide-height: 720px;
}
```

## Font Stack

```css
body {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}
```

No external font loading. This stack is available in all Chrome headless
environments without network access.

## Common Failure Modes

| Symptom | Cause | Rule violated |
|---|---|---|
| Cards stack vertically instead of row | Missing `display:flex` on card container | Card flex rules |
| Content overflows slide boundary | `align-items:stretch` pulling height | Vertical centering rule |
| Blank white slide screenshot | External CSS not loaded | No external CSS rule |
| Text truncated mid-animation | CSS transition present | No animations rule |
| Cards unequal width in row | `flex:1` instead of `width:0;flex-grow:1` | Card flex rules |
| Content pinned to top | Missing `justify-content:center` | Vertical centering rule |

## Constraint Injection

When dispatching build agents, inject this file. The orchestrator must include
these constraints in every agent prompt under `## Constraints (MANDATORY)`.
A `PostToolUse` hook on Write/Edit checks any `.html` file for:
- `align-items: stretch`
- `height: 100%` inside `.slide`
- `flex: 1` on card elements
- `fetch(` referencing notes/JSON (fails on `file://` protocol)

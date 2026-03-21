# Canonical HTML Slide Template

This is the reference template for every generated slide. Deviating from this
structure causes downstream failures in chrome-extract and slide-pptx-builder.

## Full Template

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=1280">
    <title>Slide NN — Deck Title</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body class="standalone">

    <div class="slide" style="width:1280px; height:720px; position:relative; overflow:hidden;">

        <!-- 4px accent bar at top -->
        <div class="red-bar" style="width:100%; height:4px; background:var(--vz-red);"></div>

        <!-- Section label + slide number -->
        <div class="slide-header" style="display:flex; justify-content:space-between; align-items:center; padding:12px 48px 0;">
            <span class="section-label">SECTION NAME</span>
            <span class="slide-number">NN</span>
        </div>

        <!-- Main content area — flex column, vertically centered -->
        <div class="slide-content" style="display:flex; flex-direction:column; justify-content:center; align-items:center; padding:24px 48px 20px; height:calc(720px - 4px - 40px);">

            <!-- Slide-type-specific content goes here -->

        </div>

    </div>

    <!-- Navigation controls -->
    <nav class="slide-nav">
        <a href="slide-NN-1.html" class="nav-prev">← Prev</a>
        <a href="slide-NN+1.html" class="nav-next">Next →</a>
    </nav>

    <!-- Speaker notes (never use fetch() — fails on file://) -->
    <script src="notes-data.js"></script>
    <!-- Navigation logic -->
    <script src="nav.js"></script>

</body>
</html>
```

## CSS Variables

All slides inherit these from `styles.css`. When styles.css is not available
(standalone testing), define them inline in `<style>`:

```css
:root {
    /* Brand colors */
    --vz-red: #D52B1E;

    /* Backgrounds */
    --vz-bg: #0A0A0A;
    --vz-bg-card: #141414;
    --vz-bg-elevated: #1A1A1A;

    /* Borders and text */
    --vz-border: rgba(255, 255, 255, 0.08);
    --vz-gray-300: rgba(255, 255, 255, 0.5);

    /* Canvas dimensions */
    --slide-width: 1280px;
    --slide-height: 720px;
}
```

## Font Stack

```css
body {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    background: var(--vz-bg);
    color: #FFFFFF;
}
```

## notes-data.js Format

Speaker notes are stored in `notes-data.js` as a global variable, never
fetched at runtime. Using `fetch()` breaks on `file://` protocol.

```javascript
window.SLIDE_NOTES = {
  "1": {
    "notes": "Delivery instructions for the presenter. Make eye contact before speaking.",
    "rfp": [
      "Section: [Name] -- '[exact RFP quote]'"
    ],
    "talking_points": [
      "Substantive point with objection handler. If challenged on X: 'Response...'"
    ]
  },
  "2": { ... }
};
```

The `nav.js` reads `window.SLIDE_NOTES` and renders a notes panel toggled by
pressing N. Never embed notes in the slide body.

## Component Variations

### Title Slide Body

```html
<div class="slide-content" style="display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; padding:24px 48px 20px; height:calc(720px - 44px);">
    <h1 style="font-size:52px; font-weight:700; line-height:1.15; margin-bottom:20px;">Title as an Assertion Claim</h1>
    <p style="font-size:22px; color:var(--vz-gray-300); font-weight:400;">Supporting subtitle</p>
</div>
```

### Card Row Body

```html
<!-- Container must be flex row, never align-items:stretch -->
<div style="display:flex; flex-direction:row; gap:20px; width:100%; align-items:flex-start;">

    <!-- Each card uses width:0 + flex-grow:1, never flex:1 -->
    <div class="card" style="width:0; flex-grow:1; background:var(--vz-bg-card); border:1px solid var(--vz-border); border-radius:8px; padding:16px 18px;">
        <div class="section-label" style="font-size:11px; text-transform:uppercase; letter-spacing:2px; color:var(--vz-gray-300); margin-bottom:10px;">Label</div>
        <p style="font-size:16px; line-height:1.5;">Card body content.</p>
    </div>

    <div class="card" style="width:0; flex-grow:1; ...">
        ...
    </div>

</div>
```

### Stats Slide Body

```html
<div style="display:flex; flex-direction:row; gap:24px; width:100%;">
    <div class="card" style="width:0; flex-grow:1; text-align:center; background:var(--vz-bg-card); border:1px solid var(--vz-border); border-radius:8px; padding:24px 16px;">
        <div style="font-size:48px; font-weight:700; color:var(--vz-red);">40%</div>
        <div style="font-size:14px; color:var(--vz-gray-300); margin-top:8px;">Metric Label</div>
    </div>
</div>
```

## Common Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| Chrome renders white page | Missing `<link rel="stylesheet">` or wrong path | Verify styles.css path relative to slide file |
| Layout not centering | Missing `justify-content:center` on `.slide-content` | Add flex centering rules |
| Notes not loading | `fetch()` used for notes | Use `window.SLIDE_NOTES` in `notes-data.js` |
| Nav broken after file copy | Relative paths to CSS/JS broken | Use absolute paths or keep files co-located |
| External fonts blank | Google Fonts URL | Use font stack only: Helvetica Neue, Arial |
| Animation frozen mid-state | CSS `transition` or `animation` present | Remove all animation properties |
| Slide too tall / content clips | `height:100%` on card body | Remove height constraint from card body |

## File Structure Per Deck

```
deck-directory/
  styles.css          — shared theme (CSS variables, base styles)
  notes-data.js       — all speaker notes for all slides
  nav.js              — keyboard navigation, notes panel toggle
  slide-01.html
  slide-02.html
  ...
  slide-NN.html
  index.html          — grid navigator (4-column, act dividers)
```

The deck directory must be self-contained. Never reference files outside it,
and never write temp copies to `/tmp/` — relative CSS paths break.

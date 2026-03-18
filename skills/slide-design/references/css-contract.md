# CSS Contract — Slide Class and Zone Conventions

Canonical CSS naming conventions for generated HTML slides. These class names form the contract
between outline generation, HTML rendering, Chrome extraction, and validation.

---

## Naming Conventions

| Element | Pattern | Example |
|---|---|---|
| Slide wrapper | `.slide.{type}` or `.slide-{type}` | `.slide.title-slide`, `.slide-content` |
| Zone element | `.zone-{zone-id}` | `.zone-title`, `.zone-stat1` |
| Stat label (sibling) | `.zone-stat-label` | Follows `.zone-stat*` immediately |

---

## Universal Zone Rules

All zone elements should include:

```css
.zone-* {
  box-sizing: border-box;
  overflow: hidden;
  position: absolute;
}
```

These three properties support predictable Chrome extraction — `getBoundingClientRect()` returns
accurate bounds, overflow is contained, and positioning is deterministic.

---

## Zone Type Rules

### Text Zones

```css
font-size: [N]px;        /* explicit px — never em or rem */
line-height: [N];        /* numeric, unitless — e.g. 1.3 */
```

Font size comes from the active theme's size hierarchy. Explicit px ensures Chrome extracts
consistent computed values for PPTX conversion.

### Image Zones

```css
object-fit: contain | cover;   /* contain for logos/diagrams; cover for full-bleed photos */
```

### Stat Zones

```css
font-size: [N]px;    /* minimum 36px */
font-weight: bold;
```

Stat labels paired with a stat zone:
```css
font-size: [N]px;    /* minimum 28px; must be < stat font-size */
```

The stat value element must be immediately followed by a label sibling in the DOM. The
dominance check relies on this sibling relationship.

---

## Slide Type Class Inventory

### Title Slide (`.slide.title-slide`, `.slide-title-hero`)

| Zone class | Type | Role |
|---|---|---|
| `.zone-background` | image | background |
| `.zone-title` | text | heading |
| `.zone-subtitle` | text | subheading |

### Stat Callout (`.slide-stat-callout`)

| Zone class | Type | Role | Min font-size |
|---|---|---|---|
| `.zone-stat1` | text | primary-stat | 36px |
| `.zone-stat-label` (after stat) | text | stat-label | 28px |
| `.zone-stat2`, `.zone-stat3` | text | primary-stat | 36px |
| `.zone-context` | text | caption | — |

### Content / Two-Column (`.slide-content`, `.slide-two-column`)

| Zone class | Type | Role |
|---|---|---|
| `.zone-headline` | text | heading |
| `.zone-body` | text | body |
| `.zone-visual` | image | supporting-visual |

### Section Divider (`.slide-section-divider`)

| Zone class | Type | Role |
|---|---|---|
| `.zone-section-number` | text | eyebrow |
| `.zone-section-title` | text | heading |
| `.zone-section-preview` | text | subheading |

### Closing CTA (`.slide-closing-cta`)

| Zone class | Type | Role |
|---|---|---|
| `.zone-cta-headline` | text | heading |
| `.zone-cta-actions` | text | body |
| `.zone-cta-contact` | text | caption |

### Quote Pull (`.slide-quote-pull`)

| Zone class | Type | Role |
|---|---|---|
| `.zone-quote-text` | text | quote |
| `.zone-attribution` | text | caption |

### Timeline (`.slide-timeline`)

| Zone class | Type | Role |
|---|---|---|
| `.zone-timeline-track` | text | structural |
| `.zone-event-label` | text | label (repeated) |

### Comparison Matrix (`.slide-comparison-matrix`)

| Zone class | Type | Role |
|---|---|---|
| `.zone-criteria` | text | table-header |
| `.zone-option-a` | text | table-column |
| `.zone-option-b` | text | table-column |
| `.zone-recommendation` | text | callout |

---

## Conservative Fallback Layout

When validation detects unresolvable layout failures, the fallback guarantees legibility at the
cost of visual design:

```css
.slide {
  padding: 48px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.zone-title, .zone-headline, .zone-cta-headline, .zone-section-title {
  font-size: 28px;
  line-height: 1.2;
}

.zone-body, .zone-cta-actions {
  font-size: 16px;
  line-height: 1.4;
}

.zone-stat1, .zone-stat2, .zone-stat3 {
  font-size: 36px;
  font-weight: bold;
}

.zone-visual, .zone-background {
  display: none;  /* images omitted in conservative fallback */
}
```

Slides rendered via conservative fallback are flagged as `status: REVIEW` in validation.

---

## CSS Contract Validation

During validation, the rendered DOM can be checked against this contract:

| Check | Method |
|---|---|
| Slide class present | `.slide` wrapper exists |
| Zone classes present | Expected zones for the slide type have matching elements |
| Universal rules applied | `getComputedStyle(zone).boxSizing === 'border-box'` |
| Text zones have explicit px font-size | `getComputedStyle(zone).fontSize` ends in `px` |
| Stat zones meet minimum font-size | parsed px value ≥ 36px |

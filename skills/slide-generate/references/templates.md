# Slide Templates

HTML templates for each slide type. All templates use CSS custom properties from
the active theme. Values shown here use the midnight-purple theme as examples.

---

## Title Slide

```html
<div class="slide title-slide">
    <h1>{title}</h1>
    <p class="subtitle">{subtitle}</p>
    <div class="accent-bar"></div>
</div>
```

CSS:
```css
.title-slide h1 {
    color: var(--text-primary);
    font-size: var(--title-size);
    font-weight: 700;
    text-align: center;
    padding-top: 220px;
    font-family: var(--font-heading);
}
.title-slide .subtitle {
    color: var(--text-secondary);
    font-size: var(--subtitle-size);
    text-align: center;
    margin-top: 24px;
}
.title-slide .accent-bar {
    width: 120px;
    height: 4px;
    background: var(--primary);
    margin: 32px auto 0;
}
```

---

## Content Slide — Bullets

```html
<div class="slide content-slide">
    <h2 class="slide-title">{title}</h2>
    <ul class="bullet-list">
        <li>{point 1}</li>
        <li>{point 2}</li>
        <li>{point 3}</li>
    </ul>
</div>
```

CSS:
```css
.content-slide .slide-title {
    color: var(--text-primary);
    font-size: var(--heading-size);
    font-weight: 700;
    padding: 60px 80px 0;
    font-family: var(--font-heading);
}
.content-slide .bullet-list {
    padding: 40px 80px 0 120px;
    list-style: none;
}
.content-slide .bullet-list li {
    color: var(--text-secondary);
    font-size: var(--body-size);
    line-height: 1.6;
    margin-bottom: 16px;
    padding-left: 24px;
    position: relative;
}
.content-slide .bullet-list li::before {
    content: '';
    position: absolute;
    left: 0;
    top: 10px;
    width: 8px;
    height: 8px;
    background: var(--primary);
    border-radius: 50%;
}
```

---

## Content Slide — Two Column

```html
<div class="slide two-col-slide">
    <h2 class="slide-title">{title}</h2>
    <div class="columns">
        <div class="col-left">
            <p>{left content}</p>
        </div>
        <div class="col-right">
            <p>{right content}</p>
        </div>
    </div>
</div>
```

CSS:
```css
.two-col-slide .columns {
    display: flex;
    gap: 32px;
    padding: 40px 80px 0;
}
.two-col-slide .col-left {
    flex: 3;
}
.two-col-slide .col-right {
    flex: 2;
}
.two-col-slide .col-left p,
.two-col-slide .col-right p {
    color: var(--text-secondary);
    font-size: var(--body-size);
    line-height: 1.5;
}
```

---

## Stats / Metrics Slide

```html
<div class="slide stats-slide">
    <h2 class="slide-title">{title}</h2>
    <div class="stat-cards">
        <div class="stat-card">
            <div class="stat-value">{value}</div>
            <div class="stat-label">{label}</div>
        </div>
        <!-- repeat for each stat -->
    </div>
</div>
```

CSS:
```css
.stats-slide .stat-cards {
    display: flex;
    gap: 24px;
    padding: 60px 80px 0;
    justify-content: center;
}
.stats-slide .stat-card {
    background: var(--card-bg);
    border-radius: var(--card-radius);
    padding: var(--card-padding);
    min-width: 200px;
    text-align: center;
    box-shadow: var(--card-shadow);
}
.stats-slide .stat-value {
    color: var(--primary);
    font-size: 48px;
    font-weight: 700;
    font-family: var(--font-heading);
}
.stats-slide .stat-label {
    color: var(--text-muted);
    font-size: var(--caption-size);
    margin-top: 8px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
```

---

## Comparison Slide

```html
<div class="slide comparison-slide">
    <h2 class="slide-title">{title}</h2>
    <div class="compare-columns">
        <div class="compare-col">
            <h3 class="compare-header">{header A}</h3>
            <ul>
                <li>{point}</li>
            </ul>
        </div>
        <div class="compare-divider"></div>
        <div class="compare-col">
            <h3 class="compare-header">{header B}</h3>
            <ul>
                <li>{point}</li>
            </ul>
        </div>
    </div>
</div>
```

CSS:
```css
.comparison-slide .compare-columns {
    display: flex;
    gap: 0;
    padding: 40px 80px 0;
    align-items: flex-start;
}
.comparison-slide .compare-col {
    flex: 1;
    padding: 0 24px;
}
.comparison-slide .compare-divider {
    width: 2px;
    background: var(--border);
    align-self: stretch;
    margin: 0 8px;
}
.comparison-slide .compare-header {
    color: var(--primary);
    font-size: var(--subheading-size);
    font-weight: 700;
    margin-bottom: 20px;
}
.comparison-slide .compare-col ul {
    list-style: none;
    padding: 0;
}
.comparison-slide .compare-col li {
    color: var(--text-secondary);
    font-size: var(--body-size);
    line-height: 1.5;
    margin-bottom: 12px;
}
```

---

## Quote Slide

```html
<div class="slide quote-slide">
    <div class="quote-container">
        <div class="quote-bar"></div>
        <blockquote>
            <p class="quote-text">{quote}</p>
            <cite class="quote-author">— {author}</cite>
        </blockquote>
    </div>
</div>
```

CSS:
```css
.quote-slide .quote-container {
    display: flex;
    align-items: flex-start;
    padding: 160px 120px 0;
    gap: 24px;
}
.quote-slide .quote-bar {
    width: 4px;
    min-height: 100px;
    background: var(--primary);
    flex-shrink: 0;
}
.quote-slide .quote-text {
    color: var(--text-primary);
    font-size: 28px;
    font-style: italic;
    line-height: 1.5;
}
.quote-slide .quote-author {
    color: var(--text-muted);
    font-size: var(--body-size);
    display: block;
    margin-top: 20px;
    font-style: normal;
}
```

---

## Section Divider

```html
<div class="slide section-slide">
    <h2 class="section-name">{section name}</h2>
    <div class="section-accent"></div>
</div>
```

CSS:
```css
.section-slide .section-name {
    color: var(--text-primary);
    font-size: var(--title-size);
    font-weight: 700;
    text-align: center;
    padding-top: 280px;
    font-family: var(--font-heading);
}
.section-slide .section-accent {
    width: 80px;
    height: 4px;
    background: var(--accent);
    margin: 24px auto 0;
}
```

---

## CTA / Closing Slide

```html
<div class="slide cta-slide">
    <h2 class="cta-title">{call to action}</h2>
    <ul class="cta-points">
        <li>{next step 1}</li>
        <li>{next step 2}</li>
        <li>{next step 3}</li>
    </ul>
</div>
```

CSS:
```css
.cta-slide .cta-title {
    color: var(--text-primary);
    font-size: var(--heading-size);
    font-weight: 700;
    text-align: center;
    padding-top: 160px;
    font-family: var(--font-heading);
}
.cta-slide .cta-points {
    list-style: none;
    padding: 40px 200px 0;
    text-align: center;
}
.cta-slide .cta-points li {
    color: var(--text-secondary);
    font-size: 20px;
    line-height: 1.6;
    margin-bottom: 16px;
}
.cta-slide .cta-points li:first-child {
    color: var(--accent);
    font-weight: 600;
}
```

---

## Template Selection Guide

| Outline Type | Template | When |
|---|---|---|
| `title` | Title Slide | First slide, deck opener |
| `section` | Section Divider | Between acts |
| `content` + layout `bullets` | Content — Bullets | Default for text content |
| `content` + layout `two-column` | Content — Two Column | Dual information |
| `content` + layout `image-text` | Content — Two Column | Text + visual |
| `stats` | Stats / Metrics | Numerical data, KPIs |
| `comparison` | Comparison | Before/after, A vs B |
| `quote` | Quote | Testimonials, key quotes |
| `cta` | CTA / Closing | Final slide, next steps |
| `blank` | Section Divider (minimal) | Visual pause |

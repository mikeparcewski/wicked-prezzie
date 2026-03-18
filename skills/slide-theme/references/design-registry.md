# Design Registry — Shared Design Assets

A git-backed shared repository of reusable design components. Stores the building blocks that
themes and profiles are assembled from.

---

## What Lives in the Registry

```
registry/
├── palettes/            # Named color palettes
│   ├── corporate-bold.json
│   ├── startup-fresh.json
│   └── healthcare-clean.json
├── layouts/             # Spatial composition rules
│   ├── executive-dense.json
│   └── investor-airy.json
├── iconsets/            # Icon family references
│   ├── lucide-line.json
│   └── phosphor-filled.json
└── strategies/          # Named design strategy bundles
    ├── executive-dense.json
    ├── investor-airy.json
    └── workshop-warm.json
```

---

## Registry Operations

- "sync registry" / "pull registry" → pull latest from the remote git repo
- "push palette [name]" / "push strategy [name]" → contribute an asset
- "list registry" → show all assets by category
- "show registry asset [name]" → display a specific asset
- "set registry remote [url]" → configure the git remote URL
- "registry status" → show sync status

---

## Registry Configuration

Store in `~/.something-wicked/wicked-prezzie/registry/config.json`:

```json
{
  "remote_url": "https://github.com/your-org/design-registry",
  "branch": "main",
  "last_pulled": "2025-03-05T10:00:00Z",
  "auto_pull": false
}
```

`auto_pull: false` by default — always prompt before pulling.

---

## Palette Schema

```json
{
  "name": "corporate-bold",
  "version": "2025-Q1",
  "description": "Bold corporate palette — primary purple system",
  "colors": {
    "primary": "#A100FF",
    "secondary": "#460073",
    "accent": "#FFFFFF",
    "background_light": "#F5F5F5",
    "background_dark": "#1A0038",
    "text_on_light": "#1A1A1A",
    "text_on_dark": "#FFFFFF",
    "highlight": "#7B00CC"
  }
}
```

---

## Strategy Schema

A strategy bundles layout philosophy, density, and imagery preferences. Strategies differentiate
"same palette, different feel."

```json
{
  "name": "executive-dense",
  "description": "High-information density for executive audiences. Data-forward, minimal decoration.",
  "density": "high",
  "margins": "tight",
  "preferred_templates": ["stat-callout", "two-column", "section-divider"],
  "avoid_templates": ["team-grid", "quote-pull", "closing-cta"],
  "image_treatment": "inset-right",
  "icon_usage": "minimal",
  "slide_count_bias": "lean",
  "tone": "formal"
}
```

```json
{
  "name": "investor-airy",
  "description": "Story-forward, spacious layouts for investor or board audiences.",
  "density": "low",
  "margins": "generous",
  "preferred_templates": ["title-hero", "stat-callout", "quote-pull", "closing-cta"],
  "avoid_templates": ["comparison-matrix"],
  "image_treatment": "full-bleed",
  "icon_usage": "none",
  "slide_count_bias": "lean",
  "tone": "narrative"
}
```

---

## Iconsets Schema

```json
{
  "name": "lucide-line",
  "description": "Lucide icon set — clean line style, MIT licensed",
  "style": "line",
  "license": "MIT",
  "source_url": "https://lucide.dev",
  "categories": ["arrows", "actions", "data", "people", "tech", "finance"],
  "format": "svg",
  "usage_note": "Best at 24-48px. Use at consistent size across slide."
}
```

---

## Contributing to the Registry

When sharing a new palette, template, or strategy:

1. Plugin formats it into the correct schema
2. Shows a preview of the asset JSON:
   > "Ready to push to the registry. This will be visible to your team. Confirm?"
3. On confirm: commits to git remote, pushes
4. Reports: `✓ Pushed 'my-brand' palette to registry`

Contributors should add a `description` field — prompted if missing.

---

## Registry in Theme Selection

During theme selection:
- Check if registry cache is fresh (pulled within current session or within 24h)
- If stale: *"Your design registry hasn't been synced this session — pull latest? (yes / skip)"*
- Registry palettes appear alongside local themes
- Themes built from registry components record their sources — so if a registry asset updates,
  the user can be notified

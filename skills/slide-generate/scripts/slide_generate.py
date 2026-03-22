#!/usr/bin/env python3
"""
slide-generate — Generate themed HTML slides from structured outlines.

Usage:
    python slide-generate/scripts/slide_generate.py --outline outline.json --output-dir ./slides/
    python slide-generate/scripts/slide_generate.py --type title --title "Hello" --output test.html
    python slide-generate/scripts/slide_generate.py --list-templates
"""

import argparse, json, os, re, sys
from pathlib import Path

_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_root / "slide-theme" / "scripts"))
sys.path.insert(0, str(_root / "shared"))
from paths import output_path
from slide_theme import load_theme, get_active_theme_name, theme_to_css

VIEWPORT_W = 1280
VIEWPORT_H = 720


def _slugify(title: str, max_len: int = 40) -> str:
    """Convert a slide title to a filesystem-safe kebab-case slug.

    'AI reduced latency by 60%' → 'ai-reduced-latency-by-60'
    """
    s = title.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)       # strip non-alphanumeric
    s = re.sub(r"[\s_]+", "-", s)         # spaces/underscores → hyphens
    s = re.sub(r"-{2,}", "-", s)          # collapse hyphens
    s = s.strip("-")
    return s[:max_len].rstrip("-") or "untitled"


def _resolve_css_vars(theme):
    """Build a dict of CSS variable values from theme for inline resolution."""
    c = theme["colors"]
    f = theme["fonts"]
    s = theme["sizes"]
    sp = theme["spacing"]
    layout = theme.get("layout", {})
    card = theme.get("card", {})
    return {
        "--bg": c["background"],
        "--surface": c["surface"],
        "--primary": c["primary"],
        "--secondary": c["secondary"],
        "--accent": c["accent"],
        "--text-primary": c["text_primary"],
        "--text-secondary": c["text_secondary"],
        "--text-muted": c["text_muted"],
        "--border": c["border"],
        "--font-heading": f"{f['heading']}, sans-serif",
        "--font-body": f"{f['body']}, sans-serif",
        "--title-size": s["title"],
        "--subtitle-size": s["subtitle"],
        "--heading-size": s.get("heading", "36px"),
        "--subheading-size": s.get("subheading", "24px"),
        "--body-size": s["body"],
        "--caption-size": s["caption"],
        "--margin": sp["margin"],
        "--gap-large": sp["gap_large"],
        "--gap": sp["gap_medium"],
        "--gap-small": sp["gap_small"],
        "--card-bg": card.get("background", c["surface"]),
        "--card-radius": card.get("border_radius", "12px"),
        "--card-padding": card.get("padding", "24px"),
        "--card-shadow": card.get("shadow", "none"),
        "--vertical-align": layout.get("vertical_align", "start"),
        "--content-justify": layout.get("content_justify", "start"),
    }


def _css_root_block(css_vars):
    """Generate :root CSS block from resolved variables."""
    lines = ["    :root {"]
    for key, val in css_vars.items():
        lines.append(f"      {key}: {val};")
    lines.append("    }")
    return "\n".join(lines)


def _base_css():
    """Base CSS shared by all slide types."""
    return """
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: var(--bg); font-family: var(--font-body); }
    .slide {
      width: 1280px; height: 720px;
      position: relative; overflow: hidden;
      background: var(--bg);
      display: flex;
      flex-direction: column;
      align-items: var(--content-justify, start);
      justify-content: var(--vertical-align, start);
    }
    .slide-content {
      width: 100%;
      padding: var(--margin);
    }
"""


def _type_css():
    """CSS for all slide type templates."""
    return """
    /* Title slide */
    .title-slide h1 {
      color: var(--text-primary); font-size: var(--title-size);
      font-weight: 700; text-align: center; padding-top: 220px;
      font-family: var(--font-heading);
    }
    .title-slide .subtitle {
      color: var(--text-secondary); font-size: var(--subtitle-size);
      text-align: center; margin-top: 24px;
    }
    .title-slide .accent-bar {
      width: 120px; height: 4px; background: var(--primary);
      margin: 32px auto 0;
    }

    /* Content slide - bullets */
    .content-slide .slide-title, .two-col-slide .slide-title,
    .stats-slide .slide-title, .comparison-slide .slide-title {
      color: var(--text-primary); font-size: var(--heading-size);
      font-weight: 700; padding: 60px 80px 0;
      font-family: var(--font-heading);
    }
    .content-slide .bullet-list {
      padding: 40px 80px 0 120px; list-style: none;
    }
    .content-slide .bullet-list li {
      color: var(--text-secondary); font-size: var(--body-size);
      line-height: 1.6; margin-bottom: 16px;
      padding-left: 24px; position: relative;
    }
    .content-slide .bullet-list li::before {
      content: ''; position: absolute; left: 0; top: 10px;
      width: 8px; height: 8px; background: var(--primary); border-radius: 50%;
    }

    /* Two column */
    .two-col-slide .columns {
      display: flex; gap: 32px; padding: 40px 80px 0;
    }
    .two-col-slide .col-left { flex: 3; }
    .two-col-slide .col-right { flex: 2; }
    .two-col-slide p {
      color: var(--text-secondary); font-size: var(--body-size); line-height: 1.5;
    }

    /* Stats */
    .stats-slide .stat-cards {
      display: flex; gap: 24px; padding: 60px 80px 0; justify-content: center;
    }
    .stats-slide .stat-card {
      background: var(--card-bg); border-radius: var(--card-radius);
      padding: var(--card-padding); min-width: 200px; text-align: center;
      box-shadow: var(--card-shadow);
    }
    .stats-slide .stat-value {
      color: var(--primary); font-size: 48px; font-weight: 700;
      font-family: var(--font-heading);
    }
    .stats-slide .stat-label {
      color: var(--text-muted); font-size: var(--caption-size);
      margin-top: 8px; text-transform: uppercase; letter-spacing: 1px;
    }

    /* Comparison */
    .comparison-slide .compare-columns {
      display: flex; gap: 0; padding: 40px 80px 0; align-items: flex-start;
    }
    .comparison-slide .compare-col { flex: 1; padding: 0 24px; }
    .comparison-slide .compare-divider {
      width: 2px; background: var(--border); align-self: stretch; margin: 0 8px;
    }
    .comparison-slide .compare-header {
      color: var(--primary); font-size: var(--subheading-size);
      font-weight: 700; margin-bottom: 20px;
    }
    .comparison-slide .compare-col ul { list-style: none; padding: 0; }
    .comparison-slide .compare-col li {
      color: var(--text-secondary); font-size: var(--body-size);
      line-height: 1.5; margin-bottom: 12px;
    }

    /* Quote */
    .quote-slide .quote-container {
      display: flex; align-items: flex-start; padding: 180px 120px 0; gap: 24px;
    }
    .quote-slide .quote-bar {
      width: 4px; min-height: 80px; background: var(--primary); flex-shrink: 0;
    }
    .quote-slide .quote-text {
      color: var(--text-primary); font-size: 28px; font-style: italic; line-height: 1.5;
    }
    .quote-slide .quote-author {
      color: var(--text-muted); font-size: var(--body-size);
      display: block; margin-top: 20px; font-style: normal;
    }

    /* Section divider */
    .section-slide .section-name {
      color: var(--text-primary); font-size: var(--title-size);
      font-weight: 700; text-align: center; padding-top: 280px;
      font-family: var(--font-heading);
    }
    .section-slide .section-summary {
      color: var(--text-secondary); font-size: var(--subheading-size);
      font-weight: 400; text-align: center; margin-top: 16px;
      font-family: var(--font-body);
    }
    .section-slide .section-accent {
      width: 80px; height: 4px; background: var(--accent); margin: 24px auto 0;
    }

    /* CTA */
    .cta-slide .cta-title {
      color: var(--text-primary); font-size: var(--heading-size);
      font-weight: 700; text-align: center; padding-top: 160px;
      font-family: var(--font-heading);
    }
    .cta-slide .cta-points {
      list-style: none; padding: 40px 200px 0; text-align: center;
    }
    .cta-slide .cta-points li {
      color: var(--text-secondary); font-size: 20px;
      line-height: 1.6; margin-bottom: 16px;
    }
    .cta-slide .cta-points li:first-child {
      color: var(--accent); font-weight: 600;
    }
"""


def _html_escape(text):
    """Escape HTML special characters."""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def _notes_toggle_js():
    """Inline JS to toggle speaker notes with N key when viewing HTML."""
    return """
    <script>
    document.addEventListener('keydown', function(e) {
      if (e.key === 'n' || e.key === 'N') {
        var notes = document.querySelector('.speaker-notes');
        if (notes) {
          var visible = notes.style.display !== 'none';
          notes.style.display = visible ? 'none' : 'block';
        }
      }
    });
    </script>"""


def _notes_css():
    """CSS for the speaker notes panel when toggled visible."""
    return """
    .speaker-notes {
      display: none;
      position: fixed;
      bottom: 0; left: 0; right: 0;
      max-height: 30vh;
      overflow-y: auto;
      background: rgba(0, 0, 0, 0.92);
      color: #e0e0e0;
      font-family: system-ui, sans-serif;
      font-size: 14px;
      line-height: 1.5;
      padding: 16px 24px;
      border-top: 2px solid rgba(255, 255, 255, 0.15);
      z-index: 9999;
    }
    .speaker-notes::before {
      content: 'Speaker Notes (press N to hide)';
      display: block;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #888;
      margin-bottom: 8px;
    }
"""


def _wrap_html(body_content, css_vars, slide_class, notes=""):
    """Wrap slide body in full HTML document with embedded speaker notes."""
    notes_div = ""
    if notes:
        notes_div = f'\n    <div class="speaker-notes">{_html_escape(notes)}</div>'
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width={VIEWPORT_W}">
    <style>
{_css_root_block(css_vars)}
{_base_css()}
{_type_css()}
{_notes_css()}
    </style>
</head>
<body>
    <div class="slide {slide_class}">
{body_content}
    </div>{notes_div}
{_notes_toggle_js()}
</body>
</html>
"""


# --- Template renderers ---

def render_title(slide, css_vars):
    title = _html_escape(slide.get("title", ""))
    subtitle = _html_escape(slide.get("subtitle", ""))
    body = f"        <h1>{title}</h1>"
    if subtitle:
        body += f'\n        <p class="subtitle">{subtitle}</p>'
    body += '\n        <div class="accent-bar"></div>'
    return _wrap_html(body, css_vars, "title-slide", slide.get("notes", ""))


def render_section(slide, css_vars):
    name = _html_escape(slide.get("title", ""))
    subtitle = _html_escape(slide.get("subtitle", ""))
    body = f'        <h2 class="section-name">{name}</h2>'
    if subtitle:
        body += f'\n        <p class="section-summary">{subtitle}</p>'
    body += '\n        <div class="section-accent"></div>'
    return _wrap_html(body, css_vars, "section-slide", slide.get("notes", ""))


def render_content_bullets(slide, css_vars):
    title = _html_escape(slide.get("title", ""))
    items = slide.get("body", [])
    body = f'        <h2 class="slide-title">{title}</h2>\n'
    body += '        <ul class="bullet-list">\n'
    for item in items:
        text = _html_escape(item if isinstance(item, str) else str(item))
        body += f"            <li>{text}</li>\n"
    body += "        </ul>"
    return _wrap_html(body, css_vars, "content-slide", slide.get("notes", ""))


def render_content_two_column(slide, css_vars):
    title = _html_escape(slide.get("title", ""))
    items = slide.get("body", [])
    mid = len(items) // 2 or 1
    left_items = items[:mid]
    right_items = items[mid:]

    body = f'        <h2 class="slide-title">{title}</h2>\n'
    body += '        <div class="columns">\n'
    body += '            <div class="col-left">\n'
    for item in left_items:
        body += f'                <p>{_html_escape(item if isinstance(item, str) else str(item))}</p>\n'
    body += '            </div>\n'
    body += '            <div class="col-right">\n'
    for item in right_items:
        body += f'                <p>{_html_escape(item if isinstance(item, str) else str(item))}</p>\n'
    body += '            </div>\n'
    body += '        </div>'
    return _wrap_html(body, css_vars, "two-col-slide", slide.get("notes", ""))


def render_stats(slide, css_vars):
    title = _html_escape(slide.get("title", ""))
    items = slide.get("body", [])
    body = f'        <h2 class="slide-title">{title}</h2>\n'
    body += '        <div class="stat-cards">\n'
    for item in items:
        if isinstance(item, dict):
            value = _html_escape(item.get("stat", item.get("value", "")))
            label = _html_escape(item.get("label", ""))
        else:
            value = _html_escape(str(item))
            label = ""
        body += '            <div class="stat-card">\n'
        body += f'                <div class="stat-value">{value}</div>\n'
        if label:
            body += f'                <div class="stat-label">{label}</div>\n'
        body += '            </div>\n'
    body += '        </div>'
    return _wrap_html(body, css_vars, "stats-slide", slide.get("notes", ""))


def render_comparison(slide, css_vars):
    title = _html_escape(slide.get("title", ""))
    items = slide.get("body", [])
    # Expect body to have headers and items, or split evenly
    mid = len(items) // 2 or 1
    left_items = items[:mid]
    right_items = items[mid:]

    headers = slide.get("headers", ["Option A", "Option B"])

    body = f'        <h2 class="slide-title">{title}</h2>\n'
    body += '        <div class="compare-columns">\n'
    body += '            <div class="compare-col">\n'
    body += f'                <h3 class="compare-header">{_html_escape(headers[0])}</h3>\n'
    body += '                <ul>\n'
    for item in left_items:
        body += f'                    <li>{_html_escape(item if isinstance(item, str) else str(item))}</li>\n'
    body += '                </ul>\n'
    body += '            </div>\n'
    body += '            <div class="compare-divider"></div>\n'
    body += '            <div class="compare-col">\n'
    body += f'                <h3 class="compare-header">{_html_escape(headers[1] if len(headers) > 1 else "Option B")}</h3>\n'
    body += '                <ul>\n'
    for item in right_items:
        body += f'                    <li>{_html_escape(item if isinstance(item, str) else str(item))}</li>\n'
    body += '                </ul>\n'
    body += '            </div>\n'
    body += '        </div>'
    return _wrap_html(body, css_vars, "comparison-slide", slide.get("notes", ""))


def render_quote(slide, css_vars):
    title = _html_escape(slide.get("title", ""))
    body_items = slide.get("body", [])
    author = ""
    quote_text = title
    if body_items:
        if isinstance(body_items[0], str):
            author = body_items[0]
        elif isinstance(body_items[0], dict):
            author = body_items[0].get("author", body_items[0].get("attribution", ""))

    body = '        <div class="quote-container">\n'
    body += '            <div class="quote-bar"></div>\n'
    body += '            <blockquote>\n'
    body += f'                <p class="quote-text">{_html_escape(quote_text)}</p>\n'
    if author:
        body += f'                <cite class="quote-author">— {_html_escape(author)}</cite>\n'
    body += '            </blockquote>\n'
    body += '        </div>'
    return _wrap_html(body, css_vars, "quote-slide", slide.get("notes", ""))


def render_cta(slide, css_vars):
    title = _html_escape(slide.get("title", ""))
    items = slide.get("body", [])
    body = f'        <h2 class="cta-title">{title}</h2>\n'
    if items:
        body += '        <ul class="cta-points">\n'
        for item in items:
            text = _html_escape(item if isinstance(item, str) else str(item))
            body += f"            <li>{text}</li>\n"
        body += "        </ul>"
    return _wrap_html(body, css_vars, "cta-slide", slide.get("notes", ""))


# --- Renderer dispatch ---

RENDERERS = {
    "title": render_title,
    "section": render_section,
    "content": {
        "bullets": render_content_bullets,
        "two-column": render_content_two_column,
        "image-text": render_content_two_column,
    },
    "stats": render_stats,
    "comparison": render_comparison,
    "quote": render_quote,
    "cta": render_cta,
    "blank": render_section,
}


def render_slide(slide, css_vars):
    """Render a single slide dict to HTML string."""
    slide_type = slide.get("type", "content")
    renderer = RENDERERS.get(slide_type)

    if isinstance(renderer, dict):
        layout = slide.get("layout", "bullets")
        renderer = renderer.get(layout, render_content_bullets)

    if renderer is None:
        renderer = render_content_bullets

    return renderer(slide, css_vars)


def generate_from_outline(outline, theme_name=None, output_dir=None):
    if output_dir is None:
        output_dir = output_path("slides")
    """Generate HTML slides from an outline JSON structure."""
    # Resolve theme
    t_name = theme_name or outline.get("theme") or get_active_theme_name()
    theme = load_theme(t_name)
    css_vars = _resolve_css_vars(theme)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    manifest = []
    slide_num = 0
    used_slugs: set[str] = set()

    # Support both "sections" (preferred) and "acts" (legacy alias)
    sections = outline.get("sections") or outline.get("acts", [])
    auto_dividers = outline.get("auto_dividers", True)

    for sec_idx, section in enumerate(sections):
        sec_name = section.get("name", "")
        sec_summary = section.get("summary", "")

        # Auto-insert section divider between sections (skip before first)
        if auto_dividers and sec_idx > 0 and sec_name:
            # Check if the section already starts with a section/divider slide
            first_slide_type = (section.get("slides") or [{}])[0].get("type", "")
            if first_slide_type not in ("section", "title"):
                slide_num += 1
                divider_slug = _slugify(sec_name)
                base_slug = divider_slug
                counter = 2
                while divider_slug in used_slugs:
                    divider_slug = f"{base_slug}-{counter}"
                    counter += 1
                used_slugs.add(divider_slug)

                divider_slide = {"type": "section", "title": sec_name}
                if sec_summary:
                    divider_slide["subtitle"] = sec_summary
                divider_html = render_slide(divider_slide, css_vars)
                divider_filename = f"{slide_num:02d}-{divider_slug}.html"
                divider_filepath = output_path / divider_filename
                divider_filepath.write_text(divider_html, encoding="utf-8")

                manifest.append({
                    "file": divider_filename,
                    "order": slide_num,
                    "slug": divider_slug,
                    "type": "section",
                    "title": sec_name,
                    "section": sec_name,
                    "auto_generated": True,
                })
                print(f"  Generated {divider_filename} (section divider: {sec_name})")

        for slide in section.get("slides", []):
            slide_num += 1
            slug = _slugify(slide.get("title", "untitled"))
            # Deduplicate: append -2, -3, etc. if slug already used
            base_slug = slug
            counter = 2
            while slug in used_slugs:
                slug = f"{base_slug}-{counter}"
                counter += 1
            used_slugs.add(slug)

            filename = f"{slide_num:02d}-{slug}.html"
            filepath = output_path / filename

            html = render_slide(slide, css_vars)
            filepath.write_text(html, encoding="utf-8")

            manifest.append({
                "file": filename,
                "order": slide_num,
                "slug": slug,
                "type": slide.get("type", "content"),
                "title": slide.get("title", ""),
                "section": sec_name,
            })
            print(f"  Generated {filename} ({slide.get('type', 'content')}: {slide.get('title', '')[:50]})")

    # Write manifest
    manifest_path = output_path / "slides.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\n  {slide_num} slides generated in {output_path}/")
    print(f"  Manifest: {manifest_path}")
    print(f"  Theme: {t_name}")

    return manifest


def generate_single(slide_type, title, subtitle=None, body=None, theme_name=None, output=None):
    """Generate a single slide for testing."""
    t_name = theme_name or get_active_theme_name()
    theme = load_theme(t_name)
    css_vars = _resolve_css_vars(theme)

    slide = {"type": slide_type, "title": title}
    if subtitle:
        slide["subtitle"] = subtitle
    if body:
        slide["body"] = body

    html = render_slide(slide, css_vars)

    if output:
        Path(output).write_text(html, encoding="utf-8")
        print(f"  Generated {output}")
    else:
        print(html)


def main():
    parser = argparse.ArgumentParser(description="Generate themed HTML slides from outlines")

    parser.add_argument("--outline", "-i", help="Path to outline JSON file")
    parser.add_argument("--output-dir", "-d", default=output_path("slides"), help="Output directory for slide HTML files")
    parser.add_argument("--theme", "-t", help="Theme name (overrides outline)")
    parser.add_argument("--viewport", help="Viewport dimensions (WxH)")
    parser.add_argument("--type", help="Single slide type to generate")
    parser.add_argument("--title", help="Slide title (for single slide mode)")
    parser.add_argument("--subtitle", help="Slide subtitle (for single slide mode)")
    parser.add_argument("--output", "-o", help="Output file (for single slide mode)")
    parser.add_argument("--list-templates", action="store_true", help="List available templates")

    args = parser.parse_args()

    if args.viewport:
        global VIEWPORT_W, VIEWPORT_H
        parts = args.viewport.lower().split("x")
        VIEWPORT_W = int(parts[0])
        VIEWPORT_H = int(parts[1])

    if args.list_templates:
        print("Available slide templates:")
        print("  title        — Deck opener with title, subtitle, accent bar")
        print("  section      — Section divider between acts")
        print("  content      — Standard content (layouts: bullets, two-column, image-text)")
        print("  stats        — Metric cards with large numbers")
        print("  comparison   — Side-by-side comparison columns")
        print("  quote        — Pull quote with attribution")
        print("  cta          — Call to action / closing slide")
        print("  blank        — Minimal section marker")
        return

    if args.type:
        if not args.title:
            print("Error: --title required with --type")
            sys.exit(1)
        generate_single(args.type, args.title, args.subtitle, theme_name=args.theme, output=args.output)
        return

    if args.outline:
        with open(args.outline) as f:
            outline = json.load(f)
        generate_from_outline(outline, theme_name=args.theme, output_dir=args.output_dir)
        return

    parser.print_help()


if __name__ == "__main__":
    main()

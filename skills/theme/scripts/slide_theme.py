#!/usr/bin/env python3
"""
slide-theme — Manage visual themes for wicked-pptx slide decks.

Usage:
    python slide-theme/scripts/slide_theme.py list
    python slide-theme/scripts/slide_theme.py show midnight-purple
    python slide-theme/scripts/slide_theme.py create my-brand
    python slide-theme/scripts/slide_theme.py activate midnight-purple
    python slide-theme/scripts/slide_theme.py active
    python slide-theme/scripts/slide_theme.py css midnight-purple
    python slide-theme/scripts/slide_theme.py validate midnight-purple
"""

import argparse, json, math, os, sys
from pathlib import Path

USER_DATA_DIR = Path.home() / ".something-wicked" / "wicked-prezzie"
THEMES_DIR = USER_DATA_DIR / "themes"
BUILTIN_THEMES_DIR = Path(__file__).parent.parent / "themes"
CONFIG_PATH = Path(__file__).parent.parent.parent / "slide-config" / "config.json"

# --- Built-in themes ---

BUILTIN_THEMES = {
    "midnight-purple": {
        "name": "midnight-purple",
        "display_name": "Midnight Purple",
        "description": "Dark theme with purple accents — matches wicked-pptx test slides",
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
            "error": "#EF4444",
        },
        "fonts": {"heading": "Calibri", "body": "Calibri", "mono": "Consolas"},
        "sizes": {
            "title": "48px",
            "subtitle": "28px",
            "heading": "36px",
            "subheading": "24px",
            "body": "18px",
            "caption": "13px",
            "small": "11px",
        },
        "spacing": {
            "margin": "48px",
            "gap_large": "32px",
            "gap_medium": "24px",
            "gap_small": "16px",
            "gap_xs": "8px",
        },
        "layout": {
            "viewport_width": 1280,
            "viewport_height": 720,
            "content_width": 1184,
            "content_start_x": 48,
            "content_start_y": 48,
        },
        "card": {
            "background": "#1A1A2E",
            "border_radius": "12px",
            "padding": "24px",
            "shadow": "0 2px 6px rgba(0,0,0,0.15)",
        },
    },
    "corporate-light": {
        "name": "corporate-light",
        "display_name": "Corporate Light",
        "description": "Light background with navy primary and teal accent",
        "colors": {
            "background": "#FFFFFF",
            "surface": "#F8FAFC",
            "primary": "#1E3A5F",
            "secondary": "#2563EB",
            "accent": "#0891B2",
            "text_primary": "#1E293B",
            "text_secondary": "#64748B",
            "text_muted": "#94A3B8",
            "border": "#E2E8F0",
            "success": "#059669",
            "warning": "#D97706",
            "error": "#DC2626",
        },
        "fonts": {"heading": "Calibri", "body": "Calibri", "mono": "Consolas"},
        "sizes": {
            "title": "44px",
            "subtitle": "26px",
            "heading": "34px",
            "subheading": "22px",
            "body": "18px",
            "caption": "13px",
            "small": "11px",
        },
        "spacing": {
            "margin": "48px",
            "gap_large": "32px",
            "gap_medium": "24px",
            "gap_small": "16px",
            "gap_xs": "8px",
        },
        "layout": {
            "viewport_width": 1280,
            "viewport_height": 720,
            "content_width": 1184,
            "content_start_x": 48,
            "content_start_y": 48,
        },
        "card": {
            "background": "#FFFFFF",
            "border_radius": "8px",
            "padding": "24px",
            "shadow": "0 1px 3px rgba(0,0,0,0.1)",
        },
    },
    "warm-dark": {
        "name": "warm-dark",
        "display_name": "Warm Dark",
        "description": "Dark charcoal with coral primary and gold accent",
        "colors": {
            "background": "#1A1A2E",
            "surface": "#16213E",
            "primary": "#FF6B6B",
            "secondary": "#C44569",
            "accent": "#FFD93D",
            "text_primary": "#F8F8F2",
            "text_secondary": "#B0B0C0",
            "text_muted": "#6B6B80",
            "border": "#2D2D44",
            "success": "#6BCB77",
            "warning": "#FFD93D",
            "error": "#FF6B6B",
        },
        "fonts": {"heading": "Calibri", "body": "Calibri", "mono": "Consolas"},
        "sizes": {
            "title": "48px",
            "subtitle": "28px",
            "heading": "36px",
            "subheading": "24px",
            "body": "18px",
            "caption": "13px",
            "small": "11px",
        },
        "spacing": {
            "margin": "48px",
            "gap_large": "32px",
            "gap_medium": "24px",
            "gap_small": "16px",
            "gap_xs": "8px",
        },
        "layout": {
            "viewport_width": 1280,
            "viewport_height": 720,
            "content_width": 1184,
            "content_start_x": 48,
            "content_start_y": 48,
        },
        "card": {
            "background": "#16213E",
            "border_radius": "12px",
            "padding": "24px",
            "shadow": "0 2px 6px rgba(0,0,0,0.2)",
        },
    },
}


def _hex_to_rgb(hex_color):
    """Convert #RRGGBB to (r, g, b) tuple."""
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def _relative_luminance(r, g, b):
    """WCAG 2.1 relative luminance."""
    def linearize(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def _contrast_ratio(color1, color2):
    """WCAG contrast ratio between two hex colors."""
    l1 = _relative_luminance(*_hex_to_rgb(color1))
    l2 = _relative_luminance(*_hex_to_rgb(color2))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def _is_chromatic(hex_color):
    """Check if a color is chromatic (not grayscale)."""
    r, g, b = _hex_to_rgb(hex_color)
    return not (r == g == b)


def _parse_px(value):
    """Parse '48px' to 48."""
    if isinstance(value, (int, float)):
        return value
    return int(str(value).replace("px", "").strip())


def ensure_themes_dir():
    """Create user themes directory and seed built-in themes if missing."""
    THEMES_DIR.mkdir(parents=True, exist_ok=True)
    for name, theme in BUILTIN_THEMES.items():
        path = THEMES_DIR / f"{name}.json"
        if not path.exists():
            with open(path, "w") as f:
                json.dump(theme, f, indent=2)
    # Also copy any built-in themes shipped with the skill that aren't in user dir
    if BUILTIN_THEMES_DIR.exists():
        for src in BUILTIN_THEMES_DIR.glob("*.json"):
            dest = THEMES_DIR / src.name
            if not dest.exists():
                import shutil
                shutil.copy2(src, dest)


def load_theme(name):
    """Load a theme by name. Checks user dir first, then built-in dir."""
    ensure_themes_dir()
    path = THEMES_DIR / f"{name}.json"
    if not path.exists():
        # Fall back to built-in themes shipped with the skill
        builtin_path = BUILTIN_THEMES_DIR / f"{name}.json"
        if builtin_path.exists():
            path = builtin_path
        else:
            print(f"Error: theme '{name}' not found")
            print(f"Available: {', '.join(list_themes())}")
            sys.exit(1)
    with open(path) as f:
        return json.load(f)


def list_themes():
    """List available theme names from user dir + built-in dir."""
    ensure_themes_dir()
    names = set(p.stem for p in THEMES_DIR.glob("*.json"))
    if BUILTIN_THEMES_DIR.exists():
        names |= set(p.stem for p in BUILTIN_THEMES_DIR.glob("*.json"))
    return sorted(names)


def get_active_theme_name():
    """Get the active theme name from slide-config."""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                cfg = json.load(f)
            return cfg.get("active_theme", "midnight-purple")
        except (json.JSONDecodeError, IOError):
            pass
    return "midnight-purple"


def set_active_theme(name):
    """Set the active theme in slide-config."""
    config = {}
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    config["active_theme"] = name
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def theme_to_css(theme):
    """Convert theme to CSS custom properties block."""
    c = theme["colors"]
    f = theme["fonts"]
    s = theme["sizes"]
    sp = theme["spacing"]
    card = theme.get("card", {})

    lines = [":root {"]
    lines.append(f"  --bg: {c['background']};")
    lines.append(f"  --surface: {c['surface']};")
    lines.append(f"  --primary: {c['primary']};")
    lines.append(f"  --secondary: {c['secondary']};")
    lines.append(f"  --accent: {c['accent']};")
    lines.append(f"  --text-primary: {c['text_primary']};")
    lines.append(f"  --text-secondary: {c['text_secondary']};")
    lines.append(f"  --text-muted: {c['text_muted']};")
    lines.append(f"  --border: {c['border']};")
    lines.append(f"  --font-heading: {f['heading']}, sans-serif;")
    lines.append(f"  --font-body: {f['body']}, sans-serif;")
    lines.append(f"  --title-size: {s['title']};")
    lines.append(f"  --subtitle-size: {s['subtitle']};")
    lines.append(f"  --heading-size: {s['heading']};")
    lines.append(f"  --body-size: {s['body']};")
    lines.append(f"  --caption-size: {s['caption']};")
    lines.append(f"  --margin: {sp['margin']};")
    lines.append(f"  --gap-large: {sp['gap_large']};")
    lines.append(f"  --gap: {sp['gap_medium']};")
    lines.append(f"  --gap-small: {sp['gap_small']};")
    if card:
        lines.append(f"  --card-bg: {card.get('background', c['surface'])};")
        lines.append(f"  --card-radius: {card.get('border_radius', '12px')};")
        lines.append(f"  --card-padding: {card.get('padding', '24px')};")
        lines.append(f"  --card-shadow: {card.get('shadow', 'none')};")
    lines.append("}")
    return "\n".join(lines)


def validate_theme(theme):
    """Validate theme against slide-design principles. Returns (issues, warnings)."""
    issues = []
    warnings = []
    c = theme["colors"]

    # Contrast: text_primary vs background
    ratio = _contrast_ratio(c["text_primary"], c["background"])
    if ratio < 4.5:
        issues.append(f"text_primary vs background contrast {ratio:.1f}:1 (need 4.5:1)")
    elif ratio < 7.0:
        warnings.append(f"text_primary vs background contrast {ratio:.1f}:1 (recommend 7:1)")

    # Contrast: text_secondary vs background
    ratio2 = _contrast_ratio(c["text_secondary"], c["background"])
    if ratio2 < 3.0:
        issues.append(f"text_secondary vs background contrast {ratio2:.1f}:1 (need 3:1)")
    elif ratio2 < 4.5:
        warnings.append(f"text_secondary vs background contrast {ratio2:.1f}:1 (recommend 4.5:1)")

    # Palette size — exclude semantic/status colors and text/border neutrals from count
    _palette_exclude = {"success", "warning", "error", "text_primary", "text_secondary", "text_muted", "border"}
    chromatic = [v for k, v in c.items() if _is_chromatic(v) and k not in _palette_exclude]
    if len(chromatic) > 5:
        issues.append(f"{len(chromatic)} chromatic colors (max 5)")

    # Font limit
    fonts = theme.get("fonts", {})
    unique_fonts = set(v for v in fonts.values() if v)
    if len(unique_fonts) > 2:
        issues.append(f"{len(unique_fonts)} font families (max 2)")

    # Size hierarchy
    sizes = theme.get("sizes", {})
    title_px = _parse_px(sizes.get("title", 48))
    subtitle_px = _parse_px(sizes.get("subtitle", 28))
    body_px = _parse_px(sizes.get("body", 18))
    caption_px = _parse_px(sizes.get("caption", 13))

    if not (title_px > subtitle_px > body_px > caption_px):
        issues.append(f"Size hierarchy broken: title={title_px} subtitle={subtitle_px} body={body_px} caption={caption_px}")

    if body_px < 16:
        issues.append(f"Body text {body_px}px below 16px minimum")

    if caption_px < 11:
        issues.append(f"Caption text {caption_px}px below 11px minimum")

    # Margin
    margin = _parse_px(theme.get("spacing", {}).get("margin", 48))
    if margin < 48:
        warnings.append(f"Margin {margin}px below recommended 48px")

    return issues, warnings


# --- Commands ---

def cmd_list(args):
    themes = list_themes()
    active = get_active_theme_name()
    print("Available themes:")
    for name in themes:
        marker = " (active)" if name == active else ""
        theme = load_theme(name)
        desc = theme.get("description", "")
        print(f"  {name}{marker} — {desc}")


def cmd_show(args):
    theme = load_theme(args.name)
    print(json.dumps(theme, indent=2))


def cmd_create(args):
    """Create a new theme from the default template."""
    ensure_themes_dir()
    path = THEMES_DIR / f"{args.name}.json"
    if path.exists():
        print(f"Error: theme '{args.name}' already exists. Edit it directly at {path}")
        sys.exit(1)

    template = dict(BUILTIN_THEMES["midnight-purple"])
    template["name"] = args.name
    template["display_name"] = args.name.replace("-", " ").title()
    template["description"] = f"Custom theme: {args.name}"

    with open(path, "w") as f:
        json.dump(template, f, indent=2)
    print(f"Created theme at {path}")
    print("Edit the JSON file to customize colors, fonts, and sizes.")


def cmd_activate(args):
    # Verify theme exists
    load_theme(args.name)
    set_active_theme(args.name)
    print(f"Active theme set to '{args.name}'")


def cmd_active(args):
    name = get_active_theme_name()
    print(f"Active theme: {name}")


def cmd_css(args):
    theme = load_theme(args.name)
    print(theme_to_css(theme))


def cmd_validate(args):
    theme = load_theme(args.name)
    issues, warnings = validate_theme(theme)

    print(f"Validating theme '{args.name}'...")
    if not issues and not warnings:
        print("  PASS — all checks passed")
        return

    for issue in issues:
        print(f"  ERROR: {issue}")
    for warning in warnings:
        print(f"  WARN:  {warning}")

    if issues:
        print(f"\n  {len(issues)} error(s), {len(warnings)} warning(s)")
        sys.exit(1)
    else:
        print(f"\n  {len(warnings)} warning(s), no errors")


def main():
    parser = argparse.ArgumentParser(description="Manage wicked-pptx slide themes")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List available themes")

    show_p = sub.add_parser("show", help="Show theme details as JSON")
    show_p.add_argument("name", help="Theme name")

    create_p = sub.add_parser("create", help="Create a new theme from template")
    create_p.add_argument("name", help="Theme name (lowercase-hyphenated)")

    activate_p = sub.add_parser("activate", help="Set the active theme")
    activate_p.add_argument("name", help="Theme name")

    sub.add_parser("active", help="Show the currently active theme")

    css_p = sub.add_parser("css", help="Export theme as CSS variables")
    css_p.add_argument("name", help="Theme name")

    validate_p = sub.add_parser("validate", help="Validate theme against design principles")
    validate_p.add_argument("name", help="Theme name")

    args = parser.parse_args()

    commands = {
        "list": cmd_list,
        "show": cmd_show,
        "create": cmd_create,
        "activate": cmd_activate,
        "active": cmd_active,
        "css": cmd_css,
        "validate": cmd_validate,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

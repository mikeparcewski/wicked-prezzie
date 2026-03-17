#!/usr/bin/env python3
"""
Color utilities for CSS-to-PPTX conversion.

Handles parsing CSS color strings (rgb, rgba, hex), alpha blending against
dark backgrounds, and font weight detection.
"""

import re
import html as html_mod
from pptx.dml.color import RGBColor


def parse_css_color(s, bg_rgb=(10, 10, 15)):
    """
    Parse a CSS color string into a python-pptx RGBColor.

    Handles rgb(), rgba() with alpha blending, and hex colors.
    For rgba colors with alpha < 1.0, blends against bg_rgb to produce
    the actual rendered color (since PPTX doesn't support transparency
    on shape fills in the same way CSS does).

    Args:
        s: CSS color string (e.g. 'rgb(255,0,0)', 'rgba(161,0,255,0.06)', '#A100FF')
        bg_rgb: Background RGB tuple for alpha blending (default dark slide bg)

    Returns:
        RGBColor or None if transparent/invalid
    """
    if not s:
        return None
    s = s.strip()
    m = re.match(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', s)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        ma = re.search(r',\s*([\d.]+)\s*\)', s)
        if ma:
            a = float(ma.group(1))
            if a < 0.02:
                return None  # fully transparent
            if a < 0.95:
                # Alpha blend with background
                br, bg, bb = bg_rgb
                r = int(r * a + br * (1 - a))
                g = int(g * a + bg * (1 - a))
                b = int(b * a + bb * (1 - a))
        return RGBColor(min(255, r), min(255, g), min(255, b))
    m = re.match(r'#([0-9a-fA-F]{6})', s)
    if m:
        h = m.group(1)
        return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    return None


def is_bold(font_weight):
    """Check if a CSS font-weight value indicates bold."""
    if not font_weight:
        return False
    try:
        return int(font_weight) >= 600
    except ValueError:
        return font_weight in ('bold', 'bolder')


def decode_entities(s):
    """Decode HTML entities in text (e.g. &amp; → &, &lt; → <)."""
    if not s:
        return s
    return html_mod.unescape(s)

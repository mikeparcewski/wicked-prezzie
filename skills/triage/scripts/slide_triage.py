#!/usr/bin/env python3
"""
triage — Analyse a classified slide layout and emit findings JSON.

Reads element confidence from classify_elements() output, checks against
known-pattern signatures, detects collision risks, and returns a findings dict.

This is the mechanical (deterministic) part of triage. Model inspection of
flagged elements happens in prep.
"""

import sys, re
from pathlib import Path


# ---------------------------------------------------------------------------
# Emoji detection (mirrors pptx_builder + chrome_extract)
# ---------------------------------------------------------------------------

def _is_emoji(ch):
    cp = ord(ch)
    if cp >= 0x1F300: return True
    if 0x2600 <= cp <= 0x27BF: return True
    if 0x2500 <= cp <= 0x25FF: return True
    if 0x2B00 <= cp <= 0x2BFF: return True
    if 0xFE00 <= cp <= 0xFE0F: return True
    if cp == 0x200D: return True
    if cp == 0x2022: return True
    if 0x2000 <= cp <= 0x206F: return True
    if 0x2190 <= cp <= 0x21FF: return True
    if 0x2300 <= cp <= 0x23FF: return True
    if 0x2400 <= cp <= 0x24FF: return True
    if 0x2700 <= cp <= 0x27BF: return True
    if 0x2010 <= cp <= 0x2027: return True
    if 0x2030 <= cp <= 0x205E: return True
    if 0x2200 <= cp <= 0x22FF: return True
    if 0x2100 <= cp <= 0x214F: return True
    return False


def _all_emoji(text):
    """Return True if all non-whitespace characters are emoji/symbol."""
    stripped = [ch for ch in text if not ch.isspace()]
    return bool(stripped) and all(_is_emoji(ch) for ch in stripped)


# ---------------------------------------------------------------------------
# Containment test (PATTERN-004)
# ---------------------------------------------------------------------------

def _find_parent_card(text_rect, shape_elements, slide_w, slide_h):
    """Find the tightest shape that contains this text element."""
    best = None
    best_area = float('inf')
    for s in shape_elements:
        sr = s['rect']
        # Full-slide shapes are not cards
        if sr['w'] > 1250 and sr['h'] > 680:
            continue
        if sr['w'] * sr['h'] < 400:
            continue
        if (text_rect['x'] >= sr['x'] - 5 and
                text_rect['y'] >= sr['y'] - 5 and
                text_rect['x'] + text_rect['w'] <= sr['x'] + sr['w'] + 30 and
                text_rect['y'] + text_rect['h'] <= sr['y'] + sr['h'] + 10):
            area = sr['w'] * sr['h']
            if area < best_area and sr['w'] > 20 and sr['h'] > 20:
                best = s
                best_area = area
    return best


# ---------------------------------------------------------------------------
# Collision risk detection
# ---------------------------------------------------------------------------

def _detect_obstacle_risk(element, all_elements):
    """Return True if a small badge/emoji element horizontally overlaps this element."""
    rect = element['rect']
    ry1, ry2 = rect['y'], rect['y'] + rect['h']

    for other in all_elements:
        if other is element:
            continue
        et = other.get('type', '')
        or_ = other['rect']

        is_obstacle = False
        if et in ('badge', 'circle'):
            is_obstacle = True
        elif et == 'richtext':
            runs = other.get('runs', [])
            text = ''.join(r.get('text', '') for r in runs).strip()
            if or_['w'] < 60 and or_['h'] < 60 and _all_emoji(text):
                is_obstacle = True

        if not is_obstacle:
            continue

        oy1, oy2 = or_['y'], or_['y'] + or_['h']
        v_overlap = min(ry2, oy2) - max(ry1, oy1)
        min_h = min(rect['h'], or_['h'])
        if v_overlap < min_h * 0.3:
            continue

        rx1, rx2 = rect['x'], rect['x'] + rect['w']
        ox1, ox2 = or_['x'], or_['x'] + or_['w']
        h_overlap = min(rx2, ox2) - max(rx1, ox1)
        if h_overlap > 0:
            return True

    return False


# ---------------------------------------------------------------------------
# Pattern matching
# ---------------------------------------------------------------------------

def _check_patterns(element, raw_index, all_elements, svg_elements, slide_w, slide_h):
    """Return the first matching pattern ID, or None."""
    etype = element.get('type', '')
    rect = element['rect']
    styles = element.get('styles', {})
    tag = element.get('tag', '')
    runs = element.get('runs', [])

    # PATTERN-007: Full-slide background shape
    if etype == 'shape' and rect['w'] > 1250 and rect['h'] > 680:
        return 'PATTERN-007'

    # PATTERN-008: Tiny shape noise
    if etype == 'shape' and (rect['w'] * rect['h'] < 16 or
                              (rect['w'] < 2 and rect['h'] < 2)):
        return 'PATTERN-008'

    # PATTERN-009: Out-of-bounds element
    if (rect['x'] > slide_w or rect['y'] > slide_h or
            rect['x'] + rect['w'] < 0 or rect['y'] + rect['h'] < 0):
        return 'PATTERN-009'

    # PATTERN-002: Left-border accent bar (shape only)
    if etype == 'shape':
        blw = styles.get('borderLeftWidth', 0) or 0
        blc = styles.get('borderLeftColor', '')
        if blw > 2 and blc and blc not in ('rgba(0, 0, 0, 0)', 'transparent', ''):
            return 'PATTERN-002'

    # PATTERN-003: Rotated text
    rotation = element.get('rotation', 0) or 0
    wm = styles.get('writingMode', '')
    if abs(rotation) >= 5 or wm in ('vertical-rl', 'vertical-lr'):
        return 'PATTERN-003'

    # PATTERN-006: Small decorative emoji skip
    if etype == 'richtext' and rect['w'] < 80 and rect['h'] < 80:
        text = ''.join(r.get('text', '') for r in runs).strip()
        if _all_emoji(text):
            # Only emit as pattern-006 if there's a collision with adjacent richtext
            if _detect_obstacle_risk(element, all_elements):
                return 'PATTERN-006'

    # PATTERN-004: Card text width overflow (richtext inside a card shape)
    if etype == 'richtext' and tag not in ('h1',):
        shape_elements = [e for e in all_elements if e.get('type') == 'shape']
        parent = _find_parent_card(rect, shape_elements, slide_w, slide_h)
        if parent:
            return 'PATTERN-004'

    # PATTERN-010: Duplicate text from container + leaf
    if etype == 'richtext':
        text = ''.join(r.get('text', '') for r in runs).strip()
        depth = element.get('depth', 0)
        for other in all_elements:
            if other is element:
                continue
            if other.get('type') != 'richtext':
                continue
            other_depth = other.get('depth', 0)
            if other_depth <= depth:
                continue  # we want lower-depth (ancestor) to be flagged
            other_rect = other['rect']
            # Compute overlap
            ix1 = max(rect['x'], other_rect['x'])
            iy1 = max(rect['y'], other_rect['y'])
            ix2 = min(rect['x'] + rect['w'], other_rect['x'] + other_rect['w'])
            iy2 = min(rect['y'] + rect['h'], other_rect['y'] + other_rect['h'])
            if ix2 > ix1 and iy2 > iy1:
                overlap_area = (ix2 - ix1) * (iy2 - iy1)
                self_area = max(1, rect['w'] * rect['h'])
                if overlap_area / self_area > 0.8:
                    return 'PATTERN-010'

    return None


# ---------------------------------------------------------------------------
# Complexity inference
# ---------------------------------------------------------------------------

def _infer_complexity(classified_layout, html_path=None):
    """Infer slide complexity from layout data (or HTML annotation)."""
    # Check HTML annotation first
    if html_path:
        try:
            with open(html_path, encoding='utf-8', errors='ignore') as f:
                content = f.read(4096)
            m = re.search(r'<!--\s*COMPLEXITY:\s*(high|low)\s*-->', content, re.IGNORECASE)
            if m:
                return m.group(1).lower()
        except Exception:
            pass

    elements = classified_layout.get('elements', [])
    svg_elements = classified_layout.get('svgElements', [])

    if svg_elements:
        return 'high'
    for e in elements:
        rotation = e.get('rotation', 0) or 0
        if abs(rotation) >= 5:
            return 'high'
        wm = e.get('styles', {}).get('writingMode', '')
        if wm in ('vertical-rl', 'vertical-lr'):
            return 'high'

    flagged = sum(1 for e in elements if e.get('confidence', 1.0) < 0.85)
    if flagged > 3:
        return 'high'

    return 'low'


# ---------------------------------------------------------------------------
# Main triage function
# ---------------------------------------------------------------------------

def triage_slide(raw_layout, classified_layout, slide_index=0, source_file='',
                 slide_width_px=1280, slide_height_px=720, html_path=None):
    """
    Produce findings JSON from raw + classified extraction.

    Args:
        raw_layout: Output of extract_layout() (before classify_elements())
        classified_layout: Output of classify_elements() (with confidence fields)
        slide_index: 0-based slide index in the deck
        source_file: Original HTML filename (for audit trail)
        slide_width_px: Slide width in pixels (default 1280)
        slide_height_px: Slide height in pixels (default 720)
        html_path: Path to HTML file (used to read COMPLEXITY annotation)

    Returns:
        findings dict conforming to the findings JSON schema
    """
    elements = classified_layout.get('elements', []) if classified_layout else []
    svg_elements = classified_layout.get('svgElements', []) if classified_layout else []

    complexity = _infer_complexity(classified_layout or {}, html_path)

    # Build element findings
    element_findings = []
    matched_patterns = set()

    for raw_index, element in enumerate(elements):
        confidence = element.get('confidence', 0.85)
        flag_reason = element.get('flagReason')

        pattern = _check_patterns(element, raw_index, elements, svg_elements,
                                  slide_width_px, slide_height_px)
        if pattern:
            matched_patterns.add(pattern)

        collision_risk = None
        if element.get('type') == 'richtext':
            if _detect_obstacle_risk(element, elements):
                collision_risk = 'obstacle_risk'

        entry = {
            'rawIndex': raw_index,
            'manifestId': f'e-{raw_index:03d}',
            'tag': element.get('tag', ''),
            'rect': element.get('rect', {}),
            'defaultType': element.get('type', ''),
            'confidence': confidence,
            'flagReason': flag_reason,
            'patternMatched': pattern,
            'collisionRisk': collision_risk,
        }
        element_findings.append(entry)

    # Build SVG element findings
    non_svg_ys = [e['rect']['y'] for e in elements
                  if e.get('type') in ('richtext', 'shape', 'badge')]

    svg_findings = []
    for svg_index, svg in enumerate(svg_elements):
        sr = svg['rect']
        svg_bottom = sr['y'] + sr['h']
        nearest_below_y = None
        collision_risk = None

        for ey in sorted(non_svg_ys):
            if ey > svg_bottom * 0.5 + sr['y'] * 0.5 and ey <= svg_bottom + 30:
                nearest_below_y = ey
                break

        if nearest_below_y is not None:
            collision_risk = 'svg_bottom_near_content'
            matched_patterns.add('PATTERN-001')

        svg_findings.append({
            'svgIndex': svg_index,
            'manifestId': f'svg-{svg_index:03d}',
            'rect': sr,
            'lines': svg.get('lines', 0),
            'collisionRisk': collision_risk,
            'nearestBelowY': nearest_below_y,
        })

    flagged_count = sum(1 for e in element_findings if e['confidence'] < 0.85)
    auto_count = len(element_findings) - flagged_count

    return {
        'schemaVersion': 1,
        'slideIndex': slide_index,
        'sourceFile': source_file,
        'complexity': complexity,
        'elementCount': len(element_findings),
        'flaggedCount': flagged_count,
        'autoResolvedCount': auto_count,
        'patterns': sorted(matched_patterns),
        'elements': element_findings,
        'svgElements': svg_findings,
    }

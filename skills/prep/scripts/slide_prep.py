#!/usr/bin/env python3
"""
prep — Auto-resolve triage findings into a build manifest.

Consumes the findings JSON from slide_triage and a classified layout,
applies known-pattern geometry transforms for high-confidence elements,
and returns a partially- or fully-resolved build manifest.

Flagged elements (confidence < 0.85) are included as stubs with type=None,
waiting for model resolution via the SKILL.md guided process.
"""


# ---------------------------------------------------------------------------
# Geometry transform helpers
# ---------------------------------------------------------------------------

def _find_parent_card(text_rect, shape_elements):
    """Find the tightest shape element that contains this text rect."""
    best = None
    best_area = float('inf')
    for s in shape_elements:
        sr = s['rect']
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


def _apply_pattern_001(svg_entry, svg_finding):
    """PATTERN-001: SVG Crop Bleed — clamp SVG height to avoid bleeding."""
    nearest_y = svg_finding.get('nearestBelowY')
    if nearest_y is None:
        return svg_entry

    r = svg_entry['rect']
    new_h = nearest_y - r['y'] - 8
    if new_h > r['h'] * 0.5 and new_h < r['h']:
        svg_entry['resolvedRect'] = {
            'x': r['x'], 'y': r['y'], 'w': r['w'], 'h': new_h,
            'source': 'svg_bottom_clamp',
            'note': f'nearest element below at y={nearest_y}, cropped {r["h"] - new_h:.0f}px',
        }
        svg_entry['classificationSource'] = 'pattern'
        svg_entry['patternMatched'] = 'PATTERN-001'
    return svg_entry


def _apply_pattern_002(element, manifest_elements, next_id_counter):
    """PATTERN-002: Left-Border Accent Bar — emit shape + accent_bar pair."""
    styles = element.get('styles', {})
    blw = styles.get('borderLeftWidth', 0) or 0
    blc = styles.get('borderLeftColor', '')
    r = element['rect']

    # 1. Emit the card shape without left border
    card = dict(element)
    card_styles = dict(styles)
    card_styles['borderLeftWidth'] = 0
    card['styles'] = card_styles
    card['classificationSource'] = 'pattern'
    card['patternMatched'] = 'PATTERN-002'

    # 2. Emit the accent bar as a separate element
    bar_w = max(3, min(blw, 6))
    bar_id = element['manifestId'] + '-accent'
    accent = {
        'manifestId': bar_id,
        'type': 'accent_bar',
        'rect': {'x': r['x'], 'y': r['y'], 'w': bar_w, 'h': r['h']},
        'fill': blc,
        'styles': {'backgroundColor': blc},
        'depth': element.get('depth', 0) + 0.5,
        'confidence': 1.0,
        'flagReason': None,
        'classificationSource': 'pattern',
        'patternMatched': 'PATTERN-002',
        'skipRender': False,
    }
    return card, accent


def _apply_pattern_003(element):
    """PATTERN-003: Rotated Text — swap w/h for PPTX rotation."""
    r = element['rect']
    element['resolvedRect'] = {
        'x': r['x'], 'y': r['y'],
        'w': r['h'], 'h': r['w'],
        'source': 'rotation_swap',
        'note': f'w/h swapped for rotation={element.get("rotation", 0)}deg',
    }
    element['classificationSource'] = 'pattern'
    element['patternMatched'] = 'PATTERN-003'
    return element


def _apply_pattern_004(element, shape_elements):
    """PATTERN-004: Card Text Width Overflow — clamp text width to card."""
    r = element['rect']
    parent = _find_parent_card(r, shape_elements)
    if not parent:
        return element

    pr = parent['rect']
    card_left = pr['x'] + 4
    card_w = pr['w'] - 8
    parent_id = parent.get('manifestId', '')

    if r['x'] > card_left + 20:
        # Text is inset (e.g. past a badge) — preserve x, reduce width only
        new_x = r['x']
        new_w = min(card_w - (r['x'] - card_left), r['w'] * 1.03)
    else:
        new_x = card_left
        new_w = card_w

    # Hard ceiling: never exceed card width
    new_w = min(new_w, pr['w'])

    element['resolvedRect'] = {
        'x': new_x, 'y': r['y'], 'w': new_w, 'h': r['h'],
        'source': 'card_clamp',
        'note': f'clamped to parent card {parent_id} ({pr["w"]:.0f}px wide)',
    }
    element['classificationSource'] = 'pattern'
    element['patternMatched'] = 'PATTERN-004'
    return element


def _apply_pattern_005(element, all_elements):
    """PATTERN-005: Badge/Icon Obstacle Collision — shift text past obstacle."""
    rect = element['rect']
    align = element.get('styles', {}).get('textAlign', 'left')
    if align == 'center':
        return element  # do not dodge centered text

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
            if or_['w'] < 60 and or_['h'] < 60:
                stripped = [ch for ch in text if not ch.isspace()]
                if stripped and all(_is_emoji_ch(ch) for ch in stripped):
                    is_obstacle = True

        if not is_obstacle:
            continue

        oy1, oy2 = or_['y'], or_['y'] + or_['h']
        v_overlap = min(ry2, oy2) - max(ry1, oy1)
        if v_overlap < min(rect['h'], or_['h']) * 0.3:
            continue

        rx1, rx2 = rect['x'], rect['x'] + rect['w']
        ox1, ox2 = or_['x'], or_['x'] + or_['w']
        h_overlap = min(rx2, ox2) - max(rx1, ox1)
        if h_overlap <= 0:
            continue

        new_x = ox2 + 4
        new_w = rect['w'] - (new_x - rect['x'])
        if new_w < 20:
            return element  # result too narrow, skip

        obstacle_id = other.get('manifestId', '')
        element['resolvedRect'] = {
            'x': new_x, 'y': rect['y'], 'w': new_w, 'h': rect['h'],
            'source': 'obstacle_dodge',
            'note': f'shifted past obstacle {obstacle_id} at x={ox2:.0f}',
        }
        element['classificationSource'] = 'pattern'
        element['patternMatched'] = 'PATTERN-005'
        return element

    return element


def _is_emoji_ch(ch):
    cp = ord(ch)
    if cp >= 0x1F300: return True
    if 0x2600 <= cp <= 0x27BF: return True
    if 0x2500 <= cp <= 0x25FF: return True
    if 0x2B00 <= cp <= 0x2BFF: return True
    return False


# ---------------------------------------------------------------------------
# Skip-type pattern handlers (set type = "skip")
# ---------------------------------------------------------------------------

SKIP_PATTERNS = {'PATTERN-006', 'PATTERN-007', 'PATTERN-008',
                 'PATTERN-009', 'PATTERN-010'}


# ---------------------------------------------------------------------------
# Main auto_resolve function
# ---------------------------------------------------------------------------

def auto_resolve(findings, classified_layout):
    """
    Auto-resolve high-confidence elements into a partial build manifest.

    Elements with confidence >= 0.85 are fully resolved and assigned correct
    types and geometry. Flagged elements (confidence < 0.85 without a
    skip-type pattern) are included as stubs with type=None, awaiting model
    resolution.

    Args:
        findings: dict from triage_slide() — findings JSON
        classified_layout: dict from classify_elements() — typed elements

    Returns:
        Partial manifest dict. Elements with type=None require model resolution
        before being passed to build_slide_from_manifest().
    """
    elements_raw = classified_layout.get('elements', []) if classified_layout else []
    svg_elements_raw = classified_layout.get('svgElements', []) if classified_layout else []
    findings_elements = {fe['rawIndex']: fe for fe in findings.get('elements', [])}
    findings_svgs = {sv['svgIndex']: sv for sv in findings.get('svgElements', [])}

    slide_w = classified_layout.get('slideWidth', 1280) if classified_layout else 1280
    slide_h = classified_layout.get('slideHeight', 720) if classified_layout else 720

    # Assign manifestIds to raw elements
    for i, e in enumerate(elements_raw):
        e.setdefault('manifestId', f'e-{i:03d}')

    # Collect shape elements for PATTERN-004 lookup
    shape_elements = [e for e in elements_raw if e.get('type') == 'shape']

    manifest_elements = []
    id_counter = [len(elements_raw)]  # for accent bar IDs

    for raw_index, element in enumerate(elements_raw):
        fe = findings_elements.get(raw_index, {})
        pattern = fe.get('patternMatched')
        confidence = element.get('confidence', 0.85)
        element.setdefault('skipRender', False)
        element.setdefault('classificationSource', 'auto')

        # Skip-type patterns: set type to skip regardless of confidence
        if pattern in SKIP_PATTERNS:
            element['type'] = 'skip'
            element['skipRender'] = True
            element['classificationSource'] = 'pattern'
            element['patternMatched'] = pattern
            manifest_elements.append(element)
            continue

        # Flagged elements without a known pattern: leave as stub for model
        if confidence < 0.85 and not pattern:
            stub = dict(element)
            stub['type'] = None  # signal for model resolution
            stub['patternMatched'] = pattern
            manifest_elements.append(stub)
            continue

        # PATTERN-002: accent bar — emit two elements
        if pattern == 'PATTERN-002':
            card, accent = _apply_pattern_002(element, manifest_elements, id_counter)
            manifest_elements.append(card)
            manifest_elements.append(accent)
            continue

        # PATTERN-003: rotated text — swap w/h
        if pattern == 'PATTERN-003':
            element = _apply_pattern_003(element)
            manifest_elements.append(element)
            continue

        # PATTERN-004: card text clamp — resolve geometry
        if pattern == 'PATTERN-004':
            element = _apply_pattern_004(element, shape_elements)
            manifest_elements.append(element)
            continue

        # PATTERN-005 obstacle dodge is handled after all elements are added
        # (needs full element list). We tag it here and post-process.

        # Auto-resolve: high-confidence element, no special pattern
        element['patternMatched'] = pattern
        manifest_elements.append(element)

    # Post-process PATTERN-005: obstacle dodge (needs full element list)
    for element in manifest_elements:
        fe_entry = findings_elements.get(
            int(element.get('manifestId', 'e-000').replace('e-', '').split('-')[0] or 0), {})
        if fe_entry.get('collisionRisk') == 'obstacle_risk':
            if element.get('type') == 'richtext' and not element.get('resolvedRect'):
                element = _apply_pattern_005(element, manifest_elements)

    # Build SVG manifest entries
    manifest_svgs = []
    for svg_index, svg in enumerate(svg_elements_raw):
        svg.setdefault('manifestId', f'svg-{svg_index:03d}')
        svg['type'] = 'svg_image'
        svg.setdefault('skipRender', False)
        svg['confidence'] = 1.0
        svg['flagReason'] = None
        svg.setdefault('classificationSource', 'auto')

        sv_finding = findings_svgs.get(svg_index, {})
        if sv_finding.get('collisionRisk') == 'svg_bottom_near_content':
            svg = _apply_pattern_001(svg, sv_finding)

        manifest_svgs.append(svg)

    # Speaker notes from classified layout (passed through)
    notes = classified_layout.get('notes', '') if classified_layout else ''

    return {
        'schemaVersion': 1,
        'slideIndex': findings.get('slideIndex', 0),
        'sourceFile': findings.get('sourceFile', ''),
        'slideBg': (classified_layout or {}).get('slideBg', '#0A0A0F'),
        'slideWidthPx': slide_w,
        'slideHeightPx': slide_h,
        'complexity': findings.get('complexity', 'low'),
        'triageFlags': findings.get('patterns', []),
        'elements': manifest_elements,
        'svgElements': manifest_svgs,
        'notes': notes,
    }

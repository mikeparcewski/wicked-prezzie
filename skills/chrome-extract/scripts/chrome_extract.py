#!/usr/bin/env python3
"""
Chrome Layout Extraction — Extract computed positions from rendered HTML.

Uses Chrome headless to render HTML, then injects JavaScript to walk the DOM
and extract actual bounding boxes, colors, fonts, and inline formatting.

Returns structured JSON suitable for rebuilding the layout in any format.
"""

import os, re, json, subprocess, html as html_mod
from pathlib import Path

# Default Chrome path (macOS). Override via CHROME_PATH env var.
CHROME = os.environ.get("CHROME_PATH",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

# JavaScript injected into the page to extract raw layout data.
# Walks the DOM and collects every visible element with its computed properties.
# NO classification — the model decides what each element is.
JS_EXTRACT = r'''
(function() {
    var slide = document.querySelector('.slide') || document.body;
    var SLIDE_W = parseInt(slide.style.width) || slide.offsetWidth || 1280;
    var SLIDE_H = parseInt(slide.style.height) || slide.offsetHeight || 720;
    var slideRect = slide.getBoundingClientRect();
    var scaleX = SLIDE_W / slideRect.width;
    var scaleY = SLIDE_H / slideRect.height;

    function relRect(el) {
        var r = el.getBoundingClientRect();
        return {
            x: (r.left - slideRect.left) * scaleX,
            y: (r.top - slideRect.top) * scaleY,
            w: r.width * scaleX,
            h: r.height * scaleY
        };
    }

    function gs(el) {
        var cs = window.getComputedStyle(el);
        return {
            color: cs.color,
            backgroundColor: cs.backgroundColor,
            background: cs.background,
            backgroundImage: cs.backgroundImage,
            fontSize: parseFloat(cs.fontSize),
            fontWeight: cs.fontWeight,
            fontStyle: cs.fontStyle,
            textAlign: cs.textAlign,
            borderColor: cs.borderTopColor,
            borderWidth: parseFloat(cs.borderWidth),
            borderRadius: parseFloat(cs.borderRadius),
            opacity: parseFloat(cs.opacity),
            display: cs.display,
            letterSpacing: cs.letterSpacing,
            textTransform: cs.textTransform,
            borderLeftColor: cs.borderLeftColor,
            borderLeftWidth: parseFloat(cs.borderLeftWidth),
            paddingTop: parseFloat(cs.paddingTop),
            paddingRight: parseFloat(cs.paddingRight),
            paddingBottom: parseFloat(cs.paddingBottom),
            paddingLeft: parseFloat(cs.paddingLeft),
            whiteSpace: cs.whiteSpace,
            transform: cs.transform,
            writingMode: cs.writingMode
        };
    }

    function isVis(el) {
        var cs = window.getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden' || cs.opacity === '0') return false;
        var r = el.getBoundingClientRect();
        return r.width >= 1 && r.height >= 1;
    }

    function getRuns(el) {
        var runs = [];
        function walk(node) {
            if (node.nodeType === 3) {
                var raw = node.textContent;
                if (raw.length === 0) return;
                var parent = node.parentElement;
                var pcs = window.getComputedStyle(parent);
                var ws = pcs.whiteSpace || '';
                var t;
                if (ws === 'pre' || ws === 'pre-wrap' || ws === 'pre-line') {
                    t = raw;
                } else {
                    t = raw.replace(/[\s\n\t]+/g, ' ');
                    if (!/\S/.test(t)) return;
                }
                if (t.length === 0) return;
                if (runs.length > 0 && !runs[runs.length - 1].br) {
                    var prev = runs[runs.length - 1].text;
                    if (/\w$/.test(prev) && /^\w/.test(t)) {
                        runs[runs.length - 1].text += ' ';
                    }
                }
                runs.push({
                    text: t, color: pcs.color,
                    fontSize: parseFloat(pcs.fontSize), fontWeight: pcs.fontWeight,
                    fontStyle: pcs.fontStyle, textTransform: pcs.textTransform || ''
                });
            } else if (node.nodeType === 1) {
                var tn = node.tagName;
                if (tn === 'SCRIPT' || tn === 'STYLE' || tn === 'SVG' || tn === 'NAV') return;
                if (tn === 'BR') { runs.push({text: '\n', br: true}); return; }
                if (!isVis(node)) return;
                var disp = window.getComputedStyle(node).display;
                if (disp !== 'inline' && disp !== 'inline-block' && runs.length > 0 && !runs[runs.length - 1].br) {
                    runs.push({text: '\n', br: true});
                }
                for (var i = 0; i < node.childNodes.length; i++) walk(node.childNodes[i]);
            }
        }
        walk(el);
        return runs;
    }

    function getRotation(styles) {
        if (styles.writingMode === 'vertical-rl' || styles.writingMode === 'vertical-lr') return -90;
        var t = styles.transform;
        if (!t || t === 'none') return 0;
        var m = t.match(/matrix\(([^)]+)\)/);
        if (m) {
            var vals = m[1].split(',').map(Number);
            var angle = Math.round(Math.atan2(vals[1], vals[0]) * 180 / Math.PI);
            if (Math.abs(angle) >= 5) return angle;
        }
        return 0;
    }

    function capturePseudo(el, pseudo, depth) {
        var cs = window.getComputedStyle(el, pseudo);
        if (!cs.content || cs.content === 'none' || cs.content === 'normal') return null;
        var rawContent = cs.content.replace(/^["']|["']$/g, '');
        var pBg = cs.backgroundColor;
        var hasPseudoBg = pBg && pBg !== 'rgba(0, 0, 0, 0)' && pBg !== 'transparent';
        var hasPseudoBorder = (parseFloat(cs.borderWidth) || 0) > 0.5;
        if (!rawContent && !hasPseudoBg && !hasPseudoBorder) return null;
        var pseudoW = parseFloat(cs.width) || 0;
        var pseudoH = parseFloat(cs.height) || 0;
        pseudoW += (parseFloat(cs.borderLeftWidth) || 0) + (parseFloat(cs.borderRightWidth) || 0);
        pseudoH += (parseFloat(cs.borderTopWidth) || 0) + (parseFloat(cs.borderBottomWidth) || 0);
        if (pseudoW < 2 || pseudoH < 2) return null;
        var parentRect = el.getBoundingClientRect();
        var pseudoLeft = parseFloat(cs.left) || 0;
        var pseudoTop = parseFloat(cs.top) || 0;
        return {
            tag: '::pseudo', rect: {
                x: (parentRect.left - slideRect.left + pseudoLeft) * scaleX,
                y: (parentRect.top - slideRect.top + pseudoTop) * scaleY,
                w: pseudoW * scaleX, h: pseudoH * scaleY},
            styles: {backgroundColor: cs.backgroundColor, color: cs.color,
                fontSize: parseFloat(cs.fontSize), fontWeight: cs.fontWeight,
                borderRadius: parseFloat(cs.borderRadius)},
            text: rawContent, source: pseudo, depth: depth + 0.5
        };
    }

    // --- Collect SVGs separately (structural fact) ---
    var elements = [], svgs = [];
    slide.querySelectorAll('svg').forEach(function(svg) {
        if (!isVis(svg)) return;
        var rect = relRect(svg);
        if (rect.w < 20 || rect.h < 20) return;
        svgs.push({type: 'svg', rect: rect, lines: svg.outerHTML.split('\n').length});
    });

    // --- Walk every visible element, emit raw facts ---
    function walkEl(el, depth) {
        if (depth > 15) return;
        if (!isVis(el)) return;
        var tn = el.tagName;
        if (tn === 'SCRIPT' || tn === 'STYLE' || tn === 'NAV' || tn === 'SVG') return;
        if (el.closest && el.closest('svg')) return;

        var rect = relRect(el);
        if (rect.w < 1 || rect.h < 1) return;
        var styles = gs(el);
        var tag = tn.toLowerCase();
        var cls = el.className ? String(el.className).split(/\s+/) : [];

        // --- Tables: extract structured data (factual, not a judgment call) ---
        if (tag === 'table' && rect.w > 50 && rect.h > 20) {
            var tableData = {tag: 'table', rect: rect, rows: [], styles: styles, classes: cls, depth: depth};
            el.querySelectorAll(':scope > thead > tr, :scope > tbody > tr, :scope > tr').forEach(function(tr) {
                var row = [];
                tr.querySelectorAll(':scope > td, :scope > th').forEach(function(cell) {
                    row.push({
                        rect: relRect(cell), styles: gs(cell), runs: getRuns(cell),
                        text: cell.textContent.trim().substring(0, 300),
                        colspan: cell.colSpan || 1, rowspan: cell.rowSpan || 1,
                        tag: cell.tagName.toLowerCase()
                    });
                });
                tableData.rows.push(row);
            });
            elements.push(tableData);
            return;
        }

        // --- Raw node: every visible element gets emitted with its facts ---
        var node = {
            tag: tag, classes: cls, rect: rect, depth: depth,
            styles: styles, rotation: getRotation(styles)
        };

        // Background/border facts
        var bg = styles.backgroundColor;
        node.hasBg = (bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent')
            || ((styles.backgroundImage || '').indexOf('gradient') !== -1);
        node.hasBorder = styles.borderWidth > 0.5
            && styles.borderColor !== 'rgba(0, 0, 0, 0)';

        // Text facts: does this element have its OWN text (not just children's)?
        var directText = '';
        for (var i = 0; i < el.childNodes.length; i++) {
            var cn = el.childNodes[i];
            if (cn.nodeType === 3) directText += cn.textContent;
            else if (cn.nodeType === 1 && cn.tagName === 'BR') directText += '\n';
        }
        node.directText = directText.trim().substring(0, 300);
        node.childElementCount = el.children.length;

        // Full text runs (inline formatting) — extracted by the browser, classified by the model
        var fullText = el.textContent.trim();
        if (fullText.length > 0 && node.childElementCount === 0) {
            // True leaf: no child elements, all text is ours
            node.runs = getRuns(el).map(function(r) {
                return {text: r.text.substring(0, 500), color: r.color,
                    fontSize: r.fontSize, fontWeight: r.fontWeight,
                    fontStyle: r.fontStyle, textTransform: r.textTransform || '',
                    br: r.br || false};
            });
        }

        elements.push(node);

        // Pseudo-elements
        ['::before', '::after'].forEach(function(pseudo) {
            var pn = capturePseudo(el, pseudo, depth);
            if (pn) elements.push(pn);
        });

        // Recurse into children
        for (var i = 0; i < el.children.length; i++) {
            walkEl(el.children[i], depth + 1);
        }
    }

    walkEl(slide, 0);
    var ss = gs(slide);
    document.getElementById('__layout_output__').textContent = JSON.stringify({
        slideWidth: SLIDE_W, slideHeight: SLIDE_H,
        slideClasses: Array.from(slide.classList),
        slideBg: ss.backgroundColor,
        elements: elements, svgElements: svgs
    });
})();
'''


def extract_layout(html_path, tmpdir, viewport_w=1280, viewport_h=720, hide_selectors=None):
    """
    Extract computed layout from an HTML file using Chrome headless.

    Args:
        html_path: Path to HTML file
        tmpdir: Temporary directory for intermediate files
        viewport_w: Browser viewport width (default 1280)
        viewport_h: Browser viewport height (default 720)
        hide_selectors: CSS selectors to hide before extraction (e.g. ['.nav', '.footer'])

    Returns:
        dict with {slideWidth, slideHeight, slideClasses, slideBg, elements, svgElements}
        or None on failure
    """
    with open(html_path) as f:
        html = f.read()

    # Physically remove hidden elements from DOM before Chrome sees them (#29 bug 5)
    # This is more reliable than CSS injection which can fail due to specificity conflicts
    if hide_selectors:
        from bs4 import BeautifulSoup as _BS
        _soup = _BS(html, 'html.parser')
        for sel in hide_selectors:
            for el in _soup.select(sel):
                el.decompose()
        html = str(_soup)

    # Inject CSS for standalone cleanup
    html = html.replace('</head>',
        '<style>'
        'body.standalone .slide{box-shadow:none!important;border:none!important;border-radius:0!important;}'
        '.slide{margin:0!important;}</style></head>')

    # Inject extraction script
    html = html.replace('</body>',
        '<pre id="__layout_output__" style="position:fixed;top:0;left:0;z-index:99999;display:none;"></pre>'
        f'<script>window.addEventListener("load", function(){{ setTimeout(function(){{ {JS_EXTRACT} }}, 500); }});</script></body>')

    tmp = os.path.join(tmpdir, f"extract_{os.path.basename(str(html_path))}")
    with open(tmp, 'w') as f:
        f.write(html)

    result = subprocess.run([
        CHROME, "--headless", "--disable-gpu", "--no-sandbox",
        "--disable-software-rasterizer", "--hide-scrollbars",
        f"--window-size={viewport_w},{viewport_h}",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=5000", "--dump-dom",
        f"file://{tmp}"
    ], capture_output=True, timeout=30, text=True)

    m = re.search(r'<pre id="__layout_output__"[^>]*>(.*?)</pre>', result.stdout, re.DOTALL)
    if m and m.group(1):
        raw = html_mod.unescape(m.group(1))
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None
    return None


def classify_elements(raw_data):
    """Apply default classification to raw extracted elements.

    Converts raw nodes into the typed format the builder expects.
    This is the deterministic default — the model can override any decision
    by looking at the screenshot and editing the classified output.

    Returns a new dict with the same structure but typed elements.
    """
    if not raw_data:
        return raw_data

    classified = []
    sw = raw_data.get('slideWidth', 1280)
    sh = raw_data.get('slideHeight', 720)

    for node in raw_data.get('elements', []):
        tag = node.get('tag', '')
        r = node.get('rect', {})
        styles = node.get('styles', {})
        cls = node.get('classes', [])
        depth = node.get('depth', 0)

        # Tables pass through as-is (already structured)
        if tag == 'table':
            node['type'] = 'table'
            classified.append(node)
            continue

        # Pseudo-elements pass through as shapes
        if tag == '::pseudo':
            node['type'] = 'shape'
            classified.append(node)
            continue

        has_bg = node.get('hasBg', False)
        has_border = node.get('hasBorder', False)
        runs = node.get('runs')
        direct_text = node.get('directText', '')
        child_count = node.get('childElementCount', 0)

        # Elements with runs (true leaves with text) → richtext
        if runs and len(runs) > 0:
            classified.append({
                'type': 'richtext', 'tag': tag, 'classes': cls, 'rect': r,
                'runs': runs,
                'styles': {
                    'textAlign': styles.get('textAlign', 'left'),
                    'letterSpacing': styles.get('letterSpacing'),
                    'whiteSpace': styles.get('whiteSpace'),
                    'paddingTop': styles.get('paddingTop', 0),
                    'paddingRight': styles.get('paddingRight', 0),
                    'paddingBottom': styles.get('paddingBottom', 0),
                    'paddingLeft': styles.get('paddingLeft', 0),
                },
                'rotation': node.get('rotation', 0),
                'depth': depth,
            })
            # Also emit shape if it has a visible background
            if has_bg and tag not in ('body', 'html') and r.get('w', 0) > 8 and r.get('h', 0) > 4:
                classified.append({
                    'type': 'shape', 'tag': tag, 'classes': cls, 'rect': r,
                    'styles': {
                        'backgroundColor': styles.get('backgroundColor'),
                        'borderColor': styles.get('borderColor'),
                        'borderWidth': styles.get('borderWidth', 0),
                        'borderRadius': styles.get('borderRadius', 0),
                        'opacity': styles.get('opacity', 1),
                        'borderLeftColor': styles.get('borderLeftColor'),
                        'borderLeftWidth': styles.get('borderLeftWidth', 0),
                        'background': styles.get('background'),
                    },
                    'depth': depth,
                })
            continue

        # Elements with background/border but no text → shape
        if (has_bg or has_border) and tag not in ('body', 'html') and r.get('w', 0) > 8 and r.get('h', 0) > 4:
            classified.append({
                'type': 'shape', 'tag': tag, 'classes': cls, 'rect': r,
                'styles': {
                    'backgroundColor': styles.get('backgroundColor'),
                    'borderColor': styles.get('borderColor'),
                    'borderWidth': styles.get('borderWidth', 0),
                    'borderRadius': styles.get('borderRadius', 0),
                    'opacity': styles.get('opacity', 1),
                    'borderLeftColor': styles.get('borderLeftColor'),
                    'borderLeftWidth': styles.get('borderLeftWidth', 0),
                    'background': styles.get('background'),
                },
                'depth': depth,
            })

        # Container divs with children and no direct text → skip (children handle it)
        # Container divs with bg → shape already emitted above

    result = dict(raw_data)
    result['elements'] = classified
    return result


def screenshot_html(html_path, png_path, tmpdir, viewport_w=1280, viewport_h=720,
                    scale_factor=2, hide_selectors=None):
    """
    Screenshot an HTML file using Chrome headless.

    Args:
        html_path: Path to HTML file
        png_path: Output PNG path
        tmpdir: Temporary directory
        viewport_w/h: Browser viewport size
        scale_factor: Device scale factor (2 for retina)
        hide_selectors: CSS selectors to hide

    Returns:
        True if screenshot created successfully
    """
    from PIL import Image

    with open(html_path) as f:
        html = f.read()

    hide_css = ''
    if hide_selectors:
        hide_css = ''.join(f'{sel}{{display:none!important}}' for sel in hide_selectors)
    html = html.replace('</head>',
        f'<style>{hide_css}'
        'body.standalone .slide{box-shadow:none!important;border:none!important;border-radius:0!important;}'
        '.slide{margin:0!important;}</style></head>')

    tmp = os.path.join(tmpdir, f"ss_{os.path.basename(str(html_path))}")
    with open(tmp, 'w') as f:
        f.write(html)

    subprocess.run([
        CHROME, "--headless", "--disable-gpu", "--no-sandbox",
        "--disable-software-rasterizer", "--hide-scrollbars",
        f"--screenshot={png_path}", f"--window-size={viewport_w},{viewport_h}",
        f"--force-device-scale-factor={scale_factor}",
        f"file://{tmp}"
    ], capture_output=True, timeout=30)

    if os.path.exists(png_path):
        # Crop to target aspect ratio
        img = Image.open(png_path)
        w, h = img.size
        tr = viewport_w / viewport_h
        cr = w / h
        if abs(cr - tr) > 0.01:
            if cr > tr:
                nw = int(h * tr); left = (w - nw) // 2
                img = img.crop((left, 0, left + nw, h))
            else:
                nh = int(w / tr); top = (h - nh) // 2
                img = img.crop((0, top, w, top + nh))
            img.save(png_path)
        return True
    return False


def screenshot_svg_isolated(html_path, svg_index, png_path, tmpdir,
                            viewport_w=1280, viewport_h=720, scale_factor=2):
    """Screenshot a single SVG element in isolation — hides all other content.

    This eliminates SVG crop bleed (#19) by rendering only the target SVG
    against the slide background, with no other elements visible.

    Args:
        html_path: Path to HTML file
        svg_index: 0-based index of the SVG element (matches svgElements order)
        png_path: Output PNG path
        tmpdir: Temporary directory
        viewport_w/h: Browser viewport size
        scale_factor: Device scale factor

    Returns:
        True if screenshot created successfully
    """
    from PIL import Image

    with open(html_path) as f:
        html = f.read()

    # Inject CSS that hides everything except the slide background and the target SVG.
    # Also inject JS that marks the target SVG so CSS can select it.
    isolation_js = f'''
    <script>
    window.addEventListener("load", function() {{
        var svgs = document.querySelectorAll('.slide svg');
        if (svgs[{svg_index}]) {{
            svgs[{svg_index}].setAttribute('data-isolated', 'true');
        }}
    }});
    </script>
    '''
    isolation_css = '''
    <style>
    .slide > *:not(svg) { visibility: hidden !important; }
    .slide * { visibility: hidden !important; }
    .slide svg { visibility: hidden !important; }
    .slide svg[data-isolated="true"],
    .slide svg[data-isolated="true"] * { visibility: visible !important; }
    .slide { visibility: visible !important; }
    body.standalone .slide{box-shadow:none!important;border:none!important;border-radius:0!important;}
    .slide{margin:0!important;}
    </style>
    '''

    html = html.replace('</head>', isolation_css + isolation_js + '</head>')

    tmp = os.path.join(tmpdir, f"svgiso_{svg_index}_{os.path.basename(str(html_path))}")
    with open(tmp, 'w') as f:
        f.write(html)

    subprocess.run([
        CHROME, "--headless", "--disable-gpu", "--no-sandbox",
        "--disable-software-rasterizer", "--hide-scrollbars",
        f"--screenshot={png_path}", f"--window-size={viewport_w},{viewport_h}",
        f"--force-device-scale-factor={scale_factor}",
        "--virtual-time-budget=3000",
        f"file://{tmp}"
    ], capture_output=True, timeout=30)

    if os.path.exists(png_path):
        img = Image.open(png_path)
        w, h = img.size
        tr = viewport_w / viewport_h
        cr = w / h
        if abs(cr - tr) > 0.01:
            if cr > tr:
                nw = int(h * tr); left = (w - nw) // 2
                img = img.crop((left, 0, left + nw, h))
            else:
                nh = int(w / tr); top = (h - nh) // 2
                img = img.crop((0, top, w, top + nh))
            img.save(png_path)
        return True
    return False


def crop_region(full_png_path, out_path, region_rect, source_w=1280, source_h=720):
    """
    Crop a region from a full-page screenshot.

    Args:
        full_png_path: Path to full screenshot
        out_path: Output path for cropped image
        region_rect: dict with {x, y, w, h} in source coordinate space
        source_w/h: Source coordinate dimensions (default 1280x720)

    Returns:
        True if crop successful
    """
    from PIL import Image

    if not os.path.exists(full_png_path):
        return False
    img = Image.open(full_png_path)
    iw, ih = img.size
    sx, sy = iw / source_w, ih / source_h
    left = max(0, int(region_rect['x'] * sx))
    top = max(0, int(region_rect['y'] * sy))
    right = min(iw, int((region_rect['x'] + region_rect['w']) * sx))
    bottom = min(ih, int((region_rect['y'] + region_rect['h']) * sy))
    if right <= left or bottom <= top:
        return False
    img.crop((left, top, right, bottom)).save(out_path)
    return True

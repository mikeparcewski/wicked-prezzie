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

# JavaScript injected into the page to extract layout data.
# Walks the DOM, collects shapes (background/border elements) and text
# (with inline run formatting for headings/paragraphs).
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
            fontSize: parseFloat(cs.fontSize),
            fontWeight: cs.fontWeight,
            fontStyle: cs.fontStyle,
            textAlign: cs.textAlign,
            borderColor: cs.borderColor,
            borderWidth: parseFloat(cs.borderWidth),
            borderRadius: parseFloat(cs.borderRadius),
            opacity: parseFloat(cs.opacity),
            display: cs.display,
            letterSpacing: cs.letterSpacing,
            textTransform: cs.textTransform,
            borderLeftColor: cs.borderLeftColor,
            borderLeftWidth: parseFloat(cs.borderLeftWidth)
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
                var t = node.textContent;
                if (t.length === 0) return;
                var parent = node.parentElement;
                var pcs = window.getComputedStyle(parent);
                runs.push({
                    text: t,
                    color: pcs.color,
                    fontSize: parseFloat(pcs.fontSize),
                    fontWeight: pcs.fontWeight,
                    fontStyle: pcs.fontStyle,
                    textTransform: pcs.textTransform || ''
                });
            } else if (node.nodeType === 1) {
                var tn = node.tagName;
                if (tn === 'SCRIPT' || tn === 'STYLE' || tn === 'SVG' || tn === 'NAV') return;
                if (tn === 'BR') { runs.push({text: '\n', br: true}); return; }
                if (!isVis(node)) return;
                for (var i = 0; i < node.childNodes.length; i++) walk(node.childNodes[i]);
            }
        }
        walk(el);
        return runs;
    }

    var elements = [], svgs = [];
    slide.querySelectorAll('svg').forEach(function(svg) {
        if (!isVis(svg)) return;
        var rect = relRect(svg);
        if (rect.w < 20 || rect.h < 20) return;
        svgs.push({type: 'svg', rect: rect, lines: svg.outerHTML.split('\n').length});
    });

    var richTextEls = new Set();
    var richTags = {h1:1, h2:1, h3:1, h4:1, p:1, li:1};
    var leafTags = {span:1, a:1, strong:1, b:1, em:1, i:1, label:1, td:1, th:1, div:1};

    function walkEl(el, depth) {
        if (depth > 15) return;
        if (!isVis(el)) return;
        var tn = el.tagName;
        if (tn === 'SCRIPT' || tn === 'STYLE' || tn === 'NAV' || tn === 'SVG') return;
        if (el.closest && el.closest('svg')) return;
        var rect = relRect(el);
        var styles = gs(el);
        var tag = tn.toLowerCase();
        var cls = el.className ? String(el.className).split(/\s+/) : [];
        var hasBg = styles.backgroundColor !== 'rgba(0, 0, 0, 0)' && styles.backgroundColor !== 'transparent';
        var hasBorder = styles.borderWidth > 0.5 && styles.borderColor !== 'rgba(0, 0, 0, 0)';

        if (richTags[tag] && rect.w > 5 && rect.h > 3) {
            var fullText = el.textContent.trim();
            if (fullText.length > 0) {
                var runs = getRuns(el);
                if (runs.length > 0) {
                    elements.push({
                        type: 'richtext', tag: tag, classes: cls, rect: rect,
                        runs: runs.map(function(r) {
                            return {
                                text: r.text.substring(0, 500), color: r.color,
                                fontSize: r.fontSize, fontWeight: r.fontWeight,
                                fontStyle: r.fontStyle, textTransform: r.textTransform || '',
                                br: r.br || false
                            };
                        }),
                        styles: {textAlign: styles.textAlign, letterSpacing: styles.letterSpacing},
                        depth: depth
                    });
                    richTextEls.add(el);
                    el.querySelectorAll('*').forEach(function(c) { richTextEls.add(c); });
                }
            }
        } else if (leafTags[tag] && rect.w > 3 && rect.h > 3 && !richTextEls.has(el)) {
            var dtext = '';
            for (var i = 0; i < el.childNodes.length; i++) {
                if (el.childNodes[i].nodeType === 3) dtext += el.childNodes[i].textContent;
            }
            dtext = dtext.trim();
            if (dtext.length > 0) {
                elements.push({
                    type: 'text', tag: tag, classes: cls, text: dtext.substring(0, 300), rect: rect,
                    styles: {
                        color: styles.color, fontSize: styles.fontSize,
                        fontWeight: styles.fontWeight, fontStyle: styles.fontStyle,
                        textAlign: styles.textAlign, letterSpacing: styles.letterSpacing,
                        textTransform: styles.textTransform
                    },
                    depth: depth
                });
            }
        }

        if ((hasBg || hasBorder) && tag !== 'body' && tag !== 'html' && rect.w > 8 && rect.h > 4) {
            elements.push({
                type: 'shape', tag: tag, classes: cls, rect: rect,
                styles: {
                    backgroundColor: styles.backgroundColor, borderColor: styles.borderColor,
                    borderWidth: styles.borderWidth, borderRadius: styles.borderRadius,
                    opacity: styles.opacity, borderLeftColor: styles.borderLeftColor,
                    borderLeftWidth: styles.borderLeftWidth
                },
                depth: depth
            });
        }

        for (var i = 0; i < el.children.length; i++) walkEl(el.children[i], depth + 1);
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

    # Inject CSS to hide elements and remove standalone artifacts
    hide_css = ''
    if hide_selectors:
        hide_css = ''.join(f'{sel}{{display:none!important}}' for sel in hide_selectors)
    html = html.replace('</head>',
        f'<style>{hide_css}'
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

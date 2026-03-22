#!/usr/bin/env python3
"""Standardize HTML slide files for reliable Chrome headless extraction.

Normalizes document structure, viewport, slide wrapper, strips animations
and external resources to produce self-contained, predictable HTML.
"""

import argparse
import os
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Tag

# CSS properties related to animations and transitions
ANIMATION_PROPERTIES = re.compile(
    r'\b('
    r'animation|animation-name|animation-duration|animation-delay|'
    r'animation-fill-mode|animation-timing-function|animation-iteration-count|'
    r'animation-direction|animation-play-state|'
    r'transition|transition-property|transition-duration|'
    r'transition-delay|transition-timing-function'
    r')\s*:[^;]*;?',
    re.IGNORECASE,
)

# @keyframes blocks in <style> tags (handles nested braces)
KEYFRAMES_RE = re.compile(
    r'@keyframes\s+[\w-]+\s*\{(?:[^{}]*\{[^}]*\})*[^}]*\}',
    re.IGNORECASE | re.DOTALL,
)

# External CDN hostnames to strip
EXTERNAL_HOSTS = (
    'fonts.googleapis.com',
    'fonts.gstatic.com',
    'cdnjs.cloudflare.com',
    'unpkg.com',
    'cdn.jsdelivr.net',
)


def detect_source(soup):
    """Detect the likely source of the HTML slide.

    Returns a dict with:
        source: 'chatgpt' | 'claude' | 'gemini' | 'wicked-prezzie' | 'reveal' | 'unknown'
        confidence: 'high' | 'medium' | 'low'
        signals: list of matched fingerprints
        notes_format: 'speaker-notes-div' | 'data-notes' | 'notes-data-js' | 'none'
    """
    raw = str(soup).lower()
    signals = []
    source = 'unknown'
    confidence = 'low'

    # --- Fingerprint: wicked-prezzie (our own output) ---
    if soup.find(class_='speaker-notes') and 'speaker notes (press n' in raw:
        signals.append('speaker-notes-toggle')
        source = 'wicked-prezzie'
        confidence = 'high'
    elif '--vertical-align' in raw or '--content-justify' in raw:
        signals.append('wicked-prezzie-css-vars')
        source = 'wicked-prezzie'
        confidence = 'high'

    # --- Fingerprint: ChatGPT ---
    # ChatGPT slides often use: Segoe UI font, specific gradient patterns,
    # inline styles with very specific color values, no .slide wrapper
    if source == 'unknown':
        if 'segoe ui' in raw and ('linear-gradient' in raw or 'radial-gradient' in raw):
            signals.append('segoe-ui+gradient')
            source = 'chatgpt'
            confidence = 'medium'
        elif 'font-family: arial' in raw and not soup.find(class_='slide'):
            signals.append('arial+no-slide-wrapper')
            source = 'chatgpt'
            confidence = 'low'

    # --- Fingerprint: Claude ---
    # Claude artifacts use: specific class patterns, Tailwind-style utilities
    if source == 'unknown':
        if 'bg-gradient-to' in raw or ('tailwind' in raw):
            signals.append('tailwind-classes')
            source = 'claude'
            confidence = 'medium'
        elif re.search(r'class="[^"]*(?:flex|grid|rounded|shadow)[^"]*"', raw):
            # Tailwind utility patterns without explicit tailwind mention
            utility_count = len(re.findall(
                r'(?:flex|grid|rounded-|shadow-|bg-|text-|p-\d|m-\d|gap-)', raw))
            if utility_count >= 8:
                signals.append(f'tailwind-utilities({utility_count})')
                source = 'claude'
                confidence = 'low'

    # --- Fingerprint: Gemini ---
    # Gemini slides: Material Design patterns, specific font choices
    if source == 'unknown':
        if 'roboto' in raw and ('material' in raw or '#1a73e8' in raw):
            signals.append('roboto+material')
            source = 'gemini'
            confidence = 'medium'
        elif 'google sans' in raw:
            signals.append('google-sans')
            source = 'gemini'
            confidence = 'medium'

    # --- Fingerprint: Reveal.js ---
    if source == 'unknown':
        if 'reveal' in raw and ('class="slides"' in raw or 'class="reveal"' in raw):
            signals.append('reveal-js')
            source = 'reveal'
            confidence = 'high'

    # --- Detect notes format ---
    notes_format = 'none'
    if soup.find(class_='speaker-notes'):
        notes_format = 'speaker-notes-div'
    elif soup.find(attrs={'data-notes': True}):
        notes_format = 'data-notes'
    else:
        for script in soup.find_all('script'):
            src = script.get('src', '')
            if 'notes-data' in src:
                notes_format = 'notes-data-js'
                break
            if script.string and 'SLIDE_NOTES' in (script.string or ''):
                notes_format = 'notes-data-js'
                break

    return {
        'source': source,
        'confidence': confidence,
        'signals': signals,
        'notes_format': notes_format,
    }


def annotate_source(soup, detection):
    """Insert a <!-- SOURCE: ... --> comment as the first child of <body>."""
    body = soup.find('body')
    if not body:
        return
    from bs4 import Comment
    comment = Comment(
        f' SOURCE: {detection["source"]} '
        f'(confidence={detection["confidence"]}, '
        f'notes={detection["notes_format"]}, '
        f'signals={",".join(detection["signals"]) or "none"}) '
    )
    body.insert(0, comment)


def normalize_structure(soup):
    """Ensure <html><head><body> structure. Remove duplicate bodies.
    Ensure charset meta tag exists."""
    # Ensure <html>
    html_tag = soup.find('html')
    if not html_tag:
        html_tag = soup.new_tag('html')
        for child in list(soup.children):
            if isinstance(child, Tag) and child.name not in ('html',):
                html_tag.append(child.extract())
            elif not isinstance(child, Tag):
                html_tag.append(child.extract())
        soup.append(html_tag)

    # Ensure <head>
    head_tag = html_tag.find('head', recursive=False)
    if not head_tag:
        head_tag = soup.new_tag('head')
        html_tag.insert(0, head_tag)

    # Ensure <body>
    body_tag = html_tag.find('body', recursive=False)
    if not body_tag:
        body_tag = soup.new_tag('body')
        # Move non-head children of html into body
        for child in list(html_tag.children):
            if isinstance(child, Tag) and child.name in ('head',):
                continue
            body_tag.append(child.extract())
        html_tag.append(body_tag)

    # Remove duplicate <body> tags
    bodies = html_tag.find_all('body', recursive=False)
    if len(bodies) > 1:
        primary = bodies[0]
        for dup in bodies[1:]:
            # Move children of duplicate into primary
            for child in list(dup.children):
                primary.append(child.extract())
            dup.decompose()

    # Ensure charset meta
    charset_meta = head_tag.find('meta', attrs={'charset': True})
    if not charset_meta:
        charset_meta = head_tag.find('meta', attrs={'content': re.compile(r'charset', re.I)})
    if not charset_meta:
        meta = soup.new_tag('meta', charset='utf-8')
        head_tag.insert(0, meta)


def normalize_viewport(soup, w, h):
    """Set or create <meta name="viewport" content="width={w}">. Also ensure
    the slide element has explicit width/height style."""
    head_tag = soup.find('head')
    if not head_tag:
        return

    viewport_meta = head_tag.find('meta', attrs={'name': 'viewport'})
    if viewport_meta:
        viewport_meta['content'] = f'width={w}'
    else:
        meta = soup.new_tag('meta', attrs={'name': 'viewport', 'content': f'width={w}'})
        head_tag.append(meta)

    # Ensure slide element has explicit dimensions
    slide_el = soup.find(class_='slide')
    if slide_el:
        existing_style = slide_el.get('style', '')
        # Update or add width
        if 'width' not in existing_style:
            existing_style += f'; width: {w}px'
        if 'height' not in existing_style:
            existing_style += f'; height: {h}px'
        slide_el['style'] = existing_style.strip('; ').strip()


def ensure_slide_wrapper(soup, w=1280, h=720):
    """Ensure a .slide wrapper element exists. If no element with class 'slide' found,
    wrap body content in <div class="slide" style="width:{w}px;height:{h}px">."""
    slide_el = soup.find(class_='slide')
    if slide_el:
        return

    body = soup.find('body')
    if not body:
        return

    wrapper = soup.new_tag(
        'div',
        attrs={
            'class': 'slide',
            'style': (
                f'width: {w}px; height: {h}px; '
                f'position: relative; overflow: hidden;'
            ),
        },
    )

    children = list(body.children)
    for child in children:
        wrapper.append(child.extract())
    body.append(wrapper)


def strip_animations(soup):
    """Remove CSS animation/transition properties from all style attributes.
    Remove @keyframes rules from <style> tags. Remove transition/animation
    CSS properties."""
    # Strip from inline style attributes
    for tag in soup.find_all(attrs={'style': True}):
        original = tag['style']
        cleaned = ANIMATION_PROPERTIES.sub('', original)
        # Collapse double semicolons and clean up
        cleaned = re.sub(r';\s*;', ';', cleaned)
        cleaned = re.sub(r'^\s*;\s*', '', cleaned)
        cleaned = re.sub(r'\s*;\s*$', '', cleaned)
        cleaned = cleaned.strip()
        if cleaned:
            tag['style'] = cleaned
        else:
            del tag['style']

    # Strip @keyframes and animation/transition properties from <style> tags
    for style_tag in soup.find_all('style'):
        if not style_tag.string:
            continue
        css = style_tag.string
        # Remove @keyframes blocks
        css = KEYFRAMES_RE.sub('', css)
        # Remove animation/transition property lines from rule blocks
        css = ANIMATION_PROPERTIES.sub('', css)
        # Collapse whitespace artifacts
        css = re.sub(r'\n\s*\n', '\n', css)
        style_tag.string = css


def strip_external_resources(soup):
    """Remove <link> tags pointing to external CDNs (fonts.googleapis.com, cdnjs, etc).
    Remove <script src="http..."> external scripts. Keep inline scripts/styles."""
    # Remove external <link> tags
    for link in soup.find_all('link'):
        href = link.get('href', '')
        if _is_external_url(href):
            link.decompose()

    # Remove external <script> tags (those with external src)
    for script in soup.find_all('script'):
        src = script.get('src', '')
        if src and _is_external_url(src):
            script.decompose()


def _is_external_url(url):
    """Check if a URL is external (absolute http/https or known CDN host)."""
    if not url:
        return False
    url_lower = url.lower().strip()
    if url_lower.startswith('http://') or url_lower.startswith('https://'):
        for host in EXTERNAL_HOSTS:
            if host in url_lower:
                return True
        # Any absolute URL with a different host is external
        if url_lower.startswith('http://') or url_lower.startswith('https://'):
            return True
    if url_lower.startswith('//'):
        return True
    return False


def strip_navigation(soup):
    """Remove navigation elements that shouldn't appear in the PPTX (#35).

    Strips <nav> tags and elements with slide-nav/slide-number classes.
    Must run before extraction AND screenshots to prevent nav content
    from appearing in SVG fallback images.
    """
    # Remove all <nav> elements
    for nav in soup.find_all('nav'):
        nav.decompose()
    # Remove slide navigation and slide number elements by class
    for sel in ['.slide-nav', '.slide-number']:
        for el in soup.select(sel):
            el.decompose()


COMPLEXITY_SIGNALS = re.compile(
    r'(linear-gradient|radial-gradient|writing-mode\s*:\s*vertical|'
    r'transform\s*:\s*rotate|::before|::after|clip-path|mask-image)',
    re.IGNORECASE,
)


def normalize_speaker_notes(soup):
    """Convert legacy note formats to .speaker-notes hidden div.

    Handles:
    - data-notes attribute on .slide → .speaker-notes div
    - notes-data.js script references → removed (notes must be inline)
    - Existing .speaker-notes inside .slide → moved outside as sibling
    - Adds N-key toggle script if notes exist and script is missing
    """
    body = soup.find('body')
    if not body:
        return

    slide_el = soup.find(class_='slide')
    notes_div = soup.find(class_='speaker-notes')
    notes_text = None

    # Source 1: data-notes attribute on .slide
    if slide_el and slide_el.get('data-notes'):
        notes_text = slide_el['data-notes']
        del slide_el['data-notes']

    # Source 2: existing .speaker-notes div (may be inside .slide — needs to move)
    if notes_div:
        # If inside .slide, extract it
        if slide_el and notes_div in slide_el.descendants:
            notes_div.extract()
            body.append(notes_div)
        # Ensure it has display:none
        existing_style = notes_div.get('style', '')
        if 'display' not in existing_style:
            notes_div['style'] = 'display:none'
    elif notes_text:
        # Create .speaker-notes div from data-notes
        notes_div = soup.new_tag('div', attrs={
            'class': 'speaker-notes',
            'style': 'display:none',
        })
        notes_div.string = notes_text
        body.append(notes_div)

    # Remove notes-data.js and nav.js script references
    for script in soup.find_all('script'):
        src = script.get('src', '')
        if src and ('notes-data' in src or 'nav.js' in src):
            script.decompose()

    # Add N-key toggle if notes exist and toggle script is missing
    has_notes = soup.find(class_='speaker-notes')
    if has_notes:
        # Check if toggle script already exists
        has_toggle = False
        for script in soup.find_all('script'):
            if script.string and 'speaker-notes' in script.string:
                has_toggle = True
                break

        if not has_toggle:
            toggle_script = soup.new_tag('script')
            toggle_script.string = (
                "document.addEventListener('keydown', function(e) {"
                "  if (e.key === 'n' || e.key === 'N') {"
                "    var notes = document.querySelector('.speaker-notes');"
                "    if (notes) notes.style.display = notes.style.display !== 'none' ? 'none' : 'block';"
                "  }"
                "});"
            )
            body.append(toggle_script)

    # Add notes panel CSS if not already present
    if has_notes:
        head = soup.find('head')
        has_notes_css = False
        for style in soup.find_all('style'):
            if style.string and '.speaker-notes' in style.string:
                has_notes_css = True
                break
        if not has_notes_css and head:
            notes_style = soup.new_tag('style')
            notes_style.string = (
                '.speaker-notes{'
                'display:none;position:fixed;bottom:0;left:0;right:0;'
                'max-height:30vh;overflow-y:auto;'
                'background:rgba(0,0,0,0.92);color:#e0e0e0;'
                'font-family:system-ui,sans-serif;font-size:14px;line-height:1.5;'
                'padding:16px 24px;border-top:2px solid rgba(255,255,255,0.15);'
                'z-index:9999}'
                ".speaker-notes::before{"
                "content:'Speaker Notes (press N to hide)';"
                "display:block;font-size:11px;text-transform:uppercase;"
                "letter-spacing:0.05em;color:#888;margin-bottom:8px}"
            )
            head.append(notes_style)


def annotate_complexity(soup):
    """Scan slide content and add a complexity annotation for pipeline routing (#28).

    Inserts <!-- COMPLEXITY: high|low --> as the first child of .slide.
    High complexity: SVGs, gradients, pseudo-elements, rotated text, clip-paths.
    """
    slide = soup.find(class_='slide')
    if not slide:
        return

    signals = 0
    reasons = []

    # SVG elements
    svgs = slide.find_all('svg')
    if svgs:
        signals += len(svgs)
        reasons.append(f'{len(svgs)} SVG')

    # Check all style attributes and <style> tags for complex CSS
    all_styles = ' '.join(
        tag.get('style', '') for tag in slide.find_all(attrs={'style': True})
    )
    for style_tag in soup.find_all('style'):
        if style_tag.string:
            all_styles += ' ' + style_tag.string

    gradient_count = len(re.findall(r'linear-gradient|radial-gradient', all_styles, re.I))
    if gradient_count:
        signals += gradient_count
        reasons.append(f'{gradient_count} gradient')

    if re.search(r'writing-mode\s*:\s*vertical', all_styles, re.I):
        signals += 1
        reasons.append('vertical-text')

    if re.search(r'transform\s*:\s*rotate', all_styles, re.I):
        signals += 1
        reasons.append('rotation')

    pseudo_count = len(re.findall(r'::before|::after', all_styles))
    if pseudo_count:
        signals += pseudo_count
        reasons.append(f'{pseudo_count} pseudo')

    level = 'high' if signals >= 2 else 'low'
    reason_str = ', '.join(reasons) if reasons else 'simple layout'
    from bs4 import Comment
    slide.insert(0, Comment(f' COMPLEXITY: {level} — {reason_str} '))


def standardize_html(html_path, output_path=None, viewport_w=1280, viewport_h=720):
    """Orchestrate all normalizations. Returns path to normalized file."""
    html_path = Path(html_path)
    if not html_path.exists():
        raise FileNotFoundError(f'File not found: {html_path}')

    raw = html_path.read_text(encoding='utf-8', errors='replace')
    soup = BeautifulSoup(raw, 'lxml')

    # Detect source before any modifications
    detection = detect_source(soup)

    # Apply normalizations in order
    normalize_structure(soup)
    ensure_slide_wrapper(soup, w=viewport_w, h=viewport_h)
    normalize_viewport(soup, w=viewport_w, h=viewport_h)
    strip_animations(soup)
    strip_external_resources(soup)
    strip_navigation(soup)
    normalize_speaker_notes(soup)
    annotate_complexity(soup)
    annotate_source(soup, detection)

    # Determine output path
    if output_path is None:
        output_path = html_path
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(str(soup), encoding='utf-8')

    # Print detection for pipeline visibility
    src = detection['source']
    conf = detection['confidence']
    nf = detection['notes_format']
    print(f"  [{html_path.name}] source={src} ({conf}), notes={nf}")

    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description='Standardize HTML slide files for Chrome headless extraction.',
    )
    parser.add_argument(
        'input',
        nargs='?',
        help='Path to a single HTML file to normalize.',
    )
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Output path for normalized file (default: overwrite in place).',
    )
    parser.add_argument(
        '--dir',
        default=None,
        help='Directory of HTML files to normalize (batch mode, overwrites in place).',
    )
    parser.add_argument(
        '--width',
        type=int,
        default=1280,
        help='Viewport width in pixels (default: 1280).',
    )
    parser.add_argument(
        '--height',
        type=int,
        default=720,
        help='Viewport height in pixels (default: 720).',
    )

    args = parser.parse_args()

    if not args.input and not args.dir:
        parser.error('Provide either a file path or --dir for batch mode.')

    errors = 0

    if args.dir:
        dir_path = Path(args.dir)
        if not dir_path.is_dir():
            print(f'Error: {args.dir} is not a directory', file=sys.stderr)
            sys.exit(1)
        for html_file in sorted(dir_path.glob('*.html')):
            try:
                result = standardize_html(
                    html_file,
                    output_path=None,
                    viewport_w=args.width,
                    viewport_h=args.height,
                )
                print(result)
            except Exception as e:
                print(f'Error processing {html_file}: {e}', file=sys.stderr)
                errors += 1
    else:
        try:
            result = standardize_html(
                args.input,
                output_path=args.output,
                viewport_w=args.width,
                viewport_h=args.height,
            )
            print(result)
        except Exception as e:
            print(f'Error: {e}', file=sys.stderr)
            errors += 1

    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()

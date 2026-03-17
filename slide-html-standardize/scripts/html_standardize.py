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


def standardize_html(html_path, output_path=None, viewport_w=1280, viewport_h=720):
    """Orchestrate all normalizations. Returns path to normalized file."""
    html_path = Path(html_path)
    if not html_path.exists():
        raise FileNotFoundError(f'File not found: {html_path}')

    raw = html_path.read_text(encoding='utf-8', errors='replace')
    soup = BeautifulSoup(raw, 'lxml')

    # Apply normalizations in order
    normalize_structure(soup)
    ensure_slide_wrapper(soup, w=viewport_w, h=viewport_h)
    normalize_viewport(soup, w=viewport_w, h=viewport_h)
    strip_animations(soup)
    strip_external_resources(soup)

    # Determine output path
    if output_path is None:
        output_path = html_path
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(str(soup), encoding='utf-8')

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

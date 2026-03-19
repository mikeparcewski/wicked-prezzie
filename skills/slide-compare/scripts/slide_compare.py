#!/usr/bin/env python3
"""
slide-compare skill — Visual comparison of HTML originals vs PPTX output.

Renders both as images and saves side-by-side for review.
Requires: Chrome (for HTML), PowerPoint (for PPTX via AppleScript), pdftoppm

Usage:
    python skills/slide_compare.py --html-dir ./slides --pptx deck.pptx --output-dir ./compare
    python skills/slide_compare.py --html-dir ./slides --pptx deck.pptx --slides 1,5,10
"""

import argparse, os, sys, subprocess, glob, shutil
from pathlib import Path

# Import from sibling skills
_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_root / "shared"))
from paths import output_path
sys.path.insert(0, str(_root / "chrome-extract" / "scripts"))
sys.path.insert(0, str(_root / "slide-render" / "scripts"))
from chrome_extract import screenshot_html
from slide_render import export_pptx_to_pdf


def pdf_to_pngs(pdf_path, output_dir, dpi=150):
    """Convert PDF pages to PNG images using pdftoppm."""
    os.makedirs(output_dir, exist_ok=True)
    prefix = os.path.join(output_dir, 'slide')
    subprocess.run(['pdftoppm', '-png', '-r', str(dpi), pdf_path, prefix],
                  capture_output=True, timeout=120)
    return sorted(glob.glob(f"{prefix}-*.png"))


def compare_slides(html_dir, pptx_path, output_dir, slide_indices=None,
                  hide_selectors=None, viewport_w=1280, viewport_h=720):
    """
    Generate HTML vs PPTX comparison images.

    Args:
        html_dir: Directory with HTML slide files
        pptx_path: Path to PPTX file
        output_dir: Output directory for comparison images
        slide_indices: Optional list of 1-based slide indices to compare (None = all)
        hide_selectors: CSS selectors to hide in HTML screenshots
    """
    import tempfile

    os.makedirs(output_dir, exist_ok=True)
    html_dir_path = os.path.join(output_dir, 'html')
    pptx_dir_path = os.path.join(output_dir, 'pptx')
    os.makedirs(html_dir_path, exist_ok=True)
    os.makedirs(pptx_dir_path, exist_ok=True)

    # Export PPTX to PNGs
    print("Exporting PPTX to PDF...")
    pdf_path = os.path.join(output_dir, 'deck.pdf')
    if not export_pptx_to_pdf(pptx_path, pdf_path):
        print("ERROR: Failed to export PDF from PowerPoint")
        return

    import time; time.sleep(3)

    print("Converting PDF to PNGs...")
    pptx_pngs = pdf_to_pngs(pdf_path, pptx_dir_path)
    print(f"  {len(pptx_pngs)} PPTX slides exported")

    # Screenshot HTML files
    html_files = sorted(glob.glob(os.path.join(html_dir, 'slide-*.html')))

    # Build mapping: sequential PPTX page → HTML source filename
    # pptx_pngs[i] corresponds to html_files[i]
    for i, pptx_png in enumerate(pptx_pngs):
        if i < len(html_files):
            name = os.path.splitext(os.path.basename(html_files[i]))[0]
            mapped_path = os.path.join(pptx_dir_path, f'{name}.png')
            if str(pptx_png) != mapped_path:
                shutil.move(str(pptx_png), mapped_path)

    if not html_files:
        print(f"No slide HTML files found in {html_dir}")
        return

    hide = hide_selectors or ['.slide-nav', '.slide-number']

    with tempfile.TemporaryDirectory() as tmpdir:
        for i, html_file in enumerate(html_files):
            idx = i + 1
            if slide_indices and idx not in slide_indices:
                continue

            name = os.path.splitext(os.path.basename(html_file))[0]
            html_png = os.path.join(html_dir_path, f'{name}.png')

            print(f"  [{idx}/{len(html_files)}] {name}", end="")
            screenshot_html(html_file, html_png, tmpdir, viewport_w, viewport_h,
                          hide_selectors=hide)

            pptx_png = os.path.join(pptx_dir_path, f'{name}.png')
            status = "OK" if os.path.exists(pptx_png) else "MISSING PPTX"
            print(f" [{status}]")

    print(f"\nComparison images saved to {output_dir}/")
    print(f"  HTML: {html_dir_path}/")
    print(f"  PPTX: {pptx_dir_path}/")


def main():
    parser = argparse.ArgumentParser(description='Compare HTML slides vs PPTX output')
    parser.add_argument('--html-dir', '-d', required=True, help='HTML slides directory')
    parser.add_argument('--pptx', '-p', required=True, help='PPTX file to compare')
    parser.add_argument('--output-dir', '-o', default=output_path('compare'), help='Output directory')
    parser.add_argument('--slides', '-s', help='Comma-separated slide indices (1-based)')
    parser.add_argument('--hide', help='CSS selectors to hide (comma-separated)')
    args = parser.parse_args()

    indices = [int(x) for x in args.slides.split(',')] if args.slides else None
    hide = args.hide.split(',') if args.hide else None

    compare_slides(args.html_dir, args.pptx, args.output_dir, indices, hide)


if __name__ == '__main__':
    main()

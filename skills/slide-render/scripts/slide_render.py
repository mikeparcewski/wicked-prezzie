#!/usr/bin/env python3
"""Render PowerPoint (.pptx) slides to PNG images via PowerPoint PDF export.

Pipeline: PPTX -> PDF (PowerPoint via AppleScript/COM) -> PNG per page (pdftoppm)
Optionally creates a contact-sheet montage from the rendered PNGs.

Supports macOS (AppleScript) and Windows (COM automation via win32com).
"""

import argparse
import glob
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def export_pptx_to_pdf(pptx_path, pdf_path):
    """Export PPTX to PDF using PowerPoint automation.

    Detects the platform and uses the appropriate method:
    - macOS: AppleScript
    - Windows: COM automation via win32com

    Args:
        pptx_path: Path to the input .pptx file.
        pdf_path: Desired path for the output PDF.

    Returns:
        True if the PDF was created successfully.
    """
    pptx_abs = os.path.abspath(pptx_path)
    pdf_abs = os.path.abspath(pdf_path)
    os.makedirs(os.path.dirname(pdf_abs), exist_ok=True)

    if platform.system() == "Windows":
        return _export_pdf_windows(pptx_abs, pdf_abs)
    else:
        return _export_pdf_macos(pptx_abs, pdf_abs)


def _export_pdf_macos(pptx_abs, pdf_abs):
    """Export PPTX to PDF using PowerPoint AppleScript (macOS)."""
    script = f'''tell application "Microsoft PowerPoint"
    activate
    open POSIX file "{pptx_abs}"
    delay 4
    set thePresentation to active presentation
    save thePresentation in POSIX file "{pdf_abs}" as save as PDF
end tell'''

    subprocess.run(
        ['osascript', '-e', script],
        capture_output=True, text=True, timeout=120
    )
    time.sleep(2)
    return os.path.exists(pdf_abs)


def _export_pdf_windows(pptx_abs, pdf_abs):
    """Export PPTX to PDF using PowerPoint COM automation (Windows).

    Requires pywin32: pip install pywin32
    """
    try:
        import win32com.client
    except ImportError:
        raise RuntimeError(
            "win32com not found. Install pywin32:\n"
            "  pip install pywin32"
        )

    powerpoint = None
    presentation = None
    try:
        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        presentation = powerpoint.Presentations.Open(pptx_abs, WithWindow=False)
        # 32 = ppSaveAsPDF
        presentation.SaveAs(pdf_abs, 32)
        return os.path.exists(pdf_abs)
    except Exception as e:
        print(f"PowerPoint COM error: {e}", file=sys.stderr)
        return False
    finally:
        if presentation:
            try:
                presentation.Close()
            except Exception:
                pass
        if powerpoint:
            try:
                powerpoint.Quit()
            except Exception:
                pass


def pdf_to_pngs(pdf_path, output_dir, dpi=150):
    """Convert a PDF to individual PNG files using pdftoppm.

    Args:
        pdf_path: Path to the input PDF.
        output_dir: Directory to write PNG files into.
        dpi: Resolution in dots per inch.

    Returns:
        Sorted list of PNG file paths.

    Raises:
        RuntimeError: If pdftoppm is not installed.
    """
    os.makedirs(output_dir, exist_ok=True)
    prefix = str(Path(output_dir) / "slide")

    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        raise RuntimeError(
            "pdftoppm not found. Install poppler:\n"
            "  macOS:  brew install poppler\n"
            "  Ubuntu: sudo apt install poppler-utils"
        )

    cmd = [pdftoppm, "-png", "-r", str(dpi), str(pdf_path), prefix]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"pdftoppm failed: {result.stderr}")

    pngs = sorted(glob.glob(prefix + "-*.png"))
    return _normalize_names(pngs, output_dir)


def _normalize_names(png_paths, output_dir):
    """Rename PNGs to a consistent slide-01.png, slide-02.png scheme."""
    normalized = []
    for i, src in enumerate(sorted(png_paths)):
        dst = str(Path(output_dir) / f"slide-{i + 1:02d}.png")
        if str(src) != dst:
            shutil.move(str(src), dst)
        normalized.append(dst)
    return normalized


def render_pptx_to_pngs(pptx_path, output_dir, dpi=150, slides=None):
    """Render a PPTX file to individual PNG images.

    Pipeline: PPTX -> PDF (PowerPoint) -> PNG per page (pdftoppm).

    Args:
        pptx_path: Path to the input .pptx file.
        output_dir: Directory to write slide PNGs into.
        dpi: Resolution in dots per inch (default 150).
        slides: Optional list of 1-based slide numbers to keep.
                If None, all slides are rendered.

    Returns:
        Sorted list of output PNG paths (slide-01.png, slide-02.png, ...).
    """
    pptx_path = Path(pptx_path).resolve()
    if not pptx_path.exists():
        raise FileNotFoundError(f"PPTX file not found: {pptx_path}")

    output_dir = Path(output_dir).resolve()
    os.makedirs(output_dir, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = str(Path(tmp_dir) / "deck.pdf")

        print(f"Exporting {pptx_path.name} to PDF via PowerPoint...")
        if not export_pptx_to_pdf(str(pptx_path), pdf_path):
            raise RuntimeError(
                f"Failed to export {pptx_path} to PDF. "
                "Ensure Microsoft PowerPoint is installed on macOS."
            )

        print(f"Rasterizing PDF at {dpi} DPI...")
        all_pngs = pdf_to_pngs(pdf_path, str(output_dir), dpi=dpi)

    # Filter to requested slides
    if slides:
        filtered = []
        for png in all_pngs:
            num_str = Path(png).stem.split("-")[-1]
            try:
                if int(num_str) in slides:
                    filtered.append(png)
            except ValueError:
                continue
        # Remove unselected files
        for png in all_pngs:
            if png not in filtered:
                os.remove(png)
        all_pngs = _normalize_names(filtered, str(output_dir))

    print(f"Rendered {len(all_pngs)} slide(s) to {output_dir}/")
    return all_pngs


def create_montage(png_paths, output_path, cols=4, thumb_w=480):
    """Create a contact-sheet montage from slide PNG images.

    Tiles slide thumbnails into a grid image using Pillow.

    Args:
        png_paths: List of paths to slide PNG files.
        output_path: Path to write the montage image.
        cols: Number of columns in the grid (default 4).
        thumb_w: Thumbnail width in pixels (default 480).

    Returns:
        Path to the created montage image.
    """
    from PIL import Image

    if not png_paths:
        raise ValueError("No PNG files to montage")

    thumbs = []
    for p in png_paths:
        img = Image.open(p)
        ratio = thumb_w / img.width
        thumb_h = int(img.height * ratio)
        thumb = img.resize((thumb_w, thumb_h), Image.LANCZOS)
        thumbs.append(thumb)

    rows = (len(thumbs) + cols - 1) // cols
    thumb_h = max(t.height for t in thumbs)
    padding = 4

    canvas_w = cols * thumb_w + (cols + 1) * padding
    canvas_h = rows * thumb_h + (rows + 1) * padding

    montage = Image.new("RGB", (canvas_w, canvas_h), (255, 255, 255))

    for idx, thumb in enumerate(thumbs):
        row = idx // cols
        col = idx % cols
        x = padding + col * (thumb_w + padding)
        y = padding + row * (thumb_h + padding)
        montage.paste(thumb, (x, y))

    os.makedirs(str(Path(output_path).parent), exist_ok=True)
    montage.save(str(output_path), "PNG")
    print(f"Montage saved to {output_path} ({cols}x{rows} grid, {len(thumbs)} slides)")
    return str(output_path)


def parse_slides(slide_str):
    """Parse a comma-separated string of slide numbers into a list of ints."""
    if not slide_str:
        return None
    return [int(x.strip()) for x in slide_str.split(",") if x.strip()]


def main():
    parser = argparse.ArgumentParser(
        description="Render PowerPoint slides to PNG images via PowerPoint + pdftoppm.",
        epilog=(
            "Examples:\n"
            "  %(prog)s deck.pptx -o ./renders/\n"
            "  %(prog)s deck.pptx --montage montage.png\n"
            "  %(prog)s deck.pptx --slides 1,5,10 --dpi 300\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("pptx", help="Path to the input .pptx file")
    parser.add_argument("-o", "--output-dir", default="./slide-renders",
                        help="Directory for per-slide PNG output (default: ./slide-renders/)")
    parser.add_argument("--dpi", type=int, default=150,
                        help="Rasterization resolution in DPI (default: 150)")
    parser.add_argument("--slides", type=str, default=None,
                        help="Comma-separated 1-based slide numbers to render (default: all)")
    parser.add_argument("--montage", type=str, default=None,
                        help="Path to save a contact-sheet montage image")
    parser.add_argument("--cols", type=int, default=4,
                        help="Number of columns in montage grid (default: 4)")
    parser.add_argument("--thumb-width", type=int, default=480,
                        help="Thumbnail width in pixels for montage (default: 480)")

    args = parser.parse_args()
    pngs = render_pptx_to_pngs(
        pptx_path=args.pptx,
        output_dir=args.output_dir,
        dpi=args.dpi,
        slides=parse_slides(args.slides),
    )
    if args.montage and pngs:
        create_montage(png_paths=pngs, output_path=args.montage,
                       cols=args.cols, thumb_w=args.thumb_width)


if __name__ == "__main__":
    main()

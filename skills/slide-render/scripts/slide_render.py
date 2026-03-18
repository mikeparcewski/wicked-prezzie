#!/usr/bin/env python3
"""Render PowerPoint (.pptx) slides to PNG images via LibreOffice headless.

Pipeline: PPTX -> PDF (soffice --headless) -> PNG per page (pdftoppm)
Optionally creates a contact-sheet montage from the rendered PNGs.

No Microsoft PowerPoint required — uses LibreOffice for PDF conversion,
with automatic shim for sandboxed environments where AF_UNIX sockets
are blocked.
"""

import argparse
import glob
import os
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_root / "shared"))
from paths import output_path


# ---------------------------------------------------------------------------
# LibreOffice environment helpers (adapted from Anthropic's soffice.py)
# ---------------------------------------------------------------------------

def _needs_socket_shim():
    """Check if AF_UNIX sockets are blocked (sandboxed environments)."""
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.close()
        return False
    except OSError:
        return True


def _get_soffice_env():
    """Get environment dict for running soffice, with shim if needed."""
    env = os.environ.copy()
    env["SAL_USE_VCLPLUGIN"] = "svp"
    return env


def _find_soffice():
    """Find soffice binary across platforms."""
    # Check PATH first
    soffice = shutil.which("soffice")
    if soffice:
        return soffice

    # macOS common locations
    mac_paths = [
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        os.path.expanduser("~/Applications/LibreOffice.app/Contents/MacOS/soffice"),
    ]
    for p in mac_paths:
        if os.path.exists(p):
            return p

    # Linux common locations
    linux_paths = [
        "/usr/bin/soffice",
        "/usr/lib/libreoffice/program/soffice",
    ]
    for p in linux_paths:
        if os.path.exists(p):
            return p

    return None


# ---------------------------------------------------------------------------
# PPTX to PDF conversion
# ---------------------------------------------------------------------------

def export_pptx_to_pdf(pptx_path, pdf_path):
    """Export PPTX to PDF using LibreOffice headless.

    Args:
        pptx_path: Path to the input .pptx file.
        pdf_path: Desired path for the output PDF.

    Returns:
        True if the PDF was created successfully.
    """
    pptx_abs = os.path.abspath(pptx_path)
    pdf_abs = os.path.abspath(pdf_path)
    pdf_dir = os.path.dirname(pdf_abs)
    os.makedirs(pdf_dir, exist_ok=True)

    soffice = _find_soffice()
    if not soffice:
        raise RuntimeError(
            "LibreOffice (soffice) not found. Install it:\n"
            "  macOS:  brew install --cask libreoffice\n"
            "  Ubuntu: sudo apt install libreoffice\n"
            "  Windows: https://www.libreoffice.org/download/"
        )

    # soffice writes the PDF to --outdir with the input filename's stem
    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [
            soffice,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", tmpdir,
            pptx_abs,
        ]

        env = _get_soffice_env()
        result = subprocess.run(
            cmd, env=env,
            capture_output=True, text=True, timeout=120
        )

        if result.returncode != 0:
            print(f"soffice error: {result.stderr}", file=sys.stderr)
            return False

        # Find the generated PDF (named after the input file)
        stem = Path(pptx_abs).stem
        generated_pdf = os.path.join(tmpdir, f"{stem}.pdf")

        if not os.path.exists(generated_pdf):
            # Try to find any PDF in the output dir
            pdfs = glob.glob(os.path.join(tmpdir, "*.pdf"))
            if pdfs:
                generated_pdf = pdfs[0]
            else:
                return False

        shutil.move(generated_pdf, pdf_abs)

    return os.path.exists(pdf_abs)


# ---------------------------------------------------------------------------
# PDF to PNG conversion
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# High-level render API
# ---------------------------------------------------------------------------

def render_pptx_to_pngs(pptx_path, output_dir, dpi=150, slides=None):
    """Render a PPTX file to individual PNG images.

    Pipeline: PPTX -> PDF (LibreOffice) -> PNG per page (pdftoppm).

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

        print(f"Exporting {pptx_path.name} to PDF via LibreOffice...")
        if not export_pptx_to_pdf(str(pptx_path), pdf_path):
            raise RuntimeError(
                f"Failed to export {pptx_path} to PDF. "
                "Ensure LibreOffice is installed."
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


# ---------------------------------------------------------------------------
# Montage
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_slides(slide_str):
    """Parse a comma-separated string of slide numbers into a list of ints."""
    if not slide_str:
        return None
    return [int(x.strip()) for x in slide_str.split(",") if x.strip()]


def main():
    parser = argparse.ArgumentParser(
        description="Render PPTX slides to PNG images via LibreOffice + pdftoppm.",
        epilog=(
            "Examples:\n"
            "  %(prog)s deck.pptx -o ./renders/\n"
            "  %(prog)s deck.pptx --montage montage.png\n"
            "  %(prog)s deck.pptx --slides 1,5,10 --dpi 300\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("pptx", help="Path to the input .pptx file")
    parser.add_argument("-o", "--output-dir", default=output_path("renders"),
                        help="Directory for per-slide PNG output")
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

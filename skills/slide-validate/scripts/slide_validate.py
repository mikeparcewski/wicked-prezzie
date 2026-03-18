#!/usr/bin/env python3
"""Slide Validate — QA tool for PowerPoint files produced by wicked-pptx.

Checks for layout defects, content overflow, empty slides, and structural
problems. Supports static validation (python-pptx only) and visual overflow
detection (requires PowerPoint via slide-render).
"""

import os
import sys
import json
import argparse
import tempfile
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu

# Allow importing slide-render for visual overflow detection.
_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_root / "slide-render" / "scripts"))


# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------

def check_bounds(slide, slide_w, slide_h):
    """Check shapes for overflow beyond slide boundaries."""
    issues = []
    tolerance = Emu(50000)
    for shape in slide.shapes:
        right = shape.left + shape.width
        bottom = shape.top + shape.height
        if right > slide_w + tolerance:
            overflow = right - slide_w
            issues.append({
                "type": "bounds",
                "severity": "error",
                "description": (
                    f"Shape '{shape.name}' extends "
                    f"{Emu(overflow).inches:.2f}in past right edge"
                ),
            })
        if bottom > slide_h + tolerance:
            overflow = bottom - slide_h
            issues.append({
                "type": "bounds",
                "severity": "error",
                "description": (
                    f"Shape '{shape.name}' extends "
                    f"{Emu(overflow).inches:.2f}in past bottom edge"
                ),
            })
    return issues


def check_negative_coords(slide):
    """Detect shapes with negative positions (partially off-slide)."""
    issues = []
    tolerance = Emu(-50000)
    for shape in slide.shapes:
        if shape.left < tolerance:
            issues.append({
                "type": "negative_coord",
                "severity": "warning",
                "description": f"Shape '{shape.name}' has negative left position",
            })
        if shape.top < tolerance:
            issues.append({
                "type": "negative_coord",
                "severity": "warning",
                "description": f"Shape '{shape.name}' has negative top position",
            })
    return issues


def check_empty_slide(slide):
    """Detect slides with no content."""
    if len(slide.shapes) == 0:
        return [{"type": "empty", "severity": "warning",
                 "description": "Slide has no shapes"}]
    has_text = any(
        shape.has_text_frame and shape.text_frame.text.strip()
        for shape in slide.shapes
        if hasattr(shape, "has_text_frame")
    )
    has_image = any(shape.shape_type == 13 for shape in slide.shapes)
    if not has_text and not has_image:
        return [{"type": "empty", "severity": "warning",
                 "description": "Slide has no text or images"}]
    return []


def check_text_overflow(slide):
    """Heuristic check for text that likely overflows its container."""
    issues = []
    for shape in slide.shapes:
        if not hasattr(shape, "has_text_frame") or not shape.has_text_frame:
            continue
        text = shape.text_frame.text
        if not text.strip():
            continue
        width_inches = shape.width / 914400
        estimated_chars_per_line = width_inches * 12  # ~12 chars/inch at 12pt
        estimated_lines = shape.height / 914400 / 0.25  # ~0.25in per line
        max_chars = estimated_chars_per_line * max(1, estimated_lines)
        if len(text) > max_chars * 1.5:
            issues.append({
                "type": "text_overflow",
                "severity": "warning",
                "description": (
                    f"Text in '{shape.name}' may overflow "
                    f"({len(text)} chars in {width_inches:.1f}in wide box)"
                ),
            })
    return issues


# ---------------------------------------------------------------------------
# Visual overflow detection
# ---------------------------------------------------------------------------

def detect_visual_overflow(pptx_path, slide_w_emu, slide_h_emu, padding=50):
    """Visual overflow detection using the pad+render+check pattern.

    Creates a padded copy of the PPTX with grey margins, renders it to PNG,
    then scans margin regions for non-grey pixels that indicate content bleed.

    Args:
        pptx_path: Path to the original .pptx file.
        slide_w_emu: Original slide width in EMU.
        slide_h_emu: Original slide height in EMU.
        padding: Padding in pixels to add around each slide.

    Returns:
        List of issue dicts for slides with visual overflow.
    """
    try:
        from slide_render import render_pptx_to_pngs
        from PIL import Image
    except ImportError:
        return [{
            "type": "visual_overflow",
            "severity": "info",
            "description": (
                "Visual overflow check skipped: "
                "slide-render or Pillow not available"
            ),
        }]

    issues = []
    with tempfile.TemporaryDirectory() as tmpdir:
        # --- Build padded PPTX ---
        padded_path = os.path.join(tmpdir, "padded.pptx")
        prs = Presentation(pptx_path)
        pad_emu = int(padding * 914400 / 96)  # px to EMU at 96 dpi
        new_w = prs.slide_width + 2 * pad_emu
        new_h = prs.slide_height + 2 * pad_emu
        prs.slide_width = new_w
        prs.slide_height = new_h

        for slide in prs.slides:
            # Shift every shape by the padding offset.
            for shape in slide.shapes:
                shape.left += pad_emu
                shape.top += pad_emu
            # Paint the background grey so the margin is detectable.
            from pptx.dml.color import RGBColor
            bg = slide.background
            bg.fill.solid()
            bg.fill.fore_color.rgb = RGBColor(0x80, 0x80, 0x80)

        prs.save(padded_path)

        # --- Render padded PPTX to PNGs ---
        render_dir = os.path.join(tmpdir, "renders")
        try:
            pngs = render_pptx_to_pngs(padded_path, render_dir)
        except Exception:
            return [{
                "type": "visual_overflow",
                "severity": "info",
                "description": (
                    "Visual overflow check failed: "
                    "LibreOffice rendering error"
                ),
            }]

        # --- Scan margins for content bleed ---
        grey = (128, 128, 128)
        tolerance = 15

        for idx, png_path in enumerate(pngs):
            img = Image.open(png_path)
            w, h = img.size
            # Compute expected margin size in rendered pixels.
            total_w_px = slide_w_emu / 914400 * 96 + 2 * padding
            total_h_px = slide_h_emu / 914400 * 96 + 2 * padding
            margin_x = int(w * padding / total_w_px)
            margin_y = int(h * padding / total_h_px)

            overflow_edges = []
            regions = [
                ("top", img.crop((margin_x, 0, w - margin_x, margin_y))),
                ("bottom", img.crop((margin_x, h - margin_y, w - margin_x, h))),
                ("left", img.crop((0, margin_y, margin_x, h - margin_y))),
                ("right", img.crop((w - margin_x, margin_y, w, h - margin_y))),
            ]
            for edge, region in regions:
                pixels = list(region.getdata())
                if not pixels:
                    continue
                non_grey = sum(
                    1 for p in pixels
                    if (abs(p[0] - grey[0]) > tolerance
                        or abs(p[1] - grey[1]) > tolerance
                        or abs(p[2] - grey[2]) > tolerance)
                )
                if non_grey > len(pixels) * 0.01:  # >1% non-grey
                    overflow_edges.append(edge)

            if overflow_edges:
                issues.append({
                    "type": "visual_overflow",
                    "severity": "error",
                    "slide_index": idx + 1,
                    "description": (
                        f"Content overflows on "
                        f"{', '.join(overflow_edges)} edge(s)"
                    ),
                })

    return issues


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_slide(issues):
    """Score a slide from 0-100. Deduct per issue by severity and type."""
    score = 100
    for issue in issues:
        if issue["severity"] == "error":
            if issue["type"] == "bounds":
                score -= 10
            elif issue["type"] == "visual_overflow":
                score -= 10
            elif issue["type"] == "empty":
                score -= 15
            else:
                score -= 5
        elif issue["severity"] == "warning":
            score -= 3
    return max(0, score)


# ---------------------------------------------------------------------------
# Main validation entry point
# ---------------------------------------------------------------------------

def _load_threshold():
    """Load quality threshold from config file if it exists."""
    config_path = Path(__file__).parent.parent.parent / "slide-config" / "config.json"
    if config_path.exists():
        try:
            with open(config_path) as f:
                cfg = json.load(f)
            return cfg.get("quality_threshold", 85)
        except (json.JSONDecodeError, KeyError):
            pass
    return 85


def validate_pptx(pptx_path, render=False, rubric_path=None, threshold=None):
    """Run full validation on a PPTX file.

    Args:
        pptx_path: Path to the .pptx file.
        render: If True, run visual overflow detection (requires slide-render).
        rubric_path: Reserved for future custom rubric support.
        threshold: Quality threshold (0-100). Default loaded from config or 85.

    Returns:
        Dict with summary statistics and per-slide results.
    """
    if threshold is None:
        threshold = _load_threshold()
    prs = Presentation(pptx_path)
    slide_w = prs.slide_width
    slide_h = prs.slide_height
    results = []

    for i, slide in enumerate(prs.slides):
        issues = []
        issues.extend(check_bounds(slide, slide_w, slide_h))
        issues.extend(check_negative_coords(slide))
        issues.extend(check_empty_slide(slide))
        issues.extend(check_text_overflow(slide))
        score = score_slide(issues)
        results.append({
            "index": i + 1,
            "score": score,
            "pass": score >= threshold,
            "issues": issues,
        })

    if render:
        overflow_issues = detect_visual_overflow(pptx_path, slide_w, slide_h)
        for oi in overflow_issues:
            idx = oi.get("slide_index")
            if idx and 1 <= idx <= len(results):
                results[idx - 1]["issues"].append(oi)
                results[idx - 1]["score"] = score_slide(
                    results[idx - 1]["issues"]
                )
                results[idx - 1]["pass"] = results[idx - 1]["score"] >= threshold
            else:
                # Info-level messages without a slide index (e.g. import
                # errors) are attached to the first slide for visibility.
                if results:
                    results[0]["issues"].append(oi)

    total = len(results)
    passed = sum(1 for r in results if r["pass"])
    avg_score = sum(r["score"] for r in results) / total if total else 0

    return {
        "file": os.path.basename(pptx_path),
        "total_slides": total,
        "passed": passed,
        "failed": total - passed,
        "score": round(avg_score),
        "threshold": threshold,
        "slides": results,
    }


# ---------------------------------------------------------------------------
# Human-readable report
# ---------------------------------------------------------------------------

def print_report(report):
    """Print a concise human-readable validation report."""
    print("=== Slide Validation Report ===")
    print(f"File:   {report['file']}")
    print(
        f"Slides: {report['total_slides']} total, "
        f"{report['passed']} passed, {report['failed']} failed"
    )
    print(f"Score:  {report['score']}/100 (threshold: {report['threshold']})")
    print()

    failing = [s for s in report["slides"] if not s["pass"]]
    if not failing:
        print("All slides passed.")
        return

    for slide in failing:
        print(f"Slide {slide['index']} [FAIL] score={slide['score']}")
        for issue in slide["issues"]:
            sev = issue["severity"].upper()
            print(f"  [{sev}] {issue['type']}: {issue['description']}")
        print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Validate a PPTX file for layout defects and overflow."
    )
    parser.add_argument(
        "pptx_path",
        help="Path to the .pptx file to validate.",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Enable visual overflow detection (requires slide-render + PowerPoint).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON instead of the human-readable summary.",
    )
    parser.add_argument(
        "--rubric",
        default=None,
        help="Path to a custom rubric JSON file (reserved for future use).",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=None,
        help="Quality threshold 0-100 (default: 85, or from slide-config/config.json).",
    )

    args = parser.parse_args()

    if not os.path.isfile(args.pptx_path):
        print(f"Error: file not found: {args.pptx_path}", file=sys.stderr)
        sys.exit(1)

    report = validate_pptx(
        args.pptx_path,
        render=args.render,
        rubric_path=args.rubric,
        threshold=args.threshold,
    )

    if args.json_output:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    # Exit with non-zero status if any slides failed.
    if report["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()

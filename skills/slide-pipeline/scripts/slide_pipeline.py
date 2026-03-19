#!/usr/bin/env python3
"""
slide-pipeline — End-to-end orchestrator for HTML-to-PPTX conversion.

Chains: standardize → convert → validate → render → compare

Single-pass tool. Iterative refinement is orchestrated by the SKILL.md
workflow — Claude renders, visually inspects, and re-runs as needed.

Usage:
    python slide-pipeline/scripts/slide_pipeline.py --input-dir ./slides --output deck.pptx
    python slide-pipeline/scripts/slide_pipeline.py -d ./slides -o deck.pptx --visual-overflow
    python slide-pipeline/scripts/slide_pipeline.py -d ./slides -o deck.pptx --no-render --no-compare
"""

import argparse, os, sys, json, glob
from pathlib import Path

# Import from sibling skills
_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_root / "shared"))
from paths import output_path as default_output_path
sys.path.insert(0, str(_root / "slide-html-to-pptx" / "scripts"))
sys.path.insert(0, str(_root / "slide-validate" / "scripts"))
sys.path.insert(0, str(_root / "slide-render" / "scripts"))
sys.path.insert(0, str(_root / "slide-compare" / "scripts"))
sys.path.insert(0, str(_root / "chrome-extract" / "scripts"))

from html_to_pptx import build_deck, extract_notes
from slide_validate import validate_pptx


def discover_slides(input_dir, slides_arg=None, manifest_arg=None):
    """Discover HTML slide files from arguments or directory scan."""
    if manifest_arg:
        with open(manifest_arg) as f:
            return json.load(f)
    elif slides_arg:
        return [{'file': f.strip()} for f in slides_arg.split(',')]
    else:
        html_files = sorted(glob.glob(os.path.join(input_dir, '*.html')))
        return [{'file': os.path.basename(f)} for f in html_files
                if 'index' not in os.path.basename(f).lower()
                and 'sorter' not in os.path.basename(f).lower()]


def run_pipeline(input_dir, output_path, slides, viewport_w=1280, viewport_h=720,
                 hide_selectors=None, standardize=True, validate=True,
                 render=True, compare=True, visual_overflow=False,
                 montage_path=None, render_dir=None, compare_dir=None,
                 workers=None):
    """Run the full slide conversion pipeline (single pass).

    Returns:
        dict with pipeline results and validation report
    """
    if render_dir is None:
        render_dir = default_output_path('renders')
    if compare_dir is None:
        compare_dir = default_output_path('compare')

    hide = hide_selectors or ['.slide-nav', '.slide-number']
    results = {'stages': {}, 'success': True}

    # Stage 1+2: Standardize + Convert (parallel per-slide extraction)
    stage_label = "Standardize + Convert" if standardize else "Convert"
    print(f"\n=== {stage_label} (parallel) ===")
    pptx_path = build_deck(slides, input_dir, output_path, hide, viewport_w, viewport_h,
                           standardize=standardize, workers=workers)
    results['stages']['convert'] = {'output': pptx_path}

    # Stage 3: Structural Validation (not visual fidelity)
    if validate:
        print("\n=== Stage 3: Structural Validation ===")
        print("  (checks PPTX structure: bounds, overflow, empty slides)")
        print("  (does NOT check visual fidelity — that's the per-slide comparison loop)")
        report = validate_pptx(pptx_path, render=visual_overflow)
        results['stages']['validate'] = report

        # Write report
        report_path = os.path.splitext(output_path)[0] + '-validation.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"  Structural score: {report['structural_score']}/100 "
              f"(threshold: {report['threshold']})")
        print(f"  Passed: {report['passed']}/{report['total_slides']}")
        if report['failed'] > 0:
            print(f"  Failed slides:")
            for s in report['slides']:
                if not s['pass']:
                    issues = ', '.join(i['description'][:60] for i in s['issues'][:3])
                    print(f"    Slide {s['index']}: score {s['score']} — {issues}")
            results['success'] = False
    else:
        print("\n=== Stage 3: Validate [SKIPPED] ===")

    # Stage 4: Render
    if render:
        print("\n=== Stage 4: Render ===")
        try:
            from slide_render import render_pptx_to_pngs, create_montage
            os.makedirs(render_dir, exist_ok=True)
            pngs = render_pptx_to_pngs(pptx_path, render_dir)
            results['stages']['render'] = {'pngs': len(pngs), 'output_dir': render_dir}
            print(f"  Rendered {len(pngs)} slides to {render_dir}/")

            if montage_path:
                create_montage(pngs, montage_path)
                results['stages']['render']['montage'] = montage_path
                print(f"  Montage: {montage_path}")
        except Exception as e:
            print(f"  Render failed: {e}")
            results['stages']['render'] = {'error': str(e)}
    else:
        print("\n=== Stage 4: Render [SKIPPED] ===")

    # Stage 5: Compare
    if compare:
        print("\n=== Stage 5: Compare ===")
        try:
            from slide_compare import compare_slides
            compare_slides(input_dir, pptx_path, compare_dir, hide_selectors=hide)
            results['stages']['compare'] = {'output_dir': compare_dir}
        except Exception as e:
            print(f"  Compare failed: {e}")
            results['stages']['compare'] = {'error': str(e)}
    else:
        print("\n=== Stage 5: Compare [SKIPPED] ===")

    # Summary
    print("\n=== Pipeline Complete ===")
    print(f"  Output: {output_path}")
    if 'validate' in results['stages'] and isinstance(results['stages']['validate'], dict):
        r = results['stages']['validate']
        structural_ok = results['success']
        print(f"  Structural: {'PASS' if structural_ok else 'ISSUES'} "
              f"({r['structural_score']}/100)")
    print(f"  Visual fidelity: NOT YET CHECKED")
    print()
    print("  >>> Next: run per-slide visual comparison (pipeline Step 2)")
    print("      Compare HTML screenshots vs PPTX renders for each slide.")
    print("      The structural score only checks shape bounds, not visual accuracy.")

    return results


def main():
    parser = argparse.ArgumentParser(
        description='End-to-end HTML slide conversion pipeline')
    parser.add_argument('--input-dir', '-d', default='.', help='HTML slides directory')
    parser.add_argument('--output', '-o', default='deck.pptx', help='Output PPTX path')
    parser.add_argument('--slides', '-s', help='Comma-separated HTML filenames')
    parser.add_argument('--manifest', '-m', help='JSON manifest file')
    parser.add_argument('--viewport', default='1280x720', help='Viewport WxH')
    parser.add_argument('--hide', help='CSS selectors to hide (comma-separated)')

    parser.add_argument('--workers', '-w', type=int, default=None,
                        help='Max parallel Chrome workers (default: min(slides, cpu_count/2, 6))')
    parser.add_argument('--no-standardize', action='store_true',
                        help='Skip HTML standardization')
    parser.add_argument('--no-validate', action='store_true',
                        help='Skip PPTX validation')
    parser.add_argument('--no-render', action='store_true',
                        help='Skip PPTX→PNG rendering')
    parser.add_argument('--no-compare', action='store_true',
                        help='Skip HTML vs PPTX comparison')
    parser.add_argument('--visual-overflow', action='store_true',
                        help='Enable visual overflow detection (requires LibreOffice)')
    parser.add_argument('--montage', help='Create contact sheet at given path')
    parser.add_argument('--render-dir', default=default_output_path('renders'),
                        help='Output directory for rendered PNGs')
    parser.add_argument('--compare-dir', default=default_output_path('compare'),
                        help='Output directory for comparison images')
    args = parser.parse_args()

    vw, vh = map(int, args.viewport.split('x'))
    hide = args.hide.split(',') if args.hide else None

    slides = discover_slides(args.input_dir, args.slides, args.manifest)
    if not slides:
        print("No slides found. Use --slides, --manifest, or place HTML in --input-dir")
        sys.exit(2)

    print(f"Pipeline: {len(slides)} slides from {args.input_dir}")
    results = run_pipeline(
        args.input_dir, args.output, slides,
        viewport_w=vw, viewport_h=vh, hide_selectors=hide,
        standardize=not args.no_standardize,
        validate=not args.no_validate,
        render=not args.no_render,
        compare=not args.no_compare,
        visual_overflow=args.visual_overflow,
        montage_path=args.montage,
        render_dir=args.render_dir,
        compare_dir=args.compare_dir,
        workers=args.workers,
    )

    sys.exit(0 if results['success'] else 1)


if __name__ == '__main__':
    main()

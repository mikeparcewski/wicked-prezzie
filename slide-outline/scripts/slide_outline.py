#!/usr/bin/env python3
"""
slide-outline — Structure topics into presentation outlines.

Usage:
    python slide-outline/scripts/slide_outline.py --topic "Q1 Results" --output outline.json
    python slide-outline/scripts/slide_outline.py --validate outline.json
    python slide-outline/scripts/slide_outline.py --summary outline.json
"""

import argparse, json, re, sys
from pathlib import Path

_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_root / "slide-theme" / "scripts"))

VALID_TYPES = {"title", "section", "content", "stats", "comparison", "quote", "cta", "blank"}
VALID_LAYOUTS = {
    "bullets", "two-column", "image-text", "card-grid", "big-number",
    "split", "table", "centered", "left-aligned", "centered-quote",
}


def load_outline(path):
    """Load outline from JSON file."""
    with open(path) as f:
        return json.load(f)


def save_outline(outline, path):
    """Save outline to JSON file."""
    with open(path, "w") as f:
        json.dump(outline, f, indent=2)
    print(f"Outline saved to {path}")


def _word_count(text):
    """Count words in a string or list of strings/dicts."""
    if isinstance(text, str):
        return len(text.split())
    if isinstance(text, list):
        total = 0
        for item in text:
            if isinstance(item, str):
                total += len(item.split())
            elif isinstance(item, dict):
                total += sum(len(str(v).split()) for v in item.values())
        return total
    return 0


def _is_assertion(title):
    """Heuristic: check if a title is an assertion (has a verb or number) vs a topic label."""
    # Topic labels tend to be noun phrases: "Revenue Update", "Market Overview"
    # Assertions have verbs or numbers: "Revenue grew 40%", "3 key insights"
    if re.search(r'\d', title):
        return True
    # Common verb indicators
    verb_patterns = [
        r'\b(is|are|was|were|has|have|had|will|can|should|must|need|grew|grow|increased|decreased|reduced|exceeded|achieved|delivered|enabled|drove|shows|reveals|proves|requires|demands)\b',
        r'\b\w+ed\b',  # past tense
        r'\b\w+ing\b',  # gerund (but not as first word which is often a label)
    ]
    for pattern in verb_patterns:
        if re.search(pattern, title, re.IGNORECASE):
            return True
    return False


def validate_outline(outline):
    """Validate outline structure and content. Returns (errors, warnings)."""
    errors = []
    warnings = []

    # Top-level fields
    if "title" not in outline:
        errors.append("Missing 'title' field")
    if "acts" not in outline:
        errors.append("Missing 'acts' field")
        return errors, warnings
    if "key_message" not in outline:
        warnings.append("No 'key_message' — consider adding one for narrative focus")
    if "theme" not in outline:
        warnings.append("No 'theme' specified — will use default")

    acts = outline.get("acts", [])
    if not acts:
        errors.append("No acts defined")
        return errors, warnings

    # Check act structure
    act_names = [a.get("name", "unnamed") for a in acts]
    has_setup = any("setup" in n.lower() or "intro" in n.lower() for n in act_names)
    has_close = any("close" in n.lower() or "conclusion" in n.lower() or "cta" in n.lower() for n in act_names)
    if not has_setup:
        warnings.append("No Setup/Intro act — consider adding one")
    if not has_close:
        warnings.append("No Close/Conclusion act — consider adding one")

    # Count total slides
    total_slides = 0
    for act_idx, act in enumerate(acts):
        act_name = act.get("name", f"Act {act_idx + 1}")
        slides = act.get("slides", [])

        if len(slides) > 5:
            warnings.append(f"Act '{act_name}' has {len(slides)} slides (recommend max 5)")

        for slide_idx, slide in enumerate(slides):
            total_slides += 1
            slide_ref = f"Act '{act_name}', slide {slide_idx + 1}"

            # Required fields
            if "type" not in slide:
                errors.append(f"{slide_ref}: missing 'type'")
            elif slide["type"] not in VALID_TYPES:
                errors.append(f"{slide_ref}: invalid type '{slide['type']}' (valid: {', '.join(sorted(VALID_TYPES))})")

            if "title" not in slide:
                errors.append(f"{slide_ref}: missing 'title'")
            else:
                # Check if title is an assertion (skip for title/section/blank types)
                if slide.get("type") not in ("title", "section", "blank"):
                    if not _is_assertion(slide["title"]):
                        warnings.append(f"{slide_ref}: title '{slide['title']}' looks like a topic label — consider making it an assertion")

            # Word count
            body = slide.get("body", [])
            wc = _word_count(body)
            if wc > 75:
                warnings.append(f"{slide_ref}: body has {wc} words (max 75)")

            # Layout check
            layout = slide.get("layout")
            if layout and layout not in VALID_LAYOUTS:
                warnings.append(f"{slide_ref}: unknown layout '{layout}'")

            # Notes
            if "notes" not in slide:
                warnings.append(f"{slide_ref}: no speaker notes")

    if total_slides < 3:
        errors.append(f"Only {total_slides} slides (minimum 3)")
    if total_slides > 20:
        warnings.append(f"{total_slides} slides — consider trimming for focus")

    return errors, warnings


def summarize_outline(outline):
    """Print a human-readable outline summary."""
    print(f"=== {outline.get('title', 'Untitled')} ===")
    if outline.get("subtitle"):
        print(f"    {outline['subtitle']}")
    if outline.get("key_message"):
        print(f"    Key message: {outline['key_message']}")
    if outline.get("theme"):
        print(f"    Theme: {outline['theme']}")
    if outline.get("target_audience"):
        print(f"    Audience: {outline['target_audience']}")
    print()

    total = 0
    for act in outline.get("acts", []):
        slides = act.get("slides", [])
        print(f"  [{act.get('name', 'Unnamed')}] ({len(slides)} slides)")
        for i, slide in enumerate(slides):
            stype = slide.get("type", "?")
            title = slide.get("title", "untitled")
            layout = slide.get("layout", "")
            layout_str = f" [{layout}]" if layout else ""
            print(f"    {total + 1}. ({stype}{layout_str}) {title}")
            total += 1
        print()

    print(f"  Total: {total} slides")


def scaffold_outline(topic, audience=None, key_message=None, theme=None):
    """Create a minimal outline scaffold from a topic."""
    outline = {
        "title": topic,
        "subtitle": "",
        "author": "",
        "theme": theme or "midnight-purple",
        "target_audience": audience or "",
        "key_message": key_message or "",
        "acts": [
            {
                "name": "Setup",
                "color_hint": "primary",
                "slides": [
                    {
                        "type": "title",
                        "title": topic,
                        "subtitle": "TODO: Add subtitle",
                        "notes": "TODO: Opening context",
                    },
                    {
                        "type": "content",
                        "title": "TODO: Problem statement as assertion",
                        "body": ["TODO: Supporting point 1", "TODO: Supporting point 2"],
                        "layout": "bullets",
                        "notes": "TODO: Frame the problem",
                    },
                ],
            },
            {
                "name": "Evidence",
                "color_hint": "secondary",
                "slides": [
                    {
                        "type": "content",
                        "title": "TODO: Key finding as assertion",
                        "body": ["TODO: Evidence point 1", "TODO: Evidence point 2", "TODO: Evidence point 3"],
                        "layout": "bullets",
                        "notes": "TODO: Present evidence",
                    },
                ],
            },
            {
                "name": "Close",
                "color_hint": "accent",
                "slides": [
                    {
                        "type": "cta",
                        "title": "TODO: Call to action as assertion",
                        "body": ["TODO: Next step 1", "TODO: Next step 2"],
                        "notes": "TODO: Clear ask",
                    },
                ],
            },
        ],
    }
    return outline


def main():
    parser = argparse.ArgumentParser(description="Structure topics into presentation outlines")

    parser.add_argument("--topic", "-t", help="Presentation topic")
    parser.add_argument("--audience", "-a", help="Target audience")
    parser.add_argument("--key-message", "-k", help="Key message / main takeaway")
    parser.add_argument("--theme", help="Theme name for the outline")
    parser.add_argument("--brief", "-b", help="Path to a brief/document to structure")
    parser.add_argument("--output", "-o", help="Output path for outline JSON")
    parser.add_argument("--validate", "-v", metavar="FILE", help="Validate an existing outline")
    parser.add_argument("--summary", "-s", metavar="FILE", help="Show outline summary")
    parser.add_argument("--outline", metavar="FILE", help="Existing outline to modify")
    parser.add_argument("--set-theme", help="Set theme on an existing outline")

    args = parser.parse_args()

    if args.validate:
        outline = load_outline(args.validate)
        errors, warnings = validate_outline(outline)
        for e in errors:
            print(f"  ERROR: {e}")
        for w in warnings:
            print(f"  WARN:  {w}")
        if not errors and not warnings:
            print("  PASS — outline is valid")
        elif errors:
            print(f"\n  {len(errors)} error(s), {len(warnings)} warning(s)")
            sys.exit(1)
        else:
            print(f"\n  {len(warnings)} warning(s), no errors")
        return

    if args.summary:
        outline = load_outline(args.summary)
        summarize_outline(outline)
        return

    if args.outline and args.set_theme:
        outline = load_outline(args.outline)
        outline["theme"] = args.set_theme
        save_outline(outline, args.outline)
        print(f"Theme set to '{args.set_theme}'")
        return

    if args.topic:
        outline = scaffold_outline(
            args.topic,
            audience=args.audience,
            key_message=args.key_message,
            theme=args.theme,
        )
        output = args.output or "outline.json"
        save_outline(outline, output)
        print("Scaffold created with TODO placeholders — fill in slide content.")
        summarize_outline(outline)
        return

    if args.brief:
        # For brief-to-outline, we create a scaffold and note that AI should fill it
        brief_text = Path(args.brief).read_text()
        # Extract a title from the first line
        first_line = brief_text.strip().split("\n")[0].strip("# ").strip()
        outline = scaffold_outline(first_line, audience=args.audience, key_message=args.key_message, theme=args.theme)
        output = args.output or "outline.json"
        save_outline(outline, output)
        print("Scaffold created from brief — review and refine the structure.")
        return

    parser.print_help()


if __name__ == "__main__":
    main()

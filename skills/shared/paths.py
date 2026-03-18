"""Centralized path resolution for wicked-prezzie output and data directories.

All intermediate and default output files go under ~/.something-wicked/wicked-prezzie/
to keep user project directories clean.
"""

from pathlib import Path

DATA_ROOT = Path.home() / ".something-wicked" / "wicked-prezzie"
OUTPUT_DIR = DATA_ROOT / "output"


def output_path(*parts):
    """Return a path under the default output directory, creating parents as needed.

    Example:
        output_path("renders")        -> ~/.something-wicked/wicked-prezzie/output/renders
        output_path("deck.pptx")      -> ~/.something-wicked/wicked-prezzie/output/deck.pptx
        output_path("compare", "html") -> ~/.something-wicked/wicked-prezzie/output/compare/html
    """
    p = OUTPUT_DIR.joinpath(*parts)
    return str(p)


def ensure_output_dir(*parts):
    """Return a path under the default output directory, creating it if needed."""
    p = OUTPUT_DIR.joinpath(*parts)
    p.mkdir(parents=True, exist_ok=True)
    return str(p)

# Export Safety

Safe export practices. No export is declared complete until visual verification
passes. CLI output alone is never sufficient.

## Version Bumping Before Export

Before producing any export artifact, bump the deck version:

1. Read `versioning.md` for the version scheme
2. Increment the patch version (e.g., v3.1.1 → v3.1.2) for minor fixes
3. Increment the minor version (v3.1.2 → v3.2.0) for slide additions or content changes
4. Write the new version to `deck-state.json` under `"version"`
5. Tag the commit with the version number before producing export artifacts

Never overwrite a prior version's export files. Keep previous exports until the
new version passes visual verification.

## Visual Verification (Required)

Visual verification is a distinct step, not an optional add-on. It is
architecturally required.

**Protocol**: After any export operation, screenshot representative slides and
read each with vision:

```
Slides to verify: 1, N/4, N/2, 3N/4, N
(For a 40-slide deck: slides 1, 10, 20, 30, 40)
```

**Check each screenshot for**:
- Dark background present (not white/blank)
- Text readable at expected size
- No content overflow past slide boundaries
- Styling intact (not unstyled HTML)
- Navigation elements absent from export (nav stripped for PDF/PPTX)

**Declare export complete only when**: All sampled slides pass visual check.
If any slide fails, fix and re-export that slide, then re-verify.

**The `export-visual-verification` Stop hook** warns if the conversation
includes an export tool call but no subsequent Read of a screenshot file.

## No HTML to /tmp/

Temp HTML files must never be written to `/tmp/`. Relative CSS/JS paths break
when files are copied outside the deck directory.

```
WRONG: /tmp/slide-temp.html  (breaks relative paths to styles.css, nav.js)
RIGHT: /path/to/deck/tmp/slide-temp.html  (relative paths remain valid)
```

If a temp file is needed for PDF generation, create it inside the deck
directory in a `tmp/` or `render-temp/` subdirectory.

The `prevent-tmp-html` PreToolUse hook blocks any Bash command that writes
`.html` to `/tmp/`.

## Path Audit

After any file copy or move operation involving HTML files:

1. Read the moved file with the Read tool
2. Verify every `href` and `src` attribute resolves relative to the new location
3. If any path is broken, use absolute paths or re-create the file in its
   correct location

For bundled HTML exports that inline all CSS and JS, verify the inlining
was complete by checking: no remaining `<link rel="stylesheet">` tags, no
remaining `<script src=...>` tags.

## Handling Partial Failures

When some slides pass export and others fail:

1. Record which slides passed (by slide number and file name)
2. Record which slides have REVIEW flags (inherent format limitations)
3. Record which slides failed (issue category and description)
4. Produce the export artifact with passing slides
5. Document failures in the treatment log
6. Do not declare the export complete until all blocking failures are resolved

REVIEW flags are acceptable — they indicate acknowledged format limitations
(e.g., gradient backgrounds rendered as solid, CSS animation stripped). They
are not failures. Document them and proceed.

## Rollback Protocol

Keep the previous version of all export artifacts until the new version passes
visual verification:

```
deck-v3.1.1.pptx    (previous — keep until v3.1.2 passes)
deck-v3.1.2.pptx    (new — verify before declaring current)
```

If the new version fails visual verification and cannot be fixed in the
current session, revert to the previous version and document the failure.

## Chrome Headless PDF Generation

For PDF export, use a print-optimized HTML variant:

1. Create `deck-print.html` (or similar) in the deck directory — NOT in `/tmp/`
2. Strip navigation elements: `.slide-nav`, `.nav-pill`, `.notes-panel`
3. Strip JavaScript (no nav.js, no notes-data.js needed for PDF)
4. Add page-break CSS: each `.slide` gets `page-break-after: always`
5. Run Chrome headless:

```bash
google-chrome --headless --disable-gpu \
  --print-to-pdf="deck.pdf" \
  --print-to-pdf-no-header \
  "file:///path/to/deck/deck-print.html"
```

6. Verify the PDF: check page count matches slide count, verify first/last page render correctly

**Key rule**: The `deck-print.html` file must be in the deck directory, not
`/tmp/`. Relative paths to styles.css must resolve from the print file's location.

## Bundled HTML Recipe

For email distribution / offline viewing, inline all assets into a single file:

```python
# Pseudocode — implement with BeautifulSoup or similar
from pathlib import Path
import re

deck_dir = Path("/path/to/deck")
slides_html = [f.read_text() for f in sorted(deck_dir.glob("slide-*.html"))]

# Read shared assets
styles = (deck_dir / "styles.css").read_text()
notes_data = (deck_dir / "notes-data.js").read_text()
nav_js = (deck_dir / "nav.js").read_text()

# Build bundled file
bundled = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1280">
<style>{styles}</style>
</head>
<body>
{"".join(slides_html)}
<script>{notes_data}</script>
<script>{nav_js}</script>
</body>
</html>"""

(deck_dir / "deck-bundled.html").write_text(bundled)
```

After creating the bundled file, verify:
- No remaining `<link rel="stylesheet">` tags (CSS was inlined)
- No remaining `<script src=...>` tags (JS was inlined)
- All slide content present (count `<div class="slide">` elements)
- File opens correctly in browser without network access

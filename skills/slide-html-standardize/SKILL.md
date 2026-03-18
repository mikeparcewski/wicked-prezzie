---
name: Slide HTML Standardize
description: >
  Normalizes AI-generated HTML slides before conversion — adds viewport, .slide
  wrapper, strips animations and external resources. Use whenever slides came
  from ChatGPT, Claude, Gemini, or any AI. Also use when Chrome extraction fails
  or returns empty results. Always the correct first step for AI-generated HTML
  that hasn't been preprocessed.
---

# Slide HTML Standardize

## Purpose

HTML slide decks produced by AI generators, design tools, and manual authoring arrive in wildly inconsistent formats. Some lack a proper `<html><head><body>` skeleton. Some omit a viewport meta tag, causing Chrome headless to render at an unexpected width. Some include CSS animations that produce blank or mid-transition snapshots. Some pull fonts and scripts from external CDNs that may be unavailable or slow during headless extraction.

The HTML Standardize skill preprocesses slide HTML files into a predictable, self-contained format before they enter the Chrome headless extraction pipeline. Running this step first eliminates an entire class of layout and rendering failures that would otherwise surface as mispositioned shapes, missing text, or broken screenshots in the final PPTX.

## When to Use

Run this skill in any of the following situations:

- Before converting HTML slides to PPTX for the first time.
- When AI-generated slide HTML produces unexpected layout in the PPTX output.
- When Chrome headless screenshots show animations frozen mid-transition.
- When slides render differently on different machines due to external font or script dependencies.
- When the HTML file lacks a `.slide` wrapper element and shapes appear at incorrect positions.
- When batch-processing a directory of slide files from mixed sources.
- After editing slide HTML manually to verify structural correctness.

Do not run this skill on HTML that has already been normalized unless the source was modified after the previous normalization pass.

## Usage

Normalize a single HTML file in place (overwrites the original):

```bash
python ${CLAUDE_SKILL_DIR}/scripts/html_standardize.py slide.html
```

Normalize a single file and write the result to a new path:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/html_standardize.py slide.html -o slide_clean.html
```

Normalize every `.html` file in a directory (each file is overwritten in place):

```bash
python ${CLAUDE_SKILL_DIR}/scripts/html_standardize.py --dir ./slides/
```

Normalize with a custom viewport size (default is 1280x720):

```bash
python ${CLAUDE_SKILL_DIR}/scripts/html_standardize.py slide.html --width 1920 --height 1080
```

Combine directory mode with a custom viewport:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/html_standardize.py --dir ./slides/ --width 1920 --height 1080
```

The script prints the path of each normalized file to stdout. Exit code 0 indicates success; nonzero indicates at least one file failed.

## Key Normalizations Performed

### Document Structure

Ensure the file contains a well-formed `<html>` element with `<head>` and `<body>` sections. If any of these elements are missing, create them and reparent existing content appropriately. Remove duplicate `<body>` tags if present. Guarantee a `<meta charset="utf-8">` tag exists inside `<head>`.

### Viewport Meta Tag

Set or create a `<meta name="viewport">` tag with the `content` attribute set to `width={viewport_w}`. Chrome headless uses this to determine the rendering width. Without it, slides may render at 800px or another browser default, causing all bounding-box coordinates to shift.

### Slide Wrapper Element

Verify that an element with the CSS class `slide` exists. The Chrome extraction script expects a `.slide` container to define the slide boundaries. If no such element is found, wrap all body content inside a `<div class="slide">` with explicit `width` and `height` styles matching the viewport dimensions. Also set `position: relative; overflow: hidden;` on the wrapper so absolutely positioned children resolve correctly.

### Animation and Transition Stripping

Remove all CSS animation and transition properties from inline `style` attributes on every element. Specifically strip `animation`, `animation-name`, `animation-duration`, `animation-delay`, `animation-fill-mode`, `animation-timing-function`, `animation-iteration-count`, `animation-direction`, `animation-play-state`, `transition`, `transition-property`, `transition-duration`, `transition-delay`, and `transition-timing-function`. Inside `<style>` tags, remove `@keyframes` rule blocks entirely. This prevents Chrome from capturing a mid-animation frame instead of the final visual state.

### External Resource Removal

Remove `<link>` tags whose `href` points to external CDNs including `fonts.googleapis.com`, `fonts.gstatic.com`, `cdnjs.cloudflare.com`, `unpkg.com`, `cdn.jsdelivr.net`, and any other `http://` or `https://` origin that differs from a relative path. Remove `<script>` tags whose `src` attribute references an external URL. Preserve all inline `<style>` blocks and inline `<script>` blocks (those without a `src` attribute). This makes the HTML fully self-contained so headless rendering does not depend on network access.

### Style Attribute Cleanup

After stripping animation properties, collapse any resulting double-semicolons or trailing semicolons in `style` attributes. Remove `style` attributes that become empty after cleanup.

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Shapes shifted right or down in PPTX | Viewport width does not match the design width. | Re-run with `--width` matching the original design (inspect the HTML for clues). |
| Text missing from PPTX but visible in browser | External font failed to load during headless render. | Run standardize to strip external font links; ensure fallback fonts are acceptable. |
| Blank or partially-visible slide screenshot | CSS animation captured mid-transition. | Run standardize to strip all animations and transitions. |
| `.slide` wrapper inserted but layout still wrong | Body content uses `position: absolute` relative to `<body>`, not `.slide`. | Verify the original HTML intended a different wrapper; adjust manually if needed. |
| Duplicate text or overlapping elements | Duplicate `<body>` tags in malformed HTML. | Run standardize; it removes duplicate bodies automatically. |
| Script errors in Chrome headless log | External JS dependency unavailable. | Run standardize to strip external scripts. |
| Normalized file larger than original | Inserted wrapper div and meta tags add bytes. | This is expected; the increase is negligible (under 500 bytes typically). |
| Batch mode skips some files | Files may not have `.html` extension. | Rename files or process them individually by path. |

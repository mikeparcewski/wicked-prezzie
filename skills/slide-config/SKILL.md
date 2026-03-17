---
name: Slide Config
description: >
  Project-level configuration for the wicked-pptx toolkit — quality threshold,
  viewport defaults, hide selectors, font settings. Use this skill whenever the
  user wants to change the quality threshold (default 85), set a custom viewport
  size, change which CSS selectors get hidden, configure the default font, or
  view current settings. Also use when the user says "the threshold is too strict"
  or "too lenient", "change the default viewport", or "what are the current
  settings". Settings persist in config.json and are automatically read by
  slide-validate and slide-pipeline.
---

# Slide Config

Project-level configuration for the wicked-pptx toolkit. Stores user
preferences that persist across sessions and are read by other skills.

## When to Use

- Setting the quality threshold for slide validation (default: 85)
- Configuring default viewport dimensions
- Setting default CSS selectors to hide
- Viewing current configuration

## Configuration File

Settings are stored in `skills/slide-config/config.json` at the project root.
Other skills read this file automatically when it exists.

## Usage

```bash
# View current config
python ${CLAUDE_SKILL_DIR}/scripts/slide_config.py show

# Set quality threshold
python ${CLAUDE_SKILL_DIR}/scripts/slide_config.py set quality_threshold 90

# Set default viewport
python ${CLAUDE_SKILL_DIR}/scripts/slide_config.py set viewport 1920x1080

# Set default hide selectors
python ${CLAUDE_SKILL_DIR}/scripts/slide_config.py set hide_selectors ".slide-nav,.footer"

# Reset to defaults
python ${CLAUDE_SKILL_DIR}/scripts/slide_config.py reset
```

## Settings

| Key | Default | Used By | Purpose |
|---|---|---|---|
| `quality_threshold` | 85 | slide-validate, slide-pipeline | Minimum score for a slide to pass |
| `viewport` | `1280x720` | slide-html-standardize, slide-html-to-pptx, slide-pipeline | Default viewport dimensions |
| `hide_selectors` | `[".slide-nav"]` | slide-html-to-pptx, slide-pipeline | CSS selectors to hide during extraction |
| `default_font` | `Calibri` | slide-pptx-builder | Font for generated PPTX text |
| `slide_width_inches` | `13.333` | slide-pptx-builder | Slide width |
| `slide_height_inches` | `7.5` | slide-pptx-builder | Slide height |

## How Other Skills Read Config

Skills use `_load_threshold()` or similar helpers that check for
`skills/slide-config/config.json` at the project root:

```python
config_path = Path(__file__).parent.parent.parent / "slide-config" / "config.json"
if config_path.exists():
    cfg = json.load(open(config_path))
    threshold = cfg.get("quality_threshold", 85)
```

If the config file doesn't exist, skills use their built-in defaults.

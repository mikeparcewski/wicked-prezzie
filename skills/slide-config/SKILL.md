---
name: Slide Config
description: >
  Two-tier configuration for the wicked-pptx toolkit — user-level defaults in
  ~/.something-wicked/wicked-prezzie/config.json (shared across projects:
  default_font, default_fidelity, unsplash_api_key) and project-level overrides
  in skills/slide-config/config.json (quality_threshold, viewport, hide_selectors,
  active_theme, slide dimensions). Use this skill whenever the user wants to
  change settings, set the quality threshold, configure viewport size, set the
  default font or fidelity tier, add an Unsplash API key, change which CSS
  selectors get hidden, or view current settings. Also use when the user says
  "the threshold is too strict", "change the default viewport", "set my API key",
  "what are the current settings", or "configure fidelity". Resolution order:
  defaults → user config → project config (project wins).
---

# Slide Config

Project-level configuration for the wicked-pptx toolkit. Stores user
preferences that persist across sessions and are read by other skills.

## When to Use

- Setting the quality threshold for slide validation (default: 85)
- Configuring default viewport dimensions
- Setting default CSS selectors to hide
- Viewing current configuration

## Configuration Files

Settings are stored at two levels:

- **User-level**: `~/.something-wicked/wicked-prezzie/config.json` — shared across projects
  (default_font, default_fidelity, unsplash_api_key)
- **Project-level**: `skills/slide-config/config.json` — per-project overrides
  (quality_threshold, viewport, hide_selectors, active_theme, slide dimensions)

Resolution order: defaults → user config → project config (project wins).

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
| `default_font` | `Calibri` | slide-pptx-builder | Font for generated PPTX text (user-level) |
| `default_fidelity` | `draft` | slide-pipeline | Default fidelity tier (user-level) |
| `unsplash_api_key` | (none) | slide-generate | Unsplash API key for image sourcing (user-level) |
| `slide_width_inches` | `13.333` | slide-pptx-builder | Slide width (project-level) |
| `slide_height_inches` | `7.5` | slide-pptx-builder | Slide height (project-level) |

## How Other Skills Read Config

Skills use `load_config()` which merges defaults → user → project:

```python
from pathlib import Path
import json

USER_DATA_DIR = Path.home() / ".something-wicked" / "wicked-prezzie"
USER_CONFIG = USER_DATA_DIR / "config.json"
PROJECT_CONFIG = Path(__file__).parent.parent.parent / "slide-config" / "config.json"

def load_config():
    config = {"quality_threshold": 85, "viewport": "1280x720", ...}
    if USER_CONFIG.exists():
        config.update(json.load(open(USER_CONFIG)))
    if PROJECT_CONFIG.exists():
        config.update(json.load(open(PROJECT_CONFIG)))
    return config
```

If neither config file exists, skills use their built-in defaults.

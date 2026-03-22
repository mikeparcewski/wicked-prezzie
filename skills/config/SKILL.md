---
name: config
description: |
  Settings and configuration for the slide toolkit. Thresholds, viewport,
  fonts, fidelity tiers, and slide dimensions live here.

  Use when: "change settings", "set quality threshold", "configure viewport",
  "set default font", "fidelity tier", "too strict", "too loose", "slide dimensions",
  "Unsplash API key", "view settings", "current config"
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
- **Project-level**: `skills/config/config.json` — per-project overrides
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
| `quality_threshold` | 85 | validate, convert | Minimum score for a slide to pass |
| `viewport` | `1280x720` | standardize, quick-convert, convert | Default viewport dimensions |
| `hide_selectors` | `[".slide-nav"]` | quick-convert, convert | CSS selectors to hide during extraction |
| `default_font` | `Calibri` | pptx-builder | Font for generated PPTX text (user-level) |
| `default_fidelity` | `draft` | convert | Default fidelity tier (user-level) |
| `unsplash_api_key` | (none) | generate | Unsplash API key for image sourcing (user-level) |
| `slide_width_inches` | `13.333` | pptx-builder | Slide width (project-level) |
| `slide_height_inches` | `7.5` | pptx-builder | Slide height (project-level) |
| `index_dirs` | `[]` | config | Additional directories scanned when listing decks or themes (project-level) |

## How Other Skills Read Config

Skills use `load_config()` which merges defaults → user → project:

```python
from pathlib import Path
import json

USER_DATA_DIR = Path.home() / ".something-wicked" / "wicked-prezzie"
USER_CONFIG = USER_DATA_DIR / "config.json"
PROJECT_CONFIG = Path(__file__).parent.parent.parent / "config" / "config.json"

def load_config():
    config = {"quality_threshold": 85, "viewport": "1280x720", ...}
    if USER_CONFIG.exists():
        config.update(json.load(open(USER_CONFIG)))
    if PROJECT_CONFIG.exists():
        config.update(json.load(open(PROJECT_CONFIG)))
    return config
```

If neither config file exists, skills use their built-in defaults.

## Reference Files

Read on demand — do not load all at once.

| File | Read when... |
|---|---|
| [constraint-format.md](references/constraint-format.md) | constraints.json schema, field definitions, severity levels, relationship to config.json, index_dirs key |

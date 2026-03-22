# Constraint Format

Canonical JSON schema for constraints. Constraints persist across sessions,
preventing recurring bugs from being re-learned.

## File Locations

| File | Purpose | Scope |
|---|---|---|
| `{deck-dir}/constraints.json` | Runtime constraints for this deck | Per-project |
| `skills/config/config.json` | Settings (quality threshold, viewport, etc.) | Per-project |
| `~/.something-wicked/wicked-prezzie/config.json` | User defaults | User-level |

`constraints.json` and `config.json` serve different purposes:
- `config.json` stores **settings** (numeric thresholds, string values, API keys)
- `constraints.json` stores **behavioral rules** (what agents must do or not do)

## constraints.json Full Schema

```json
{
  "constraints": [
    {
      "id": "string",
      "phase_added": "string",
      "severity": "blocking | recommended",
      "rule": "string",
      "reason": "string",
      "applies_to": ["array", "of", "phase", "strings"],
      "slide_override": {
        "SLIDE_NUMBER": "override rule or 'skip'"
      }
    }
  ]
}
```

### Field Definitions

#### `id` (required, string)
Unique kebab-case identifier. Must be stable — other files may reference it.

```
"css-vertical-centering"
"notes-inline-only"
"visual-verification-required"
```

Rules:
- Lowercase kebab-case only
- No spaces or underscores
- Descriptive of the constraint, not the bug
- Must be unique within the file

#### `phase_added` (required, string)
The phase during which this constraint was created.

Valid values:
- `"default"` — shipped with the skill, not session-specific
- `"brainstorm"` — learned during brainstorming phase
- `"build"` — learned during slide build phase
- `"validate"` — learned during validation phase
- `"export"` — learned during export phase

#### `severity` (required, string)
Controls how strictly the constraint is enforced.

**`"blocking"`**:
- Must be followed without exception
- Violation causes visible failure or significant rework
- Hook-enforced where architecturally possible
- A task cannot be marked complete if a blocking constraint is violated
- Per-slide overrides require explicit `slide_override` entry with reason

**`"recommended"`**:
- Should be followed; deviation requires documented justification
- Violation degrades quality but does not cause hard failure
- Per-slide overrides are acceptable with documented reason

#### `rule` (required, string)
The constraint text injected into agent prompts. Must be:
- Actionable (tells the agent exactly what to do)
- Self-contained (makes sense without reading this file)
- Specific (not "be careful with CSS" but "never use align-items:stretch on .slide-content")

#### `reason` (required, string)
Why this constraint exists. Reference the session, version, or bug that made it necessary.

```
"7 recurrences, 22 CSS edits, 1 dedicated 783KB cleanup agent in v3"
"fetch() fails on file:// protocol — broke identically in v1 and v3"
"PDF export lost all styling when temp file was written to /tmp/"
```

The reason helps future agents understand the consequence of violation, not just
the rule itself.

#### `applies_to` (required, array of strings)
Phases where this constraint is injected into agent prompts. The orchestrator
filters by phase before injection — a build agent only sees build constraints.

Valid values: `"brainstorm"`, `"build"`, `"validate"`, `"export"`

Multiple phases: `["build", "validate", "export"]`

#### `slide_override` (optional, object)
Per-slide exceptions to the constraint. Key is the slide number as a string.
Value is either a modified rule (if the slide needs a different rule) or `"skip"`
(if the constraint does not apply to this slide at all).

```json
"slide_override": {
  "12": "skip — slide 12 uses a fixed-width sidebar, standard flex rule does not apply",
  "23": "use align-items:flex-start instead of center — this slide is top-aligned by design"
}
```

## Relationship to config.json

`config.json` stores settings; `constraints.json` stores behavioral rules.
They are separate files with different read patterns:

| | config.json | constraints.json |
|---|---|---|
| Read by | All skills via `load_config()` | Orchestrator only, then injected |
| Updated by | `slide_config.py set KEY VALUE` | "Learn Constraint" protocol |
| Format | Key-value settings | Array of rule objects |
| Scope | Settings that skills query | Rules that agents must follow |

## index_dirs Configuration Key

The `index_dirs` key in `config.json` specifies directories that the slide
config skill scans when listing available decks or themes.

```json
{
  "index_dirs": [
    "/path/to/projects/presentations",
    "/path/to/another/deck/collection"
  ]
}
```

This is a project-level key stored in `skills/config/config.json`.

**Usage**: When the user asks "what decks do I have?" or "show me all themes",
the config skill reads `index_dirs` and scans each directory for deck
directories (containing `slides.json`) and theme files (`*.json` in `themes/`).

**Default**: `[]` (empty — no additional directories scanned beyond the current project)

## Resolution Order

Settings resolve in this order (later wins):

```
built-in defaults
    ↓
~/.something-wicked/wicked-prezzie/config.json  (user-level)
    ↓
skills/config/config.json  (project-level)
    ↓
result
```

Project-level always wins. If a key appears in both user and project config,
the project value is used.

User-level keys: `default_font`, `default_fidelity`, `unsplash_api_key`
Project-level keys: `quality_threshold`, `viewport`, `hide_selectors`,
`active_theme`, `slide_width_inches`, `slide_height_inches`, `index_dirs`

## Validation Rules

A valid `constraints.json` must:
- Have a top-level `"constraints"` key that is an array
- Each constraint must have: `id`, `phase_added`, `severity`, `rule`, `reason`, `applies_to`
- `severity` must be exactly `"blocking"` or `"recommended"`
- All `applies_to` values must be valid phase names
- All `id` values must be unique within the file
- `slide_override` keys must be string representations of slide numbers

If `constraints.json` is malformed, the orchestrator logs a warning and
proceeds without constraints rather than failing. Fix the file before the
next session.

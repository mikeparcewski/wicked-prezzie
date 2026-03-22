#!/usr/bin/env python3
"""
config — Manage wicked-pptx project configuration.

Usage:
    python config/scripts/slide_config.py show
    python config/scripts/slide_config.py set quality_threshold 90
    python config/scripts/slide_config.py reset
"""

import argparse, json, os, sys
from pathlib import Path

USER_DATA_DIR = Path.home() / ".something-wicked" / "wicked-prezzie"
USER_CONFIG_PATH = USER_DATA_DIR / "config.json"
PROJECT_CONFIG_PATH = Path(__file__).parent.parent / "config.json"

DEFAULTS = {
    "quality_threshold": 85,
    "viewport": "1280x720",
    "hide_selectors": [".slide-nav"],
    "default_font": "Calibri",
    "slide_width_inches": 13.333,
    "slide_height_inches": 7.5,
}

# Keys that are user-level (shared across projects)
USER_KEYS = {"default_font", "default_fidelity", "unsplash_api_key"}
# All other keys are project-level
VALID_KEYS = set(DEFAULTS.keys()) | USER_KEYS


def load_config():
    """Load config: defaults → user config → project config (project wins)."""
    config = dict(DEFAULTS)
    # Layer 1: user-level config
    if USER_CONFIG_PATH.exists():
        try:
            with open(USER_CONFIG_PATH) as f:
                config.update(json.load(f))
        except (json.JSONDecodeError, IOError):
            pass
    # Layer 2: project-level config (overrides user)
    if PROJECT_CONFIG_PATH.exists():
        try:
            with open(PROJECT_CONFIG_PATH) as f:
                config.update(json.load(f))
        except (json.JSONDecodeError, IOError):
            pass
    return config


def save_config(config, key=None):
    """Save config to the appropriate file based on key scope."""
    if key and key in USER_KEYS:
        # Save to user-level config
        user_config = {}
        if USER_CONFIG_PATH.exists():
            try:
                with open(USER_CONFIG_PATH) as f:
                    user_config = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        user_config[key] = config[key]
        USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(USER_CONFIG_PATH, 'w') as f:
            json.dump(user_config, f, indent=2)
        print(f"Config saved to {USER_CONFIG_PATH} (user-level)")
    else:
        # Save to project-level config (exclude user keys)
        project_config = {k: v for k, v in config.items() if k not in USER_KEYS}
        with open(PROJECT_CONFIG_PATH, 'w') as f:
            json.dump(project_config, f, indent=2)
        print(f"Config saved to {PROJECT_CONFIG_PATH} (project-level)")


def coerce_value(key, value):
    """Coerce string value to the appropriate type for the key."""
    default = DEFAULTS.get(key)
    if isinstance(default, int):
        return int(value)
    elif isinstance(default, float):
        return float(value)
    elif isinstance(default, list):
        return [v.strip() for v in value.split(',')]
    return value


def cmd_show(args):
    """Show current configuration."""
    config = load_config()
    print("=== wicked-pptx Configuration ===")
    print(f"  User config:    {USER_CONFIG_PATH}")
    print(f"  Project config: {PROJECT_CONFIG_PATH}")
    print()
    for key, value in sorted(config.items()):
        default = DEFAULTS.get(key)
        scope = "user" if key in USER_KEYS else "project"
        marker = "" if value == default else " (custom)"
        print(f"  {key}: {value}{marker}  [{scope}]")


def cmd_set(args):
    """Set a configuration value."""
    if args.key not in VALID_KEYS:
        print(f"Error: unknown key '{args.key}'")
        print(f"Valid keys: {', '.join(sorted(VALID_KEYS))}")
        sys.exit(1)

    config = load_config()
    config[args.key] = coerce_value(args.key, args.value)
    save_config(config, key=args.key)
    scope = "user" if args.key in USER_KEYS else "project"
    print(f"  {args.key} = {config[args.key]} ({scope}-level)")


def cmd_reset(args):
    """Reset to default configuration."""
    save_config(dict(DEFAULTS))
    print("Reset to defaults.")


def main():
    parser = argparse.ArgumentParser(description='Manage wicked-pptx configuration')
    sub = parser.add_subparsers(dest='command')

    sub.add_parser('show', help='Show current configuration')

    set_p = sub.add_parser('set', help='Set a configuration value')
    set_p.add_argument('key', help='Configuration key')
    set_p.add_argument('value', help='Value to set')

    sub.add_parser('reset', help='Reset to defaults')

    args = parser.parse_args()

    if args.command == 'show':
        cmd_show(args)
    elif args.command == 'set':
        cmd_set(args)
    elif args.command == 'reset':
        cmd_reset(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
slide-config — Manage wicked-pptx project configuration.

Usage:
    python slide-config/scripts/slide_config.py show
    python slide-config/scripts/slide_config.py set quality_threshold 90
    python slide-config/scripts/slide_config.py reset
"""

import argparse, json, os, sys
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.json"

DEFAULTS = {
    "quality_threshold": 85,
    "viewport": "1280x720",
    "hide_selectors": [".slide-nav"],
    "default_font": "Calibri",
    "slide_width_inches": 13.333,
    "slide_height_inches": 7.5,
}

VALID_KEYS = set(DEFAULTS.keys())


def load_config():
    """Load config from file, falling back to defaults."""
    config = dict(DEFAULTS)
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                saved = json.load(f)
            config.update(saved)
        except (json.JSONDecodeError, IOError):
            pass
    return config


def save_config(config):
    """Save config to file."""
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Config saved to {CONFIG_PATH}")


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
    for key, value in sorted(config.items()):
        default = DEFAULTS.get(key)
        marker = "" if value == default else " (custom)"
        print(f"  {key}: {value}{marker}")


def cmd_set(args):
    """Set a configuration value."""
    if args.key not in VALID_KEYS:
        print(f"Error: unknown key '{args.key}'")
        print(f"Valid keys: {', '.join(sorted(VALID_KEYS))}")
        sys.exit(1)

    config = load_config()
    config[args.key] = coerce_value(args.key, args.value)
    save_config(config)
    print(f"  {args.key} = {config[args.key]}")


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

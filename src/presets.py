"""
presets.py — Load a vertical preset and merge it over the base agent config.

Presets in presets/*.yaml are partial overlays (routes, qualification, scoring
weights, compliance). This merges a chosen preset onto config/agent_config.yaml
so you get a complete, vertical-specific config without editing the base.

Usage:
    python src/presets.py --list
    python src/presets.py healthcare_intake          # prints merged config
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "config" / "agent_config.yaml"
PRESET_DIR = ROOT / "presets"


def list_presets() -> list[str]:
    return sorted(p.stem for p in PRESET_DIR.glob("*.yaml"))


def _deep_merge(base: dict, overlay: dict) -> dict:
    out = dict(base)
    for k, v in overlay.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_merged(preset_name: str) -> dict:
    preset_path = PRESET_DIR / f"{preset_name}.yaml"
    if not preset_path.exists():
        raise FileNotFoundError(f"Preset '{preset_name}' not found. Available: {list_presets()}")
    base = yaml.safe_load(BASE.read_text())
    overlay = yaml.safe_load(preset_path.read_text())
    return _deep_merge(base, overlay)


def main() -> int:
    parser = argparse.ArgumentParser(description="Load and merge a vertical preset.")
    parser.add_argument("preset", nargs="?", help="Preset name (see --list)")
    parser.add_argument("--list", action="store_true", help="List available presets")
    args = parser.parse_args()

    if args.list or not args.preset:
        print("Available presets:")
        for p in list_presets():
            print(f"  - {p}")
        return 0

    merged = load_merged(args.preset)
    print(yaml.safe_dump(merged, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

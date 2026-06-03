"""
validate_config.py — Pre-deploy validator for the agent config and schema.

Catches the broken-config-in-production failure mode: missing required keys,
malformed YAML/JSON, unfilled {{PLACEHOLDER}} tokens in a config you intended to
deploy, and tier definitions that don't match the expected shape.

Usage:
    python src/validate_config.py config/agent_config.yaml
    python src/validate_config.py config/agent_config.local.yaml --strict
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

REQUIRED_TOP_LEVEL = {"agent", "routes", "qualification", "sms", "rules"}
EXPECTED_ROUTES = {
    "A_primary_service", "B_secondary_service", "C_partner_program",
    "D_returning_client", "E_other_triage",
}
PLACEHOLDER = re.compile(r"\{\{[A-Z_]+\}\}")


def validate_yaml_config(path: Path, strict: bool) -> list[str]:
    errors: list[str] = []
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        return [f"YAML parse error: {e}"]

    if not isinstance(data, dict):
        return ["Config root must be a mapping."]

    missing = REQUIRED_TOP_LEVEL - data.keys()
    if missing:
        errors.append(f"Missing required top-level keys: {sorted(missing)}")

    routes = data.get("routes", [])
    route_ids = {r.get("id") for r in routes if isinstance(r, dict)}
    missing_routes = EXPECTED_ROUTES - route_ids
    if missing_routes:
        errors.append(f"Missing expected routes: {sorted(missing_routes)}")

    # In strict mode, a deployable config must have no unfilled placeholders.
    if strict:
        leftover = PLACEHOLDER.findall(path.read_text())
        if leftover:
            uniq = sorted(set(leftover))
            errors.append(f"Unfilled placeholders in strict mode: {uniq}")

    return errors


def validate_json_schema(path: Path) -> list[str]:
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return [f"JSON parse error: {e}"]
    tiers = data.get("properties", {}).get("tiers", {}).get("properties", {})
    if len(tiers) != 4:
        return [f"Expected 4 tiers, found {len(tiers)}"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate agent config / schema.")
    parser.add_argument("path", help="Path to a .yaml config or .json schema")
    parser.add_argument("--strict", action="store_true",
                        help="Fail if unfilled {{PLACEHOLDER}} tokens remain")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"ERROR: {path} not found")
        return 2

    if path.suffix in (".yaml", ".yml"):
        errors = validate_yaml_config(path, args.strict)
    elif path.suffix == ".json":
        errors = validate_json_schema(path)
    else:
        print(f"ERROR: unsupported file type {path.suffix}")
        return 2

    if errors:
        print(f"INVALID: {path}")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"VALID: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

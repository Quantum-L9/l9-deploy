#!/usr/bin/env python3
"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer:
- repository
tags:
- L9_META
- deployment-platform
owner: platform
status: active
--- /L9_META ---
"""
from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import add_repository_src

ROOT = add_repository_src()

from l9_deploy.contracts.validator import SchemaRegistry  # noqa: E402
from l9_deploy.inventory.generator import generate_ansible_inventory  # noqa: E402
from l9_deploy.inventory.loader import load_fleet  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Ansible inventory from the fleet contract"
    )
    parser.add_argument("--fleet", type=Path, default=ROOT / "fleet/registry.yaml")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "ansible/inventories/generated/hosts.yml",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registry = SchemaRegistry(ROOT / "schemas/v1")
    fleet = load_fleet(args.fleet, registry)
    generate_ansible_inventory(fleet, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

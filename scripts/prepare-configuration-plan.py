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
import json
from pathlib import Path

from _bootstrap import add_repository_src

add_repository_src()

from l9_deploy.canonical import atomic_write_json  # noqa: E402
from l9_deploy.planning.configuration import build_configuration_plan  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--repository-revision", required=True)
    parser.add_argument("--fleet", type=Path, default=Path("fleet/registry.yaml"))
    parser.add_argument("--playbook", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--server-id", default="")
    parser.add_argument("--allow-environment-wide", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    plan = build_configuration_plan(
        repository_root=root,
        repository_revision=args.repository_revision,
        fleet_path=(root / args.fleet),
        playbook_path=(root / args.playbook),
        inventory_path=(root / args.inventory),
        environment=args.environment,
        server_id=args.server_id,
        allow_environment_wide=args.allow_environment_wide,
    )
    atomic_write_json(args.output, plan, mode=0o640)
    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

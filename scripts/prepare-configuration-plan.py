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
import sys
from pathlib import Path

from _bootstrap import add_repository_src

add_repository_src()

from l9_deploy.planning.configuration import build_configuration_plan  # noqa: E402

_PLAYBOOK_PATHS = {
    "bootstrap": Path("ansible/playbooks/bootstrap.yml"),
    "harden": Path("ansible/playbooks/harden.yml"),
    "configure-runner": Path("ansible/playbooks/configure-runner.yml"),
    "configure-runtime": Path("ansible/playbooks/configure-runtime.yml"),
    "configure-backups": Path("ansible/playbooks/configure-backups.yml"),
    "verify": Path("ansible/playbooks/verify.yml"),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-revision", required=True)
    parser.add_argument("--playbook", choices=tuple(_PLAYBOOK_PATHS), required=True)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--server-id", default="")
    parser.add_argument("--allow-environment-wide", action="store_true")
    args = parser.parse_args()

    root = Path.cwd().resolve()
    plan = build_configuration_plan(
        repository_root=root,
        repository_revision=args.repository_revision,
        fleet_path=root / "fleet/registry.yaml",
        playbook_path=root / _PLAYBOOK_PATHS[args.playbook],
        inventory_path=root / "ansible/inventories/generated/hosts.yml",
        environment=args.environment,
        server_id=args.server_id,
        allow_environment_wide=args.allow_environment_wide,
    )
    sys.stdout.write(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

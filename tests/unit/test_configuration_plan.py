"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer:
- tests
tags:
- L9_META
- deployment-platform
owner: platform
status: active
--- /L9_META ---
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from l9_deploy.errors import AuthorizationError
from l9_deploy.planning.configuration import build_configuration_plan


def _fixture_files(root: Path) -> tuple[Path, Path, Path]:
    fleet = root / "fleet/registry.yaml"
    playbook = root / "ansible/playbooks/configure-runtime.yml"
    inventory = root / "ansible/inventories/generated/hosts.yml"
    fleet.parent.mkdir(parents=True)
    playbook.parent.mkdir(parents=True)
    inventory.parent.mkdir(parents=True)
    fleet.write_text(
        yaml.safe_dump(
            {
                "servers": [
                    {
                        "id": "mcp-staging-01",
                        "environment": "staging",
                    }
                ]
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    playbook.write_text("- hosts: application\n  tasks: []\n", encoding="utf-8")
    inventory.write_text("all:\n  hosts: {}\n", encoding="utf-8")
    return fleet, playbook, inventory


def test_configuration_plan_is_deterministic_and_binds_exact_server(tmp_path: Path) -> None:
    fleet, playbook, inventory = _fixture_files(tmp_path)
    kwargs = {
        "repository_root": tmp_path,
        "repository_revision": "a" * 40,
        "fleet_path": fleet,
        "playbook_path": playbook,
        "inventory_path": inventory,
        "environment": "staging",
        "server_id": "mcp-staging-01",
    }
    first = build_configuration_plan(**kwargs)
    second = build_configuration_plan(**kwargs)
    assert first == second
    assert first["target"] == {
        "limit": "mcp-staging-01",
        "server_id": "mcp-staging-01",
        "environment_wide": False,
    }
    assert first["plan_digest"].startswith("sha256:")


def test_configuration_plan_blocks_implicit_environment_wide_scope(tmp_path: Path) -> None:
    fleet, playbook, inventory = _fixture_files(tmp_path)
    with pytest.raises(AuthorizationError, match="explicit allow-environment-wide"):
        build_configuration_plan(
            repository_root=tmp_path,
            repository_revision="b" * 40,
            fleet_path=fleet,
            playbook_path=playbook,
            inventory_path=inventory,
            environment="staging",
        )


def test_configuration_plan_rejects_server_from_other_environment(tmp_path: Path) -> None:
    fleet, playbook, inventory = _fixture_files(tmp_path)
    with pytest.raises(AuthorizationError, match="selected environment"):
        build_configuration_plan(
            repository_root=tmp_path,
            repository_revision="c" * 40,
            fleet_path=fleet,
            playbook_path=playbook,
            inventory_path=inventory,
            environment="production",
            server_id="mcp-staging-01",
        )

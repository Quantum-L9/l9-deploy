"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests, workflows]
tags: [L9_TEST, adopted-host, fail-closed]
owner: platform
status: active
--- /L9_META ---
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_release_workflow_does_not_auto_authorize_adopted_host_mutation() -> None:
    workflow = (ROOT / ".github/workflows/deploy-dispatch.yml").read_text(encoding="utf-8")
    assert "--allow-adopted-host-mutation" not in workflow


def test_runtime_configuration_fails_before_roles_on_adopted_hosts() -> None:
    playbook = (ROOT / "ansible/playbooks/configure-runtime.yml").read_text(encoding="utf-8")
    assert "Refuse normal host configuration on adopted servers" in playbook
    assert "l9_lifecycle" in playbook
    assert "roles: [docker, caddy, conformance]" in playbook


def test_caddy_role_refuses_to_own_adopted_host_edge() -> None:
    role = (ROOT / "ansible/roles/caddy/tasks/main.yml").read_text(encoding="utf-8")
    assert "Refuse Caddy ownership on adopted hosts" in role
    assert "l9_lifecycle" in role
    assert "overwrite /etc/caddy/Caddyfile" in role

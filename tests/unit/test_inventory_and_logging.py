"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests, unit]
tags: [L9_TEST, inventory, logging, boundaries]
owner: platform
status: active
--- /L9_META ---
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest
import yaml

from l9_deploy.errors import ContractError
from l9_deploy.inventory.generator import generate_ansible_inventory
from l9_deploy.inventory.loader import load_fleet
from l9_deploy.logging import JsonFormatter, configure_logging


def test_inventory_generation_is_deterministic_private_and_role_grouped(
    tmp_path: Path, deployment_context: dict[str, object]
) -> None:
    output = tmp_path / "inventory" / "hosts.yml"
    fleet = deployment_context["fleet"]
    assert isinstance(fleet, dict)

    first = generate_ansible_inventory(fleet, output)
    first_bytes = output.read_bytes()
    second = generate_ansible_inventory(fleet, output)

    assert first == second
    assert first_bytes == output.read_bytes()
    assert output.stat().st_mode & 0o777 == 0o640
    assert first["all"]["children"]["management"]["hosts"]["l9-deploy-01"][  # type: ignore[index]
        "ansible_host"
    ] == "10.90.1.10"
    children = first["all"]["children"]
    application_hosts = children["application"]["hosts"]
    assert application_hosts["seo-staging-01"]["l9_environment"] == "staging"


def test_fleet_loader_validates_schema_and_rejects_non_object(
    tmp_path: Path, deployment_context: dict[str, object], schema_registry
) -> None:  # type: ignore[no-untyped-def]
    fleet_path = tmp_path / "fleet.yaml"
    fleet_path.write_text(
        yaml.safe_dump(deployment_context["fleet"], sort_keys=False),
        encoding="utf-8",
    )
    loaded = load_fleet(fleet_path, schema_registry)
    assert loaded["schema"] == "l9.fleet-inventory/v1"

    invalid = tmp_path / "invalid.yaml"
    invalid.write_text("- not\n- an\n- object\n", encoding="utf-8")
    with pytest.raises(ContractError, match="must be an object"):
        load_fleet(invalid, schema_registry)


def test_json_logging_configuration_is_explicit_and_secret_safe() -> None:
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    original_level = root.level
    try:
        configure_logging("debug", json_output=True)
        assert root.level == logging.DEBUG
        assert len(root.handlers) == 1
        formatter = root.handlers[0].formatter
        assert isinstance(formatter, JsonFormatter)

        record = logging.LogRecord(
            "l9.test",
            logging.INFO,
            __file__,
            1,
            "deployment accepted",
            (),
            None,
        )
        context = {"token": "frontier-secret", "request_id": "req-1"}
        record.context = context  # type: ignore[attr-defined]
        payload = json.loads(formatter.format(record))
        assert payload == {
            "context": {"request_id": "req-1", "token": "[REDACTED]"},
            "level": "INFO",
            "logger": "l9.test",
            "message": "deployment accepted",
        }
    finally:
        root.handlers.clear()
        root.handlers.extend(original_handlers)
        root.setLevel(original_level)

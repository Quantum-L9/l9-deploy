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
import os
from pathlib import Path

import pytest
import yaml

from l9_deploy.errors import ContractError
from l9_deploy.inventory.generator import _is_valid_public_hostname, generate_ansible_inventory
from l9_deploy.inventory.loader import load_fleet
from l9_deploy.logging import JsonFormatter, configure_logging

ROOT = Path(__file__).resolve().parents[2]


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
    assert (
        first["all"]["children"]["management"]["hosts"]["l9-deploy-01"][  # type: ignore[index]
            "ansible_host"
        ]
        == "10.90.1.10"
    )
    children = first["all"]["children"]
    application_hosts = children["application"]["hosts"]
    assert application_hosts["seo-staging-01"]["l9_environment"] == "staging"
    assert application_hosts["seo-staging-01"]["l9_lifecycle"] == "managed"


def _bind_profile(profile_root: Path, project_id: str, registered_path: str, source: Path) -> Path:
    target = profile_root / project_id / registered_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())
    return target


def test_cognitive_runtime_adopts_c1_without_claiming_caddy_ownership(
    tmp_path: Path, container_service_profile: dict[str, object]
) -> None:
    fleet = yaml.safe_load((ROOT / "fleet/registry.yaml").read_text(encoding="utf-8"))
    project = next(item for item in fleet["projects"] if item["id"] == "l9-cognitive-runtime")
    assert project["profile_path"] == ".l9/deployment.yaml"
    assert project["environments"]["staging"]["server_ids"] == ["c1"]
    assert project["environments"]["staging"]["public_hostnames"] == [
        "mcp-staging.quantumaipartners.com"
    ]

    # No profile bound: the adopted host renders without edge configuration and the
    # unbound ingress is recorded as blocked rather than read from this checkout.
    inventory = generate_ansible_inventory(fleet, tmp_path / "unbound.yml")
    host = inventory["all"]["children"]["application"]["hosts"]["c1"]
    assert host["ansible_host"] == "46.62.243.82"
    assert host["ansible_user"] == "root"
    assert host["l9_lifecycle"] == "adopted"
    assert host["l9_caddy_sites"] == []
    assert inventory["all"]["vars"]["l9_public_ingress_blocked"] == [
        {
            "environment": "staging",
            "project_id": "l9-cognitive-runtime",
            "reason": "consumer deployment profile is not bound",
        }
    ]

    # The consumer's source-owned profile, materialized under a profile root at its
    # registered path, binds the ingress; C1 still receives no Caddy ownership.
    profile_root = tmp_path / "profiles"
    source = tmp_path / "source-profile.yaml"
    source.write_text(yaml.safe_dump(container_service_profile, sort_keys=False), encoding="utf-8")
    _bind_profile(profile_root, "l9-cognitive-runtime", ".l9/deployment.yaml", source)
    bound = generate_ansible_inventory(fleet, tmp_path / "bound.yml", profile_root)
    assert "vars" not in bound["all"]
    assert bound["all"]["children"]["application"]["hosts"]["c1"]["l9_caddy_sites"] == []


def test_registered_profiles_are_source_owned_not_platform_mirrors() -> None:
    fleet = yaml.safe_load((ROOT / "fleet/registry.yaml").read_text(encoding="utf-8"))
    for project in fleet["projects"]:
        assert not project["profile_path"].startswith("integrations/"), project["id"]
        # A registered path never resolves to a document in this checkout, so no
        # code path can fall back to a platform-authored copy.
        assert not (ROOT / project["profile_path"]).exists(), project["id"]

    # No platform-local profile document may stand in for a registered project:
    # profile authority is the consumer's own source at the request's commit.
    # seo-bot keeps its pre-adoption fixture only while Quantum-L9/SEO-Bot publishes
    # no consumer-owned profile; the fixture is test input and is never registered.
    pending_consumer_profiles = {"seo-bot"}
    registered = {project["id"] for project in fleet["projects"]}
    mirrors: dict[str, str] = {}
    for directory, subdirectories, files in os.walk(ROOT):
        subdirectories[:] = [
            name for name in subdirectories if not name.startswith(".") and name != "templates"
        ]
        for name in files:
            if not name.endswith((".yaml", ".yml")):
                continue
            path = Path(directory) / name
            text = path.read_text(encoding="utf-8")
            if "l9.deployment-profile/v1" not in text:
                continue
            document = yaml.safe_load(text)
            project_id = document.get("project", {}).get("id") if document else None
            if project_id in registered:
                mirrors[project_id] = str(path.relative_to(ROOT))
    assert set(mirrors) <= pending_consumer_profiles, mirrors


def _managed_public_fleet(deployment_context: dict[str, object]) -> dict[str, object]:
    fleet = json.loads(json.dumps(deployment_context["fleet"]))
    project = fleet["projects"][0]
    project["environments"]["staging"]["public_hostnames"] = ["seo-staging.example.com"]
    return fleet


def _public_profile(deployment_context: dict[str, object], tmp_path: Path) -> Path:
    profile = json.loads(json.dumps(deployment_context["profile"]))
    profile["network"]["public_ingress"] = {
        "enabled": True,
        "hostnames": ["seo-staging.example.com"],
        "tls": "automatic",
    }
    source = tmp_path / "public-profile.yaml"
    source.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")
    return source


def test_managed_public_ingress_without_bound_profile_is_refused(
    tmp_path: Path, deployment_context: dict[str, object]
) -> None:
    fleet = _managed_public_fleet(deployment_context)
    output = tmp_path / "hosts.yml"
    # Rendering the managed host without this project's site would rewrite its
    # Caddy configuration; the generator refuses instead of inventing or dropping it.
    with pytest.raises(ContractError, match="requires the consumer's source-bound"):
        generate_ansible_inventory(fleet, output)
    with pytest.raises(ContractError, match="requires the consumer's source-bound"):
        generate_ansible_inventory(fleet, output, tmp_path / "empty-profile-root")
    assert not output.exists()


def test_managed_public_ingress_projects_only_the_bound_profile(
    tmp_path: Path, deployment_context: dict[str, object]
) -> None:
    fleet = _managed_public_fleet(deployment_context)
    profile_root = tmp_path / "profiles"
    registered = fleet["projects"][0]["profile_path"]  # type: ignore[index]
    _bind_profile(
        profile_root, "seo-bot", registered, _public_profile(deployment_context, tmp_path)
    )
    inventory = generate_ansible_inventory(fleet, tmp_path / "hosts.yml", profile_root)
    port = deployment_context["profile"]["runtime"]["container_port"]  # type: ignore[index]
    assert inventory["all"]["children"]["application"]["hosts"]["seo-staging-01"][
        "l9_caddy_sites"
    ] == [
        {
            "environment": "staging",
            "hostname": "seo-staging.example.com",
            "project_id": "seo-bot",
            "upstream": f"127.0.0.1:{port}",
        }
    ]


def test_inventory_profile_root_rejects_symlinked_material(
    tmp_path: Path, deployment_context: dict[str, object]
) -> None:
    from l9_deploy.errors import AuthorizationError

    fleet = _managed_public_fleet(deployment_context)
    profile_root = tmp_path / "profiles"
    registered = fleet["projects"][0]["profile_path"]  # type: ignore[index]
    link = profile_root / "seo-bot" / registered
    link.parent.mkdir(parents=True)
    link.symlink_to(_public_profile(deployment_context, tmp_path))
    with pytest.raises(AuthorizationError, match="crosses a symlink"):
        generate_ansible_inventory(fleet, tmp_path / "hosts.yml", profile_root)


@pytest.mark.parametrize(
    ("hostname", "expected"),
    [
        ("mcp-staging.quantumaipartners.com", True),
        ("a-b.example.com", True),
        ("localhost", False),
        ("Upper.example.com", False),
        ("-edge.example.com", False),
        ("edge-.example.com", False),
        ("edge..example.com", False),
        ("edge_example.com", False),
        (f"{'a' * 64}.example.com", False),
        (f"{'a' * 250}.com", False),
    ],
)
def test_public_hostname_validation_is_bounded_and_deterministic(
    hostname: str, expected: bool
) -> None:
    assert _is_valid_public_hostname(hostname) is expected


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

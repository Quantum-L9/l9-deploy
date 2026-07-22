"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests, fixtures]
tags: [L9_TEST, canonical-evidence]
owner: platform
status: active
--- /L9_META ---
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
import yaml

from l9_deploy.canonical import file_sha256, sha256_digest
from l9_deploy.contracts.validator import SchemaRegistry

REPO_ROOT = Path(__file__).resolve().parents[1]


class FakeBundleValidator:
    def __init__(self) -> None:
        self.calls: list[tuple[Path, str]] = []

    def validate(self, bundle: Path, minimum_sdk_version: str) -> None:
        assert bundle.is_file()
        self.calls.append((bundle, minimum_sdk_version))


@pytest.fixture
def schema_registry() -> SchemaRegistry:
    return SchemaRegistry(REPO_ROOT / "schemas" / "v1")


@pytest.fixture
def profile() -> dict[str, Any]:
    value = yaml.safe_load(
        (REPO_ROOT / "integrations/consumers/seo-bot.deployment.yaml").read_text(encoding="utf-8")
    )
    assert isinstance(value, dict)
    value = copy.deepcopy(value)
    value["health"]["post_deploy"] = {
        "type": "command",
        "command": ["true"],
        "timeout_seconds": 5,
        "attempts": 1,
        "interval_seconds": 1,
    }
    value["health"]["startup"] = copy.deepcopy(value["health"]["post_deploy"])
    return value


@pytest.fixture
def deployment_context(tmp_path: Path, profile: dict[str, Any]) -> dict[str, Any]:
    profile_path = tmp_path / "profiles" / "seo-bot.yaml"
    profile_path.parent.mkdir(parents=True)
    profile_path.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")
    profile_digest = file_sha256(profile_path)
    fleet: dict[str, Any] = {
        "schema": "l9.fleet-inventory/v1",
        "management": {
            "runner_server_id": "l9-deploy-01",
            "private_cidr": "10.90.1.0/24",
        },
        "environments": {
            "management": {
                "approval_required": True,
                "concurrency_group": "l9-management",
                "allowed_source_refs": ["refs/heads/main"],
            },
            "staging": {
                "approval_required": False,
                "concurrency_group": "l9-staging",
                "allowed_source_refs": ["refs/heads/main"],
            },
            "production": {
                "approval_required": True,
                "concurrency_group": "l9-production",
                "allowed_source_refs": ["refs/tags/v*"],
            },
        },
        "servers": [
            {
                "schema": "l9.server-profile/v1",
                "id": "l9-deploy-01",
                "environment": "management",
                "provider": "hetzner",
                "private_ip": "10.90.1.10",
                "public_ip": None,
                "ssh": {"user": "l9deploy", "port": 22},
                "roles": ["management"],
                "labels": {"managed_by": "l9-deployment-platform"},
                "conformance": {"profile": "management-runner", "max_age_hours": 24},
            },
            {
                "schema": "l9.server-profile/v1",
                "id": "seo-staging-01",
                "environment": "staging",
                "provider": "hetzner",
                "private_ip": "10.90.10.11",
                "public_ip": None,
                "ssh": {"user": "l9deploy", "port": 22},
                "roles": ["application"],
                "labels": {"managed_by": "l9-deployment-platform"},
                "conformance": {"profile": "application", "max_age_hours": 24},
            },
        ],
        "projects": [
            {
                "id": "seo-bot",
                "repository": "Quantum-L9/SEO-Bot",
                "profile_path": "profiles/seo-bot.yaml",
                "environments": {
                    "staging": {
                        "server_ids": ["seo-staging-01"],
                        "infisical_environment": "staging",
                    }
                },
            }
        ],
    }
    image_digest = "sha256:" + "a" * 64
    run_id = 1234
    evidence_root = tmp_path / "canonical-evidence"
    evidence_root.mkdir()
    bundle_path = evidence_root / "finding-bundle.json"
    bundle_path.write_text(
        json.dumps(
            {
                "schema": "l9.finding-bundle/v1",
                "schema_version": "1.0.0",
                "SDK_version": "1.0.0",
                "source_revision": "b" * 40,
                "findings": [],
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    bundle_digest = file_sha256(bundle_path)
    gate_binding: dict[str, Any] = {
        "schema": "l9.ci-gate-binding/v1",
        "status": "PASS",
        "source": {
            "repository": "Quantum-L9/SEO-Bot",
            "commit_sha": "b" * 40,
            "ref": "refs/heads/main",
        },
        "canonical": {
            "bundle_digest": bundle_digest,
            "schema_version": "1.0.0",
            "sdk_version": "1.0.0",
        },
        "workflow": {"artifact_name": f"l9-release-evidence-{run_id}"},
    }
    gate_path = evidence_root / "ci-gate-binding.json"
    gate_path.write_text(
        json.dumps(gate_binding, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    gate_digest = file_sha256(gate_path)

    artifact_binding: dict[str, Any] = {
        "schema": "l9.release-artifact-binding/v1",
        "binding_id": str(uuid4()),
        "source": {
            "repository": "Quantum-L9/SEO-Bot",
            "commit_sha": "b" * 40,
            "ref": "refs/heads/main",
            "run_id": run_id,
        },
        "artifact": {
            "image_ref": f"ghcr.io/quantum-l9/seo-bot@{image_digest}",
            "digest": image_digest,
        },
        "canonical": {
            "gate_binding_path": "ci-gate-binding.json",
            "gate_binding_digest": gate_digest,
            "bundle_path": "finding-bundle.json",
            "bundle_digest": bundle_digest,
        },
        "workflow": {
            "repository": "Quantum-L9/SEO-Bot",
            "workflow_ref": "Quantum-L9/SEO-Bot/.github/workflows/release.yml@refs/heads/main",
            "run_id": run_id,
            "artifact_name": f"l9-release-evidence-{run_id}",
        },
        "created_at": "2026-07-21T12:00:00Z",
    }
    artifact_binding["binding_digest"] = sha256_digest(artifact_binding)
    artifact_binding_path = evidence_root / "release-artifact-binding.json"
    artifact_binding_path.write_text(
        json.dumps(artifact_binding, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    artifact_binding_digest = file_sha256(artifact_binding_path)

    request: dict[str, Any] = {
        "schema": "l9.deployment-request/v1",
        "request_id": str(uuid4()),
        "idempotency_key": "seo-bot-staging-0001",
        "source": {
            "repository": "Quantum-L9/SEO-Bot",
            "commit_sha": "b" * 40,
            "ref": "refs/heads/main",
            "run_id": run_id,
        },
        "artifact": {
            "architecture": "linux/amd64",
            "image": "ghcr.io/quantum-l9/seo-bot",
            "digest": image_digest,
            "image_ref": f"ghcr.io/quantum-l9/seo-bot@{image_digest}",
        },
        "profile": {"path": "profiles/seo-bot.yaml", "digest": profile_digest},
        "evidence": {
            "schema": "l9.release-evidence-reference/v1",
            "schema_version": "1.0.0",
            "sdk_version": "1.0.0",
            "bundle_digest": bundle_digest,
            "gate_binding_digest": gate_digest,
            "artifact_binding_digest": artifact_binding_digest,
            "workflow_run_id": run_id,
            "artifact_name": f"l9-release-evidence-{run_id}",
            "bundle_path": "finding-bundle.json",
            "gate_binding_path": "ci-gate-binding.json",
            "artifact_binding_path": "release-artifact-binding.json",
            "provenance_reference": "oci://ghcr.io/quantum-l9/seo-bot@" + image_digest,
            "sbom_reference": "artifact://sbom/1234",
        },
        "target": {"environment": "staging"},
        "requested_by": "release-broker",
        "requested_at": "2026-07-21T12:00:00Z",
    }
    return {
        "root": tmp_path,
        "profile_path": profile_path,
        "profile": profile,
        "fleet": fleet,
        "request": request,
        "evidence_root": evidence_root,
        "bundle_validator": FakeBundleValidator(),
    }


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]

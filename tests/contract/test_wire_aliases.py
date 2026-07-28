"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests, contracts]
tags: [L9_TEST, wire-alias, schema-parity, warning-free]
owner: platform
status: active
--- /L9_META ---
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from l9_deploy.canonical import sha256_digest
from l9_deploy.contracts.catalog import WIRE_CONTRACTS
from l9_deploy.contracts.loader import load_document
from l9_deploy.contracts.models import (
    ApprovalReceipt,
    DeploymentPlan,
    DeploymentProfile,
    DeploymentReceipt,
    DeploymentRequest,
    FleetInventory,
    IdempotencyDocument,
    ReceiptStep,
    ReleaseEvidenceReference,
    RepositoryReleaseReceipt,
    ServerProfile,
)
from l9_deploy.evidence.receipts import create_deployment_receipt
from l9_deploy.planning.planner import build_plan
from l9_deploy.requests.verifier import verify_request

ROOT = Path(__file__).resolve().parents[2]


def _approval_document() -> dict[str, Any]:
    value: dict[str, Any] = {
        "schema": "l9.approval-receipt/v1",
        "approval_id": "c6969d36-a4dd-4a01-89b1-64ec114cb9fd",
        "request_id": "0b6d09a6-1a48-4c84-87af-6f2902fcd59f",
        "environment": "production",
        "plan_digest": "sha256:" + "a" * 64,
        "requester": "requester",
        "approved": True,
        "approved_by": "reviewer",
        "approved_at": "2026-07-21T12:00:01Z",
        "authorization_method": "github_protected_environment_review",
        "workflow": {
            "repository": "Quantum-L9/l9-deployment-platform",
            "run_id": 123,
            "run_attempt": 1,
            "job_id": 456,
            "workflow_ref": (
                "Quantum-L9/l9-deployment-platform/.github/workflows/"
                "deploy-dispatch.yml@refs/heads/main"
            ),
            "environment": "production",
            "approval_api_url": (
                "https://api.github.com/repos/Quantum-L9/l9-deployment-platform/"
                "actions/runs/123/approvals"
            ),
            "approval_record_digest": "sha256:" + "b" * 64,
        },
    }
    value["receipt_digest"] = sha256_digest(value)
    return value


def _wire_documents(
    deployment_context: dict[str, Any], schema_registry: Any
) -> dict[type[Any], dict[str, Any]]:
    verified = verify_request(
        deployment_context["request"],
        deployment_context["fleet"],
        schema_registry,
        deployment_context["root"],
        evidence_root=deployment_context["evidence_root"],
        bundle_validator=deployment_context["bundle_validator"],
    )
    plan = build_plan(verified, created_at="2026-07-21T12:01:00Z")
    receipt = create_deployment_receipt(
        request_id="request-001",
        project_id="seo-bot",
        environment="staging",
        status="PASS",
        started_at="2026-07-21T12:00:00Z",
        source_commit_sha="a" * 40,
        image_ref="ghcr.io/quantum-l9/seo-bot@sha256:" + "b" * 64,
        plan_digest="sha256:" + "c" * 64,
        previous_release=None,
        steps=[ReceiptStep(step_id="verify", kind="verify", status="PASS")],
    )
    return {
        ReleaseEvidenceReference: deepcopy(deployment_context["request"]["evidence"]),
        DeploymentRequest: deepcopy(deployment_context["request"]),
        DeploymentProfile: deepcopy(deployment_context["profile"]),
        ServerProfile: deepcopy(deployment_context["fleet"]["servers"][0]),
        FleetInventory: deepcopy(deployment_context["fleet"]),
        DeploymentPlan: plan.model_dump(mode="json", by_alias=True),
        ApprovalReceipt: _approval_document(),
        IdempotencyDocument: {
            "schema": "l9.idempotency-store/v1",
            "entries": {},
        },
        RepositoryReleaseReceipt: {
            "schema": "l9.repository-release-receipt/v1",
            "repository": "Quantum-L9/l9-deployment-platform",
            "version": "0.1.5",
            "archive_name": "l9-deployment-platform-v0.1.5.zip",
            "archive_sha256": "sha256:" + "d" * 64,
            "archive_size_bytes": 123456,
            "archive_files": 350,
            "source_manifest_sha256": "sha256:" + "e" * 64,
            "source_date_epoch": 1784678400,
            "built_at": "2026-07-22T00:00:00Z",
            "receipt_digest": "sha256:" + "f" * 64,
        },
        DeploymentReceipt: receipt.model_dump(mode="json", by_alias=True),
    }


def test_wire_contracts_round_trip_without_runtime_name_leak(
    deployment_context: dict[str, Any], schema_registry: Any
) -> None:
    documents = _wire_documents(deployment_context, schema_registry)
    for definition in WIRE_CONTRACTS:
        wire = documents[definition.model]
        contract = definition.model.model_validate(wire)

        assert contract.schema_id == definition.schema_id
        assert contract.model_dump(mode="json", by_alias=True, exclude_unset=True) == wire
        default_dump = contract.model_dump(mode="json")
        assert "schema" in default_dump
        assert "schema_id" not in default_dump


def test_runtime_field_name_is_rejected_at_wire_boundary(
    deployment_context: dict[str, Any], schema_registry: Any
) -> None:
    documents = _wire_documents(deployment_context, schema_registry)
    for definition in WIRE_CONTRACTS:
        invalid = deepcopy(documents[definition.model])
        invalid["schema_id"] = invalid.pop("schema")
        with pytest.raises(ValidationError):
            definition.model.model_validate(invalid)


def test_exported_model_schemas_use_published_wire_names() -> None:
    for definition in WIRE_CONTRACTS:
        generated = definition.model.model_json_schema(by_alias=True)
        committed = load_document(ROOT / "schemas/v1" / definition.schema_file)

        assert "schema" in generated["properties"]
        assert "schema_id" not in generated["properties"]
        assert generated["properties"]["schema"]["const"] == definition.schema_id
        assert committed["properties"]["schema"]["const"] == definition.schema_id
        assert set(generated["properties"]) == set(committed["properties"])
        assert set(generated["required"]) == set(committed["required"])


def _load_fast_contract_scanner() -> Any:
    import importlib.util
    import sys

    scripts = ROOT / "scripts"
    path = scripts / "fast-contract-scan.py"
    sys.path.insert(0, str(scripts))
    spec = importlib.util.spec_from_file_location("l9_fast_contract_scan_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(scripts))
    return module


def test_contract_scanner_allows_only_schema_wire_alias(tmp_path: Path) -> None:
    scanner = _load_fast_contract_scanner()
    source = tmp_path / "src/l9_deploy/contracts"
    source.mkdir(parents=True)
    (source / "models.py").write_text(
        "from typing import Literal\n"
        "from pydantic import Field\n"
        'schema_id: Literal["l9.example/v1"] = Field(alias="schema")\n',
        encoding="utf-8",
    )
    assert scanner.scan(tmp_path) == []


def test_contract_scanner_rejects_unrelated_alias(tmp_path: Path) -> None:
    scanner = _load_fast_contract_scanner()
    source = tmp_path / "src/l9_deploy/contracts"
    source.mkdir(parents=True)
    (source / "models.py").write_text(
        'from pydantic import Field\nruntime_name: str = Field(alias="wire_name")\n',
        encoding="utf-8",
    )
    findings = scanner.scan(tmp_path)
    assert [finding.rule_id for finding in findings] == ["NAME-001"]


def test_contract_scanner_rejects_pass_only_function(tmp_path: Path) -> None:
    scanner = _load_fast_contract_scanner()
    source = tmp_path / "src"
    source.mkdir(parents=True)
    (source / "stub.py").write_text(
        "def unfinished() -> None:\n    pass\n",
        encoding="utf-8",
    )
    findings = scanner.scan(tmp_path)
    assert [finding.rule_id for finding in findings] == ["STUB-007"]

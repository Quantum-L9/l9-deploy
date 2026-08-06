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
from jsonschema import Draft202012Validator

from l9_deploy.contracts.compatibility import require_supported_schema
from l9_deploy.contracts.loader import load_document
from l9_deploy.errors import CompatibilityError, ContractError

ROOT = Path(__file__).resolve().parents[2]


def test_all_json_schemas_are_meta_schema_valid() -> None:
    for path in sorted((ROOT / "schemas/v1").glob("*.schema.json")):
        Draft202012Validator.check_schema(load_document(path))


def test_all_declared_probe_examples_validate(
    schema_registry,
) -> None:  # type: ignore[no-untyped-def]
    for path in sorted((ROOT / "deployment/probes").glob("*.yaml")):
        schema_registry.validate(load_document(path), "health-probe")


def test_profile_example_validates(schema_registry) -> None:  # type: ignore[no-untyped-def]
    document = load_document(ROOT / "integrations/consumers/seo-bot.deployment.yaml")
    schema_registry.validate(document, "deployment-profile")


def test_unknown_major_fails_closed() -> None:
    with pytest.raises(CompatibilityError):
        require_supported_schema("l9.deployment-request/v2")


def test_unknown_schema_fails_closed(schema_registry) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(ContractError):
        schema_registry.validate({}, "not-real")


def test_idempotency_schema_enforces_status_field_consistency(
    schema_registry,
) -> None:  # type: ignore[no-untyped-def]
    base = {
        "schema": "l9.idempotency-store/v1",
        "entries": {
            "request-1": {
                "request_digest": "sha256:" + "a" * 64,
                "status": "COMPLETE",
                "updated_at": "2026-07-21T00:00:00Z",
                "receipt_digest": "sha256:" + "b" * 64,
                "reason": None,
            }
        },
    }
    schema_registry.validate(base, "idempotency-store")

    invalid_complete = {
        **base,
        "entries": {
            "request-1": {
                **base["entries"]["request-1"],
                "receipt_digest": None,
            }
        },
    }
    with pytest.raises(ContractError):
        schema_registry.validate(invalid_complete, "idempotency-store")

    invalid_fail = {
        **base,
        "entries": {
            "request-1": {
                **base["entries"]["request-1"],
                "status": "FAIL",
                "receipt_digest": "sha256:" + "b" * 64,
                "reason": "failed",
            }
        },
    }
    with pytest.raises(ContractError):
        schema_registry.validate(invalid_fail, "idempotency-store")

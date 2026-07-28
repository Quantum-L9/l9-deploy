"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [authorization, evidence]
tags: [L9_CONTRACT, github-environment-approval]
owner: platform
status: active
--- /L9_META ---

Independent verification of GitHub protected-environment approval evidence.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path

from ..canonical import file_sha256, load_structured, sha256_digest
from ..contracts.models import ApprovalReceipt
from ..contracts.validator import SchemaRegistry
from ..errors import AuthorizationError, ContractError


def _object(path: Path) -> dict[str, object]:
    value = load_structured(path)
    if not isinstance(value, dict):
        raise ContractError(f"expected object document: {path}")
    return value


def _history_records(value: object) -> list[dict[str, object]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        records = value.get("reviews") or value.get("approvals")
        if isinstance(records, list):
            return [item for item in records if isinstance(item, dict)]
    raise AuthorizationError("GitHub approval history has an unsupported shape")


def _environment_names(record: dict[str, object]) -> set[str]:
    environments = record.get("environments")
    if not isinstance(environments, list):
        return set()
    names: set[str] = set()
    for environment in environments:
        if isinstance(environment, dict) and isinstance(environment.get("name"), str):
            names.add(environment["name"])
    return names


def _reviewer(record: dict[str, object]) -> str | None:
    user = record.get("user")
    if isinstance(user, dict) and isinstance(user.get("login"), str):
        return user["login"]
    return None


def _approved_at(record: dict[str, object]) -> str | None:
    for field in ("submitted_at", "approved_at", "created_at"):
        value = record.get(field)
        if isinstance(value, str) and value:
            return value
    return None


def _canonical_time(value: str) -> str:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise AuthorizationError("approval timestamp must include a timezone")
    return parsed.astimezone(UTC).isoformat().replace("+00:00", "Z")


def verify_approval_receipt(
    receipt_path: Path,
    approval_history_path: Path,
    registry: SchemaRegistry,
    *,
    request_id: str,
    requester: str,
    environment: str,
    plan_digest: str,
    expected_repository: str = "Quantum-L9/l9-deployment-platform",
    expected_run_id: int | None = None,
) -> ApprovalReceipt:
    receipt_document = _object(receipt_path)
    registry.validate(receipt_document, "approval-receipt")
    supplied_digest = receipt_document.get("receipt_digest")
    digest_input = deepcopy(receipt_document)
    digest_input.pop("receipt_digest", None)
    if supplied_digest != sha256_digest(digest_input):
        raise AuthorizationError("approval receipt digest is invalid")
    receipt = ApprovalReceipt.model_validate(receipt_document)

    if receipt.request_id != request_id:
        raise AuthorizationError("approval receipt request mismatch")
    if receipt.requester != requester:
        raise AuthorizationError("approval receipt requester mismatch")
    if receipt.environment != environment or receipt.workflow.environment != environment:
        raise AuthorizationError("approval receipt environment mismatch")
    if receipt.plan_digest != plan_digest:
        raise AuthorizationError("approval receipt plan mismatch")
    if receipt.workflow.repository != expected_repository:
        raise AuthorizationError("approval receipt repository mismatch")
    if expected_run_id is not None and receipt.workflow.run_id != expected_run_id:
        raise AuthorizationError("approval receipt workflow run mismatch")
    if receipt.workflow.approval_record_digest != file_sha256(approval_history_path):
        raise AuthorizationError("approval history digest mismatch")

    history = load_structured(approval_history_path)
    matched = False
    for record in _history_records(history):
        state = record.get("state")
        reviewer = _reviewer(record)
        approved_at = _approved_at(record)
        if (
            state == "approved"
            and environment in _environment_names(record)
            and reviewer == receipt.approved_by
            and approved_at is not None
            and _canonical_time(approved_at) == _canonical_time(receipt.approved_at.isoformat())
        ):
            matched = True
            break
    if not matched:
        raise AuthorizationError("approval receipt is not backed by GitHub approval history")
    return receipt

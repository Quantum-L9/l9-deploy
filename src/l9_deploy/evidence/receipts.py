"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [evidence, contracts]
tags: [L9_CONTRACT, receipt, typed-steps]
owner: platform
status: active
--- /L9_META ---
"""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from uuid import uuid4

from pydantic import JsonValue

from ..canonical import sha256_digest
from ..contracts.models import DeploymentReceipt, ReceiptArtifact, ReceiptStep, ReleaseState
from ..redaction import redact


def _canonical_timestamp(value: str) -> str:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("receipt timestamps must include a timezone")
    return parsed.astimezone(UTC).isoformat().replace("+00:00", "Z")


def create_deployment_receipt(
    *,
    request_id: str,
    project_id: str,
    environment: str,
    status: str,
    started_at: str,
    source_commit_sha: str,
    image_ref: str,
    plan_digest: str,
    previous_release: ReleaseState | None,
    steps: list[ReceiptStep],
    artifacts: list[ReceiptArtifact] | None = None,
    unknowns: list[str] | None = None,
) -> DeploymentReceipt:
    step_documents = [item.model_dump(mode="json", by_alias=True) for item in steps]
    artifact_documents = [item.model_dump(mode="json", by_alias=True) for item in artifacts or []]
    payload: dict[str, object] = {
        "schema": "l9.deployment-receipt/v1",
        "receipt_id": str(uuid4()),
        "request_id": request_id,
        "project_id": project_id,
        "environment": environment,
        "status": status,
        "started_at": _canonical_timestamp(started_at),
        "completed_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source_commit_sha": source_commit_sha,
        "image_ref": image_ref,
        "plan_digest": plan_digest,
        "previous_release": (
            previous_release.model_dump(mode="json", by_alias=True) if previous_release else None
        ),
        "steps": redact(step_documents),
        "artifacts": redact(artifact_documents),
        "unknowns": unknowns or [],
    }
    payload["receipt_digest"] = sha256_digest(payload)
    return DeploymentReceipt.model_validate(payload)


def create_receipt(
    schema: str,
    *,
    request_id: str,
    project_id: str,
    environment: str,
    status: str,
    started_at: str,
    source_commit_sha: str,
    image_ref: str,
    plan_digest: str,
    previous_release: dict[str, JsonValue] | None,
    steps: list[dict[str, JsonValue]],
    artifacts: list[dict[str, JsonValue]] | None = None,
    unknowns: list[str] | None = None,
) -> dict[str, object]:
    receipt: dict[str, object] = {
        "schema": schema,
        "receipt_id": str(uuid4()),
        "request_id": request_id,
        "project_id": project_id,
        "environment": environment,
        "status": status,
        "started_at": _canonical_timestamp(started_at),
        "completed_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source_commit_sha": source_commit_sha,
        "image_ref": image_ref,
        "plan_digest": plan_digest,
        "previous_release": redact(previous_release),
        "steps": redact(steps),
        "artifacts": redact(artifacts or []),
        "unknowns": unknowns or [],
    }
    receipt["receipt_digest"] = sha256_digest(receipt)
    return receipt


def verify_receipt_digest(receipt: dict[str, object]) -> bool:
    supplied = receipt.get("receipt_digest")
    if not isinstance(supplied, str):
        return False
    digest_input = deepcopy(receipt)
    del digest_input["receipt_digest"]
    return supplied == sha256_digest(digest_input)

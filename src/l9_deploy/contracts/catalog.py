"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [contracts]
tags: [L9_CONTRACT, wire-catalog, schema-parity]
owner: platform
status: active
--- /L9_META ---

Versioned catalog linking self-describing wire identities to runtime DTO projections.
"""
from __future__ import annotations

from dataclasses import dataclass

from .models import (
    ApprovalReceipt,
    DeploymentPlan,
    DeploymentProfile,
    DeploymentReceipt,
    DeploymentRequest,
    FleetInventory,
    FrozenModel,
    IdempotencyDocument,
    ReleaseEvidenceReference,
    RepositoryReleaseReceipt,
    ServerProfile,
)


@dataclass(frozen=True, slots=True)
class WireContractDefinition:
    name: str
    schema_id: str
    schema_file: str
    model: type[FrozenModel]


WIRE_CONTRACTS: tuple[WireContractDefinition, ...] = (
    WireContractDefinition(
        name="release-evidence-reference",
        schema_id="l9.release-evidence-reference/v1",
        schema_file="release-evidence-reference.schema.json",
        model=ReleaseEvidenceReference,
    ),
    WireContractDefinition(
        name="deployment-request",
        schema_id="l9.deployment-request/v1",
        schema_file="deployment-request.schema.json",
        model=DeploymentRequest,
    ),
    WireContractDefinition(
        name="deployment-profile",
        schema_id="l9.deployment-profile/v1",
        schema_file="deployment-profile.schema.json",
        model=DeploymentProfile,
    ),
    WireContractDefinition(
        name="server-profile",
        schema_id="l9.server-profile/v1",
        schema_file="server-profile.schema.json",
        model=ServerProfile,
    ),
    WireContractDefinition(
        name="fleet-inventory",
        schema_id="l9.fleet-inventory/v1",
        schema_file="fleet-inventory.schema.json",
        model=FleetInventory,
    ),
    WireContractDefinition(
        name="deployment-plan",
        schema_id="l9.deployment-plan/v1",
        schema_file="deployment-plan.schema.json",
        model=DeploymentPlan,
    ),
    WireContractDefinition(
        name="approval-receipt",
        schema_id="l9.approval-receipt/v1",
        schema_file="approval-receipt.schema.json",
        model=ApprovalReceipt,
    ),
    WireContractDefinition(
        name="idempotency-store",
        schema_id="l9.idempotency-store/v1",
        schema_file="idempotency-store.schema.json",
        model=IdempotencyDocument,
    ),
    WireContractDefinition(
        name="repository-release-receipt",
        schema_id="l9.repository-release-receipt/v1",
        schema_file="repository-release-receipt.schema.json",
        model=RepositoryReleaseReceipt,
    ),
    WireContractDefinition(
        name="deployment-receipt",
        schema_id="l9.deployment-receipt/v1",
        schema_file="deployment-receipt.schema.json",
        model=DeploymentReceipt,
    ),
)

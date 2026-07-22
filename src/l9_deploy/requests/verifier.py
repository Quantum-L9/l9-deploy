"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [authorization]
tags: [L9_CONTRACT, request-verification]
owner: platform
status: active
--- /L9_META ---
"""
from __future__ import annotations

import fnmatch
from pathlib import Path

from ..canonical import file_sha256, sha256_digest
from ..contracts.models import (
    DeploymentProfile,
    DeploymentRequest,
    FleetInventory,
    VerifiedRequest,
)
from ..contracts.validator import SchemaRegistry
from ..errors import AuthorizationError, ContractError
from ..evidence.ci import CanonicalBundleValidator, verify_canonical_release_evidence
from .allowlist import find_project, require_environment


def _source_ref_allowed(ref: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatchcase(ref, pattern) for pattern in patterns)


def verify_request(
    request_document: dict[str, object],
    fleet_document: FleetInventory | dict[str, object],
    registry: SchemaRegistry,
    repository_root: Path,
    *,
    evidence_root: Path,
    bundle_validator: CanonicalBundleValidator | None = None,
) -> VerifiedRequest:
    registry.validate(request_document, "deployment-request")
    request = DeploymentRequest.model_validate(request_document)
    if isinstance(fleet_document, FleetInventory):
        fleet = fleet_document
    else:
        registry.validate(fleet_document, "fleet-inventory")
        fleet = FleetInventory.model_validate(fleet_document)

    project = find_project(fleet, request.source.repository)
    project_environment = require_environment(project, request.target.environment)
    root = repository_root.resolve()
    profile_path = (root / project.profile_path).resolve()
    if profile_path != root and root not in profile_path.parents:
        raise AuthorizationError("registered deployment profile escapes repository root")
    if not profile_path.is_file():
        raise ContractError(f"registered deployment profile is missing: {profile_path}")
    profile_document = registry_document(profile_path)
    registry.validate(profile_document, "deployment-profile")
    profile = DeploymentProfile.model_validate(profile_document)

    if profile.project.id != project.id:
        raise AuthorizationError("deployment profile project id does not match fleet registration")
    if profile.project.repository != request.source.repository:
        raise AuthorizationError("deployment profile repository does not match request source")
    if profile.artifact.image != request.artifact.image:
        raise AuthorizationError("requested image repository is not allowed by deployment profile")
    actual_profile_digest = file_sha256(profile_path)
    if request.profile.digest != actual_profile_digest:
        raise AuthorizationError("deployment profile digest mismatch")
    if request.profile.path != project.profile_path:
        raise AuthorizationError("deployment profile path does not match fleet registration")

    verify_canonical_release_evidence(
        request,
        evidence_root,
        registry,
        bundle_validator=bundle_validator,
    )
    patterns = profile.policy.allowed_source_refs.get(request.target.environment, ())
    if not _source_ref_allowed(request.source.ref, patterns):
        raise AuthorizationError(
            f"source ref {request.source.ref} is not allowed for {request.target.environment}"
        )
    return VerifiedRequest(
        document=request,
        project=project,
        environment=project_environment,
        profile=profile,
        fleet=fleet,
    )


def registry_document(path: Path) -> dict[str, object]:
    from ..contracts.loader import load_document

    value = load_document(path)
    if not isinstance(value, dict):
        raise ContractError(f"expected object document: {path}")
    return value


def request_digest(request: DeploymentRequest | dict[str, object]) -> str:
    value = (
        request.model_dump(mode="json", by_alias=True)
        if isinstance(request, DeploymentRequest)
        else request
    )
    return sha256_digest(value)

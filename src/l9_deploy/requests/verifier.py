"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [authorization]
tags: [L9_CONTRACT, request-verification]
owner: platform
status: active
--- /L9_META ---

Bind one deployment request to the consumer-authored deployment profile it names.

The profile bytes are never read from the l9-deploy checkout. The caller
materializes them from the exact source repository and immutable source commit
named by ``request.source`` (``deploy-dispatch.yml`` does this with the GitHub
contents API before ``scripts/prepare-deployment.py`` runs) into a dedicated
*profile root*. This module resolves the registered relative path inside that
root with path and symlink confinement, checks the request digest against the
materialized bytes before parsing them, and only then validates the document.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path, PurePosixPath

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


def _verify_public_ingress_alignment(
    profile: DeploymentProfile,
    fleet_hostnames: tuple[str, ...],
) -> None:
    ingress = profile.network.public_ingress
    profile_hostnames = set(ingress.hostnames)
    registered_hostnames = set(fleet_hostnames)
    if not profile_hostnames and not registered_hostnames:
        return
    if not ingress.enabled:
        raise AuthorizationError("fleet public hostnames require enabled public ingress")
    if profile.runtime.container_port is None:
        raise AuthorizationError("public ingress requires a container port")
    if not registered_hostnames:
        raise AuthorizationError("public ingress hostnames are not registered in the fleet")
    if not registered_hostnames.issubset(profile_hostnames):
        raise AuthorizationError("fleet public hostnames do not match deployment profile")


def resolve_registered_profile(profile_root: Path, relative_path: str) -> Path:
    """Return the materialized profile file for ``relative_path`` inside ``profile_root``.

    ``relative_path`` is the fleet-registered, consumer-repository-relative profile
    path. The result is confined to ``profile_root``: absolute paths, ``.``/``..``
    segments, symlinks on any component, and targets that resolve outside the root
    are rejected before any byte is read. A missing or non-regular file is a
    contract failure, never a reason to look anywhere else.
    """
    parts = PurePosixPath(relative_path).parts
    if (
        not parts
        or PurePosixPath(relative_path).is_absolute()
        or any(part in {".", ".."} for part in parts)
    ):
        raise AuthorizationError("registered deployment profile path is not confined")
    root = profile_root.resolve()
    candidate = root
    for part in parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise AuthorizationError(
                "registered deployment profile path crosses a symlink; "
                "only materialized source bytes are accepted"
            )
    resolved = candidate.resolve()
    if resolved == root or root not in resolved.parents:
        raise AuthorizationError("registered deployment profile escapes the profile root")
    if not candidate.is_file():
        raise ContractError(
            f"registered deployment profile is missing from the profile root: {relative_path}"
        )
    return candidate


def verify_request(
    request_document: dict[str, object],
    fleet_document: FleetInventory | dict[str, object],
    registry: SchemaRegistry,
    profile_root: Path,
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
    if request.profile.path != project.profile_path:
        raise AuthorizationError("deployment profile path does not match fleet registration")
    profile_path = resolve_registered_profile(profile_root, project.profile_path)
    # The requester's digest claim is checked against the materialized source bytes
    # before those bytes are parsed: an unclaimed document is never interpreted.
    if request.profile.digest != file_sha256(profile_path):
        raise AuthorizationError("deployment profile digest mismatch")
    profile_document = registry_document(profile_path)
    registry.validate(profile_document, "deployment-profile")
    profile = DeploymentProfile.model_validate(profile_document)

    if profile.project.id != project.id:
        raise AuthorizationError("deployment profile project id does not match fleet registration")
    if profile.project.repository != request.source.repository:
        raise AuthorizationError("deployment profile repository does not match request source")
    if profile.artifact.image != request.artifact.image:
        raise AuthorizationError("requested image repository is not allowed by deployment profile")
    _verify_public_ingress_alignment(profile, project_environment.public_hostnames)

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

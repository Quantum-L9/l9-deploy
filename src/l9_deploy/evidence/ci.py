"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [evidence, integration]
tags: [L9_CONTRACT, l9-ci-sdk, l9-ci-core]
owner: platform
status: active
--- /L9_META ---

Verify external CI gate evidence separately from the status-free OCI artifact binding.
"""

from __future__ import annotations

import shutil
from collections.abc import Sequence
from copy import deepcopy
from pathlib import Path
from typing import Protocol

from ..canonical import file_sha256, load_structured, sha256_digest
from ..contracts.models import DeploymentRequest
from ..contracts.validator import SchemaRegistry
from ..errors import AuthorizationError, ContractError
from ..subprocesses import run_command


class CanonicalBundleValidator(Protocol):
    def validate(self, bundle: Path, minimum_sdk_version: str) -> None: ...


class L9CiCliBundleValidator:
    def __init__(self, executable: str = "l9-ci") -> None:
        self.executable = executable

    def validate(self, bundle: Path, minimum_sdk_version: str) -> None:
        executable = shutil.which(self.executable)
        if executable is None:
            raise ContractError(
                "canonical l9-ci CLI is unavailable; evidence validation fails closed"
            )
        commands: Sequence[Sequence[str]] = (
            (executable, "bundle", "validate", str(bundle)),
            (
                executable,
                "compatibility",
                "check",
                "--bundle",
                str(bundle),
                "--minimum-SDK-version",
                minimum_sdk_version,
            ),
        )
        for command in commands:
            run_command(command, timeout=120)


def _object(path: Path) -> dict[str, object]:
    value = load_structured(path)
    if not isinstance(value, dict):
        raise ContractError(f"expected object document: {path}")
    return value


def _verify_document_digest(document: dict[str, object], field: str) -> None:
    supplied = document.get(field)
    if not isinstance(supplied, str):
        raise AuthorizationError(f"{field} is missing")
    digest_input = deepcopy(document)
    del digest_input[field]
    if supplied != sha256_digest(digest_input):
        raise AuthorizationError(f"{field} does not match document content")


def _confined(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if root not in path.parents:
        raise AuthorizationError("evidence paths must remain inside the downloaded artifact root")
    return path


def _mapping(document: dict[str, object], key: str) -> dict[str, object]:
    value = document.get(key)
    if not isinstance(value, dict):
        raise AuthorizationError(f"evidence {key} contract is invalid")
    return value


def verify_canonical_release_evidence(
    request: DeploymentRequest,
    evidence_root: Path,
    registry: SchemaRegistry,
    bundle_validator: CanonicalBundleValidator | None = None,
) -> None:
    reference = request.evidence
    root = evidence_root.resolve()
    bundle_path = _confined(root, reference.bundle_path)
    gate_path = _confined(root, reference.gate_binding_path)
    artifact_path = _confined(root, reference.artifact_binding_path)
    if not all(path.is_file() for path in (bundle_path, gate_path, artifact_path)):
        raise AuthorizationError("canonical evidence artifact is incomplete")

    gate = _object(gate_path)
    artifact_binding = _object(artifact_path)
    registry.validate(gate, "ci-gate-binding")
    registry.validate(artifact_binding, "release-artifact-binding")
    _verify_document_digest(artifact_binding, "binding_digest")

    gate_source = _mapping(gate, "source")
    gate_canonical = _mapping(gate, "canonical")
    gate_workflow = _mapping(gate, "workflow")
    artifact_source = _mapping(artifact_binding, "source")
    artifact = _mapping(artifact_binding, "artifact")
    artifact_canonical = _mapping(artifact_binding, "canonical")
    artifact_workflow = _mapping(artifact_binding, "workflow")

    pairs = (
        (gate.get("status"), "PASS", "external gate status"),
        (gate_source.get("repository"), request.source.repository, "gate source repository"),
        (gate_source.get("commit_sha"), request.source.commit_sha, "gate source commit"),
        (gate_source.get("ref"), request.source.ref, "gate source ref"),
        (gate_canonical.get("bundle_digest"), reference.bundle_digest, "gate bundle digest"),
        (gate_canonical.get("schema_version"), reference.schema_version, "schema version"),
        (gate_canonical.get("sdk_version"), reference.sdk_version, "SDK version"),
        (gate_workflow.get("artifact_name"), reference.artifact_name, "gate artifact name"),
        (
            artifact_source.get("repository"),
            request.source.repository,
            "artifact source repository",
        ),
        (artifact_source.get("commit_sha"), request.source.commit_sha, "artifact source commit"),
        (artifact_source.get("ref"), request.source.ref, "artifact source ref"),
        (artifact_source.get("run_id"), request.source.run_id, "artifact source run"),
        (artifact.get("image_ref"), request.artifact.image_ref, "image ref"),
        (artifact.get("digest"), request.artifact.digest, "image digest"),
        (artifact_canonical.get("gate_binding_path"), reference.gate_binding_path, "gate path"),
        (
            artifact_canonical.get("gate_binding_digest"),
            reference.gate_binding_digest,
            "gate digest",
        ),
        (artifact_canonical.get("bundle_path"), reference.bundle_path, "bundle path"),
        (artifact_canonical.get("bundle_digest"), reference.bundle_digest, "bundle digest"),
        (artifact_workflow.get("run_id"), reference.workflow_run_id, "workflow run"),
        (artifact_workflow.get("artifact_name"), reference.artifact_name, "release artifact name"),
    )
    for actual, expected, label in pairs:
        if actual != expected:
            raise AuthorizationError(f"canonical evidence {label} mismatch")

    if file_sha256(bundle_path) != reference.bundle_digest:
        raise AuthorizationError("canonical bundle file digest mismatch")
    if file_sha256(gate_path) != reference.gate_binding_digest:
        raise AuthorizationError("CI gate binding file digest mismatch")
    if file_sha256(artifact_path) != reference.artifact_binding_digest:
        raise AuthorizationError("release artifact binding file digest mismatch")

    validator = bundle_validator or L9CiCliBundleValidator()
    validator.validate(bundle_path, reference.sdk_version)

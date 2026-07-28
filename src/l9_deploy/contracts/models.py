"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [contracts]
tags: [L9_CONTRACT, deployment, pydantic]
owner: platform
status: active
--- /L9_META ---

Frozen Pydantic v2 contracts for deployment control-plane boundaries.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import PurePosixPath
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    StringConstraints,
    field_validator,
    model_validator,
)


PROJECT_ID_PATTERN = r"^[a-z][a-z0-9-]{1,63}$"
RELATIVE_PATH_PATTERN = r"^[A-Za-z0-9._/-]+$"
ENVIRONMENT_PATTERN = r"^[a-z][a-z0-9-]{1,31}$"
SHA256_PATTERN = r"^sha256:[a-f0-9]{64}$"

Sha256Digest = Annotated[str, StringConstraints(pattern=SHA256_PATTERN)]
IdempotencyKey = Annotated[str, StringConstraints(min_length=1, max_length=200)]


def _require_confined_relative_path(value: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {".", ".."} for part in path.parts):
        raise ValueError("path must be a confined repository-relative path")
    return value


class FrozenModel(BaseModel):
    """Strict wire-contract model with explicit alias-bound serialization."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_by_alias=True,
        validate_by_name=False,
        serialize_by_alias=True,
    )


class SourceReference(FrozenModel):
    repository: str
    commit_sha: str = Field(pattern=r"^[a-f0-9]{40}$")
    ref: str = Field(pattern=r"^refs/")
    run_id: int = Field(ge=1)


class ArtifactReference(FrozenModel):
    image: str
    digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    image_ref: str
    architecture: Literal["linux/amd64", "linux/arm64"] = "linux/amd64"

    @model_validator(mode="after")
    def image_ref_is_bound(self) -> ArtifactReference:
        if self.image_ref != f"{self.image}@{self.digest}":
            raise ValueError("image_ref must equal image@digest")
        return self


class ProfileReference(FrozenModel):
    path: str = Field(min_length=1, pattern=RELATIVE_PATH_PATTERN)

    @field_validator("path")
    @classmethod
    def path_is_confined(cls, value: str) -> str:
        return _require_confined_relative_path(value)

    digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")


class ReleaseEvidenceReference(FrozenModel):
    schema_id: Literal["l9.release-evidence-reference/v1"] = Field(alias="schema")
    schema_version: str
    sdk_version: str
    bundle_digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    gate_binding_digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    artifact_binding_digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    workflow_run_id: int = Field(ge=1)
    artifact_name: str
    bundle_path: str
    gate_binding_path: str
    artifact_binding_path: str
    provenance_reference: str
    sbom_reference: str


class DeploymentTarget(FrozenModel):
    environment: str = Field(pattern=ENVIRONMENT_PATTERN)


class DeploymentRequest(FrozenModel):
    schema_id: Literal["l9.deployment-request/v1"] = Field(alias="schema")
    request_id: str
    idempotency_key: str = Field(min_length=16, max_length=200)
    source: SourceReference
    artifact: ArtifactReference
    profile: ProfileReference
    evidence: ReleaseEvidenceReference
    target: DeploymentTarget
    requested_by: str
    requested_at: datetime


class HealthProbe(FrozenModel):
    type: Literal["http", "tcp", "command", "database"]
    path: str | None = None
    expected_status: int | None = None
    host: str | None = None
    port: int | None = None
    command: tuple[str, ...] | None = None
    timeout_seconds: int = Field(ge=1)
    interval_seconds: int = Field(default=5, ge=0)
    attempts: int = Field(default=1, ge=1)


class ProjectIdentity(FrozenModel):
    id: str = Field(pattern=PROJECT_ID_PATTERN)
    repository: str = Field(pattern=r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
    owner_team: str = Field(min_length=1)
    runtime_profile: Literal[
        "container-service",
        "worker-service",
        "stateful-container",
        "scheduled-job",
        "external-platform",
    ]


class ProfileArtifactPolicy(FrozenModel):
    registry: Literal["ghcr.io"]
    image: str
    require_digest: bool
    require_provenance_attestation: bool
    require_sbom_attestation: bool


class RuntimeVolume(FrozenModel):
    source: str
    target: str
    read_only: bool = False


class RuntimeConfig(FrozenModel):
    architecture: Literal["linux/amd64", "linux/arm64"]
    container_port: int | None = Field(default=None, ge=1, le=65535)
    user: Literal["non_root", "image_defined"]
    read_only_root_filesystem: bool = False
    stop_grace_seconds: int = Field(ge=1, le=300)
    command: tuple[str, ...] = ()
    environment: dict[str, str] = Field(default_factory=dict)
    volumes: tuple[RuntimeVolume, ...] = ()


class HealthConfig(FrozenModel):
    startup: HealthProbe
    post_deploy: HealthProbe


class ReleasePolicy(FrozenModel):
    strategy: Literal["rolling-single-host", "blue-green-single-host", "replace"]
    retain_successful_releases: int = Field(ge=2, le=50)
    automatic_rollback: bool
    production_approval_required: bool
    stabilization_seconds: int = Field(default=30, ge=0, le=900)


class MigrationConfig(FrozenModel):
    enabled: bool
    command: tuple[str, ...] = ()
    mode: Literal["pre_start", "post_start", "manual"] | None = None
    use_release_image: bool = True
    backup_required: bool = False
    timeout_seconds: int = Field(default=600, ge=1)
    rollback_safe: bool = False


class BackupConfig(FrozenModel):
    command: tuple[str, ...] = ()
    verify_command: tuple[str, ...] = ()
    restore_test_command: tuple[str, ...] = ()
    timeout_seconds: int = Field(default=1800, ge=1)


class SecretsConfig(FrozenModel):
    authority: Literal["infisical"]
    runtime_mode: Literal["runtime_fetch", "deploy_render"]
    project_slug: str
    environment_mapping: dict[str, str]


class PublicIngress(FrozenModel):
    enabled: bool
    hostnames: tuple[str, ...] = ()
    tls: Literal["automatic", "external", "disabled"] | None = None


class NetworkConfig(FrozenModel):
    public_ingress: PublicIngress
    private_dependencies_only: bool


class DeploymentPolicy(FrozenModel):
    allowed_source_refs: dict[str, tuple[str, ...]]
    require_clean_ci_gate: bool
    require_profile_digest_match: bool


class PersistentVolume(FrozenModel):
    name: str
    mount_path: str
    backup_policy: Literal["none", "daily", "weekly", "before_deploy"]


class StorageConfig(FrozenModel):
    persistent_volumes: tuple[PersistentVolume, ...] = ()


class ServiceConfig(FrozenModel):
    mode: Literal["managed_on_fleet", "external", "none"]
    required: bool
    probe: HealthProbe | None = None


class DeploymentProfile(FrozenModel):
    schema_id: Literal["l9.deployment-profile/v1"] = Field(alias="schema")
    project: ProjectIdentity
    artifact: ProfileArtifactPolicy
    runtime: RuntimeConfig
    health: HealthConfig
    release: ReleasePolicy
    migrations: MigrationConfig
    storage: StorageConfig = Field(default_factory=StorageConfig)
    services: dict[str, ServiceConfig] = Field(default_factory=dict)
    backup: BackupConfig | None = None
    secrets: SecretsConfig
    network: NetworkConfig
    policy: DeploymentPolicy


class SshConfig(FrozenModel):
    user: str
    port: int = Field(ge=1, le=65535)


class ConformanceConfig(FrozenModel):
    profile: str
    max_age_hours: int = Field(ge=1)


class ServerProfile(FrozenModel):
    schema_id: Literal["l9.server-profile/v1"] = Field(alias="schema")
    id: str
    environment: str
    provider: Literal["hetzner"]
    private_ip: str
    public_ip: str | None = None
    ssh: SshConfig
    roles: tuple[str, ...]
    labels: dict[str, str] = Field(default_factory=dict)
    conformance: ConformanceConfig


class FleetEnvironment(FrozenModel):
    approval_required: bool
    concurrency_group: str
    allowed_source_refs: tuple[str, ...] = ()


class ProjectEnvironment(FrozenModel):
    server_ids: tuple[str, ...]
    infisical_environment: str | None = None
    public_hostnames: tuple[str, ...] = ()


class FleetProject(FrozenModel):
    id: str = Field(pattern=PROJECT_ID_PATTERN)
    repository: str = Field(pattern=r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
    profile_path: str = Field(min_length=1, pattern=RELATIVE_PATH_PATTERN)
    environments: dict[str, ProjectEnvironment]

    @field_validator("profile_path")
    @classmethod
    def profile_path_is_confined(cls, value: str) -> str:
        return _require_confined_relative_path(value)


class FleetManagement(FrozenModel):
    runner_server_id: str
    private_cidr: str


class FleetInventory(FrozenModel):
    schema_id: Literal["l9.fleet-inventory/v1"] = Field(alias="schema")
    management: FleetManagement
    environments: dict[str, FleetEnvironment]
    servers: tuple[ServerProfile, ...]
    projects: tuple[FleetProject, ...]


class ReleaseState(FrozenModel):
    request_id: str
    source_commit_sha: str = Field(pattern=r"^[a-f0-9]{40}$")
    image_ref: str
    plan_digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")


class PlanStep(FrozenModel):
    id: str
    kind: Literal[
        "verify",
        "backup",
        "migration",
        "pull",
        "render",
        "deploy",
        "health",
        "promote",
        "cleanup",
        "rollback",
    ]
    mutating: bool
    timeout_seconds: int = Field(ge=1)
    details: dict[str, JsonValue] = Field(default_factory=dict)


class DeploymentPlan(FrozenModel):
    schema_id: Literal["l9.deployment-plan/v1"] = Field(alias="schema")
    request_id: str
    requested_by: str = Field(min_length=1)
    project_id: str = Field(pattern=PROJECT_ID_PATTERN)
    environment: str = Field(pattern=ENVIRONMENT_PATTERN)
    source_commit_sha: str = Field(pattern=r"^[a-f0-9]{40}$")
    image_ref: str
    profile_digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    target_servers: tuple[str, ...]
    previous_release: ReleaseState | None
    steps: tuple[PlanStep, ...]
    created_at: datetime
    plan_digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")


class ApprovalWorkflowEvidence(FrozenModel):
    repository: Literal["Quantum-L9/l9-deployment-platform"]
    run_id: int = Field(ge=1)
    run_attempt: int = Field(ge=1)
    job_id: int = Field(ge=1)
    workflow_ref: str
    environment: str
    approval_api_url: str
    approval_record_digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")


class ApprovalReceipt(FrozenModel):
    schema_id: Literal["l9.approval-receipt/v1"] = Field(alias="schema")
    approval_id: str
    request_id: str
    environment: str
    plan_digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    requester: str
    approved: Literal[True]
    approved_by: str
    approved_at: datetime
    authorization_method: Literal["github_protected_environment_review"]
    workflow: ApprovalWorkflowEvidence
    receipt_digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")

    @model_validator(mode="after")
    def separate_requester_and_approver(self) -> ApprovalReceipt:
        if self.requester == self.approved_by:
            raise ValueError("requester and approver must be different identities")
        return self


class IdempotencyEntry(FrozenModel):
    request_digest: Sha256Digest
    status: Literal["IN_PROGRESS", "PREPARED", "COMPLETE", "FAIL"]
    updated_at: datetime
    receipt_digest: Sha256Digest | None = None
    reason: str | None = None

    @model_validator(mode="after")
    def status_fields_are_consistent(self) -> IdempotencyEntry:
        if self.status == "IN_PROGRESS":
            if self.receipt_digest is not None or self.reason is not None:
                raise ValueError("IN_PROGRESS entries cannot carry completion or failure fields")
        elif self.status in {"PREPARED", "COMPLETE"}:
            if self.receipt_digest is None:
                raise ValueError(f"{self.status} entries require receipt_digest")
            if self.reason is not None:
                raise ValueError(f"{self.status} entries cannot carry a failure reason")
        elif self.status == "FAIL":
            if self.receipt_digest is not None:
                raise ValueError("FAIL entries cannot carry receipt_digest")
            if self.reason is None or not self.reason.strip():
                raise ValueError("FAIL entries require a non-empty reason")
        return self


class IdempotencyDocument(FrozenModel):
    schema_id: Literal["l9.idempotency-store/v1"] = Field(alias="schema")
    entries: dict[IdempotencyKey, IdempotencyEntry]


class VerifiedRequest(FrozenModel):
    document: DeploymentRequest
    project: FleetProject
    environment: ProjectEnvironment
    profile: DeploymentProfile
    fleet: FleetInventory


class ResolvedTarget(FrozenModel):
    project_id: str
    environment: str
    servers: tuple[ServerProfile, ...]


class ReceiptStep(FrozenModel):
    step_id: str
    kind: str
    status: Literal["PASS", "FAIL", "BLOCKED", "UNKNOWN"]
    details: dict[str, JsonValue] = Field(default_factory=dict)


class ReceiptArtifact(FrozenModel):
    kind: str
    digest: str | None = None
    path: str | None = None
    reference: str | None = None
    details: dict[str, JsonValue] = Field(default_factory=dict)


class RepositoryReleaseReceipt(FrozenModel):
    """Detached receipt binding one deterministic source archive to its manifest."""

    schema_id: Literal["l9.repository-release-receipt/v1"] = Field(alias="schema")
    repository: Literal["Quantum-L9/l9-deployment-platform"]
    version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    archive_name: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*\.zip$")
    archive_sha256: Sha256Digest
    archive_size_bytes: int = Field(ge=1)
    archive_files: int = Field(ge=1)
    source_manifest_sha256: Sha256Digest
    source_date_epoch: int = Field(ge=315532800)
    built_at: datetime
    receipt_digest: Sha256Digest


class DeploymentReceipt(FrozenModel):
    schema_id: Literal["l9.deployment-receipt/v1"] = Field(alias="schema")
    receipt_id: str
    request_id: str
    project_id: str
    environment: str
    status: Literal["PASS", "PASS_WITH_FINDINGS", "BLOCKED", "FAIL", "UNKNOWN"]
    started_at: datetime
    completed_at: datetime
    source_commit_sha: str = Field(pattern=r"^[a-f0-9]{40}$")
    image_ref: str
    plan_digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    previous_release: ReleaseState | None = None
    steps: tuple[ReceiptStep, ...]
    artifacts: tuple[ReceiptArtifact, ...]
    unknowns: tuple[str, ...]
    receipt_digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")

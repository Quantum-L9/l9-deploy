"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [execution]
tags: [L9_CONTRACT, release-layout, runtime-configuration]
owner: platform
status: active
--- /L9_META ---

Deterministic release-owned runtime configuration paths.
"""

from __future__ import annotations

import base64
import binascii
import json
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from ..canonical import bytes_sha256
from ..contracts.models import (
    ENVIRONMENT_PATTERN,
    PROJECT_ID_PATTERN,
    SHA256_PATTERN,
    DeploymentPlan,
    DeploymentProfile,
    FleetProject,
    ReleaseState,
)
from ..contracts.validator import SchemaRegistry
from ..errors import AuthorizationError, ContractError, ExecutionError
from ..planning.planner import verify_plan_digest
from ..requests.verifier import load_sealed_profile

PROJECTS_ROOT = Path("/srv/l9/projects")


class Executor(Protocol):
    def run(self, command: Sequence[str], **kwargs: object) -> object: ...
    def write_text(self, path: Path, text: str, mode: int = 0o600) -> None: ...


def _require_match(value: str, pattern: str, label: str) -> str:
    if re.fullmatch(pattern, value) is None:
        raise ValueError(f"invalid {label}: {value!r}")
    return value


def environment_root(project_id: str, environment: str) -> Path:
    project = _require_match(project_id, PROJECT_ID_PATTERN, "project id")
    target = _require_match(environment, ENVIRONMENT_PATTERN, "environment")
    return PROJECTS_ROOT / project / target


def active_runtime_env_path(project_id: str, environment: str) -> Path:
    """Return the legacy mutable path retained only for transition checks."""
    return environment_root(project_id, environment) / "runtime.env"


def release_directory(project_id: str, environment: str, plan_digest: str) -> Path:
    digest = _require_match(plan_digest, SHA256_PATTERN, "plan digest").removeprefix("sha256:")
    return environment_root(project_id, environment) / "releases" / digest


def release_runtime_env_path(project_id: str, environment: str, plan_digest: str) -> Path:
    return release_directory(project_id, environment, plan_digest) / "runtime.env"


def release_plan_path(project_id: str, environment: str, plan_digest: str) -> Path:
    return release_directory(project_id, environment, plan_digest) / "plan.json"


def release_profile_path(project_id: str, environment: str, plan_digest: str) -> Path:
    return release_directory(project_id, environment, plan_digest) / "deployment-profile"


def seal_release_profile(
    executor: Executor,
    plan: DeploymentPlan,
    profile_source: bytes,
) -> dict[str, str]:
    """Persist the approved plan and its sealed profile bytes with the release.

    The release directory is already keyed by ``plan_digest`` and retained for the
    current and previous release. Writing the plan and the exact profile bytes it
    was approved over beside ``runtime.env`` lets rollback, backup and restore
    later reach *that release's* consumer profile through the same digest chain
    (runtime state -> plan content -> profile bytes) without a platform copy, a
    second store, or a floating source branch.
    """
    if bytes_sha256(profile_source) != plan.profile_digest:
        raise AuthorizationError(
            "sealed deployment profile does not match the approved plan profile digest"
        )
    plan_path = release_plan_path(plan.project_id, plan.environment, plan.plan_digest)
    profile_path = release_profile_path(plan.project_id, plan.environment, plan.plan_digest)
    plan_text = (
        json.dumps(plan.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True) + "\n"
    )
    executor.write_text(plan_path, plan_text, mode=0o600)
    executor.write_text(profile_path, profile_source.decode("utf-8"), mode=0o600)
    return {"plan_path": str(plan_path), "profile_path": str(profile_path)}


def _read_release_file(executor: Executor, path: Path) -> bytes:
    # base64 keeps the transfer byte-exact: command output is newline-normalized
    # and redacted text, which must never be what a digest is checked against.
    result = executor.run(["base64", "-w0", "--", str(path)], check=False)
    if getattr(result, "returncode", 1) != 0:
        raise ContractError(f"sealed release material is unavailable: {path}")
    try:
        return base64.b64decode(str(getattr(result, "stdout", "")).strip(), validate=True)
    except binascii.Error as exc:
        raise ContractError(f"sealed release material is unreadable: {path}") from exc


def load_release_profile(
    executor: Executor,
    release: ReleaseState,
    project: FleetProject,
    environment: str,
    registry: SchemaRegistry,
) -> DeploymentProfile:
    """Return the consumer profile ``release`` was approved and deployed with.

    Only material sealed in the release's own directory is accepted, and only
    through the digest chain that ties it to the runtime state: the sealed plan
    must reproduce ``release.plan_digest`` from its content and name the same
    project, environment, request, source commit and image, and the sealed
    profile bytes must equal the plan's ``profile_digest``. Anything missing or
    inconsistent fails closed before the caller mutates anything; a release
    deployed before profiles were sealed is therefore blocked, never served a
    current or platform-local profile in its place.
    """
    validate_release_runtime_env_path(release, project.id, environment)
    plan_bytes = _read_release_file(
        executor, release_plan_path(project.id, environment, release.plan_digest)
    )
    try:
        plan_document = json.loads(plan_bytes.decode("utf-8"))
    except ValueError as exc:  # UnicodeDecodeError is a ValueError
        raise ContractError("sealed release plan is not parseable") from exc
    registry.validate(plan_document, "deployment-plan")
    plan = DeploymentPlan.model_validate(plan_document)
    verify_plan_digest(plan)
    if (
        plan.plan_digest != release.plan_digest
        or plan.project_id != project.id
        or plan.environment != environment
        or plan.request_id != release.request_id
        or plan.source_commit_sha != release.source_commit_sha
        or plan.image_ref != release.image_ref
    ):
        raise AuthorizationError("sealed release plan does not match the runtime release state")
    profile_bytes = _read_release_file(
        executor, release_profile_path(project.id, environment, release.plan_digest)
    )
    return load_sealed_profile(
        profile_bytes, plan=plan, repository=project.repository, registry=registry
    )


def bind_release_runtime_env(
    release: ReleaseState,
    project_id: str,
    environment: str,
) -> ReleaseState:
    expected = str(release_runtime_env_path(project_id, environment, release.plan_digest))
    if release.runtime_env_path is not None and release.runtime_env_path != expected:
        raise ExecutionError("release runtime environment path conflicts with release identity")
    return release.model_copy(update={"runtime_env_path": expected})


def validate_release_runtime_env_path(
    release: ReleaseState,
    project_id: str,
    environment: str,
) -> Path | None:
    if release.runtime_env_path is None:
        return None
    expected = release_runtime_env_path(project_id, environment, release.plan_digest)
    if release.runtime_env_path != str(expected):
        raise ExecutionError("release runtime environment path does not match release identity")
    return expected


def materialize_release_runtime_env(
    executor: Executor,
    release: ReleaseState,
    project_id: str,
    environment: str,
    content: str,
) -> ReleaseState:
    bound = bind_release_runtime_env(release, project_id, environment)
    if bound.runtime_env_path is None:
        raise ExecutionError("release runtime environment path was not bound")
    path = Path(bound.runtime_env_path)
    executor.run(["install", "-d", "-m", "0700", str(path.parent)])
    executor.write_text(path, content, mode=0o600)
    return bound


def remove_release_directory(
    executor: Executor,
    release: ReleaseState,
    project_id: str,
    environment: str,
) -> None:
    path = release_directory(project_id, environment, release.plan_digest)
    executor.run(["rm", "-rf", "--", str(path)])


def cleanup_release_directories(
    executor: Executor,
    current: ReleaseState,
    previous: ReleaseState | None,
    project_id: str,
    environment: str,
) -> dict[str, object]:
    retained = retained_release_directories(current, previous, project_id, environment)
    root = environment_root(project_id, environment) / "releases"
    result = executor.run(
        ["find", str(root), "-mindepth", "1", "-maxdepth", "1", "-type", "d", "-print"]
    )
    removed: list[str] = []
    retained_set = {str(path) for path in retained}
    for line in str(getattr(result, "stdout", "")).splitlines():
        candidate = Path(line)
        if candidate.parent != root or re.fullmatch(r"[0-9a-f]{64}", candidate.name) is None:
            raise ExecutionError("unsafe release directory returned by cleanup inventory")
        if str(candidate) not in retained_set:
            executor.run(["rm", "-rf", "--", str(candidate)])
            removed.append(str(candidate))
    return {
        "status": "PASS",
        "retained_release_directories": [str(path) for path in retained],
        "removed_release_directories": removed,
    }


def retained_release_directories(
    current: ReleaseState,
    previous: ReleaseState | None,
    project_id: str,
    environment: str,
) -> tuple[Path, ...]:
    releases = [current]
    if previous is not None:
        releases.append(previous)
    retained: list[Path] = []
    for release in releases:
        validate_release_runtime_env_path(release, project_id, environment)
        directory = release_directory(project_id, environment, release.plan_digest)
        if directory not in retained:
            retained.append(directory)
    return tuple(retained)

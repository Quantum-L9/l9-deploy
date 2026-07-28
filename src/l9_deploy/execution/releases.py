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

import re
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from ..contracts.models import (
    ENVIRONMENT_PATTERN,
    PROJECT_ID_PATTERN,
    SHA256_PATTERN,
    ReleaseState,
)
from ..errors import ExecutionError

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

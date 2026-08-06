"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests, execution]
tags: [L9_TEST, release-layout, runtime-state]
owner: platform
status: active
--- /L9_META ---
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from l9_deploy import cli
from l9_deploy.contracts.models import ReleaseState, RuntimeState
from l9_deploy.errors import ExecutionError
from l9_deploy.execution.promotion import write_runtime_state
from l9_deploy.execution.releases import (
    active_runtime_env_path,
    bind_release_runtime_env,
    materialize_release_runtime_env,
    release_runtime_env_path,
    retained_release_directories,
)
from l9_deploy.execution.remote import Host, RemoteExecutor


def _release(plan_digest: str = "sha256:" + "a" * 64) -> ReleaseState:
    return ReleaseState(
        request_id="release-request",
        source_commit_sha="b" * 40,
        image_ref="ghcr.io/quantum-l9/app@sha256:" + "c" * 64,
        plan_digest=plan_digest,
    )


class RecordingExecutor:
    def __init__(self) -> None:
        self.runs: list[tuple[list[str], dict[str, object]]] = []
        self.writes: list[tuple[Path, str, int]] = []

    def run(self, command: list[str], **kwargs: object) -> object:
        self.runs.append((command, kwargs))
        return object()

    def write_text(self, path: Path, text: str, mode: int = 0o600) -> None:
        self.writes.append((path, text, mode))


def test_release_runtime_env_path_is_deterministic_and_isolated() -> None:
    release = _release()
    path = release_runtime_env_path("seo-bot", "staging", release.plan_digest)

    assert path == Path("/srv/l9/projects/seo-bot/staging/releases/" + "a" * 64 + "/runtime.env")
    assert path != active_runtime_env_path("seo-bot", "staging")


@pytest.mark.parametrize(
    ("project_id", "environment", "plan_digest"),
    [
        ("../escape", "staging", "sha256:" + "a" * 64),
        ("seo-bot", "../escape", "sha256:" + "a" * 64),
        ("seo-bot", "staging", "not-a-digest"),
    ],
)
def test_release_runtime_env_path_rejects_unsafe_identity(
    project_id: str,
    environment: str,
    plan_digest: str,
) -> None:
    with pytest.raises(ValueError):
        release_runtime_env_path(project_id, environment, plan_digest)


def test_old_runtime_state_loads_and_new_state_round_trips(tmp_path: Path) -> None:
    old_document = {
        "schema": "l9.runtime-state/v1",
        "current": _release().model_dump(mode="json", by_alias=True, exclude_none=True),
        "previous": None,
        "promoted_at": "2026-07-21T12:00:00Z",
    }
    state_path = tmp_path / "state.json"
    state_path.write_text(json.dumps(old_document), encoding="utf-8")

    loaded_previous = cli._load_previous_state(state_path, "seo-bot", "staging")
    assert loaded_previous is not None
    assert "runtime_env_path" not in loaded_previous

    current = bind_release_runtime_env(_release(), "seo-bot", "staging")
    new_state = RuntimeState(
        schema="l9.runtime-state/v1",
        current=current,
        previous=RuntimeState.model_validate(old_document).current,
        promoted_at="2026-07-21T12:01:00Z",
    )
    wire = new_state.model_dump(mode="json", by_alias=True)
    assert RuntimeState.model_validate(wire).model_dump(mode="json", by_alias=True) == wire
    assert wire["current"]["runtime_env_path"].endswith("/runtime.env")


def test_runtime_env_path_cannot_conflict_with_release_identity() -> None:
    release = _release().model_copy(
        update={
            "runtime_env_path": (
                "/srv/l9/projects/seo-bot/staging/releases/" + "d" * 64 + "/runtime.env"
            )
        }
    )
    with pytest.raises(ExecutionError, match="conflicts"):
        bind_release_runtime_env(release, "seo-bot", "staging")


def test_runtime_state_writer_validates_and_persists_release_env_identity() -> None:
    executor = RecordingExecutor()
    current = bind_release_runtime_env(_release(), "seo-bot", "staging")

    result = write_runtime_state(executor, "seo-bot", "staging", current, None)

    assert result["status"] == "PASS"
    assert len(executor.writes) == 1
    path, text, mode = executor.writes[0]
    document = json.loads(text)
    assert path == Path("/srv/l9/projects/seo-bot/staging/state.json")
    assert mode == 0o600
    assert document["current"]["runtime_env_path"] == current.runtime_env_path
    RuntimeState.model_validate(document)


def test_materialize_release_runtime_env_creates_private_release_directory() -> None:
    executor = RecordingExecutor()
    release = _release()

    bound = materialize_release_runtime_env(
        executor,
        release,
        "seo-bot",
        "staging",
        "TOKEN=secret-canary\n",
    )

    assert bound.runtime_env_path is not None
    path = Path(bound.runtime_env_path)
    assert executor.runs == [(["install", "-d", "-m", "0700", str(path.parent)], {})]
    assert executor.writes == [(path, "TOKEN=secret-canary\n", 0o600)]
    assert path != active_runtime_env_path("seo-bot", "staging")


def test_retention_preserves_current_and_rollback_release_directories() -> None:
    current = bind_release_runtime_env(_release("sha256:" + "a" * 64), "seo-bot", "staging")
    previous = bind_release_runtime_env(_release("sha256:" + "d" * 64), "seo-bot", "staging")

    retained = retained_release_directories(current, previous, "seo-bot", "staging")

    assert retained == (
        Path("/srv/l9/projects/seo-bot/staging/releases/" + "a" * 64),
        Path("/srv/l9/projects/seo-bot/staging/releases/" + "d" * 64),
    )


def test_remote_writer_streams_secret_content_outside_process_arguments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_run_command(command: list[str], **kwargs: object) -> object:
        captured["command"] = command
        captured.update(kwargs)
        return object()

    monkeypatch.setattr("l9_deploy.execution.remote.run_command", fake_run_command)
    executor = RemoteExecutor(Host("server", "10.0.0.10", "deploy"))
    env_body = "TOKEN=secret-canary\n"

    executor.write_text(Path("/srv/l9/projects/seo-bot/staging/runtime.env"), env_body)

    command = captured["command"]
    assert isinstance(command, list)
    command_text = " ".join(command)
    assert captured["input_text"] == env_body
    assert env_body.strip() not in command_text
    assert base64.b64encode(env_body.encode()).decode() not in command_text
    assert "mktemp" in command_text
    assert "chmod 600" in command_text
    assert "mv -f" in command_text


def test_runtime_state_rejects_secret_bearing_fields() -> None:
    document = {
        "schema": "l9.runtime-state/v1",
        "current": {
            **_release().model_dump(mode="json", by_alias=True, exclude_none=True),
            "secret_values": {"TOKEN": "not-allowed"},
        },
        "previous": None,
        "promoted_at": "2026-07-21T12:00:00Z",
    }
    with pytest.raises(ValidationError):
        RuntimeState.model_validate(document)


def test_release_state_rejects_non_release_runtime_env_path() -> None:
    with pytest.raises(ValidationError):
        ReleaseState(
            request_id="release-request",
            source_commit_sha="b" * 40,
            image_ref="ghcr.io/quantum-l9/app@sha256:" + "c" * 64,
            plan_digest="sha256:" + "a" * 64,
            runtime_env_path="/srv/l9/projects/seo-bot/staging/runtime.env",
        )

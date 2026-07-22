"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests, boundaries]
tags: [L9_TEST, deployment-platform, integrations, fail-closed]
owner: platform
status: active
--- /L9_META ---
"""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from l9_deploy.canonical import sha256_digest
from l9_deploy.contracts.models import HealthProbe
from l9_deploy.errors import (
    AuthorizationError,
    ContractError,
    ExecutionError,
    OperationalLimitError,
)
from l9_deploy.evidence.records import evidence_record
from l9_deploy.execution.health import run_probe
from l9_deploy.integrations import ansible, ghcr, github, hetzner, infisical, opentofu
from l9_deploy.logging import JsonFormatter
from l9_deploy.subprocesses import CommandResult, run_command


def _result(command: list[str], stdout: str = "", returncode: int = 0) -> CommandResult:
    return CommandResult(tuple(command), returncode, stdout, "")


def test_github_repository_guard_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    with pytest.raises(AuthorizationError, match="<unset>"):
        github.require_private_control_repository()
    monkeypatch.setenv("GITHUB_REPOSITORY", "Quantum-L9/other")
    with pytest.raises(AuthorizationError, match="Quantum-L9/other"):
        github.require_private_control_repository()
    monkeypatch.setenv("GITHUB_REPOSITORY", "Quantum-L9/l9-deployment-platform")
    github.require_private_control_repository()


def test_github_event_loader_and_dispatch(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    with pytest.raises(ContractError, match="unavailable"):
        github.load_github_event(missing)

    event = tmp_path / "event.json"
    event.write_text("[]", encoding="utf-8")
    with pytest.raises(ContractError, match="JSON object"):
        github.load_github_event(event)

    event.write_text(json.dumps({"action": "unexpected", "client_payload": {}}), encoding="utf-8")
    with pytest.raises(ContractError):
        github.request_from_github_event(event)


def test_infisical_environment_is_private_cleaned_and_injection_safe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = json.dumps([
        {"secretKey": "API_KEY", "secretValue": "abc=123"},
        {"secretKey": "PORT", "secretValue": "443"},
    ])
    monkeypatch.setattr(infisical, "run_command", lambda *a, **k: _result([], payload))
    with infisical.rendered_environment("project", "production") as path:
        assert path.read_text(encoding="utf-8") == "API_KEY=abc=123\nPORT=443\n"
        assert path.stat().st_mode & 0o777 == 0o600
        rendered = path
    assert not rendered.exists()

    for invalid in (
        [{"secretKey": "BAD\nKEY", "secretValue": "value"}],
        [{"secretKey": "A", "secretValue": "one"}, {"secretKey": "A", "secretValue": "two"}],
        [{"secretKey": "A", "secretValue": "line\nbreak"}],
        ["not-an-object"],
    ):
        monkeypatch.setattr(
            infisical,
            "run_command",
            lambda *a, payload=json.dumps(invalid), **k: _result([], payload),
        )
        with pytest.raises(ExecutionError):
            with infisical.rendered_environment("project", "production"):
                pytest.fail("unsafe secret material was yielded")


def test_infisical_rejects_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(infisical, "run_command", lambda *a, **k: _result([], "not-json"))
    with pytest.raises(ExecutionError, match="invalid JSON"):
        with infisical.rendered_environment("project", "production"):
            pytest.fail("invalid export was yielded")


def test_evidence_record_is_redacted_schema_valid_and_digest_bound() -> None:
    record = evidence_record(
        "deployment-check",
        "PASS",
        {"project": "seo-bot", "token": "super-secret"},
        [{"name": "health", "status": "PASS", "evidence": {"ok": True}}],
        [{"name": "report", "digest": "sha256:" + "a" * 64}],
    )
    assert record["subject"]["token"].startswith("[REDACTED")
    digest = record.pop("digest")
    assert digest == sha256_digest(record)

    with pytest.raises(ContractError):
        evidence_record("deployment-check", "NOT_A_STATUS", {}, [])


def test_ansible_adapters_build_argument_arrays(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[list[str], dict[str, object]]] = []

    def fake(command: list[str], **kwargs: object) -> CommandResult:
        calls.append((command, kwargs))
        return _result(command)

    monkeypatch.setattr(ansible, "run_command", fake)
    playbook = Path("site.yml")
    inventory = Path("hosts.yml")
    ansible.syntax_check(playbook, inventory)
    ansible.check(playbook, inventory, limit="web", timeout=10)
    ansible.apply(playbook, inventory, limit="web", timeout=20)
    assert calls[0][0] == ["ansible-playbook", "-i", "hosts.yml", "--syntax-check", "site.yml"]
    assert calls[1][0][-2:] == ["--limit", "web"]
    assert calls[1][1]["timeout"] == 10
    assert calls[2][1]["timeout"] == 20


def test_ghcr_and_hetzner_adapters_validate_outputs(monkeypatch: pytest.MonkeyPatch) -> None:
    image_ref = "ghcr.io/quantum-l9/app@sha256:" + "a" * 64
    monkeypatch.setattr(ghcr, "run_command", lambda command, **kwargs: _result(command, "manifest"))
    assert ghcr.verify_remote_manifest(image_ref)["output"] == "manifest"
    with pytest.raises(ContractError):
        ghcr.verify_remote_manifest("ghcr.io/quantum-l9/app:latest")

    monkeypatch.setattr(
        hetzner,
        "run_command",
        lambda command, **kwargs: _result(command, '{"id": 1}'),
    )
    assert hetzner.server("1") == {"id": 1}
    monkeypatch.setattr(hetzner, "run_command", lambda command, **kwargs: _result(command, "[]"))
    with pytest.raises(ValueError, match="invalid server document"):
        hetzner.server("1")


def test_opentofu_plan_and_apply_are_digest_and_destruction_bound(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan_file = tmp_path / "plan.tfplan"
    plan_file.write_bytes(b"plan")
    changes = {
        "resource_changes": [
            {"address": "server.new", "change": {"actions": ["create"]}},
            {"address": "server.old", "change": {"actions": ["delete"]}},
        ]
    }
    calls: list[list[str]] = []

    def fake(command: list[str], **kwargs: object) -> CommandResult:
        calls.append(command)
        if command[:3] == ["tofu", "show", "-json"]:
            return _result(command, json.dumps(changes))
        if command[:3] == ["tofu", "version", "-json"]:
            return _result(command, '{"terraform_version":"1.9.0"}')
        return _result(command)

    monkeypatch.setattr(opentofu, "run_command", fake)
    receipt = opentofu.plan(tmp_path, "staging", plan_file)
    assert receipt["change_summary"] == {"create": 1, "update": 0, "delete": 1, "replace": 0}
    assert receipt["destructive_changes"] == [{"address": "server.old"}]

    digest = opentofu.file_sha256(plan_file)
    with pytest.raises(AuthorizationError, match="destructive"):
        opentofu.apply(tmp_path, plan_file, digest)
    opentofu.apply(tmp_path, plan_file, digest, allow_destructive=True)
    assert ["tofu", "apply", "-input=false", "-lock=true", str(plan_file)] in calls
    with pytest.raises(AuthorizationError, match="digest mismatch"):
        opentofu.apply(tmp_path, plan_file, "sha256:" + "0" * 64, allow_destructive=True)


def test_run_command_validates_inputs_redacts_and_reports_failures() -> None:
    with pytest.raises(ValueError, match="at least one"):
        run_command([])
    with pytest.raises(ValueError, match="at least one second"):
        run_command([sys.executable, "-c", "pass"], timeout=0)

    result = run_command(
        [sys.executable, "-c", "print('TOKEN=secret-value')"],
        env={"TOKEN": "secret-value"},
    )
    assert "secret-value" not in result.stdout

    with pytest.raises(ExecutionError, match="command failed"):
        run_command([sys.executable, "-c", "import sys; sys.exit(7)"])
    unchecked = run_command(
        [sys.executable, "-c", "import sys; sys.exit(7)"],
        check=False,
    )
    assert unchecked.returncode == 7


def test_run_command_timeout_terminates_process_group() -> None:
    with pytest.raises(OperationalLimitError, match="timed out"):
        run_command([sys.executable, "-c", "import time; time.sleep(5)"], timeout=1)


def test_health_command_probe_and_http_scheme_restriction() -> None:
    calls: list[tuple[tuple[str, ...], dict[str, object]]] = []

    class Executor:
        def run(self, command: tuple[str, ...], **kwargs: object) -> object:
            calls.append((command, kwargs))
            return SimpleNamespace(returncode=0)

    probe = HealthProbe(
        type="command",
        command=("true",),
        timeout_seconds=2,
        attempts=1,
    )
    assert run_probe(probe, executor=Executor()) == {"attempt": 1, "type": "command"}
    assert calls == [(('true',), {"timeout": 2})]

    http = HealthProbe(
        type="http",
        path="/health",
        expected_status=200,
        timeout_seconds=1,
        attempts=1,
    )
    with pytest.raises(ExecutionError, match="http or https"):
        run_probe(http, base_url="file:///etc/passwd")


def test_json_formatter_redacts_context() -> None:
    formatter = JsonFormatter()
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "hello", (), None)
    record.context = {"password": "secret-value"}  # type: ignore[attr-defined]
    payload = json.loads(formatter.format(record))
    assert payload["message"] == "hello"
    assert payload["context"]["password"].startswith("[REDACTED")

"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests, unit]
tags: [L9_TEST, cli, operator-surface]
owner: platform
status: active
--- /L9_META ---
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from l9_deploy import cli
from l9_deploy.errors import ContractError


def _top_level_commands(parser: argparse.ArgumentParser) -> set[str]:
    action = next(item for item in parser._actions if isinstance(item, argparse._SubParsersAction))
    return set(action.choices)


def test_parser_exposes_the_complete_operator_surface() -> None:
    parser = cli.build_parser()
    assert _top_level_commands(parser) == {
        "adoption",
        "approval",
        "backup",
        "config",
        "contract",
        "deploy",
        "fleet",
        "host",
        "infra",
        "inventory",
        "plan",
        "promote",
        "receipt",
        "request",
        "restore",
        "rollback",
        "status",
    }
    parsed = parser.parse_args(["status", "--project", "seo-bot", "--environment", "staging"])
    assert parsed.handler is cli.cmd_status
    assert parsed.timeout == 300


def test_contract_validation_cli_succeeds_and_missing_document_fails_closed(
    repo_root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    valid = repo_root / "deployment" / "probes" / "http.yaml"
    exit_code = cli.main(
        [
            "contract",
            "validate",
            "--root",
            str(repo_root),
            "--path",
            str(valid),
            "--schema",
            "health-probe",
            "--json",
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "PASS"
    assert payload["schema"] == "health-probe"
    assert payload["digest"].startswith("sha256:")

    missing = tmp_path / "missing.yaml"
    exit_code = cli.main(
        [
            "contract",
            "validate",
            "--root",
            str(repo_root),
            "--path",
            str(missing),
            "--schema",
            "health-probe",
            "--json",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == ContractError.exit_code
    error = json.loads(captured.err)
    assert error["status"] == "FAIL"
    assert error["error_type"] == "ContractError"
    assert "document not found" in error["error"]


def test_inventory_cli_validates_and_generates_private_output(
    repo_root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    fleet = repo_root / "fleet" / "registry.yaml"
    assert (
        cli.main(
            [
                "inventory",
                "validate",
                "--root",
                str(repo_root),
                "--fleet",
                str(fleet),
                "--json",
            ]
        )
        == 0
    )
    validated = json.loads(capsys.readouterr().out)
    assert validated["status"] == "PASS"
    assert validated["servers"] >= 1

    output = tmp_path / "generated" / "hosts.yml"
    assert (
        cli.main(
            [
                "inventory",
                "generate",
                "--root",
                str(repo_root),
                "--fleet",
                str(fleet),
                "--output",
                str(output),
                "--json",
            ]
        )
        == 0
    )
    generated = json.loads(capsys.readouterr().out)
    assert generated["status"] == "PASS"
    assert output.is_file()
    assert output.stat().st_mode & 0o777 == 0o640


def test_adoption_cli_renders_projection_and_refuses_unapproved_replacement(
    repo_root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    destination = tmp_path / "consumer"
    arguments = [
        "adoption",
        "render",
        "--root",
        str(repo_root),
        "--profile",
        "container-service",
        "--project-id",
        "sample-app",
        "--repository",
        "Quantum-L9/Sample-App",
        "--image",
        "ghcr.io/quantum-l9/sample-app",
        "--destination",
        str(destination),
        "--json",
    ]
    assert cli.main(arguments) == 0
    rendered = json.loads(capsys.readouterr().out)
    assert rendered["status"] == "PASS"
    assert (destination / ".l9" / "deployment.yaml").is_file()
    assert (destination / ".github" / "workflows" / "release.yml").is_file()
    assert (destination / ".l9-deployment-projection.json").stat().st_mode & 0o777 == 0o640

    assert cli.main(arguments) == 6
    assert "destination is not empty" in capsys.readouterr().err

    force_arguments = [*arguments[:-1], "--force", "--json"]
    assert cli.main(force_arguments) == 0
    capsys.readouterr()


def test_object_document_rejects_non_object(tmp_path: Path) -> None:
    path = tmp_path / "list.yaml"
    path.write_text("- one\n- two\n", encoding="utf-8")
    with pytest.raises(ContractError, match="expected object document"):
        cli.object_document(path)

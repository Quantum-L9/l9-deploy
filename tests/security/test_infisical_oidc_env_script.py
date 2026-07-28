"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests, security]
tags: [L9_TEST, infisical, atomic-publication, secret-redaction]
owner: platform
status: active
--- /L9_META ---
"""
from __future__ import annotations

import json
import os
import stat
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/infisical-oidc-env.sh"


def _fake_tooling(tmp_path: Path) -> Path:
    binary_dir = tmp_path / "bin"
    binary_dir.mkdir()
    curl = binary_dir / "curl"
    curl.write_text(
        "#!/usr/bin/env bash\n"
        "if [[ \"$*\" == *oidc-auth/login* ]]; then\n"
        "  printf '%s' '{\"accessToken\":\"access-token-canary\"}'\n"
        "else\n"
        "  printf '%s' '{\"value\":\"oidc-token-canary\"}'\n"
        "fi\n",
        encoding="utf-8",
    )
    infisical = binary_dir / "infisical"
    infisical.write_text(
        "#!/usr/bin/env bash\nprintf '%s' \"$FAKE_INFISICAL_JSON\"\n",
        encoding="utf-8",
    )
    curl.chmod(0o755)
    infisical.chmod(0o755)
    return binary_dir


def _run(
    tmp_path: Path,
    payload: object,
    destination: Path,
    *,
    output_file: bool = True,
) -> subprocess.CompletedProcess[str]:
    binary_dir = _fake_tooling(tmp_path)
    env = {
        **os.environ,
        "PATH": f"{binary_dir}:{os.environ['PATH']}",
        "ACTIONS_ID_TOKEN_REQUEST_URL": "https://github.invalid/oidc",
        "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "request-token-canary",
        "INFISICAL_IDENTITY_ID": "identity",
        "INFISICAL_PROJECT_SLUG": "project",
        "FAKE_INFISICAL_JSON": json.dumps(payload),
    }
    arguments = ["bash", str(SCRIPT), "staging"]
    if output_file:
        arguments.append(str(destination))
    else:
        env["GITHUB_ENV"] = str(destination)
    return subprocess.run(
        arguments,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def test_valid_export_is_sorted_private_and_published_atomically(tmp_path: Path) -> None:
    destination = tmp_path / "runtime.env"
    result = _run(
        tmp_path,
        [
            {"secretKey": "SECOND", "secretValue": "two-canary"},
            {"secretKey": "FIRST", "secretValue": "one-canary"},
        ],
        destination,
    )

    assert result.returncode == 0, result.stderr
    assert destination.read_text(encoding="utf-8") == (
        "FIRST=one-canary\nSECOND=two-canary\n"
    )
    assert stat.S_IMODE(destination.stat().st_mode) == 0o600
    assert "one-canary" not in result.stdout + result.stderr
    assert "two-canary" not in result.stdout + result.stderr
    assert "access-token-canary" not in result.stdout + result.stderr
    assert list(tmp_path.glob(".l9-runtime-env.*")) == []


def test_github_env_mode_validates_then_appends(tmp_path: Path) -> None:
    destination = tmp_path / "github-env"
    destination.write_text("EXISTING=preserved\n", encoding="utf-8")

    result = _run(
        tmp_path,
        [{"secretKey": "APP_TOKEN", "secretValue": "token-canary"}],
        destination,
        output_file=False,
    )

    assert result.returncode == 0, result.stderr
    assert destination.read_text(encoding="utf-8") == (
        "EXISTING=preserved\nAPP_TOKEN=token-canary\n"
    )
    assert "token-canary" not in result.stdout + result.stderr


@pytest.mark.parametrize(
    "payload",
    [
        [
            {"secretKey": "SAFE", "secretValue": "secret-canary"},
            {"secretKey": "BAD-KEY", "secretValue": "bad"},
        ],
        [
            {"secretKey": "DUPLICATE", "secretValue": "one"},
            {"secretKey": "DUPLICATE", "secretValue": "two"},
        ],
        [{"secretKey": "PATH", "secretValue": "/unsafe"}],
        [{"secretKey": "EMPTY", "secretValue": ""}],
        [{"secretKey": "MULTILINE", "secretValue": "line\nbreak"}],
        [{"secretKey": "NUL_VALUE", "secretValue": "before\u0000after"}],
        {"not": "a-list"},
        ["not-an-object"],
        [{"secretKey": "NOT_STRING", "secretValue": None}],
    ],
)
def test_invalid_export_leaves_existing_destination_unchanged(
    tmp_path: Path,
    payload: object,
) -> None:
    destination = tmp_path / "runtime.env"
    destination.write_text("ORIGINAL=preserved\n", encoding="utf-8")

    result = _run(tmp_path, payload, destination)

    assert result.returncode == 2
    assert destination.read_text(encoding="utf-8") == "ORIGINAL=preserved\n"
    assert "secret-canary" not in result.stdout + result.stderr
    assert list(tmp_path.glob(".l9-runtime-env.*")) == []

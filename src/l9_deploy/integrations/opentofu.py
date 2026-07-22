"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer:
- repository
tags:
- L9_META
- deployment-platform
owner: platform
status: active
--- /L9_META ---
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ..canonical import file_sha256, sha256_digest
from ..errors import AuthorizationError
from ..subprocesses import run_command


def plan(
    directory: Path, environment: str, output_plan: Path, timeout: int = 900
) -> dict[str, Any]:
    run_command(["tofu", "init", "-input=false"], cwd=directory, timeout=timeout)
    run_command(["tofu", "validate"], cwd=directory, timeout=timeout)
    output_plan.parent.mkdir(parents=True, exist_ok=True)
    run_command(
        ["tofu", "plan", "-input=false", "-lock=true", "-out", str(output_plan)],
        cwd=directory,
        timeout=timeout,
    )
    show = run_command(["tofu", "show", "-json", str(output_plan)], cwd=directory, timeout=timeout)
    document = json.loads(show.stdout)
    summary = {"create": 0, "update": 0, "delete": 0, "replace": 0}
    destructive = []
    for change in document.get("resource_changes", []):
        actions = change.get("change", {}).get("actions", [])
        if actions == ["create"]:
            summary["create"] += 1
        elif actions == ["update"]:
            summary["update"] += 1
        elif actions == ["delete"]:
            summary["delete"] += 1
            destructive.append(change.get("address"))
        elif "delete" in actions and "create" in actions:
            summary["replace"] += 1
            destructive.append(change.get("address"))
    receipt = {
        "schema": "l9.infrastructure-plan/v1",
        "environment": environment,
        "created_at": datetime.now(UTC).isoformat(),
        "tofu_version": run_command(["tofu", "version", "-json"], cwd=directory).stdout.strip(),
        "plan_file_digest": file_sha256(output_plan),
        "change_summary": summary,
        "destructive_changes": [{"address": item} for item in destructive if item],
    }
    receipt["plan_digest"] = sha256_digest(receipt)
    return receipt


def apply(
    directory: Path,
    plan_file: Path,
    expected_digest: str,
    allow_destructive: bool = False,
    timeout: int = 1800,
) -> None:
    if file_sha256(plan_file) != expected_digest:
        raise AuthorizationError("OpenTofu plan file digest mismatch")
    show = run_command(["tofu", "show", "-json", str(plan_file)], cwd=directory, timeout=timeout)
    document = json.loads(show.stdout)
    destructive = [
        change.get("address")
        for change in document.get("resource_changes", [])
        if "delete" in change.get("change", {}).get("actions", [])
    ]
    if destructive and not allow_destructive:
        raise AuthorizationError("destructive OpenTofu changes require explicit approval")
    run_command(
        ["tofu", "apply", "-input=false", "-lock=true", str(plan_file)],
        cwd=directory,
        timeout=timeout,
    )

#!/usr/bin/env python3
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

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[object, object]:
    mapping: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate key: {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _local_action_exists(root: Path, use: str) -> bool:
    target = (root / use.removeprefix("./")).resolve()
    if target != root and root not in target.parents:
        return False
    if target.is_file():
        return True
    return (target / "action.yml").is_file() or (target / "action.yaml").is_file()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate GitHub workflow policy")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    return parser.parse_args()


def main() -> int:
    root = parse_args().root.resolve()
    errors: list[str] = []
    sha = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[a-f0-9]{40}$")
    allowed_versioned = re.compile(r"^Quantum-L9/[A-Za-z0-9_.-]+/.+@v[1-9][0-9]*$")

    mutating_workflows = {
        "configure-hosts.yml",
        "deploy-dispatch.yml",
        "provision-apply.yml",
        "rollback.yml",
        "runner-maintenance.yml",
    }
    for path in sorted((root / ".github/workflows").glob("*.yml")):
        try:
            loader = UniqueKeyLoader(path.read_text(encoding="utf-8"))
            try:
                doc = loader.get_single_data()
            finally:
                loader.dispose()
        except yaml.YAMLError as exc:
            errors.append(f"{path}: invalid or duplicate-key YAML: {exc}")
            continue
        if not isinstance(doc, dict):
            errors.append(f"{path}: workflow is not an object")
            continue
        triggers = doc.get("on", doc.get(True))
        pull_request = isinstance(triggers, dict) and "pull_request" in triggers
        jobs = doc.get("jobs", {})
        if not isinstance(jobs, dict):
            errors.append(f"{path}: jobs must be an object")
            continue
        workflow_permissions = doc.get("permissions", {}) or {}
        if not isinstance(workflow_permissions, dict):
            errors.append(f"{path}: workflow permissions must be an object")
            workflow_permissions = {}
        if workflow_permissions.get("id-token") == "write":
            errors.append(f"{path}: id-token write must be scoped to the consuming job")
        text = path.read_text(encoding="utf-8")
        if path.name == "validate.yml":
            for required in (
                "--cov=l9_deploy",
                "--cov-branch",
                "--cov-report=xml",
                "--cov-fail-under=75",
            ):
                if required not in text:
                    errors.append(f"{path}: validation workflow lacks coverage gate {required}")
        if path.name == "release.yml":
            detached_root = "${{ runner.temp }}/l9-deployment-platform-release"
            if detached_root not in text:
                errors.append(
                    f"{path}: release outputs must use the detached runner temp directory"
                )
            if text.count("--receipt") < 2:
                errors.append(f"{path}: archive build and validation must bind a release receipt")
            if '"dist/' in text or "'dist/" in text:
                errors.append(f"{path}: release outputs cannot be written inside the source tree")
            if "uv build" not in text or "--out-dir" not in text:
                errors.append(
                    f"{path}: Python distributions require an explicit detached output directory"
                )
            if "PYTHONDONTWRITEBYTECODE" not in text:
                errors.append(f"{path}: release workflow must suppress source-tree bytecode")
        if path.name in mutating_workflows:
            if "collect-approval" not in text or "approval-history.json" not in text:
                errors.append(f"{path}: mutating workflow lacks independent approval evidence")
            forbidden_approver = "--approved-by " + '"${{ github.actor }}"'
            if forbidden_approver in text:
                errors.append(f"{path}: triggering actor cannot be recorded as approver")
            authorize = jobs.get("authorize")
            if not isinstance(authorize, dict) or "environment" not in authorize:
                errors.append(f"{path}: mutating workflow lacks protected authorize job")
        for job_name, job_value in jobs.items():
            if not isinstance(job_value, dict):
                continue
            job = {str(key): value for key, value in job_value.items()}
            runs_on = job.get("runs-on")
            job_permissions = job.get("permissions", {}) or {}
            if not isinstance(job_permissions, dict):
                errors.append(f"{path}:{job_name}: permissions must be an object")
                job_permissions = {}
            id_token_write = job_permissions.get("id-token") == "write"
            if job_name == "authorize" and id_token_write:
                errors.append(f"{path}:{job_name}: approval jobs cannot request OIDC")
            if pull_request and "self-hosted" in str(runs_on):
                errors.append(
                    f"{path}:{job_name}: pull_request workflow cannot use self-hosted runner"
                )
            steps = job.get("steps", []) or []
            if not isinstance(steps, list):
                errors.append(f"{path}:{job_name}: steps must be a list")
                continue
            consumes_oidc = any(
                isinstance(step, dict)
                and "scripts/infisical-oidc-env.sh" in str(step.get("run", ""))
                for step in steps
            )
            if consumes_oidc and not id_token_write:
                errors.append(f"{path}:{job_name}: Infisical OIDC consumer lacks id-token write")
            if id_token_write and not consumes_oidc:
                errors.append(f"{path}:{job_name}: id-token write granted without OIDC consumption")
            for step in steps:
                if not isinstance(step, dict) or "uses" not in step:
                    continue
                use_value: Any = step["uses"]
                if not isinstance(use_value, str):
                    errors.append(f"{path}:{job_name}: action reference must be a string")
                    continue
                if use_value.startswith("./"):
                    if not _local_action_exists(root, use_value):
                        errors.append(
                            f"{path}:{job_name}: local action does not exist: {use_value}"
                        )
                    continue
                if sha.fullmatch(use_value) or allowed_versioned.fullmatch(use_value):
                    continue
                errors.append(
                    f"{path}:{job_name}: action is not SHA-pinned or governed @vN: {use_value}"
                )
    if errors:
        raise SystemExit("\n".join(errors))
    sys.stdout.write("workflow policy validation passed\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
import json
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from .canonical import atomic_write_json, file_sha256, sha256_digest
from .contracts.loader import load_document
from .contracts.models import DeploymentPlan, DeploymentProfile, ReleaseState, ServerProfile
from .contracts.validator import SchemaRegistry
from .errors import AuthorizationError, ContractError, L9DeployError
from .evidence.approval import verify_approval_receipt
from .evidence.ledger import ReceiptLedger
from .evidence.publisher import publish_json, publish_receipt
from .evidence.receipts import create_receipt, verify_receipt_digest
from .execution.backups import create_backup
from .execution.engine import execute_plan
from .execution.remote import Host, LocalExecutor, RemoteExecutor
from .execution.rollback import rollback_release
from .integrations import ansible as ansible_integration
from .integrations import opentofu
from .inventory.generator import generate_ansible_inventory
from .inventory.loader import load_fleet
from .inventory.resolver import resolve_target
from .logging import configure_logging
from .planning.planner import build_plan
from .redaction import redact
from .requests.idempotency import IdempotencyStore
from .requests.verifier import request_digest, verify_request

Handler = Callable[[argparse.Namespace], Any]


def repository_root(args: argparse.Namespace) -> Path:
    return Path(args.root).resolve()


def registry(args: argparse.Namespace) -> SchemaRegistry:
    return SchemaRegistry(repository_root(args) / "schemas" / "v1")


def object_document(path: Path) -> dict[str, Any]:
    value = load_document(path)
    if not isinstance(value, dict):
        raise ContractError(f"expected object document: {path}")
    return value


def emit(args: argparse.Namespace, value: Any) -> None:
    if args.output:
        path = Path(args.output)
        if isinstance(value, dict):
            publish_json(path, value)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(str(value), encoding="utf-8")
    if args.json or isinstance(value, (dict, list)):
        sys.stdout.write(json.dumps(redact(value), indent=2, sort_keys=True) + "\n")
    else:
        sys.stdout.write(str(value) + "\n")


def require_mutation_approval(args: argparse.Namespace, *, request_id: str) -> None:
    requester = getattr(args, "requester", None)
    if not isinstance(requester, str) or not requester:
        raise AuthorizationError("mutation requester identity is required")
    verify_approval_receipt(
        Path(args.approval_receipt),
        Path(args.approval_history),
        registry(args),
        request_id=request_id,
        requester=requester,
        environment=args.environment,
        plan_digest=args.expected_plan_digest,
        expected_run_id=args.approval_run_id,
    )


def cmd_approval_verify(args: argparse.Namespace) -> dict[str, Any]:
    require_mutation_approval(args, request_id=args.request_id or "manual-approval-verification")
    return {
        "status": "PASS",
        "request_id": args.request_id or "manual-approval-verification",
        "environment": args.environment,
        "plan_digest": args.expected_plan_digest,
    }


def cmd_contract_validate(args: argparse.Namespace) -> dict[str, Any]:
    document = load_document(Path(args.path))
    registry(args).validate(document, args.schema)
    return {
        "status": "PASS",
        "path": args.path,
        "schema": args.schema,
        "digest": file_sha256(Path(args.path)),
    }


def _request_context(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any], Any]:
    reg = registry(args)
    request = object_document(Path(args.request))
    fleet = load_fleet(Path(args.fleet), reg)
    verified = verify_request(
        request,
        fleet,
        reg,
        repository_root(args),
        evidence_root=Path(args.evidence_root),
    )
    return request, fleet, verified


def cmd_request_validate(args: argparse.Namespace) -> dict[str, Any]:
    request, _, verified = _request_context(args)
    return {
        "status": "PASS",
        "request_id": request["request_id"],
        "project_id": verified.project.id,
        "environment": verified.document.target.environment,
        "request_digest": request_digest(request),
    }


def cmd_request_inspect(args: argparse.Namespace) -> dict[str, Any]:
    request, _, verified = _request_context(args)
    return cast(
        dict[str, Any],
        redact(
            {
                "request": request,
                "registered_project": verified.project.model_dump(mode="json", by_alias=True),
                "profile": verified.profile.model_dump(mode="json", by_alias=True),
            }
        ),
    )


def _load_previous_state(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    value = object_document(path)
    current = value.get("current")
    return current if isinstance(current, dict) else None


def cmd_plan(args: argparse.Namespace) -> dict[str, Any]:
    _request, _fleet, verified = _request_context(args)
    plan = build_plan(
        verified,
        previous_release=_load_previous_state(
            Path(args.previous_state) if args.previous_state else None
        ),
    )
    document = plan.model_dump(mode="json", by_alias=True)
    registry(args).validate(document, "deployment-plan")
    return document


def _host_from_server(server: ServerProfile | dict[str, Any]) -> Host:
    typed = server if isinstance(server, ServerProfile) else ServerProfile.model_validate(server)
    return Host(typed.id, typed.private_ip, typed.ssh.user, typed.ssh.port)


def _fleet_items(fleet: dict[str, object], key: str) -> list[dict[str, Any]]:
    """Return the fleet document's list of items under ``key``.

    The fleet document is validated against the fleet-inventory schema before
    this helper is called, so ``key`` is guaranteed to resolve to a list of
    objects; the cast reflects that contract for the type checker.
    """
    return cast(list[dict[str, Any]], fleet[key])


def _target_executor(
    args: argparse.Namespace, fleet: dict[str, Any], project: dict[str, Any], environment: str
) -> Any:
    target = resolve_target(fleet, project, environment)
    if len(target.servers) != 1:
        raise ContractError(
            "version 1 rolling-single-host execution requires exactly one target server"
        )
    if args.local_executor_root:
        return LocalExecutor(Path(args.local_executor_root), timeout=args.timeout)
    return RemoteExecutor(_host_from_server(target.servers[0]), timeout=args.timeout)


def cmd_deploy(args: argparse.Namespace) -> dict[str, Any]:
    root = repository_root(args)
    reg = registry(args)
    plan_document = object_document(Path(args.plan))
    reg.validate(plan_document, "deployment-plan")
    plan = DeploymentPlan.model_validate(plan_document)
    if plan.environment != args.environment:
        raise AuthorizationError("command environment does not match plan")
    fleet = load_fleet(Path(args.fleet), reg)
    project = next(
        (item for item in _fleet_items(fleet, "projects") if item["id"] == plan.project_id),
        None,
    )
    if not isinstance(project, dict):
        raise ContractError("plan project is not present in fleet")
    profile_document = object_document(root / str(project["profile_path"]))
    reg.validate(profile_document, "deployment-profile")
    profile = DeploymentProfile.model_validate(profile_document)
    executor = _target_executor(args, fleet, project, args.environment)
    idempotency = IdempotencyStore(Path(args.idempotency_store))
    latest_pointer = Path(args.output or "receipts/latest/deployment.json")
    result = execute_plan(
        plan=plan,
        profile=profile,
        executor=executor,
        expected_plan_digest=args.expected_plan_digest,
        approval_receipt=Path(args.approval_receipt),
        approval_history=Path(args.approval_history),
        approval_run_id=args.approval_run_id,
        latest_pointer=latest_pointer,
        receipt_ledger_root=Path(args.receipt_ledger_root),
        lock_root=Path(args.lock_root),
        idempotency_store=idempotency,
        request_digest=args.request_digest
        or sha256_digest({"request_id": plan.request_id, "plan_digest": plan.plan_digest}),
        base_url=args.base_url,
        runtime_env_file=Path(args.runtime_env_file) if args.runtime_env_file else None,
    )
    args.output = None
    return result


def cmd_promote(args: argparse.Namespace) -> dict[str, Any]:
    plan = object_document(Path(args.plan))
    if plan["environment"] != args.environment or plan["plan_digest"] != args.expected_plan_digest:
        raise AuthorizationError("promotion command is not bound to the supplied plan")
    require_mutation_approval(
        args, request_id=str(plan.get("request_id") or args.request_id or "manual-promotion")
    )
    return {
        "status": "PASS",
        "message": "promotion is executed as an atomic step of deploy",
        "plan_digest": plan["plan_digest"],
    }


def _remote_state(executor: Any, project: str, environment: str) -> dict[str, Any]:
    path = f"/srv/l9/projects/{project}/{environment}/state.json"
    result = executor.run(["cat", path])
    value = json.loads(result.stdout)
    if not isinstance(value, dict):
        raise ContractError("runtime state is invalid")
    return value


def cmd_rollback(args: argparse.Namespace) -> dict[str, Any]:
    reg = registry(args)
    fleet = load_fleet(Path(args.fleet), reg)
    project = next(
        (item for item in _fleet_items(fleet, "projects") if item["id"] == args.project), None
    )
    if not isinstance(project, dict):
        raise ContractError("project is not registered")
    request_id = args.request_id or "manual-rollback"
    require_mutation_approval(args, request_id=request_id)
    executor = _target_executor(args, fleet, project, args.environment)
    state = _remote_state(executor, args.project, args.environment)
    previous = state.get("previous")
    previous_release = ReleaseState.model_validate(previous) if isinstance(previous, dict) else None
    current_release = (
        ReleaseState.model_validate(state.get("current"))
        if isinstance(state.get("current"), dict)
        else None
    )
    result = rollback_release(
        executor,
        args.project,
        args.environment,
        previous_release,
        failed_release=current_release,
    )
    receipt = create_receipt(
        "l9.rollback-receipt/v1",
        request_id=request_id,
        project_id=args.project,
        environment=args.environment,
        status="PASS",
        started_at=datetime.now(UTC).isoformat(),
        source_commit_sha=(previous or {}).get("source_commit_sha", "0" * 40),
        image_ref=cast(str, result["restored_image_ref"]),
        plan_digest=args.expected_plan_digest,
        previous_release=state.get("current"),
        steps=[result],
    )
    published = publish_receipt(
        Path(args.receipt_ledger_root),
        receipt,
        latest_pointer=Path(args.output) if args.output else None,
    )
    args.output = None
    return {**receipt, "canonical_path": str(published.canonical_path)}


def cmd_status(args: argparse.Namespace) -> dict[str, Any]:
    reg = registry(args)
    fleet = load_fleet(Path(args.fleet), reg)
    project = next(
        (item for item in _fleet_items(fleet, "projects") if item["id"] == args.project), None
    )
    if not isinstance(project, dict):
        raise ContractError("project is not registered")
    executor = _target_executor(args, fleet, project, args.environment)
    return cast(
        dict[str, Any],
        redact(_remote_state(executor, args.project, args.environment)),
    )


def cmd_receipt_verify(args: argparse.Namespace) -> dict[str, Any]:
    receipt = object_document(Path(args.receipt))
    schema_name = receipt.get("schema", "").removeprefix("l9.").removesuffix("/v1")
    registry(args).validate(receipt, schema_name)
    if not verify_receipt_digest(receipt):
        raise ContractError("receipt digest is invalid")
    return {
        "status": "PASS",
        "receipt_digest": receipt["receipt_digest"],
        "schema": receipt["schema"],
    }


def cmd_receipt_ledger_verify(args: argparse.Namespace) -> dict[str, Any]:
    return cast(dict[str, Any], ReceiptLedger(Path(args.ledger_root)).verify())


def cmd_inventory_generate(args: argparse.Namespace) -> dict[str, Any]:
    fleet = load_fleet(Path(args.fleet), registry(args))
    output = Path(args.output or "ansible/inventories/generated/hosts.yml")
    inventory = generate_ansible_inventory(fleet, output)
    # The command owns --output as the inventory destination. Prevent the generic
    # emitter from replacing that file with the summary document after return.
    args.output = None
    return {
        "status": "PASS",
        "output": str(output),
        "groups": sorted(inventory["all"]["children"]),
        "digest": sha256_digest(inventory),
    }


def cmd_inventory_validate(args: argparse.Namespace) -> dict[str, Any]:
    fleet = load_fleet(Path(args.fleet), registry(args))
    ids = [server["id"] for server in _fleet_items(fleet, "servers")]
    ips = [server["private_ip"] for server in _fleet_items(fleet, "servers")]
    if len(ids) != len(set(ids)) or len(ips) != len(set(ips)):
        raise ContractError("fleet server ids and private IPs must be unique")
    registered = set(ids)
    projects = _fleet_items(fleet, "projects")
    for project in projects:
        for config in project["environments"].values():
            unknown = set(config["server_ids"]) - registered
            if unknown:
                raise ContractError(
                    f"project {project['id']} references unknown servers: {sorted(unknown)}"
                )
    return {
        "status": "PASS",
        "servers": len(ids),
        "projects": len(projects),
        "digest": sha256_digest(fleet),
    }


def cmd_host_verify(args: argparse.Namespace) -> dict[str, Any]:
    reg = registry(args)
    fleet = load_fleet(Path(args.fleet), reg)
    server = next(
        (item for item in _fleet_items(fleet, "servers") if item["id"] == args.server), None
    )
    if not isinstance(server, dict):
        raise ContractError("server is not registered")
    executor = (
        LocalExecutor(Path(args.local_executor_root), timeout=args.timeout)
        if args.local_executor_root
        else RemoteExecutor(_host_from_server(server), timeout=args.timeout)
    )
    checks = []
    for name, command in [
        ("docker", ["docker", "version"]),
        ("compose", ["docker", "compose", "version"]),
        ("time", ["timedatectl", "show", "--property=NTPSynchronized", "--value"]),
        ("firewall", ["sh", "-lc", "command -v nft >/dev/null || command -v ufw >/dev/null"]),
        ("disk", ["sh", "-lc", "test $(df -P / | awk 'NR==2 {print $5}' | tr -d %) -lt 90"]),
    ]:
        result = executor.run(command, check=False)
        checks.append({"name": name, "status": "PASS" if result.returncode == 0 else "FAIL"})
    overall = "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL"
    document = {
        "schema": "l9.host-conformance/v1",
        "server_id": args.server,
        "checked_at": datetime.now(UTC).isoformat(),
        "status": overall,
        "checks": checks,
    }
    document["digest"] = sha256_digest(document)
    registry(args).validate(document, "host-conformance")
    return document


def cmd_fleet_verify(args: argparse.Namespace) -> dict[str, Any]:
    inventory = cmd_inventory_validate(args)
    return {
        **inventory,
        "host_checks": (
            "not executed by fleet verify; use host verify or fleet-conformance workflow"
        ),
    }


def cmd_infra_plan(args: argparse.Namespace) -> dict[str, Any]:
    receipt = opentofu.plan(
        Path(args.working_directory), args.environment, Path(args.plan_file), args.timeout
    )
    registry(args).validate(receipt, "infrastructure-plan")
    return receipt


def cmd_infra_apply(args: argparse.Namespace) -> dict[str, Any]:
    plan_receipt = object_document(Path(args.plan_receipt))
    registry(args).validate(plan_receipt, "infrastructure-plan")
    if (
        plan_receipt["environment"] != args.environment
        or plan_receipt["plan_digest"] != args.expected_plan_digest
    ):
        raise AuthorizationError("infrastructure apply is not bound to the supplied plan receipt")
    require_mutation_approval(args, request_id=args.request_id or "manual-infrastructure-apply")
    opentofu.apply(
        Path(args.working_directory),
        Path(args.plan_file),
        plan_receipt["plan_file_digest"],
        args.allow_destructive,
        args.timeout,
    )
    return {
        "status": "PASS",
        "environment": args.environment,
        "plan_digest": args.expected_plan_digest,
    }


def cmd_config_check(args: argparse.Namespace) -> dict[str, Any]:
    result = ansible_integration.check(
        Path(args.playbook), Path(args.inventory), args.limit, args.timeout
    )
    return {"status": "PASS", "stdout": result.stdout}


def cmd_config_apply(args: argparse.Namespace) -> dict[str, Any]:
    require_mutation_approval(args, request_id=args.request_id or "manual-configuration-apply")
    result = ansible_integration.apply(
        Path(args.playbook), Path(args.inventory), args.limit, args.timeout
    )
    return {"status": "PASS", "stdout": result.stdout}


def _project_profile(
    args: argparse.Namespace,
) -> tuple[dict[str, Any], DeploymentProfile, Any]:
    reg = registry(args)
    fleet = load_fleet(Path(args.fleet), reg)
    project = next(
        (item for item in _fleet_items(fleet, "projects") if item["id"] == args.project), None
    )
    if not isinstance(project, dict):
        raise ContractError("project is not registered")
    profile_document = object_document(repository_root(args) / project["profile_path"])
    reg.validate(profile_document, "deployment-profile")
    profile = DeploymentProfile.model_validate(profile_document)
    executor = _target_executor(args, fleet, project, args.environment)
    return project, profile, executor


def cmd_backup_create(args: argparse.Namespace) -> dict[str, Any]:
    _, profile, executor = _project_profile(args)
    require_mutation_approval(args, request_id=args.request_id or "manual-backup")
    return cast(
        dict[str, Any],
        create_backup(
            executor, profile, args.project, args.environment, args.request_id or "manual-backup"
        ),
    )


def cmd_backup_verify(args: argparse.Namespace) -> dict[str, Any]:
    _, profile, executor = _project_profile(args)
    config = profile.backup
    if config is None:
        raise ContractError("profile has no backup contract")
    substitutions = {
        "project": args.project,
        "environment": args.environment,
        "request_id": args.request_id or "verify",
    }
    command = [part.format_map(substitutions) for part in config.verify_command]
    result = executor.run(command, timeout=config.timeout_seconds, check=False)
    return {
        "status": "PASS" if result.returncode == 0 else "FAIL",
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def cmd_restore_test(args: argparse.Namespace) -> dict[str, Any]:
    _, profile, executor = _project_profile(args)
    require_mutation_approval(args, request_id=args.request_id or "manual-restore-test")
    config = profile.backup
    if config is None:
        raise ContractError("profile has no backup contract")
    substitutions = {
        "project": args.project,
        "environment": args.environment,
        "request_id": args.request_id or "restore-test",
    }
    command = [part.format_map(substitutions) for part in config.restore_test_command]
    result = executor.run(command, timeout=config.timeout_seconds)
    return {"status": "PASS", "stdout": result.stdout}


def cmd_adoption_render(args: argparse.Namespace) -> dict[str, Any]:
    source = repository_root(args) / "templates" / "consumer" / args.profile
    if not source.is_dir():
        raise ContractError(f"unknown consumer profile: {args.profile}")
    destination = Path(args.destination)
    if destination.exists() and any(destination.iterdir()) and not args.force:
        raise AuthorizationError(
            "destination is not empty; use --force to replace generated projection"
        )
    destination.mkdir(parents=True, exist_ok=True)
    values = {"PROJECT_ID": args.project_id, "REPOSITORY": args.repository, "IMAGE": args.image}
    written = []
    for item in sorted(source.rglob("*")):
        if item.is_dir():
            continue
        relative = item.relative_to(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        text = item.read_text(encoding="utf-8")
        for key, value in values.items():
            text = text.replace("{{" + key + "}}", value)
        target.write_text(text, encoding="utf-8")
        written.append(str(relative))
    manifest = {
        "schema": "l9.adoption-projection/v1",
        "profile": args.profile,
        "files": written,
        "source_digest": sha256_digest({"profile": args.profile, "files": written}),
    }
    atomic_write_json(destination / ".l9-deployment-projection.json", manifest, mode=0o640)
    return {
        "status": "PASS",
        "destination": str(destination),
        "files": written,
        "manifest_digest": sha256_digest(manifest),
    }


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", default=str(Path.cwd()))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--non-interactive", action="store_true")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--request-id")
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--evidence-root", default="artifacts/canonical-evidence")


def add_mutation(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--environment", required=True)
    parser.add_argument("--expected-plan-digest", required=True)
    parser.add_argument("--approval-receipt", required=True)
    parser.add_argument("--approval-history", default="approval-history.json")
    parser.add_argument("--approval-run-id", type=int)
    parser.add_argument("--requester")
    parser.add_argument("--receipt-ledger-root", default="receipts/ledger")


def leaf(
    parent: argparse._SubParsersAction[Any], name: str, handler: Handler, help_text: str
) -> argparse.ArgumentParser:
    parser = cast(argparse.ArgumentParser, parent.add_parser(name, help=help_text))
    add_common(parser)
    parser.set_defaults(handler=handler)
    return parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="l9-deploy")
    top = parser.add_subparsers(dest="group", required=True)
    approval = top.add_parser("approval")
    aps = approval.add_subparsers(dest="command", required=True)
    p = leaf(aps, "verify", cmd_approval_verify, "verify independent mutation approval")
    add_mutation(p)
    contract = top.add_parser("contract")
    cs = contract.add_subparsers(dest="command", required=True)
    p = leaf(cs, "validate", cmd_contract_validate, "validate a document against a platform schema")
    p.add_argument("--path", required=True)
    p.add_argument("--schema", required=True)
    request = top.add_parser("request")
    rs = request.add_subparsers(dest="command", required=True)
    for name, handler in [("validate", cmd_request_validate), ("inspect", cmd_request_inspect)]:
        p = leaf(rs, name, handler, f"{name} a release request")
        p.add_argument("--request", required=True)
        p.add_argument("--fleet", default="fleet/registry.yaml")
    p = leaf(top, "plan", cmd_plan, "create a deterministic deployment plan")
    p.add_argument("--request", required=True)
    p.add_argument("--fleet", default="fleet/registry.yaml")
    p.add_argument("--previous-state")
    p = leaf(top, "deploy", cmd_deploy, "execute an approved deployment plan")
    add_mutation(p)
    p.add_argument("--plan", required=True)
    p.add_argument("--fleet", default="fleet/registry.yaml")
    p.add_argument("--runtime-env-file")
    p.add_argument("--base-url")
    p.add_argument("--idempotency-store", default="state/runtime/idempotency.json")
    p.add_argument("--lock-root", default="state/runtime/locks")
    p.add_argument("--request-digest")
    p.add_argument("--local-executor-root")
    p = leaf(top, "promote", cmd_promote, "verify a promotion-bound plan")
    add_mutation(p)
    p.add_argument("--plan", required=True)
    p = leaf(top, "rollback", cmd_rollback, "restore the previous verified release")
    add_mutation(p)
    p.add_argument("--project", required=True)
    p.add_argument("--fleet", default="fleet/registry.yaml")
    p.add_argument("--local-executor-root")
    p = leaf(top, "status", cmd_status, "read current deployment state")
    p.add_argument("--project", required=True)
    p.add_argument("--environment", required=True)
    p.add_argument("--fleet", default="fleet/registry.yaml")
    p.add_argument("--local-executor-root")
    receipt = top.add_parser("receipt")
    rcs = receipt.add_subparsers(dest="command", required=True)
    p = leaf(rcs, "verify", cmd_receipt_verify, "verify schema and digest")
    p.add_argument("--receipt", required=True)
    p = leaf(rcs, "ledger-verify", cmd_receipt_ledger_verify, "verify append-only receipt ledger")
    p.add_argument("--ledger-root", required=True)
    inventory = top.add_parser("inventory")
    invs = inventory.add_subparsers(dest="command", required=True)
    p = leaf(invs, "generate", cmd_inventory_generate, "render Ansible inventory")
    p.add_argument("--fleet", default="fleet/registry.yaml")
    p = leaf(invs, "validate", cmd_inventory_validate, "validate fleet references")
    p.add_argument("--fleet", default="fleet/registry.yaml")
    host = top.add_parser("host")
    hs = host.add_subparsers(dest="command", required=True)
    p = leaf(hs, "verify", cmd_host_verify, "run host conformance checks")
    p.add_argument("--server", required=True)
    p.add_argument("--fleet", default="fleet/registry.yaml")
    p.add_argument("--local-executor-root")
    fleet = top.add_parser("fleet")
    fs = fleet.add_subparsers(dest="command", required=True)
    p = leaf(fs, "verify", cmd_fleet_verify, "validate fleet desired state")
    p.add_argument("--fleet", default="fleet/registry.yaml")
    infra = top.add_parser("infra")
    ins = infra.add_subparsers(dest="command", required=True)
    p = leaf(ins, "plan", cmd_infra_plan, "produce an OpenTofu plan receipt")
    p.add_argument("--environment", required=True)
    p.add_argument("--working-directory", required=True)
    p.add_argument("--plan-file", required=True)
    p = leaf(ins, "apply", cmd_infra_apply, "apply an approved OpenTofu plan")
    add_mutation(p)
    p.add_argument("--working-directory", required=True)
    p.add_argument("--plan-file", required=True)
    p.add_argument("--plan-receipt", required=True)
    p.add_argument("--allow-destructive", action="store_true")
    config = top.add_parser("config")
    cos = config.add_subparsers(dest="command", required=True)
    p = leaf(cos, "check", cmd_config_check, "run Ansible check mode")
    p.add_argument("--playbook", required=True)
    p.add_argument("--inventory", required=True)
    p.add_argument("--limit")
    p = leaf(cos, "apply", cmd_config_apply, "apply approved Ansible configuration")
    add_mutation(p)
    p.add_argument("--playbook", required=True)
    p.add_argument("--inventory", required=True)
    p.add_argument("--limit")
    backup = top.add_parser("backup")
    bs = backup.add_subparsers(dest="command", required=True)
    p = leaf(bs, "create", cmd_backup_create, "create a policy-bound backup")
    add_mutation(p)
    p.add_argument("--project", required=True)
    p.add_argument("--fleet", default="fleet/registry.yaml")
    p.add_argument("--local-executor-root")
    p = leaf(bs, "verify", cmd_backup_verify, "verify a registered backup")
    p.add_argument("--project", required=True)
    p.add_argument("--environment", required=True)
    p.add_argument("--fleet", default="fleet/registry.yaml")
    p.add_argument("--local-executor-root")
    restore = top.add_parser("restore")
    rss = restore.add_subparsers(dest="command", required=True)
    p = leaf(rss, "test", cmd_restore_test, "execute an isolated restore test")
    add_mutation(p)
    p.add_argument("--project", required=True)
    p.add_argument("--fleet", default="fleet/registry.yaml")
    p.add_argument("--local-executor-root")
    adoption = top.add_parser("adoption")
    ads = adoption.add_subparsers(dest="command", required=True)
    p = leaf(ads, "render", cmd_adoption_render, "render a thin consumer projection")
    p.add_argument("--profile", required=True)
    p.add_argument("--project-id", required=True)
    p.add_argument("--repository", required=True)
    p.add_argument("--image", required=True)
    p.add_argument("--destination", required=True)
    p.add_argument("--force", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.log_level, args.json)
    try:
        result = args.handler(args)
        emit(args, result)
        if isinstance(result, dict) and result.get("status") == "FAIL":
            return 1
        return 0
    except L9DeployError as exc:
        payload = {"status": "FAIL", "error": str(exc), "error_type": type(exc).__name__}
        if getattr(args, "json", False):
            sys.stderr.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        else:
            sys.stderr.write(f"ERROR: {exc}\n")
        return exc.exit_code
    except Exception as exc:
        payload = {"status": "FAIL", "error": str(exc), "error_type": type(exc).__name__}
        if getattr(args, "json", False):
            sys.stderr.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        else:
            sys.stderr.write(f"ERROR: {exc}\n")
        return 7


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [authorization, github-actions]
tags: [L9_CONTRACT, approval-collector]
owner: platform
status: active
--- /L9_META ---

Create a digest-bound receipt from GitHub's workflow-run approval-history API response.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from uuid import uuid4

from _bootstrap import add_repository_src

add_repository_src()

from l9_deploy.canonical import file_sha256, load_structured, sha256_digest  # noqa: E402


def records(value: object) -> list[dict[str, object]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        nested = value.get("reviews") or value.get("approvals")
        if isinstance(nested, list):
            return [item for item in nested if isinstance(item, dict)]
    raise ValueError("unsupported approval-history response")


def environment_names(record: dict[str, object]) -> set[str]:
    value = record.get("environments")
    if not isinstance(value, list):
        return set()
    return {
        item["name"]
        for item in value
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }


def reviewer(record: dict[str, object]) -> str | None:
    value = record.get("user")
    if isinstance(value, dict) and isinstance(value.get("login"), str):
        return value["login"]
    return None


def approval_time(record: dict[str, object]) -> str | None:
    for field in ("submitted_at", "approved_at", "created_at"):
        value = record.get(field)
        if isinstance(value, str) and value:
            return value
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--approval-history", required=True, type=Path)
    parser.add_argument("--request-id", required=True)
    parser.add_argument("--requester", required=True)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--plan-digest", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--run-id", required=True, type=int)
    parser.add_argument("--run-attempt", required=True, type=int)
    parser.add_argument("--job-id", required=True, type=int)
    parser.add_argument("--workflow-ref", required=True)
    parser.add_argument("--approval-api-url", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    history = load_structured(args.approval_history)
    candidates: list[tuple[str, str]] = []
    for record in records(history):
        if record.get("state") != "approved" or args.environment not in environment_names(record):
            continue
        actor = reviewer(record)
        timestamp = approval_time(record)
        if actor and timestamp and actor != args.requester:
            candidates.append((actor, timestamp))
    if not candidates:
        raise SystemExit("no independent approved reviewer found for the protected environment")
    approved_by, approved_at = candidates[-1]

    document: dict[str, object] = {
        "schema": "l9.approval-receipt/v1",
        "approval_id": str(uuid4()),
        "request_id": args.request_id,
        "environment": args.environment,
        "plan_digest": args.plan_digest,
        "requester": args.requester,
        "approved": True,
        "approved_by": approved_by,
        "approved_at": approved_at,
        "authorization_method": "github_protected_environment_review",
        "workflow": {
            "repository": args.repository,
            "run_id": args.run_id,
            "run_attempt": args.run_attempt,
            "job_id": args.job_id,
            "workflow_ref": args.workflow_ref,
            "environment": args.environment,
            "approval_api_url": args.approval_api_url,
            "approval_record_digest": file_sha256(args.approval_history),
        },
    }
    digest_input = deepcopy(document)
    document["receipt_digest"] = sha256_digest(digest_input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output.chmod(0o600)
    sys.stdout.write(f"approval_receipt={args.output}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

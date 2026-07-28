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
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from _bootstrap import add_repository_src

add_repository_src()

from l9_deploy.canonical import sha256_digest  # noqa: E402
from l9_deploy.contracts.loader import load_document  # noqa: E402
from l9_deploy.contracts.validator import SchemaRegistry  # noqa: E402


def object_document(path: Path) -> dict[str, Any]:
    value = load_document(path)
    if not isinstance(value, dict):
        raise TypeError(f"expected object document: {path}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--staging-receipt", required=True, type=Path)
    parser.add_argument("--expected-staging-receipt-digest", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--schemas", default=Path("schemas/v1"), type=Path)
    args = parser.parse_args()

    request = object_document(args.request)
    receipt = object_document(args.staging_receipt)
    actual_receipt_digest = sha256_digest(receipt)
    if actual_receipt_digest != args.expected_staging_receipt_digest:
        raise ValueError("staging receipt digest mismatch")
    if receipt.get("status") != "PASS" or receipt.get("environment") != "staging":
        raise ValueError("only a passing staging deployment may be promoted")
    if receipt.get("image_ref") != request["artifact"]["image_ref"]:
        raise ValueError("promotion image does not match the staged image")

    promoted = json.loads(json.dumps(request))
    promoted["request_id"] = str(uuid.uuid4())
    promoted["idempotency_key"] = (
        f"promote:{promoted['source']['commit_sha']}:{promoted['artifact']['digest']}"
    )
    promoted["target"]["environment"] = "production"
    promoted["requested_at"] = datetime.now(UTC).isoformat()
    promoted["requested_by"] = "l9-deployment-platform/promote"

    SchemaRegistry(args.schemas).validate(promoted, "deployment-request")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(promoted, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

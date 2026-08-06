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

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from ..canonical import sha256_digest
from ..contracts.validator import default_registry
from ..redaction import redact


def evidence_record(
    record_type: str,
    status: str,
    subject: dict[str, Any],
    assertions: list[dict[str, Any]],
    artifacts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    record = {
        "schema": "l9.evidence-record/v1",
        "record_id": str(uuid4()),
        "record_type": record_type,
        "status": status,
        "timestamp": datetime.now(UTC).isoformat(),
        "subject": redact(subject),
        "assertions": redact(assertions),
        "artifacts": redact(artifacts or []),
    }
    digest_input = deepcopy(record)
    record["digest"] = sha256_digest(digest_input)
    default_registry().validate(record, "evidence-record")
    return record

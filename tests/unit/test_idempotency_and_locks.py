"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer:
- tests
tags:
- L9_META
- deployment-platform
owner: platform
status: active
--- /L9_META ---
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from l9_deploy.contracts.models import IdempotencyEntry
from l9_deploy.errors import AuthorizationError, ExecutionError
from l9_deploy.execution.locks import environment_lock
from l9_deploy.requests.idempotency import IdempotencyStore

REQUEST_DIGEST = "sha256:" + "1" * 64
OTHER_REQUEST_DIGEST = "sha256:" + "2" * 64
RECEIPT_DIGEST = "sha256:" + "a" * 64
OTHER_RECEIPT_DIGEST = "sha256:" + "b" * 64


def test_idempotency_store_replays_complete_request(tmp_path: Path) -> None:
    store = IdempotencyStore(tmp_path / "idempotency.json")
    assert store.begin("key", REQUEST_DIGEST) is None
    store.prepare_completion("key", RECEIPT_DIGEST)
    store.complete("key", RECEIPT_DIGEST)
    replay = store.begin("key", REQUEST_DIGEST)
    assert replay is not None
    assert replay.status == "COMPLETE"
    assert replay.receipt_digest == RECEIPT_DIGEST


def test_idempotency_store_rejects_key_reuse(tmp_path: Path) -> None:
    store = IdempotencyStore(tmp_path / "idempotency.json")
    store.begin("key", REQUEST_DIGEST)
    with pytest.raises(AuthorizationError, match="different request"):
        store.begin("key", OTHER_REQUEST_DIGEST)


def test_idempotency_store_retries_failed_request_as_in_progress(tmp_path: Path) -> None:
    store = IdempotencyStore(tmp_path / "idempotency.json")
    store.begin("key", REQUEST_DIGEST)
    store.fail("key", "candidate health check failed")

    assert store.begin("key", REQUEST_DIGEST) is None
    current = store.get("key")
    assert current is not None
    assert current.status == "IN_PROGRESS"
    assert current.reason is None
    assert current.receipt_digest is None


def test_idempotency_store_enforces_transition_order_and_immutability(
    tmp_path: Path,
) -> None:
    store = IdempotencyStore(tmp_path / "idempotency.json")
    store.begin("key", REQUEST_DIGEST)

    with pytest.raises(AuthorizationError, match="IN_PROGRESS -> COMPLETE"):
        store.complete("key", RECEIPT_DIGEST)

    store.prepare_completion("key", RECEIPT_DIGEST)
    store.prepare_completion("key", RECEIPT_DIGEST)  # exact replay is idempotent
    with pytest.raises(AuthorizationError, match="cannot be replaced"):
        store.prepare_completion("key", OTHER_RECEIPT_DIGEST)

    store.complete("key", RECEIPT_DIGEST)
    store.complete("key", RECEIPT_DIGEST)  # exact replay is idempotent
    with pytest.raises(AuthorizationError, match="immutable"):
        store.fail("key", "late failure")


def test_idempotency_store_rejects_invalid_keys_digests_and_reasons(
    tmp_path: Path,
) -> None:
    store = IdempotencyStore(tmp_path / "idempotency.json")
    with pytest.raises(AuthorizationError, match="invalid idempotency key"):
        store.begin("", REQUEST_DIGEST)
    with pytest.raises(AuthorizationError, match="invalid idempotency key"):
        store.begin("key", "sha256:bad")

    store.begin("key", REQUEST_DIGEST)
    with pytest.raises(AuthorizationError, match="transition payload"):
        store.prepare_completion("key", "sha256:bad")
    with pytest.raises(AuthorizationError, match="transition payload"):
        store.fail("key", "   ")


def test_idempotency_model_rejects_inconsistent_status_fields() -> None:
    with pytest.raises(ValidationError):
        IdempotencyEntry.model_validate(
            {
                "request_digest": REQUEST_DIGEST,
                "status": "COMPLETE",
                "updated_at": "2026-07-21T00:00:00Z",
                "receipt_digest": None,
            }
        )
    with pytest.raises(ValidationError):
        IdempotencyEntry.model_validate(
            {
                "request_digest": REQUEST_DIGEST,
                "status": "FAIL",
                "updated_at": "2026-07-21T00:00:00Z",
                "receipt_digest": RECEIPT_DIGEST,
                "reason": "failed",
            }
        )


def test_persisted_idempotency_state_uses_wire_schema_name(tmp_path: Path) -> None:
    path = tmp_path / "idempotency.json"
    store = IdempotencyStore(path)
    store.begin("key", REQUEST_DIGEST)
    persisted = json.loads(path.read_text(encoding="utf-8"))
    assert persisted["schema"] == "l9.idempotency-store/v1"
    assert "schema_id" not in persisted


def test_environment_lock_is_fail_closed(tmp_path: Path) -> None:
    with (
        environment_lock(tmp_path, "production"),
        pytest.raises(ExecutionError),
        environment_lock(tmp_path, "production"),
    ):
        pass

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
import math
from pathlib import Path

import pytest

from l9_deploy.canonical import atomic_write_json, canonical_json_bytes, file_sha256, sha256_digest


def test_canonical_json_is_key_order_independent() -> None:
    left = {"b": 2, "a": [3, 1]}
    right = {"a": [3, 1], "b": 2}
    assert canonical_json_bytes(left) == canonical_json_bytes(right)
    assert sha256_digest(left) == sha256_digest(right)


def test_atomic_write_json_sets_content_and_digest(tmp_path: Path) -> None:
    path = tmp_path / "receipt.json"
    atomic_write_json(path, {"z": 1, "a": 2})
    assert json.loads(path.read_text(encoding="utf-8")) == {"a": 2, "z": 1}
    assert file_sha256(path).startswith("sha256:")


def test_canonical_json_rejects_non_finite_numbers() -> None:
    for value in (math.nan, math.inf, -math.inf):
        with pytest.raises(ValueError):
            canonical_json_bytes({"value": value})


def test_atomic_json_rejects_non_finite_numbers(tmp_path: Path) -> None:
    path = tmp_path / "invalid.json"
    with pytest.raises(ValueError):
        atomic_write_json(path, {"value": math.nan})
    assert not path.exists()

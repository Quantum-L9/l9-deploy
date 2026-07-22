"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests, contracts, governance]
tags: [L9_TEST, alias-policy, NAME-001]
owner: platform
status: active
--- /L9_META ---
"""
from __future__ import annotations

import ast
from pathlib import Path

from l9_deploy.contracts.alias_policy import (
    ALIAS_EXCEPTION_PATH,
    allowed_alias_call_ids,
)
from l9_deploy.contracts.catalog import WIRE_CONTRACTS

ROOT = Path(__file__).resolve().parents[2]


def test_only_cataloged_schema_identity_aliases_are_allowed() -> None:
    path = ROOT / ALIAS_EXCEPTION_PATH
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    allowed = allowed_alias_call_ids(tree, ALIAS_EXCEPTION_PATH)
    alias_calls = {
        id(node)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "Field"
        and any(keyword.arg == "alias" for keyword in node.keywords)
    }
    assert alias_calls == set(allowed)
    assert len(allowed) == len(WIRE_CONTRACTS)


def test_alias_exception_is_path_and_shape_bound() -> None:
    exact = ast.parse('schema_id: Literal["l9.example/v1"] = Field(alias="schema")\n')
    assert len(allowed_alias_call_ids(exact, ALIAS_EXCEPTION_PATH)) == 1
    assert allowed_alias_call_ids(exact, "src/other.py") == frozenset()

    wrong_name = ast.parse('other: Literal["l9.example/v1"] = Field(alias="schema")\n')
    wrong_alias = ast.parse('schema_id: Literal["l9.example/v1"] = Field(alias="other")\n')
    wrong_type = ast.parse('schema_id: str = Field(alias="schema")\n')
    assert allowed_alias_call_ids(wrong_name, ALIAS_EXCEPTION_PATH) == frozenset()
    assert allowed_alias_call_ids(wrong_alias, ALIAS_EXCEPTION_PATH) == frozenset()
    assert allowed_alias_call_ids(wrong_type, ALIAS_EXCEPTION_PATH) == frozenset()

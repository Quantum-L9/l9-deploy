"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [contracts, governance]
tags: [L9_CONTRACT, alias-policy, wire-boundary]
owner: platform
status: active
--- /L9_META ---

Narrow exception policy for the durable v1 ``schema`` wire identity.

L9 NAME-001 continues to prohibit Pydantic aliases generally. The only permitted
alias is a top-level contract identity declared as ``schema_id`` in the canonical
contract model module and serialized as the established wire key ``schema``.
"""

from __future__ import annotations

import ast
import re
from typing import Final

ALIAS_EXCEPTION_PATH: Final = "src/l9_deploy/contracts/models.py"
RUNTIME_FIELD_NAME: Final = "schema_id"
WIRE_FIELD_NAME: Final = "schema"
SCHEMA_ID_PATTERN: Final = re.compile(r"^l9\.[a-z0-9.-]+/v[1-9][0-9]*$")


def _field_call(node: ast.AST | None) -> ast.Call | None:
    if not isinstance(node, ast.Call):
        return None
    if not isinstance(node.func, ast.Name) or node.func.id != "Field":
        return None
    return node


def _keyword_string(call: ast.Call, name: str) -> str | None:
    for keyword in call.keywords:
        if keyword.arg != name:
            continue
        if isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
            return keyword.value.value
        return None
    return None


def _literal_schema_id(annotation: ast.AST) -> str | None:
    if not isinstance(annotation, ast.Subscript):
        return None
    if not isinstance(annotation.value, ast.Name) or annotation.value.id != "Literal":
        return None
    value = annotation.slice
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        return value.value
    return None


def is_allowed_schema_identity_alias(node: ast.AnnAssign, relative_path: str) -> bool:
    """Return true only for the catalog-backed ``schema_id`` wire alias shape."""
    if relative_path != ALIAS_EXCEPTION_PATH:
        return False
    if not isinstance(node.target, ast.Name) or node.target.id != RUNTIME_FIELD_NAME:
        return False
    call = _field_call(node.value)
    if call is None or _keyword_string(call, "alias") != WIRE_FIELD_NAME:
        return False
    if any(keyword.arg in {"validation_alias", "serialization_alias"} for keyword in call.keywords):
        return False
    schema_id = _literal_schema_id(node.annotation)
    return schema_id is not None and SCHEMA_ID_PATTERN.fullmatch(schema_id) is not None


def allowed_alias_call_ids(tree: ast.AST, relative_path: str) -> frozenset[int]:
    """Return call identities for the exact alias exception in one syntax tree."""
    allowed: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and is_allowed_schema_identity_alias(
            node, relative_path
        ):
            call = _field_call(node.value)
            if call is not None:
                allowed.add(id(call))
    return frozenset(allowed)

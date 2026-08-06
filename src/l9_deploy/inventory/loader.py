"""--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [inventory]
tags: [L9_CONTRACT, fleet]
owner: platform
status: active
--- /L9_META ---"""

from __future__ import annotations

from pathlib import Path

from ..contracts.loader import load_document
from ..contracts.validator import SchemaRegistry
from ..errors import ContractError


def load_fleet(path: Path, registry: SchemaRegistry) -> dict[str, object]:
    value = load_document(path)
    if not isinstance(value, dict):
        raise ContractError("fleet inventory must be an object")
    registry.validate(value, "fleet-inventory")
    return value

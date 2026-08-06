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

from pathlib import Path
from typing import Any

from ..canonical import load_structured
from ..errors import ContractError


def load_document(path: Path) -> Any:
    if not path.is_file():
        raise ContractError(f"document not found: {path}")
    try:
        return load_structured(path)
    except Exception as exc:
        raise ContractError(f"unable to parse document {path}: {exc}") from exc

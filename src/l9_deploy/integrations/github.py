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

import json
import os
from pathlib import Path
from typing import Any

from ..errors import AuthorizationError, ContractError
from ..requests.parser import parse_repository_dispatch


def load_github_event(path: Path | None = None) -> dict[str, Any]:
    event_path = path or Path(os.environ.get("GITHUB_EVENT_PATH", ""))
    if not event_path.is_file():
        raise ContractError("GitHub event payload is unavailable")
    value = json.loads(event_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ContractError("GitHub event must be a JSON object")
    return value


def request_from_github_event(path: Path | None = None) -> dict[str, Any]:
    return parse_repository_dispatch(load_github_event(path))


def require_private_control_repository(expected: str = "Quantum-L9/l9-deployment-platform") -> None:
    actual = os.environ.get("GITHUB_REPOSITORY")
    if actual != expected:
        observed = actual or "<unset>"
        raise AuthorizationError(f"deployment workflow may run only in {expected}; got {observed}")

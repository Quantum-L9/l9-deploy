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

import re

from ..errors import CompatibilityError

SCHEMA_PATTERN = re.compile(r"^l9\.[a-z0-9-]+/v(?P<major>[1-9][0-9]*)$")
SUPPORTED_MAJOR = 1


def require_supported_schema(schema_name: str) -> int:
    match = SCHEMA_PATTERN.fullmatch(schema_name)
    if not match:
        raise CompatibilityError(f"invalid schema identifier: {schema_name!r}")
    major = int(match.group("major"))
    if major != SUPPORTED_MAJOR:
        raise CompatibilityError(
            f"unsupported schema major v{major}; supported major is v{SUPPORTED_MAJOR}"
        )
    return major

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
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

SECRET_KEY = re.compile(
    r"(?i)(token|secret|password|authorization|private[_-]?key|api[_-]?key|"
    r"credential|database[_-]?url)"
)
AUTH_URL = re.compile(r"(?P<scheme>[a-z][a-z0-9+.-]*://)(?P<credentials>[^/@\s]+)@", re.IGNORECASE)
BEARER = re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+")
GITHUB_TOKEN = re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")


def redact_text(value: str, extra_secrets: Iterable[str] = ()) -> str:
    for secret in sorted({item for item in extra_secrets if item}, key=len, reverse=True):
        value = value.replace(secret, "[REDACTED]")
    value = AUTH_URL.sub(r"\g<scheme>[REDACTED]@", value)
    value = BEARER.sub("Bearer [REDACTED]", value)
    return GITHUB_TOKEN.sub("[REDACTED]", value)


def redact(value: Any, key: str | None = None) -> Any:
    if key is not None and SECRET_KEY.search(key):
        return "[REDACTED]"
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, Mapping):
        return {str(k): redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [redact(item) for item in value]
    return value

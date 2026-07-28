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

from l9_deploy.redaction import redact, redact_text


def test_nested_secret_fields_are_redacted() -> None:
    value = {
        "token": "secret-token",
        "nested": {"password": "very-secret", "safe": "visible"},
        "items": [{"api_key": "key"}],
    }
    result = redact(value)
    assert result["token"] == "[REDACTED]"  # noqa: S105
    assert result["nested"]["password"] == "[REDACTED]"  # noqa: S105
    assert result["nested"]["safe"] == "visible"
    assert result["items"][0]["api_key"] == "[REDACTED]"


def test_text_redaction_masks_credentials() -> None:
    text = "Authorization: Bearer abcdefghijklmnop DATABASE_URL=postgres://u:p@host/db"
    redacted = redact_text(text)
    assert "abcdefghijklmnop" not in redacted
    assert "postgres://u:p@" not in redacted


def test_text_redaction_masks_explicit_secret_values() -> None:
    text = "deploy token=custom-secret-value completed"
    redacted = redact_text(text, ["custom-secret-value"])
    assert "custom-secret-value" not in redacted
    assert "[REDACTED]" in redacted

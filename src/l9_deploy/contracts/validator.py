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

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from ..errors import ContractError
from .compatibility import require_supported_schema
from .loader import load_document

SCHEMA_FILES = {
    "deployment-profile": "deployment-profile.schema.json",
    "server-profile": "server-profile.schema.json",
    "fleet-inventory": "fleet-inventory.schema.json",
    "deployment-request": "deployment-request.schema.json",
    "release-evidence-reference": "release-evidence-reference.schema.json",
    "deployment-plan": "deployment-plan.schema.json",
    "deployment-receipt": "deployment-receipt.schema.json",
    "rollback-receipt": "rollback-receipt.schema.json",
    "backup-receipt": "backup-receipt.schema.json",
    "migration-receipt": "migration-receipt.schema.json",
    "health-probe": "health-probe.schema.json",
    "host-conformance": "host-conformance.schema.json",
    "infrastructure-plan": "infrastructure-plan.schema.json",
    "infrastructure-receipt": "infrastructure-receipt.schema.json",
    "evidence-record": "evidence-record.schema.json",
    "ci-gate-binding": "ci-gate-binding.schema.json",
    "release-artifact-binding": "release-artifact-binding.schema.json",
    "approval-receipt": "approval-receipt.schema.json",
    "idempotency-store": "idempotency-store.schema.json",
    "repository-release-receipt": "repository-release-receipt.schema.json",
}


class SchemaRegistry:
    def __init__(self, schema_root: Path) -> None:
        self.schema_root = schema_root
        self._schemas: dict[str, dict[str, Any]] = {}
        resources: list[tuple[str, Resource[Any]]] = []
        for schema_path in sorted(schema_root.glob("*.schema.json")):
            schema = load_document(schema_path)
            if not isinstance(schema, dict):
                raise ContractError(f"schema is not an object: {schema_path}")
            self._schemas[schema_path.name] = schema
            schema_id = schema.get("$id")
            if isinstance(schema_id, str):
                resources.append((schema_id, Resource.from_contents(schema)))
        self._registry = Registry().with_resources(resources)

    def schema(self, name: str) -> dict[str, Any]:
        filename = SCHEMA_FILES.get(name, name)
        try:
            return self._schemas[filename]
        except KeyError as exc:
            raise ContractError(f"unknown schema: {name}") from exc

    def validate(self, document: Any, schema_name: str) -> None:
        if isinstance(document, dict) and isinstance(document.get("schema"), str):
            require_supported_schema(document["schema"])
        schema = self.schema(schema_name)
        validator = Draft202012Validator(
            schema, registry=self._registry, format_checker=FormatChecker()
        )
        errors = sorted(validator.iter_errors(document), key=lambda item: list(item.path))
        if errors:
            formatted = []
            for error in errors:
                location = ".".join(str(part) for part in error.absolute_path) or "$"
                formatted.append(f"{location}: {error.message}")
            raise ContractError("contract validation failed:\n" + "\n".join(formatted))


def default_registry(root: Path | None = None) -> SchemaRegistry:
    if root is None:
        root = Path(__file__).resolve().parents[3] / "schemas" / "v1"
    return SchemaRegistry(root)

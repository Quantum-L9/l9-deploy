#!/usr/bin/env python3
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
import sys
from pathlib import Path

from _bootstrap import add_repository_src

add_repository_src()

from jsonschema import Draft202012Validator

from l9_deploy.contracts.catalog import WIRE_CONTRACTS  # noqa: E402
from l9_deploy.contracts.models import FrozenModel  # noqa: E402
from l9_deploy.contracts.loader import load_document  # noqa: E402
from l9_deploy.contracts.validator import SchemaRegistry  # noqa: E402


def _contract_models() -> set[type[FrozenModel]]:
    pending = list(FrozenModel.__subclasses__())
    discovered: set[type[FrozenModel]] = set()
    while pending:
        model = pending.pop()
        if model in discovered:
            continue
        discovered.add(model)
        pending.extend(model.__subclasses__())
    return {model for model in discovered if "schema_id" in model.model_fields}


def validate_wire_model_parity(registry: SchemaRegistry) -> None:
    """Prove runtime DTOs preserve published v1 wire names and requiredness."""
    catalog_models = {definition.model for definition in WIRE_CONTRACTS}
    runtime_models = _contract_models()
    if catalog_models != runtime_models:
        raise ValueError(
            "wire contract catalog drift: "
            f"uncataloged={sorted(model.__name__ for model in runtime_models - catalog_models)} "
            f"missing_runtime={sorted(model.__name__ for model in catalog_models - runtime_models)}"
        )
    for definition in WIRE_CONTRACTS:
        generated = definition.model.model_json_schema(by_alias=True)
        committed = registry.schema(definition.name)

        generated_properties = generated.get("properties")
        committed_properties = committed.get("properties")
        if not isinstance(generated_properties, dict) or not isinstance(
            committed_properties, dict
        ):
            raise ValueError(f"contract properties are malformed: {definition.name}")

        if "schema_id" in generated_properties or "schema" not in generated_properties:
            raise ValueError(f"runtime field leaked into wire schema: {definition.name}")
        generated_schema = generated_properties["schema"]
        committed_schema = committed_properties.get("schema")
        if not isinstance(generated_schema, dict) or not isinstance(committed_schema, dict):
            raise ValueError(f"schema identity is malformed: {definition.name}")
        if generated_schema.get("const") != definition.schema_id:
            raise ValueError(f"runtime schema identity drift: {definition.name}")
        if committed_schema.get("const") != definition.schema_id:
            raise ValueError(f"published schema identity drift: {definition.name}")

        generated_names = set(generated_properties)
        committed_names = set(committed_properties)
        if generated_names != committed_names:
            raise ValueError(
                f"top-level field drift for {definition.name}: "
                f"runtime_only={sorted(generated_names - committed_names)} "
                f"schema_only={sorted(committed_names - generated_names)}"
            )

        generated_required = set(generated.get("required", []))
        committed_required = set(committed.get("required", []))
        if generated_required != committed_required:
            raise ValueError(
                f"required-field drift for {definition.name}: "
                f"runtime_only={sorted(generated_required - committed_required)} "
                f"schema_only={sorted(committed_required - generated_required)}"
            )


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    registry = SchemaRegistry(root / "schemas/v1")

    schema_files = sorted((root / "schemas/v1").glob("*.schema.json"))
    for schema_file in schema_files:
        schema = load_document(schema_file)
        Draft202012Validator.check_schema(schema)

    validate_wire_model_parity(registry)

    checks: list[tuple[Path, str]] = [
        (root / "fleet/registry.yaml", "fleet-inventory"),
        (
            root / "integrations/consumers/seo-bot.deployment.yaml",
            "deployment-profile",
        ),
    ]
    checks.extend(
        (path, "health-probe") for path in sorted((root / "deployment/probes").glob("*.yaml"))
    )
    for path, schema_name in checks:
        registry.validate(load_document(path), schema_name)

    sys.stdout.write(
        f"validated {len(checks)} canonical documents and {len(schema_files)} schemas\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

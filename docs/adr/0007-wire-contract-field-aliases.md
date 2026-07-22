<!-- L9_META
l9_schema: 1
origin: l9-deployment-platform
layer: [documentation, architecture, contracts]
tags: [L9_META, deployment-platform, ADR, wire-contract]
owner: platform
status: active
/L9_META -->
# ADR-0007: Preserve wire identity through explicit field aliases

- Status: Accepted
- Date: 2026-07-21

## Context

The durable v1 contracts use the self-describing wire key `schema`. Pydantic also exposes an
inherited compatibility member named `schema`, so declaring `schema` directly as a model field
produced import-time namespace warnings. Renaming the wire key would break archived requests,
receipts, schemas, hashes, signatures, and downstream consumers.

## Decision

- Preserve `schema` in every v1 YAML and JSON artifact.
- Represent the field in Python as `schema_id` with `Field(alias="schema")`.
- Accept aliases and reject runtime field names when validating boundary payloads.
- Serialize contract models by alias, with explicit `by_alias=True` at durable boundaries.
- Treat published JSON Schema as the wire-contract authority and Pydantic models as strict runtime
  projections.
- Enforce top-level field, requiredness, identity, round-trip, and schema-export parity in tests and
  `scripts/validate-contracts.py`.
- Use aliases only for lexical name differences. Add semantic mappers only when values or structure
  change meaning.
- Run the test suite with warnings elevated to errors so namespace collisions cannot return silently.
- Keep L9 NAME-001 merge-blocking everywhere else. The AST scanners permit only the exact
  `schema_id: Literal["l9.<contract>/vN"] = Field(alias="schema")` form in the canonical
  contract model module, and catalog/parity checks must cover every permitted occurrence.

## Consequences

The v1 wire format remains byte-shape compatible, Python code uses an unambiguous attribute name,
and generated Pydantic JSON Schema exposes the published key. Pydantic 2.11 or newer is required
because the model policy uses explicit alias-validation and alias-serialization configuration.

A future `apiVersion`/`kind` envelope is a separate, versioned contract decision and is not part of
this correction.

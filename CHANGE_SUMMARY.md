<!-- L9_META
l9_schema: 1
origin: l9-deployment-platform
layer: [repository, validation]
tags: [L9_META, deployment-platform, change-summary]
owner: platform
status: active
/L9_META -->
# Final Consolidated Change Summary

## Release identity

- Repository: `Quantum-L9/l9-deployment-platform`
- Version: `0.1.5`
- Input lineage: improved 0.1.2 pack, recursive alignment remediation, final consolidation
- Scope: validation, source-supported repair, gap filling, hardening, regression proof, and packaging
- Architecture change: none
- Public v1 wire-contract break: none

## Material corrections

### Contract namespace and wire compatibility

- Renamed the Python-only field `schema` to `schema_id` in versioned DTOs while preserving the
  durable wire key `schema` through `Field(alias="schema")`.
- Enforced strict alias ingestion, alias serialization, catalog completeness, generated-schema
  parity, round trips, and warnings-as-errors.
- Added and registered `l9.repository-release-receipt/v1` and `l9.idempotency-store/v1`.

### Transaction and evidence integrity

- Enforced validated idempotency transitions, immutable completion, safe failed retry, and
  receipt-bound recovery.
- Rejected non-finite canonical JSON and validated evidence records before publication.
- Preserved independent GitHub approval, external CI evidence, immutable image digests, and the
  append-only receipt ledger.

### Security and process boundaries

- Hardened GitHub repository authorization, Infisical exports, explicit secret redaction,
  process-group timeout cleanup, HTTP probe schemes, path confinement, and workflow parsing.
- Removed source import side effects and caller-supplied `PYTHONPATH` dependencies from operational
  scripts.

### Source-release integrity

- Added a detached receipt binding the exact ZIP to its source manifest, version, name, digest,
  size, member count, and reproducible timestamp.
- Moved Python distributions, ZIPs, and receipts outside the validated source root.
- Added exact archive inventory, byte, mode, path, timestamp, checksum, and receipt validation.
- Rejected caches, coverage residue, build output, nested archives, symlinks, and unsafe paths.
- Made release tooling self-clean interpreter bytecode before source inventory and archive validation.

### Runtime correctness and operator behavior

- Fixed backup planning to read the typed `StorageConfig.persistent_volumes` contract.
- Fixed `inventory generate --output` so the generic emitter cannot overwrite the generated
  Ansible inventory.
- Added complete CLI-surface, inventory, logging, backup-policy, receipt-tamper, and release tests.

### Quality gates

- Raised the branch-coverage floor to 75 percent.
- Final local suite: 103 tests passed, zero warnings, 79.45 percent branch coverage.
- Canonical contract validation: 6 documents and 20 JSON Schemas.
- L9 metadata verification: 326 eligible files.

## Preserved capabilities

Provisioning, deployment planning, approval, immutable digest enforcement, backup, migration,
health verification, promotion, rollback, idempotency recovery, receipts, consumer projections,
OpenTofu, Ansible, GHCR, Infisical, and dedicated-runner boundaries remain intact.

No live infrastructure, GitHub environment, registry, runner, or secret store was modified.

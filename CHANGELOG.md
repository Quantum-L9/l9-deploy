<!-- L9_META
l9_schema: 1
origin: l9-deployment-platform
layer:
- repository
tags:
- L9_META
- deployment-platform
owner: platform
status: active
/L9_META -->
# Changelog

## 0.1.5 - 2026-07-22

### Source-release integrity

- Added a detached `l9.repository-release-receipt/v1` contract that binds repository,
  version, source manifest, archive name, archive digest, byte size, member count, and
  reproducible timestamp.
- Corrected the tagged-release workflow to build Python distributions, repository ZIP,
  and receipt outside the validated source tree.
- Made `make release-archive` generate and verify the archive and detached receipt as one unit.
- Registered the receipt in the contract catalog, schema registry, and L9 compatibility policy.

### Correctness and operator safety

- Fixed backup planning to consume the typed `StorageConfig` contract rather than calling
  dictionary methods on a Pydantic model.
- Fixed `inventory generate --output` so the generic CLI emitter cannot overwrite the generated
  Ansible inventory with the command summary.
- Added behavioral CLI, inventory, logging, backup-policy, release-receipt, and tamper tests.

### Quality gates

- Raised the enforced branch-coverage floor to 75 percent.
- Reached 103 passing tests, zero warnings, and 79.45 percent measured branch coverage locally.
- Blocked coverage databases, XML reports, HTML reports, build directories, and nested archives
  from source releases.
- Reconciled source, version, manifest, checksums, validation evidence, archive, and receipt into
  one deterministic release unit.
- Made release tooling remove its own interpreter bytecode before inventory, packaging, or validation.

## 0.1.4 - 2026-07-21

### Boundary security

- Made the private control-repository guard fail closed when GitHub context is missing.
- Rejected unsafe, duplicate, multiline, NUL-bearing, or invalid Infisical environment entries.
- Redacted explicitly supplied secret environment values from subprocess output.
- Drained subprocess pipes after timeout termination to prevent descriptor leaks.
- Restricted HTTP health probes to `http` and `https` schemes.

### Transaction and evidence integrity

- Enforced validated idempotency state transitions and immutable completion.
- Added safe same-digest retry after a failed deployment transaction.
- Added state-dependent JSON Schema constraints for idempotency records.
- Rejected non-finite JSON numbers at canonical hashing and durable JSON boundaries.
- Validated generated evidence records against the published evidence schema.

### Quality and release consolidation

- Added focused boundary, adapter, state-machine, redaction, and schema regression tests.
- Replaced the generated-inventory `.gitkeep` scaffold with an ownership README.
- Consolidated validation evidence and release documentation for the final source pack.

## 0.1.3 - 2026-07-21

### Contract correctness

- Preserved every v1 wire key named `schema` while renaming Python attributes to `schema_id`.
- Added strict alias validation and alias serialization for all durable Pydantic contracts.
- Added warning-as-error, round-trip, runtime-name leakage, and JSON Schema parity tests.
- Added the previously missing idempotency-store JSON Schema and registry entry.
- Aligned server-profile and deployment-receipt requiredness across runtime and wire schemas.

### Release hardening

- Made alias usage explicit at every durable serialization and hashing boundary.
- Raised the supported Pydantic floor to 2.11 for explicit alias policy controls.
- Added ADR-0007 documenting wire identity, runtime naming, and schema authority.

## 0.1.2 - 2026-07-21

### Correctness

- Aligned package, lockfile, runtime, manifest, and validation version metadata.
- Made operational scripts directly executable from a clean checkout without an installed package.
- Removed import-time execution from `l9_deploy.__main__`.
- Rejected duplicate YAML mapping keys in workflow validation.

### Security and hardening

- Added path confinement for fleet deployment-profile resolution and local executor writes.
- Constrained project identifiers and deployment profile paths at typed and JSON-schema boundaries.
- Added regression coverage for entrypoints, path traversal, version consistency, and workflow parsing.

## 0.1.1 - 2026-07-21

### Security

- Replaced synthetic release PASS evidence with externally produced canonical CI artifacts.
- Added independent GitHub protected-environment approval-history verification.
- Added create-only content-addressed receipts and a hash-chained append-only ledger.
- Added approval enforcement to every mutating workflow, including runner maintenance.

### Correctness

- Added frozen typed contracts for canonical deployment boundaries.
- Added two-phase transaction completion and replay recovery after receipt publication.
- Restored both runtime and release-state pointers during eligible rollback.
- Removed repository-local virtual-environment assumptions from tests.

### Governance

- Added L9 metadata coverage, explicit exclusions, transport classification, AST scanning,
  recursive alignment validation, Semgrep normalization, and merge-blocking workflow gates.
- Removed production `print()` calls and documented blocked validation honestly.

## 0.1.0 - 2026-07-21

- Initial provisioning and deployment control-plane build.

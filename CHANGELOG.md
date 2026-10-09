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

## Unreleased

### Immutable consumer profile ingestion

- The deployment profile is now consumer-owned source: `deploy-dispatch.yml` resolves
  `profile.path` from `source.repository` at the exact `source.commit_sha` through the
  existing read-only evidence transport, verifies the blob against the Git object id,
  and seals it in the validated-deployment artifact beside the request and plan.
- `verify_request` and `scripts/prepare-deployment.py` resolve the fleet-registered
  relative profile path inside an explicit `--profile-root` (symlink- and
  traversal-confined), check the request digest against those bytes before parsing,
  and never read a profile from the l9-deploy checkout.
- `l9-deploy deploy` requires `--profile-root` and reverifies the sealed bytes against
  `plan.profile_digest`, project, repository, and image before the executor exists;
  absence, drift, or tampering fails closed before backup, pull, render, migration,
  Compose, or promotion. `request validate`, `request inspect`, and `plan` take the
  same `--profile-root`.
- `plan_digest` is now content-bound: `build_plan` computes it over the plan's canonical
  wire form, so `plan.json` reproduces its own digest, and both `l9-deploy deploy` and the
  execution engine recompute it before trusting any plan field (`profile_digest` included).
  A plan edited around an unchanged digest string is refused before approval is consulted.
- Request, profile, plan, and receipt contract shapes are unchanged.

### Declared service readiness

- `build_plan` qualifies the profile's `services` map before a plan exists: a
  `required: true` service with `mode: none`, or a required `external` /
  `managed_on_fleet` service without a typed `probe`, is a contract failure. Optional
  services are not a gate and are never claimed. The plan shape and digest inputs are
  unchanged; the declaration is bound by the sealed profile digest.
- `execute_plan` applies the same qualification before approval, idempotency, or any host
  command, so a direct caller cannot bypass it. The existing `health` step now runs the
  profile's `health.startup` probe, then every required service's declared probe in name
  order, then the configured stabilization window once, then `health.post_deploy`; any
  failure raises with the phase named before promotion and takes the existing rollback and
  failure-receipt path. `health.post_deploy` remains the rollback verification probe.
- `execute_plan` refuses, before any side effect, a plan that could promote without the
  health gate: whenever a `promote` step is present there must be exactly one `health`
  step strictly between the last `deploy` step and `promote`. Promotion itself also
  refuses unless the health step completed in the same transaction.
- The health `ReceiptStep.details` records `startup` and the ordered `services` results
  beside the existing post-deploy fields. A probe result means exactly what the supplied
  probe checks; it is readiness evidence, not provisioning or lifecycle ownership.
- Consumer profiles that declare required services without probes
  (`integrations/consumers/seo-bot.deployment.yaml`,
  `integrations/consumers/graphiti-memory.deployment.yaml`,
  `templates/consumer/stateful-container/.l9/deployment.yaml`) are now blocked at planning
  until they supply one; they are deliberately not edited here.

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

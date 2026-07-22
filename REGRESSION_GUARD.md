<!-- L9_META
l9_schema: 1
origin: l9-deployment-platform
layer: [repository, validation]
tags: [L9_META, deployment-platform, regression-guard]
owner: platform
status: active
/L9_META -->
# Regression Guard

## Preserved capabilities

- Typed request verification and deterministic deployment planning.
- Canonical external evidence and independent protected-environment approval.
- Immutable OCI digest deployment through a repository-scoped dedicated runner.
- OpenTofu provisioning and Ansible host configuration.
- Backup, migration, health, promotion, rollback, idempotency recovery, and append-only receipts.
- Consumer adoption profiles and the installed `l9-deploy` CLI.
- Self-describing durable v1 YAML and JSON artifacts using wire key `schema`.

## Contract invariants

Reject any change that:

- emits `schema_id` into a durable artifact;
- accepts `schema_id` as an external v1 wire key;
- adds a Pydantic alias outside the exact cataloged schema-identity exception;
- leaves an alias-bearing DTO uncataloged;
- changes a v1 wire key without a new contract version;
- lets runtime fields or requiredness drift from published JSON Schema;
- permits warnings in the test suite;
- permits NaN or infinity in canonical or persisted JSON.

Use aliases for lexical differences only. Semantic transformations require a mapper and a versioned
compatibility decision.

## Transaction invariants

Reject any change that:

- persists an idempotency state without full model validation;
- allows `COMPLETE` to lose or replace its receipt digest;
- allows an illegal idempotency state transition;
- retries a failed request with a different request digest;
- completes a transaction before authoritative receipt publication;
- rolls back a committed release only because secondary idempotency indexing failed;
- restores a container without restoring its release-state pointer.

## Security invariants

Reject any change that:

- lets missing GitHub repository context pass the private-control-repository guard;
- accepts invalid, duplicate, multiline, or NUL-bearing Infisical environment entries;
- persists explicit secret environment values in subprocess output;
- leaves subprocess descendants or pipes alive after timeout;
- permits non-HTTP schemes in HTTP health probes;
- constructs an evidence record that does not validate against its published schema;
- permits public pull-request execution on the deployment runner.

## Packaging invariants

Reject any change that permits:

- operational scripts to depend on caller-supplied `PYTHONPATH`;
- package import to execute the CLI;
- duplicate workflow mapping keys;
- project IDs, profile paths, or executor writes to escape their roots;
- release versions to disagree;
- stale manifests or checksums to pass;
- archive inventory, bytes, or executable modes to differ from validated source;
- archive symlinks, nested archives, caches, generated build residue, or unsafe paths;
- empty scaffold-only files in required operational directories;
- non-deterministic ZIP output for identical source and epoch;
- an archive or receipt whose version, source manifest, digest, name, size, count, or timestamp disagrees;
- release outputs written inside the validated source root;
- release tooling that leaves `__pycache__`, `.pyc`, or `.pyo` residue in the source tree;
- coverage below the enforced 75 percent branch floor;
- typed deployment policy code falling back to unchecked dictionary access;
- a CLI handler and generic emitter both owning the same output path.

## Required local gates

```bash
PYTHONPATH=src python3 -m pytest -q -W error \
  --cov=l9_deploy --cov-branch --cov-report=term-missing \
  --cov-report=xml:artifacts/coverage.xml --cov-fail-under=75
python3 scripts/validate-contracts.py
python3 scripts/validate-workflows.py
python3 scripts/verify-l9-meta.py
python3 scripts/fast-contract-scan.py
python3 scripts/validate-alignment.py
bash -n scripts/*.sh
python3 -m compileall -q src scripts tests
make release-prepare
SOURCE_DATE_EPOCH="$(git log -1 --pretty=%ct)" make release-archive \
  ARCHIVE=../l9-deployment-platform.zip \
  RECEIPT=../l9-deployment-platform.receipt.json
```

CI additionally runs Ruff, Ruff formatting, strict mypy, pinned Semgrep, canonical `l9-ci-sdk`
normalization, and `uv build` on Python 3.12.

## Protected paths

Platform review and an explicit rollback plan are required for:

- `.github/workflows/`
- `.github/actions/collect-approval/`
- `.l9/policies/`
- `schemas/v1/`
- `src/l9_deploy/contracts/`
- `src/l9_deploy/evidence/`
- `src/l9_deploy/execution/`
- `src/l9_deploy/integrations/`
- `src/l9_deploy/requests/`
- `src/l9_deploy/subprocesses.py`
- `src/l9_deploy/release_inventory.py`
- release-generation and validation scripts
- `infrastructure/opentofu/`
- `ansible/roles/github_runner/`

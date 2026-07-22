<!-- L9_META
l9_schema: 1
origin: l9-deployment-platform
layer: [repository, validation]
tags: [L9_META, deployment-platform, validation]
owner: platform
status: active
/L9_META -->
# Validation

## Executive decision

```yaml
source_release: APPROVED_WITH_FINDINGS
local_release_blockers: 0
warning_policy: PASS
branch_coverage_gate: PASS
wire_contract_regression: PASS
exact_archive_validation: DETACHED_REQUIRED
production_readiness: BLOCKED_ON_VALIDATION
```

The 0.1.5 source tree passes every check executable with the installed toolchain. It is ready for
repository review, canonical CI, and controlled staging integration. It is not evidence that a
production fleet has been provisioned or exercised.

Local evidence was produced with Python 3.13.5 and pytest 9.0.2. The canonical lock targets Python
3.12 and pytest 8.4.2, so a frozen Python 3.12 CI run remains an external acceptance gate.

## Baseline versus final

| Check | Baseline | Final source |
|---|---|---|
| Input archive | 440 files, one root, zero forbidden residue | Frozen deterministic inventory |
| Version | 0.1.2 lineage | 0.1.5 |
| Tests | 54 passed, 9 warnings | 103 passed, 0 warnings |
| Branch coverage | Not enforced | 79.45 percent, 75 percent floor |
| Contract schemas | 18 | 20 |
| Wire field | Python and wire both used `schema` | Python `schema_id`, wire `schema` |
| Release binding | Archive and evidence could diverge | Detached manifest and archive receipt |
| Tagged release | Build output could contaminate source | Outputs isolated in runner temporary storage |
| Backup planning | Typed storage treated as dictionary | Typed policy access |
| Inventory output | Generic emitter could overwrite file | Handler owns artifact path exclusively |

## Executed source checks

| Check | Result | Evidence |
|---|---|---|
| Pytest, warnings as errors, branch coverage | PASS, 103 tests, 0 warnings, 79.45 percent | `validation/evidence/final/pytest.txt` |
| Canonical documents and schemas | PASS, 6 documents and 20 schemas | `validation/evidence/final/contracts.txt` |
| Workflow policy and duplicate keys | PASS | `validation/evidence/final/workflows.txt` |
| L9 metadata | PASS, 326 eligible files | `validation/evidence/final/metadata.txt` |
| Fast AST contract scan | PASS, zero findings | `validation/evidence/final/fast-contract-scan.txt` |
| Recursive alignment | PASS | `validation/evidence/final/alignment.txt` |
| Package imports | PASS, 56 modules | `validation/evidence/final/module-imports.txt` |
| CLI help | PASS | `validation/evidence/final/cli-help.txt` |
| Shell syntax | PASS | `validation/evidence/final/shell-syntax.txt` |
| Python compilation | PASS | `validation/evidence/final/python-compile.txt` |
| Structured document parsing | PASS | `validation/evidence/final/structured-parse.txt` |
| Python line length | PASS, maximum 100 | `validation/evidence/final/line-length.txt` |
| Active stubs, placeholders, symlinks, nested archives, and residue | PASS | `validation/evidence/final/no-stub-placeholder.txt` |
| Frozen release root, checksums, ZIP, and receipt | DETACHED_REQUIRED | Detached final validation report |

## Detached archive proof

The exact ZIP cannot contain its own final digest without self-reference. After source freeze, the
release process creates these external artifacts as one set:

- deterministic repository ZIP;
- `l9.repository-release-receipt/v1` JSON receipt;
- ZIP SHA-256 file;
- detached final validation report.

The detached validation verifies archive inventory, bytes, executable modes, canonical root,
uniform timestamps, receipt digest, source manifest digest, archive digest, byte size, member count,
clean extraction, and regression tests.

## Blocked checks

| Check | Status | Reason |
|---|---|---|
| Ruff and Ruff formatting | BLOCKED | Tool unavailable and network installation disabled |
| Strict mypy | BLOCKED | Tool unavailable and network installation disabled |
| Canonical Semgrep and `l9-ci` | BLOCKED | Pinned tools unavailable locally |
| Frozen Python 3.12 `uv sync` | BLOCKED | Interpreter and distributions absent from offline cache |
| Python wheel and sdist build | BLOCKED | `hatchling` absent from offline cache |
| OpenTofu, Ansible, and Docker | BLOCKED | Tools, credentials, backend, or live targets unavailable |
| GitHub approval and attestation APIs | BLOCKED | Authenticated workflow context unavailable |

Blocked checks are not represented as passing.

## External acceptance gates

Production readiness requires direct evidence for protected-environment approval, GHCR publication
and attestation, OpenTofu state locking and exact-plan apply, Ansible idempotency, dedicated-runner
isolation, Infisical OIDC, staging deployment and rollback, and backup restore. See
`UNKNOWN_REGISTER.md`.

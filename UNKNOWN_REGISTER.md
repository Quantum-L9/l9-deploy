<!-- L9_META
l9_schema: 1
origin: l9-deployment-platform
layer: [repository, validation]
tags: [L9_META, deployment-platform, unknowns]
owner: platform
status: active
/L9_META -->
# Unknown Register

No unresolved local source, contract, test, documentation, or packaging defect remains from this
consolidation.

## External acceptance Unknowns

| ID | Unknown | Evidence required to resolve | Owner |
|---|---|---|---|
| EXT-001 | GitHub protected-environment approval behavior | Real run proving reviewer identity, requester separation, and approval verification | Platform |
| EXT-002 | GHCR publication and provenance | Published digest, SBOM, provenance, and remote attestation verification | Platform |
| EXT-003 | OpenTofu provider and backend behavior | Reviewed plan, locked remote state, exact-plan apply, and infrastructure receipt | Infrastructure |
| EXT-004 | Ansible host idempotency | First apply, no-change second apply, and host-conformance report | Infrastructure |
| EXT-005 | Dedicated runner isolation | Repository-scoped registration, labels, network controls, cleanup, and public-PR denial | Platform |
| EXT-006 | Infisical workload identity | OIDC authentication and least-privilege retrieval without persisted credentials | Security |
| EXT-007 | Staging transaction | Real digest deployment, probes, receipt, ledger verification, and observed rollback | Platform |
| EXT-008 | Stateful backup and restore | Verified backup, isolated restore, integrity result, and migration recovery decision | Data owner |
| EXT-009 | Canonical Python 3.12 CI toolchain | Frozen sync, Ruff, strict mypy, Semgrep normalization, tests, and package build | Platform |
| EXT-010 | Fleet capacity and recovery objectives | Approved sizing, RTO, RPO, retention, monitoring, and alert routing per workload | Operator |

These are external validation gates. They remain `UNKNOWN` or `BLOCKED` until direct evidence exists.

<!-- L9_META
l9_schema: 1
origin: l9-deploy
layer:
- repository
tags:
- L9_META
- deployment-platform
owner: platform
status: active
/L9_META -->
# Security

## Boundary

This repository can provision infrastructure and mutate production systems. Its workflows, schemas,
runner, OpenTofu state, Ansible roles, approval evidence, and receipt ledger are high-blast-radius
assets.

## Mandatory controls

- GitHub repository visibility must be private before production use.
- The self-hosted runner must be repository-scoped to `Quantum-L9/l9-deploy`.
- Public pull-request code must never execute on the deployment runner.
- Mutating workflows use protected environments and independent approval evidence.
- Requester and approver identities must differ.
- Canonical CI evidence is consumed, not reconstructed.
- OCI images are deployed by immutable digest.
- Secrets come from Infisical through job-scoped workload identity where supported.
- Infrastructure apply consumes the exact approved OpenTofu plan artifact.
- Canonical receipts are create-only and hash-chained.
- Logs and evidence are redacted before persistence.
- Missing or mismatched repository, approval, identity, or evidence context fails closed.

Repository visibility is an external GitHub setting. Source validation can document and guard the
required posture, but it cannot make a public repository private. Operators must verify the actual
GitHub setting before production authorization.

## Identity

The sole live repository identity is `Quantum-L9/l9-deploy`. It is used by OIDC claims, runner
scope, approval receipts, repository guards, dispatch, release receipts, interface registration, and
new source releases. The retired identity is not accepted on those surfaces.

## Approval integrity

The collector queries GitHub workflow-run approval history and preserves the raw response. The
receipt binds requester, reviewer, environment, plan digest, repository, run, attempt, job, workflow
reference, timestamp, and approval-history digest. A locally authored `approved: true` document is
not sufficient.

## OIDC

Workflow-level `id-token: write` is forbidden. Job-scoped OIDC is allowed only on the four approved
Infisical consumers listed in `ARCHITECTURE.md`. Approval and validation jobs may not mint tokens.

External Infisical claim policy must positively accept the canonical repository claim and reject
legacy or unrelated claims before production use.

## Runner hardening

The deployment runner must not host application workloads, databases, or general CI. Registration
material is short-lived. The configured runner repository must equal
`https://github.com/Quantum-L9/l9-deploy`. Required custom labels are
`l9-deployment,hetzner-private`. If the runner is offline, repair it through the out-of-band
bootstrap path rather than pretending the self-hosted maintenance workflow can execute.

## Evidence and receipts

Release requests bind source revision, CI evidence, image digest, SBOM/provenance references, and
profile digest. Receipts are content-addressed and the latest pointer is non-authoritative. A ledger
verification failure is an incident.

## Secrets and subprocesses

Infisical exports are hostile boundary data. Keys must be unique and POSIX-compatible; values must be
single-line and NUL-free. Runtime env files are mode `0600`, release-owned, never uploaded as
artifacts, and never edited in place. Subprocess output is redacted using pattern rules plus explicit
secret environment values. Timeouts terminate process groups.

## Break glass

Break-glass access is time-bounded, attributable, and followed by reconciliation through OpenTofu and
Ansible. Emergency manual state is not automatically the new desired state.

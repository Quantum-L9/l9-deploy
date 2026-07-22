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
# Threat model

Primary threats are untrusted public pull requests reaching the runner, mutable image substitution,
request replay, forged evidence references, secret leakage, SSH lateral movement, destructive
infrastructure plans, migration failure, and rollback failure. Controls include repository-scoped
runner access, source and profile allowlists, full SHAs, digest-only images, idempotency records,
environment locks, OIDC secret retrieval, host firewalling, exact plan application, approvals,
redaction, backup gates, health probes, and immutable receipts.

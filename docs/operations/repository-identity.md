<!-- L9_META
l9_schema: 1
origin: l9-deploy
layer:
- documentation
- operations
tags:
- L9_META
- repository-identity
owner: platform
status: active
/L9_META -->
# Repository Identity and Compatibility Map

## Canonical identity

- Repository: `Quantum-L9/l9-deploy`
- URL: `https://github.com/Quantum-L9/l9-deploy`
- Short name: `l9-deploy`
- OIDC repository claim: `Quantum-L9/l9-deploy`
- Repository-scoped runner allowlist: `Quantum-L9/l9-deploy`
- Source archive basename: `l9-deploy.zip`
- Detached receipt basename: `l9-deploy.receipt.json`

These values are authoritative for live metadata, workflows, external policy, integration contracts,
operator commands, and generated Phase 5 evidence.

## Legacy identifier classification

`l9-deployment-platform` was the former internal identity. References are classified as follows:

| Reference class | Treatment |
|---|---|
| Repository URL, producer/consumer identity, runner scope, OIDC claim | Replace with canonical identity. |
| Source archive and detached receipt basename | Replace on the next regenerated release set. |
| Existing external state keys, Infisical identities, historical receipts | Do not rename without migration and accessibility evidence. Record as compatibility aliases. |
| `origin: l9-deployment-platform` in existing L9 metadata | Historical provenance only. Retain until an authorized metadata migration; it must not be interpreted as a live repository coordinate. |
| Historical changelog, ADR, or audit narrative | Retain when it describes past state; annotate if operationally ambiguous. |

## Compatibility rule

No external state key, OIDC subject condition, Infisical identity, runner registration, receipt, or
archive may be blindly renamed. Phase 6 must prove the canonical GitHub claim and verify any persisted
legacy identifiers remain reachable or are migrated through an approved mapping.

## Scan interpretation

A repository-wide occurrence of `l9-deployment-platform` is acceptable only when it is one of:

1. an L9 metadata `origin` provenance label;
2. an explicitly documented compatibility alias;
3. historical narrative.

Any live `repository`, `repository_url`, integration `producer` or `consumer`, runner scope, OIDC
claim, or new archive name using the legacy identity is a defect.

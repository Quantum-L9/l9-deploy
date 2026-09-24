<!-- L9_META
l9_schema: 1
origin: l9-deploy
layer:
- documentation
tags:
- L9_META
- deployment-platform
owner: platform
status: active
/L9_META -->
# Workflow Inventory

| Workflow | Role | OIDC |
|---|---|---|
| `validate.yml` | Repository-native source, contract, workflow, metadata, identity, and alignment validation. | None |
| `release.yml` | Builds the deterministic repository source release on version tags. | None |
| `deploy-dispatch.yml` | Validates bounded release requests, records approval, materializes runtime secrets, verifies provenance, deploys. | `deploy` only |
| `deploy-manual.yml` | Operator entrypoint that emits the governed repository dispatch. | None |
| `promote.yml` | Promotes a validated request between governed environments. | None |
| `rollback.yml` | Approved runtime rollback. | None |
| `backup-verify.yml` | Backup/restore verification. | None |
| `drift-detect.yml` | Scheduled and manual OpenTofu drift plans. | `plan` only |
| `fleet-conformance.yml` | Scheduled and manual host/fleet conformance on the dedicated runner. | None |
| `configure-hosts.yml` | Deterministic Ansible configuration plan, approval, check, and apply. | None |
| `provision-plan.yml` | Creates immutable OpenTofu plan artifacts. | `plan` only |
| `provision-apply.yml` | Approved exact-plan infrastructure apply. | `apply` only |
| `runner-maintenance.yml` | Approved runner reconciliation when the runner is already available. | None |

## Release ownership

`l9-ci-core`, not this repository, owns consumer image release orchestration and dispatch
construction. `l9-deploy` receives and verifies the bounded deployment request.

## OIDC invariant

Workflow-level OIDC is forbidden. A job may request `id-token: write` only when that same job uses
the approved Infisical exchange. The allowlist is exactly:

- `deploy-dispatch.yml/deploy`
- `drift-detect.yml/plan`
- `provision-plan.yml/plan`
- `provision-apply.yml/apply`

The canonical GitHub repository claim is `Quantum-L9/l9-deploy`.

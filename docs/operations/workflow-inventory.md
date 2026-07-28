<!--
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer:
- documentation
tags:
- L9_META
- deployment-platform
owner: platform
status: active
--- /L9_META ---
-->
# Minimum Functional Workflow Inventory

Phase 3 keeps only deployment wiring and its existing operational prerequisites in scope. It does not add scanners, linters, or a generalized CI framework.

| Workflow | Disposition | Functional role | OIDC policy |
|---|---|---|---|
| `deploy-dispatch.yml` | Deployment-required | Validates an immutable release request, collects protected approval, materializes runtime secrets, verifies provenance, and executes the exact approved plan. | Only `deploy` may request `id-token: write`. |
| `deploy-manual.yml` | Deployment-required | Produces the governed repository dispatch that enters `deploy-dispatch.yml`. | No OIDC. |
| `promote.yml` | Deployment-required | Promotes an already validated deployment request between governed environments. | No OIDC. |
| `rollback.yml` | Deployment-required | Collects protected incident approval and invokes rollback on the private runner. | No OIDC. |
| `backup-verify.yml` | Deployment-required safeguard | Verifies recovery artifacts required by the deployment recovery path. | No OIDC. |
| `drift-detect.yml` | Deployment-required safeguard | Uses short-lived infrastructure credentials to detect environment drift. | Only `plan` may request `id-token: write`. |
| `fleet-conformance.yml` | Deployment-required safeguard | Verifies private fleet conformance and emits evidence. | No OIDC. |
| `configure-hosts.yml` | Provisioning-related | Applies approved host configuration through Ansible. | No OIDC; the workflow does not exchange identity. |
| `provision-plan.yml` | Provisioning-related | Materializes short-lived infrastructure credentials and creates an immutable OpenTofu plan. | Only `plan` may request `id-token: write`. |
| `provision-apply.yml` | Provisioning-related | Collects protected approval, materializes short-lived credentials, and applies the exact approved OpenTofu plan. | Only `apply` may request `id-token: write`; `authorize` cannot. |
| `runner-maintenance.yml` | Provisioning-related | Reconciles the repository-scoped private runner after protected approval. | No OIDC; credentials come from explicit repository secrets. |
| `release.yml` | Deferred CI/release | Builds and validates release artifacts. It remains unchanged in Phase 3. | No OIDC. |
| `validate.yml` | Deferred generalized CI | Runs the existing repository validation stack. No new scanner, linter, or CI framework is introduced in Phase 3. | No OIDC. |

## Required deployment chain

`deploy-manual` or an authorized external producer emits `l9.release.requested.v1` -> `deploy-dispatch.validate` validates and binds immutable evidence -> `deploy-dispatch.authorize` records protected approval -> `deploy-dispatch.deploy` alone receives OIDC, renders `runtime.env`, verifies provenance, and executes the exact approved plan.

## Security invariants

- Workflow-level `id-token: write` is prohibited.
- A job may request `id-token: write` only when that same job invokes `scripts/infisical-oidc-env.sh`.
- Approval jobs never receive OIDC permission.
- Deployment secret materialization remains downstream of both validation and protected approval.
- Scanner and linter expansion is outside Phase 3.
- No workflow is classified obsolete at this phase.

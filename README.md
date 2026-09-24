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
# L9 Deploy

`Quantum-L9/l9-deploy` is the provisioning and deployment control plane for Quantum-L9 hosted
services. It is a non-node infrastructure control plane.

## Authority boundary

- `l9-ci-sdk` owns canonical CI evidence and compatibility.
- `l9-ci-core` owns CI, image publication, release evidence construction, and bounded deployment dispatch.
- `Quantum-L9/.github` owns organization-level public interface discovery and starter projections.
- `l9-deploy` owns infrastructure desired state, fleet registration, host reconciliation, request
  verification, deterministic deployment plans, protected approval verification, deployment mutation,
  rollback, and operational receipts.

No executable copy of `l9-ci-core` release orchestration belongs in this repository.

## Canonical identity

All live trust surfaces use `Quantum-L9/l9-deploy`: OIDC repository claim, repository-scoped runner,
approval receipt repository, repository guard, dispatch destination, release receipt, interface
provider, package name, and source-release archive identity.

The retired identity is historical only. The one deliberate compatibility exception is the existing
OpenTofu remote-state storage prefix. That persisted key is not repository identity and must not be
used for OIDC, approvals, runner scope, dispatch, receipts, interfaces, packages, or new archives.

See `docs/operations/repository-identity.md`.

## Trust spine

A deployment mutation requires:

1. canonical external CI evidence;
2. one immutable OCI image digest;
3. a registered deployment profile and exact profile digest;
4. a deterministic plan digest;
5. independent GitHub protected-environment approval bound to that plan;
6. the repository-scoped dedicated deployment runner;
7. health evidence; and
8. create-only content-addressed receipt publication.

Self-authored PASS evidence, mutable image tags, self-issued approvals, receipt replacement, and
public pull-request execution on the deployment runner are rejected.

## Implemented runtime profiles

- `container-service`
- `worker-service`
- `stateful-container`
- `scheduled-job`
- `external-platform`

`static-site` is not an implemented v1 profile.

## Operational posture

Repository visibility is an external GitHub administrative control. The security contract requires
this repository to be private before production use. Repository source cannot change that account
setting by itself.

Operational readiness additionally requires current evidence that the dedicated runner is online
with the required labels, OpenTofu plan/drift workflows execute successfully, and staging has proven
deploy, rollback, backup, and restore behavior. Historical validation reports are not substitutes for
revision-bound evidence.

## Primary validation

```bash
uv sync --all-extras --frozen
make validate
python3 scripts/validate-repository-identity.py
```

Release artifacts are generated only after source validation:

```bash
export SOURCE_DATE_EPOCH="$(git log -1 --pretty=%ct)"
make release-prepare
make release-archive ARCHIVE=../l9-deploy.zip RECEIPT=../l9-deploy.receipt.json
```

`release-prepare` regenerates the manifest, final tree, and checksum index. Those generated files
describe a frozen release set; they are not current-runtime evidence merely because they are tracked.

## Safety invariants

- Build once and deploy by immutable digest.
- Never build application source on production hosts.
- Never treat `github.actor` as protected-environment approval.
- Never apply a different infrastructure plan than the approved plan file and digest.
- Never overwrite canonical receipts.
- Never infer database rollback from container rollback.
- Never allow legacy repository identity back into a live trust surface.
- Never claim production readiness while mandatory live validation is missing.

See `ARCHITECTURE.md`, `SECURITY.md`, `RUNBOOK.md`, and `VALIDATION.md`.

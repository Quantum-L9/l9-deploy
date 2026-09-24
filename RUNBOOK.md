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
# Operator Runbook

## 1. Preflight

Before any production mutation, verify:

1. GitHub repository visibility is private.
2. protected environments exist with independent reviewers;
3. OIDC/Infisical trust accepts `Quantum-L9/l9-deploy`;
4. the dedicated runner is online, repository-scoped to `Quantum-L9/l9-deploy`, and has
   `l9-deployment` and `hetzner-private` labels;
5. current source validation is green; and
6. the intended environment has current infrastructure and fleet-conformance evidence.

## 2. Provision infrastructure

Run `Provision Plan`, review `tfplan` and `infrastructure-plan.json`, then run `Provision Apply`
with the originating run ID, artifact name, expected plan digest, and protected approval. Apply must
consume the exact approved plan artifact. Replanning during apply is forbidden.

The existing remote-state prefix is a persisted compatibility namespace. Do not rename or copy state
as part of repository identity cleanup.

## 3. Bootstrap or recover the runner

When no healthy self-hosted runner exists, use
`docs/runbooks/bootstrap-management-runner.md`. The bootstrap path runs from an operator-controlled
environment with a fresh repository-scoped registration token and verified runner archive SHA-256.

Use `Runner Maintenance` only when the self-hosted runner is already healthy enough to execute it.

## 4. Onboard a consumer

The consumer owns application source, Dockerfile, health behavior, migrations, and
`.l9/deployment.yaml`. `l9-ci-core` owns release orchestration. Register the deployment profile and
environment placement in `fleet/registry.yaml`; do not copy release orchestration into this repo or
the consumer.

## 5. Standard release

1. consumer CI emits canonical evidence;
2. `l9-ci-core` builds and publishes one immutable OCI digest;
3. `l9-ci-core` binds release evidence and dispatches `l9.release.requested.v1`;
4. `l9-deploy` revalidates request, evidence, source, profile, and digest;
5. a deterministic plan is generated;
6. the protected authorize job records independent approval;
7. the dedicated runner executes the exact approved plan;
8. health is verified; and
9. an immutable deployment receipt is published.

## 6. Rollback

Use the protected rollback workflow. Restore the previous release-owned configuration and image
together, verify health, then republish the previous runtime state. Database restoration remains a
separate policy decision.

## 7. Failure handling

- Before receipt publication: preserve evidence and allow policy-governed runtime rollback.
- After receipt publication but before idempotency finalization: replay the same request; do not
  redeploy or edit the idempotency store.
- Ledger failure: stop affected deployments and preserve the ledger and workflow artifacts.
- Approval mismatch: do not manufacture a replacement receipt.
- Runner offline: use out-of-band bootstrap; queued self-hosted jobs are not proof of conformance.

## 8. Validation

```bash
make validate
python3 scripts/validate-repository-identity.py
```

After implementation and documentation are final, generate the release set:

```bash
export SOURCE_DATE_EPOCH="$(git log -1 --pretty=%ct)"
make release-prepare
make release-archive ARCHIVE=../l9-deploy.zip RECEIPT=../l9-deploy.receipt.json
```

Never treat historical validation files as current evidence for a different revision.

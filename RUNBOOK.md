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
# Operator Runbook

## 1. Bootstrap the management plane

1. Configure the remote OpenTofu backend and locking.
2. Populate Infisical with Hetzner, state backend, registry, runner, and backup credentials.
3. Run the management environment plan.
4. Review the exact plan artifact and digest.
5. Run the protected `Provision Apply` workflow.
6. Generate Ansible inventory from `fleet/registry.yaml`.
7. Run host bootstrap, hardening, Docker, firewall, and runner configuration.
8. Verify the repository-scoped runner labels and deny public repository access.

Never place long-lived infrastructure credentials in repository secrets when OIDC-backed
Infisical retrieval is available.

## 2. Onboard a consumer repository

Render a thin projection:

```bash
uv run l9-deploy adoption render \
  --profile stateful-container \
  --project-id seo-bot \
  --repository Quantum-L9/SEO-Bot \
  --image ghcr.io/quantum-l9/seo-bot \
  --destination /path/to/consumer
```

Review the generated `.l9/deployment.yaml`, release caller workflow, health policy,
migration policy, and backup policy. Register the project and target server in
`fleet/registry.yaml` through a reviewed pull request.

## 3. Standard release

1. Consumer CI produces a canonical finding bundle and external CI gate binding.
2. The release kernel validates both artifacts.
3. The kernel builds and publishes one OCI image.
4. The exact digest is bound to the validated CI artifacts.
5. A bounded request is dispatched to this private repository.
6. The private receiver downloads and revalidates the evidence artifact by workflow run.
7. A deterministic plan is generated.
8. The protected authorize job obtains independent environment review.
9. The dedicated runner verifies the approval history and executes the plan.
10. The immutable receipt and ledger entry are uploaded as workflow artifacts.

## 4. Verify a release

```bash
uv run l9-deploy receipt verify \
  --receipt receipts/ledger/receipts/sha256/<digest>.json \
  --json

uv run l9-deploy receipt ledger-verify \
  --ledger-root receipts/ledger \
  --json
```

A latest pointer may help navigation, but always verify the content-addressed receipt and
ledger chain for audit or recovery decisions.

## 5. Rollback

Use the protected `Rollback` workflow with:

- project,
- environment,
- incident ID,
- expected rollback-plan digest.

The workflow collects independent approval, verifies its history, restores the previous
verified image and release state, performs health verification, and emits a rollback receipt.
Do not run ad hoc `docker compose` rollback commands except under a documented break-glass
incident procedure.

## 6. Infrastructure change

1. Run `Provision Plan`.
2. Download and review `tfplan` and `infrastructure-plan.json`.
3. Confirm the plan-file digest.
4. Use `Provision Apply` with the source run ID, artifact name, and expected digest.
5. Require explicit protected-environment approval.
6. Use `allow-destructive` only after documented review.
7. Run host configuration and fleet conformance after apply.

The apply workflow must consume the exact plan artifact. Replanning during apply is forbidden.

## 7. Runner maintenance

Run `Runner Maintenance` with an expected plan digest. The workflow has a separate protected
authorize job, verifies GitHub approval history, retrieves short-lived runner credentials,
and reconciles the runner through Ansible.

The runner must remain:

- repository scoped,
- private,
- unavailable to public pull requests,
- free of application workloads and databases,
- disposable and rebuildable from OpenTofu and Ansible.

## 8. Failure handling

### Deployment fails before receipt publication

The engine restores the previous runtime image and release-state pointer when automatic
rollback is enabled. A failure receipt is published. Database rollback remains policy-bound
and is reported as an Unknown when it cannot be proven safe.

### Receipt is published but idempotency finalization fails

Do not edit the idempotency store manually. Rerun the same request. The engine detects `PREPARED`, loads the content-addressed receipt,
verifies it through the ledger, and completes the idempotency record without redeploying.

### A failed request is retried

Use the same request and request digest. `begin()` resets a validated `FAIL` entry to `IN_PROGRESS`.
A different digest under the same key is rejected. `COMPLETE` is immutable and exact completion
replays are no-ops.

### Ledger verification fails

Stop deployments to the affected environment. Preserve the full ledger directory and
workflow artifacts. Do not rewrite or repair records in place. Open an incident and recover
from the last independently verified ledger snapshot.

### Approval verification fails

Confirm environment protection rules, requested reviewer identity, requester separation,
workflow run ID, and approval-history artifact. Do not create a replacement approval receipt
manually.

## 9. Validation and source-release commands

```bash
PYTHONPATH=src python3 -m pytest -q -W error \
  --cov=l9_deploy --cov-branch --cov-report=term-missing \
  --cov-report=xml:artifacts/coverage.xml --cov-fail-under=75
PYTHONPATH=src python3 scripts/validate-contracts.py
python3 scripts/validate-workflows.py
python3 scripts/verify-l9-meta.py
python3 scripts/fast-contract-scan.py
python3 scripts/validate-alignment.py
bash -n scripts/*.sh
python3 -m compileall -q src scripts tests
```

Freeze the source release only after code, tests, docs, and validation evidence are final:

```bash
export SOURCE_DATE_EPOCH="$(git log -1 --pretty=%ct)"
make release-prepare
make release-archive \
  ARCHIVE=../l9-deployment-platform.zip \
  RECEIPT=../l9-deployment-platform.receipt.json
```

`release-prepare` removes generated residue, regenerates `MANIFEST.json`, `MANIFEST.md`,
`FINAL_TREE.md`, and `checksums.sha256`, then validates the frozen root. `release-archive` writes the
ZIP and receipt outside the repository and validates both against the frozen source.

The receipt is detached because embedding a post-build digest inside the ZIP would change the ZIP.
Treat the ZIP, receipt, and checksum as one release set. Do not rename the ZIP without rebuilding the
receipt because `archive_name` is part of the signed logical identity.

Archive validation rejects missing, extra, modified, unsafe, forbidden, symlinked, mode-drifted, or
non-deterministically timestamped members. Run release-root validation before commands that create
`.coverage`, `artifacts/coverage.xml`, caches, or build output.

## 10. Contract evolution

For existing v1 artifacts, preserve the serialized key `schema`. Python uses `schema_id` only as a
runtime name. Always validate external documents through `model_validate`, serialize durable
contracts with aliases, and run `scripts/validate-contracts.py`.

A new alias is prohibited unless it is the exact cataloged schema-identity exception. Semantic field
or structure changes require a new contract version, compatibility tests, and migration or mapping
logic. Do not use aliases to disguise semantic changes.

## 11. Secret rendering and subprocess safety

Infisical rendering rejects invalid or duplicate environment names and values containing CR, LF,
or NUL. Rendered files are mode `0600` and deleted when the context exits. Do not bypass this path
with ad hoc `infisical export > file` commands.

Commands must be supplied as argument arrays, never shell-concatenated strings. Explicit secret
environment values are redacted from captured output. Timeouts terminate the entire process group
and drain its pipes before returning an operational-limit failure.

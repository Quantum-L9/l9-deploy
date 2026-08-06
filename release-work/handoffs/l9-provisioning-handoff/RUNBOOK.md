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
# Operator Runbook — Parts B/C (exact commands)

Run from a checkout of `Quantum-L9/l9-deploy` at branch
`claude/l9-deploy-skill-install-rs1fuf` unless noted. All secrets come from your
own vault / Infisical (see `secrets/`). Placeholders look like `<...>`.

Subnets (created by the management env): management `10.90.1.0/24`, staging
`10.90.10.0/24`, production `10.90.20.0/24`. Provisional host IPs already in
`fleet/registry.yaml` — `TF_VAR_servers[<id>].private_ip` MUST match them:
`mem-staging-01 10.90.10.10`, `mem-prod-01 10.90.20.10`,
`seo-staging-01 10.90.10.20`, `seo-prod-01 10.90.20.20`.

---

## Phase 0 — Preflight
Confirm `PREFLIGHT_CHECKLIST.md` is fully satisfied (accounts, tokens, GitHub
protected environments, config changes in `config-changes/CONFIG_CHANGES.md`
applied and merged). Then:
```bash
uv sync --all-extras --frozen
make validate            # expect EXIT 0
bash scripts/install-opentofu.sh 1.11.7
```

## Phase 1 — State backend + Infisical
```bash
# S3-compatible remote state bucket (idempotent). Requires AWS_*/L9_STATE_* in env.
export AWS_ACCESS_KEY_ID=<...> AWS_SECRET_ACCESS_KEY=<...>
export L9_STATE_BUCKET=<bucket> L9_STATE_ENDPOINT=<https-endpoint> L9_STATE_REGION=eu-central
bash scripts/bootstrap-state.sh
```
Populate Infisical per environment slug (`management`, `staging`, `prod`) with
every key in `secrets/REQUIRED_SECRETS.md`, and configure the machine identity +
OIDC trust (audience `https://github.com/Quantum-L9`).

## Phase 2 — Management (bootstrap exception: operator-run, off the runner)
The self-hosted runner does not exist yet, so this first apply is run by you, not
by `provision-apply.yml`.
```bash
DIR=infrastructure/opentofu/environments/management
# Render backend.hcl from your state secrets (keys per backend.example.hcl), then:
tofu -chdir="$DIR" init -input=false -backend-config=backend.hcl
# Feed TF_VAR_hcloud_token / TF_VAR_ssh_key_ids from Infisical into the environment first.
uv run l9-deploy infra plan --environment management --working-directory "$DIR" \
  --plan-file tfplan --output infrastructure-plan.json --json
# Review change_summary + plan_digest in infrastructure-plan.json, then apply:
uv run l9-deploy infra apply --environment management --working-directory "$DIR" \
  --plan-file tfplan --plan-receipt infrastructure-plan.json \
  --expected-plan-digest <plan_digest> \
  --approval-receipt <receipt.json> --approval-history <history.json> \
  --approval-run-id <id> --requester <you> --receipt-ledger-root receipts/ledger
```
Creates the `l9-management` network + three subnets + runner `l9-deploy-01`
(`10.90.1.10`). Capture the `network_id` output — staging/production need it.

## Phase 3 — Management host config + register the runner
```bash
# 1. Transcribe tofu outputs (runner_private_ip/runner_server_id) into fleet/registry.yaml.
#    (Manual: no automated tofu->registry feedback exists. l9-deploy-01 is already 10.90.1.10.)
uv run l9-deploy inventory validate --fleet fleet/registry.yaml
uv run l9-deploy inventory generate --fleet fleet/registry.yaml
# 2. Trust the new host's SSH key (host_key_checking=True), then configure + register:
bash scripts/bootstrap-runner.sh \
  -e l9_runner_registration_token=<short-lived-repo-token> \
  -e l9_runner_sha256=<verified-2.334.0-tarball-sha256>
# bootstrap-runner.sh runs bootstrap.yml -> harden.yml -> configure-runner.yml -> verify.yml (--limit management)
uv run l9-deploy host verify --server l9-deploy-01 --fleet fleet/registry.yaml
uv run l9-deploy fleet verify --fleet fleet/registry.yaml
```
Confirm the runner shows labels `l9-deployment,hetzner-private`, is registered to
**`Quantum-L9/l9-deploy`**, and public-repo access is denied.

## Phase 4 — Staging (now via the designed workflows; runner exists)
1. In Infisical `staging`: set `TF_VAR_network_id` = management's `network_id`,
   and `TF_VAR_servers` including `mem-staging-01` (10.90.10.10) and
   `seo-staging-01` (10.90.10.20) with matching private IPs, server types, roles.
2. Run the GitHub Actions **`provision-plan.yml`** (environment: `staging`),
   review the uploaded `infrastructure-plan.json` + digest, then run
   **`provision-apply.yml`** (protected environment `staging`, `plan-run-id`,
   `artifact-name`, `expected-plan-digest`).
3. Transcribe the staging server outputs into `fleet/registry.yaml`, then:
```bash
uv run l9-deploy inventory generate --fleet fleet/registry.yaml
INV=ansible/inventories/generated/hosts.yml
# Configure the memory (cache) host: docker, redis, sqlite_backup, conformance.
uv run l9-deploy config apply --playbook ansible/playbooks/bootstrap.yml       --inventory "$INV" --limit staging <mutation-args>
uv run l9-deploy config apply --playbook ansible/playbooks/harden.yml          --inventory "$INV" --limit staging <mutation-args>
uv run l9-deploy config apply --playbook ansible/playbooks/configure-memory.yml --inventory "$INV" --limit cache \
  -e l9_redis_acl_password=<from-infisical> <mutation-args>
uv run l9-deploy config apply --playbook ansible/playbooks/verify.yml          --inventory "$INV" --limit staging <mutation-args>
uv run l9-deploy host verify --server mem-staging-01 --fleet fleet/registry.yaml
```
`<mutation-args>` = `--environment staging --expected-plan-digest <d>
--approval-receipt <r> --approval-history <h> --approval-run-id <id>
--requester <you> --receipt-ledger-root receipts/ledger`.

## Phase 5 — Production
Repeat Phase 4 against the production subnet (`10.90.20.0/24`), `mem-prod-01`,
`seo-prod-01`, and the production protected-environment approval.

## Phase 6 — Deploy the memory server (first real end-to-end deploy)
Prerequisite: the GHCR image exists (build via `graphiti-image/`).
```bash
# Register is already done (fleet/registry.yaml projects[].graphiti-memory).
# Build a deployment request bound to the published image digest, then:
uv run l9-deploy request validate --request request.json --fleet fleet/registry.yaml --json
uv run l9-deploy plan --request request.json --fleet fleet/registry.yaml --output plan.json --json
# Staging first (approval_required: false for staging), then deploy:
uv run l9-deploy deploy --plan plan.json --fleet fleet/registry.yaml \
  --runtime-env-file <deploy-render.env> --base-url http://mem-staging-01:8200 <mutation-args>
# The backup step now runs the declared verify_command (l9-sqlite-verify) in-band
# and fails closed if the SQLite snapshot cannot be verified.
uv run l9-deploy status --project graphiti-memory --environment staging --fleet fleet/registry.yaml
```
Then promote to production via `provision`/`deploy` with the protected approval.

## Phase 7 — Register SEO-Bot (register only; deploy gated on postgres)
`seo-bot` is already in `fleet/registry.yaml`. Complete consumer-side onboarding
in the SEO-Bot repo (`adoption render` output committed there). Its full deploy
stays deferred until postgres is in scope.

## Rollback / drift
- Any failed deploy auto-rolls back (profile `automatic_rollback: true`); verify
  with `uv run l9-deploy receipt ledger-verify --ledger-root receipts/ledger`.
- Infra drift: run `drift-detect.yml` (read-only) per environment.

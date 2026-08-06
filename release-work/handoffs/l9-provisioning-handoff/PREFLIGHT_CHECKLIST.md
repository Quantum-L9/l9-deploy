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
# Preflight Checklist + Acceptance Gates

## Before Phase 1 (accounts, identities, config)
- [ ] Hetzner Cloud project created; API token available; SSH key(s) uploaded (ids known).
- [ ] S3-compatible object store reachable; access/secret keys available; bucket name + endpoint chosen.
- [ ] Infisical project exists; machine identity created with **OIDC trust**, audience `https://github.com/Quantum-L9`, granted to env slugs `management`/`staging`/`prod`. `INFISICAL_IDENTITY_ID` + `INFISICAL_PROJECT_SLUG` recorded.
- [ ] GitHub **protected Environments** `management`, `staging`, `production` created on `Quantum-L9/l9-deploy` with independent reviewers.
- [ ] GitHub admin on `Quantum-L9/l9-deploy` (to mint a self-hosted runner registration token and manage the runner).
- [ ] **Config changes applied + merged** (see `config-changes/CONFIG_CHANGES.md`): `l9_runner_repository` = `Quantum-L9/l9-deploy`; `l9_runner_sha256` supplied at runtime.
- [ ] `secrets/REQUIRED_SECRETS.md` fully populated in Infisical per env slug.
- [ ] `make validate` is green on the branch.

## Per-phase acceptance gates
- **Phase 1:** `bootstrap-state.sh` reports the bucket exists with versioning + full public-access-block.
- **Phase 2:** `infrastructure-plan.json` shows only expected creates (network, 3 subnets, runner); `infra apply` returns `{"status":"PASS"}`; `network_id` captured.
- **Phase 3:** `inventory validate` PASS; runner online with labels `l9-deployment,hetzner-private` on `Quantum-L9/l9-deploy`; public-repo access denied; `host verify l9-deploy-01` PASS.
- **Phase 4/5:** `provision-apply` PASS on the protected env; `host verify mem-<env>-01` PASS; Redis reachable only on the private interface, auth required (no `nopass`).
- **Phase 6 (active-memory acceptance — from `l9-graphiti-memory/docs/ACTIVE_MEMORY_DEPLOYMENT_CONTRACT.md`):**
  - [ ] Redis not on any publicly routable interface; auth required.
  - [ ] Startup capability probe passes (PING, auth'd read/write, sorted-set, publish).
  - [ ] One-time backend-outage test performed before production.
  - [ ] `tests/conformance/active/` (in l9-graphiti-memory) run against the real Redis — green.
  - [ ] Rendered ACL matches the contract (prohibited commands actually denied); credentials redacted in logs.
  - [ ] `/healthz` returns 200 post-deploy; `/mcp` reachable from bot hosts over the private network only.

## EXT gate mapping (l9-deploy `UNKNOWN_REGISTER.md`)
Provisioning resolves EXT-001 (approval), EXT-002 (GHCR, via `graphiti-image/`),
EXT-003 (OpenTofu/state), EXT-004 (Ansible idempotency), EXT-005 (runner
isolation), EXT-006 (Infisical OIDC), EXT-007 (staging transaction — Phase 6).
EXT-008 (backup/restore) is covered for the memory store by `l9-sqlite-*`;
postgres remains out of scope.

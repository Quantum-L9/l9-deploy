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
# L9 Provisioning Handoff — Parts B/C + deferred items

> **SUPERSEDED for Memory (2026-10-12).** Every standalone-Memory step in this
> pack is retired and must not be executed: the `mem-*` hosts, `configure-memory.yml`,
> the `graphiti-image/` container, and the `l9-memory-server` deploy. Memory
> (`Quantum-L9/l9-graphiti-memory`) is ProductKind `dependency` (its
> `product-topology.yaml`): it has no runtime identity of its own and runs inside
> its consumer, which deploys through its own consumer-owned `.l9/deployment.yaml`.
> `fleet/registry.yaml` no longer registers `graphiti-memory` or the `mem-*` hosts.
> The management-runner and SEO-Bot registration steps are unaffected. This pack is
> kept as history.

**Audience:** an agent/operator with real credentials (Hetzner, Infisical, an
S3-compatible object store, GitHub admin on `Quantum-L9/l9-deploy`) able to
execute the operator runbook. **This session had no credentials and did not
provision anything.**

**Source of truth:** `Quantum-L9/l9-deploy` branch
`claude/l9-deploy-skill-install-rs1fuf` (this handoff ships inside it). The
in-repo changes (fleet registration, provider pins, Redis + sqlite_backup roles,
`configure-memory.yml`, and the `graphiti-memory` deployment profile) are already
committed and pass `make validate`. What remains is **operator execution** +
two deferred artifacts, all covered here.

## What this pack contains

| File | Purpose |
|---|---|
| `RUNBOOK.md` | Parts B/C, phase by phase, with copy-paste exact commands. |
| `PREFLIGHT_CHECKLIST.md` | Everything that must be true before Phase 1, plus per-phase acceptance gates. |
| `secrets/REQUIRED_SECRETS.md` | The exact secret keys + Infisical paths per environment slug. **No real values.** |
| `secrets/.env.example` | Placeholder names only, to populate from your own vault. |
| `config-changes/CONFIG_CHANGES.md` | The two deferred config edits: runner repo slug (→ `Quantum-L9/l9-deploy`) and the runner tarball SHA-256. |
| `graphiti-image/` | **Retired.** Was a Dockerfile + GHCR publish workflow for a standalone `l9-graphiti-memory` image; do not publish. |

## Decisions locked (do not re-litigate)
- Scope: **full estate, deploy-ready** (management + staging + production).
- Execution: **build as designed** — use the existing `provision-plan.yml` /
  `provision-apply.yml` workflows + protected Environments + self-hosted runner;
  **do not modify existing CI**.
- Redis: ~~in scope for the Memory cache host~~ **retired with the `mem-*` hosts**
  (the `ansible/roles/redis` role itself is unchanged).
- Memory: ~~deploy `l9-memory-server` as a shared fleet service~~ **superseded**:
  Memory is a `dependency` and is deployed only inside its consumer.
- **Out of scope: postgres/pgvector** (SEO-Bot's own deploy stays gated; it is
  registered only).
- **Runner repo slug: `Quantum-L9/l9-deploy`** (confirmed).

## Hard prerequisites / gates
- ~~Memory image (Open Q2)~~ **Retired:** no standalone Memory image is built or
  published; Phase 6 of the runbook is withdrawn.
- **Runner SHA-256 (Open Q1 part):** supply the verified `actions-runner`
  `2.334.0` tarball SHA-256 at runner-config time; never fabricated here.

## Never do
- Do not put real secrets in any committed file or in this pack.
- Do not weaken the Redis ACL, expose Redis publicly, or use `nopass` in staging/production.
- Do not modify the existing CI/provision workflows.
- Do not change deploy behaviour for profiles that declare no `verify_command`.

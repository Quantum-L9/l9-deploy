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
| `graphiti-image/` | Dockerfile + GHCR publish workflow for `l9-graphiti-memory` (Open Q2 — the last gate before a real memory-server deploy). |

## Decisions locked (do not re-litigate)
- Scope: **full estate, deploy-ready** (management + staging + production).
- Execution: **build as designed** — use the existing `provision-plan.yml` /
  `provision-apply.yml` workflows + protected Environments + self-hosted runner;
  **do not modify existing CI**.
- Redis: **in scope** — private, authenticated, ACL-scoped (role: `ansible/roles/redis`).
- Memory: **deploy `l9-memory-server`** as a shared fleet service.
- **Out of scope: postgres/pgvector** (SEO-Bot's own deploy stays gated; it is
  registered only).
- **Runner repo slug: `Quantum-L9/l9-deploy`** (confirmed).

## Hard prerequisites / gates
- **Memory image (Open Q2):** `l9-graphiti-memory` has no container image today.
  Build + publish it (see `graphiti-image/`) before Phase 6.
- **Runner SHA-256 (Open Q1 part):** supply the verified `actions-runner`
  `2.334.0` tarball SHA-256 at runner-config time; never fabricated here.

## Never do
- Do not put real secrets in any committed file or in this pack.
- Do not weaken the Redis ACL, expose Redis publicly, or use `nopass` in staging/production.
- Do not modify the existing CI/provision workflows.
- Do not change deploy behaviour for profiles that declare no `verify_command`.

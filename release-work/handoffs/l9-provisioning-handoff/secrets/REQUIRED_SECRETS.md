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
# Required Secrets (names + locations only — NO values)

Populate these in Infisical per environment slug. Nothing here contains real
values; supply them from your own vault. Redis/DB credential *values* live only
in Infisical and are rendered at deploy time (`runtime_mode: deploy_render`).

## Operator environment (shell, Phase 1–3 bootstrap)
| Var | Used by |
|---|---|
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | `bootstrap-state.sh`, tofu S3 backend |
| `L9_STATE_BUCKET`, `L9_STATE_ENDPOINT`, `L9_STATE_REGION` | state backend + rendered `backend.hcl` |
| `INFISICAL_IDENTITY_ID`, `INFISICAL_PROJECT_SLUG` | `infisical-oidc-env.sh` |

## Infisical, per env slug (`management` / `staging` / `prod`)
| Key | Consumer |
|---|---|
| `TF_VAR_hcloud_token` | OpenTofu Hetzner provider |
| `TF_VAR_ssh_key_ids` | server module (JSON list of numbers) |
| `TF_VAR_network_id` | **staging/prod only** — = management's `network_id` output |
| `TF_VAR_servers` | **staging/prod only** — HCL/JSON map; `private_ip` MUST match `fleet/registry.yaml` |
| `L9_STATE_BUCKET`, `L9_STATE_REGION`, `L9_STATE_ENDPOINT`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | backend.hcl render in workflows |

## Active-memory (graphiti-memory), per env slug — rendered into the deploy env file
| Key | Consumer |
|---|---|
| `l9_redis_acl_password` | `ansible/roles/redis` ACL user + the service's Redis credential |
| Redis URL / connection (per `RedisCredentialSettings`: `url_file` \| `password_file` \| `secret_provider_reference` \| `url_env`) | `l9-memory-server` active-memory backend |
| `deployment_id` | ADR-065 deployment identity (non-placeholder in production) |
| `trust_domain` | ADR-065 deployment identity |
| memory HTTP auth token(s) | server `--transport http` requires auth when bound to `0.0.0.0` |

## Runner (Phase 3, runtime `-e`, never stored in repo)
| Var | Notes |
|---|---|
| `l9_runner_registration_token` | short-lived, repo-scoped for `Quantum-L9/l9-deploy`, single-use |
| `l9_runner_sha256` | verified SHA-256 of the `actions-runner` 2.334.0 tarball |

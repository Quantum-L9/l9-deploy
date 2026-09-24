<!-- L9_META
l9_schema: 1
origin: l9-deploy
layer:
- documentation
- runbook
tags:
- L9_META
- deployment-platform
owner: platform
status: active
/L9_META -->
# Onboard Consumer

1. Author and validate the consumer-owned `.l9/deployment.yaml`.
2. Use the release interface authorized by the current `l9-ci-core` release plane; do not copy
   release orchestration into the consumer or `l9-deploy`.
3. Register the project, canonical profile path, allowed source refs, and target servers in
   `fleet/registry.yaml`.
4. Confirm image repository, health, migration, backup, secret, and ingress policies.
5. Prove staging release and rollback before production authorization.

Retain the consumer source SHA, profile digest, release evidence artifact, image digest, deployment
request, plan digest, approval evidence, deployment receipt, and staging rollback evidence.

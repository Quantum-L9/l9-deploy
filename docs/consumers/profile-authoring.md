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
# Deployment profile authoring

Choose one supported runtime profile. Declare the exact GHCR repository, runtime architecture,
health probes, release strategy, migration and backup rules, Infisical mapping, ingress behavior, and
allowed refs. Do not include credentials. Stateful profiles must define backup and restore-test
commands. Production must use tag refs and immutable image digests.

Validate with:

```bash
uv run l9-deploy contract validate --path .l9/deployment.yaml --schema deployment-profile
```

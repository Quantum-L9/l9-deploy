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
commands. Production must use tag refs and immutable image digests. A `required` service needs a
readiness probe that names its own target (`tcp` with host and port, or `command`/`database` run on
the deployment target); `http` service probes are refused because HTTP probes are issued against the
application's own base URL and an application response cannot qualify an independent dependency.

Validate with:

```bash
uv run l9-deploy contract validate --path .l9/deployment.yaml --schema deployment-profile
```

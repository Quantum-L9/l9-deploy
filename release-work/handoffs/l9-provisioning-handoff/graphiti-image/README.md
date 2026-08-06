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
# graphiti-memory container image (Open Q2)

`l9-graphiti-memory` publishes a PyPI wheel + a TS client but **no container
image**. The fleet deploy of `l9-memory-server` needs one. These two files are
authored **for the `Quantum-L9/l9-graphiti-memory` repo** — commit them there,
not into `l9-deploy`.

## Placement in `l9-graphiti-memory`
- `Dockerfile` → repo root `Dockerfile`.
- `publish-image.yml` → `.github/workflows/publish-image.yml`.

## What it produces
- Image `ghcr.io/quantum-l9/l9-graphiti-memory` published **by digest**, with
  build **provenance** and an **SBOM** attestation — matching the
  `graphiti-memory` deployment profile's `artifact` policy
  (`require_digest`, `require_provenance_attestation`, `require_sbom_attestation`).
- Runs `l9-memory-server --transport http --host 0.0.0.0 --port 8200`
  (`/healthz`, `/mcp`), non-root, with the canonical SQLite store on
  `/var/lib/l9-memory` (declared as the profile's persistent volume).

## Confirm before publishing (owner of l9-graphiti-memory)
- The exact env/config the server reads for **HTTP auth tokens**, **Redis
  credentials** (`RedisCredentialSettings`), and **deployment identity**
  (`deployment_id`/`trust_domain`) — these arrive via the deploy-render env file
  at runtime; the Dockerfile does not bake them.
- Whether the worker (`l9-memory-worker`) runs as a sidecar/second container or
  is out of the first cut.

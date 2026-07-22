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
# Consumer adoption

Render a thin consumer kit with `scripts/package-adoption-kit.py`, review every generated value,
commit it in the consumer, and register the consumer centrally in `fleet/registry.yaml`. The caller
workflow invokes `Quantum-L9/l9-ci-core/.github/workflows/container-release.yml@v1`; it must not copy
platform logic or target the private runner.

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
# L9 Deployment Platform

**Source release:** `0.1.5`  
**Local release status:** validated and warning-free  
**Production status:** externally gated until live staging and infrastructure evidence exists

Private, evidence-bearing provisioning and deployment control plane for Quantum-L9.

## Purpose

`l9-deploy` provisions Hetzner infrastructure, configures hosts, deploys
approved OCI image digests, verifies health, records immutable receipts, and restores the
previous verified release when a transaction fails.

It is intentionally separate from source validation:

- `l9-ci-sdk` owns canonical evidence and schema validation.
- `l9-ci-core` orchestrates CI and produces approved release evidence.
- `Quantum-L9/.github` publishes organization interfaces and thin starter workflows.
- This repository owns infrastructure provisioning, host configuration, deployment,
  rollback, and operational receipts.

## Trust model

A production mutation requires all of the following:

1. Canonical `l9-ci-sdk` finding-bundle evidence.
2. An external CI gate binding tied to the source repository, commit, ref, and workflow run.
3. A status-free artifact binding tied to one immutable GHCR digest.
4. A deterministic deployment or infrastructure plan digest.
5. Independent GitHub protected-environment approval for that exact plan.
6. A repository-scoped dedicated deployment runner on the Hetzner private network.
7. Create-only, content-addressed receipt publication into a hash-chained ledger.

Self-authored PASS evidence, mutable image tags, self-issued approvals, receipt overwrites,
and public pull-request access to the deployment runner are rejected.

## Architecture classification

This repository is a non-node infrastructure control plane. GitHub Actions,
`repository_dispatch`, SSH, GHCR, Infisical, OpenTofu, Ansible, and Hetzner are external
control-plane integrations, not constellation node messages. Any future work directed to a
constellation node must use `TransportPacket` through Gate.

See `.l9/transport-classification.yaml`.

## Primary commands

```bash
uv sync --all-extras --frozen
uv run l9-deploy --help
uv run l9-deploy request validate --request request.json --fleet fleet/registry.yaml --json
uv run l9-deploy plan --request request.json --fleet fleet/registry.yaml --output plan.json --json
uv run l9-deploy approval verify \
  --environment production \
  --expected-plan-digest sha256:<digest> \
  --approval-receipt approval-receipt.json \
  --approval-history approval-history.json \
  --approval-run-id <run-id> \
  --request-id <request-id> \
  --requester <requester> \
  --json
uv run l9-deploy receipt ledger-verify --ledger-root receipts/ledger --json
```

## Validation

```bash
PYTHONPATH=src python3 -m pytest -q -W error \
  --cov=l9_deploy --cov-branch --cov-report=term-missing \
  --cov-report=xml:artifacts/coverage.xml --cov-fail-under=75
PYTHONPATH=src python3 scripts/validate-contracts.py
python3 scripts/validate-workflows.py
python3 scripts/verify-l9-meta.py
python3 scripts/fast-contract-scan.py
python3 scripts/validate-alignment.py
bash -n scripts/*.sh
make release-prepare
SOURCE_DATE_EPOCH="$(git log -1 --pretty=%ct)" \
  make release-archive \
  ARCHIVE=../l9-deploy.zip \
  RECEIPT=../l9-deploy.receipt.json
```

`release-artifacts` regenerates the manifest, responsibility map, final tree, and checksum
index. `release-pack-check` rejects stale inventory, version drift, nested archives, cache
residue, and checksum mismatches. The archive builder is deterministic for a fixed source tree
and `SOURCE_DATE_EPOCH`; archive validation proves exact file inventory, bytes, executable modes,
root confinement, and ZIP integrity.

CI additionally runs Ruff, Ruff formatting, strict mypy, Semgrep, and canonical
`l9-ci-sdk` normalization.

## Durable contract naming

The established v1 wire contracts remain self-describing with key `schema`. Python contract DTOs
use `schema_id` with the narrow, governed alias `Field(alias="schema")` to avoid framework namespace
collisions. External payloads must use `schema`; runtime-only names are rejected and never serialized.
Published JSON Schemas, the wire contract catalog, round-trip tests, warnings-as-errors, and the L9
contract scanners enforce this boundary. See `docs/adr/0007-wire-contract-field-aliases.md`.

## Source-release integrity

The repository ZIP is a deterministic source artifact, not an informal folder dump. A detached
`l9.repository-release-receipt/v1` document binds the exact ZIP to `MANIFEST.json`, repository
identity, semantic version, archive digest, byte size, member count, and `SOURCE_DATE_EPOCH`.
The receipt remains outside the ZIP to avoid self-reference. Release validation checks source-to-ZIP
inventory, bytes, modes, root confinement, timestamps, receipt digest, and archive integrity.

All release outputs are written outside the source root. This prevents `dist/`, coverage databases,
reports, or a partially written ZIP from contaminating the artifact being attested.

## Repository map

- `src/l9_deploy/`: typed control-plane implementation and CLI.
- `schemas/v1/`: versioned JSON contracts.
- `infrastructure/opentofu/`: Hetzner infrastructure modules and environments.
- `ansible/`: host, runner, Docker, firewall, backup, and conformance configuration.
- `.github/workflows/`: validation, provisioning, deployment, rollback, and fleet workflows.
- `integrations/`: thin projections for `.github`, `l9-ci-core`, and consumer repositories.
- `tests/`: contract, security, transaction, workflow, infrastructure, and compliance tests.
- `receipts/`: runtime location for content-addressed operational evidence, not committed data.
- `validation/`: generated validation evidence for the packaged release.

## Safety invariants

- Build once and deploy by digest.
- Never build application source on production servers.
- Never deploy `latest`, `main`, or another mutable tag.
- Never accept a deployment request without canonical external CI evidence.
- Never treat `github.actor` as proof of environment approval.
- Never overwrite canonical receipts.
- Never run public pull-request jobs on the deployment runner.
- Never apply an infrastructure plan other than the exact approved plan file and digest.
- Never hide blocked validation behind a PASS label.

See `RUNBOOK.md`, `SECURITY.md`, `ARCHITECTURE.md`, and `VALIDATION.md`.

## Canonical repository identity

The canonical repository identity is `Quantum-L9/l9-deploy` and the canonical short name is
`l9-deploy`. Historical `origin: l9-deployment-platform` values in L9 metadata are provenance labels,
not active repository coordinates. They are retained only where changing them would rewrite artifact
history. Live repository URLs, OIDC claims, runner scopes, integration producers/consumers, archive
names, and operator instructions must use `Quantum-L9/l9-deploy`.

See `docs/operations/repository-identity.md` and `docs/agents/deployment-agent.md`.

## Release-owned runtime configuration

Each candidate release owns a protected `runtime.env` inside its digest-addressed release directory.
Secret preparation writes a validated temporary file and atomically publishes it with mode `0600`.
Migration and Docker Compose consume the same candidate env path. Promotion records image and
configuration identity together; rollback restores the previous release directory, env file, image,
and health before republishing state. The mutable top-level `runtime.env` is not a release authority.

OIDC is job-scoped. Only jobs that exchange GitHub identity for Infisical credentials may request
`id-token: write`; validation and approval jobs may not mint tokens.

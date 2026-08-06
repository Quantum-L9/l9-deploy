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
# Architecture

## System role

`l9-deploy` is the authoritative provisioning and deployment control plane for
Quantum-L9 hosted services. It is not a constellation runtime node, CI evidence producer,
secret authority, or application repository.

## Control flow

```text
consumer repository
  -> l9-ci-core workflow
  -> canonical l9-ci-sdk evidence
  -> immutable GHCR digest
  -> bounded deployment request
  -> private deployment repository
  -> protected-environment authorization
  -> dedicated deployment runner
  -> Hetzner private network
  -> target host
  -> health verification
  -> append-only receipt ledger
```

## Authority boundaries

### `l9-ci-sdk`

Owns provider normalization, canonical evidence, findings, gate outcomes, compatibility,
and deterministic serialization. This repository consumes those artifacts and does not
reconstruct them.

### `l9-ci-core`

Owns CI orchestration, image build and publication, SBOM and provenance, and the bounded
release request. Its release integration must download and validate external canonical
CI evidence before binding it to an image.

### `Quantum-L9/.github`

Owns the public organization interface registry and thin starter workflows. It does not
contain deployment execution logic or production credentials.

### `l9-deploy`

Owns request verification, deterministic plans, authorization verification, OpenTofu,
Ansible, private runner execution, deployment transactions, rollback, and receipts.

## Trust-boundary artifacts

### CI gate binding

`l9.ci-gate-binding/v1` binds a successful canonical CI gate to the source repository,
commit SHA, ref, workflow run, SDK version, schema version, and canonical bundle digest.

### Release artifact binding

`l9.release-artifact-binding/v1` binds the external gate and canonical bundle to one exact
image digest. It intentionally contains no PASS field of its own.

### Approval receipt

`l9.approval-receipt/v1` is derived from GitHub's protected-environment approval history.
It binds the reviewer, requester, environment, plan digest, workflow run, attempt, job,
workflow ref, timestamp, and raw approval-history digest. The requester cannot approve the
same mutation.

### Deployment receipt

`l9.deployment-receipt/v1` records the source revision, image digest, plan, previous release,
steps, artifacts, timestamps, result, and unknowns. The receipt is content-addressed and
written create-only.

## Contract representation boundary

Durable YAML and JSON contracts are self-describing and retain the established v1 key `schema`.
Pydantic DTOs use the runtime attribute `schema_id` with a strict alias solely at this lexical
boundary. External payloads are validated by alias and runtime field names are rejected. Durable
serialization always emits the wire name.

The contract catalog binds each schema identity to one runtime DTO and one published JSON Schema.
CI verifies catalog completeness, top-level field and requiredness parity, schema identity, wire
round-trip behavior, and warning-free imports. Lexical renaming uses aliases; semantic conversion
requires an explicit mapper and versioned contract evolution.

## Receipt ledger

Canonical receipts are stored under a digest-derived path. The append-only `index.jsonl`
contains a monotonically increasing sequence, previous-entry digest, receipt digest,
receipt path, timestamp, and entry digest. A mutable latest pointer is a convenience view
only and is never authoritative.

The ledger verifier detects:

- receipt mutation,
- receipt replacement,
- duplicate sequence entries,
- broken previous-entry links,
- altered entry digests,
- missing content-addressed receipts.

## Deployment transaction

The transaction uses an idempotency state machine:

```text
IN_PROGRESS -> PREPARED -> COMPLETE
      |             |
      +-----------> FAIL, only before authoritative receipt publication
FAIL --same request digest retry--> IN_PROGRESS
```

1. Verify request, evidence, plan, image digest, target, and approval.
2. Acquire the environment lock.
3. Execute backup, pull, render, migration, deployment, health, and promotion steps.
4. Build and validate the deployment receipt.
5. Mark the request `PREPARED` with the receipt digest.
6. Publish the authoritative receipt to the immutable ledger.
7. Mark the request `COMPLETE`.

Every persisted transition is reconstructed through the frozen contract model. Illegal transitions,
invalid digests, blank failure reasons, and receipt replacement are rejected. If final idempotency
indexing fails after receipt publication, replay loads the authoritative receipt from the ledger and
completes the index. It does not roll back a committed release.
If failure occurs before authoritative publication, runtime and release-state pointers are
restored together when rollback is allowed.

## Release artifact boundary

The release tree is frozen after validation. A deterministic builder emits one canonical-root ZIP
from the shared release inventory. Validation proves that every archive member exists in the source
tree with identical bytes and executable mode and that no untracked, unsafe, cached, symlinked, or
nested-archive content is present. The repository ZIP is therefore a source-bound release artifact,
not an incidental directory snapshot.

## Network model

The dedicated runner and target hosts share Hetzner private networking. Application hosts
accept management traffic only from the runner's private address. Public ingress is limited
to service ports, normally 80 and 443. Host-level firewall rules remain required because
private-network traffic is not treated as automatically filtered.

## Extensibility

Supported profiles are bounded:

- `static-site`
- `container-service`
- `worker-service`
- `stateful-container`
- `scheduled-job`
- `external-platform`

New adapters must preserve the evidence, approval, digest, lock, receipt, and rollback
invariants. A profile may extend execution behavior but may not bypass the trust spine.

## Canonicalization boundary

Human-authored YAML and JSON are parsed into validated logical contracts. Digest-bearing content is
then serialized to deterministic UTF-8 JSON with sorted keys, compact separators, alias-aware wire
names, and non-finite numbers prohibited. Hashes and signatures operate on those bytes, not emitted
YAML. Cryptographic signing and key management remain composed services rather than model methods.


## Repository source-release trust boundary

Application deployment receipts and repository source-release receipts are different authorities.
Application receipts prove a runtime mutation. `l9.repository-release-receipt/v1` proves that one
repository ZIP matches one frozen source manifest and reproducible timestamp.

```text
validated source root
  -> deterministic manifest and checksums
  -> deterministic ZIP outside source root
  -> detached repository release receipt
  -> receipt and archive validation
  -> publication as one release set
```

The receipt is deliberately detached to avoid recursive hashing. Its digest covers every receipt
field except `receipt_digest`, while `archive_sha256` covers the ZIP bytes and
`source_manifest_sha256` covers the frozen source inventory. The release workflow may publish only
when all three identities agree.

## Release-owned configuration transaction

```text
approved immutable plan
  -> create digest-addressed candidate release directory
  -> materialize validated runtime.env.tmp
  -> chmod 0600 and atomic rename to runtime.env
  -> run migration with candidate runtime.env
  -> run Docker Compose with candidate runtime.env
  -> verify health
  -> atomically promote image + runtime configuration identity
  -> retain previous release as rollback target
```

The release directory is the unit of runtime identity. Candidate and active release identities may
not collide. Missing previous configuration identity or a missing previous env file fails before
remote mutation. A failure before promotion leaves active state byte-identical and removes only the
failed candidate directory.

Rollback is configuration-consistent: it selects the previous release directory, uses that
release's `runtime.env`, restores the previous image, verifies health, and only then republishes the
previous state pointer. Database recovery remains a separate policy decision.

## Workflow identity boundary

Workflow-level OIDC is prohibited. Token permission belongs only to the exact secret-consuming job.
Approval, request-validation, and evidence-validation jobs operate without `id-token: write`. The
workflow validator enforces both directions: an Infisical consumer requires job-scoped OIDC, and a
job with OIDC must contain the approved Infisical consumer.

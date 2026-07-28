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
# Security

## Security boundary

This repository can provision infrastructure and mutate production systems. Treat its
workflows, schemas, runner, OpenTofu state, Ansible roles, approval evidence, and receipt
ledger as high-blast-radius assets.

## Mandatory controls

- The repository is private.
- The self-hosted runner is repository scoped and cannot execute public pull-request code.
- Mutating workflows use protected environments and independent approval evidence.
- The requester cannot approve the same mutation.
- Canonical CI evidence is consumed, not recreated.
- OCI images are deployed by digest only.
- GitHub Actions are pinned to immutable SHAs or governed Quantum-L9 major interfaces.
- Secrets come from Infisical through workload identity where supported.
- Target hosts are reached through Hetzner private networking.
- Canonical receipts are create-only and hash chained.
- Durable contract serialization preserves wire names and rejects runtime-only field names.
- Repository archives are deterministic and verified against exact source bytes and modes.
- Logs and evidence are redacted before persistence, including explicit secret environment values.
- Missing GitHub repository context is an authorization failure.
- Infisical environment rendering rejects invalid names, duplicates, CR/LF, and NUL bytes.
- Subprocess timeouts terminate process groups and drain pipes.
- HTTP health probes reject non-HTTP schemes.
- Canonical JSON rejects non-finite numbers.
- Infrastructure apply uses the exact approved plan artifact.

## Approval integrity

The approval collector queries GitHub's workflow-run approval history and preserves the raw
response. The approval receipt contains its digest and the verifier rechecks reviewer,
requester, environment, plan, run, and timestamp. A locally written `approved: true` document
without matching approval history is rejected.

## Evidence integrity

The release request must reference:

- a valid canonical finding bundle,
- an external CI gate binding,
- a status-free image binding,
- the exact source workflow run,
- the exact source commit and ref,
- the exact image digest,
- SBOM and provenance references.

Any digest or source mismatch fails closed.

## Runner hardening

The deployment runner must not host applications, databases, or general CI. Restrict outbound
and inbound traffic, rotate registration material, remove workspace residue after jobs, and
rebuild the host rather than manually repairing configuration drift.

## Receipt and audit security

Never edit canonical ledger entries or receipts. The latest pointer is non-authoritative.
Back up the full ledger directory with retention and restore testing. A ledger verification
failure is an incident, not a formatting problem.

## Break-glass access

Break-glass access must be time bounded, attributable, and followed by reconciliation through
OpenTofu and Ansible. Record the incident, commands, affected hosts, resulting state, and the
follow-up receipt. Do not normalize emergency manual state as the new baseline without review.

## Reporting

Report vulnerabilities through the private GitHub Security Advisory process for the affected
Quantum-L9 repository. Do not disclose runner credentials, infrastructure state, approval
history, secrets, host addresses, or production receipts in public issues.

## Boundary data handling

Durable wire contracts accept only their published field names. Runtime aliases are narrowly
limited to the `schema_id` to `schema` identity mapping and are enforced by AST policy. Evidence
records are redacted, hashed, and validated against their published schema before use.

Infisical exports are treated as hostile boundary data. Each item must be an object with a unique
POSIX-compatible environment key and a single-line, NUL-free string value. Captured subprocess
output is redacted using both pattern rules and explicit secret values supplied to the command.


## Repository release supply-chain controls

Source releases are built outside the repository tree from a frozen, validated inventory. The
platform rejects mutable or self-contaminating release inputs, including build directories,
coverage databases, coverage reports, caches, nested archives, symlinks, unsafe paths, and stale
checksums.

The detached repository release receipt binds repository identity, version, exact archive name,
archive SHA-256, byte size, member count, source manifest SHA-256, and reproducible timestamp. A
receipt digest mismatch, archive rename, source manifest drift, member mismatch, mode drift, or
non-uniform timestamp is a release-blocking integrity failure.

## Job-scoped OIDC policy

The repository claim used by GitHub OIDC policy is `Quantum-L9/l9-deploy`. Workflow-level
`id-token: write` is forbidden. The only jobs permitted to request it are:

- `deploy-dispatch.yml` / `deploy`
- `drift-detect.yml` / `plan`
- `provision-plan.yml` / `plan`
- `provision-apply.yml` / `apply`

Every permitted job must actually exchange the token through the approved Infisical path. Approval
and validation jobs must not request identity tokens. External Infisical claim restrictions remain a
Phase 6 validation dependency and must be tested with positive and negative exchanges.

## Runtime secret retention

Release-owned `runtime.env` files contain secret material and are mode `0600`. They are never logged,
attached as workflow artifacts, copied into receipts, or treated as generated evidence. Cleanup may
remove only validated stale digest-addressed release directories and must retain the active and
rollback releases. Operators must not edit historical env files in place.

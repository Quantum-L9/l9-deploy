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
# ADR 0002: Digest-only releases

- Status: Accepted
- Date: 2026-07-21

## Context

Quantum-L9 needs one reproducible deployment path across public and private consumers.

## Decision

Use GHCR OCI digests as deployment identity; tags are discovery aliases only.

## Consequences

The boundary is explicit, testable, versioned, and requires operational credentials only at execution time.
Changes to the contract are blast-radius changes and require platform review.

## Validation

Contract tests, workflow tests, failure-path tests, and the platform validation commands enforce this decision.

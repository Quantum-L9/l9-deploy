<!-- L9_META
l9_schema: 1
origin: l9-deploy
layer:
- documentation
- agent-contract
tags:
- L9_META
- deployment-agent
owner: platform
status: active
/L9_META -->
# Deployment Agent Operating Contract

## Mission

Operate the `Quantum-L9/l9-deploy` control plane without acquiring infrastructure ownership or
production authority. The agent may transform an authorized request into validated plans, reviewed
source changes, and evidence. Humans and protected environments remain the approval authority.

## Owned responsibilities

- Inspect repository source, schemas, tests, workflow wiring, fleet declarations, and receipts.
- Validate deployment requests, immutable digests, evidence references, plan digests, approvals, and
  ledger integrity through repository-supported commands.
- Prepare deterministic deployment and infrastructure plans.
- Implement explicitly authorized repository changes on a change branch.
- Run targeted and repository-native validation.
- Produce redacted validation evidence, change summaries, rollback instructions, and unknowns.
- Trigger governed workflows only when the user explicitly authorizes that mutation.

## Excluded responsibilities

- Owning application source, cloud accounts, secrets, CI findings, registry policy, or databases.
- Granting itself approval, widening scopes, changing protected-environment rules, or weakening OIDC
  claims.
- Direct production SSH, ad hoc Compose mutation, direct OpenTofu apply, or manual state editing.
- Inferring database rollback from container rollback.
- Publishing, committing, pushing, opening a pull request, releasing, or deploying without explicit
  authorization for that lifecycle action.

## Authority order

1. Latest explicit user instruction.
2. Repository policy and protected-environment controls.
3. Approved immutable request, plan digest, and approval evidence.
4. Validated schemas, source, and tests.
5. Operational documentation.
6. Unknowns, which fail closed.

No lower authority may override a higher one.

## Read operations

The agent may inspect tracked source, status, branches, diffs, schemas, workflow definitions, plans,
receipts, logs, and redacted external evidence. Secret values must never be requested merely for
inspection. Reading production hosts, external state, or private policy requires explicit access and
scope.

## Mutation operations

Repository mutation is allowed only when the user authorizes a phase or change scope. Keep each phase
within its file ceiling, preserve unrelated work, and never edit generated Phase 5 evidence manually.
External mutation requires separate explicit authorization and must use the governed workflow.

## Required deployment gates

Before deployment execution, verify:

- exact repository and source revision;
- immutable OCI digest and provenance evidence;
- validated deployment request and profile digest;
- deterministic plan and expected plan digest;
- independent protected-environment approval for that exact plan;
- host and environment lock;
- job-scoped OIDC only on the secret-consuming job;
- previous image and runtime configuration identity for rollback.

Any mismatch, missing evidence, stale approval, mutable tag, unknown secret contract, or absent rollback
configuration fails closed.

## Secret handling

- Retrieve secrets only through the approved GitHub OIDC to Infisical path.
- Never echo, serialize, attach, commit, summarize, or include secret values in receipts.
- Candidate secrets are written to a temporary file, validated, chmod `0600`, and atomically renamed
  to the release-owned `runtime.env`.
- Do not overwrite active or historical env files in place.
- Redact explicit secret values from subprocess output.

## Release transaction

1. Validate request, evidence, plan, approval, and locks.
2. Create the digest-addressed candidate release directory.
3. Materialize the candidate `runtime.env` atomically.
4. Run migration and Compose using the same candidate env.
5. Verify health.
6. Promote image and configuration identity together.
7. Publish immutable receipt evidence.
8. Retain active and rollback releases; clean only validated stale releases.

A pre-promotion failure must leave active state byte-identical and remove only the failed candidate.

## Rollback trigger and behavior

Trigger rollback on failed candidate health, failed post-start validation, or an explicitly approved
incident rollback. Preflight the previous configuration identity and env file before mutation. Restore
the previous image with its release-owned env, verify health, then restore the previous state pointer.
If rollback health fails, stop, preserve evidence, and escalate. Database recovery remains separate.

## Validation and reporting

Run the narrowest targeted tests first, then repository-native contract, workflow, alignment, syntax,
compile, and full test gates available in the environment. Report exact commands, passes, failures,
coverage, unavailable tools, environmental blockers, changed-file count, and whether any external
mutation occurred. Never convert missing evidence into a PASS.

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
# L9 Deployment Platform Repository Specification

## 1. Specification metadata

```yaml
specification:
  name: l9-deployment-platform-repository-specification
  version: 1.0.0
  status: proposed
  date: 2026-07-20
  target_repository: Quantum-L9/l9-deployment-platform
  recommended_visibility: private
  authoritative_role: infrastructure_provisioning_and_deployment_control_plane
  primary_cloud: Hetzner Cloud
  deployment_connectivity: dedicated_self_hosted_runner_plus_hetzner_private_network
  first_reference_consumer: Quantum-L9/SEO-Bot
```

## 2. Executive decision

Create one private repository named `Quantum-L9/l9-deployment-platform`.

The repository becomes the authoritative control plane for:

1. Provisioning Hetzner infrastructure with OpenTofu.
2. Configuring and hardening servers with Ansible.
3. Operating the dedicated GitHub Actions deployment runner.
4. Receiving authenticated deployment requests from consumer repositories.
5. Verifying release evidence, image provenance, image digest, source revision, and deployment policy.
6. Deploying exact OCI image digests from `ghcr.io`.
7. Running backups, migrations, health checks, and rollback.
8. Producing immutable deployment, rollback, backup, migration, and conformance receipts.
9. Detecting infrastructure and host-configuration drift.
10. Maintaining a reproducible fleet inventory and desired-state ledger.

The repository does not become another CI implementation, observability platform, application monorepo, secrets store, image registry, or policy-pack warehouse.

## 3. Architectural thesis

The deployment platform must separate five concerns that are frequently tangled together:

```text
source validation     -> l9-ci-core + l9-ci-sdk
release artifact      -> GHCR image by immutable digest
release authorization -> GitHub environment and deployment request contract
execution             -> private l9-deployment-platform runner
runtime               -> Hetzner servers on private networks
```

The canonical path is:

```text
Consumer repository
  -> l9-ci-core validates source and builds release evidence
  -> GitHub-hosted runner builds one OCI image
  -> image is pushed to GHCR
  -> image provenance and SBOM are attached
  -> a bounded deployment request is dispatched
  -> private deployment repository validates the request
  -> dedicated runner reaches target hosts through Hetzner private networking
  -> exact digest is deployed
  -> health and operational probes run
  -> success or rollback receipt is emitted
```

The server never clones the application repository, runs `git pull`, builds source, resolves mutable package versions, or deploys a mutable `latest` image.

## 4. Current Quantum-L9 alignment

### 4.1 Quantum-L9/.github

Observed role:

- Organization governance and community-health backbone.
- Public workflow interface registry.
- Starter workflow templates.
- Organization profile and adoption documentation.
- Blast-radius review ownership through CODEOWNERS.

Required deployment-platform integration:

- Add a separate public `deployment-interface-registry.yml`.
- Add deployment caller templates under `workflow-templates/`.
- Update organization profile architecture table.
- Extend CODEOWNERS for deployment interface files and templates.
- Add deployment onboarding and incident issue forms.
- Do not place provisioning or deployment implementation in `.github`.

### 4.2 Quantum-L9/l9-ci-core

Observed role:

- Thin GitHub Actions control plane.
- Provisions and invokes `l9-ci-sdk`.
- Owns workflow permissions, provider selection, artifact publication, checks, and pull-request summaries.
- Must not reconstruct canonical findings or copy SDK schemas.

Required deployment-platform integration:

- Continue owning public build and release workflow orchestration.
- Add or formalize container-release and deployment-request kernels.
- Produce a bounded release request and release receipt.
- Never SSH to production and never execute OpenTofu or Ansible against production.
- Never decide target infrastructure topology.
- Never mutate deployment receipts after platform execution.

### 4.3 Quantum-L9/l9-ci-sdk

Observed role:

- Canonical CI evidence, findings, provider failure records, coverage records, bundle construction, schema validation, semantic validation, deterministic serialization, and agent-review projection.

Required deployment-platform integration:

- Deployment requests may reference SDK-owned release evidence as immutable inputs.
- The deployment platform treats SDK bundles as validated evidence references.
- The deployment platform must not parse provider-native reports or reconstruct SDK findings.
- No phase-1 SDK changes are required.
- Future SDK support may add a generic release-evidence projection, but deployment-domain receipts remain owned by `l9-deployment-platform`.

### 4.3.1 Repository source-release receipt

The deployment platform owns a separate `l9.repository-release-receipt/v1` contract for its own
source distribution. It binds the deterministic repository ZIP to the repository identity,
semantic version, frozen `MANIFEST.json`, archive digest, byte size, member count, and
`SOURCE_DATE_EPOCH`. It is detached from the ZIP to avoid self-referential hashing and is not a
substitute for application CI evidence or runtime deployment receipts.

Release outputs must be created outside the validated source root and published only after exact
source, archive, and receipt validation succeeds.

### 4.4 Quantum-L9/l9-assurance

Observed role:

- Reusable compliance-grade DevOps assurance and security testkits.

Required deployment-platform integration:

- Use verified assurance packages for contract tests, security tests, evidence-integrity checks, and release-gate tests where package interfaces exist.
- Do not duplicate assurance packages inside the deployment repository.
- Do not make `l9-assurance` responsible for deployment execution.

### 4.5 Quantum-L9/l9-repo-template

Observed baseline:

- The repository currently contains only its root README.

Required deployment-platform integration:

- Receive a generated consumer adoption projection from the deployment platform.
- Include thin caller workflows and a deployment-profile template.
- Record source repository, source tag, source commit, and generated digest.
- Never become the authority for deployment schemas or workflow logic.

### 4.6 Consumer repositories

Consumer repositories own application-specific facts only:

- Application source.
- Dockerfile or OCI build definition.
- Application test and build commands.
- Port and health endpoint.
- Runtime profile selection.
- Required volumes and standard dependencies.
- Migration command and migration policy.
- Deployment profile.
- Optional validated Compose bundle for complex services.

They do not own:

- Server provisioning.
- Server hardening.
- Runner installation.
- Fleet inventory.
- Production SSH keys.
- Hetzner API tokens.
- Central deployment logic.
- Rollback implementation.
- Deployment receipt schemas.

## 5. Repository identity and boundaries

### 5.1 Canonical purpose

`l9-deployment-platform` is a private, deterministic, policy-enforced infrastructure and deployment control plane for Quantum-L9 projects.

### 5.2 Primary responsibilities

```yaml
responsibilities:
  infrastructure:
    - network provisioning
    - firewall provisioning
    - server provisioning
    - volume provisioning
    - server replacement
    - remote state management
  host_configuration:
    - base operating-system configuration
    - host firewall policy
    - SSH hardening
    - Docker installation
    - reverse-proxy installation
    - backup-agent installation
    - deployment-user management
    - runner installation and maintenance
  deployment:
    - request validation
    - release-plan construction
    - image-attestation verification
    - digest-based deployment
    - migration orchestration
    - backup orchestration
    - health verification
    - rollback
    - receipt generation
  governance:
    - environment authorization
    - concurrency control
    - idempotency
    - audit trail
    - drift detection
    - fleet conformance
```

### 5.3 Explicit non-goals

```yaml
non_goals:
  - application source hosting
  - application compilation on servers
  - CI finding normalization
  - provider-native scanner parsing
  - centralized observability implementation
  - central policy-pack implementation
  - general secret storage
  - OCI image storage
  - Kubernetes orchestration
  - multi-cloud abstraction in version 1
  - arbitrary shell execution service
  - public pull-request execution on the deployment runner
  - direct public-repository access to the private runner
```

Centralized observability must remain a separate shared capability. This repository emits structured deployment signals and receipts but does not own the organization-wide logging, metrics, traces, dashboards, or alerting stack.

## 6. Repository visibility and trust boundary

### 6.1 Visibility

`Quantum-L9/l9-deployment-platform` must be private.

Reasons:

- It contains fleet topology and host aliases.
- It owns runner and deployment implementation.
- It has network access to private infrastructure.
- It processes production deployment authorization.
- GitHub recommends that self-hosted runners be limited to trusted private repositories.

### 6.2 Public consumer boundary

Public consumer repositories must not call a private reusable deployment workflow directly and must not execute on the self-hosted deployment runner.

They may:

- Build on GitHub-hosted runners.
- Push an image to GHCR.
- Generate attestations and SBOMs.
- Request deployment through the bounded broker interface.

They may not:

- Possess production SSH credentials.
- Possess Hetzner API credentials.
- Possess OpenTofu state credentials.
- Run arbitrary code on the deployment runner.
- Select an unregistered target host.
- bypass environment approval or platform policy.

## 7. System architecture

### 7.1 Trust zones

```text
ZONE A: Public source and CI
  public or private consumer repositories
  GitHub-hosted runners
  l9-ci-core workflows

ZONE B: Artifact registry
  GHCR images
  image attestations
  SBOM attestations

ZONE C: Private deployment control plane
  private l9-deployment-platform repository
  protected GitHub environments
  dedicated self-hosted runner group
  Infisical OIDC identity

ZONE D: Hetzner management network
  l9-deploy-01
  private network interfaces
  host firewall enforcement

ZONE E: Application runtime
  production and staging servers
  PostgreSQL and Redis services
  application containers
  persistent volumes
```

### 7.2 Management server

Recommended host identity:

```yaml
management_server:
  name: l9-deploy-01
  role: deployment_runner_and_management_plane
  application_workloads_allowed: false
  databases_allowed: false
  public_ingress_default: deny
  outbound_https: required
  private_network_access: required
  runner_group: l9-deployment-runners
  runner_repository_access:
    - Quantum-L9/l9-deployment-platform
  runner_workflow_allowlist:
    - .github/workflows/deploy-dispatch.yml
    - .github/workflows/deploy-manual.yml
    - .github/workflows/provision-apply.yml
    - .github/workflows/configure-hosts.yml
    - .github/workflows/rollback.yml
    - .github/workflows/fleet-conformance.yml
```

### 7.3 Network topology

Recommended initial topology:

```text
Hetzner Project
  Network: l9-platform
    subnet: management
      l9-deploy-01
    subnet: staging
      staging application hosts
      staging data hosts
    subnet: production
      production application hosts
      production data hosts
```

CIDRs are configuration values, not hard-coded protocol values. A recommended default may be provided, but the selected ranges must be recorded in the environment configuration and checked for overlap.

### 7.4 Firewall model

Hetzner Cloud Firewalls protect public interfaces. Host-level nftables or UFW rules must additionally protect private-network traffic because Hetzner Cloud Firewalls do not filter private-network traffic.

Required policy:

- Application hosts expose only 80 and 443 publicly when required.
- Application-host SSH accepts only the management server private IP.
- Database ports accept only explicitly authorized application subnets or hosts.
- Redis is never publicly exposed.
- Deployment runner public SSH is disabled by default.
- Break-glass SSH requires a temporary, recorded firewall exception or console rescue procedure.
- All network rules are generated from machine-readable policy.

## 8. Release and deployment request boundary

### 8.1 Broker mechanism

Use a dedicated GitHub App named `l9-deployment-broker`.

The public release workflow mints a short-lived installation token and creates a `repository_dispatch` event in the private deployment repository.

Required event type:

```text
l9.release.requested.v1
```

The GitHub App must have the minimum permissions necessary:

```yaml
github_app_permissions:
  metadata: read
  contents:
    consumer_repositories: read
    deployment_repository: write
  actions:
    consumer_repositories: read
  attestations:
    consumer_repositories: read
  packages:
    organization_packages: read
```

The exact permission set must be validated against current GitHub App capabilities before installation. Unknown or unsupported permissions fail closed.

### 8.2 Request payload

The dispatch payload must remain bounded and versioned:

```json
{
  "schema": "l9.deployment-request/v1",
  "request_id": "drq_<deterministic-id>",
  "source": {
    "repository": "Quantum-L9/SEO-Bot",
    "commit_sha": "40-hex-sha",
    "ref": "refs/heads/main",
    "workflow_run_id": 123456789
  },
  "artifact": {
    "image": "ghcr.io/quantum-l9/seo-bot",
    "digest": "sha256:<digest>",
    "attestation_subject": "oci://ghcr.io/quantum-l9/seo-bot@sha256:<digest>",
    "sbom_digest": "sha256:<digest>"
  },
  "target": {
    "environment": "staging",
    "deployment_profile_path": ".l9/deployment.yaml",
    "deployment_profile_digest": "sha256:<digest>"
  },
  "evidence": {
    "release_receipt_digest": "sha256:<digest>",
    "ci_bundle_digest": "sha256:<digest>",
    "gate_status": "PASS"
  },
  "idempotency_key": "sha256:<digest>"
}
```

### 8.3 Request validation

The private platform must verify all of the following before planning a deployment:

1. Request schema and supported major version.
2. Repository is registered and enabled for deployment.
3. Source commit exists in the declared repository.
4. Source ref is allowed by environment policy.
5. Workflow run belongs to the source repository and commit.
6. Required CI gate is successful.
7. Image digest exists in the expected GHCR namespace.
8. Image provenance attestation resolves to the same repository, commit, workflow, and digest.
9. SBOM attestation is present when required.
10. Deployment profile exists at the source commit.
11. Deployment profile digest matches the request.
12. Target environment is allowed for the project.
13. Idempotency key is valid and has not completed under different parameters.
14. No active environment deployment lock conflicts.
15. Required human approval has been satisfied.

Any unresolved field becomes `UNKNOWN` and blocks production.

## 9. State and receipt model

### 9.1 Deployment state machine

```text
REQUESTED
  -> VALIDATING
  -> BLOCKED | PLANNED
  -> PREFLIGHT
  -> BACKING_UP
  -> MIGRATING
  -> DEPLOYING
  -> VERIFYING
  -> SUCCEEDED

Any mutable phase may transition to:
  -> ROLLING_BACK
  -> ROLLED_BACK | FAILED
```

Allowed terminal statuses:

```yaml
terminal_statuses:
  - SUCCEEDED
  - ROLLED_BACK
  - BLOCKED
  - FAILED
  - UNKNOWN
```

### 9.2 Idempotency

The canonical idempotency key is a digest over:

```text
source repository
source commit SHA
image digest
deployment profile digest
target environment
platform contract major version
```

Rules:

- An identical completed request returns the existing receipt.
- An identical failed request may be retried with a new attempt number.
- A changed parameter must produce a new idempotency key.
- `force_reconcile` is a separate approved operation and never mutates the original receipt.

### 9.3 Receipts

The platform must emit:

- `deployment-plan.json`
- `deployment-receipt.json`
- `migration-receipt.json` when applicable
- `backup-receipt.json` when applicable
- `rollback-receipt.json` when applicable
- `host-conformance.json`
- `evidence.jsonl`
- redacted command logs

Every receipt includes:

```yaml
receipt_base:
  schema: versioned schema identifier
  receipt_id: deterministic or UUIDv7 identifier
  request_id: source deployment request
  project: canonical project identifier
  environment: target environment
  source_repository: owner/name
  source_commit_sha: exact SHA
  image_ref: registry image name
  image_digest: immutable digest
  profile_digest: immutable profile digest
  platform_commit_sha: deployment implementation SHA
  runner_identity: runner name and group
  started_at: RFC3339 timestamp
  completed_at: RFC3339 timestamp
  status: canonical status
  evidence_digest: digest over evidence records
  logs_digest: digest over redacted logs
  previous_release_id: prior active release
  findings: bounded structured findings
  unknowns: bounded unresolved facts
```

Receipts are immutable after publication. Corrections are new superseding receipts.

## 10. Target repository tree

```text
l9-deployment-platform/
├── README.md
├── ARCHITECTURE.md
├── SPECIFICATION.md
├── SECURITY.md
├── CONTRIBUTING.md
├── RUNBOOK.md
├── CHANGELOG.md
├── pyproject.toml
├── uv.lock
├── Makefile
├── .python-version
├── .editorconfig
├── .gitignore
├── .pre-commit-config.yaml
│
├── .l9/
│   ├── repo-spec.yaml
│   ├── architecture.yaml
│   ├── ownership.yaml
│   ├── compatibility.yaml
│   ├── release-policy.yaml
│   ├── tool-stack.yaml
│   └── integration-contracts/
│       ├── github-org.contract.yaml
│       ├── ci-core.contract.yaml
│       ├── ci-sdk.contract.yaml
│       ├── assurance.contract.yaml
│       ├── repo-template.contract.yaml
│       ├── consumer.contract.yaml
│       ├── ghcr.contract.yaml
│       ├── infisical.contract.yaml
│       └── hetzner.contract.yaml
│
├── .github/
│   ├── CODEOWNERS
│   ├── dependabot.yml
│   ├── pull_request_template.md
│   └── workflows/
│       ├── validate.yml
│       ├── provision-plan.yml
│       ├── provision-apply.yml
│       ├── configure-hosts.yml
│       ├── deploy-dispatch.yml
│       ├── deploy-manual.yml
│       ├── promote.yml
│       ├── rollback.yml
│       ├── drift-detect.yml
│       ├── fleet-conformance.yml
│       ├── backup-verify.yml
│       ├── runner-maintenance.yml
│       └── release.yml
│
├── schemas/
│   └── v1/
│       ├── deployment-profile.schema.json
│       ├── server-profile.schema.json
│       ├── fleet-inventory.schema.json
│       ├── deployment-request.schema.json
│       ├── release-evidence-reference.schema.json
│       ├── deployment-plan.schema.json
│       ├── deployment-receipt.schema.json
│       ├── rollback-receipt.schema.json
│       ├── backup-receipt.schema.json
│       ├── migration-receipt.schema.json
│       ├── health-probe.schema.json
│       ├── host-conformance.schema.json
│       ├── infrastructure-plan.schema.json
│       ├── infrastructure-receipt.schema.json
│       └── evidence-record.schema.json
│
├── src/
│   └── l9_deploy/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── canonical.py
│       ├── errors.py
│       ├── logging.py
│       ├── redaction.py
│       ├── subprocesses.py
│       ├── contracts/
│       │   ├── loader.py
│       │   ├── validator.py
│       │   ├── compatibility.py
│       │   └── models.py
│       ├── requests/
│       │   ├── parser.py
│       │   ├── verifier.py
│       │   ├── idempotency.py
│       │   └── allowlist.py
│       ├── planning/
│       │   ├── planner.py
│       │   ├── topology.py
│       │   ├── migrations.py
│       │   ├── backups.py
│       │   └── rollback.py
│       ├── execution/
│       │   ├── engine.py
│       │   ├── locks.py
│       │   ├── compose.py
│       │   ├── images.py
│       │   ├── migrations.py
│       │   ├── backups.py
│       │   ├── health.py
│       │   ├── promotion.py
│       │   └── rollback.py
│       ├── evidence/
│       │   ├── records.py
│       │   ├── receipts.py
│       │   ├── digests.py
│       │   └── publisher.py
│       ├── inventory/
│       │   ├── loader.py
│       │   ├── resolver.py
│       │   └── generator.py
│       └── integrations/
│           ├── github.py
│           ├── ghcr.py
│           ├── infisical.py
│           ├── opentofu.py
│           ├── ansible.py
│           └── hetzner.py
│
├── infrastructure/
│   └── opentofu/
│       ├── versions.tf
│       ├── providers.tf
│       ├── backend.example.hcl
│       ├── modules/
│       │   ├── network/
│       │   ├── firewall/
│       │   ├── server/
│       │   ├── volume/
│       │   ├── placement-group/
│       │   ├── load-balancer/
│       │   └── dns-record/
│       └── environments/
│           ├── management/
│           ├── staging/
│           └── production/
│
├── ansible/
│   ├── ansible.cfg
│   ├── requirements.yml
│   ├── inventories/
│   │   ├── generated/
│   │   └── group_vars/
│   ├── playbooks/
│   │   ├── bootstrap.yml
│   │   ├── harden.yml
│   │   ├── configure-runner.yml
│   │   ├── configure-runtime.yml
│   │   ├── configure-backups.yml
│   │   ├── verify.yml
│   │   └── decommission.yml
│   └── roles/
│       ├── base/
│       ├── users/
│       ├── sshd/
│       ├── host_firewall/
│       ├── unattended_upgrades/
│       ├── docker/
│       ├── caddy/
│       ├── github_runner/
│       ├── backup_agent/
│       ├── journald/
│       ├── time_sync/
│       └── conformance/
│
├── deployment/
│   ├── profiles/
│   │   ├── container-service.yaml
│   │   ├── worker-service.yaml
│   │   ├── stateful-container.yaml
│   │   ├── scheduled-job.yaml
│   │   └── external-platform.yaml
│   ├── policies/
│   │   ├── production.yaml
│   │   ├── staging.yaml
│   │   ├── compose-policy.yaml
│   │   ├── migration-policy.yaml
│   │   └── rollback-policy.yaml
│   ├── templates/
│   │   ├── compose.yaml.j2
│   │   ├── caddy-site.caddy.j2
│   │   ├── systemd-unit.service.j2
│   │   └── env-file.j2
│   └── probes/
│       ├── http.yaml
│       ├── tcp.yaml
│       ├── command.yaml
│       └── database.yaml
│
├── fleet/
│   ├── registry.yaml
│   ├── projects/
│   │   └── README.md
│   ├── environments/
│   │   ├── management.yaml
│   │   ├── staging.yaml
│   │   └── production.yaml
│   └── desired-state/
│       └── README.md
│
├── templates/
│   └── consumer/
│       ├── common/
│       │   ├── deployment.yaml
│       │   └── release.yml
│       ├── container-service/
│       ├── worker-service/
│       ├── stateful-container/
│       └── scheduled-job/
│
├── scripts/
│   ├── bootstrap-state.sh
│   ├── bootstrap-runner.sh
│   ├── generate-inventory.py
│   ├── validate-contracts.py
│   ├── verify-attestation.sh
│   ├── rotate-runner.sh
│   ├── break-glass-access.sh
│   └── package-adoption-kit.py
│
├── tests/
│   ├── contracts/
│   ├── unit/
│   ├── integration/
│   ├── infrastructure/
│   ├── ansible/
│   ├── deployment/
│   ├── security/
│   ├── fixtures/
│   └── adversarial/
│
└── docs/
    ├── architecture/
    │   ├── control-planes.md
    │   ├── trust-boundaries.md
    │   ├── networking.md
    │   ├── state-management.md
    │   ├── deployment-engine.md
    │   └── evidence-model.md
    ├── operations/
    │   ├── provisioning.md
    │   ├── deployments.md
    │   ├── rollbacks.md
    │   ├── backups.md
    │   ├── restore-tests.md
    │   ├── runner-recovery.md
    │   └── incident-response.md
    ├── adoption/
    │   ├── consumer-contract.md
    │   ├── profiles.md
    │   ├── seo-bot-reference.md
    │   └── migration-guide.md
    └── adr/
        ├── 0001-private-deployment-control-plane.md
        ├── 0002-dedicated-runner-private-network.md
        ├── 0003-build-once-promote-by-digest.md
        ├── 0004-opentofu-plus-ansible-boundary.md
        ├── 0005-public-to-private-deployment-broker.md
        ├── 0006-deployment-receipts.md
        ├── 0007-no-production-git-checkouts.md
        ├── 0008-host-firewall-for-private-network.md
        ├── 0009-infisical-oidc-for-workflows.md
        └── 0010-observability-out-of-scope.md
```

## 11. Command-line interface

Canonical executable:

```text
l9-deploy
```

Required commands:

```text
l9-deploy contract validate
l9-deploy request validate
l9-deploy request inspect
l9-deploy plan
l9-deploy deploy
l9-deploy promote
l9-deploy rollback
l9-deploy status
l9-deploy receipt verify
l9-deploy inventory generate
l9-deploy inventory validate
l9-deploy host verify
l9-deploy fleet verify
l9-deploy infra plan
l9-deploy infra apply
l9-deploy config check
l9-deploy config apply
l9-deploy backup create
l9-deploy backup verify
l9-deploy restore test
l9-deploy adoption render
```

All commands must support:

```text
--json
--output <path>
--non-interactive
--timeout <seconds>
--request-id <id>
--log-level <level>
```

Mutating commands additionally require:

```text
--environment <name>
--expected-plan-digest <digest>
--approval-receipt <path-or-reference>
```

No command may silently default to production.

## 12. Deployment profiles

### 12.1 Supported version-1 profiles

#### `container-service`

Long-running HTTP or TCP service with no locally managed database requirement.

#### `worker-service`

Long-running worker with no public ingress.

#### `stateful-container`

Long-running application with persistent volumes, database dependencies, migrations, backups, and stricter rollback gates.

#### `scheduled-job`

Bounded container execution triggered by schedule or dispatch, with no permanent application process.

#### `external-platform`

Records deployment integration for systems operated by another authoritative platform. It may validate and dispatch but does not pretend to own the external platform runtime.

### 12.2 Example consumer deployment profile

```yaml
schema: l9.deployment-profile/v1

project:
  id: seo-bot
  repository: Quantum-L9/SEO-Bot
  owner_team: platform
  runtime_profile: stateful-container

artifact:
  registry: ghcr.io
  image: ghcr.io/quantum-l9/seo-bot
  require_digest: true
  require_provenance_attestation: true
  require_sbom_attestation: true

runtime:
  architecture: linux/amd64
  container_port: 3100
  user: non_root
  read_only_root_filesystem: false
  stop_grace_seconds: 30

health:
  startup:
    type: http
    path: /health
    expected_status: 200
    timeout_seconds: 120
    interval_seconds: 5
  post_deploy:
    type: http
    path: /health
    expected_status: 200
    attempts: 12
    interval_seconds: 5

release:
  strategy: rolling-single-host
  retain_successful_releases: 5
  automatic_rollback: true
  production_approval_required: true

migrations:
  enabled: true
  command: ["npm", "run", "migrate"]
  mode: pre_start
  use_release_image: true
  backup_required: true
  timeout_seconds: 300

storage:
  persistent_volumes:
    - name: reports
      mount_path: /app/data/reports
      backup_policy: daily

services:
  postgres:
    mode: managed_on_fleet
    required: true
  redis:
    mode: managed_on_fleet
    required: true

secrets:
  authority: infisical
  runtime_mode: runtime_fetch
  project_slug: seo-bot
  environment_mapping:
    staging: staging
    production: prod

network:
  public_ingress:
    enabled: true
    hostnames:
      - seo.example.invalid
    tls: automatic
  private_dependencies_only: true

policy:
  allowed_source_refs:
    staging:
      - refs/heads/main
    production:
      - refs/tags/v*
  require_clean_ci_gate: true
  require_profile_digest_match: true
```

Example hostnames and domains are placeholders in the specification only and must not be copied into production configuration.

## 13. Infrastructure provisioning

### 13.1 OpenTofu ownership

OpenTofu owns cloud resources:

- Hetzner networks and subnets.
- Hetzner cloud firewalls.
- Servers.
- Volumes.
- Placement groups.
- Load balancers when required.
- Server labels.
- Network attachment.
- DNS records only when the selected provider is explicitly configured.

OpenTofu does not:

- Install Docker.
- Configure users beyond minimal bootstrap.
- Render application configuration.
- Deploy application containers.
- Run database migrations.

### 13.2 State backend

Requirements:

- Remote state only.
- State locking required.
- Versioning required.
- Encryption at rest required.
- Separate state key per environment.
- Separate credentials from application secrets.
- State access limited to provisioning workflows.
- State backups and recovery procedure documented.

Preferred initial backend:

- Private Hetzner S3-compatible Object Storage bucket.
- Bucket versioning enabled.
- OpenTofu S3 backend.
- Native S3 lockfile enabled only after a compatibility proof confirms the endpoint supports the required conditional-write semantics.

Until that compatibility proof passes, production apply is blocked. An approved backend with proven locking must be used instead of pretending locking exists.

State key convention:

```text
l9-deployment-platform/<environment>/opentofu.tfstate
```

### 13.3 Planning and apply separation

`provision-plan.yml`:

- Runs on GitHub-hosted runner when no private network is required.
- Authenticates to Infisical with GitHub OIDC.
- Fetches temporary Hetzner and state credentials.
- Runs format, validate, lint, and plan.
- Uploads a binary plan and JSON plan summary.
- Produces plan digest and infrastructure-plan receipt.

`provision-apply.yml`:

- Runs only after protected-environment approval.
- Requires exact plan digest.
- Rejects stale plans when the base commit or state serial changed.
- Uses concurrency lock per environment.
- Applies the exact reviewed plan.
- Generates inventory output and infrastructure receipt.
- Triggers Ansible conformance after successful apply.

### 13.4 Destructive changes

Replacement or deletion of production resources requires:

- Explicit destructive-change finding.
- Backup proof when stateful data may be affected.
- Named approval.
- Expected resource list.
- Rollback or rebuild plan.
- No `-auto-approve` outside the protected apply workflow.

## 14. Host configuration

### 14.1 Ansible ownership

Ansible owns operating-system desired state:

- Users and groups.
- SSH configuration.
- Host firewall.
- Docker Engine and Compose plugin.
- Reverse proxy.
- Backup client.
- Runner service.
- Directories and permissions.
- Log rotation and journald settings.
- Automatic security updates.
- Time synchronization.
- Required kernel and sysctl settings.
- Host conformance checks.

### 14.2 Idempotency contract

Every role must pass:

1. Syntax validation.
2. ansible-lint.
3. Check-mode execution where supported.
4. First apply.
5. Second apply with zero unexpected changes.
6. Conformance verification.

Tasks that cannot be idempotent must:

- State why.
- Be isolated behind an explicit handler or command wrapper.
- Produce a deterministic changed condition.
- Have a regression test.

### 14.3 Inventory generation

OpenTofu outputs machine-readable inventory facts. The platform generates Ansible inventory from those outputs.

Inventory must not be hand-maintained separately from infrastructure state.

Required host facts:

```yaml
host:
  id: provider resource id
  name: canonical host name
  role: management | application | data | external
  environment: management | staging | production
  private_ip: address
  public_ip: address | null
  architecture: amd64 | arm64
  server_type: provider server type
  labels: key-value map
  allowed_projects: list
  ansible_groups: list
```

## 15. Dedicated runner specification

### 15.1 Runner isolation

The runner:

- Belongs to a dedicated runner group.
- Is accessible only to `l9-deployment-platform`.
- Is restricted to selected deployment workflows where GitHub plan capabilities allow.
- Never runs pull-request code from public repositories.
- Never checks out consumer source to execute arbitrary scripts.
- Uses only platform-controlled deployment commands and validated consumer metadata.
- Runs under a non-root service account.
- Uses controlled privilege escalation for approved operations.
- Has no application database or application workloads.

### 15.2 Runner updates

The runner must remain within GitHub's supported update window.

Required controls:

- Automatic runner updates enabled, or a scheduled update workflow.
- Daily version conformance check.
- Alert when runner version is outside policy.
- Monthly runner replacement rehearsal.
- Rebuild from OpenTofu and Ansible, not hand repair.

### 15.3 Runner filesystem

```text
/opt/l9-runner/          GitHub runner installation
/var/lib/l9-deploy/      transient deployment workspace
/var/log/l9-deploy/      redacted local logs with bounded retention
/etc/l9-deploy/          non-secret platform configuration
/run/l9-deploy/          temporary runtime files and locks
```

Secrets must not persist in the runner work directory after a job.

## 16. Secrets and identity

### 16.1 Authority

Infisical remains the secrets authority.

### 16.2 GitHub workflow authentication

GitHub Actions workflows authenticate to Infisical using OIDC and short-lived tokens.

Do not store long-lived Infisical client secrets in GitHub when OIDC is available.

Claims must bind at minimum:

- Organization.
- Repository.
- Workflow path.
- Environment.
- Ref or protected branch context.

### 16.3 Runtime authentication

Supported runtime secret modes:

#### `runtime_fetch`

The application or Infisical agent fetches secrets at runtime using a project-scoped machine identity.

#### `deploy_render`

The approved deployment workflow fetches secrets and writes a root-owned environment file with mode `0600`. The file content is never included in logs, receipts, diffs, or artifacts.

`runtime_fetch` is preferred for applications that already support it.

### 16.4 Secret classes

```yaml
secret_classes:
  infrastructure:
    - HCLOUD_TOKEN
    - state_backend_access_key
    - state_backend_secret_key
  github_broker:
    - github_app_private_key
  registry_pull:
    - GHCR_READ_TOKEN
  host_bootstrap:
    - bootstrap_ssh_private_key
  application_runtime:
    - project-specific secrets
```

Each class must use a different identity and least-privilege policy where practical.

## 17. OCI image and GHCR contract

### 17.1 Build once

A consumer repository builds the OCI image exactly once per release candidate.

The same digest moves through:

```text
build -> staging -> production -> rollback reference
```

Production promotion never rebuilds the image.

### 17.2 Required image metadata

```text
org.opencontainers.image.source
org.opencontainers.image.revision
org.opencontainers.image.version
org.opencontainers.image.created
org.opencontainers.image.title
```

### 17.3 Required release properties

- Exact digest.
- Source commit SHA.
- Repository association.
- Build provenance attestation.
- SBOM attestation.
- Vulnerability-scan result or referenced evidence.
- Non-root execution unless explicitly approved.
- Health-check definition for long-running services.

### 17.4 Pull credentials

Private image pull credentials must be read-only and stored in Infisical.

The platform must not use a developer's personal token. Use a dedicated machine credential with `read:packages` and only the repository or package access required.

## 18. Deployment execution

### 18.1 Host release layout

```text
/opt/l9/apps/<project>/
  releases/<release-id>/
    compose.yaml
    release.json
    profile.json
    env.reference
  current -> releases/<release-id>
  previous -> releases/<previous-release-id>

/var/lib/l9/<project>/
  persistent application data

/etc/l9/apps/<project>/
  root-owned runtime environment references
```

### 18.2 Deployment algorithm

1. Validate the deployment request.
2. Resolve registered project and target environment.
3. Verify CI evidence references.
4. Verify GHCR digest and attestations.
5. Load and validate deployment profile.
6. Resolve target hosts from fleet inventory.
7. Acquire GitHub concurrency lock.
8. Acquire host deployment lock.
9. Run host-conformance preflight.
10. Verify available disk, memory, Docker, network, and dependency health.
11. Create backup when required.
12. Render a new immutable release directory.
13. Pull the exact image digest.
14. Run migration preflight.
15. Execute migrations according to policy.
16. Start candidate release.
17. Run startup health probes.
18. Switch reverse proxy or service pointer.
19. Run post-deployment probes.
20. Mark the release current.
21. Emit deployment receipt.
22. Remove expired releases according to retention policy.
23. Release locks.

### 18.3 Compose policy

Consumer-provided Compose bundles are allowed only through the `compose-bundle` adapter and must be normalized with `docker compose config`.

The policy rejects by default:

- `build:` in production Compose.
- Mutable image tags without a digest.
- `privileged: true`.
- Host network mode.
- Docker socket mounts.
- Unbounded host filesystem mounts.
- Public database ports.
- Public Redis ports.
- Unapproved capabilities.
- Root user without exception.
- Missing restart policy for long-running services.
- Missing health checks where required.
- Inline secrets.

## 19. Database migrations

Supported modes:

```yaml
migration_modes:
  none: no migration
  pre_start: run before candidate application start
  post_start: run after candidate is healthy
  expand_contract: staged backward-compatible migration sequence
  manual: deployment blocks until external migration receipt is supplied
```

Rules:

- Migration uses the same image digest as the release unless an explicit migration artifact is approved.
- State-changing production migration requires a current backup receipt.
- Migration command has a hard timeout.
- Migration output is redacted.
- Migration result is a separate receipt.
- Destructive or irreversible migration requires `manual` or `expand_contract` policy.
- Automatic container rollback does not imply automatic schema rollback.
- Unknown schema compatibility blocks deployment.

## 20. Backup and recovery

### 20.1 Backup ownership

The deployment platform orchestrates deployment-coupled backups and restore tests.

It does not become the central observability system.

### 20.2 Backup destinations

Preferred:

- Private Hetzner Object Storage bucket.
- S3-compatible backup tooling such as Restic.
- Separate bucket or prefix from OpenTofu state.
- Versioning and retention policies.

### 20.3 Backup rules

- Database-native backup before risky migration.
- Volume backup for declared persistent data.
- Backup receipt includes object digest and restore metadata.
- Production backup is not considered valid until periodic restore testing succeeds.
- Quarterly automated restore test for each critical data class.
- Backup credentials cannot read OpenTofu state unless explicitly required.

## 21. Health and readiness

Health checks are contracts, not prose.

Supported probes:

- HTTP status and bounded response assertions.
- TCP connection.
- Bounded command execution.
- PostgreSQL query.
- Redis ping.
- Container health state.
- Reverse-proxy route verification.

Probe results include:

```yaml
probe_result:
  probe_id: string
  type: http | tcp | command | postgres | redis | container
  target: redacted target identifier
  started_at: timestamp
  duration_ms: integer
  status: PASS | FAIL | BLOCKED | UNKNOWN
  expected: structured expectation
  actual: redacted structured result
  attempts: integer
  evidence_digest: digest
```

A deployment cannot be marked `SUCCEEDED` from container-start success alone.

## 22. Rollback

### 22.1 Automatic rollback triggers

- Candidate container fails to start.
- Startup probe fails within policy timeout.
- Reverse-proxy switch fails.
- Post-deployment probe fails.
- Required dependency becomes unavailable during deployment.
- Receipt persistence fails before success is committed.

### 22.2 Rollback algorithm

1. Freeze new deployments for the environment.
2. Record rollback initiation.
3. Stop or isolate the failed candidate.
4. Restore previous release pointer.
5. Restart previous release if necessary.
6. Restore proxy configuration.
7. Run previous-release health probes.
8. Record data migration compatibility state.
9. Emit rollback receipt.
10. Preserve failed release files for forensic retention.

### 22.3 Rollback limits

Automatic rollback must stop and report `FAILED` or `UNKNOWN` when:

- Previous release is unavailable.
- Database schema is not backward compatible.
- Backup restore is required but not authorized.
- Previous release fails health checks.
- Required facts are unresolved.

## 23. Drift and conformance

### 23.1 Infrastructure drift

Scheduled workflow:

```text
drift-detect.yml
```

It runs OpenTofu plan in read-only mode and emits:

- No-change receipt.
- Drift findings.
- Proposed resource changes.
- Severity based on affected resource class.

It never auto-applies production drift corrections.

### 23.2 Host drift

`fleet-conformance.yml` runs Ansible check mode and explicit host probes.

Classification:

```yaml
conformance:
  PASS: desired state satisfied
  PASS_WITH_FINDINGS: non-blocking drift
  FAIL: required host control absent or incorrect
  BLOCKED: host unreachable or approval required
  UNKNOWN: insufficient evidence
```

### 23.3 Application drift

The platform compares:

- Desired image digest.
- Running image digest.
- Release directory pointer.
- Compose digest.
- Environment-reference digest.
- Health state.

A running mutable tag is a failure even when the resolved digest happens to match.

## 24. Evidence and observability boundary

The platform emits structured signals:

- Deployment requested.
- Deployment validated.
- Deployment blocked.
- Deployment started.
- Backup completed.
- Migration completed.
- Candidate started.
- Health verification completed.
- Deployment succeeded.
- Rollback started.
- Rollback completed.
- Host drift detected.
- Infrastructure drift detected.

It publishes these through a stable event and receipt interface.

It does not own:

- Long-term log aggregation.
- Metrics database.
- Trace backend.
- Alert-routing product.
- Fleet dashboard product.
- Organization-wide observability SDK.

The future centralized observability capability consumes deployment events. It is not implemented inside this repository.

## 25. GitHub Actions workflows

### 25.1 `validate.yml`

Triggers:

- Pull request.
- Push to main.

Runs only on GitHub-hosted runners.

Gates:

- Python lock consistency.
- Formatting.
- Lint.
- Typecheck.
- Unit tests.
- Contract schema tests.
- OpenTofu format and validate.
- Ansible syntax and lint.
- Security scans through `l9-ci-core`.
- Manifest and ownership checks.

### 25.2 `provision-plan.yml`

- Manual or pull-request-triggered for infrastructure changes.
- GitHub-hosted runner when network access is not required.
- OIDC to Infisical.
- Produces exact plan digest.
- No apply.

### 25.3 `provision-apply.yml`

- Protected manual dispatch only.
- Exact plan digest required.
- Environment approval required.
- Production concurrency is serialized.
- Generates infrastructure receipt.

### 25.4 `deploy-dispatch.yml`

- Triggered only by `repository_dispatch` event type `l9.release.requested.v1`.
- Workflow file on default branch is authoritative.
- Uses dedicated runner after initial payload validation on a GitHub-hosted gate job.
- Production environment approval precedes secrets and runner execution.

Recommended job split:

```text
validate-request       GitHub-hosted
verify-release         GitHub-hosted
await-environment      protected environment
plan-deployment        GitHub-hosted or self-hosted, no mutation
execute-deployment     dedicated self-hosted runner
publish-receipt        GitHub-hosted where possible
```

This split minimizes untrusted data and secret exposure on the self-hosted runner.

### 25.5 `deploy-manual.yml`

Break-glass and controlled manual deployment.

Required inputs:

- Registered project.
- Environment.
- Exact image digest.
- Source commit.
- Reason.
- Incident or change ticket reference.
- Expected previous release.

Manual deployment cannot bypass artifact verification.

### 25.6 `rollback.yml`

- Protected manual dispatch or automatic workflow call from failed deployment.
- Requires release identifier.
- Produces rollback receipt.
- Does not delete evidence from failed release.

## 26. Integration contract: Quantum-L9/.github

### 26.1 Files to add

```text
Quantum-L9/.github/
├── deployment-interface-registry.yml
├── workflow-templates/
│   ├── l9-container-release.yml
│   ├── l9-container-release.properties.json
│   ├── l9-deployment-request.yml
│   └── l9-deployment-request.properties.json
└── .github/ISSUE_TEMPLATE/
    ├── deployment-onboarding.yml
    └── deployment-incident.yml
```

### 26.2 Files to modify

- `profile/README.md`
- `.github/CODEOWNERS`
- `CONTRIBUTING.md`
- `PULL_REQUEST_TEMPLATE.md`

### 26.3 Registry requirements

`deployment-interface-registry.yml` must describe:

- Public contract versions.
- Event types.
- Required payload schema.
- Supported consumer profiles.
- `l9-ci-core` release-request workflow reference.
- Private implementation repository identity without exposing secrets or topology.
- Compatibility policy.
- Deprecation schedule.
- Current audited implementation commit or release tag.

### 26.4 CODEOWNERS

Deployment interface files are blast-radius paths and require platform plus owner review.

### 26.5 No implementation leakage

`.github` must not contain:

- Hetzner token handling.
- SSH implementation.
- OpenTofu modules.
- Ansible roles.
- Host inventory.
- Production hostnames or private IPs.
- Runtime secrets.

## 27. Integration contract: l9-ci-core

### 27.1 Required reusable kernels

```text
.github/workflows/container-release.yml
.github/workflows/request-deployment.yml
```

### 27.2 `container-release.yml` outputs

```yaml
outputs:
  image_ref: ghcr image name
  image_digest: exact sha256 digest
  source_commit_sha: exact source commit
  provenance_attestation_ref: attestation reference
  sbom_attestation_ref: SBOM reference
  release_receipt_path: generated receipt path
  release_receipt_digest: receipt digest
  gate_status: canonical gate status
```

### 27.3 `request-deployment.yml` responsibilities

- Validate caller-provided deployment profile path.
- Require exact container-release outputs.
- Mint short-lived GitHub App token.
- Create bounded repository dispatch event.
- Publish request ID in workflow summary.
- Never access production network.
- Never invoke SSH, OpenTofu apply, or Ansible apply.

### 27.4 Prohibited coupling

`l9-ci-core` may not:

- Copy deployment schemas.
- Reimplement deployment request validation beyond caller-side structural validation.
- Decide host placement.
- Generate deployment receipts.
- Report deployment success from dispatch success.

A `204` dispatch response means only that the request was accepted by GitHub, not that deployment succeeded.

## 28. Integration contract: l9-ci-sdk

The release request may include:

```yaml
ci_evidence_reference:
  bundle_schema: SDK-owned schema identifier
  bundle_digest: sha256 digest
  SDK_version: semantic version
  gate_outcome: PASS | FAIL | BLOCKED | UNKNOWN
  artifact_reference: immutable artifact location
```

The deployment platform verifies the reference and compatibility metadata.

It does not:

- Parse raw Semgrep, test, or security reports.
- Reclassify CI findings.
- Change the SDK gate outcome.
- Copy SDK schemas.

## 29. Integration contract: l9-assurance

Initial integration:

- Use `l9-security-testkit` for relevant security controls when compatible.
- Use `l9-agent-security-testkit` only for agent-facing interfaces if present.
- Record exact package versions and lock them.
- Treat unavailable or undocumented package interfaces as `UNKNOWN` rather than inventing imports.

Future integration may add deployment-specific assurance packages, but the deployment runtime remains in this repository.

## 30. Integration contract: l9-repo-template

Canonical source of consumer templates:

```text
l9-deployment-platform/templates/consumer/
```

Generated projection target:

```text
l9-repo-template/.l9/generated/deployment/
```

Required lock file in `l9-repo-template`:

```yaml
schema: l9.generated-projection-lock/v1
source_repository: Quantum-L9/l9-deployment-platform
source_ref: v1
source_commit_sha: exact SHA
template_digest: sha256 digest
generated_at: timestamp
files: sorted file list with digests
```

The template repo must fail validation when generated files drift from the lock.

## 31. Consumer repository adoption contract

### 31.1 Minimum files

```text
consumer-repo/
├── .l9/deployment.yaml
├── .github/workflows/release.yml
├── Dockerfile
└── application-specific source and tests
```

Optional:

```text
deploy/compose.yaml
```

only for the validated compose-bundle adapter.

### 31.2 Thin caller workflow

```yaml
name: Release and Request Deployment

on:
  push:
    tags:
      - "v*"
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [staging]
        required: true

permissions:
  contents: read
  packages: write
  id-token: write
  attestations: write

jobs:
  release:
    uses: Quantum-L9/l9-ci-core/.github/workflows/container-release.yml@v1
    with:
      deployment-profile: .l9/deployment.yaml
    secrets: inherit

  request:
    needs: release
    uses: Quantum-L9/l9-ci-core/.github/workflows/request-deployment.yml@v1
    with:
      environment: ${{ inputs.environment || 'production' }}
      deployment-profile: .l9/deployment.yaml
      image-ref: ${{ needs.release.outputs.image_ref }}
      image-digest: ${{ needs.release.outputs.image_digest }}
      release-receipt-digest: ${{ needs.release.outputs.release_receipt_digest }}
    secrets: inherit
```

The production-default expression shown above must be replaced with explicit event-aware policy in implementation. A manual dispatch must never silently default to production.

### 31.3 Consumer repository prohibitions

- No direct SSH deployment action.
- No production private key.
- No Hetzner token.
- No `git pull` deployment.
- No server-side build.
- No `latest` deployment.
- No duplicate Ansible or OpenTofu logic.
- No copied rollback script.

## 32. Security model

### 32.1 Threats

- Malicious pull request attempts runner execution.
- Compromised consumer repository dispatches unauthorized artifact.
- Mutable image tag changes after approval.
- Fabricated release receipt.
- Stale or replayed deployment request.
- Secrets printed in logs.
- Runner persistence after compromise.
- Private-network lateral movement.
- OpenTofu state disclosure.
- Migration destroys incompatible data.
- Rollback points to unavailable or unhealthy image.

### 32.2 Required mitigations

- Private deployment repository.
- Runner-group repository and workflow restrictions.
- GitHub-hosted validation before self-hosted execution.
- Exact image digest.
- Provenance attestation verification.
- Profile digest verification.
- Request idempotency and replay detection.
- Protected environments and approvals.
- Infisical OIDC for workflow secrets.
- Dedicated identities by secret class.
- Redaction at capture and persistence boundaries.
- Host-level firewall on private interfaces.
- Immutable receipts.
- Backup and migration compatibility gates.
- Runner rebuild procedure.

### 32.3 Log redaction

Redaction must cover:

- Environment variables.
- CLI arguments.
- URLs containing credentials.
- Docker login output.
- Ansible diffs containing secrets.
- OpenTofu state values.
- HTTP authorization headers.
- Infisical access tokens.
- GitHub tokens.
- SSH private material.

A log labeled redacted must be passed through the canonical redactor before persistence.

## 33. Validation strategy

### 33.1 Contract tests

- Every example validates against its schema.
- Invalid status values fail.
- Unknown major versions fail.
- Additional properties fail unless explicitly allowed.
- Canonical serialization is deterministic.
- Digests are stable across runs.

### 33.2 Infrastructure tests

- OpenTofu format and validate.
- Provider lockfile committed.
- Module input/output contract tests.
- Plan fixture tests.
- Destructive-plan classification tests.
- State-locking compatibility proof.

### 33.3 Ansible tests

- Syntax check.
- ansible-lint.
- Molecule or equivalent role tests where practical.
- Check mode.
- First apply.
- Second apply with no unexpected change.
- Host firewall assertions.
- SSH hardening assertions.

### 33.4 Deployment-engine tests

- Valid request success path.
- Invalid schema rejection.
- Unauthorized repository rejection.
- Digest mismatch rejection.
- Attestation mismatch rejection.
- Replay handling.
- Concurrency collision.
- Backup failure.
- Migration failure.
- Health failure.
- Successful rollback.
- Rollback failure.
- Receipt-persistence failure.
- Secret redaction.
- Timeout and process-tree termination.

### 33.5 Adversarial tests

- Public PR cannot schedule self-hosted runner.
- Modified workflow path cannot access runner group.
- Consumer cannot select arbitrary host.
- Compose bundle cannot mount Docker socket.
- Mutable tag is rejected.
- Payload with unknown fields is rejected.
- Stale plan is rejected.
- Previous release digest mismatch blocks rollback.

## 34. Branch protection and release discipline

Required repository rules:

- Default branch `main`.
- Pull request required.
- Required CODEOWNERS review.
- Two reviews for infrastructure, workflow, schema, runner, and security paths.
- Required signed commits where organization policy supports it.
- Required status checks.
- No force push to main.
- No branch deletion for protected release branches.
- Immutable semantic-version tags.
- Moving major compatibility tag only when explicitly governed.

Recommended versioning:

```text
v1.0.0 immutable implementation release
v1     moving compatible interface tag
v2     breaking contract generation
```

Consumer callers use `@v1`. Internal production receipts record the exact implementation commit SHA in addition to the compatibility tag.

## 35. Implementation phases

### Phase 0: Contract lock

Create:

- Repository skeleton.
- Repo spec and ownership files.
- Schemas.
- Status model.
- Request and receipt contracts.
- Architecture ADRs.
- No production mutation.

Exit gate:

- All contracts validate.
- Boundaries approved.
- `.github` integration PR drafted.

### Phase 1: Management infrastructure

Build:

- OpenTofu network, firewall, and management-server modules.
- Remote-state backend proof.
- Minimal cloud-init.
- Ansible base, SSH, firewall, Docker, and runner roles.

Proof:

- Create `l9-deploy-01`.
- Destroy and recreate it from code.
- Runner re-registers without manual configuration drift.

### Phase 2: Deployment engine core

Build:

- Request validation.
- Inventory resolution.
- Image verification.
- Release directory model.
- Health probes.
- Receipts.
- Idempotency and locks.

Proof:

- Deploy a fixture service to staging.
- Repeat identical request without duplicate mutation.
- Force health failure and prove rollback.

### Phase 3: Public release bridge

Change:

- `.github` registry and templates.
- `l9-ci-core` container-release and request-deployment kernels.
- GitHub App broker.
- Infisical OIDC identities.

Proof:

- Public fixture repository builds on GitHub-hosted runner.
- Private platform receives validated request.
- Public repository never accesses self-hosted runner.

### Phase 4: Stateful deployment

Build:

- Backup integration.
- Migration modes.
- PostgreSQL and Redis dependency probes.
- Restore-test workflow.

Proof:

- Stateful fixture deployment.
- Migration failure rollback.
- Restore proof from generated backup.

### Phase 5: SEO-Bot reference adoption

Migrate SEO-Bot:

- Canonical deployment profile.
- npm-only image build.
- GHCR publication.
- Staging deployment.
- Database migration gate.
- Redis and PostgreSQL probes.
- Production promotion.
- Rollback rehearsal.

Do not claim production readiness until target-host evidence passes.

### Phase 6: Fleet rollout

- Render adoption kits.
- Populate `l9-repo-template` projection.
- Migrate projects by runtime profile.
- Add scheduled drift and backup verification.
- Publish fleet conformance summary.

## 36. Required ADRs

1. Private deployment control plane.
2. Dedicated runner plus Hetzner private networking.
3. Build once and promote by digest.
4. OpenTofu owns cloud resources; Ansible owns host state.
5. Public-to-private GitHub App broker.
6. Deployment receipts are immutable evidence.
7. Production servers contain no Git checkout.
8. Host firewall governs private-network segmentation.
9. GitHub OIDC authenticates workflows to Infisical.
10. Centralized observability is out of scope.
11. Consumer deployment profiles are declarative and bounded.
12. Database rollback is separate from container rollback.

## 37. Acceptance criteria

### Repository

- Private repository created.
- Complete file tree implemented.
- No stubs or pass-only scripts.
- Manifest and ownership complete.
- CI and security gates green.

### Provisioning

- Remote state and locking proven.
- Management server reproducibly created.
- Destroy/recreate test passes.
- Production plans require approval and exact digest.

### Runner

- Runner isolated to private deployment repository.
- Workflow allowlist configured where supported.
- Public PR cannot execute on runner.
- Runner rebuild documented and tested.

### Deployment

- Exact digest only.
- Attestation verification required.
- Idempotent request handling.
- Environment concurrency enforced.
- Health failure triggers rollback.
- Receipts verify cryptographically by digest.

### Stateful operations

- Backup before risky migration.
- Migration receipt emitted.
- Restore test passes.
- Schema incompatibility blocks automatic rollback.

### Integration

- `.github` deployment registry published.
- `l9-ci-core` release and request interfaces registered.
- `l9-ci-sdk` boundary preserved.
- `l9-assurance` reused without duplication.
- `l9-repo-template` projection generated and locked.
- SEO-Bot deployed as reference consumer.

## 38. Stop conditions

Provisioning or deployment must halt when:

- Contract schema is unknown or incompatible.
- Required evidence is missing.
- CI gate is not `PASS`.
- Source commit cannot be verified.
- Image digest or attestation does not match.
- Deployment profile digest differs.
- Target environment is not registered.
- State locking is unavailable.
- OpenTofu plan is stale.
- Host conformance fails.
- Backup is required but unsuccessful.
- Migration compatibility is unknown.
- Production approval is absent.
- Previous release cannot be verified for rollback.
- Secrets cannot be fetched without exposing them.
- Receipt persistence cannot be guaranteed.

## 39. Convergence target

```yaml
convergence:
  repository_identity: locked
  provisioning_authority: l9-deployment-platform
  deployment_authority: l9-deployment-platform
  CI_authority: l9-ci-core
  CI_evidence_authority: l9-ci-sdk
  assurance_authority: l9-assurance
  org_registry_authority: Quantum-L9/.github
  consumer_template_projection: l9-repo-template
  image_registry: GHCR
  secrets_authority: Infisical
  cloud_provider_v1: Hetzner Cloud
  deployment_connectivity: dedicated runner plus private network
  centralized_observability: external shared capability
  production_git_checkouts: forbidden
  mutable_image_deployment: forbidden
  server_side_builds: forbidden
  deployment_receipts: required
  automatic_rollback: required where safe
  database_rollback: never assumed
```

## 40. Highest-leverage first build

The first implementation should not begin with every runtime profile.

Build this vertical slice:

```text
private deployment repository
  -> management network
  -> l9-deploy-01 runner
  -> container-service fixture
  -> GHCR digest verification
  -> one staging host
  -> HTTP health check
  -> automatic rollback
  -> immutable receipt
```

Once that path is proven, add stateful deployment and migrate SEO-Bot. This proves the control plane before databases, analytics, and complex Compose topology widen the blast radius.

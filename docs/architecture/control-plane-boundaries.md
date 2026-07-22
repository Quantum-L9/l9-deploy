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
# Control-plane boundaries

The platform owns server provisioning, host reconciliation, approved release deployment, health
verification, rollback, and deployment receipts. It consumes CI evidence but does not normalize
scanner output or reconstruct CI findings. Consumer repositories own application code, Dockerfiles,
health behavior, migration commands, and `.l9/deployment.yaml`. The organization `.github`
repository owns public interface discovery and starter projections. `l9-ci-core` owns public release
orchestration and the bounded broker call. `l9-ci-sdk` owns canonical CI evidence.

The deployment repository is private. Its self-hosted runner is repository-scoped and never executes
consumer pull-request code. A public consumer can only submit a versioned request containing a full
source SHA, exact image digest, exact profile digest, and evidence references. The private receiver
revalidates every field against its fleet registry before mutation.

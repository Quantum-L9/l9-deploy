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
# Evidence model

CI evidence and deployment evidence have separate authorities. The deployment request references an
immutable CI bundle and release receipt by digest. The platform produces infrastructure plan/apply,
backup, migration, deployment, rollback, and host-conformance receipts. Every receipt includes the
source commit, image digest, environment, plan digest, status, bounded step records, timestamps, and a
canonical digest.

Logs and receipts pass through redaction before persistence. Unknown or incompatible schema majors
fail closed. PASS means the documented check executed successfully; absent credentials, binaries,
servers, or third-party services produce BLOCKED or UNKNOWN, never synthetic success.

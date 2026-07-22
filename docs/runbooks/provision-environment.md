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
# Provision Environment

Run the plan workflow, review `infrastructure-plan.json` and the binary plan artifact, obtain environment approval, then run apply using the originating run ID, artifact name, and exact plan digest. Generate inventory and reconcile host configuration after apply.

## Evidence to retain

Retain the source SHA, plan digest, image digest, approval receipt, command output, resulting receipt, and operator identity.

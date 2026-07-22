#!/usr/bin/env bash
# --- L9_META ---
# l9_schema: 1
# origin: l9-deployment-platform
# layer:
# - repository
# tags:
# - L9_META
# - deployment-platform
# owner: platform
# status: active
# --- /L9_META ---
set -euo pipefail

: "${L9_RUNNER_REGISTRATION_TOKEN:?fresh runner registration token required}"
: "${L9_RUNNER_ARCHIVE_SHA256:?runner archive SHA-256 required}"
ansible-playbook \
  -i ansible/inventories/generated/hosts.yml \
  ansible/playbooks/configure-runner.yml \
  --limit management \
  -e "l9_runner_registration_token=$L9_RUNNER_REGISTRATION_TOKEN" \
  -e "l9_runner_archive_sha256=$L9_RUNNER_ARCHIVE_SHA256"

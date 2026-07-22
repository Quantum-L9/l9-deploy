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

inventory=${1:-ansible/inventories/generated/hosts.yml}
ansible-playbook -i "$inventory" ansible/playbooks/bootstrap.yml --limit management
ansible-playbook -i "$inventory" ansible/playbooks/harden.yml --limit management
ansible-playbook -i "$inventory" ansible/playbooks/configure-runner.yml --limit management
ansible-playbook -i "$inventory" ansible/playbooks/verify.yml --limit management

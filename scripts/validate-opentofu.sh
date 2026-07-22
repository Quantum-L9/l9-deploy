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
export TF_IN_AUTOMATION=true
export CHECKPOINT_DISABLE=1
tofu fmt -check -recursive infrastructure/opentofu
for module in infrastructure/opentofu/modules/*; do
  [[ -d "$module" ]] || continue
  tofu -chdir="$module" init -backend=false -input=false >/dev/null
  tofu -chdir="$module" validate
  rm -rf "$module/.terraform" "$module/.terraform.lock.hcl"
done
for environment in infrastructure/opentofu/environments/*; do
  [[ -d "$environment" ]] || continue
  tofu -chdir="$environment" init -backend=false -input=false >/dev/null
  tofu -chdir="$environment" validate
  rm -rf "$environment/.terraform" "$environment/.terraform.lock.hcl"
done

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

image_ref=${1:?exact image digest required}
repository=${2:?source repository required}
[[ "$image_ref" =~ ^ghcr\.io/[a-z0-9._-]+/[a-z0-9._/-]+@sha256:[a-f0-9]{64}$ ]] || {
  echo "mutable or invalid image reference rejected" >&2
  exit 2
}
[[ "$repository" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || {
  echo "invalid source repository" >&2
  exit 2
}
gh attestation verify "oci://$image_ref" --repo "$repository"

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

version=${1:-1.11.7}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

curl --proto '=https' --tlsv1.2 --fail --silent --show-error \
  https://get.opentofu.org/install-opentofu.sh \
  -o "$tmp/install-opentofu.sh"
chmod 0700 "$tmp/install-opentofu.sh"
"$tmp/install-opentofu.sh" \
  --install-method standalone \
  --install-path "$HOME/.local/bin" \
  --version "$version"
"$HOME/.local/bin/tofu" version | grep -F "OpenTofu v$version" >/dev/null

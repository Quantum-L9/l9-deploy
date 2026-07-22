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

incident=${1:?incident identifier required}
host=${2:?target host required}
printf 'Break-glass procedure for incident %s\n' "$incident"
printf '%s\n' \
  '1. Record approval in the incident system.' \
  '2. Issue a short-lived SSH certificate.' \
  "3. Connect through the approved management path to $host." \
  '4. Capture commands and evidence.' \
  '5. Revoke the certificate and rotate affected credentials.'

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

environment=${1:?Infisical environment slug required}
output_file=${2:-}
: "${ACTIONS_ID_TOKEN_REQUEST_URL:?GitHub OIDC URL unavailable}"
: "${ACTIONS_ID_TOKEN_REQUEST_TOKEN:?GitHub OIDC token unavailable}"
: "${INFISICAL_IDENTITY_ID:?Infisical identity id required}"
: "${INFISICAL_PROJECT_SLUG:?Infisical project slug required}"

api=${INFISICAL_API_URL:-https://app.infisical.com}
audience=${INFISICAL_OIDC_AUDIENCE:-https://github.com/Quantum-L9}
separator='?'
[[ "$ACTIONS_ID_TOKEN_REQUEST_URL" == *\?* ]] && separator='&'
oidc_url="${ACTIONS_ID_TOKEN_REQUEST_URL}${separator}audience=${audience}"

oidc=$(curl --fail --silent --show-error \
  -H "Authorization: Bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" \
  "$oidc_url" | jq -er .value)
access=$(curl --fail --silent --show-error \
  -X POST "$api/api/v1/auth/oidc-auth/login" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "identityId=$INFISICAL_IDENTITY_ID" \
  --data-urlencode "jwt=$oidc" | jq -er .accessToken)

echo "::add-mask::$access"
export INFISICAL_TOKEN=$access
export INFISICAL_DISABLE_UPDATE_CHECK=true
json=$(infisical export \
  --format=json \
  --projectId "$INFISICAL_PROJECT_SLUG" \
  --env "$environment" \
  --path / \
  --silent)

if [[ -n "$output_file" ]]; then
  umask 077
  : > "$output_file"
  destination=$output_file
else
  destination=${GITHUB_ENV:?GITHUB_ENV is required when no output file is supplied}
fi

while IFS=$'\t' read -r key value; do
  [[ "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || {
    echo "invalid environment key from Infisical" >&2
    exit 2
  }
  [[ "$value" != *$'\n'* && "$value" != *$'\r'* ]] || {
    echo "multiline Infisical values require file-based secret handling" >&2
    exit 2
  }
  echo "::add-mask::$value"
  printf '%s=%s\n' "$key" "$value" >> "$destination"
done < <(jq -er '.[] | [.secretKey,.secretValue] | @tsv' <<<"$json")

[[ -z "$output_file" ]] || chmod 0600 "$output_file"

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

mask_value() {
  if [[ ${GITHUB_ACTIONS:-} == true ]]; then
    printf '::add-mask::%s\n' "$1"
  fi
}

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

mask_value "$access"
export INFISICAL_TOKEN=$access
export INFISICAL_DISABLE_UPDATE_CHECK=true
json=$(infisical export \
  --format=json \
  --projectId "$INFISICAL_PROJECT_SLUG" \
  --env "$environment" \
  --path / \
  --silent)

validated=$(jq -cer '
  def fail($message): error($message);
  def unsafe_key:
    . == "ACTIONS_STEP_DEBUG" or
    . == "BASH_ENV" or
    . == "ENV" or
    . == "GITHUB_ENV" or
    . == "GITHUB_OUTPUT" or
    . == "GITHUB_PATH" or
    . == "IFS" or
    . == "LD_LIBRARY_PATH" or
    . == "LD_PRELOAD" or
    . == "NODE_OPTIONS" or
    . == "PATH" or
    . == "PYTHONPATH";
  if type != "array" then fail("Infisical export is not a secret list") else . end
  | map(
      if type != "object" then fail("Infisical secret entry is not an object") else . end
      | .secretKey as $key
      | .secretValue as $value
      | if ($key | type) != "string" or (($key | test("^[A-Za-z_][A-Za-z0-9_]*$")) | not)
        then fail("Infisical secret key is not a valid environment name")
        elif ($key | unsafe_key)
        then fail("Infisical secret key is prohibited")
        elif ($value | type) != "string"
        then fail("Infisical secret value is not a string")
        elif ($value | length) == 0
        then fail("Infisical secret value is empty")
        elif (
          ($value | contains("\u0000")) or
          ($value | contains("\r")) or
          ($value | contains("\n"))
        )
        then fail("Infisical secret value cannot be rendered safely")
        else {key: $key, value: $value}
        end
    )
  | sort_by(.key)
  | group_by(.key)
  | if any(.[]; length != 1)
    then fail("Infisical export contains a duplicate secret key")
    else map(.[0])
    end
' <<<"$json") || {
  echo "Infisical export failed validation" >&2
  exit 2
}

if [[ -n "$output_file" ]]; then
  destination=$output_file
else
  destination=${GITHUB_ENV:?GITHUB_ENV is required when no output file is supplied}
fi

destination_dir=$(dirname -- "$destination")
[[ -d "$destination_dir" ]] || {
  echo "runtime environment destination directory does not exist" >&2
  exit 2
}

umask 077
temporary=$(mktemp "$destination_dir/.l9-runtime-env.XXXXXX")
cleanup() {
  rm -f -- "$temporary"
}
trap cleanup EXIT

while IFS= read -r encoded; do
  [[ -n "$encoded" ]] || continue
  record=$(printf '%s' "$encoded" | base64 -d)
  key=$(jq -er .key <<<"$record")
  value=$(jq -er .value <<<"$record")
  mask_value "$value"
  printf '%s=%s\n' "$key" "$value" >> "$temporary"
done < <(jq -r '.[] | @base64' <<<"$validated")
chmod 0600 "$temporary"

if [[ -n "$output_file" ]]; then
  mv -f -- "$temporary" "$destination"
else
  cat "$temporary" >> "$destination"
fi

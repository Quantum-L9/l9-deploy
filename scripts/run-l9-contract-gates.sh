#!/usr/bin/env bash
# --- L9_META ---
# l9_schema: 1
# origin: l9-deployment-platform
# layer: [governance, validation]
# tags: [L9_CONTRACT, semgrep, l9-ci]
# owner: platform
# status: active
# --- /L9_META ---
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$root"

artifact_root=${L9_ARTIFACT_ROOT:-"$root/artifacts/l9-contracts"}
mkdir -p "$artifact_root/raw/semgrep" "$artifact_root/l9"

semgrep_version=$(semgrep --version)

# Paths must be repository-relative for l9-ci normalize (SDK v1+).
semgrep scan \
  --config .l9/policies/l9-deployment-contracts.yml \
  --json \
  --output "$artifact_root/raw/semgrep/report.json" \
  src scripts

l9-ci semgrep normalize \
  --input "$artifact_root/raw/semgrep/report.json" \
  --output "$artifact_root/l9/finding-bundle.json" \
  --root . \
  --snapshot-id "${GITHUB_SHA:-local}" \
  --provider-version "$semgrep_version" \
  --strict \
  --required \
  --revision "${GITHUB_SHA:-local}" \
  --no-dirty

l9-ci bundle validate "$artifact_root/l9/finding-bundle.json"

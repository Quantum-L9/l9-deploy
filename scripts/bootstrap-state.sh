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

: "${AWS_ACCESS_KEY_ID:?Object storage access key required}"
: "${AWS_SECRET_ACCESS_KEY:?Object storage secret key required}"
: "${L9_STATE_BUCKET:?State bucket name required}"
: "${L9_STATE_ENDPOINT:?S3 endpoint required}"
region=${L9_STATE_REGION:-eu-central}

if ! aws --endpoint-url "$L9_STATE_ENDPOINT" s3api head-bucket \
  --bucket "$L9_STATE_BUCKET" >/dev/null 2>&1; then
  aws --endpoint-url "$L9_STATE_ENDPOINT" s3api create-bucket \
    --bucket "$L9_STATE_BUCKET" \
    --region "$region"
fi
aws --endpoint-url "$L9_STATE_ENDPOINT" s3api put-bucket-versioning \
  --bucket "$L9_STATE_BUCKET" \
  --versioning-configuration Status=Enabled
aws --endpoint-url "$L9_STATE_ENDPOINT" s3api put-public-access-block \
  --bucket "$L9_STATE_BUCKET" \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

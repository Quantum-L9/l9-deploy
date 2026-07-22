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
provider "hcloud" {
  token = var.hcloud_token
}

variable "hcloud_token" {
  description = "Short-lived or runtime-injected Hetzner Cloud API token. Never persist in tfvars."
  type        = string
  sensitive   = true
}

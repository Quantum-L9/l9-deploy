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
variable "name" { type=string }
variable "load_balancer_type" { type=string }
variable "location" { type=string }
variable "network_id" { type=number }
variable "targets" { type=list(number); default=[] }
variable "listen_port" { type=number; default=443 }
variable "destination_port" { type=number; default=443 }
variable "labels" { type=map(string); default={} }

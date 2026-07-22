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
output "network_id" { value=module.network.id }
output "runner_server_id" { value=module.runner.id }
output "runner_private_ip" { value=module.runner.private_ip }
output "runner_public_ip" { value=module.runner.ipv4_address }

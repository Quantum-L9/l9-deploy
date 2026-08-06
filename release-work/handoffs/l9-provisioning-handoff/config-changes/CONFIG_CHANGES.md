<!-- L9_META
l9_schema: 1
origin: l9-deployment-platform
layer:
- repository
tags:
- L9_META
- deployment-platform
owner: platform
status: active
/L9_META -->
# Deferred config changes (apply + merge before Phase 2)

These were intentionally NOT fabricated in this session. Apply them on the branch
and merge, then proceed with the runbook.

## 1. Runner repository slug (confirmed: `Quantum-L9/l9-deploy`)
The self-hosted runner must attach to the repo that hosts the provision
workflows. Edit `ansible/inventories/group_vars/all.yml`:
```yaml
# before
l9_runner_repository: "Quantum-L9/l9-deployment-platform"
# after
l9_runner_repository: "Quantum-L9/l9-deploy"
```
(Also confirm the `github_runner` role default in
`ansible/roles/github_runner/defaults/main.yml` does not override this, or set it
to the same value.)

## 2. Runner tarball SHA-256 (supply at runtime)
`l9_runner_sha256` ships empty; the `github_runner` role asserts `length == 64`.
Obtain the verified SHA-256 for `actions-runner` **2.334.0** (linux-x64) from the
official release checksums and pass it at runtime:
```bash
# do NOT commit the value unless you have verified it against the official release
bash scripts/bootstrap-runner.sh \
  -e l9_runner_registration_token=<token> \
  -e l9_runner_sha256=<64-hex-sha256>
```
Alternatively commit the verified value into
`ansible/inventories/group_vars/all.yml` as `l9_runner_sha256: "<64-hex>"`.

## 3. Verify after applying
```bash
make validate           # expect EXIT 0
uv run l9-deploy inventory validate --fleet fleet/registry.yaml
```

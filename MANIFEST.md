<!-- L9_META
l9_schema: 1
origin: l9-deployment-platform
layer: [repository]
tags: [L9_META, deployment-platform, manifest]
owner: platform
status: active
/L9_META -->
# Repository Manifest

## Summary

- Repository: `Quantum-L9/l9-deployment-platform`
- Version: `0.1.5`
- Manifested files: **353**
- Manifested bytes: **788738**

`MANIFEST.json`, `MANIFEST.md`, and `checksums.sha256` are excluded from the JSON 
manifest to avoid self-referential hashes. The checksum index covers both manifest files.

## Responsibility map

| Path family | Responsibility | Files |
|---|---|---:|
| `.github/` | GitHub governance and workflow orchestration | 17 |
| `.l9/` | L9 ownership, policy, compatibility, and integration contracts | 19 |
| `src/` | deployment control-plane implementation | 57 |
| `schemas/` | versioned public JSON contracts | 20 |
| `scripts/` | operator, validation, and release tooling | 24 |
| `tests/` | behavioral, contract, security, and regression tests | 25 |
| `validation/` | machine-readable validation evidence | 23 |
| `infrastructure/` | OpenTofu infrastructure desired state | 39 |
| `ansible/` | host configuration and conformance | 33 |
| `deployment/` | runtime profiles, policies, probes, and templates | 18 |
| `fleet/` | fleet desired state and environment registration | 6 |
| `integrations/` | cross-repository integration projections | 16 |
| `templates/` | consumer adoption templates | 9 |
| `docs/` | architecture, operations, security, and consumer guidance | 23 |

## File inventory

| Path | Responsibility | Bytes | SHA-256 |
|---|---|---:|---|
| `.editorconfig` | repository governance, packaging, or operator entrypoint | 202 | `6297da6b1169de32dca2f6184b4eaa63a8bb6c7e1c66c20d6e813166256e3856` |
| `.github/CODEOWNERS` | GitHub governance and workflow orchestration | 576 | `e6ae145e3ab95fe530a9fe6ad9d83a4febbe91dd4c61079876c1723af25c07d3` |
| `.github/actions/collect-approval/action.yml` | GitHub governance and workflow orchestration | 2028 | `e2e23ce7478c72033e1a33d0d55613c095ed36243a8b088971d63a2ff8114a7d` |
| `.github/dependabot.yml` | GitHub governance and workflow orchestration | 479 | `735f2414437271c24e3a49441419d4cad28fcc41a9bf5d2eb52be9733389cb5c` |
| `.github/pull_request_template.md` | GitHub governance and workflow orchestration | 665 | `169fd0342bb137c69c97777da86a48df87109497b2a8a1f51e53f9944ae1bc6c` |
| `.github/workflows/backup-verify.yml` | GitHub governance and workflow orchestration | 1201 | `b6325d74c648141c5f21a0a6194a63b432f2b7673a738be1ba13654b55c5fba7` |
| `.github/workflows/configure-hosts.yml` | GitHub governance and workflow orchestration | 3141 | `02d7bbb7d8013cad19b9cd43962f4f9ce4debe5672672f8fa1f60d70c9065813` |
| `.github/workflows/deploy-dispatch.yml` | GitHub governance and workflow orchestration | 6637 | `afacfc086f4428d0c4bdaa77df7a957f4d1630adf39c941a7bacc31261dda6d9` |
| `.github/workflows/deploy-manual.yml` | GitHub governance and workflow orchestration | 1383 | `88bc0e8c96789088d39322e9ed084e4753f6fb0eb1137bbf22b219f6b573e086` |
| `.github/workflows/drift-detect.yml` | GitHub governance and workflow orchestration | 2524 | `390d4630903726794bd95f49001b03a9b318468432e346b8d75a48036f32eda6` |
| `.github/workflows/fleet-conformance.yml` | GitHub governance and workflow orchestration | 1096 | `8f8008f586fd01d4fd986ec19d57f53ccbb85f55b05eabb6d1cd93f2501510dc` |
| `.github/workflows/promote.yml` | GitHub governance and workflow orchestration | 2380 | `37c911a02c779312058827f8ddca13deacc994667e06085e520c35c0b960f329` |
| `.github/workflows/provision-apply.yml` | GitHub governance and workflow orchestration | 3886 | `c7e82ef7214142abd9269e7c1649380623aec14f927fceb7eac3762eb3e7b6cb` |
| `.github/workflows/provision-plan.yml` | GitHub governance and workflow orchestration | 2602 | `d0433b29cf5eb26d4980f531e030a17cdd859c91238336caaecddd76aa18144e` |
| `.github/workflows/release.yml` | GitHub governance and workflow orchestration | 2339 | `75543d09228ec66c0f16d8ebda825a5f9383faf8476bac734207e39bd483c473` |
| `.github/workflows/rollback.yml` | GitHub governance and workflow orchestration | 2958 | `5a215beb1f480e1845422a5b096f2a9bc9bc6489da4ac789226ac4a057781ca8` |
| `.github/workflows/runner-maintenance.yml` | GitHub governance and workflow orchestration | 3189 | `b2aa8539cbcef1b5a0b5af739583434d0a4e803990e75263b6939d813ad19555` |
| `.github/workflows/validate.yml` | GitHub governance and workflow orchestration | 1921 | `bc6a80b04ba7e618a5669a1b5a47e266b0051d77a56d7c0f4d6e65c4eb2eab95` |
| `.gitignore` | repository governance, packaging, or operator entrypoint | 306 | `64465eebb11dd91c5ceac877eeadf3ecd0ed609045e061a7912fb4df5504ec68` |
| `.l9/architecture.yaml` | L9 ownership, policy, compatibility, and integration contracts | 677 | `494c16a5b02c1c6b9e7369c54e1bbba02fcdea27c6728d7a07129c2570cf7d60` |
| `.l9/compatibility.yaml` | L9 ownership, policy, compatibility, and integration contracts | 890 | `cfa1a3c5a11559f8a4544180cb640a78704783d2501bf977df21b35309c8185a` |
| `.l9/governance-provider.yaml` | L9 ownership, policy, compatibility, and integration contracts | 757 | `98b0728d0eca1e2dcc5162e56e3f1df22efdcec86278ee7e52a3773fc84cacaf` |
| `.l9/integration-contracts/assurance.contract.yaml` | L9 ownership, policy, compatibility, and integration contracts | 460 | `a48da0d7658e1f5b11d3130d9cef3400f0d550c5184e005f835b078bfe7fd553` |
| `.l9/integration-contracts/ci-core.contract.yaml` | L9 ownership, policy, compatibility, and integration contracts | 496 | `295a7dde52c304aaaf9f8e5e4bae84bb2c815c38d7184753804c298811680264` |
| `.l9/integration-contracts/ci-sdk.contract.yaml` | L9 ownership, policy, compatibility, and integration contracts | 475 | `b4a64a533fc2a72ecc29e511241e46a9559ee6b31d25b9468c9f0d49c75923cf` |
| `.l9/integration-contracts/consumer.contract.yaml` | L9 ownership, policy, compatibility, and integration contracts | 581 | `6e01dec6663fd99efc5ada01b9834655611328692f45f87e69a4eb18d0c24bfd` |
| `.l9/integration-contracts/ghcr.contract.yaml` | L9 ownership, policy, compatibility, and integration contracts | 414 | `9a0b6a45e1b136fe0d9046d2c8d48006d7a28a3d24f7b6fd409c59ef1bbf005f` |
| `.l9/integration-contracts/github-org.contract.yaml` | L9 ownership, policy, compatibility, and integration contracts | 469 | `ae1a6c749a990af5ae544db90555397c152d51b6042edba988931a871c7d9333` |
| `.l9/integration-contracts/hetzner.contract.yaml` | L9 ownership, policy, compatibility, and integration contracts | 441 | `c80443f7dabeaf976a594d74c364fa2f95810c5baa3596f708c8c41dde97d0d1` |
| `.l9/integration-contracts/infisical.contract.yaml` | L9 ownership, policy, compatibility, and integration contracts | 402 | `50564bfabe7ef6cbf999304d6d7714261fe4e457da153c9f51baf92c8fa75094` |
| `.l9/integration-contracts/repo-template.contract.yaml` | L9 ownership, policy, compatibility, and integration contracts | 471 | `735b67550f00b6c18318b3bfcb526e05a5f0b83f26185762306d66022095f2ff` |
| `.l9/metadata-exclusions.yaml` | L9 ownership, policy, compatibility, and integration contracts | 1342 | `17155d67c6b8ff59c51de6ddc4e4496876e36a6ba927d5ad58ba8bcd225c07aa` |
| `.l9/ownership.yaml` | L9 ownership, policy, compatibility, and integration contracts | 721 | `2546f0b2febe2e948d439b6465e315e118629ccde28e4ec08212362db37570c4` |
| `.l9/policies/l9-deployment-contracts.yml` | L9 ownership, policy, compatibility, and integration contracts | 2269 | `e9801e314228a9e771472a6af2ed0bef30504593b5aa0b8b79e9e2e3120b2e2e` |
| `.l9/release-policy.yaml` | L9 ownership, policy, compatibility, and integration contracts | 448 | `c616ba614f8794e1c012ba9ef37b07c0c1d9b6b7eb2bdf908463a4c46505b918` |
| `.l9/repo-spec.yaml` | L9 ownership, policy, compatibility, and integration contracts | 5973 | `720860e7d7ca10467922dcceec62332db93decac72073804a31634f9a22c3e3b` |
| `.l9/tool-stack.yaml` | L9 ownership, policy, compatibility, and integration contracts | 409 | `33efce1f905c31d37fbd0cf214766b4cf5e8f8a5eb3407d72b72ae39e8a1ce49` |
| `.l9/transport-classification.yaml` | L9 ownership, policy, compatibility, and integration contracts | 1057 | `00f638d34e3d8d7db0b9326f56d480eff6d0e312c6ac8624b9c4bd012e0e6864` |
| `.pre-commit-config.yaml` | repository governance, packaging, or operator entrypoint | 1099 | `29326f094af5f45dacd6040015c8ea8da7e3e694f254bcc1803b8609ba9073da` |
| `.python-version` | repository governance, packaging, or operator entrypoint | 5 | `7b55f8e67b5623c4bef3fa691288da9437d79d3aba156de48d481db32ac7d16d` |
| `ARCHITECTURE.md` | repository governance, packaging, or operator entrypoint | 7459 | `cc4a2db8de684b227886899bea219d8177050f315185a1247588d5635464dfcb` |
| `CHANGELOG.md` | repository governance, packaging, or operator entrypoint | 5375 | `f2d1eaf91d55e9deca2b8867cebc96b18ca72b218caa8a4f102efad6f91c8a6b` |
| `CHANGE_SUMMARY.md` | repository governance, packaging, or operator entrypoint | 3303 | `4b8c8609fb33c513a4bcd5a16922ca1be6ddc1c17ff9dc16d7974820bf52d9d6` |
| `CONTRIBUTING.md` | repository governance, packaging, or operator entrypoint | 1927 | `f2d38831fd762effe0b025579d768e9ce7e0b4373b09ed41868e1a71d8fdc64f` |
| `CONVERGENCE_REPORT.yaml` | repository governance, packaging, or operator entrypoint | 1283 | `4595a29ef5ecf825e3e550ef765863578e2c78254ab6f99791ad5d51447f18ad` |
| `DELTA_REPORT.md` | repository governance, packaging, or operator entrypoint | 1894 | `c935caf56f22f4da77393fce2d3f2b8a4e465faf5927d262e75619841f1f439e` |
| `FINAL_TREE.md` | repository governance, packaging, or operator entrypoint | 17398 | `0c24ebaee06c67041f65ceb8946f76d714d806b86244216e83fc545b40826073` |
| `GAP_DEFECT_MATRIX.yaml` | repository governance, packaging, or operator entrypoint | 6285 | `646785cc6d95308273a2b30d53b922f1a9f0a457d0415c09b78f3b96a1644a82` |
| `Makefile` | repository governance, packaging, or operator entrypoint | 2496 | `8262d94a9373439fd92afd4e91666271d446f611aa52db72bae6daf1e62a65a8` |
| `README.md` | repository governance, packaging, or operator entrypoint | 6578 | `f96088b5d88ed78b2cd793481171ea0a6b3e91fd7690cac8cb72374120117f0e` |
| `REGRESSION_GUARD.md` | repository governance, packaging, or operator entrypoint | 4812 | `ee7e150ecb39f08de4e79277445ed6dcfa9c8e676ab4ffe6c241aeb639439dac` |
| `REMEDIATION_REPORT.md` | repository governance, packaging, or operator entrypoint | 2612 | `9336b7d64fe230b4ff56f298dd06a703a27649f53667dee6df68b65c9c3d270f` |
| `RUNBOOK.md` | repository governance, packaging, or operator entrypoint | 7807 | `007eb158e5654549cb837c3e0b80f09a88f1b7132ed7d6da5987eee5be6ad662` |
| `SECURITY.md` | repository governance, packaging, or operator entrypoint | 4795 | `03d38d11110e756f9ea66b84ed9cc07742850a3b83ae08bb2adfec64c13a2711` |
| `SPECIFICATION.md` | repository governance, packaging, or operator entrypoint | 63012 | `d22967cd5a0a0a217420341b638f51dc91ad6551a2d31915cbbda741e99429b7` |
| `TRACEABILITY_MAP.yaml` | repository governance, packaging, or operator entrypoint | 5436 | `64c06ecdc6af2042e9cd42cf37e14c0a9178697d8cf7284d2850c1b57bb4691e` |
| `UNKNOWN_REGISTER.md` | repository governance, packaging, or operator entrypoint | 1927 | `461da7ab836744033835f67c69b635b781a70bfedc6d6ca6109624d5ecf08ec0` |
| `VALIDATION.md` | repository governance, packaging, or operator entrypoint | 4778 | `8b9189c4b81f481fd9246c560c3372c5a81718f39a67155ddad6bce52d3a91bc` |
| `ansible/ansible.cfg` | host configuration and conformance | 533 | `46c5542c6ef7e1346b733502a694ff534650d1517af917a7df708412802d918f` |
| `ansible/inventories/generated/README.md` | host configuration and conformance | 542 | `bb78f38411d36f6eac934f34ca8e9d971be973691a9e4851bad6203af89fe350` |
| `ansible/inventories/group_vars/all.yml` | host configuration and conformance | 577 | `4b886e398302b6037f40c03a4ddacaf188e17080d2360e13e442ee73e21d98f5` |
| `ansible/playbooks/bootstrap.yml` | host configuration and conformance | 301 | `5ebe0c669779af4febbade9ec8b5136d9a9c3c06bbd3d55d00c84ba64cddebbe` |
| `ansible/playbooks/configure-backups.yml` | host configuration and conformance | 290 | `cedb7209cd9f3c0320ed9a5563517bd8ee07762b3648dbd13dea5e9e7fbc2819` |
| `ansible/playbooks/configure-runner.yml` | host configuration and conformance | 331 | `8260624a08deba33747c4e188e8820d14541ab2165d1ab985b26af5491c95b5b` |
| `ansible/playbooks/configure-runtime.yml` | host configuration and conformance | 307 | `e9360d6132a05a7efa57e86b1743541e72a58c8b39dcc4de2ae92352f3bcc927` |
| `ansible/playbooks/decommission.yml` | host configuration and conformance | 900 | `5aff4062f025ee5d3e2123b89e1b40c57099907b423feff25b67eef2dabcec21` |
| `ansible/playbooks/harden.yml` | host configuration and conformance | 284 | `b50aeab8a0e6df95be835d56111c0bf7a61685101738d45cf3ce899d63274080` |
| `ansible/playbooks/verify.yml` | host configuration and conformance | 271 | `d0775ab9078cf2428b9ef91c7b802580830dc942951f6d33fea638599be95657` |
| `ansible/requirements.yml` | host configuration and conformance | 373 | `bb81f7cd5300cd8dcb8571c5a2a3cb7d05c855505fa27fc9a2d93df1ba9c1d1d` |
| `ansible/roles/backup_agent/files/l9-backup-verify` | host configuration and conformance | 323 | `8a92bbcd5c952eebd2c3a23ad3bb759f44a92ec0eb5725f147dabac0355dbbae` |
| `ansible/roles/backup_agent/files/l9-postgres-backup` | host configuration and conformance | 634 | `8940aae311c45cd48780ccd6b1b8767959ef16e42c23241e83af1f9548421f93` |
| `ansible/roles/backup_agent/tasks/main.yml` | host configuration and conformance | 679 | `05233a52cbd929b69d3f51379ec09b88e755a79d89b5e3f8fa582c27fc45ccfd` |
| `ansible/roles/base/defaults/main.yml` | host configuration and conformance | 288 | `ea4e554a060c5602e033b7372a3bf5141e94614469e3c6d172640d54c3e3ea3a` |
| `ansible/roles/base/tasks/main.yml` | host configuration and conformance | 701 | `83164fa8f920e07b8c587f52ae4dec5cb9df7ea552eec41b5b959e60ad802d70` |
| `ansible/roles/caddy/tasks/main.yml` | host configuration and conformance | 1125 | `a8dc56126d85de54c2b63dd38f334749dc0e1ced39cb5c95fad57893a2535b6e` |
| `ansible/roles/conformance/tasks/main.yml` | host configuration and conformance | 864 | `30b88b136411ac18827b16aa583c61ae5221fa0bb8d3db1c6e25933922cf5260` |
| `ansible/roles/docker/handlers/main.yml` | host configuration and conformance | 286 | `ec663aeb586263631beead2eb9736e798b96ad3e4b75b2f904111906f2226725` |
| `ansible/roles/docker/tasks/main.yml` | host configuration and conformance | 1296 | `62c418bb95d657f3e7b42f249679c07c1333c0b969f6673a3e407a2634deaa9b` |
| `ansible/roles/github_runner/defaults/main.yml` | host configuration and conformance | 427 | `b73c4067700cb2352b43751f42dd5c859defe36b018ff5a8214877e55a74c2f2` |
| `ansible/roles/github_runner/tasks/main.yml` | host configuration and conformance | 2133 | `b5d951c55278b94203255ca5731252e5be572512d48a41eb9ac0e8609e289974` |
| `ansible/roles/host_firewall/handlers/main.yml` | host configuration and conformance | 286 | `af0cfd68a0fe9bdf4c5d24b887b2fdff64d47e7f49b04830d36f43d0c31e652a` |
| `ansible/roles/host_firewall/tasks/main.yml` | host configuration and conformance | 542 | `a3a8c5466c6cf299db876ea6c98f10e8dd9972dd0540e876f65367f80e23a7ef` |
| `ansible/roles/host_firewall/templates/nftables.conf.j2` | host configuration and conformance | 754 | `28fb1a55593819252bc757558a60a562ab65e1160ce3470ba245911f4ad73d20` |
| `ansible/roles/journald/handlers/main.yml` | host configuration and conformance | 283 | `dcba791e03aae9db3406eea8ed77623baff11857b79a59030abbc533dd0cedf8` |
| `ansible/roles/journald/tasks/main.yml` | host configuration and conformance | 477 | `882856a106c6fc60e0aa75542752d96b323fb4f36bda4b207139622a1df581ed` |
| `ansible/roles/runner_tooling/tasks/main.yml` | host configuration and conformance | 2309 | `c8d8a4fcc1cf5f1e528458cc4de986376c0379f20856fa9bc0f70f8ed943ef27` |
| `ansible/roles/sshd/handlers/main.yml` | host configuration and conformance | 265 | `e38c98a873c0644ebe4c53fc6dce17307792014a864dfc8d859ea62c9cc8c1f3` |
| `ansible/roles/sshd/tasks/main.yml` | host configuration and conformance | 755 | `fb19d0ea8cf1b5cd2ca349967793127fc62aa709dd3fc1bb7d295efb2217ec9a` |
| `ansible/roles/time_sync/tasks/main.yml` | host configuration and conformance | 360 | `913c57335ab909fd531cf124d11cc92fcaf1b52e9953d245ab5167e3505eb981` |
| `ansible/roles/unattended_upgrades/tasks/main.yml` | host configuration and conformance | 573 | `0f8e1e3df625f5f1cc337488ed4dc581e6c1b7dd3f0dce49d18e4e93d1288540` |
| `ansible/roles/users/tasks/main.yml` | host configuration and conformance | 708 | `81ca7fd8ccbc533d63182688e64e6b9a785cf677be89eb05954622f15761b85c` |
| `deployment/policies/compose-policy.yaml` | runtime profiles, policies, probes, and templates | 413 | `88fce6e698d7ac529045c6d41ca4db82bd06e116617aab41811156cf8d47fa1a` |
| `deployment/policies/migration-policy.yaml` | runtime profiles, policies, probes, and templates | 486 | `01cc91304e9d8d00e4c5e896903690989185740b07225ed0565a5c006a0c1db9` |
| `deployment/policies/production.yaml` | runtime profiles, policies, probes, and templates | 419 | `8f990db3b629c5896e777139b204f861483eb42dac70c0ec3d840552f867fca0` |
| `deployment/policies/rollback-policy.yaml` | runtime profiles, policies, probes, and templates | 502 | `3d2e6d913ee1fdbd340c15615406628ee37b9016d27797b7bd4a0841fa10857b` |
| `deployment/policies/staging.yaml` | runtime profiles, policies, probes, and templates | 417 | `5de0da2c8d0d0616f73c19bb3b084684f7154cfda8bf6fa9b6dc2bf175413b3c` |
| `deployment/probes/command.yaml` | runtime profiles, policies, probes, and templates | 308 | `df91293e8a8e06cccdc059c5ef7d53c4e36f3d21c456641250269dabd9ed05e4` |
| `deployment/probes/database.yaml` | runtime profiles, policies, probes, and templates | 305 | `e7a5927bdf059c49d7d17c6678bce8e4df7e96ec8e6d2a656fa4b2df9578e95b` |
| `deployment/probes/http.yaml` | runtime profiles, policies, probes, and templates | 314 | `1702a2f361f2a12d7532b5280741110dbece5db4e0e3f5b41c9ec4225c394029` |
| `deployment/probes/tcp.yaml` | runtime profiles, policies, probes, and templates | 303 | `0e51888b93b2483a09ac3a074d420ffa34ee5a2a3c7d8bcec5dfcfeb708190ef` |
| `deployment/profiles/container-service.yaml` | runtime profiles, policies, probes, and templates | 491 | `69fb9f8ccb35aeb68d1980c97110bd39a962e1903b30038f3fedc353b19bf34b` |
| `deployment/profiles/external-platform.yaml` | runtime profiles, policies, probes, and templates | 413 | `3010b57d5a049fbe339c291cc4d8be30991d041dab593a53da9db7e60034f166` |
| `deployment/profiles/scheduled-job.yaml` | runtime profiles, policies, probes, and templates | 415 | `304778c999a2d7bc2e854c8220290f8f506dbc42023b3138471445d34b80cff9` |
| `deployment/profiles/stateful-container.yaml` | runtime profiles, policies, probes, and templates | 538 | `d1a43264cc0d5c4492ac6f425d8e1e284a5cb091ee4f98302f4e80d83de56bac` |
| `deployment/profiles/worker-service.yaml` | runtime profiles, policies, probes, and templates | 455 | `617c0ef11e727157de302b4a8d6c589e9c29b27d3442434888beaf1319ce4206` |
| `deployment/templates/caddy-site.caddy.j2` | runtime profiles, policies, probes, and templates | 427 | `a71ce64763f2225f3314d9e59bc56e73ba45cbc5fe4b96dc68302a99b2605874` |
| `deployment/templates/compose.yaml.j2` | runtime profiles, policies, probes, and templates | 413 | `f6c140c4ffbbcdd917de26cc36dd7a1487d342dc41b47f3b275640862b71e03c` |
| `deployment/templates/env-file.j2` | runtime profiles, policies, probes, and templates | 370 | `baf6b9ca7d7e8e6a6904e95e7d87ae8d4f4704c3b46f09bfe37bc7b9bfe4efee` |
| `deployment/templates/systemd-unit.service.j2` | runtime profiles, policies, probes, and templates | 582 | `3c623cae750ed91cc93e3838f4d1e5e135f096bc1eaf293dc048dfc59743b0aa` |
| `docs/adr/0001-private-control-plane.md` | architecture, operations, security, and consumer guidance | 796 | `ae03a302fb7045de74741b0b96ca4a7bec10aceb940eeafcffe0cdb4c4f388a5` |
| `docs/adr/0002-digest-only-releases.md` | architecture, operations, security, and consumer guidance | 755 | `9e8100274470f2ac8a4bbce4bdbc6977610ad5ed6ff1b9fc3e3c4b9c7beb4770` |
| `docs/adr/0003-dedicated-runner.md` | architecture, operations, security, and consumer guidance | 783 | `482dc947afc4f89edcff726292d6d4b0d71b18e4e47b9f0daee61054e85bff5c` |
| `docs/adr/0004-opentofu-and-ansible.md` | architecture, operations, security, and consumer guidance | 779 | `d57faf258b64739a3eb54de3757e8d145db12ff38dddd0c5bf324de0197e950e` |
| `docs/adr/0005-public-private-broker.md` | architecture, operations, security, and consumer guidance | 790 | `03232b817ac21fbc8504b126775c177281f18dab4c85f4c977d3ff06b0312a80` |
| `docs/adr/0006-fail-closed-rollback.md` | architecture, operations, security, and consumer guidance | 790 | `3fa3d3386e96009126f419ea82f57f9f6e91be489544efcc0fc41aedf0398d92` |
| `docs/adr/0007-wire-contract-field-aliases.md` | architecture, operations, security, and consumer guidance | 2157 | `1566b2a28645a4b01683748b1ea04ee2e82c2c530862ba620ef44a5d228ba8ae` |
| `docs/architecture/control-plane-boundaries.md` | architecture, operations, security, and consumer guidance | 1124 | `2a94e64468f18414b8102f6fe0baed7bf51485339e8db29a00cf3a2634bd1762` |
| `docs/architecture/evidence-model.md` | architecture, operations, security, and consumer guidance | 881 | `796d3c2cf5db060e8e96cecef06987c42e52ac277c36a916ec29247654b03da9` |
| `docs/architecture/network-topology.md` | architecture, operations, security, and consumer guidance | 865 | `a7972c2ddd74515b52a182e6d349b52fb30af70a9d981db0270662337a164648` |
| `docs/architecture/release-transaction.md` | architecture, operations, security, and consumer guidance | 895 | `f0a2d96296975638356aa8f7cce3f6665c8464ca3ef0545b6dcc94ff9b57ce3c` |
| `docs/consumers/adoption.md` | architecture, operations, security, and consumer guidance | 524 | `2a58be0c3217d761ef9f11ca36a505eb956d438ac24718d9793299412636048b` |
| `docs/consumers/profile-authoring.md` | architecture, operations, security, and consumer guidance | 671 | `0707b65fdb0139bbfbd4eba3d2cd38080213b1229b0748022cd6d80e5dde20a4` |
| `docs/operations/fleet-conformance.md` | architecture, operations, security, and consumer guidance | 562 | `98460754876dad253e8c3da4d1bbb09d8b3a338e33497ca2354062cb26f4cb19` |
| `docs/runbooks/bootstrap-management-runner.md` | architecture, operations, security, and consumer guidance | 665 | `ec31fe2205bd3068e6e7f9283c516695ef6b107c5b91ea75b3a9a8bcfead8fa0` |
| `docs/runbooks/deploy.md` | architecture, operations, security, and consumer guidance | 585 | `343c3eec7c6437de919438abcb7a80f46822d10fa8f1deed8191b742769b675d` |
| `docs/runbooks/incident.md` | architecture, operations, security, and consumer guidance | 588 | `ae8b3943db100b1225c4e96d8b09a0f642145a26e4583f7d43870811a143f2bc` |
| `docs/runbooks/onboard-consumer.md` | architecture, operations, security, and consumer guidance | 630 | `3c09aa24874844efb357c6b9880eca4589916db7eabb0234f4c5d296ac8705e9` |
| `docs/runbooks/provision-environment.md` | architecture, operations, security, and consumer guidance | 598 | `64705e9eab3dcdc9d897bda225e0dcc7928e70b5cd71f269cac9729f2f7032eb` |
| `docs/runbooks/restore.md` | architecture, operations, security, and consumer guidance | 564 | `d6f68a95bfa7859b9c5616b083710796dbfc33a6c539ebc0a05655ddb366fe23` |
| `docs/runbooks/rollback.md` | architecture, operations, security, and consumer guidance | 554 | `e3dd7c7d5c2775a2c5c3b11e4a32c9b82ebefd477f5f850e500c0ec5073b6bce` |
| `docs/runbooks/rotate-runner.md` | architecture, operations, security, and consumer guidance | 572 | `8e2581d8ad70d3f878de20de303ae7b396e23a09083cb6c6999719392c4ae50d` |
| `docs/security/threat-model.md` | architecture, operations, security, and consumer guidance | 724 | `7cd65f8d0080ddf1e71b33ee6fb514a6f29d4abe72f593a9378f9c3945a4ab16` |
| `fleet/desired-state/README.md` | fleet desired state and environment registration | 346 | `2590bf72b726bdc3f16e9ab6e6cbde998719270e2725d9646fd42f16dc084de1` |
| `fleet/environments/management.yaml` | fleet desired state and environment registration | 303 | `27c210b6b2f1b5bb1cfa1b547af94c21d1944864289f9cf94b785b7ecc8fe958` |
| `fleet/environments/production.yaml` | fleet desired state and environment registration | 326 | `41765249bcdd73c6ba23fb819b1947bca39c206cc14c20e119520ba0b1367b25` |
| `fleet/environments/staging.yaml` | fleet desired state and environment registration | 324 | `8b36796c28196210130ca27cadef37c5825c7bbb712755b2046bc76dfe0684e1` |
| `fleet/projects/README.md` | fleet desired state and environment registration | 354 | `0f353af6f86c264e4967abdc5dd85dc80e11ec547eaaa8ed0685de6d5d48da8f` |
| `fleet/registry.yaml` | fleet desired state and environment registration | 1025 | `1a90b7a22260475285e1980d7221cc3c7da8b9dfbdc0509f1d8593a80a367586` |
| `infrastructure/opentofu/backend.example.hcl` | OpenTofu infrastructure desired state | 524 | `103dd1f5969c1d93e00bf0b90c55341dfad03a1548c77499b3cd809ce91aeba2` |
| `infrastructure/opentofu/environments/management/backend.tf` | OpenTofu infrastructure desired state | 220 | `4e812a939c4b324cced2939feab7d8419afd0f87839d1d1c4dc50f0a8dab4060` |
| `infrastructure/opentofu/environments/management/main.tf` | OpenTofu infrastructure desired state | 1665 | `c11a2b12beb3b79565947b92b224b0d8c6e66d59f70da95cd03fe1b148c67d95` |
| `infrastructure/opentofu/environments/management/outputs.tf` | OpenTofu infrastructure desired state | 414 | `843e3326d150679c4cf29e41df42dc92938ac66108724d28c8388d54769c5eb9` |
| `infrastructure/opentofu/environments/management/variables.tf` | OpenTofu infrastructure desired state | 600 | `f6f2cbe2e86eb96d2ac45b00968af93d7b1994e32ada35c27bd2e35100274c1b` |
| `infrastructure/opentofu/environments/management/versions.tf` | OpenTofu infrastructure desired state | 188 | `e409eaf70409a83a4443cc8e61ca9a98f214d3cfb9a6c8233f0b8a67dcee65f9` |
| `infrastructure/opentofu/environments/production/backend.tf` | OpenTofu infrastructure desired state | 220 | `4e812a939c4b324cced2939feab7d8419afd0f87839d1d1c4dc50f0a8dab4060` |
| `infrastructure/opentofu/environments/production/main.tf` | OpenTofu infrastructure desired state | 1534 | `e3c32a1f4e90a56d9ec48f1f620f01c75205994a66da7563ca034b753430ef90` |
| `infrastructure/opentofu/environments/production/outputs.tf` | OpenTofu infrastructure desired state | 326 | `ddaddab006be5102ccf170207ef52a5a9ac9652fe766fa1da3d1984e87e36353` |
| `infrastructure/opentofu/environments/production/variables.tf` | OpenTofu infrastructure desired state | 603 | `c2b2b51a10312e99645091d64ad3397d30bbd8e7631d4978f295532c6d1caae6` |
| `infrastructure/opentofu/environments/production/versions.tf` | OpenTofu infrastructure desired state | 188 | `e409eaf70409a83a4443cc8e61ca9a98f214d3cfb9a6c8233f0b8a67dcee65f9` |
| `infrastructure/opentofu/environments/staging/backend.tf` | OpenTofu infrastructure desired state | 220 | `4e812a939c4b324cced2939feab7d8419afd0f87839d1d1c4dc50f0a8dab4060` |
| `infrastructure/opentofu/environments/staging/main.tf` | OpenTofu infrastructure desired state | 1525 | `ea31461e9ae47f371d256e86e3222fac5c924e29c9bdb7b57606838aa7fa20d9` |
| `infrastructure/opentofu/environments/staging/outputs.tf` | OpenTofu infrastructure desired state | 326 | `ddaddab006be5102ccf170207ef52a5a9ac9652fe766fa1da3d1984e87e36353` |
| `infrastructure/opentofu/environments/staging/variables.tf` | OpenTofu infrastructure desired state | 603 | `c2b2b51a10312e99645091d64ad3397d30bbd8e7631d4978f295532c6d1caae6` |
| `infrastructure/opentofu/environments/staging/versions.tf` | OpenTofu infrastructure desired state | 188 | `e409eaf70409a83a4443cc8e61ca9a98f214d3cfb9a6c8233f0b8a67dcee65f9` |
| `infrastructure/opentofu/modules/dns-record/main.tf` | OpenTofu infrastructure desired state | 436 | `ba42e69b530426fabbbba9982f797a69cc6a7183d1dbecf5bde886c8642d5fc5` |
| `infrastructure/opentofu/modules/dns-record/outputs.tf` | OpenTofu infrastructure desired state | 235 | `29bc385603969cae57fce10badca7dd4ccdbc7b9e2293ee8f63c33f4505a6333` |
| `infrastructure/opentofu/modules/dns-record/variables.tf` | OpenTofu infrastructure desired state | 335 | `0cc481aeaec26b93ae7cfc5572d39e672c38e53d8cfacd180919d80cb4243c7a` |
| `infrastructure/opentofu/modules/firewall/main.tf` | OpenTofu infrastructure desired state | 567 | `60f144730aa2397e9c36cbda7b112e143152ab52b5cddee9c59ca661267fc159` |
| `infrastructure/opentofu/modules/firewall/outputs.tf` | OpenTofu infrastructure desired state | 234 | `d6de1ee70ac063ed0b5e2a02639d3f8a51be5af9ae81c638d855f34cbf995a49` |
| `infrastructure/opentofu/modules/firewall/variables.tf` | OpenTofu infrastructure desired state | 481 | `0730f2ba89bf34e49d07018a7bf67136a1f093f5b82d5236e41e0b8ae7ff9db9` |
| `infrastructure/opentofu/modules/load-balancer/main.tf` | OpenTofu infrastructure desired state | 953 | `73ed7c3777240f8ab1657f32244cdb3e2113150a0027efe51aca828dadc30e34` |
| `infrastructure/opentofu/modules/load-balancer/outputs.tf` | OpenTofu infrastructure desired state | 294 | `f4145af989845c00b93fe97340302e5dda76d6d452c0c780cf757834b4aed785` |
| `infrastructure/opentofu/modules/load-balancer/variables.tf` | OpenTofu infrastructure desired state | 553 | `f7316ad5484a8830bb39bfb4cd805d34dd016c508a418e9ab66a794f0db20d50` |
| `infrastructure/opentofu/modules/network/main.tf` | OpenTofu infrastructure desired state | 487 | `fe4120cbc19c370d4aa7a8270269768336b16ec7b08461010a147b84de629254` |
| `infrastructure/opentofu/modules/network/outputs.tf` | OpenTofu infrastructure desired state | 385 | `cb8240ea46311aedcf00499fe0f39454cc486776fb616bb6b17344a7d7887428` |
| `infrastructure/opentofu/modules/network/variables.tf` | OpenTofu infrastructure desired state | 439 | `7dd66f4efd0ab88df92be6c7f22d4ab649e0cf348d68d7fb76a86f5076e168a5` |
| `infrastructure/opentofu/modules/placement-group/main.tf` | OpenTofu infrastructure desired state | 281 | `f6c02f0ec4a7de31d2f62a90f3c6a9852fce4b624157f7a1c756996dbf4149b1` |
| `infrastructure/opentofu/modules/placement-group/outputs.tf` | OpenTofu infrastructure desired state | 241 | `ad2c988061f221c7a3759a5187c851985fb1d6214f164e9cfe0832b443f237e0` |
| `infrastructure/opentofu/modules/placement-group/variables.tf` | OpenTofu infrastructure desired state | 321 | `338cba9be36ac1ab1b92f36197c226974cc6c3595a1c6a9cf1f709033e25deb7` |
| `infrastructure/opentofu/modules/server/main.tf` | OpenTofu infrastructure desired state | 749 | `21ee8c78d50c3eb8f4e2a7da61a0a9ee2bdf5f356f20ed05550e86708379dca8` |
| `infrastructure/opentofu/modules/server/outputs.tf` | OpenTofu infrastructure desired state | 404 | `08b8b5628f8f33ad86dedcaf0c14340ffc93a55f1644cc31628c1261c93cc1ce` |
| `infrastructure/opentofu/modules/server/variables.tf` | OpenTofu infrastructure desired state | 782 | `040a5174809911d453c860d930c6e79330421dfef95922782d56a3fe0d65d409` |
| `infrastructure/opentofu/modules/volume/main.tf` | OpenTofu infrastructure desired state | 380 | `f2e8667f5a450bd5a7a106605541e026d0997d1e767059d77f68c7da5dc7f67b` |
| `infrastructure/opentofu/modules/volume/outputs.tf` | OpenTofu infrastructure desired state | 296 | `b4540a4d5679d3facc6fc76dfd85126807b9277cd6b0fee4c05b66bd01fb8b16` |
| `infrastructure/opentofu/modules/volume/variables.tf` | OpenTofu infrastructure desired state | 497 | `1e9fea31b59f6eda446c6dc214797f8e031b8a5608ccd9a2818bedd466664d2c` |
| `infrastructure/opentofu/providers.tf` | OpenTofu infrastructure desired state | 410 | `ea51484124f2f45ad1fa48c0a1c7d0f6d08d4b48ae5aef16f84c5261e0ee78c2` |
| `infrastructure/opentofu/versions.tf` | OpenTofu infrastructure desired state | 355 | `7c11ef6cee27a274b3983ded77cc950c02429f8da0f5ec36eef05942dd65b6cb` |
| `integrations/consumers/seo-bot.deployment.yaml` | cross-repository integration projections | 2178 | `42b5776614db9a4e34a5025eaac2123467e8065a24c31ff5cfe09312392216bd` |
| `integrations/github-org/README.md` | cross-repository integration projections | 437 | `673391e965459ec4b6cf15eb52b935c5e37d62bae2444133a65260451a25b2fb` |
| `integrations/github-org/deployment-interface-registry.yml` | cross-repository integration projections | 967 | `f02cc1ac39716d63e3523b6e057e4d4cf5b1d548f37784a1505326587c03dee6` |
| `integrations/github-org/workflow-templates/l9-container-release.properties.json` | cross-repository integration projections | 241 | `1e93201abf265095d65f2a2464d37b6b460450e2393d90f072fc7864bd557862` |
| `integrations/github-org/workflow-templates/l9-container-release.yml` | cross-repository integration projections | 804 | `256153ee27df626ab3a3bff20df4db2e27d9921a2179ad9a1ff31cabbcf18656` |
| `integrations/github-org/workflow-templates/l9-scheduled-job-release.properties.json` | cross-repository integration projections | 244 | `70f38b62ef692b9caf693bef7878eb75ffd073417654e0c409dff1291f91b94f` |
| `integrations/github-org/workflow-templates/l9-scheduled-job-release.yml` | cross-repository integration projections | 804 | `256153ee27df626ab3a3bff20df4db2e27d9921a2179ad9a1ff31cabbcf18656` |
| `integrations/github-org/workflow-templates/l9-stateful-container-release.properties.json` | cross-repository integration projections | 246 | `9f183e9f00a24e6d25f5e85cb129fa3bbcf452d8346cf195f96f77f51d69b480` |
| `integrations/github-org/workflow-templates/l9-stateful-container-release.yml` | cross-repository integration projections | 804 | `256153ee27df626ab3a3bff20df4db2e27d9921a2179ad9a1ff31cabbcf18656` |
| `integrations/github-org/workflow-templates/l9-worker-release.properties.json` | cross-repository integration projections | 233 | `4f3fbc74dea843e32c87f6681042cbe5d7f6767366ca4c63a17f83bd3135afe1` |
| `integrations/github-org/workflow-templates/l9-worker-release.yml` | cross-repository integration projections | 804 | `256153ee27df626ab3a3bff20df4db2e27d9921a2179ad9a1ff31cabbcf18656` |
| `integrations/l9-assurance/README.md` | cross-repository integration projections | 376 | `87a997398492525448b10276a1bc8f40b959f15775cec68e4b4dd518a3ea9d72` |
| `integrations/l9-ci-core/README.md` | cross-repository integration projections | 830 | `822da4d8da001a84999670b77eff0ea1d320fd426342122c2ff3ae53a4bacf22` |
| `integrations/l9-ci-core/container-release.yml` | cross-repository integration projections | 11547 | `8391f612cbacddcf2da3453524929a78a0c9c8a190b830ece69269cb1a637861` |
| `integrations/l9-ci-sdk/README.md` | cross-repository integration projections | 345 | `6494ab9ae035682ab76fad51649fd49abed8a1d4c95a7676ecbb66aa70cf2796` |
| `integrations/l9-repo-template/README.md` | cross-repository integration projections | 354 | `795db4b37684e77546d33b548b4c7c96c8ac28c6d95573930491a47ecce1422c` |
| `pyproject.toml` | repository governance, packaging, or operator entrypoint | 1529 | `07a40726ae6d72f262fc6b273e05fd2a5df426c4f53902adb8893bd554473c6e` |
| `schemas/v1/approval-receipt.schema.json` | versioned public JSON contracts | 2677 | `65b18a01f39b3660fe824e08d0a8215afdafaf60c132baafd64c8e7d9a8b1049` |
| `schemas/v1/backup-receipt.schema.json` | versioned public JSON contracts | 2187 | `3d18b035794d0e13f07a3d2c43d4b1953250d872933d72d554cd381600bafc07` |
| `schemas/v1/ci-gate-binding.schema.json` | versioned public JSON contracts | 1436 | `8836a726e34ddf3d800de33fa4066c20e13051ab9d550bd999cf1f7864acd9ef` |
| `schemas/v1/deployment-plan.schema.json` | versioned public JSON contracts | 2785 | `88a3e2b887c96824b6b95e36b01c23ce9a7badeea7f59ef7fa750180a0c3d08f` |
| `schemas/v1/deployment-profile.schema.json` | versioned public JSON contracts | 11382 | `42e1ee3e83751f36c922dcc72c98c8e5f77589758f5b8b03bb8d5bf7a3910803` |
| `schemas/v1/deployment-receipt.schema.json` | versioned public JSON contracts | 3444 | `cd1ef7235f846359c1b8d3baf17915780dd1093e2e84d87bfe002011985bede6` |
| `schemas/v1/deployment-request.schema.json` | versioned public JSON contracts | 3186 | `31c52e4f9a226a722d263a7754999100902e86f4d6568cd90b7712e3aa1cd502` |
| `schemas/v1/evidence-record.schema.json` | versioned public JSON contracts | 2292 | `f447dfee092b9db8f75b09e3b3cac708030e852d03ee938242d8d8681af316cb` |
| `schemas/v1/fleet-inventory.schema.json` | versioned public JSON contracts | 3335 | `bddc0c427b65b0374e43b2f0db0791e4bce61a2c5ed045a8e8adeb4df487e627` |
| `schemas/v1/health-probe.schema.json` | versioned public JSON contracts | 2448 | `72d94cccb68a23c5bb48e6e5e13c7553a01109334847fde471890ff0e6b20900` |
| `schemas/v1/host-conformance.schema.json` | versioned public JSON contracts | 1133 | `c9bd60c7773d784b42c308f43de5cc193822145a852592b3a39f201b3058a0f0` |
| `schemas/v1/idempotency-store.schema.json` | versioned public JSON contracts | 3566 | `24b2a00a9b9f648895974bdc66ab81d4fe6d0419406970341ce9fb76da89759a` |
| `schemas/v1/infrastructure-plan.schema.json` | versioned public JSON contracts | 1812 | `ef1c39b5938e1f5d37b92df46a174d3e91450c62070d41cfbcf59f4922acc5a1` |
| `schemas/v1/infrastructure-receipt.schema.json` | versioned public JSON contracts | 2132 | `9ec350a143a095cf68949b00856988eb363f34ae2a70e5764e6a30f07a35d3b8` |
| `schemas/v1/migration-receipt.schema.json` | versioned public JSON contracts | 2196 | `1467019652a2b6f1f7722f82323ff179ea9861e4485573eb5b3a816f42a93f76` |
| `schemas/v1/release-artifact-binding.schema.json` | versioned public JSON contracts | 2482 | `dd719d890f8c82d3b6fb4af7a8ccfed701468616b52b4b66d8056d7651b9b25d` |
| `schemas/v1/release-evidence-reference.schema.json` | versioned public JSON contracts | 1885 | `d1f9ff0102d6f30012d1481d6a76aee88c72153c0d798f500ce56faafd4f38bd` |
| `schemas/v1/repository-release-receipt.schema.json` | versioned public JSON contracts | 1904 | `fea9471ec99e36e8dcff9d6f53f78395290a8533e2abb2182d8075bce4de8545` |
| `schemas/v1/rollback-receipt.schema.json` | versioned public JSON contracts | 2193 | `cf947515927fa650a00ac71fdf3440d6bbc7111d91b3ccd1b4ac10b9e7c1b321` |
| `schemas/v1/server-profile.schema.json` | versioned public JSON contracts | 2226 | `7e367e95778f961d70743ddee4becac38ee74a4c48b3fb251895af2641d273bf` |
| `scripts/_bootstrap.py` | operator, validation, and release tooling | 1450 | `583808586d20742fa427a968df358a1ca6143195afbdf727c5587347df9c62ed` |
| `scripts/bootstrap-runner.sh` | operator, validation, and release tooling | 620 | `00489a4cd6a69cbf10a2ba604a27188b274d3549525ced09a3afa75c6fdb88b1` |
| `scripts/bootstrap-state.sh` | operator, validation, and release tooling | 1116 | `2a6943c7e9bab8fc533d3e4b785879afd41f1de92b691b7526dae327cc45d413` |
| `scripts/break-glass-access.sh` | operator, validation, and release tooling | 642 | `d4f37ea6e5a10e82c8ab9bc2987912730276711926a3befd34b8ec6a1a1b142b` |
| `scripts/build-release-archive.py` | operator, validation, and release tooling | 6706 | `72ff5fe77c191940a2c39c8ced294e1dc3851c217111d335f7ab480bc107910a` |
| `scripts/collect-github-approval.py` | operator, validation, and release tooling | 4472 | `40ee5108ae22ec92ed4f237588d7472a3bb923d60de1b05d902794b0a6323eae` |
| `scripts/fast-contract-scan.py` | operator, validation, and release tooling | 6812 | `f94ea52495cc8e4e1f78e81495750fd226b208a557f95456f85084c079f111e6` |
| `scripts/generate-inventory.py` | operator, validation, and release tooling | 1238 | `de260e8effa60acaa59ca7a9c702f4e4f6027188cb049d34662d50a97aacc60e` |
| `scripts/generate-release-artifacts.py` | operator, validation, and release tooling | 7924 | `9192635ff37c69355a9f44c0f7b1bfa88c4f9ad953f1a3a04b6613728810fc47` |
| `scripts/infisical-oidc-env.sh` | operator, validation, and release tooling | 2160 | `cbbe70b9c52a30e9bf056d7972e4a0fad50e731093bfe9fb6d0d699e842da0d6` |
| `scripts/inject-l9-meta.py` | operator, validation, and release tooling | 4697 | `a23d1c87850be8b71ddd1c593a011177485987bfcb3518117d559ec4061edd18` |
| `scripts/install-opentofu.sh` | operator, validation, and release tooling | 670 | `00def39fd1531058d04e813456e23b32073649e4a0d01a5e9c478aa6015f9c1f` |
| `scripts/package-adoption-kit.py` | operator, validation, and release tooling | 1216 | `3d579e391dedfa3b3089b35873825b41a2572a72a9f6b7729dcd00af3b872624` |
| `scripts/prepare-deployment.py` | operator, validation, and release tooling | 3356 | `71be224d810a5f1c92738ab9b0d756fe3b7f8bd42092fa07468547217f74e9bd` |
| `scripts/promote-request.py` | operator, validation, and release tooling | 2548 | `73e041e1b1b24ebc31eadbf364e83c2f9ddcf2c748f5314caa50fd43af6abb45` |
| `scripts/rotate-runner.sh` | operator, validation, and release tooling | 628 | `35afd2970c46ae0c36c7e09398a9580a9de597d2f6157b9e4fa41187ef170b7c` |
| `scripts/run-l9-contract-gates.sh` | operator, validation, and release tooling | 979 | `143b3edbc6585932114b16ecf50312f4929ad54c145644439483343c2282923b` |
| `scripts/validate-alignment.py` | operator, validation, and release tooling | 7474 | `d88729f376d9adae501aebbac3307c391b0fa9226b90f59d1948428f18a16d65` |
| `scripts/validate-contracts.py` | operator, validation, and release tooling | 4730 | `3c6209437d0dfea89ee70bd48efe89698f53969bedc06c9c546d7d321d40daf2` |
| `scripts/validate-opentofu.sh` | operator, validation, and release tooling | 871 | `862b6bfd5aa370f438c81cef6861edf8ae840ca90f19d4c4e7a47c7c5f4bd2e6` |
| `scripts/validate-release-pack.py` | operator, validation, and release tooling | 12178 | `7e26c9e993fafe329ef61266d23306c13071e66bad83a1f2bac38c8fd4aaa9b0` |
| `scripts/validate-workflows.py` | operator, validation, and release tooling | 6733 | `c18adf601bc450b889411f8d40b33b2a2a71381940118747625df30b2f19405a` |
| `scripts/verify-attestation.sh` | operator, validation, and release tooling | 642 | `3efe7fadf713378ae6febfa375804c866d7ef91baa6d7c8f192527ccce5cfb63` |
| `scripts/verify-l9-meta.py` | operator, validation, and release tooling | 788 | `6cfb505a1b6bae9bfafe8b2a237baf2c7fbc0bb2275d0aa4cdf28ec55520a3cf` |
| `src/l9_deploy/__init__.py` | deployment control-plane implementation | 196 | `d9f3de438e3697db90fd5733a73a06e9c684444ac610699b12676179e15399b6` |
| `src/l9_deploy/__main__.py` | deployment control-plane implementation | 254 | `a0bc5fa92ee5c45f59eb5bbed4210cbd109dbf45c46fb374557d71c808f7dd26` |
| `src/l9_deploy/canonical.py` | deployment control-plane implementation | 1857 | `7337cd8742fb7f2cc72b4472a93119828ec732c551dd40b015e01c1c0e1fed40` |
| `src/l9_deploy/cli.py` | deployment control-plane implementation | 30161 | `e83bf5a3f2c9ccfcb0740d00e385b07d1eb3650ac46affbbb92b05fc2b501f5b` |
| `src/l9_deploy/contracts/__init__.py` | deployment control-plane implementation | 174 | `38cd74064a41cdc13a425a20d9f350e4d9cb396b57397b9bb9f19e7c9339abd8` |
| `src/l9_deploy/contracts/alias_policy.py` | deployment control-plane implementation | 2986 | `14e0007d32d31eaf7b5e7d3de438723a2d0b4923160f2d2bdc62d4e4aa4509e2` |
| `src/l9_deploy/contracts/catalog.py` | deployment control-plane implementation | 2870 | `a93b082645fe1c91c189af27fcf5d80162611b72b45feb994b9994c6b05e28ba` |
| `src/l9_deploy/contracts/compatibility.py` | deployment control-plane implementation | 780 | `e33e326f5343686fd2ca2dd5bdc4562556c7f0e645e360c1501e560eb2a977a5` |
| `src/l9_deploy/contracts/loader.py` | deployment control-plane implementation | 615 | `fcef8081285d0341d8cd621b1b72774b4959d5c2ea5d58f687c30049e3187003` |
| `src/l9_deploy/contracts/models.py` | deployment control-plane implementation | 14796 | `075fbedc8e6202cf89cd6c1b49441aeb5edb940674310532a8d1daeaeb1f36eb` |
| `src/l9_deploy/contracts/validator.py` | deployment control-plane implementation | 3665 | `b99d1b913096ca9e560754f4fdd4d11dae16ac46e539947c2a12cf0df9b3fb96` |
| `src/l9_deploy/errors.py` | deployment control-plane implementation | 560 | `e8893f6af96dd123159741060aaf711d2bf66d50dacc2f8e8dfc244f3645ea1e` |
| `src/l9_deploy/evidence/__init__.py` | deployment control-plane implementation | 174 | `38cd74064a41cdc13a425a20d9f350e4d9cb396b57397b9bb9f19e7c9339abd8` |
| `src/l9_deploy/evidence/approval.py` | deployment control-plane implementation | 4830 | `af2b5d053245218febcdf765bca15531321660f33ad30581dabe4e2eeb6c040e` |
| `src/l9_deploy/evidence/ci.py` | deployment control-plane implementation | 6593 | `f1a7e0177af7386457ba3fe5eb9726eafc1ba40dc331321ff88775d64e31a165` |
| `src/l9_deploy/evidence/digests.py` | deployment control-plane implementation | 269 | `04ee5b0d1f4bc97b6eb1ff0ea9f4a93f4e2ce46ef3e8e291c5f7c7a42235131a` |
| `src/l9_deploy/evidence/ledger.py` | deployment control-plane implementation | 8945 | `0afc75c26f77c9c69e0807b3704a871e80409c59b7bd233ee6ed11d6cb6b46d1` |
| `src/l9_deploy/evidence/publisher.py` | deployment control-plane implementation | 1188 | `9eef476a36efa7114db534b883184cd67d20b15d272a26a15f00b0cc7749fbee` |
| `src/l9_deploy/evidence/receipts.py` | deployment control-plane implementation | 3718 | `520312f4f3ec5d1d81e22ebe52a8ceb886a3b5ab6fb804809712215c929b1ed5` |
| `src/l9_deploy/evidence/records.py` | deployment control-plane implementation | 1140 | `a8c877e4c5b32ef8b0efbf22c06914c186c9748c2b0a338d626d1d166cf27f97` |
| `src/l9_deploy/execution/__init__.py` | deployment control-plane implementation | 174 | `38cd74064a41cdc13a425a20d9f350e4d9cb396b57397b9bb9f19e7c9339abd8` |
| `src/l9_deploy/execution/backups.py` | deployment control-plane implementation | 1667 | `bea41227400e42e912413e6c37758b10a41b5fdc4aaf4416575033e9260884bf` |
| `src/l9_deploy/execution/compose.py` | deployment control-plane implementation | 2051 | `566752b2e27f9b5058d1f333011c616b10b2e31674f107536ab6984074a3284a` |
| `src/l9_deploy/execution/engine.py` | deployment control-plane implementation | 11524 | `2116d7465bc3c176d181133e63cf828c3a9f47c08382909caf15e7f09cb42bff` |
| `src/l9_deploy/execution/health.py` | deployment control-plane implementation | 2725 | `133306f4f8b1816f0e3900755e1df038d73ee6e48f91896f6b0802970e41002e` |
| `src/l9_deploy/execution/images.py` | deployment control-plane implementation | 1322 | `e5b9d5ed555000370be255a98c9ce8e10366e231e410a4f1a53663fc8e40b3eb` |
| `src/l9_deploy/execution/locks.py` | deployment control-plane implementation | 1010 | `a713b7909d47b1c918bd7475f9f460bf56f04cc7dad4e8267b5896318ee3de78` |
| `src/l9_deploy/execution/migrations.py` | deployment control-plane implementation | 1275 | `b62066ee1cdff845299e7b7eaf1ad76f66279303dc0918df16cceedcd70a2e72` |
| `src/l9_deploy/execution/promotion.py` | deployment control-plane implementation | 1791 | `c7aa11c7d42e43f80f17ea6c9095b35b1ff8974e9d0f616fa8501d0c771d97f5` |
| `src/l9_deploy/execution/remote.py` | deployment control-plane implementation | 3152 | `d5b6eee12536c590c1719aa0d43c1f9a3a85066051fb2f7d8f3e97b10abe6b39` |
| `src/l9_deploy/execution/rollback.py` | deployment control-plane implementation | 1608 | `636f02b59a0a7051abd9716e78c061dea9c334ca1beae0d7572354bb803a7feb` |
| `src/l9_deploy/integrations/__init__.py` | deployment control-plane implementation | 174 | `38cd74064a41cdc13a425a20d9f350e4d9cb396b57397b9bb9f19e7c9339abd8` |
| `src/l9_deploy/integrations/ansible.py` | deployment control-plane implementation | 1069 | `7621b6cf6a2d60d6eaba509ad01df4cedcf6bbe1c1e892b85814b9793ef514a7` |
| `src/l9_deploy/integrations/ghcr.py` | deployment control-plane implementation | 596 | `5055f89ef6c0b88ed28c30612948b81ff419bc765877409a0bba2de4e5bcc0f5` |
| `src/l9_deploy/integrations/github.py` | deployment control-plane implementation | 1293 | `8a17ebdbc641d12767885b9da470f777a6e1a1dd822a5303b76e8ad5b442a838` |
| `src/l9_deploy/integrations/hetzner.py` | deployment control-plane implementation | 591 | `ea46828c9aaf2eec9c5d3b937d6f58e3403ec719ac63632e1a4077c71e3b9387` |
| `src/l9_deploy/integrations/infisical.py` | deployment control-plane implementation | 2337 | `3465cf5a2f445dd5c09ef4b8110da8037f318e9ad205af2f93e72fe7a115bdab` |
| `src/l9_deploy/integrations/opentofu.py` | deployment control-plane implementation | 3042 | `a035fca6679391966dea8a24edb7e4295109f5e2247b330021b9f627a0248b0d` |
| `src/l9_deploy/inventory/__init__.py` | deployment control-plane implementation | 174 | `38cd74064a41cdc13a425a20d9f350e4d9cb396b57397b9bb9f19e7c9339abd8` |
| `src/l9_deploy/inventory/generator.py` | deployment control-plane implementation | 1176 | `9e534bcaf2a2604e4d4dd143ba49716b454818e3a908df3917bbc61d24c2ea4c` |
| `src/l9_deploy/inventory/loader.py` | deployment control-plane implementation | 626 | `a8c6bea6c3ad486b9d19afb646627a3019857b6cb950aeb95711f9d3215f2444` |
| `src/l9_deploy/inventory/resolver.py` | deployment control-plane implementation | 1504 | `2fbab1856c233b445388d8a489e6eb574be1db9cc496886554add89802ea1db9` |
| `src/l9_deploy/logging.py` | deployment control-plane implementation | 1100 | `5759eaae77098c41034be01d0b4ebd332863a191018daf3e06239daabdc2e64f` |
| `src/l9_deploy/planning/__init__.py` | deployment control-plane implementation | 174 | `38cd74064a41cdc13a425a20d9f350e4d9cb396b57397b9bb9f19e7c9339abd8` |
| `src/l9_deploy/planning/backups.py` | deployment control-plane implementation | 906 | `8faa3bb136e3e6ac9f18705ba1ccad7f4db4d8a023ab3fb0be9c36f1756ad154` |
| `src/l9_deploy/planning/migrations.py` | deployment control-plane implementation | 799 | `e485adcb7de30034f5b738dd6900584a907b4a141612578bb7bb07db4177c221` |
| `src/l9_deploy/planning/planner.py` | deployment control-plane implementation | 3410 | `7f2c62c4c71bd8129c123de2155e2fb235120b22dcece934f3a06a9171f11681` |
| `src/l9_deploy/planning/rollback.py` | deployment control-plane implementation | 353 | `6c93424687271cbdb4d6fa53679b76dbbc01cdde67dbef1b996d08061674af33` |
| `src/l9_deploy/planning/topology.py` | deployment control-plane implementation | 381 | `29be8302daf8272466a1774a013b124aeda878e64dd080cd39bdb690ef499af6` |
| `src/l9_deploy/redaction.py` | deployment control-plane implementation | 1523 | `487fa7fa4a1efbb94b36d2d214ae6b947a9b00354cc27a0d30f55eba949c3b06` |
| `src/l9_deploy/release_inventory.py` | deployment control-plane implementation | 1564 | `08f91c53af925f72fedee16c3dfb0d004005520101ac69a8f769c4402e19e777` |
| `src/l9_deploy/requests/__init__.py` | deployment control-plane implementation | 174 | `38cd74064a41cdc13a425a20d9f350e4d9cb396b57397b9bb9f19e7c9339abd8` |
| `src/l9_deploy/requests/allowlist.py` | deployment control-plane implementation | 1149 | `7db9cce8a9afb5439ff849a99c67f62ae29e6f9e2a1513759b373d031aa240ac` |
| `src/l9_deploy/requests/idempotency.py` | deployment control-plane implementation | 6666 | `40428483dab2740482ddbb7df921d964b34af680a820e77dafd0587179203ac5` |
| `src/l9_deploy/requests/parser.py` | deployment control-plane implementation | 704 | `18f98b779dadac99dea67d3104c2ddc85effc8eee0e7cf0e705932ccb405b05c` |
| `src/l9_deploy/requests/verifier.py` | deployment control-plane implementation | 4067 | `70a0b345e0de11a7639397d5c4a0912900dd446f87493bbe047711087e068d2e` |
| `src/l9_deploy/subprocesses.py` | deployment control-plane implementation | 2346 | `6926cd33899b2d4e138c05146c2d681cfc4cb7aa8b21a3d693917e0726e36475` |
| `templates/consumer/common/README.md` | consumer adoption templates | 311 | `e0406e3a7a16dc38fa9d8df2e178a86944faf850dc8430d504582bae802681e3` |
| `templates/consumer/container-service/.github/workflows/release.yml` | consumer adoption templates | 804 | `256153ee27df626ab3a3bff20df4db2e27d9921a2179ad9a1ff31cabbcf18656` |
| `templates/consumer/container-service/.l9/deployment.yaml` | consumer adoption templates | 1492 | `49f3cc0fbd13ff52f91ea0622b9b4b0e9c10918a7fb388ba0bc031f8b6b79835` |
| `templates/consumer/scheduled-job/.github/workflows/release.yml` | consumer adoption templates | 804 | `256153ee27df626ab3a3bff20df4db2e27d9921a2179ad9a1ff31cabbcf18656` |
| `templates/consumer/scheduled-job/.l9/deployment.yaml` | consumer adoption templates | 1458 | `7d19a73b0041989ccb331efe1c582cd820c9d1d33c4dc24c41bfeec72aac6a42` |
| `templates/consumer/stateful-container/.github/workflows/release.yml` | consumer adoption templates | 804 | `256153ee27df626ab3a3bff20df4db2e27d9921a2179ad9a1ff31cabbcf18656` |
| `templates/consumer/stateful-container/.l9/deployment.yaml` | consumer adoption templates | 2156 | `f461aa4eccf32e25c8290771022c35547ab34be9957737673363d8ae1f577ebe` |
| `templates/consumer/worker-service/.github/workflows/release.yml` | consumer adoption templates | 804 | `256153ee27df626ab3a3bff20df4db2e27d9921a2179ad9a1ff31cabbcf18656` |
| `templates/consumer/worker-service/.l9/deployment.yaml` | consumer adoption templates | 1473 | `6c34b1156f9ead76a69fbad202617a89430e89d893b0e39450b91baea8472765` |
| `tests/compliance/test_coverage_policy.py` | behavioral, contract, security, and regression tests | 1362 | `23efd8ecd148e3f0c89b4ac9e0b71d0730f1e14f57c0af4ef2e22f00e875d0a8` |
| `tests/compliance/test_l9_alignment.py` | behavioral, contract, security, and regression tests | 2707 | `20f505f1742bb4c45f64a3ce06da5983c2d950320546cbd4408449d88ad23fec` |
| `tests/compliance/test_pack_hardening.py` | behavioral, contract, security, and regression tests | 5478 | `484957ff965259d6b4db5ede2da8dbe9cdab3641035b7dad22722d1d6e426be1` |
| `tests/compliance/test_release_archive.py` | behavioral, contract, security, and regression tests | 6829 | `5e67791888d085f8db232e3441c93c621953c50d844df36c85f84d5ad9576777` |
| `tests/conftest.py` | behavioral, contract, security, and regression tests | 8669 | `6cc9ffa6dcb39a3f1a8c75f1149706c93cce8dfc881b18bd2a2c8818c8ec8e78` |
| `tests/contract/test_alias_policy.py` | behavioral, contract, security, and regression tests | 1868 | `1a155af50cbdc1336aee0027ce1d8ad365dd28cc977358b42d42161b8a829179` |
| `tests/contract/test_schemas.py` | behavioral, contract, security, and regression tests | 2823 | `44ad7b3b853921bdeeec682aba4362206d4fac93e33d0bfdc0e35221453b02d3` |
| `tests/contract/test_wire_aliases.py` | behavioral, contract, security, and regression tests | 8189 | `39d901fe1faba10008c1758b5161710617a88e3985a585a23d2e581b7f1a977b` |
| `tests/infrastructure/test_structure.py` | behavioral, contract, security, and regression tests | 1265 | `e7ab953b813ef5fe3725330bf89e1794cff9e4ab919fb1dc5e385037aea75bb8` |
| `tests/integration/test_adoption_templates.py` | behavioral, contract, security, and regression tests | 1494 | `40681529ebbe8ece989c84cd083c4143b6303c1a8f901c980e2a6253279c4cfa` |
| `tests/integration/test_execution_engine.py` | behavioral, contract, security, and regression tests | 11940 | `9e9bbbcb90f26e410921234d7efb2b4c8a0416ac2992c232bdc3b250cab9939e` |
| `tests/integration/test_promotion_request.py` | behavioral, contract, security, and regression tests | 3251 | `8e87831f6ac9bef4b4ad9ec6fe384bd1c20e329576bc21714b47ae57a4da4aa9` |
| `tests/security/test_approval.py` | behavioral, contract, security, and regression tests | 3385 | `a84f96f377e118816021a99e9903c89e46205f1b15a6878e6c92c7d4fd3e2f66` |
| `tests/security/test_redaction.py` | behavioral, contract, security, and regression tests | 1263 | `afef5d6ff3f1fadfa1ccf66467ae1c4414b02cd6b5a9e51623519598373a87ac` |
| `tests/unit/test_boundary_components.py` | behavioral, contract, security, and regression tests | 9891 | `113cf31a9565b1747e8457e436405ea6a1fec272b7421dec9314b3bef099d9af` |
| `tests/unit/test_canonical.py` | behavioral, contract, security, and regression tests | 1346 | `bbccbec2c377eb13925e0d6326a2dfe7da5a8ac6f5bcfb284ee75134cac7ca2b` |
| `tests/unit/test_cli_surface.py` | behavioral, contract, security, and regression tests | 4978 | `b90f26d7895712074b4a3e33fd0704dda0a6dadfd038c2cfdc21d31e29900765` |
| `tests/unit/test_compose_and_images.py` | behavioral, contract, security, and regression tests | 1183 | `f6b73bd5cfb5b5cb4421ec0c0bb1146c4a500b4e9b016a14ea8101f1e69e486c` |
| `tests/unit/test_contract_primitives.py` | behavioral, contract, security, and regression tests | 2233 | `557dc782e89adc028dfe33d4888097e1d50df5aac38452a0eff10da033cc8223` |
| `tests/unit/test_idempotency_and_locks.py` | behavioral, contract, security, and regression tests | 4728 | `e91d9173296cbaa0115ff7335dcbb80876df139f67863aa9485991607c216d47` |
| `tests/unit/test_inventory_and_logging.py` | behavioral, contract, security, and regression tests | 3230 | `2e3ad98453f2b82f0d292bb24480839c9296d0c61fb4cc1869eb03bca139b5f5` |
| `tests/unit/test_planning.py` | behavioral, contract, security, and regression tests | 1664 | `9e5e2f96ee3e30898b4b6d7ad8285ceaea20b743b3d65e76fded374a64b40543` |
| `tests/unit/test_receipt_ledger.py` | behavioral, contract, security, and regression tests | 2236 | `d633ba5e4c91fafc91417e2e8146617b5487173884be279ebc11ecb3d57ce859` |
| `tests/unit/test_requests.py` | behavioral, contract, security, and regression tests | 4093 | `6d871ad1c8a7c7b2ec57408ccf5eace99cbbb3160fa59ad085715336875ea14e` |
| `tests/workflows/test_workflows.py` | behavioral, contract, security, and regression tests | 2697 | `a881eafcd31e6b47484eb702cc65188f24fbf8cc65db2f9a1f3b67b51b55ece1` |
| `uv.lock` | repository governance, packaging, or operator entrypoint | 62342 | `5afe87d097fd674d19647ac885197415adc0a1fccee4b325e9283475f8672289` |
| `validation/evidence/final/alignment.txt` | machine-readable validation evidence | 38 | `794d5a9ace67033420582e5b077ab640f62e01d6a1fac9ba8ae67a5e0ef25e2c` |
| `validation/evidence/final/archive-validation-model.txt` | machine-readable validation evidence | 302 | `302d8d879d8b09c8224770c22f1a2c3f1fb915782c81b0d29c9997b64a03c3ba` |
| `validation/evidence/final/baseline-summary.txt` | machine-readable validation evidence | 197 | `c4b002e91a678562d9676801ab8cccd0ca4b7af4895273638ca50e6271635b1e` |
| `validation/evidence/final/cli-help.txt` | machine-readable validation evidence | 718 | `eed439bf5a1dc14d27495ac955242439c58dd9f23987cfd53ff99648b3559020` |
| `validation/evidence/final/contracts.txt` | machine-readable validation evidence | 47 | `1d76c28d69a09478cb463d703b4311f0dc27e5c4ca5bea5cb82c5b95a4af0ef0` |
| `validation/evidence/final/fast-contract-scan.txt` | machine-readable validation evidence | 81 | `f5dc6264a372323d7e85bd1af3f199257d875f57ff72cc2dc11d6525cc5ade1b` |
| `validation/evidence/final/line-length.txt` | machine-readable validation evidence | 51 | `3d10498de7e1f53c61bd3378dc7c95154839d4321efc6053d729910b1fcba8c3` |
| `validation/evidence/final/metadata.txt` | machine-readable validation evidence | 50 | `c588e40651b82fb915b707228ac600ce33ad1233e21d9c1c27231c178f7ed730` |
| `validation/evidence/final/module-imports.txt` | machine-readable validation evidence | 28 | `5407fc62c1ab8df040e6a41ce7900a98d345b1c12e5648cc2291a9eed60dd0e3` |
| `validation/evidence/final/no-stub-placeholder.txt` | machine-readable validation evidence | 104 | `287fefe0f3df50018e280e0ff959ebcf2fce4a06c6c09b65497e780f09451e31` |
| `validation/evidence/final/post-fix-summary.txt` | machine-readable validation evidence | 334 | `9e6cf28d2bf6b3be471f0942a2d95007a3eca7b893275e0cbe48403faafe2a21` |
| `validation/evidence/final/pytest.txt` | machine-readable validation evidence | 4369 | `0700c3b3c0c3ab14e182114e004b236c1d5c8f196ad98ab221de7aa7e99c3018` |
| `validation/evidence/final/python-compile.txt` | machine-readable validation evidence | 42 | `ebbebeab99c82659d6afc44e42ce660c36e1363444afc954fba63296ff5894dc` |
| `validation/evidence/final/release-behavior-tests.txt` | machine-readable validation evidence | 99 | `89e499bf23aedf3cba845f7fa473cc85bd929028682fd65ec7806f593c57ea28` |
| `validation/evidence/final/shell-syntax.txt` | machine-readable validation evidence | 55 | `693947e263f34dde21d34b7860dd76cdf23201ddb100941ee5f0bc00de74c9c9` |
| `validation/evidence/final/structured-parse.txt` | machine-readable validation evidence | 35 | `26f30dfe93899dfe343ad252c8fe7241fd9af728ee10d15f3e67433a4012d207` |
| `validation/evidence/final/tool-availability.txt` | machine-readable validation evidence | 285 | `cce245ffd13ea466732db3ade1f86dde2ad62b6795d89d3ec046d7a647ecedab` |
| `validation/evidence/final/uv-build.txt` | machine-readable validation evidence | 334 | `069fb139047a1f02c46a1db1a8d41e2a72311b79db21bb3f13b7224ece2d6176` |
| `validation/evidence/final/uv-lock-check.txt` | machine-readable validation evidence | 189 | `bef9d9e89d0fb08703a368c10db604ae4137cc0b6db0fbb4dcff2348a33d4dda` |
| `validation/evidence/final/workflows.txt` | machine-readable validation evidence | 34 | `20d3bb28bffab1e4eeca5d14ed4b16ae5b1274917e48ed17c38b3775d84ecacf` |
| `validation/validation_checks.jsonl` | machine-readable validation evidence | 8465 | `b99a78446a7b7ef99f6c3875c52de715eaa729de704dd21aa6d21512e4fc68ef` |
| `validation/validation_findings.jsonl` | machine-readable validation evidence | 10293 | `32a4219d5dd7eda381f04683ec88a0643b18ea14460c78757aac3ea790754b88` |
| `validation/validation_report.yaml` | machine-readable validation evidence | 2393 | `a003dd226cd166b889f278df7f5aa70db47ee5c2d6d0ea2e13d9fda94b1e1a94` |

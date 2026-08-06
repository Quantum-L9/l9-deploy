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
- Manifested files: **390**
- Manifested bytes: **910810**

`MANIFEST.json`, `MANIFEST.md`, and `checksums.sha256` are excluded from the JSON 
manifest to avoid self-referential hashes. The checksum index covers both manifest files.

## Responsibility map

| Path family | Responsibility | Files |
|---|---|---:|
| `.github/` | GitHub governance and workflow orchestration | 17 |
| `.l9/` | L9 ownership, policy, compatibility, and integration contracts | 19 |
| `src/` | deployment control-plane implementation | 58 |
| `schemas/` | versioned public JSON contracts | 21 |
| `scripts/` | operator, validation, and release tooling | 24 |
| `tests/` | behavioral, contract, security, and regression tests | 28 |
| `validation/` | machine-readable validation evidence | 29 |
| `infrastructure/` | OpenTofu infrastructure desired state | 39 |
| `ansible/` | host configuration and conformance | 42 |
| `deployment/` | runtime profiles, policies, probes, and templates | 18 |
| `fleet/` | fleet desired state and environment registration | 6 |
| `integrations/` | cross-repository integration projections | 17 |
| `templates/` | consumer adoption templates | 9 |
| `docs/` | architecture, operations, security, and consumer guidance | 26 |

## File inventory

| Path | Responsibility | Bytes | SHA-256 |
|---|---|---:|---|
| `.editorconfig` | repository governance, packaging, or operator entrypoint | 202 | `6297da6b1169de32dca2f6184b4eaa63a8bb6c7e1c66c20d6e813166256e3856` |
| `.github/CODEOWNERS` | GitHub governance and workflow orchestration | 576 | `e6ae145e3ab95fe530a9fe6ad9d83a4febbe91dd4c61079876c1723af25c07d3` |
| `.github/actions/collect-approval/action.yml` | GitHub governance and workflow orchestration | 2028 | `e2e23ce7478c72033e1a33d0d55613c095ed36243a8b088971d63a2ff8114a7d` |
| `.github/dependabot.yml` | GitHub governance and workflow orchestration | 479 | `735f2414437271c24e3a49441419d4cad28fcc41a9bf5d2eb52be9733389cb5c` |
| `.github/pull_request_template.md` | GitHub governance and workflow orchestration | 665 | `169fd0342bb137c69c97777da86a48df87109497b2a8a1f51e53f9944ae1bc6c` |
| `.github/workflows/backup-verify.yml` | GitHub governance and workflow orchestration | 1201 | `b6325d74c648141c5f21a0a6194a63b432f2b7673a738be1ba13654b55c5fba7` |
| `.github/workflows/configure-hosts.yml` | GitHub governance and workflow orchestration | 3123 | `9e06882e4ff8febe2fb126d89c8847c5b31338206877351801d4547327e0d703` |
| `.github/workflows/deploy-dispatch.yml` | GitHub governance and workflow orchestration | 6691 | `551549fd551f2c28bf5300448d0385b238670988174e277050188d0d32fdc438` |
| `.github/workflows/deploy-manual.yml` | GitHub governance and workflow orchestration | 1383 | `88bc0e8c96789088d39322e9ed084e4753f6fb0eb1137bbf22b219f6b573e086` |
| `.github/workflows/drift-detect.yml` | GitHub governance and workflow orchestration | 2566 | `7303aafe2735d1573f5cbec7fef41f77f9eae92161aa38bcb44c211dc019ea0b` |
| `.github/workflows/fleet-conformance.yml` | GitHub governance and workflow orchestration | 1096 | `8f8008f586fd01d4fd986ec19d57f53ccbb85f55b05eabb6d1cd93f2501510dc` |
| `.github/workflows/promote.yml` | GitHub governance and workflow orchestration | 2380 | `37c911a02c779312058827f8ddca13deacc994667e06085e520c35c0b960f329` |
| `.github/workflows/provision-apply.yml` | GitHub governance and workflow orchestration | 3948 | `7de3239a3470719f4f465835e68c02e13eedd0c32dca837f86e9b89880f262d0` |
| `.github/workflows/provision-plan.yml` | GitHub governance and workflow orchestration | 2644 | `78d6d1436d21b6618407279e3c40251533399e9b899b578357fa471f6ef48908` |
| `.github/workflows/release.yml` | GitHub governance and workflow orchestration | 2339 | `75543d09228ec66c0f16d8ebda825a5f9383faf8476bac734207e39bd483c473` |
| `.github/workflows/rollback.yml` | GitHub governance and workflow orchestration | 2958 | `5a215beb1f480e1845422a5b096f2a9bc9bc6489da4ac789226ac4a057781ca8` |
| `.github/workflows/runner-maintenance.yml` | GitHub governance and workflow orchestration | 3171 | `45c4f724443dec30e162df7804a6d2b7032343da4d02123a2f9076b489121de5` |
| `.github/workflows/validate.yml` | GitHub governance and workflow orchestration | 1952 | `1ef8a449065bceae0d4f6ac8ba5ff563a7738f95c5680b7e4b742256d9c8ee66` |
| `.gitignore` | repository governance, packaging, or operator entrypoint | 306 | `64465eebb11dd91c5ceac877eeadf3ecd0ed609045e061a7912fb4df5504ec68` |
| `.l9/architecture.yaml` | L9 ownership, policy, compatibility, and integration contracts | 664 | `705e8c84e2fd29a285b8e8972e1f5decc0a973e1263631d0f90eb86423222266` |
| `.l9/compatibility.yaml` | L9 ownership, policy, compatibility, and integration contracts | 890 | `cfa1a3c5a11559f8a4544180cb640a78704783d2501bf977df21b35309c8185a` |
| `.l9/governance-provider.yaml` | L9 ownership, policy, compatibility, and integration contracts | 757 | `98b0728d0eca1e2dcc5162e56e3f1df22efdcec86278ee7e52a3773fc84cacaf` |
| `.l9/integration-contracts/assurance.contract.yaml` | L9 ownership, policy, compatibility, and integration contracts | 447 | `5a017cc766e8d8934766277996eab5b3ed589a900bf0b6f86178156fb10d88cd` |
| `.l9/integration-contracts/ci-core.contract.yaml` | L9 ownership, policy, compatibility, and integration contracts | 483 | `d78643300b7376b5850086de1ae1c1ea965f503b776f6d0c5602425063148316` |
| `.l9/integration-contracts/ci-sdk.contract.yaml` | L9 ownership, policy, compatibility, and integration contracts | 462 | `beb6e09f8856b860a0fc2183b510f8c0f9c973bd1fa7cff474bdcc859a2a6e05` |
| `.l9/integration-contracts/consumer.contract.yaml` | L9 ownership, policy, compatibility, and integration contracts | 568 | `50a00a4671074a414da9a195d80cba0b0782ee412204e9e90d61353c170208d9` |
| `.l9/integration-contracts/ghcr.contract.yaml` | L9 ownership, policy, compatibility, and integration contracts | 401 | `fa1713852d84cf1b1c20d5f7c6b6e3f15d6f5660e0ff99d659ecef4f1fd674df` |
| `.l9/integration-contracts/github-org.contract.yaml` | L9 ownership, policy, compatibility, and integration contracts | 456 | `ba43272f5cee03a45065287c2795e845f4c8a8471b72f8ae24cee204a2d1a8b2` |
| `.l9/integration-contracts/hetzner.contract.yaml` | L9 ownership, policy, compatibility, and integration contracts | 428 | `efdae9773d9665785ec359cd51f70e18ba0ca230172d6aef8fd824c994e2f72d` |
| `.l9/integration-contracts/infisical.contract.yaml` | L9 ownership, policy, compatibility, and integration contracts | 402 | `50564bfabe7ef6cbf999304d6d7714261fe4e457da153c9f51baf92c8fa75094` |
| `.l9/integration-contracts/repo-template.contract.yaml` | L9 ownership, policy, compatibility, and integration contracts | 458 | `b3c5e22471a31f7070eb8ca28502cdf8d5379554d2cd722cc45a1df07217c5bb` |
| `.l9/metadata-exclusions.yaml` | L9 ownership, policy, compatibility, and integration contracts | 1342 | `17155d67c6b8ff59c51de6ddc4e4496876e36a6ba927d5ad58ba8bcd225c07aa` |
| `.l9/ownership.yaml` | L9 ownership, policy, compatibility, and integration contracts | 721 | `2546f0b2febe2e948d439b6465e315e118629ccde28e4ec08212362db37570c4` |
| `.l9/policies/l9-deployment-contracts.yml` | L9 ownership, policy, compatibility, and integration contracts | 2269 | `e9801e314228a9e771472a6af2ed0bef30504593b5aa0b8b79e9e2e3120b2e2e` |
| `.l9/release-policy.yaml` | L9 ownership, policy, compatibility, and integration contracts | 448 | `c616ba614f8794e1c012ba9ef37b07c0c1d9b6b7eb2bdf908463a4c46505b918` |
| `.l9/repo-spec.yaml` | L9 ownership, policy, compatibility, and integration contracts | 5908 | `935d320f4fd50279e8581161822d5206cbf6a18816efb682d8cefa14d70f1082` |
| `.l9/tool-stack.yaml` | L9 ownership, policy, compatibility, and integration contracts | 409 | `33efce1f905c31d37fbd0cf214766b4cf5e8f8a5eb3407d72b72ae39e8a1ce49` |
| `.l9/transport-classification.yaml` | L9 ownership, policy, compatibility, and integration contracts | 1044 | `7d0a4e3d685c7186f79e30f54a32d5bbefe9cb7569f715d61f55cf3f16b665c7` |
| `.pre-commit-config.yaml` | repository governance, packaging, or operator entrypoint | 1099 | `29326f094af5f45dacd6040015c8ea8da7e3e694f254bcc1803b8609ba9073da` |
| `.python-version` | repository governance, packaging, or operator entrypoint | 5 | `7b55f8e67b5623c4bef3fa691288da9437d79d3aba156de48d481db32ac7d16d` |
| `ARCHITECTURE.md` | repository governance, packaging, or operator entrypoint | 8875 | `82c07447413f514eacd3f2b1ee3970e497cc170e55ad48f9b4201cad2a9445f1` |
| `CHANGELOG.md` | repository governance, packaging, or operator entrypoint | 5375 | `f2d1eaf91d55e9deca2b8867cebc96b18ca72b218caa8a4f102efad6f91c8a6b` |
| `CHANGE_SUMMARY.md` | repository governance, packaging, or operator entrypoint | 3303 | `4b8c8609fb33c513a4bcd5a16922ca1be6ddc1c17ff9dc16d7974820bf52d9d6` |
| `CONTRIBUTING.md` | repository governance, packaging, or operator entrypoint | 1927 | `f2d38831fd762effe0b025579d768e9ce7e0b4373b09ed41868e1a71d8fdc64f` |
| `CONVERGENCE_REPORT.yaml` | repository governance, packaging, or operator entrypoint | 1283 | `4595a29ef5ecf825e3e550ef765863578e2c78254ab6f99791ad5d51447f18ad` |
| `DELTA_REPORT.md` | repository governance, packaging, or operator entrypoint | 1894 | `c935caf56f22f4da77393fce2d3f2b8a4e465faf5927d262e75619841f1f439e` |
| `FINAL_TREE.md` | repository governance, packaging, or operator entrypoint | 19515 | `bf4921a2f8cdd4f85d1f2c95e935841a0970da6945bed6a26ad86853443b4f7b` |
| `GAP_DEFECT_MATRIX.yaml` | repository governance, packaging, or operator entrypoint | 6285 | `646785cc6d95308273a2b30d53b922f1a9f0a457d0415c09b78f3b96a1644a82` |
| `Makefile` | repository governance, packaging, or operator entrypoint | 2496 | `8262d94a9373439fd92afd4e91666271d446f611aa52db72bae6daf1e62a65a8` |
| `README.md` | repository governance, packaging, or operator entrypoint | 7825 | `e34358c5b7b65b94a1f27c022216de506affbe962359f305847a3ac210169b11` |
| `REGRESSION_GUARD.md` | repository governance, packaging, or operator entrypoint | 4812 | `ee7e150ecb39f08de4e79277445ed6dcfa9c8e676ab4ffe6c241aeb639439dac` |
| `REMEDIATION_REPORT.md` | repository governance, packaging, or operator entrypoint | 2612 | `9336b7d64fe230b4ff56f298dd06a703a27649f53667dee6df68b65c9c3d270f` |
| `RUNBOOK.md` | repository governance, packaging, or operator entrypoint | 9541 | `8f81c97c0e62f43c46fa579c8a2f9e87a685c9c77726b07e93afa7dca00eaa9c` |
| `SECURITY.md` | repository governance, packaging, or operator entrypoint | 5810 | `5ae5d1132a6ed11316aefd8e4bbe87f777f75d9ab3ae0b70f87a89f1688cf1e7` |
| `SPECIFICATION.md` | repository governance, packaging, or operator entrypoint | 63012 | `d22967cd5a0a0a217420341b638f51dc91ad6551a2d31915cbbda741e99429b7` |
| `TRACEABILITY_MAP.yaml` | repository governance, packaging, or operator entrypoint | 5436 | `64c06ecdc6af2042e9cd42cf37e14c0a9178697d8cf7284d2850c1b57bb4691e` |
| `UNKNOWN_REGISTER.md` | repository governance, packaging, or operator entrypoint | 1927 | `461da7ab836744033835f67c69b635b781a70bfedc6d6ca6109624d5ecf08ec0` |
| `VALIDATION.md` | repository governance, packaging, or operator entrypoint | 4778 | `8b9189c4b81f481fd9246c560c3372c5a81718f39a67155ddad6bce52d3a91bc` |
| `ansible/ansible.cfg` | host configuration and conformance | 533 | `46c5542c6ef7e1346b733502a694ff534650d1517af917a7df708412802d918f` |
| `ansible/inventories/group_vars/all.yml` | host configuration and conformance | 577 | `4b886e398302b6037f40c03a4ddacaf188e17080d2360e13e442ee73e21d98f5` |
| `ansible/playbooks/bootstrap.yml` | host configuration and conformance | 301 | `5ebe0c669779af4febbade9ec8b5136d9a9c3c06bbd3d55d00c84ba64cddebbe` |
| `ansible/playbooks/configure-backups.yml` | host configuration and conformance | 290 | `cedb7209cd9f3c0320ed9a5563517bd8ee07762b3648dbd13dea5e9e7fbc2819` |
| `ansible/playbooks/configure-memory.yml` | host configuration and conformance | 314 | `37a51f32bdd135e0f378bcae75193e051daf46dad4caabf606806bfca5c9eb0f` |
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
| `ansible/roles/redis/defaults/main.yml` | host configuration and conformance | 1891 | `2bea57a43164ec7878a172eef4bf0e2dac7e141de39247c0b81cfe050e888317` |
| `ansible/roles/redis/handlers/main.yml` | host configuration and conformance | 291 | `c23f01a12a85a4972c2e9a9eaf1b703849a80cd5e813abfd0cde9cdffdb7ff51` |
| `ansible/roles/redis/tasks/main.yml` | host configuration and conformance | 1936 | `2387d867c512148b735b44e5e7e458476556ec412754b186e0ebe3ea924cf8ae` |
| `ansible/roles/redis/templates/redis.conf.j2` | host configuration and conformance | 998 | `ebcc930176aedcaa0f7ce4b210bf5e45262da93f30b4e55688dd45d90331dd0a` |
| `ansible/roles/redis/templates/users.acl.j2` | host configuration and conformance | 867 | `8a71c5497ab4e304a1eb14f747375fd9787e64dcf9185861f906538570d7b0df` |
| `ansible/roles/runner_tooling/tasks/main.yml` | host configuration and conformance | 2309 | `c8d8a4fcc1cf5f1e528458cc4de986376c0379f20856fa9bc0f70f8ed943ef27` |
| `ansible/roles/sqlite_backup/files/l9-sqlite-backup` | host configuration and conformance | 862 | `5a7edb8b5cdc9872853540705a9646c1bc45c9c7e0912ad2233e726c08fe8c46` |
| `ansible/roles/sqlite_backup/files/l9-sqlite-restore-test` | host configuration and conformance | 728 | `b05f87d2215ff90fbb60884165c0518486bb70d86ba8fc240daf12e4c7983484` |
| `ansible/roles/sqlite_backup/files/l9-sqlite-verify` | host configuration and conformance | 595 | `5435d9f145a1f94714d2aa90261e30e8c890d31779aed72970ceb6dc9d396d15` |
| `ansible/roles/sqlite_backup/tasks/main.yml` | host configuration and conformance | 982 | `1a4eba300a3101834f6103bfd5544270ce4245a93b9a6fb544ea983129135881` |
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
| `docs/agents/deployment-agent.md` | architecture, operations, security, and consumer guidance | 5095 | `4e1c3146f0fde3c8d2dda111495f41a45fce623171fc149b6679f7e7cf578f8e` |
| `docs/architecture/control-plane-boundaries.md` | architecture, operations, security, and consumer guidance | 1124 | `2a94e64468f18414b8102f6fe0baed7bf51485339e8db29a00cf3a2634bd1762` |
| `docs/architecture/evidence-model.md` | architecture, operations, security, and consumer guidance | 881 | `796d3c2cf5db060e8e96cecef06987c42e52ac277c36a916ec29247654b03da9` |
| `docs/architecture/network-topology.md` | architecture, operations, security, and consumer guidance | 865 | `a7972c2ddd74515b52a182e6d349b52fb30af70a9d981db0270662337a164648` |
| `docs/architecture/release-transaction.md` | architecture, operations, security, and consumer guidance | 1571 | `c1569979b41c0340068cb1137f50aef52eb03ccba6d596bbf4ac97c81b639feb` |
| `docs/consumers/adoption.md` | architecture, operations, security, and consumer guidance | 524 | `2a58be0c3217d761ef9f11ca36a505eb956d438ac24718d9793299412636048b` |
| `docs/consumers/profile-authoring.md` | architecture, operations, security, and consumer guidance | 671 | `0707b65fdb0139bbfbd4eba3d2cd38080213b1229b0748022cd6d80e5dde20a4` |
| `docs/operations/fleet-conformance.md` | architecture, operations, security, and consumer guidance | 562 | `98460754876dad253e8c3da4d1bbb09d8b3a338e33497ca2354062cb26f4cb19` |
| `docs/operations/repository-identity.md` | architecture, operations, security, and consumer guidance | 2291 | `11ae25e517c743188485daf04febe1f2d3390dc41a6c4e3b74623b43f01fa566` |
| `docs/operations/workflow-inventory.md` | architecture, operations, security, and consumer guidance | 3917 | `42deb4e34fa9ba36f25a7be226f6ebb1116b62eaef750c8b9554a9d5f30510d0` |
| `docs/runbooks/bootstrap-management-runner.md` | architecture, operations, security, and consumer guidance | 665 | `ec31fe2205bd3068e6e7f9283c516695ef6b107c5b91ea75b3a9a8bcfead8fa0` |
| `docs/runbooks/deploy.md` | architecture, operations, security, and consumer guidance | 585 | `343c3eec7c6437de919438abcb7a80f46822d10fa8f1deed8191b742769b675d` |
| `docs/runbooks/incident.md` | architecture, operations, security, and consumer guidance | 588 | `ae8b3943db100b1225c4e96d8b09a0f642145a26e4583f7d43870811a143f2bc` |
| `docs/runbooks/onboard-consumer.md` | architecture, operations, security, and consumer guidance | 630 | `3c09aa24874844efb357c6b9880eca4589916db7eabb0234f4c5d296ac8705e9` |
| `docs/runbooks/provision-environment.md` | architecture, operations, security, and consumer guidance | 598 | `64705e9eab3dcdc9d897bda225e0dcc7928e70b5cd71f269cac9729f2f7032eb` |
| `docs/runbooks/restore.md` | architecture, operations, security, and consumer guidance | 564 | `d6f68a95bfa7859b9c5616b083710796dbfc33a6c539ebc0a05655ddb366fe23` |
| `docs/runbooks/rollback.md` | architecture, operations, security, and consumer guidance | 1695 | `613a53b80f7df80598f086b69912b2f0d71169ba99e26c40a616ba78f71e36c4` |
| `docs/runbooks/rotate-runner.md` | architecture, operations, security, and consumer guidance | 572 | `8e2581d8ad70d3f878de20de303ae7b396e23a09083cb6c6999719392c4ae50d` |
| `docs/security/threat-model.md` | architecture, operations, security, and consumer guidance | 724 | `7cd65f8d0080ddf1e71b33ee6fb514a6f29d4abe72f593a9378f9c3945a4ab16` |
| `fleet/desired-state/README.md` | fleet desired state and environment registration | 346 | `2590bf72b726bdc3f16e9ab6e6cbde998719270e2725d9646fd42f16dc084de1` |
| `fleet/environments/management.yaml` | fleet desired state and environment registration | 303 | `27c210b6b2f1b5bb1cfa1b547af94c21d1944864289f9cf94b785b7ecc8fe958` |
| `fleet/environments/production.yaml` | fleet desired state and environment registration | 326 | `41765249bcdd73c6ba23fb819b1947bca39c206cc14c20e119520ba0b1367b25` |
| `fleet/environments/staging.yaml` | fleet desired state and environment registration | 324 | `8b36796c28196210130ca27cadef37c5825c7bbb712755b2046bc76dfe0684e1` |
| `fleet/projects/README.md` | fleet desired state and environment registration | 354 | `0f353af6f86c264e4967abdc5dd85dc80e11ec547eaaa8ed0685de6d5d48da8f` |
| `fleet/registry.yaml` | fleet desired state and environment registration | 3509 | `0941983d558a5f5d104b2c5b6159b150b4d211d9d2689e2802f78367c01b6638` |
| `infrastructure/opentofu/backend.example.hcl` | OpenTofu infrastructure desired state | 524 | `103dd1f5969c1d93e00bf0b90c55341dfad03a1548c77499b3cd809ce91aeba2` |
| `infrastructure/opentofu/environments/management/backend.tf` | OpenTofu infrastructure desired state | 220 | `4e812a939c4b324cced2939feab7d8419afd0f87839d1d1c4dc50f0a8dab4060` |
| `infrastructure/opentofu/environments/management/main.tf` | OpenTofu infrastructure desired state | 1665 | `c11a2b12beb3b79565947b92b224b0d8c6e66d59f70da95cd03fe1b148c67d95` |
| `infrastructure/opentofu/environments/management/outputs.tf` | OpenTofu infrastructure desired state | 414 | `843e3326d150679c4cf29e41df42dc92938ac66108724d28c8388d54769c5eb9` |
| `infrastructure/opentofu/environments/management/variables.tf` | OpenTofu infrastructure desired state | 600 | `f6f2cbe2e86eb96d2ac45b00968af93d7b1994e32ada35c27bd2e35100274c1b` |
| `infrastructure/opentofu/environments/management/versions.tf` | OpenTofu infrastructure desired state | 355 | `29bd759c367aa54dbc7ad622e02e9c6cbbbd430c66401ed3dcd65a0d7d16daff` |
| `infrastructure/opentofu/environments/production/backend.tf` | OpenTofu infrastructure desired state | 220 | `4e812a939c4b324cced2939feab7d8419afd0f87839d1d1c4dc50f0a8dab4060` |
| `infrastructure/opentofu/environments/production/main.tf` | OpenTofu infrastructure desired state | 1534 | `e3c32a1f4e90a56d9ec48f1f620f01c75205994a66da7563ca034b753430ef90` |
| `infrastructure/opentofu/environments/production/outputs.tf` | OpenTofu infrastructure desired state | 326 | `ddaddab006be5102ccf170207ef52a5a9ac9652fe766fa1da3d1984e87e36353` |
| `infrastructure/opentofu/environments/production/variables.tf` | OpenTofu infrastructure desired state | 603 | `c2b2b51a10312e99645091d64ad3397d30bbd8e7631d4978f295532c6d1caae6` |
| `infrastructure/opentofu/environments/production/versions.tf` | OpenTofu infrastructure desired state | 355 | `29bd759c367aa54dbc7ad622e02e9c6cbbbd430c66401ed3dcd65a0d7d16daff` |
| `infrastructure/opentofu/environments/staging/backend.tf` | OpenTofu infrastructure desired state | 220 | `4e812a939c4b324cced2939feab7d8419afd0f87839d1d1c4dc50f0a8dab4060` |
| `infrastructure/opentofu/environments/staging/main.tf` | OpenTofu infrastructure desired state | 1525 | `ea31461e9ae47f371d256e86e3222fac5c924e29c9bdb7b57606838aa7fa20d9` |
| `infrastructure/opentofu/environments/staging/outputs.tf` | OpenTofu infrastructure desired state | 326 | `ddaddab006be5102ccf170207ef52a5a9ac9652fe766fa1da3d1984e87e36353` |
| `infrastructure/opentofu/environments/staging/variables.tf` | OpenTofu infrastructure desired state | 603 | `c2b2b51a10312e99645091d64ad3397d30bbd8e7631d4978f295532c6d1caae6` |
| `infrastructure/opentofu/environments/staging/versions.tf` | OpenTofu infrastructure desired state | 355 | `29bd759c367aa54dbc7ad622e02e9c6cbbbd430c66401ed3dcd65a0d7d16daff` |
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
| `integrations/consumers/graphiti-memory.deployment.yaml` | cross-repository integration projections | 2926 | `b1909859365bee5e8c1c1887f1dd38c1f590c8bf3ca43494daccac8f88c02ace` |
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
| `integrations/l9-ci-core/container-release.yml` | cross-repository integration projections | 11547 | `a8ccbd989be471bb1792ca6255e97404c83d2c273e37cebe21c09dffda23de26` |
| `integrations/l9-ci-sdk/README.md` | cross-repository integration projections | 345 | `6494ab9ae035682ab76fad51649fd49abed8a1d4c95a7676ecbb66aa70cf2796` |
| `integrations/l9-repo-template/README.md` | cross-repository integration projections | 354 | `795db4b37684e77546d33b548b4c7c96c8ac28c6d95573930491a47ecce1422c` |
| `memory-bank/activeContext.md` | repository governance, packaging, or operator entrypoint | 260 | `ff4eb88fd898cd824c6bbe6550897b76e162ac3c33f3cf505767f5283115e974` |
| `memory-bank/progress.md` | repository governance, packaging, or operator entrypoint | 196 | `56c34f21fef51e2c50fa478798b4d29ed28c561f979f98f0e6ba50d9df42362f` |
| `memory-bank/tasks.md` | repository governance, packaging, or operator entrypoint | 187 | `8aca501737a24e2f7f75e8d6a132d1e6d77d0a42ab94efca31e2435a9114d0ed` |
| `memory-bank/tech-debt.md` | repository governance, packaging, or operator entrypoint | 203 | `cd770a5b6c6f71563b7d22c33f129c879a5093717828a0ee9ae92780f7131c4c` |
| `pyproject.toml` | repository governance, packaging, or operator entrypoint | 1529 | `07a40726ae6d72f262fc6b273e05fd2a5df426c4f53902adb8893bd554473c6e` |
| `release-work/handoffs/l9-provisioning-handoff/PREFLIGHT_CHECKLIST.md` | repository governance, packaging, or operator entrypoint | 2945 | `9f996793eb4293d31481efa43bf78e7e6480d3126f818d038e6dd32e7a4e4844` |
| `release-work/handoffs/l9-provisioning-handoff/README.md` | repository governance, packaging, or operator entrypoint | 2880 | `be8a8ed0299dcf224d34e119d459220520db4ba7a62b25088496b31cbec12047` |
| `release-work/handoffs/l9-provisioning-handoff/RUNBOOK.md` | repository governance, packaging, or operator entrypoint | 7310 | `953211c6c7c23398285f614e6fc5d12d1656692562217c7d65391e06fd130562` |
| `release-work/handoffs/l9-provisioning-handoff/config-changes/CONFIG_CHANGES.md` | repository governance, packaging, or operator entrypoint | 1563 | `761829986510df6c4b91211cc5853895adf61caf2077eda33e1788f4c7f7e21f` |
| `release-work/handoffs/l9-provisioning-handoff/graphiti-image/Dockerfile` | repository governance, packaging, or operator entrypoint | 1601 | `4fded1358d398022c087dfbafc5bd1ff20589ccba66c7c7e154db73f87aa53e0` |
| `release-work/handoffs/l9-provisioning-handoff/graphiti-image/README.md` | repository governance, packaging, or operator entrypoint | 1574 | `24c1446b53b6d7bc362d90b69411f627251177eef76506911c099b7c58101c7d` |
| `release-work/handoffs/l9-provisioning-handoff/graphiti-image/publish-image.yml` | repository governance, packaging, or operator entrypoint | 1716 | `b779ee9463c6fd34e5a929ca73f096f47e760d18930282037ae43814d3382ffa` |
| `release-work/handoffs/l9-provisioning-handoff/secrets/.env.example` | repository governance, packaging, or operator entrypoint | 821 | `7f0bc1f8096a1e45d4c64604db7091d6bbf1380c8afe63362c6af34e761e22b6` |
| `release-work/handoffs/l9-provisioning-handoff/secrets/REQUIRED_SECRETS.md` | repository governance, packaging, or operator entrypoint | 2239 | `54f9dcbcb7372005893fe204d6570b2b6239881043f0c69f655ac11ec340a5c8` |
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
| `schemas/v1/runtime-state.schema.json` | versioned public JSON contracts | 2142 | `7402db61b679af8e69e31d1aeb4c7c67cb8a910241497b73560adb90e5f4b4e9` |
| `schemas/v1/server-profile.schema.json` | versioned public JSON contracts | 2226 | `7e367e95778f961d70743ddee4becac38ee74a4c48b3fb251895af2641d273bf` |
| `scripts/_bootstrap.py` | operator, validation, and release tooling | 1451 | `a6456e5251bc7ef6978b8e3b25db9cd7ee1ff9abd1a9cdc540b5e91432a9eafc` |
| `scripts/bootstrap-runner.sh` | operator, validation, and release tooling | 620 | `00489a4cd6a69cbf10a2ba604a27188b274d3549525ced09a3afa75c6fdb88b1` |
| `scripts/bootstrap-state.sh` | operator, validation, and release tooling | 1116 | `2a6943c7e9bab8fc533d3e4b785879afd41f1de92b691b7526dae327cc45d413` |
| `scripts/break-glass-access.sh` | operator, validation, and release tooling | 642 | `d4f37ea6e5a10e82c8ab9bc2987912730276711926a3befd34b8ec6a1a1b142b` |
| `scripts/build-release-archive.py` | operator, validation, and release tooling | 6707 | `e4cff1e9a3c577cf13321e9919db5ef8262db942ac6caa6fce15fc83459d0190` |
| `scripts/collect-github-approval.py` | operator, validation, and release tooling | 4473 | `fdeb2e1782390120953796e1b0e076a750af04ddfe9e91959863fc29aa3a0de9` |
| `scripts/fast-contract-scan.py` | operator, validation, and release tooling | 6791 | `d8278277612f2b915c24db280e41a7a0b5b51234dd9fcc363f9c4b93241d3643` |
| `scripts/generate-inventory.py` | operator, validation, and release tooling | 1239 | `aa857eb8c5fd52d4db41d2cfe7c011ced547e228277cb718407d55a17dd1ccc4` |
| `scripts/generate-release-artifacts.py` | operator, validation, and release tooling | 7839 | `19a73558554e04040879e67dfac72e772888790ffe1befaa62f3d004185ec16c` |
| `scripts/infisical-oidc-env.sh` | operator, validation, and release tooling | 4019 | `94995f5d3b467fa39b8e2a6c670b55b39465ede154df5999fe4f1a9dcf5f7c6d` |
| `scripts/inject-l9-meta.py` | operator, validation, and release tooling | 4782 | `1ab9df1dcf53b0d6c45a52f26c9e5d19be1040c2ba9aed5185b8c3d9ff8c5532` |
| `scripts/install-opentofu.sh` | operator, validation, and release tooling | 670 | `00def39fd1531058d04e813456e23b32073649e4a0d01a5e9c478aa6015f9c1f` |
| `scripts/package-adoption-kit.py` | operator, validation, and release tooling | 1217 | `00384e6f7b795e9112b578f7689c06eef5826cf5e1e913e5ca20f057338b0d57` |
| `scripts/prepare-deployment.py` | operator, validation, and release tooling | 3357 | `49e589243444154f0d4ecdca5586a8ac018a7e64d11b85cbf5d61722e0c5bb0d` |
| `scripts/promote-request.py` | operator, validation, and release tooling | 2549 | `6140c646654c0c2e5bdabf0b1fbecdb3dcd62ae10c0ed52d3c112cbbc5481b7f` |
| `scripts/rotate-runner.sh` | operator, validation, and release tooling | 628 | `35afd2970c46ae0c36c7e09398a9580a9de597d2f6157b9e4fa41187ef170b7c` |
| `scripts/run-l9-contract-gates.sh` | operator, validation, and release tooling | 1046 | `f2e6432ac6dfd0b6e40066f774cf18b73ef46afcdc2204e279f859541e0547aa` |
| `scripts/validate-alignment.py` | operator, validation, and release tooling | 7404 | `703209e5c8d3d7024f82e0700674ccbc7e82e2164a93d3dcdc0fec0c33cb4e14` |
| `scripts/validate-contracts.py` | operator, validation, and release tooling | 4723 | `d4d4a1eabe2f8fe96d5695b27aa4c130a33ed7e55da9b5b2765be00eb74609aa` |
| `scripts/validate-opentofu.sh` | operator, validation, and release tooling | 871 | `862b6bfd5aa370f438c81cef6861edf8ae840ca90f19d4c4e7a47c7c5f4bd2e6` |
| `scripts/validate-release-pack.py` | operator, validation, and release tooling | 12133 | `a690918a4c440cbd75e5567b68cedcb4caa96bd6fdaba2bfae92d27f88f60531` |
| `scripts/validate-workflows.py` | operator, validation, and release tooling | 8077 | `429537253d104f0bf476641a1fe28798c6e415bb277fb61e7d4fefb50cd0e3d8` |
| `scripts/verify-attestation.sh` | operator, validation, and release tooling | 642 | `3efe7fadf713378ae6febfa375804c866d7ef91baa6d7c8f192527ccce5cfb63` |
| `scripts/verify-l9-meta.py` | operator, validation, and release tooling | 789 | `2531af52e952edb0147d233dfcdd249efb571135b03d73eccb9b84704d46b6ac` |
| `src/l9_deploy/__init__.py` | deployment control-plane implementation | 197 | `b147f3a2fcac2ac67402d79fce72bea15693227519a0f61b5a1bd05324401d9a` |
| `src/l9_deploy/__main__.py` | deployment control-plane implementation | 254 | `1195c369846a92179344ac88db15a6272e59c791fee03382ace645a203435e7e` |
| `src/l9_deploy/canonical.py` | deployment control-plane implementation | 1850 | `3311a46d9bb2ba8e9514c336d5c4edd0366c3cfc22865df8f2a05ea489319fa7` |
| `src/l9_deploy/cli.py` | deployment control-plane implementation | 31835 | `b5cde04689876138b1e028ef71dd0f7c2f40d5a3f58690340816671181c9b8e5` |
| `src/l9_deploy/contracts/__init__.py` | deployment control-plane implementation | 174 | `38cd74064a41cdc13a425a20d9f350e4d9cb396b57397b9bb9f19e7c9339abd8` |
| `src/l9_deploy/contracts/alias_policy.py` | deployment control-plane implementation | 2965 | `c21e72f97c3577d386ca269725c9631cb2eb7942abe10f07c546cf24f5f98daf` |
| `src/l9_deploy/contracts/catalog.py` | deployment control-plane implementation | 3072 | `514c819629d8c74cc688cdd10602e63b936f92e4c186c0624cec8d76586c1654` |
| `src/l9_deploy/contracts/compatibility.py` | deployment control-plane implementation | 781 | `35295c85b122e9b3d6b869325ab594327a5ed6dd4f4e7413c6eb289bc27e34cb` |
| `src/l9_deploy/contracts/loader.py` | deployment control-plane implementation | 616 | `cbe16de940bcaeccd0034f98b00d70149c02d11cec66666f292b8bf788934f62` |
| `src/l9_deploy/contracts/models.py` | deployment control-plane implementation | 15208 | `c03d1dbca357c20d5798c18a6dab2a1063ba2745b0c8f9d47dd12c04afd93305` |
| `src/l9_deploy/contracts/validator.py` | deployment control-plane implementation | 3716 | `193833dd9f7c6ab9e8d2dbbbe7db6144c17e01b1c667cf87883361b3d17db849` |
| `src/l9_deploy/errors.py` | deployment control-plane implementation | 561 | `888566ecc102386605d86ae8b6b86dea193927ae03c8026c1b48de8ffdc8411a` |
| `src/l9_deploy/evidence/__init__.py` | deployment control-plane implementation | 174 | `38cd74064a41cdc13a425a20d9f350e4d9cb396b57397b9bb9f19e7c9339abd8` |
| `src/l9_deploy/evidence/approval.py` | deployment control-plane implementation | 4857 | `ed6afea2c476df981ec276709f6c9808198b36f8a83afd038b5e3910c82709ec` |
| `src/l9_deploy/evidence/ci.py` | deployment control-plane implementation | 6594 | `3b465d2a8ca6615252ecffc192532aba47d847d702cd80626e0e7d0049fc9f6c` |
| `src/l9_deploy/evidence/digests.py` | deployment control-plane implementation | 270 | `afd0ee3c65a1af7c27d92b6e67fbabffaf960c207031e03ab9a2d4b92c465410` |
| `src/l9_deploy/evidence/ledger.py` | deployment control-plane implementation | 8946 | `4608294466d557fcb02c3bb45fbb86e7dbe7588636e0c47f764a4220280ddc33` |
| `src/l9_deploy/evidence/publisher.py` | deployment control-plane implementation | 1189 | `01b7034eed64e2a374409c4a48ff10f95eafbb30f0ff220287a2c4a4c57f8e33` |
| `src/l9_deploy/evidence/receipts.py` | deployment control-plane implementation | 3695 | `d0bd41fd2f38314a64b044b05690aab366d6dce6c02e62bbf0705589f60e56ce` |
| `src/l9_deploy/evidence/records.py` | deployment control-plane implementation | 1141 | `8d630cceef65fa4cc018a4f5b9d1242a369191fbd50623f3731d47c86d0bf8ee` |
| `src/l9_deploy/execution/__init__.py` | deployment control-plane implementation | 174 | `38cd74064a41cdc13a425a20d9f350e4d9cb396b57397b9bb9f19e7c9339abd8` |
| `src/l9_deploy/execution/backups.py` | deployment control-plane implementation | 2999 | `e2c3efe2730c021786b234138bfdb944da22ee2c495f9aa01324fdf5bad4b32d` |
| `src/l9_deploy/execution/compose.py` | deployment control-plane implementation | 2388 | `cbce7df16ede037af0ff0a0249c4580dc312e126e64e16222cc578b71cc73f23` |
| `src/l9_deploy/execution/engine.py` | deployment control-plane implementation | 16350 | `322c26ee6477482425d18a2ba4b3c1e86e9fa2fa307e33ddb46d5785dc0a7b5e` |
| `src/l9_deploy/execution/health.py` | deployment control-plane implementation | 2740 | `cb1167b0e462d5d04d15f16ffee9b27de3ce5585369c63c8e3e76e01656ad932` |
| `src/l9_deploy/execution/images.py` | deployment control-plane implementation | 1323 | `28a64a3276f6ca14ba85865e8653f24dbb875e435afe6ecc941c42e48d81e417` |
| `src/l9_deploy/execution/locks.py` | deployment control-plane implementation | 1011 | `ce15b405e8dfd501abc9f12cfbb6a0755f53af16bf77a7b97bb583c4d987111c` |
| `src/l9_deploy/execution/migrations.py` | deployment control-plane implementation | 1276 | `d58a2e0e1bfaac62ac4edf0552c35c6900daaf4b35594e3e7fa3a4ceb14b31cf` |
| `src/l9_deploy/execution/promotion.py` | deployment control-plane implementation | 2044 | `8c974b5fe1ec82fd8f887850eacb8d43e78c660a26ae6c1822121ec58521d993` |
| `src/l9_deploy/execution/releases.py` | deployment control-plane implementation | 5296 | `02b87c622b5a3fd9b0bcbba7eb50022b1b7f9c4c0eefb52c5760a0d63261b652` |
| `src/l9_deploy/execution/remote.py` | deployment control-plane implementation | 3654 | `42f582d0210f5512fe546ea0de1859cdf05923d3547d3457b1f1c0f606b2da7b` |
| `src/l9_deploy/execution/rollback.py` | deployment control-plane implementation | 2626 | `85def6fbef4d94c089c2c1a1a296f5935295641bd12714bb33f59a14bbc85de0` |
| `src/l9_deploy/integrations/__init__.py` | deployment control-plane implementation | 174 | `38cd74064a41cdc13a425a20d9f350e4d9cb396b57397b9bb9f19e7c9339abd8` |
| `src/l9_deploy/integrations/ansible.py` | deployment control-plane implementation | 1070 | `b26ccf075b01f35259f83135a98087bb8bc2482b85d3098ba2487cfc71595a32` |
| `src/l9_deploy/integrations/ghcr.py` | deployment control-plane implementation | 597 | `49d6c390f363e8eb82aa0c5dad8139d8f2a3fe7f02c63e3790fe0f2ecec75aa4` |
| `src/l9_deploy/integrations/github.py` | deployment control-plane implementation | 1272 | `1012b0ab3467a5b59ef31f6d3a690b640f60240d250c1f10eba9b18e0e491c61` |
| `src/l9_deploy/integrations/hetzner.py` | deployment control-plane implementation | 592 | `241114b3bc9f31fe4b2e407b15d2f2a928428bdf20d8350a40a13e9bc9a107b3` |
| `src/l9_deploy/integrations/infisical.py` | deployment control-plane implementation | 2338 | `9b8ab1b5e6c8caf33b6d9c9463afe62f41aa00816ba43be36c70707fe6b39b5f` |
| `src/l9_deploy/integrations/opentofu.py` | deployment control-plane implementation | 3043 | `a5472533556658ee158751b419f94e63341019b26eb075b33a3a245a6a08e8fc` |
| `src/l9_deploy/inventory/__init__.py` | deployment control-plane implementation | 174 | `38cd74064a41cdc13a425a20d9f350e4d9cb396b57397b9bb9f19e7c9339abd8` |
| `src/l9_deploy/inventory/generator.py` | deployment control-plane implementation | 1177 | `e42a272dad5ddcfb025a7fafb703e5d352adbcfc01a18abe3ee0e53fde32df13` |
| `src/l9_deploy/inventory/loader.py` | deployment control-plane implementation | 627 | `954931c5d1f2ad15cd0b06e0a2453069a24440a5b043e5d5a2c11ed351103aa1` |
| `src/l9_deploy/inventory/resolver.py` | deployment control-plane implementation | 1505 | `48504c210c49229860665f84f13a540e490670e126edc77abf7e313e14050429` |
| `src/l9_deploy/logging.py` | deployment control-plane implementation | 1101 | `8b4aaea52e7420a136e193a017c33da7d504a6fc563fab5a17e189eb1277858a` |
| `src/l9_deploy/planning/__init__.py` | deployment control-plane implementation | 174 | `38cd74064a41cdc13a425a20d9f350e4d9cb396b57397b9bb9f19e7c9339abd8` |
| `src/l9_deploy/planning/backups.py` | deployment control-plane implementation | 899 | `5adb98e6997ccb3d6ef90903dfa7ccc0b5a9d611e2cb0779ce0f5f41ebbfd85c` |
| `src/l9_deploy/planning/migrations.py` | deployment control-plane implementation | 800 | `25f745492a9e7cdf7a96a095758af239db2dc81484ab5cdd9769d4185d6ae817` |
| `src/l9_deploy/planning/planner.py` | deployment control-plane implementation | 3411 | `7a4a073ede67692ecfbc3fb0c4cf1135e1d72563357bd073415eb97c4f44e164` |
| `src/l9_deploy/planning/rollback.py` | deployment control-plane implementation | 354 | `ffa4d7fc7ff07faaa232f7c4f9cb25f725cb850939d10e8ac6329602ddd42f8d` |
| `src/l9_deploy/planning/topology.py` | deployment control-plane implementation | 382 | `abad530b7999581c49bfbfcc4ecc29bf94749db80777ad1ea269c6e7f8d5845a` |
| `src/l9_deploy/redaction.py` | deployment control-plane implementation | 1524 | `806ca45d7ac270d34166e640d5ebff762d8c33cd78227e4a69bec576ec901cfa` |
| `src/l9_deploy/release_inventory.py` | deployment control-plane implementation | 1535 | `74aceb290e4149b01dc2553c3a0af73e4d2d1a67056194f8e8aa7861b0b8a7ab` |
| `src/l9_deploy/requests/__init__.py` | deployment control-plane implementation | 174 | `38cd74064a41cdc13a425a20d9f350e4d9cb396b57397b9bb9f19e7c9339abd8` |
| `src/l9_deploy/requests/allowlist.py` | deployment control-plane implementation | 1144 | `a19ceabcdae8e5782a6b114b8740aa98f28b0f3e26e6f6155713c377df3b5fa2` |
| `src/l9_deploy/requests/idempotency.py` | deployment control-plane implementation | 6469 | `3cc3e2db634cb00450fe9d259ff69f7eec4035699c2ccc65730c9639e291410c` |
| `src/l9_deploy/requests/parser.py` | deployment control-plane implementation | 705 | `b55529e497d3e8401075855c5904956032172c7a092386ac95fb9d61d9094da9` |
| `src/l9_deploy/requests/verifier.py` | deployment control-plane implementation | 4068 | `b41e7ee0c7afdb8b928d6caddc34afe3e6719ad2f46294e1d965e7e335e5c123` |
| `src/l9_deploy/subprocesses.py` | deployment control-plane implementation | 2347 | `4abe6fd3246bd683b64d5eb583dda78ee9087b38080850739923246b0993c713` |
| `templates/consumer/common/README.md` | consumer adoption templates | 311 | `e0406e3a7a16dc38fa9d8df2e178a86944faf850dc8430d504582bae802681e3` |
| `templates/consumer/container-service/.github/workflows/release.yml` | consumer adoption templates | 804 | `256153ee27df626ab3a3bff20df4db2e27d9921a2179ad9a1ff31cabbcf18656` |
| `templates/consumer/container-service/.l9/deployment.yaml` | consumer adoption templates | 1492 | `49f3cc0fbd13ff52f91ea0622b9b4b0e9c10918a7fb388ba0bc031f8b6b79835` |
| `templates/consumer/scheduled-job/.github/workflows/release.yml` | consumer adoption templates | 804 | `256153ee27df626ab3a3bff20df4db2e27d9921a2179ad9a1ff31cabbcf18656` |
| `templates/consumer/scheduled-job/.l9/deployment.yaml` | consumer adoption templates | 1458 | `7d19a73b0041989ccb331efe1c582cd820c9d1d33c4dc24c41bfeec72aac6a42` |
| `templates/consumer/stateful-container/.github/workflows/release.yml` | consumer adoption templates | 804 | `256153ee27df626ab3a3bff20df4db2e27d9921a2179ad9a1ff31cabbcf18656` |
| `templates/consumer/stateful-container/.l9/deployment.yaml` | consumer adoption templates | 2156 | `f461aa4eccf32e25c8290771022c35547ab34be9957737673363d8ae1f577ebe` |
| `templates/consumer/worker-service/.github/workflows/release.yml` | consumer adoption templates | 804 | `256153ee27df626ab3a3bff20df4db2e27d9921a2179ad9a1ff31cabbcf18656` |
| `templates/consumer/worker-service/.l9/deployment.yaml` | consumer adoption templates | 1473 | `6c34b1156f9ead76a69fbad202617a89430e89d893b0e39450b91baea8472765` |
| `tests/compliance/test_coverage_policy.py` | behavioral, contract, security, and regression tests | 1363 | `4a79b738a34870f0ae7bd605cb7b8f95e4769b25234fdb621c0d8f0d9648b9eb` |
| `tests/compliance/test_l9_alignment.py` | behavioral, contract, security, and regression tests | 2762 | `21b3f327fdcee849dde9148df9baa2015eb950f9e23a02032896914723dee15f` |
| `tests/compliance/test_pack_hardening.py` | behavioral, contract, security, and regression tests | 5479 | `f7612df962460a75506d2cd70789555b1b0ada15cccb7084863f1dbe781f7911` |
| `tests/compliance/test_release_archive.py` | behavioral, contract, security, and regression tests | 7422 | `f5aa5833bc6cdc5ece05738d416ac6cf349c373a1bdd84dafaebc8bbe01d5ec2` |
| `tests/conftest.py` | behavioral, contract, security, and regression tests | 8670 | `7aac470a58264356fb0e7567593a25e9a32fcb42d6edaa6970de200e9de0d873` |
| `tests/contract/test_alias_policy.py` | behavioral, contract, security, and regression tests | 1869 | `c0d4dbdeb43252614460efb11e4630df628c64f789524cd2e390a4c6e84635b9` |
| `tests/contract/test_schemas.py` | behavioral, contract, security, and regression tests | 2824 | `6ec7d4750d8eb2b1b8ad2337e08a03f2dca6d4edfa61a383b7b002f79c9b6104` |
| `tests/contract/test_wire_aliases.py` | behavioral, contract, security, and regression tests | 8803 | `41816806874dfa64abca94e184d26d14e7ca8cdc1f2eb0c8c5a84a0d1c2d4070` |
| `tests/infrastructure/test_structure.py` | behavioral, contract, security, and regression tests | 1266 | `adf5f04446e12b0ccc164ffb258be071acbea00028d4f639dc87b0ad34f74235` |
| `tests/integration/test_adoption_templates.py` | behavioral, contract, security, and regression tests | 1495 | `4f767a5130d25a87a9cad96a835880c7a99dc87b0c2e92bb96a4a1decd469790` |
| `tests/integration/test_execution_engine.py` | behavioral, contract, security, and regression tests | 18822 | `3604ffbf4ea9dc12a31e1e2f89807213eb5f159659929f9bb493dd020ef433d4` |
| `tests/integration/test_promotion_request.py` | behavioral, contract, security, and regression tests | 3252 | `141cceb0190281c948500343fc4daa01e51ee911f53e5e4b5271e84a696f2c28` |
| `tests/security/test_approval.py` | behavioral, contract, security, and regression tests | 3380 | `c2d954da77ab555574e64f7d0e4c626b8bc21483fbe15e2056310c5c9a8a6154` |
| `tests/security/test_infisical_oidc_env_script.py` | behavioral, contract, security, and regression tests | 5198 | `f1a9ababa395b3cfd488e78ccae61dd3ea3d1026191cc074b4b598de7f2d2b13` |
| `tests/security/test_redaction.py` | behavioral, contract, security, and regression tests | 1264 | `473332b6ef51548e61fb6942c8261afaf7b19ac718f157faee8012bd4ad3ad85` |
| `tests/unit/test_backup_verification.py` | behavioral, contract, security, and regression tests | 2242 | `46a3ad3e586ab3b86647759d70cb4969638d0afeee0a3c102c6f7adabe86efdc` |
| `tests/unit/test_boundary_components.py` | behavioral, contract, security, and regression tests | 9923 | `242c927273db5a9d379fe92d85818a9110e7faa49fa17c55c66c824672f99252` |
| `tests/unit/test_canonical.py` | behavioral, contract, security, and regression tests | 1347 | `b3ebba8af2db86f7b5fb8c945a48a7861a848bb7f8edde3bc298ddc40f5d5805` |
| `tests/unit/test_cli_surface.py` | behavioral, contract, security, and regression tests | 5087 | `2a42e5a86fe79d9aca077276c8eafcc946cbbd5eb49ee8cd3690c9cb611511b1` |
| `tests/unit/test_compose_and_images.py` | behavioral, contract, security, and regression tests | 1299 | `28da32623f8b59ac30692c8d4a86638d226bf15861dd66d24bf00bac98454b31` |
| `tests/unit/test_contract_primitives.py` | behavioral, contract, security, and regression tests | 2234 | `b5e6a85c8e65f0b5d975c98cda316d326f318b0866ea6377880d3d4d566c9994` |
| `tests/unit/test_idempotency_and_locks.py` | behavioral, contract, security, and regression tests | 4729 | `c59196e02fbc6f5cc450562e39fdc69a6865c686f591d0dde7f8ed300766943b` |
| `tests/unit/test_inventory_and_logging.py` | behavioral, contract, security, and regression tests | 3263 | `73e6a27bf0c8b8e9ba9877d8729fee82a66b819ebe804db1219f48b03b980080` |
| `tests/unit/test_planning.py` | behavioral, contract, security, and regression tests | 1659 | `51d25479f2e814414f11edbee3c61cefee3ac5678acfb6ea675b5990c65965b2` |
| `tests/unit/test_receipt_ledger.py` | behavioral, contract, security, and regression tests | 2237 | `cd6bf26ed4f69aa9f6d5dbe2a11bfd668197c1c97ca4c9d0c5cbc4a2fae0c578` |
| `tests/unit/test_release_runtime_state.py` | behavioral, contract, security, and regression tests | 9462 | `a65ef8a453ffa75b3295629f983fe58322ee375861c91db9cd27aa4308b26f39` |
| `tests/unit/test_requests.py` | behavioral, contract, security, and regression tests | 4076 | `951144be70145144be2c7787d1f3a0f508cfa96294f4865ff12a578adaf19ba1` |
| `tests/workflows/test_workflows.py` | behavioral, contract, security, and regression tests | 6057 | `6696b217b8afcc27e3650a565e0bd45a903986fad95f4a4ac60dda215e54bd36` |
| `uv.lock` | repository governance, packaging, or operator entrypoint | 74129 | `54e84a66f5db7d9f944c8b47ab700d86d05ca5a5845aa751bdfeb5f58eef8579` |
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
| `validation/evidence/phase5-environment.txt` | machine-readable validation evidence | 153 | `d97e9bdf862acbee20ad2bcb42dd675aa47ccecdd2abf49dd189e7fc161a4ea5` |
| `validation/evidence/phase5-meta.txt` | machine-readable validation evidence | 50 | `dc41ca862765bf779a7df54880e3b63193bb488cf0113be9e3054ebcda77b85b` |
| `validation/evidence/phase5-pytest.txt` | machine-readable validation evidence | 180 | `fbe08196459b41339375bfb47fe32d00e92bd4bbd841f91654a57e9febd4b51e` |
| `validation/evidence/phase5-release-archive.txt` | machine-readable validation evidence | 394 | `d83e30aceab2128b27b33e97c98910bae4fbac9c48b0d6f223ab252ab0a96596` |
| `validation/evidence/phase5-release-receipt.json` | machine-readable validation evidence | 591 | `4506a8bd7a02c817cbd8a4cfbf6aca0035424a3889575edd985d5a51212df7e7` |
| `validation/evidence/phase5-root-digests.sha256` | machine-readable validation evidence | 317 | `e7ac189b22261cf4cc8444c78fd198ca00ed1de87373b525904d7eea18a1a763` |
| `validation/validation_checks.jsonl` | machine-readable validation evidence | 8465 | `b99a78446a7b7ef99f6c3875c52de715eaa729de704dd21aa6d21512e4fc68ef` |
| `validation/validation_findings.jsonl` | machine-readable validation evidence | 10293 | `32a4219d5dd7eda381f04683ec88a0643b18ea14460c78757aac3ea790754b88` |
| `validation/validation_report.yaml` | machine-readable validation evidence | 2393 | `a003dd226cd166b889f278df7f5aa70db47ee5c2d6d0ea2e13d9fda94b1e1a94` |

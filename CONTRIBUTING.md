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
# Contributing

Changes must preserve the deployment boundary, fail-closed behavior, and reproducible source release.

1. Create a conventional branch and commit.
2. Run `make validate` on the pinned Python 3.12 toolchain.
3. Keep branch coverage at or above 75 percent and run tests with warnings promoted to errors.
4. Update schemas, contract catalog entries, examples, tests, and compatibility metadata together.
5. Preserve established v1 wire keys. The only permitted Pydantic alias is the cataloged
   `schema_id` to `schema` identity mapping in canonical contract DTOs.
6. Prove wire round-trip behavior, alias-aware JSON Schema parity, and warning-free model import.
7. Keep typed contract logic typed. Do not reintroduce dictionary fallbacks after validation.
8. Give each CLI output path one owner. A handler that writes `--output` must prevent the generic
   emitter from replacing that artifact.
9. Include rollback impact for workflow, infrastructure, runner, schema, security, migration, and
   deployment-engine changes.
10. Never reference reusable interfaces at `@main`; use a compatible major tag and record the
    resolved SHA.
11. Regenerate manifests and checksums only after the final source change.
12. Build Python distributions, the repository archive, and its detached receipt outside the source
    root. Validate the exact archive and receipt before publication.
13. Require two reviews for `.github/workflows`, `schemas`, `infrastructure`,
    `ansible/roles/github_runner`, `src/l9_deploy/execution`, and security-sensitive paths.

No pull request may weaken digest enforcement, runner isolation, approval requirements, receipt
persistence, redaction, coverage, contract parity, source-release binding, or database rollback
separation.

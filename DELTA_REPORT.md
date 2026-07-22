<!-- L9_META
l9_schema: 1
origin: l9-deployment-platform
layer: [repository, validation]
tags: [L9_META, deployment-platform, delta-report]
owner: platform
status: active
/L9_META -->
# Before and After Delta

| Area | Baseline | Final 0.1.5 source |
|---|---|---|
| Pydantic import | 9 namespace warnings | 0 warnings, warnings fail tests |
| Wire identity | Python and wire both used `schema` | Python `schema_id`, wire `schema` |
| Published schemas | 18 | 20 |
| Tests | 54 passed, 9 warnings | 103 passed, 0 warnings |
| Branch coverage | Not enforced | 79.45 percent measured, 75 percent floor |
| Idempotency | Weak transition validation | Typed legal state machine and immutable completion |
| Canonical JSON | Accepted NaN and infinity | Rejects non-finite values |
| Release provenance | Archive and validation could diverge | Detached source-manifest and archive receipt |
| Tagged release path | Outputs could enter source root | All outputs use runner-temporary storage |
| Release residue | Coverage and build outputs not fully governed | Explicitly rejected and cleaned |
| Release tooling | Direct execution could create bytecode residue | Self-cleans bytecode before inventory and validation |
| Backup planning | Typed storage treated as a dictionary | Typed persistent-volume policy access |
| Inventory CLI | Summary could overwrite inventory | Single output owner, private mode retained |
| GitHub guard | Missing context passed | Missing or wrong context fails closed |
| Infisical export | Key and duplicate injection gaps | Strict key, uniqueness, CR/LF, and NUL validation |
| Timeout cleanup | Possible open descendants and pipes | Process group terminated and pipes drained |
| Evidence records | Could skip schema validation | Redacted, digested, schema-validated records |
| Source archive | Folder snapshot | Deterministic single-root ZIP with exact parity gate |

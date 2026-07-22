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
## Summary

## Change class

- [ ] Contract or schema
- [ ] Infrastructure
- [ ] Host configuration
- [ ] Deployment engine
- [ ] Workflow or integration
- [ ] Documentation

## Proof

- [ ] `make validate` passes
- [ ] No mutable image reference introduced
- [ ] No public workflow can reach the deployment runner
- [ ] Rollback behavior reviewed
- [ ] Migration and backup impact reviewed
- [ ] Receipt and redaction behavior preserved
- [ ] Exact compatibility ref used, never `@main`

## Rollback plan

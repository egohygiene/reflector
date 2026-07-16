# Publication Workflow

1. Define publication metadata in `metadata/` and `VERSION`
2. Synchronize derived surfaces with `scripts/sync-version.py`
3. Validate metadata with `scripts/validate-metadata.py`
4. Author and refine the paper in `paper/`
5. Lint and build the PDF locally or in CI
6. Publish the site and artifact through Pages or release workflows

## Recommended loop

```bash
task metadata:check
task paper:lint
task paper:build
```

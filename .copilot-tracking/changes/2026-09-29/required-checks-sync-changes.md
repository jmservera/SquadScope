# Required checks sync changes

Date: 2026-09-29
Task ID: required-checks-sync

## Changes

- Added `workflow_dispatch` to `ci.yml`, `lint.yml`, `checkov.yml`, `security-scanning.yml`, and `squad-ci.yml`.
- Granted `actions: write` to the generated publish sync job so it can dispatch required checks.
- Added explicit dispatch of required workflows on `sync/publish-to-main` after the sync branch push.
- Replaced generic check registration polling with exact required GitHub Actions check-run name polling on the sync branch head SHA.

## Validation

- `python3` YAML parse over workflow files: passed.
- `git diff --check`: passed.

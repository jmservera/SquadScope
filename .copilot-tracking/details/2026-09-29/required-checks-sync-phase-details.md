# Required checks sync phase details

Task ID: required-checks-sync
Date: 2026-09-29

## P01 Context

The target workflows already expose stable job names and have no pull-request-only payload references. The sync workflow creates the branch and PR from `GITHUB_TOKEN`, so dispatch must happen after the push and before merge waiting.

## P01 Completion Expectations

- Required workflows include `workflow_dispatch` without changing existing push or pull_request behavior.
- Sync job has `actions: write` plus existing content and PR permissions.
- Sync job dispatches `ci.yml`, `lint.yml`, `checkov.yml`, `security-scanning.yml`, and `squad-ci.yml` on `sync/publish-to-main`.
- Sync job polls commit check-runs for GitHub Actions app ID `15368` and refuses to continue if any required context is absent.

## P02 Context

Repository instructions require branch/PR workflow and review-thread resolution before merge.

## P02 Completion Expectations

- Local parse/diff checks pass.
- PR is open against `main`, checks are green, Copilot review is complete, and unresolved threads are addressed.
- PR merges via squash and branch deletion.

## P03 Context

Ruleset enforcement must wait until the merged default-branch workflows support manual dispatch. The safe verification path is a throwaway branch, not running publish/sync in a way that could publish content or force-push `main`.

## P03 Completion Expectations

- Throwaway branch exists at a known SHA.
- Manual dispatches create the exact required check-run names on that SHA.
- Prepared ruleset body is sanitized to `bypass_actors: []` before PUT.
- Outcome is recorded in coordinator issue and Squad state.

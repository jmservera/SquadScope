# Required checks sync implementation plan

Task ID: required-checks-sync
Date: 2026-09-29

## Executive Summary

Enable `main` required checks without blocking the weekly generated publish sync by making required workflows manually dispatchable and having the sync workflow dispatch them on the generated branch before attempting auto-merge. Apply the repository ruleset only after PR merge and end-to-end check-run verification.

## User Decisions and Requirements

- Required checks must be enforceable on `jmservera/SquadScope` `main`.
- The weekly publish sync PR must not block forever because it is created by `GITHUB_TOKEN`.
- Preferred approach: explicit `workflow_dispatch` of required workflows from `sync-publish-to-main.yml` after pushing the sync branch.
- Keep least privilege, pinned actions, and no untrusted interpolation in `run:`.
- Do not create secrets; consider a GitHub App token only if a suitable secret already exists.
- Verify exact check-run contexts on a SHA before applying ruleset `16532660`.
- Remove the invalid GitHub Actions bypass actor from the prepared ruleset body before applying it.

## Goals

- Required GitHub Actions check contexts appear on generated sync PR head SHAs.
- Sync workflow refuses to merge unless all intended required contexts register.
- Ruleset update is applied only after verification.

## Scope and Non-Goals

In scope: `.github/workflows/ci.yml`, `lint.yml`, `checkov.yml`, `security-scanning.yml`, `squad-ci.yml`, `sync-publish-to-main.yml`, PR validation, ruleset application, coordinator issue/state updates.

Out of scope: changing publish content, force-pushing `main`, creating GitHub App secrets, weakening required checks, or modifying unrelated workflows.

## Functional Requirements

- Add `workflow_dispatch` triggers to each required workflow.
- Add `actions: write` only to the sync job that dispatches checks.
- Dispatch required workflows on `sync/publish-to-main` after push.
- Confirm exact required check names from GitHub Actions app (`15368`) register on the generated head SHA before auto-merge.

## Non-Functional Requirements

- Preserve pinned actions and existing job names.
- Keep shell logic fail-fast and explicit.
- Avoid unsafe event payload assumptions under `workflow_dispatch`.

## Acceptance Criteria

- PR checks pass and review threads are resolved.
- Manual workflow dispatch on a throwaway branch confirms the required check-run contexts on the branch SHA.
- Ruleset `16532660` is updated with `bypass_actors: []` and the prepared code scanning rule only after verification.
- Coordinator issue `jmservera/SquadScope-Coordinator#38` and Squad decision state record the outcome.

## Phase Checklist

### P01 — Implement workflow dispatch and sync guard

- P01-T01 Add `workflow_dispatch` to required workflows.
- P01-T02 Add `actions: write` and explicit workflow dispatch calls to the sync workflow.
- P01-T03 Replace generic check registration polling with exact required-context polling.

### P02 — PR validation and merge

- P02-T01 Run local workflow syntax/diff checks.
- P02-T02 Push branch, open PR, wait for CI and Copilot review.
- P02-T03 Resolve review threads and merge with squash.

### P03 — End-to-end verification and ruleset

- P03-T01 Dispatch required workflows on a safe throwaway branch.
- P03-T02 Confirm exact check-run names on the throwaway SHA.
- P03-T03 Apply ruleset only if verification succeeds.
- P03-T04 Update coordinator issue and Squad decision state.

## Critique Disposition

No separate critique findings. The plan is narrow, evidence-backed, and follows the user-provided implementation direction.

## Follow-Up Items

- Watch the next scheduled weekly sync after the ruleset is active.

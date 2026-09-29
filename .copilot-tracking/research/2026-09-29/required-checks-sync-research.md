# Required checks sync research

Date: 2026-09-29
Task: Make required status checks enforceable on `jmservera/SquadScope` `main` without blocking the generated publish sync PR.

## Brief

The weekly publish sync workflow creates `sync/publish-to-main` PRs with `GITHUB_TOKEN`, then enables auto-merge. PRs authored by `GITHUB_TOKEN` do not trigger `pull_request` workflows, so branch protection/ruleset required checks would never appear unless the workflow triggers them explicitly or uses another credential. Personal-account rulesets cannot add GitHub Actions as a bypass actor, so bypass is not viable.

## Evidence

- C1: `.github/workflows/sync-publish-to-main.yml` uses `GITHUB_TOKEN`, force-pushes `sync/publish-to-main`, creates/updates a PR, waits for checks, then enables auto-merge.
- C2: `.github/workflows/ci.yml`, `lint.yml`, `checkov.yml`, `security-scanning.yml`, and `squad-ci.yml` contained `push`/`pull_request` triggers but no `workflow_dispatch` trigger.
- C3: Required check job names in the workflows are `Python`, `Lockfile`, `Publish hydration parity`, `Production site build`, `Production site (Axe and responsive browser gates)`, `Production site (Lighthouse gates)`, `Production site (Visual structure gate)`, `Ruff`, `Checkov IaC/container scan`, `Bandit Python security scan`, `GitHub Actions Security Scan (zizmor)`, and `test`.
- C4: Search found no `github.event.pull_request.*` references in the target required workflows; references were limited to unrelated `site-preview.yml`.

## Alternatives evaluated

1. GitHub App token: cleaner event model, but no suitable existing app secret was identified in scope and the request forbids creating secrets.
2. Ruleset bypass actor: unavailable for this personal-account repository; API rejects adding GitHub Actions as a bypass actor.
3. Explicit workflow dispatch from sync branch: least-privilege and works with `GITHUB_TOKEN` once target workflows support `workflow_dispatch`; check runs attach to the sync branch head SHA and can satisfy required status checks.

## Recommendation

Add `workflow_dispatch` to the required workflows and grant only `actions: write` to the sync job so it can dispatch those workflows on `sync/publish-to-main` after pushing. Replace the existing generic "some checks registered" guard with an exact required-check registration guard against GitHub Actions app check runs on the sync head SHA.

## Planning readiness

Ready for implementation. No user clarification needed.

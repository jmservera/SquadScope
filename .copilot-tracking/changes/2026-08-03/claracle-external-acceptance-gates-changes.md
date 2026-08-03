<!-- markdownlint-disable-file -->
# Changes Log: Claracle External Acceptance Gates

## Related Plan

`.copilot-tracking/plans/2026-08-03/claracle-external-acceptance-gates-plan.instructions.md`

## Implementation Date

2026-08-03

## Summary

Retained current-main and credential-free public-production acceptance evidence,
linked it from the owning relaunch package, and preserved every human and protected
environment authority boundary. No side-effecting workflow was dispatched.

## Added

* `.copilot-tracking/research/2026-08-03/claracle-external-acceptance-gates-research.md`
* `.copilot-tracking/research/subagents/2026-08-03/claracle-production-acceptance-gates-research.md`
* `.copilot-tracking/research/subagents/2026-08-03/claracle-protected-acceptance-gates-research.md`
* `.copilot-tracking/plans/2026-08-03/claracle-external-acceptance-gates-plan.instructions.md`
* `.copilot-tracking/details/2026-08-03/claracle-external-acceptance-gates-details.md`
* `.copilot-tracking/plans/logs/2026-08-03/claracle-external-acceptance-gates-log.md`
* `.copilot-tracking/changes/2026-08-03/claracle-external-acceptance-gates-changes.md`
* `docs/review/data-observatory-relaunch/automated-acceptance-evidence-2026-08-03.md`

## Modified

* `docs/review/data-observatory-relaunch/README.md`
* `docs/review/data-observatory-relaunch/owner-action-register.md`
* `docs/review/data-observatory-relaunch/status-of-record.md`

## Validation

* Public production: robots, sitemap, root feed, weekly feed, and topic feed returned expected responses and parsed successfully
* Public production: five representative page classes had complete consistent social metadata and valid page-specific JSON-LD
* Focused security, lifecycle, embed privacy, and export controls: 147 passed, 5 skipped
* Focused publication, hydration, workflow, and Podcaster contracts: 108 passed, 26 subtests passed
* Internal-link checker tests: 5 passed
* Full pytest: 1,401 passed, 19 skipped, 2 expected warnings, 34 subtests passed
* Ruff lint and format: passed; 144 files already formatted
* Editor diagnostics and `git diff --check`: passed
* Current-main CI, production site, hydration parity, security scanning, CodeQL, and Checkov: passed
* Rollout flags: both remain disabled

## Remaining Work

* jmservera and Hermes retain live denied and granted analytics observations
* jmservera records GSC processing and numeric baseline conclusions
* Amy or a named reviewer records external metadata validators and visual acceptance
* Fry and a named accessibility reviewer complete keyboard and screen-reader review
* Hermes, URL, and jmservera record security and production-owner dispositions
* Repository administrator and Podcaster owners establish and execute one protected real run
* Sponsor records separate decisions for both rollout flags
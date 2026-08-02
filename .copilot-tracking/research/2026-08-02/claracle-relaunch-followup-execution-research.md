<!-- markdownlint-disable-file -->
# Research: Claracle Relaunch Follow-Up Execution

## Scope

Execute all four follow-up items from the relaunch reconciliation: publish review corrections, complete repository-side GA4/GSC work, close executable acceptance evidence gaps, and plan gated rollouts plus incremental cost measurement.

## Source Research

* .copilot-tracking/research/subagents/2026-08-02/claracle-ga4-gsc-followup-research.md
* .copilot-tracking/research/subagents/2026-08-02/claracle-acceptance-gates-followup-research.md
* .copilot-tracking/research/subagents/2026-08-02/claracle-rollout-cost-followup-research.md

## Verified Findings

* Review correction commit `8fddceb` is pushed to PR #647 and both review threads are resolved.
* Production renders GA configuration, the `GA_MEASUREMENT_ID` secret name exists, and the sitemap returns HTTP 200 with `application/xml`.
* Production does not render GSC verification metadata and no `GSC_SITE_VERIFICATION` secret name exists.
* Repository-side GA4/GSC wiring, consent gating, GSC metadata rendering, workflow injection, and tests already exist. Google account verification and baseline capture require jmservera.
* Focused acceptance research passed 102 security tests plus 42 UX/lifecycle tests; six Hugo-dependent tests skipped locally.
* Real Podcaster generation and environment-bound smoke evidence exist separately. No run combines real generation with a protected environment, and `podcaster-release-smoke` has no protection rules.
* Issue #622 explicitly classifies its work as non-blocking polish. Issue #626 is independent hardening and forbids lowering quality thresholds.
* Both rollout flags remain disabled. Repository activation lacks stable production GitHub IDs and lifecycle-transition evidence. Dynamic activation has five eligible candidates and no useful preview-only dry run.
* Hugo and Pagefind timing are already separated in CI, but Q-01 lacks workload variants, retained comparable samples, aggregation, and an approved budget.

## Selected Approach

1. Preserve the pushed review correction and verify PR checks.
2. Correct GA4/GSC evidence to distinguish fork-safe checked-in defaults from observed production configuration.
3. Refresh the acceptance package with current automated evidence and implementation dispositions without granting human sign-off.
4. Create implementation-ready owner checklists for external acceptance, protected real Podcaster execution, rollout canaries, and report-only cost measurement.
5. Keep both rollout flags disabled and do not trigger external side effects.

## External Boundaries

* Google property inspection, GSC token retrieval, ownership verification, sitemap submission, Realtime confirmation, and baseline values require jmservera or delegated Google access.
* Environment protection configuration requires repository administration and named reviewer policy.
* Real podcast generation requires Podcaster maintainer authorization because duplicate suppression is not evidenced in this repository.
* Manual keyboard, screen-reader, visual, security, and sponsor conclusions require named human reviewers.

## Validation

* Focused Python tests for workflow mapping, links, security, lifecycle, and exports
* Public presence-only production probes that do not print identifiers or tokens
* GitHub PR status checks and environment metadata
* Documentation diagnostics, stale-claim scans, and `git diff --check`

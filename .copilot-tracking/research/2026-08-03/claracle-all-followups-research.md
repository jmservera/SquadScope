<!-- markdownlint-disable-file -->
# Claracle All Follow-Ups Research

## Scope

Continue all five Suggested Next Work items from the 2026-08-03 external
acceptance review:

1. Complete executable preparation for human acceptance reviews.
2. Prove atomic publishing in an isolated environment.
3. Protect real Podcaster generation and prepare one authorized run.
4. Implement the report-only build cost experiment.
5. Resolve the executable #622 UX and #626 Lighthouse hardening work.

## Evidence

* `.copilot-tracking/research/subagents/2026-08-03/claracle-atomic-proof-research.md`
* `.copilot-tracking/research/subagents/2026-08-03/claracle-podcaster-protection-research.md`
* `.copilot-tracking/research/subagents/2026-08-03/claracle-cost-experiment-research.md`
* `.copilot-tracking/research/subagents/2026-08-03/claracle-ux-lighthouse-research.md`
* Existing acceptance and rollout plans under `.copilot-tracking/plans/2026-08-02/`

## Selected Approach

* Add a read-only atomic proof workflow that executes the production commit step
  against a temporary local bare remote and retains a five-scenario matrix.
* Make real Podcaster generation manual-only, exact-manifest, merged-article, and
  environment-bound; remove automatic real generation from publish sync.
* Add a manual read-only Hugo/Pagefind cost experiment with immutable SHAs,
  isolated cumulative variants, retained raw samples, and report-only aggregation.
* Fix the Star Velocity clipping with a stable dataset-wide absolute-star scale,
  add mobile consent geometry coverage, extend lean CSS bundling, add Brotli,
  document Lighthouse methodology, target the observed font-swap CLS source, and
  add bounded per-page Lighthouse concurrency.
* Prepare exact reviewer handoffs, but do not grant security, accessibility,
  visual, production, or sponsor approval.

## Authority Boundaries

* Do not dispatch publication, cost, or Podcaster workflows during implementation.
* Do not configure GitHub environment reviewers or secrets through source code.
* Do not mark the protected Podcaster gate complete until an approved real run and
  downstream conclusion exist.
* Do not promote historical generated topic state to `publish` from this worktree.
* Do not enable either rollout flag or add blocking cost thresholds.

## Success Criteria

* New workflows are manual-only, read-only, deterministic, and security-scanned.
* Focused and full tests pass, with retained isolated atomic proof output.
* #622 and #626 source defects are covered without lowering quality thresholds.
* Human owners receive exact, evidence-linked actions for remaining decisions.
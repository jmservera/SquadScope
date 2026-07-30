<!-- markdownlint-disable-file -->
# Planning Log: Claracle Data Observatory Relaunch Remediation

## Discrepancy Log

Gaps and differences identified between research findings and the implementation plan.

### Unaddressed Research Items

* None

### Plan Deviations from Research

* DD-02: The implementation plan file uses the required `-plan.instructions.md` naming convention
  * Research recommends: `.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation.md`.
  * Plan implements: `.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md`.
  * Rationale: Task Planner mode requires the instructions suffix and frontmatter for implementation handoff.
* DD-03: Phase 1 Python validation used `python3` instead of `python`
  * Plan specifies: Run baseline commands with `python`.
  * Implementation differs: The same commands ran with `python3` because `python` is unavailable locally.
  * Rationale: `python3` is the repository-compatible interpreter available in the execution environment.
* DD-04: The Phase 1 Hugo baseline remains unexecuted locally
  * Plan specifies: Run `hugo --minify`.
  * Implementation differs: The command could not run because Hugo is unavailable.
  * Rationale: The gate was preserved and recorded as pending rather than weakened or represented as passing.
* DD-05: Phase 2 rendered hub and feed checks remain unexecuted locally
  * Plan specifies: Validate populated hub rendering and nonempty feeds after backfill.
  * Implementation differs: Python contracts passed, but two Hugo-dependent rendered checks skipped because Hugo is unavailable.
  * Rationale: Rendered acceptance remains explicit and pending for a Hugo-enabled environment.
* DD-06: Phase 3 rendered repository validation remains unexecuted locally
  * Plan specifies: Validate generated repository pages and curated topic links through Hugo rendering.
  * Implementation differs: Generator and template contracts passed, but the Hugo-dependent test skipped because Hugo is unavailable.
  * Rationale: Repository rollout remains off, and rendered acceptance remains pending rather than inferred from source tests.
* DD-07: Phase 4 freshness workflow installs PyYAML explicitly
  * Plan specifies: Convert the competing workflow to read-only freshness validation.
  * Implementation differs: The workflow also installs PyYAML before running dependent scripts.
  * Rationale: The freshness commands import YAML and require their runtime dependency in a clean Actions environment.
* DD-08: Dataset freshness reports timestamp-only generated-state drift
  * Plan specifies: Freshness checks pass after weekly generation.
  * Implementation differs: The standalone check found stale `generated_at` values in `CITATION.md` and `dataset-metadata.json`.
  * Rationale: The authoritative weekly transaction regenerates these artifacts before checking; current checked-in drift is recorded for final idempotence validation.
* DD-09: Phase 5 rendered contracts await preview CI
  * Plan specifies: Validate rendered metadata, feeds, XML, and weekly links.
  * Implementation differs: Source and fixture contracts passed locally, while 13 Hugo-dependent tests skipped.
  * Rationale: Hugo is unavailable locally; the Hugo-enabled preview workflow now owns executable rendered evidence.
* DD-10: Phase 6 Playwright assertions are blocked by a missing host library
  * Plan specifies: Execute browser consent, payload, and network assertions.
  * Implementation differs: Chromium downloaded but could not launch because `libnspr4.so` is unavailable.
  * Rationale: Static, VM, and Hugo-rendered checks passed; browser evidence remains pending in CI or a host with Playwright system dependencies.
* DD-11: Phase 7 timing enforcement remains report-only
  * Plan specifies: Collect at least three representative CI runs, calculate median and p95, then require owner approval before enforcement.
  * Implementation differs: One local Hugo and Pagefind timing sample exists; three comparable CI artifacts and approval do not.
  * Rationale: No numeric blocking budget is introduced without measured evidence and owner approval.
* DD-12: Phase 7 rendered execution exposed three Phase 5 SEO failures
  * Plan specifies: The production build job owns rendered SEO contracts.
  * Implementation differs: 21 contracts passed and 3 embed/topic social metadata or fixture contracts failed.
  * Rationale: The failures were routed to the owning SEO implementation rather than weakening CI. Shared embed SEO, alias metadata, and deterministic fixtures now pass all nine focused rendered tests.
* DD-13: Phase 8 downstream acceptance requires a deployed protected-environment run
  * Plan specifies: Retain a successful exact-release Podcaster smoke for relaunch acceptance.
  * Implementation differs: Reusable and post-deploy workflows are validated locally, but no Actions run URL exists before deployment.
  * Rationale: Local workflow tests cannot substitute for downstream endpoint evidence; Step 8.2 remains open.
* DD-14: Phase 10 browser gates cannot launch locally
  * Plan specifies: Run the complete Playwright and Lighthouse suites.
  * Implementation differs: Chromium cannot launch because the host lacks `libnspr4` and `libnss3`.
  * Rationale: Privileged system dependencies were not installed; CI is configured to install pinned browser dependencies.
* DD-15: Phase 10 Zizmor gate fails on existing Squad workflows
  * Plan specifies: `zizmor .github/workflows/` must pass.
  * Implementation differs: Zizmor reports 1 low, 12 medium, and 1 high finding, primarily credential persistence and excessive permissions in pre-existing Squad workflows.
  * Rationale: Findings were not suppressed or weakened. Remediation exceeds an isolated final-validation correction and remains blocking.
* DD-16: Literal two-run generator proof remains pending
  * Plan specifies: Run every generator twice and require no second generated diff.
  * Implementation differs: Focused idempotence tests and all four explicit freshness checks pass, but a complete two-run workspace diff proof was not executed.
  * Rationale: Existing unrelated worktree changes make broad generated-diff attribution unsafe without a clean isolated workspace.

## Implementation Paths Considered

### Selected: Unified Weekly Publish Transaction

* Approach: Hydrate prior generated state, run topic and repository state transitions, generate every Observatory surface in dependency order, and publish one lease-protected commit consumed by deployment.
* Rationale: This makes weekly state atomic, removes manual merge ambiguity, avoids competing branch writers, and preserves the static architecture.
* Evidence: `.copilot-tracking/research/subagents/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md` (Lines 151-201, 632-654)

### IP-01: Independent Scheduled Generator Workflows

* Approach: Keep separate schedules and pull requests for data, repository, topic, dataset, and tool outputs.
* Trade-offs: Smaller workflow edits, but multiple writers can race, outputs can represent different weekly states, and publication still depends on manual merges.
* Rejection rationale: It does not satisfy automatic coherent publication and repeats the current data-page workflow defect.

### IP-02: Regenerate Historical Weekly Articles

* Approach: Re-run full content generation for W21 through W31 from archived analyses.
* Trade-offs: Reuses the current generator, but can change editorial bodies and tags because archived inputs and accepted content differ.
* Rejection rationale: A frontmatter-only backfill is narrower, deterministic, and preserves accepted editorial content.

### IP-03: Treat Raw GitHub Topics as Dynamic Hubs

* Approach: Promote recurrent raw repository topics directly into the canonical topic taxonomy.
* Trade-offs: Easy candidate supply, but creates noisy or unsafe thin hubs and collapses the editorial distinction between tags and durable topics.
* Rejection rationale: The existing design calls for multi-signal evidence and safety filtering before promotion.

### IP-04: Infer Deletion From Missing Weekly Search Results

* Approach: Mark a repository deleted when it no longer appears in current artifacts.
* Trade-offs: Fully automatic, but produces false deletion states because search results are sampled and thresholded.
* Rejection rationale: Deletion requires positive evidence or reviewed override; absence only updates last-seen state.

## Suggested Follow-On Work

Items identified during planning that fall outside the initial remediation implementation.

* WI-01: Bounded repository lifecycle verifier - Evaluate a rate-limited metadata lookup for previously tracked repositories to confirm redirects and 404/410 states (medium priority, medium effort)
  * Source: DR-02
  * Dependency: Stable lifecycle ledger and owner approval for crawl behavior
* WI-02: Blocking build-time regression budget - Set and enforce Hugo and Pagefind budgets from at least three representative CI runs (medium priority, small effort after data collection)
  * Source: DR-01
  * Dependency: Phase 7 report-only timing baseline
* WI-03: Steady-state Podcaster smoke policy - Choose weekly, release-only, or contract-change execution and document secret/environment cost (low priority, small effort)
  * Source: DR-03
  * Dependency: Successful blocking relaunch smoke
* WI-04: Long-term search and analytics review cadence - Assign the named owner and automate reminders for GA4/GSC baseline updates (medium priority, small effort)
  * Source: Research remaining owner decisions
  * Dependency: Production GSC and GA4 acceptance
* WI-05: Relaunch external acceptance packet - Complete Hermes and URL sign-off, GA4/GSC verification, production XML and debugger checks, Podcaster run, accessibility review, visual captures, and sponsor approvals (high priority, external access required)
  * Source: Phase 9 external acceptance boundaries
  * Dependency: Committed deployment to the protected production environments
* WI-06: Squad workflow security remediation - Resolve Zizmor credential-persistence and excessive-permission findings without weakening workflow behavior (high priority)
  * Source: Phase 10 full workflow scan
  * Dependency: Review ownership for the Squad-generated workflow set

## Validation History

* 2026-07-29: Initial Plan Validator review found four repairable major planning gaps and one intentional deletion-verification deferral. Supporting-signal eligibility, CI ownership, all-severity traceability, and the Lighthouse server dependency were corrected before revalidation.

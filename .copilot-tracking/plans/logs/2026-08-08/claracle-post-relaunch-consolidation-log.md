<!-- markdownlint-disable-file -->

# Planning Log: Claracle Post-Relaunch Consolidation

## Selected Approach

* Use the approved BRD V1.1 as the controlling business baseline.
* Preserve server-rendered Hugo content as authoritative and add scoped
  progressive enhancement through shared versioned JSON contracts.
* Sequence governance and contracts before experience implementation, then join
  shell/editorial/cost, repository migration, and ranking/embed lanes at one
  immutable release candidate.
* Treat CR-04 and CR-06 as independent operational lanes. Neither authorizes the
  redesigned release.
* Make repository retirement URL-specific and evidence-gated. Keep GitHub Pages
  when the final approved map has no redirect rows; require a redirect-capable
  atomic deployment boundary only for a genuine-equivalent 301/308 row.

## Alternatives Considered

* One large implementation pull request was rejected because it would combine
  design, generated data, infrastructure, migration, and acceptance evidence.
* Enabling or enriching all repository details was rejected because CR-05 is
  superseded and BR-003 requires zero low-information output.
* Blanket repository-to-explorer redirects were rejected because they can lose
  repository-specific intent and become soft 404s.
* Blanket deletion based on aggregate analytics was rejected because retirement
  eligibility requires named URL-level evidence.
* Immediate hosting migration was rejected because V1.1 makes it conditional on
  the approved final URL map.
* Client-only rendering was rejected because search, accessibility, resilience,
  and no-JavaScript requirements make useful Hugo HTML mandatory.

## Discrepancy Log

* The implementation handoff predates V1.1 and calls redirect-capable hosting a
  planning blocker. V1.1 supersedes that conclusion with evidence-gated direct
  HTTP 404 retirement and conditional hosting migration.
* The primary research contains both the approved direct-404 approach and stale
  language describing V1.1 as proposed. The approved BRD and BRD session state
  control implementation planning.
* The BRD baseline calls external metadata delivered while the handoff identifies
  narrower remaining external debugger and named-review evidence. Phase 0 will
  reconcile the evidence without reopening approved scope.
* No implementation checkbox is marked complete by this planning transaction.
  Existing BRD research and approval are inputs, not delivery evidence.

## Dependencies And Human Gates

* Sponsor approval is required for CR-04 activation, pricing exceptions,
  repository dispositions, blocking-finding exceptions, and release GO.
* Hermes and URL review any hosting, deployment, workflow, or infrastructure
  change. Nibbler reviews generated content and prompt-injection surfaces.
* Fry owns test evidence; Leela owns architecture and final code review;
  Calculon owns design and visualization acceptance; Farnsworth owns annual
  editorial delivery; Bender owns cost and generated-data contracts.
* GSC, URL Inspection, sampled link evidence, first-party referrals, live
  assistive-technology review, and production observations may require external
  access and cannot be fabricated from repository state.

## Planned Validation

* Focused tests immediately after each story
* `ruff check .`, `ruff format --check .`, and `pytest tests/` for affected Python
* `hugo --minify`, internal-link validation, and rendered inspection for Hugo
* Repository-pinned Checkov and Zizmor checks for affected workflow or IaC files
* Schema, deterministic-generation, stale, malformed, unavailable, duplicate,
  empty, and future-version fixtures for public artifacts
* Automated accessibility and visual checks plus named keyboard, screen-reader,
  touch, zoom, reduced-motion, editorial, SEO, security, and migration evidence

## Implementation Log

* Repaired CR-06 experiment hydration by retaining the reviewed main-branch
  topic corpus instead of replacing it with the stale publish subtree. The
  workflow contract test passes; dispatch evidence and the budget-owner
  conclusion remain open.
* Added shared repository and ranking schemas, an evidence-first 274-URL
  repository inventory, deterministic generation, and focused tests. All URL
  dispositions remain pending because external evidence was not inferred.
* Added workflow run and attempt identity to token-ledger production, then added
  a deterministic fail-closed cost projection. Activation was intentionally
  withheld because historical rows are unidentified and the sponsor has not
  approved exclusion or cutover policy.
* Persisted complete monthly source packs, added stable annual claim/source
  evidence, invalidated clipped caches, and removed cumulative mid-thought
  publication clipping. Full-year fixtures now exercise the 1,200 to 1,800 word
  acceptance range.
* Reordered the primary navigation to Weekly, Monthly, and Yearly and added a
  configuration-level contract test.
* Preserved user-owned BRD, status, session-state, research, and instruction
  changes while updating only the controlling RPI implementation records.

## Validation Results

* Ruff checks passed for the affected Python surface.
* Six JSON schemas validated under Draft 2020-12.
* The consolidated affected test suite passed with 80 tests.
* The focused yearly evidence and rollup suite passed with 25 tests.
* Hugo `v0.147.9` built 2,701 pages and eight aliases successfully.
* Earlier focused slices passed 55 producer-identity tests and 19 subtests, 31
  cost-projection tests, and the navigation and experiment workflow checks.

## Remaining Blockers

* Sponsor approval of the cost legacy-row exclusion or cutover policy
* At least one fresh identified production ledger record before cost activation
* URL-level external and production evidence plus approved repository dispositions
* Workflow dispatch artifacts and a dated CR-06 budget-owner conclusion
* Named design, accessibility, editorial, SEO, security, and sponsor acceptance
* Production rollout and scheduled outcome observations

## Suggested Delivery Slices

1. Governance matrix and CR-06 cost-experiment repair
2. BR-001 design brief plus shared data-contract architecture
3. BR-008 navigation and BR-009 cost provenance as bounded implementation slices
4. BR-006 annual editorial repair with complete claim traceability
5. BR-003 URL evidence inventory before explorer implementation or page removal

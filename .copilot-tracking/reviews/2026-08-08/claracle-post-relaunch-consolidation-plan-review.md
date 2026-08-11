<!-- markdownlint-disable-file -->

# Implementation Review: Claracle Post-Relaunch Consolidation

## Review Metadata

| Field | Value |
|-------|-------|
| Plan | `.copilot-tracking/plans/2026-08-08/claracle-post-relaunch-consolidation-plan.instructions.md` |
| Reviewer | GitHub Copilot, RPI Agent |
| Date | 2026-08-08 |
| Iteration | 2 |
| Overall status | Complete for selected local slices; controlling plan remains in progress |

## User Request Fulfillment

| Request | Status | Evidence |
|---------|--------|----------|
| Follow the RPI workflow using the approved BRD and repository context | Complete | Research and plan artifacts controlled implementation, affected gates passed, and durable records were updated |
| Continue all five selected post-planning delivery slices | Complete for locally actionable scope | Governance, contracts, repository inventory, navigation and cost provenance, and yearly editorial repair are implemented without fabricating external evidence |
| Preserve V1.1 retirement policy, historical evidence, ownership, severity policy, and change control | Complete | Inventory rows remain pending, redirects remain conditional, frozen evidence is mapped rather than rewritten, and named gates remain open |
| Keep approval, implementation, acceptance, release, and outcome evidence distinct | Complete | Only verified implementation items are checked; design approval, cost activation, migration, named acceptance, release GO, and outcomes remain open |

## Placement And Quality Findings

* Changes landed in owning generators, workflows, schemas, configuration, tests,
  and tracking records rather than generated public output.
* Repository inventory records all 274 local URL forms while retaining pending
  evidence and disposition states. No deletion or redirect was attempted.
* Cost identity and projection are implemented at the producer and projection
  boundaries. Publication remains disconnected until sponsor policy and fresh
  identified input make reconciliation admissible.
* Yearly publication and evidence retention are separate: complete source packs
  and stable claim/source records remain available independently of paragraph-safe
  publication composition.
* Worktree review identified pre-existing user-owned BRD, status, session-state,
  research, and instruction edits. This review did not rewrite or revert them.

## Validation Results

* Ruff: passed on the affected Python surface
* JSON Schema Draft 2020-12 validation: six schemas passed
* Consolidated affected pytest suite: 80 passed
* Focused yearly evidence and rollup suite: 25 passed
* Hugo `v0.147.9`: 2,701 pages and eight aliases built successfully
* Focused producer identity: 55 tests and 19 subtests passed
* Focused cost projection: 31 tests passed

## Remaining Delivery Work

* Sponsor-approved cost legacy exclusion or cutover policy and a fresh identified
  production ledger record
* Cost projection workflow integration and About-page migration after those gates
* URL-level GSC, URL Inspection, link, referral, production, and disposition evidence
* CR-06 workflow dispatch artifacts and dated budget-owner conclusion
* Remaining product implementation in Phases 2 through 4
* Named design, accessibility, editorial, SEO, security, and sponsor acceptance
* Production rollout, rollback evidence, and scheduled outcome observations

## Review Conclusion

Complete for the five selected locally actionable slices. Their affected
automated gates pass, and the implementation fails closed where sponsor or
external evidence is absent. The broader controlling plan remains in progress;
no claim is made that Claracle is accepted, migrated, activated, or release-ready.

## CR-06 Harness Repair Review (Iteration 3, 2026-08-09)

| Field | Value |
|-------|-------|
| Scope | CR-06 build-cost experiment harness repair and official execution |
| Reviewer | GitHub Copilot, RPI Agent |
| Iteration | 3 |
| Overall status | Complete; only the dated budget-owner conclusion remains |

### User Request Fulfillment

| Request | Status | Evidence |
|---------|--------|----------|
| CR-06 option 1 (derive repository count) | Complete | PR #686 `67045a3` derives the count from the reviewed publish tree; 26 unit tests pass |
| Use worktrees for parallel work | Complete | Isolated lanes at `/home/jmservera/source/sqs-*`; each fix on its own branch/PR |
| Establish a faster local test loop | Complete | `python3 -m scripts.build_cost_experiment ...` full 3-rep run in ~22 s versus multi-minute CI |
| Merge each fix on explicit go-ahead | Complete | PRs #686, #687, #689 merged `--squash --admin` after 4/4 Squad approvals |

### Executive Findings

* Three cascading defects were each isolated with the local loop before any fix,
  which prevented masking and produced minimal, reviewable diffs.
* Fix placement is correct: count derivation lives in `discover_workload`/
  `run_experiment`; tool invocation in `_tool_version`/`_run_timed`; dependent-leaf
  exclusion in `materialize_variant`. No generated output was edited.
* Leela's review overturned the agent's initial option-1 recommendation for the
  embed/chart defect because that divisor would be contaminated. Option 2
  (consistent exclusion from every variant) was adopted, preserving a clean
  marginal denominator.
* Official run `31305223877` (main `8f680f4`, publish `4120078d`, 3 reps,
  report-only) completed cleanly with retained evidence. Report-only mode defines
  no blocking threshold and authorizes no rollout.
* `assert_rollouts_disabled` verified both `repo_pages.enabled` and
  `topic_hubs.dynamic_creation.enabled` were false during the measured run, so the
  CR-05 invariant held and CR-04 remains correctly sequenced after this evidence.

### Validation Results (Iteration 3)

* 26 build-cost unit tests pass; `ruff check` and `ruff format --check` clean
* Official experiment produced valid `summary.json`, `manifest.json`, per-sample
  JSON, per-variant logs, and `SHA256SUMS`

### Overall Status

Complete. Only the dated Q-01/NFR-009 budget-owner conclusion by jmservera and
the subsequent CR-04 canary activation remain in Phase 0.

### Q-01/NFR-009 Budget Conclusion (2026-08-09)

jmservera recorded the dated conclusion: report-only, no blocking budget. The
only material cost (`repository_pages`, Hugo ~8.8 ms/page, Pagefind ~2.4 ms/page)
is the low-information corpus slated for removal/reduction under Phase 3; CR-05
keeps `repo_pages` disabled. Cost is dismissed as a launch gate, to be
re-evaluated only if Phase 3 retains a meaningful repo-page corpus. CR-06 is now
fully closed. Rollout flags were disabled during measurement, clearing the CR-04
sequencing precondition.

### Phase 0 Completion (2026-08-09)

Phase 0 (Governance And Independent Operations) is complete. All six items are
closed: CR-01/CR-02 finding map, CR-03 supersession, CR-05 invariant, CR-06
repair/execute plus dated budget conclusion, CR-04 canary activation (PR #684,
merge `bd1cf04`, bounded to `local-first`, rollback owner jmservera), and the
external-metadata delivery-statement reconciliation (evidence clarification; the
narrower external debugger and named-review conclusions remain owner-gated in the
existing launch-gate register). No release, rollout beyond the bounded canary, or
named human acceptance is claimed. CR-04 promotion executes on the next
crawl-and-publish; observe that run and keep the tested disabled-rollback ready.

## Phase 2 Closure Review (Iteration 4, 2026-08-11)

| Field | Value |
|-------|-------|
| Scope | BR-006 yearly editorial closure and Phase 2 approval |
| Patch fingerprint | `cd545a1e431d88bf7cdd2fbf2c0d4d465618cad37ba4e2c3e1812320e7b8db54` |
| Named reviewers | Farnsworth and Nibbler |
| Final editor | jmservera |
| Overall status | Complete; proceed with closure PR |

### Request Fulfillment

| Request | Status | Evidence |
|---------|--------|----------|
| Produce a complete annual article without breaking crawl continuity | Complete | Deterministic monthly inputs remain the source; the generated article covers May-August and contains 1,266 words |
| Obtain named editorial acceptance | Complete | Farnsworth accepted publication quality, evidence bounds, structural variation, capitalization, punctuation, and month completeness on the exact patch |
| Obtain generated-content safety acceptance | Complete | Nibbler accepted the convergent sanitizer after probing nested entities, split entities, active markup, shortcodes, links, and instruction variants |
| Record final-editor approval | Complete | jmservera approved Phase 2 and directed creation of the closure PR on 2026-08-11 |

### Final Validation

* Focused generation surface: 63 tests and six subtests passed
* Full Python suite: 1,593 tests and 40 subtests passed
* Ruff check and format check passed across the repository
* Hugo 0.147.9 built 2,707 pages and eight aliases
* Adversarial sanitizer probes for shortcode-split and link-split entities passed
* `git diff --check` passed

### Review Conclusion

Complete. Phase 2 is approved for the closure PR. This approval does not start
Phase 3, authorize repository URL migration, or constitute release GO.

<!-- markdownlint-disable-file -->
# RPI Validation: Claracle Data Observatory Relaunch Remediation Phase 3

## Validation Metadata

* Plan: `.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md`
* Phase: 3, Durable Repository Lifecycle
* Changes log: `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md`
* Research: `.copilot-tracking/research/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md`
* Validation date: 2026-07-30
* Status: Failed

## Phase Requirements

Phase 3 is marked complete in the plan at
`.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md:167-175`.
The detailed requirements are:

* Preserve GitHub `id`, `node_id`, archive and disabled evidence, update timestamps,
	and canonical URLs while continuing to read legacy reduced records
	(`.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md:121-135`)
* Persist a versioned lifecycle ledger keyed by stable GitHub ID, preserve prior
	names and slugs, distinguish absence from deletion, and retain confirmed deleted
	pages for at least three years
	(`.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md:137-151`)
* Remove only expired tombstones and log the reason
	(`.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md:151`)
* Keep raw GitHub topics as tags and create repository-to-topic links only from
	aliases of promoted editorial topics
	(`.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md:156-167`)

The research requires positive deletion evidence or a reviewed override and rejects
absence from sampled weekly search as deletion evidence
(`.copilot-tracking/research/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md:24-25,60`).
FR-022 independently requires deleted pages to persist for at least three years
(`docs/prds/claracle-data-observatory-relaunch.md:132`).

## Plan-to-Change Comparison

| Plan item | Changes-log claim | Verified status | Evidence |
|-----------|-------------------|-----------------|----------|
| Step 3.1, preserve stable identity and lifecycle fields | Complete behind rollout gate as part of CR-03 | Implemented | `scripts/crawl.py:946-967` retains the required fields; `scripts/crawl.py:1084-1107` accepts all-or-none lifecycle fields for legacy compatibility; `tests/test_crawl.py:13-70` covers both contracts. |
| Step 3.2, persist lifecycle state and enforce retention | Complete behind rollout gate | Partial | Stable-ID keys, ledger merge, rename aliases, absence preservation, positive status evidence, check mode, and expiry exist in `scripts/observatory_repos.py:129-132,280-290,301-479,704-748,788-865`. The minimum retention requirement is violated when a deleted override omits `deletion_confirmed_at`, and the checked-in ledger has no repository state. |
| Step 3.3, add curated repository-to-topic links | Complete behind rollout gate | Implemented; rendered acceptance pending | Promoted aliases are loaded at `scripts/observatory_repos.py:684-702`, mapped at `scripts/observatory_repos.py:572-578`, and rendered separately from tags at `layouts/repo/single.html:63-84`. Fixture coverage is at `tests/test_observatory_repos.py:104-180`. The Hugo test remains skipped. |

The changes log reports CR-03 and MAJ-03 complete behind the rollout gate at
`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:17,24`.
That status is overstated for CR-03 because one supported deletion path can expire
before three years from confirmation and the current corpus has not been migrated
into the durable ledger.

## Verified Repository Evidence

* Crawl reduction includes stable identity, lifecycle booleans, timestamps, HTML
	URL, and API URL at `scripts/crawl.py:946-967`.
* Payload validation preserves backward compatibility only when all lifecycle fields
	are absent; partial lifecycle records are rejected at `scripts/crawl.py:1084-1107`.
* Stable GitHub IDs become lifecycle keys at `scripts/observatory_repos.py:129-132`,
	and legacy name keys migrate when a stable ID first appears at
	`scripts/observatory_repos.py:408-417`.
* Archive and disabled transitions require positive crawl fields at
	`scripts/observatory_repos.py:434-451`. Reviewed overrides receive explicit
	evidence at `scripts/observatory_repos.py:466-475`.
* The focused tests exercise stable-ID rename and archive evidence, absence without
	deletion, explicit-date deletion expiry, check mode, and disabled-state
	preservation at `tests/test_observatory_repos.py:282-451`.
* The configured production default remains disabled and declares three-year
	retention at `config/observatory.toml:1-12`.
* The current ledger is structurally versioned but contains zero repositories at
	`data/derived/observatory/repository-lifecycle.json:1-4`.
* Existing generated repository pages remain present. For example,
	`content/repo/anthropics-claude-code/index.md:8,194-201` identifies the generator
	and lifecycle status, but the page predates current `status_evidence` and curated
	`topic_links` output.
* The changes log records 17 crawl tests and 10 repository lifecycle tests passing,
	with one Hugo-dependent skip, at
	`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:142-150`.
	Terminal re-execution was attempted during this validation but was interrupted,
	so those historical counts were not independently reproduced in this session.

## Findings

### Critical

#### P3-CR-01: Deleted pages can be retained for less than three years

When `status = "deleted"` is supplied as a reviewed override without
`deletion_confirmed_at`, `reconcile_lifecycle` substitutes the repository's
last-seen week and starts retention from that older date
(`scripts/observatory_repos.py:738-746`). A repository last seen one year before
reviewed confirmation would therefore expire after only two more years. This
violates the Phase 3 success criterion and FR-022's minimum three-year retention
guarantee.

The test at `tests/test_observatory_repos.py:224-278` codifies the unsafe fallback
by marking a repository deleted without a confirmation date and accepting a
deadline based on its last-seen week. The explicit-date path is correctly covered
at `tests/test_observatory_repos.py:352-390`, but it does not protect the supported
date-omitted override.

Required correction: require `deletion_confirmed_at` for reviewed deleted
overrides, or start the clock from a persisted reconciliation date that cannot
predate confirmation. Add a regression test where last seen substantially predates
confirmation.

### Major

#### P3-MAJ-01: Current repository histories are not persisted in the lifecycle ledger

The changes log describes `data/derived/observatory/repository-lifecycle.json` as
durable repository identity and lifecycle state at
`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:48`,
but the artifact contains an empty `repositories` object
(`data/derived/observatory/repository-lifecycle.json:2`). Existing generated pages
and derived repository output are present, so the checked-in corpus has not been
migrated into the new durable state model.

The rollout gate reduces immediate mutation risk, but it also causes `generate` to
return before loading or reconciling the ledger at
`scripts/observatory_repos.py:852-863`. The current artifact therefore cannot serve
as evidence that existing repository identities, aliases, or lifecycle status will
survive source loss before the first enabled run.

Required correction: produce and review a deterministic initial ledger from the
checked-in corpus in a controlled enabled fixture or migration step, then verify
freshness and a second byte-identical generation without enabling production page
creation.

#### P3-MAJ-02: Rendered repository acceptance remains unexecuted

The only repository Hugo check is conditional on a locally installed Hugo binary
at `tests/test_observatory_repos.py:453-461`. The planning log explicitly records
the rendered page and curated-link validation as unexecuted at
`.copilot-tracking/plans/logs/2026-07-29/claracle-data-observatory-relaunch-remediation-log.md:30-34`,
and the changes log confirms the skip at
`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:150`.

Source and fixture contracts support the implementation claim, but they do not
prove that aliases, lifecycle notices, and curated links resolve in generated Hugo
output. This is a repository acceptance gap, not an external platform dependency.

Required correction: retain a Hugo-enabled run showing the generated canonical
page, prior-name alias, archive/deletion notice, raw tag links, and promoted topic
links resolve without broken internal URLs.

### Minor

No minor findings.

## Repository Implementation and External Acceptance

Repository implementation is substantially present for stable identity, positive
lifecycle evidence, rename aliases, absence preservation, expiry, check mode, and
curated topic mapping. It is not complete until P3-CR-01 is corrected. The empty
ledger and skipped Hugo test prevent current-corpus and rendered acceptance.

No GA4, GSC, social debugger, security sign-off, or downstream Podcaster evidence is
required to validate Phase 3's repository lifecycle semantics. Those are later
external acceptance gates. The `repo_pages.enabled = false` setting is an intended
rollout boundary, not evidence that Phase 3 behavior has passed production
acceptance.

## Coverage Assessment

* Step 3.1: Complete repository implementation with focused fixture evidence
* Step 3.2: Partial; most transitions are implemented, but minimum retention is
	incorrect on a supported path and current durable state is empty
* Step 3.3: Complete source and fixture implementation; rendered acceptance pending
* Overall requirement coverage: approximately 75 percent
* Validation status: Failed because a Critical FR-022 guarantee is not met

## Clarifying Questions

* Should `deletion_confirmed_at` be mandatory for every reviewed deletion override,
	or should reconciliation persist the operator's review date automatically?
* Is the empty checked-in lifecycle ledger intentional until a protected rollout
	run, or was an initial migration artifact expected in this PR?

## Recommended Next Validations

* Add and run the date-omitted deletion regression after correcting the retention
	clock
* Generate and review a populated initial lifecycle ledger from the checked-in
	repository corpus
* Run repository generation twice and verify byte-identical pages, derived JSON,
	and ledger output
* Run the Hugo-dependent repository test and assert canonical rename aliases,
	lifecycle notices, raw tags, and promoted topic links in rendered HTML
* Re-run the focused crawl and repository suites and attach fresh counts to the
	changes log
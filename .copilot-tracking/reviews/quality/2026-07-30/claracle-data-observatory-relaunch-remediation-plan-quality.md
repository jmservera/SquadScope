<!-- markdownlint-disable-file -->
# Implementation Quality: Claracle Data Observatory Relaunch Remediation

## Scope

* Pull request: `jmservera/SquadScope#623`
* Head: `f7adea1a4f06b2e0d3417956e9d00b42343939fc`
* Base: `83000a4ffab8ee83906b81a3f6bb3034a14156b4`
* Validation date: 2026-07-30
* Scope: Correctness, security, architecture, maintainability, and test quality

The Implementation Validator was invoked twice but could not access repository
execution or file tools. It issued no formal findings. This record contains the
reviewer's direct source verification and executable checks so the quality phase
does not imply unsupported validator evidence.

## Status

Needs Rework.

## Findings

### Critical

#### QUAL-CR-01 Deletion retention can begin before confirmation

`scripts/observatory_repos.py:738-746` falls back to the repository's last-seen
week when a reviewed deletion override omits `deletion_confirmed_at`. The resulting
deadline can be less than three years after the operator confirms deletion. The
supported date-omitted override path therefore violates FR-022.

Required action: require a confirmation date or persist the current reconciliation
date, then add a regression where last-seen substantially predates confirmation.

#### QUAL-CR-02 The protected Podcaster verifier cannot execute or prove exact bytes

The second Python heredoc in `.github/workflows/podcaster-handoff-smoke.yml:222-225`
normalizes to inconsistent indentation and fails compilation at line 33. Even after
indentation repair, `scripts/podcaster_handoff.py:524-555` truncates content at
50,000 characters, while the release contract requires exact promoted bytes.

Required action: make the verifier executable, define a non-truncating exact-release
path, and execute valid, mismatched, and over-limit fixtures before any network call.

### Major

#### QUAL-MAJ-01 Analytics privacy tests do not block CI

`.github/workflows/ci.yml:171-172` invokes the accessibility suites but omits
`tests/visual/observatory-analytics.spec.mjs`. The dedicated spec also calls the
analytics adapter directly instead of proving Cookie Consent integration, GA script
and cookie absence, reload persistence, and withdrawal behavior.

Required action: add the analytics suite to blocking CI and test the real consent
lifecycle and network boundary.

#### QUAL-MAJ-02 Dynamic-topic disablement lacks an operator decision

`scripts/manage_topic_hubs.py:393-394` returns silently when creation is disabled or
the command is a dry run. The plan requires an explicit disabled decision so an
intentional rollout gate is distinguishable from an unexplained no-op.

Required action: emit and test a stable non-mutating decision.

#### QUAL-MAJ-03 The checked-in lifecycle ledger does not seed existing histories

`data/derived/observatory/repository-lifecycle.json:1-4` contains no repositories
despite existing generated repository pages. A first enabled run therefore begins
without checked-in durable identity or alias state for the current corpus.

Required action: create and review a deterministic migration or seed artifact, then
prove a byte-identical second generation without enabling production rollout.

### Minor

#### QUAL-MIN-01 Workflow tests inspect text instead of executing embedded programs

`tests/test_pipeline.py:656-711` checks workflow strings but does not compile or run
the embedded Python verifiers. The invalid Podcaster heredoc consequently passed the
focused suite.

Required action: extract and execute workflow programs against representative
fixtures.

#### QUAL-MIN-02 Custom dataset freshness errors can mask the intended result

`scripts/export_observatory_dataset.py:405-409` calls `relative_to(PROJECT_ROOT)`
for every stale output. A custom output directory outside the repository raises
`ValueError` instead of reporting stale files.

Required action: format external paths safely and add a custom-output regression.

## Validation

* Focused Python suites: 91 passed and 8 subtests passed
* Full pytest: 1362 passed, 2 warnings, and 16 subtests passed
* Ruff lint and format: passed
* Hugo Extended 0.161.1: passed
* Pagefind 1.5.2: passed
* Internal links: passed
* Checkov: passed with one documented manual-dispatch skip
* Podcaster payload-verifier compile: failed with `IndentationError` at extracted line 33
* Hosted Production site job: failed after 66 browser tests passed and 97 skipped
* Hosted Lighthouse step: skipped after the browser failure
* Local Zizmor: 1 low, 12 medium, and 1 high finding
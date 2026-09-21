<!-- markdownlint-disable-file -->
# Plan: W38 Delivery Reliability

**Date:** 2026-09-14
**Status:** P08 post-delivery review correction complete; PR open and unmerged
**Scope:** P08 independent post-delivery correction
**Worktree:** /home/azureuser/source/worktrees/SquadScope-w38-delivery
**Branch:** squad/w38-delivery-reliability

## User Decisions and Requirements

* Scope legacy compatibility evidence to the exact publication identity:
  `week`, `publish_run_id`, and `article_sha256`.
* Ignore conclusively pre-submit legacy auto-dispatch runs, including
  observe-only, no-anchor, detection-failed, and protected-generation-skipped
  runs that could not have submitted.
* Preserve fail-closed handling for genuinely uncertain same-identity evidence
  and preserve all canonical receipt, workflow anchoring, concurrency, pause,
  approval, secret, manifest, digest, and retry safeguards.
* Reproduce the W38 auto-dispatch-path failure involving publication run `34806779896`,
  auto-dispatch run `34807417082`, and unrelated legacy run `34255052607`.
* Add narrowly scoped notification evidence only if an existing repository
  surface supports it without a cross-repository contract.
* Do not trigger production workflows or downstream mutations.
* Commit, push, and open a pull request against `main`; do not merge.
* Livingston rejected the delivered artifact. The independent revision must
  carry `manifest_sha256` end to end and fail closed when canonical evidence
  matches the first three identity fields but conflicts on the manifest digest.

## Goals

* Allow W38 and future publications to proceed when unrelated legacy runs are
  conclusively pre-submit.
* Continue blocking canonical duplicates and uncertain legacy evidence that can
  belong to the requested exact identity.
* Make eligible-but-not-submitted failures actionable and deduplicated where
  the existing workflow summary/annotation surface permits.

## Scope and Non-Goals

In scope: duplicate detection compatibility logic, the SquadScope-owned
Podcaster request payload contract, focused regression tests, workflow-contract
coverage, existing workflow notification evidence, and directly related
documentation.

Out of scope: changes within the Podcaster repository or service, production
dispatches, environment approval changes, secret changes, concurrency changes,
or retry-policy weakening.

## Acceptance Criteria

* Legacy compatibility decisions use the four-field publication identity when
  evidence is available.
* The Podcaster request includes the exact manifest SHA-256 and exact-release
  validation proves it matches the authorized manifest bytes.
* Canonical receipt matching treats a conflicting manifest digest as ambiguous
  prior submission evidence, never as the same proven duplicate or a clear
  retry.
* Run `34255052607` cannot block W38 when represented as no-anchor or failed
  detection with protected generation skipped.
* Same-identity ambiguous legacy evidence remains
  `ambiguous_prior_submission`.
* Same-identity canonical submitted or rejected receipts remain duplicates.
* Targeted detection and workflow-contract tests pass, followed by relevant
  Ruff checks.
* The canonical lowercase public article URL is verified using existing
  non-flaky test support or an anonymous fetch.
* The branch is committed, pushed, and submitted as an unmerged PR.

## Phases

<!-- rpi:phase id=P01 -->
### P01 - Safeguard Review and Incident Reproduction [x]

<!-- rpi:task id=P01-T01 -->
- [x] P01-T01: Review current duplicate, receipt, workflow, approval, secret,
  pause, manifest, digest, concurrency, and retry safeguards.

<!-- rpi:task id=P01-T02 -->
- [x] P01-T02: Reproduce the legacy W38 blocker from repository code and run
  evidence without executing production workflows.

<!-- rpi:phase id=P02 -->
### P02 - Identity-Scoped Compatibility Fix [x]

<!-- rpi:task id=P02-T01 -->
- [x] P02-T01: Scope legacy auto-dispatch compatibility to exact publication
  identity and ignore conclusively pre-submit runs.

<!-- rpi:task id=P02-T02 -->
- [x] P02-T02: Preserve fail-closed same-identity ambiguity and canonical
  duplicate behavior.

<!-- rpi:phase id=P03 -->
### P03 - Regression and Contract Tests [x]

<!-- rpi:task id=P03-T01 -->
- [x] P03-T01: Add the W38 regression and same-identity ambiguity/canonical
  duplicate negative tests.

<!-- rpi:task id=P03-T02 -->
- [x] P03-T02: Add or update workflow-contract coverage for actionable,
  deduplicated eligible-but-not-submitted evidence if the existing summary
  surface is sufficient.

<!-- rpi:phase id=P04 -->
### P04 - Documentation and Validation [x]

<!-- rpi:task id=P04-T01 -->
- [x] P04-T01: Update directly related documentation or comments only where
  needed.

<!-- rpi:task id=P04-T02 -->
- [x] P04-T02: Run targeted detection/workflow tests, relevant Ruff checks, and
  canonical lowercase public article URL verification.

<!-- rpi:phase id=P05 -->
### P05 - Delivery [x]

<!-- rpi:task id=P05-T01 -->
- [x] P05-T01: Review the final diff and reconcile implementation evidence.

<!-- rpi:task id=P05-T02 -->
- [x] P05-T02: Commit with the required conventional message and trailers.

<!-- rpi:task id=P05-T03 -->
- [x] P05-T03: Push the branch and open an unmerged PR against `main` with
  incident, tests, rollback, and preserved-safeguard evidence.

<!-- rpi:phase id=P06 -->
### P06 - Independent Contract Revision [x]

<!-- rpi:task id=P06-T01 -->
- [x] P06-T01: Add `manifest_sha256` to the exact Podcaster payload and validate
  it against the exact authorized manifest bytes.

<!-- rpi:task id=P06-T02 -->
- [x] P06-T02: Extend canonical receipt and legacy evidence comparison to the
  four-field publication identity, failing closed on conflicting manifest
  digests while retaining only evidenced safe legacy compatibility.

<!-- rpi:task id=P06-T03 -->
- [x] P06-T03: Reconcile tests, documentation, changes evidence, PR description,
  commit, push, and CI without production dispatch or merge.

<!-- rpi:phase id=P07 -->
### P07 - Reviewer-Lockout Correction [x]

<!-- rpi:task id=P07-T01 -->
- [x] P07-T01: Validate every canonical identity field, including the requested
  manifest digest, before missing-credential or missing-repository short-circuits
  in both duplicate-check entry points.

<!-- rpi:task id=P07-T02 -->
- [x] P07-T02: Add regression coverage for credential-less and repository-less
  missing or invalid manifest digests while preserving valid no-credential
  compatibility behavior.

<!-- rpi:task id=P07-T03 -->
- [x] P07-T03: Reconcile P06 validation counts, run targeted and full validation,
  commit, push, update PR evidence, and resolve the current review threads without
  production dispatch or merge.

<!-- rpi:phase id=P08 -->
### P08 - Post-Delivery Evidence Correction [x]

<!-- rpi:task id=P08-T01 -->
- [x] P08-T01: Make the conflicting legacy-manifest regression explicitly mock
  the reconstructed manifest bytes and prove the digest conflict deterministically.

<!-- rpi:task id=P08-T02 -->
- [x] P08-T02: Distinguish historical P06 and current P07 validation snapshots
  by exact commit, command, scope, and result in tracking and the PR description.

<!-- rpi:task id=P08-T03 -->
- [x] P08-T03: Revalidate, commit, push, answer and resolve the new review
  threads, and leave the PR green, thread-clean, open, and unmerged.

## Dependencies

* P02 depends on P01.
* P03 depends on P02.
* P04 depends on P03.
* P05 depends on P04.
* P06 is a reviewer-directed revision of P02-P05 and depends on the rejected
  delivered baseline remaining intact.
* P07 is an independent reviewer-lockout correction of P06 and depends on the
  pushed P06 baseline remaining intact.
* P08 is a post-delivery evidence correction of P07 and depends on preserving
  the pushed P07 implementation and validation results.

## Follow-Up Items

* None at implementation start. If durable notifications require a new
  cross-repository contract or a substantially larger operational surface,
  create a narrowly scoped GitHub issue instead of expanding this PR.

> **Authoritative correction — 2026-09-21:** This historical plan originally used broader incident wording for the W38 auto-dispatch-path failure. W38 was not a missed-publication incident: manual recovery run `34958522782` reached Azure and W38 ultimately published successfully. W39 is the sole missed-publication production incident. Historical execution context above is superseded wherever it implies no successful W38 public outcome.

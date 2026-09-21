# Production Incident Research: Podcast Dispatch Identity and Reconciliation

**Research date:** 2026-09-21
**Posture:** Balanced, thorough production-incident investigation
**Scope:** Read-only repository, GitHub metadata/log evidence, and conceptual Podcaster contract research. No source, test, workflow, configuration, Git state, or external-repository changes.
**Objective:** Establish planning evidence for identity-scoped dispatch deduplication and terminal-outcome reconciliation after the W38/W39 dispatch failures.

## Research protocol and initial boundary

- Required sequence: Wider → Deeper → Contrarian.
- Facts are distinguished from inferences. An HTTP/API acceptance alone is not treated as a completed provider submission.
- Incident facts supplied by the caller are recorded as caller-verified context pending corroboration from accessible GitHub evidence.
- Artifact path preflight: this file is the explicitly approved primary artifact under `.copilot-tracking/research/2026-09-21/`, distinct from source and all other tracking artifacts.

## Initial evidence register

| ID | Wave | Statement | Provenance | Confidence |
|---|---|---|---|---|
| C1 | Wider | Prior architecture decision defines trusted correlation as article SHA-256 matched to `origin/publish` manifest `candidate.content_sha256`, with manifest `run_id` as trusted crawl identity. | `.squad/decisions.md:3-6` | High |
| C2 | Wider | Prior duplicate key was `week + publish_run_id + article_sha256`; workflow concurrency and API history check were intended as separate defenses, with Podcaster `--require-merged` defense in depth. | `.squad/decisions.md:8-12` | High |
| C3 | Wider | Caller reports W39 publication 35561779454 succeeded, while auto-dispatch 35562322880 stopped at `ambiguous_prior_submission` due to cancelled historical 32730109166; no W39 Azure execution occurred. The report must not be reduced to HTTP 200 evidence. | Caller-verified incident evidence, 2026-09-21; corroborated for publish/detect/job disposition by C6-C8 | High |

## Wave status

- **Wider:** Complete — mapped present boundaries and independently corroborated incident run metadata.
- **Deeper:** Complete — inspected current workflow/script/test semantics and Podcaster evidence surfaces.
- **Contrarian:** Complete — tested the proposed boundary against unrelated legacy ambiguity, exact-identity uncertainty, and false terminal-success assumptions.

## Open questions

1. Where do auto-dispatch and canonical identity construction occur, and which digest fields are actually persisted?
2. What exact history/dedup branch converts legacy cancelled or unreadable runs into an ambiguous blocker?
3. What receipt schema and mutation point exist now, including `no_anchor` / observe-only behavior?
4. Which GitHub run/job/step/log conditions represent cancellation or missing execution?
5. Which Podcaster surface is authoritative for synthesis, video, and provider terminal outcomes?
6. Which repository tests and CI gates constrain a safe change?

## Wave 1 — Wider: current boundary map and incident metadata

### Facts

| ID | Finding | Evidence / provenance | Confidence |
|---|---|---|---|
| C4 | Auto-dispatch is a `workflow_run` chain from successful `Sync publish data to main`, with manual `workflow_dispatch` week override and `observe_only`; its global concurrency is intentionally non-cancelling. | `.github/workflows/auto-podcast-dispatch.yml:11-37` | High |
| C5 | Detection exposes week, publishing run, article SHA-256, manifest SHA-256, dedup status, and prior-run URL. It binds the triggering workflow to a sync commit; absent anchor exits `no_anchor` fail-closed, whereas no article is a clean `no_new_article`. | `.github/workflows/auto-podcast-dispatch.yml:50-62,114-165` | High |
| C6 | Run 35561779454 (`Crawl and publish weekly data`) completed successfully. Run 35562322880 (`Auto-dispatch podcast after weekly article`) failed: detect job failed, and both protected-dispatch and observe-only jobs were skipped. | GitHub Actions runs 35561779454 and 35562322880, retrieved 2026-09-21: https://github.com/jmservera/SquadScope/actions/runs/35561779454 and https://github.com/jmservera/SquadScope/actions/runs/35562322880 | High |
| C7 | The W39 run log records exact W39 identity (`week=2026-W39`, `publish_run_id=35561779454`, article digest `f666…506c`, manifest digest `e2d4…42a7`) and rejects run 32730109166 as `legacy_submission_without_canonical_receipt`, emitting an `ambiguous_prior_submission` receipt. | Run 35562322880 log, retrieved 2026-09-21, lines containing receipt/error; canonical run URL above | High |
| C8 | Run 32730109166 (`Trigger podcast generation`) is `cancelled`; its only job is cancelled with **zero steps**, and its GitHub log download is an empty ZIP (22 bytes). W38 auto run 34255052607 likewise failed in detect with protected and observe-only jobs skipped; W38 recovery 34958522782 completed successfully with a 10-step manual trigger job. | GitHub Actions runs 32730109166, 34255052607, 34958522782, retrieved 2026-09-21: https://github.com/jmservera/SquadScope/actions/runs/32730109166 ; https://github.com/jmservera/SquadScope/actions/runs/34255052607 ; https://github.com/jmservera/SquadScope/actions/runs/34958522782 | High |

### Wider relationship

`C6/C7` supports the caller's W39 sequence: successful publishing identity → detect-only failure → no protected job. `C8` explains why a cancelled legacy run supplies no canonical counter-evidence; it **does not** prove provider submission or non-submission. It supports a bounded evidence model, not a global blocker.

## Wave 2 — Deeper: identity, mutation, receipts, and reconciliation

### Current implementation facts

| ID | Finding | Evidence / provenance | Confidence |
|---|---|---|---|
| C9 | The current in-process `DispatchIdentity` is only `(week, publish_run_id, article_sha256)`. Receipt identity matching compares those same three fields. `manifest_sha256` is emitted in receipts but is not part of the identity comparator or duplicate-check input. | `scripts/auto_dispatch_detect.py:90-103,173-193`; `.github/workflows/auto-podcast-dispatch.yml:167-181,215-225` | High |
| C10 | Exact mutation boundary is the protected job's `podcaster_handoff.py` invocation after it refetches the exact publish-branch manifest and validates week/run/mode/eligibility/article SHA. That call returns a Podcaster `job_id` on accepted response. | `.github/workflows/auto-podcast-dispatch.yml:326-403,405-439`; `scripts/podcaster_handoff.py:972-1058,1106-1165` | High |
| C11 | Present receipt persistence is log-only: detect prints `PODCAST_DISPATCH_RECEIPT::<JSON>` for duplicate, ambiguity, or detect outcomes; the handoff writes GHA outputs for receipt state/job ID/status. There is no durable Coordinator-side pre/post mutation receipt storage shown by these paths. | `.github/workflows/auto-podcast-dispatch.yml:183-227`; `scripts/auto_dispatch_detect.py:173-185,355-366`; `scripts/podcaster_handoff.py:991-1005,1156-1165` | High |
| C12 | Receipt states distinguish submitted/rejected/unknown from nonblocking observation and pre-submit states. Existing duplicate logic reads up to 50 auto/manual workflow runs, jobs, and zipped logs; an exact `submitted` receipt blocks, `pre_submit_failed` permits retry, and `submission_unknown` is ambiguous/fail-closed. | `scripts/auto_dispatch_detect.py:73-87,874-1046`; `tests/test_auto_dispatch_detect.py:449-549` | High |
| C13 | Legacy auto observe-only is deliberately ignored only when jobs prove successful observe-only summary plus skipped protected dispatch. A manual legacy success is blocking only when a manifest/run/sync-derived canonical identity can be reconstructed; missing exact identity or unreadable jobs/logs returns ambiguity. | `scripts/auto_dispatch_detect.py:276-335,916-1046`; `tests/test_auto_dispatch_detect.py:577-711` | High |
| C14 | `no_anchor` is fail-closed; observe-only excludes protected mutation. Current tests cover no-anchor correlation failure, legacy observe-only, unreadable logs, legacy exact identity failure, receipt state behavior, and same-week/different-article non-conflation. | `.github/workflows/auto-podcast-dispatch.yml:94-125,272-289`; `tests/test_auto_dispatch_detect.py:449-711,742-846` | High |
| C15 | A 2xx handoff is only API acceptance with a validated `job_id` and accepted status; the Coordinator has no terminal synth/video/provider readback or incident creation/dedup stage in these dispatch surfaces. | `scripts/podcaster_handoff.py:972-1058,1156-1165`; `.github/workflows/auto-podcast-dispatch.yml:405-440` | High |
| C16 | Podcaster's current conceptual authoritative surface is its canonical publication evidence keyed by accepted job ID, with explicit provider outcomes and `external_verified` required for public/published state. It retains provider intent/outcome outside expiring job storage. | `jmservera/SquadScope-Podcaster#680`, merged 2026-09-15, retrieved 2026-09-21: https://github.com/jmservera/SquadScope-Podcaster/pull/680 | Medium-High (cross-repo contract, not locally executed) |
| C17 | Podcaster's open contracts require identity-bound provider readback using accepted `job_id`, publish run, week, and article SHA; ambiguous create remains `publication_unknown` and is never blindly repeated. Its bounded lifecycle explicitly distinguishes synth/recording/render/archive/provider mutation/readback stages. | `jmservera/SquadScope-Podcaster#678`, `#679`, `#681`, and `#682`, retrieved 2026-09-21: https://github.com/jmservera/SquadScope-Podcaster/issues/678 ; https://github.com/jmservera/SquadScope-Podcaster/issues/679 ; https://github.com/jmservera/SquadScope-Podcaster/issues/681 ; https://github.com/jmservera/SquadScope-Podcaster/pull/682 | Medium-High |
| C18 | `jmservera/SquadScope-Coordinator#17` is unrelated closed yearly-rollup work, not an incident authority or dispatch contract. | https://github.com/jmservera/SquadScope-Coordinator/issues/17, retrieved 2026-09-21 | High |

### Deeper relationship

`C9 → C11` identifies the defect seam: manifest digest is evidence but not identity, and Coordinator receipts are ephemeral logs rather than durable mutation records. `C10/C15 → C16/C17` shows the required handoff boundary: accepted `job_id` must become durable correlation input to a bounded terminal monitor; an API 2xx cannot establish synth, video, or provider completion.

## Wave 3 — Contrarian: limits and fail-closed cases

| ID | Challenge tested | Result and evidence relationship | Confidence |
|---|---|---|---|
| C19 | “Treat every legacy run with no identity as a duplicate.” | **Disproven for unrelated identities.** C8 shows cancelled run 32730109166 has empty jobs/logs; C7 shows it blocked W39 despite no canonical connection. Global fail-closed turns absence of identity into a poison pill. Legacy unknown may remain fail-closed only after an exact identity association is established. | High |
| C20 | “Clear any legacy ambiguity to restore throughput.” | **Weakens idempotency and is rejected.** C12/C13 and Podcaster #678/#679 require unknown exact submission to remain mutation-blocked because response loss/crash can leave a real provider artifact. | High |
| C21 | “A handoff 200/accepted job proves publication.” | **Disproven.** C15 identifies acceptance only; C16/C17 require provider outcome and external verification. Caller-verified W39 facts and C6 confirm protected job never executed. | High |
| C22 | “Current identity is already canonical.” | **Weakens required outcome.** C9 excludes manifest digest from dedup matching despite recording it. A plan that leaves it outside the equality key cannot satisfy the caller-required four-part canonical identity. | High |
| C23 | “No-anchor/observe-only can be treated like an actual submission.” | **Disproven.** C5/C14 define them as fail-closed/no-mutation states; tests intentionally keep observe-only nonblocking. | High |

## Planning-ready recommendation and boundaries

### Recommended plan boundary (no implementation)

1. **Coordinator identity and durable receipts:** Define the canonical identity as `(week, publish_run_id, article_sha256, manifest_sha256)` and create durable canonical pre-mutation and post-API-acceptance receipts at the protected handoff boundary. Require dispatch-run ID, full identity, attempt ID, API/receipt state, and Podcaster accepted job/correlation ID. Preserve append-only history and do not leak credentials or payloads.
2. **Identity-scoped dedup/migration:** Query/compare only full canonical identities. Classify legacy evidence as unrelated when it cannot be demonstrably associated; it must not block a different identity. If legacy evidence maps to the exact requested identity but lacks terminal proof, retain `submission_unknown` / fail-closed behavior and create an operator-visible reconciliation need.
3. **Bounded terminal reconciliation:** Add an explicit Coordinator monitor, bounded deadline, and state model from acceptance through Podcaster synth start, video terminal state, and authoritative provider outcome. Use Podcaster's accepted job/correlation ID and canonical evidence/readback—not HTTP status. Missing stage, timeout, unknown, or nonterminal provider state must visibly fail.
4. **Operational incident lifecycle:** Create/deduplicate a Coordinator incident by canonical identity + failed monitor stage/state; record safe correlation/evidence pointers and recovery rule. Do not auto-repeat ambiguous provider mutation. Define reconciliation/manual-handoff ownership with Podcaster.
5. **Validation and release gates:** retain (not weaken) the full Python tests, Ruff check/format, blocking Checkov, Bandit/Zizmor security scanning, pip-audit CI dependency audit, and relevant workflow/production build gates. Repository-standard local commands are `ruff check .`, `ruff format --check .`, and `pytest tests/`; see `.github/copilot-instructions.md:68-79`, `.github/workflows/ci.yml:43-54`, `.github/workflows/lint.yml:41-49`, `.github/workflows/checkov.yml:46-63`, `.github/workflows/security-scanning.yml:53-98`.

### Required test matrix

- cancelled historical run whose jobs/steps/log ZIP are empty: unrelated canonical W39/W38 identity proceeds; exact mapped identity remains blocked/reconcilable;
- `no_anchor` produces no mutation receipt and no false terminal monitor success;
- observe-only produces a durable observation record but is never submission/terminal-success evidence;
- unrelated ambiguous legacy evidence does not block a different full four-field identity;
- exact-identity ambiguous legacy/API failure remains fail-closed and opens/deduplicates an incident;
- duplicate workflow delivery/retry creates no second handoff for an accepted exact identity;
- crash before receipt, after pre-mutation receipt, after API acceptance before post-receipt, and monitor restart all preserve idempotency;
- accepted `job_id` without synth start, without video terminal result, or without authoritative provider outcome reaches visible failed/unknown incident state rather than success;
- terminal externally verified provider outcome closes/reconciles the exact identity only.

## Risks, gaps, and stop decision

- **Planning Readiness: Ready.** The defect, exact Coordinator mutation seam, current receipt/dedup semantics, incident run facts, and the necessary cross-repo provider contract are sufficient to make a bounded implementation plan without guessing terminal success.
- **Smallest remaining gaps:** Before implementation, agree the durable Coordinator receipt backing store/retention and the Podcaster machine-readable monitor/readback endpoint or artifact schema for accepted `job_id` and synth/video/provider terminal states. These are contract design choices, not research blockers.
- **Risks:** Older run history is finite (`WORKFLOW_LOOKBACK_RUNS=50`) and GitHub logs are ephemeral; migration must avoid treating absence as safe. Cross-repo PR/issue text is design evidence, not proof that an endpoint is deployed. Monitoring must prevent both premature success and unbounded polling.
- **Stop decision:** Wave criteria met and source evidence saturated within the read-only scope. Further source inspection would not resolve the two explicit cross-repo contract decisions.

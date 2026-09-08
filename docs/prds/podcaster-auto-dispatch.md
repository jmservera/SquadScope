---
title: Protected Podcaster Auto-Dispatch Product Requirements Document
description: Requirements for automatically starting the protected Podcaster handoff after a verified weekly publication
author: SquadScope Squad
ms.date: 2026-09-08
ms.topic: reference
---

# Protected Podcaster Auto-Dispatch

Version 0.1 | Status Draft | Owner jmservera | Team SquadScope Squad

## 1. Executive summary

SquadScope publishes a weekly article and retains an exact publish manifest, but
real Podcaster generation currently starts only when an operator manually
dispatches `.github/workflows/trigger-podcast.yml` with the week and crawl run
ID. The crawl, publish sync, and deployment workflows do not start that
workflow.

This PRD proposes an automated handoff that starts the existing protected
Podcaster workflow only after the exact article represented by a valid publish
manifest is merged to the default branch. Automation must preserve the
`podcaster-real-generation` environment approval, branch restriction, secret
scope, exact-manifest validation, digest validation, and duplicate prevention.
It must not automatically approve or bypass real generation.

## 2. Problem statement

The weekly pipeline can complete successfully without creating a Podcaster run.
Operators must notice the completed publication, locate the correct week and
publish run ID, confirm downstream readiness, and manually dispatch the
workflow. A missed manual action leaves no pending environment deployment,
failure signal, or automated reminder.

The 2026-W37 publication exposed this gap:

| Evidence | Result |
|---|---|
| Crawl and publish run | `34082521901` completed successfully on 2026-09-07 |
| Manifest | `data/candidates/2026-W37/34082521901/publish-manifest.json` exists on `publish` |
| Manifest identity | `week=2026-W37`, `run_id=34082521901`, normal mode |
| Promotion and validation | Promotion eligible; decision `promote`; analysis gate passed |
| Article digest | Manifest digest `fff67a320acafd2341dca4c2ff5cd6c74a3862d8f035a326f5562cb2d0d604f1` matches `content/weekly/2026/W37.md` on `main` |
| Podcast workflow | No run was created because `trigger-podcast.yml` supports only `workflow_dispatch` |

This is a capability gap, not a failed retry, skipped condition, or invalid
input incident.

## 3. Goals

| ID | Goal |
|---|---|
| G-001 | Automatically create one protected Podcaster handoff run for each eligible weekly publication after its exact article is merged to `main`. |
| G-002 | Preserve human approval before production secrets are exposed or the Podcaster endpoint is called. |
| G-003 | Bind every handoff to the exact week, crawl run ID, manifest, and article digest that were published. |
| G-004 | Make missing, blocked, duplicate, rejected, and failed handoffs observable to operators. |
| G-005 | Retain the existing manual dispatch as an audited recovery path. |

## 4. Non-goals

* Automatically approving the `podcaster-real-generation` environment.
* Removing `--require-merged`, manifest identity checks, article digest checks,
  branch restrictions, or protected secrets.
* Changing the SquadScope-Podcaster request or response contract.
* Generating an episode before the weekly article is present on `main`.
* Retrying a rejected or failed real-generation request without an explicit,
  bounded policy.
* Implementing the workflow as part of this PRD.

## 5. Users and operational roles

| Role | Need |
|---|---|
| Repository owner | A pending protected deployment appears automatically for the correct weekly publication. |
| Environment approver | Enough immutable evidence to approve or reject the exact handoff without reconstructing workflow history. |
| Pipeline operator | Clear status when no handoff was created, approval is pending, or downstream admission failed. |
| Podcaster maintainer | Exactly one request for the intended article revision, with the existing idempotency and provenance fields. |

## 6. Functional requirements

| ID | Requirement | Acceptance |
|---|---|---|
| FR-001 | Detect an eligible weekly publication only after the corresponding article is merged to the repository default branch. | A successful crawl alone cannot start real generation; the trigger becomes eligible only when the exact article exists on `main`. |
| FR-002 | Resolve the week and crawl run ID from trusted, machine-readable publication evidence rather than selecting the latest manifest by time. | The created run records the same `week` and `run_id` as the accepted publish transaction, including when multiple runs exist for one week. |
| FR-003 | Validate the manifest using the existing exact path `data/candidates/<week>/<run_id>/publish-manifest.json`. | Missing, malformed, ineligible, or identity-mismatched evidence fails closed before environment secrets are available. |
| FR-004 | Verify that the article on `main` matches `candidate.content_sha256` in the selected manifest. | A stale, amended, or unrelated article cannot reach the Podcaster endpoint. |
| FR-005 | Start the real-generation job automatically but retain the `podcaster-real-generation` environment gate and required reviewers. | Automation creates a pending deployment; no endpoint request occurs until GitHub records approval. |
| FR-006 | Prevent duplicate automatic or manual requests for the same week, publish run ID, and article digest. | Concurrent events, reruns, and workflow retries produce at most one admitted request unless an authorized operator selects an explicit rerun path. |
| FR-007 | Keep `workflow_dispatch` available for recovery and controlled reruns. | Manual runs execute the same validation and protected job as automatic runs and are distinguishable in retained evidence. |
| FR-008 | Record the trigger source, week, publish run ID, manifest path and digest, article path and digest, approval state, workflow URL, and downstream admission result. | Operators can trace the handoff without exposing endpoint URLs, credentials, request bodies, response bodies, or breaking-news text. |
| FR-009 | Surface failures and missing handoffs on the weekly tracking issue or another owner-approved operational channel. | An eligible publication that does not create a pending protected run within the configured service window produces an actionable alert. |
| FR-010 | Support an owner-controlled pause for known downstream outages or deployment blocks. | While paused, no endpoint call occurs; the publication remains visible as deferred and can resume without selecting a different manifest. |

## 7. Trigger and trust-boundary design constraints

The implementation design must be reviewed before workflow changes begin. It
must define a trusted correlation mechanism between the merged publication and
the crawl run ID. Acceptable designs may include a machine-readable publication
descriptor or verified metadata produced by the publish-sync path. Inferring
the target from "latest successful run," free-form pull request text, issue
comments, or user-controlled branch names is not acceptable.

The automatic event may start a workflow run, but the real-generation job must
continue to:

1. Execute reviewed workflow code from `main`.
2. Check out the default branch for the article.
3. Fetch the exact manifest from `publish`.
4. Validate week, run ID, eligibility, and article digest.
5. Wait for the protected environment approval.
6. Read `PODCASTER_ENDPOINT` and `PODCASTER_API_KEY` only inside the protected
   job.
7. Call `scripts/podcaster_handoff.py --require-merged`.

## 8. Reliability and security requirements

| ID | Requirement |
|---|---|
| NFR-001 | The trigger must be idempotent across duplicate GitHub events, job retries, workflow reruns, and manual recovery. |
| NFR-002 | The design must fail closed if publication evidence is missing, ambiguous, invalid, or does not match `main`. |
| NFR-003 | Workflow permissions must be job-scoped and least privilege; any dispatch permission must be justified and reviewed. |
| NFR-004 | Fork and pull-request events must not gain access to the protected environment or production secrets. |
| NFR-005 | Untrusted commit messages, pull request text, issue text, and generated article content must not become workflow commands or trusted correlation data. |
| NFR-006 | Automatic dispatch latency should be no more than 10 minutes after the exact publication reaches `main`, excluding environment approval time. |
| NFR-007 | A blocked or failed handoff must be visible without weakening required checks or environment protection. |

Workflow implementation requires URL pipeline review and Hermes security
review. Any generated or externally supplied text that affects trigger behavior
also requires Nibbler review.

## 9. Rollout

1. Approve the trusted correlation design and threat model.
2. Add tests for event correlation, exact-manifest selection, digest mismatch,
   duplicate events, pause behavior, and manual recovery.
3. Run in observe-only mode, recording which handoff would have been created
   without contacting Podcaster.
4. Enable automatic creation of pending protected deployments while retaining
   required reviewer approval.
5. Compare four consecutive weekly publications against their manifests,
   approvals, and downstream admission records.
6. Remove any temporary observe-only instrumentation after owner acceptance.

## 10. Acceptance criteria

The feature is accepted when:

* Four consecutive eligible weekly publications automatically create exactly
  one pending protected Podcaster deployment each.
* Every run uses the correct week, crawl run ID, manifest, and article digest.
* No Podcaster request occurs before environment approval.
* Duplicate events and workflow reruns do not create duplicate admitted jobs.
* Invalid or stale evidence fails closed and creates an actionable operator
  signal.
* Manual recovery remains functional and uses the same validation path.
* URL, Hermes, Leela, Fry, and jmservera record approval of the implementation
  and production evidence.

## 11. Open decisions

| Decision | Owner |
|---|---|
| Select the trusted publication-to-run correlation artifact and event source. | Leela / URL |
| Define the duplicate key and authorized rerun procedure across both repositories. | Leela / Podcaster maintainer |
| Define the owner-controlled pause mechanism and maximum deferred duration. | jmservera |
| Select the operational alert channel and service window. | jmservera / URL |
| Confirm whether environment approval should remain required for every weekly run. | jmservera / Hermes |

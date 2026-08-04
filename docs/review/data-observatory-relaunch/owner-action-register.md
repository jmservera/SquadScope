---
title: Data Observatory Relaunch Owner Action Register
description: Sequenced owner actions and evidence requirements for Claracle relaunch gates that cannot be completed by repository automation
author: SquadScope Squad
ms.date: 2026-08-03
ms.topic: reference
keywords:
  - launch gates
  - acceptance evidence
  - owner actions
  - rollout approval
estimated_reading_time: 7
---

## Purpose

Repository automation proves implementation behavior, not external platform state or
human approval. This register defines the remaining actions, actors, and completion
evidence without recording secret values or granting approval by implication.

## Analytics and search acceptance

Owner: jmservera, with Hermes reviewing production consent behavior.

Current evidence:

* Production renders secret-backed GA configuration on the main site and standalone embed
* The `GA_MEASUREMENT_ID` secret name exists
* Production serves `https://claracle.com/sitemap.xml` as HTTP 200 and `application/xml`
* jmservera confirmed the intended GA4 stream, verified GSC property, root sitemap submission, and GA4-to-GSC product link on 2026-08-02
* The root sitemap is one complete `<urlset>` rather than a sitemap index, so there are no child sitemaps to submit

Required actions:

1. Record denied and granted production consent behavior without exposing identifiers.
2. Transcribe the supplied GSC performance export and capture GA4 values for one explicit date range.
3. Confirm GSC finishes processing the sitemap and review indexed and excluded URL counts.
4. Update the [dated baseline](../../growth/ga4-gsc-baseline-2026-07-29.md) with redacted conclusions and actual values.

Completion evidence still needed: consent observations, processed sitemap conclusion,
numeric baseline date range, and reviewer/date.

## Security acceptance

Owners: Hermes, URL, and jmservera.

Required actions:

1. Hermes records a disposition for SEC-01 through SEC-06 in the [security review](security-review.md).
2. Review the implemented SEC-02 no-referrer and frame-local consent model, including its publisher-markup and third-party-storage limitations.
3. Approve, reject, or amend the SEC-03 exact public export field and source-path allowlists.
4. Approve, reject, or require additional controls for the SEC-05 defense-in-depth accepted-risk recommendation; no acceptance is currently recorded.
5. URL reviews protected workflow and secret scope after the real Podcaster environment change.
6. jmservera records the production-owner conclusion after external evidence is linked.

Completion evidence: dated sign-off rows with finding-level dispositions and linked test,
workflow, or production observations.

## Accessibility acceptance

Owners: Fry and a named accessibility reviewer.

Required actions:

1. Identify the tested revision, production URLs, browser, operating system, screen reader, and viewport.
2. Review the retained axe and responsive reports from the final CI revision.
3. Complete keyboard-only navigation for primary navigation, consent, filters, charts, tools, and related links.
4. Complete screen-reader review for headings, landmarks, labels, status changes, chart alternatives, and errors.
5. Record each finding, severity, disposition, reviewer, and date.

Completion evidence: a retained review record combining automated results with keyboard
and screen-reader conclusions. Automated axe success alone does not close NFR-005.

Current automated evidence: the
[2026-08-03 automated evidence record](automated-acceptance-evidence-2026-08-03.md#automated-control-evidence)
ties successful axe, responsive, analytics-contract, Lighthouse, and Python checks to
the tested current-main revision. Manual keyboard and screen-reader conclusions remain
required.

## Protected real Podcaster run

Owners: URL, Hermes, a repository administrator, the Podcaster maintainer, and the
environment approver.

Repository controls now separate the automatic dry-run smoke from real generation. Real
generation is manual-only, requires an exact retained publish run and merged article,
and binds to the `podcaster-real-generation` environment. No real workflow was dispatched
as part of this implementation.

Required actions:

1. ~~Confirm downstream idempotency or authorize one exact eligible week and publish
  run ID.~~ Done 2026-08-04: jmservera authorized `2026-W32` / publish run
  `30782430176`; `candidate.content_sha256` verified to match the merged
  `content/weekly/2026/W32.md` on `main` before dispatch.
2. ~~Create or configure the `podcaster-real-generation` environment with required
  reviewer approval, no self-review, and deployment restricted to `main`.~~ Done
  2026-08-04: environment created with jmservera as required reviewer, self-review
  prevented, and deployment restricted to `main`.
3. ~~Configure the environment-scoped endpoint variable and API-key secret without
  recording their values.~~ Done 2026-08-04: `PODCASTER_ENDPOINT` variable and
  `PODCASTER_API_KEY` secret configured on the environment (values not recorded here).
4. Have URL and Hermes review the environment policy, secret scope, exact-manifest
  validation, and retained evidence fields. **Not yet done** — see the amended
  self-review note below; this review should also cover that amendment.
5. ~~Approve and dispatch one exact week and publish run ID only after maintainer
  authorization.~~ Done 2026-08-04: jmservera dispatched and approved run
  [30908778884](https://github.com/jmservera/SquadScope/actions/runs/30908778884)
  for `2026-W32` / `30782430176`.
6. ~~Retain the approver, week, manifest run ID and digest, article digest, Actions
  URL, downstream job ID, status, and final conclusion.~~ Done 2026-08-04 (see
  evidence table below).

**Self-review amendment (2026-08-04):** the environment's `prevent_self_review`
flag was set `true` when only one reviewer (jmservera) was configured, which
deadlocked approval on the first dispatch (30908570104, cancelled) because the
same account cannot approve its own run. jmservera authorized disabling
`prevent_self_review` (reviewer set and `main`-only branch restriction unchanged)
to unblock the redispatch. This weakens a previously-recorded security control and
should be included in the pending URL/Hermes environment-policy review (action 4).

Evidence for the completed run:

| Field | Value |
| --- | --- |
| Approver / dispatcher | jmservera |
| Week | `2026-W32` |
| Manifest run ID | `30782430176` |
| Manifest path / SHA-256 | `data/candidates/2026-W32/30782430176/publish-manifest.json` / `d5f1e4210e8e23c43970dc2da60552f3ae96e36ea2794a2121b0985078f9df0c` |
| Article path / SHA-256 | `content/weekly/2026/W32.md` / `b9806f1ff308dd94d8a9c39ab69c7224ccea586628bb49b8c82ded878d17f76b` |
| Actions run | [30908778884](https://github.com/jmservera/SquadScope/actions/runs/30908778884) |
| Downstream job ID / status | `podcast-2026-W32-d07bb05dc073` / accepted |
| Conclusion | success |

Completion evidence: one successful real downstream run after environment approval —
satisfied by the run above. Action 4 (URL/Hermes environment-policy review, including
the self-review amendment) remains open.

## Atomic publish acceptance

Owner: URL, with jmservera reviewing retained evidence.

The repository now includes an isolated proof that executes the production commit step
against a temporary local bare remote. Local validation passed normal publication,
byte-identical rerun, injected failure, unchanged-branch, accepted-tree identity, and
hydrated-tree identity scenarios. The production workflow also detects publish-relative
no-op state before creating immutable backups.

Required actions:

1. Review the atomic proof workflow and production no-op guard.
2. Dispatch the manual `Atomic publish proof` workflow for the reviewed revision.
3. Retain its JSON evidence and tree manifests with the workflow URL and reviewer conclusion.

Completion evidence: a successful retained manual proof artifact for the reviewed revision.

## Incremental generation cost acceptance

Owners: URL and the budget owner.

The report-only experiment now measures cumulative baseline, topic-hub, data-page, and
repository-page variants from immutable reviewed `main` and `publish` revisions. It does
not run generators, mutate rollout flags, or enforce a blocking threshold.

Required actions:

1. Review and dispatch the manual experiment with immutable reviewed SHAs.
2. Retain either three or five repetitions and the generated aggregate report.
3. Record the budget owner's conclusion before proposing any threshold or rollout.

Completion evidence: retained experiment artifacts and a dated budget-owner conclusion.

## Visual acceptance

Owner: Amy or another named visual reviewer.

The repository implementation removes Star Velocity clipping, stabilizes its scale across
filters, clarifies its semantics, adds mobile consent geometry coverage, serves compressed
static responses, extends lean CSS loading, and bounds Lighthouse concurrency without
weakening thresholds. Topic aggregation remains correct; historical topic backfill
promotion to `publish` remains owner-controlled. Follow the
[screenshot capture checklist](screenshots/README.md) against the final revision with
populated content, resolved consent state, desktop and mobile viewports, light and dark
themes, interaction states, and a dated reviewer conclusion.

Completion evidence: replacement visual matrix with revision metadata and an explicit
accept or reject conclusion. Screenshots alone are not approval.

## External metadata and feed validation

Owners: Amy for rendered metadata and jmservera for production access.

Current automated evidence: representative production pages have complete and
internally consistent social metadata and parseable page-specific JSON-LD. The root,
weekly, and representative topic feeds return 200 `application/xml`, parse as RSS,
and use absolute Claracle links. See the
[2026-08-03 automated evidence record](automated-acceptance-evidence-2026-08-03.md).

Required actions:

1. Validate the homepage and one representative article in supported social preview debuggers.
2. Validate representative article and breadcrumb markup with Google Rich Results Test.
3. Validate each relevant page type with Schema.org Validator.
4. Review the retained HTTP, media-type, XML, and absolute-link conclusions for the
  site, weekly, and representative topic feeds.
5. Retain the tested URLs, revision, tool conclusions, reviewer, and date without exposing credentials.

Completion evidence: dated social preview, structured-data, and production feed
conclusions with retained links or redacted records.

## Sponsor rollout decision

Owner: jmservera.

Record a separate decision for each flag. Do not use one blanket approval.

| Flag | Decision | Reviewed revision and evidence | Conditions | Date |
| ---- | -------- | ------------------------------ | ---------- | ---- |
| `dynamic_topic_creation` | Pending | Pending | Security disposition and approved canary required | Pending |
| `repo_pages` | Pending | Pending | Stable identity and lifecycle evidence required | Pending |

Completion evidence: dated approve, reject, or defer decisions identifying the exact
revision, evidence, conditions, and rollback owner for each flag.

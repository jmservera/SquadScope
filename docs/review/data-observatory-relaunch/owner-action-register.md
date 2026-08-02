---
title: Data Observatory Relaunch Owner Action Register
description: Sequenced owner actions and evidence requirements for Claracle relaunch gates that cannot be completed by repository automation
author: SquadScope Squad
ms.date: 2026-08-02
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

## Protected real Podcaster run

Owners: URL, Hermes, a repository administrator, the Podcaster maintainer, and the
environment approver.

Current evidence is split: run `30202586031` proves real accepted generation, while run
`30721575540` proves an environment-bound dry run. The `podcaster-release-smoke`
environment has no protection rules, and the real workflow is not environment-bound.

Required actions:

1. Confirm downstream idempotency or authorize one exact eligible week and manifest.
2. Define required reviewers and branch policy for a real-generation environment.
3. Bind the real generation job to that environment in a separately reviewed workflow change.
4. Review secret scope without recording secret values.
5. Approve and execute one real run.
6. Retain the approver, week, manifest run ID, article digest, Actions URL, downstream job ID, and final conclusion.

Completion evidence: one successful real downstream run after environment approval.

## Visual acceptance

Owner: Amy or another named visual reviewer.

Complete issue #622's factual checks and any layout-affecting #626 work before capture.
Then follow the [screenshot capture checklist](screenshots/README.md) against the final
revision with populated content, resolved consent state, desktop and mobile viewports,
light and dark themes, interaction states, and a dated reviewer conclusion.

Completion evidence: replacement visual matrix with revision metadata and an explicit
accept or reject conclusion. Screenshots alone are not approval.

## Sponsor rollout decision

Owner: jmservera.

Record a separate decision for each flag. Do not use one blanket approval.

| Flag | Decision | Reviewed revision and evidence | Conditions | Date |
| ---- | -------- | ------------------------------ | ---------- | ---- |
| `dynamic_topic_creation` | Pending | Pending | Security disposition and approved canary required | Pending |
| `repo_pages` | Pending | Pending | Stable identity and lifecycle evidence required | Pending |

Completion evidence: dated approve, reject, or defer decisions identifying the exact
revision, evidence, conditions, and rollback owner for each flag.

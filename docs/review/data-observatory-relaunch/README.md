---
title: Data Observatory Relaunch Acceptance Evidence
description: Bounded evidence index for repository implementation, external launch gates, security review, and visual acceptance of the Claracle relaunch
author: SquadScope Squad
ms.date: 2026-08-02
ms.topic: reference
keywords:
  - acceptance evidence
  - data observatory
  - release review
  - visual acceptance
estimated_reading_time: 8
---

## Release status

Repository implementation evidence is available, but relaunch acceptance is incomplete.
Dynamic topic creation and repository-page creation remain disabled in
`config/observatory.toml`. This index does not authorize either rollout.

External baseline and consent, remaining production responses, cross-repository run,
security sign-off, accessibility review, and visual acceptance evidence remain pending
as listed below. The GA4/GSC connection itself is complete.

The [owner action register](owner-action-register.md) sequences the remaining human and
protected-environment work without treating repository automation as approval evidence.

## Evidence principles

- Repository links prove checked-in implementation, not production behavior
- Command output proves only the revision and environment in which it ran
- Screenshots prove visible rendering only; they do not prove metadata, schema, network,
  consent, lifecycle, accessibility, or secret behavior
- External claims require a date, observed value or conclusion, actor, and retained link
- Secret values and private tokens must never appear in evidence

## Repository evidence

| Evidence                                                  | Status                      | Record                                                                      |
| --------------------------------------------------------- | --------------------------- | --------------------------------------------------------------------------- |
| Observatory operations, recovery, rollback, and ownership | Complete                    | [Data Observatory runbook](../../data-observatory-runbook.md)               |
| FR-052 tool selection and architecture rationale          | Complete                    | [Star Velocity Explorer ADR](../../decisions/adr-star-velocity-explorer.md) |
| Security and privacy surface review                       | Complete with open findings | [Security review](security-review.md)                                       |
| Hermes security acceptance                                | Pending                     | Security review sign-off table                                              |
| GA4 and GSC connection                                   | Complete                    | [Dated baseline](../../growth/ga4-gsc-baseline-2026-07-29.md)               |
| GA4 and GSC external baseline values                      | Pending                     | Dated baseline external evidence matrix                                     |
| Product delivery and rollout status                       | Pending acceptance          | [PRD](../../prds/claracle-data-observatory-relaunch.md)                     |
| Sponsor-approved lifecycle state                          | Pending                     | [BRD](../../brds/claracle-data-observatory-relaunch-brd.md)                 |
| Visual capture requirements                               | Pending                     | [Screenshot capture checklist](screenshots/README.md)                       |
| Owner-gated acceptance actions                            | Pending                     | [Owner action register](owner-action-register.md)                           |

## External acceptance matrix

| Gate                                  | Status  | Actor or access needed                              | Required evidence                                          |
| ------------------------------------- | ------- | --------------------------------------------------- | ---------------------------------------------------------- |
| GSC property verification             | Complete | jmservera                                          | Owner confirmed verification on 2026-08-02                 |
| GSC sitemap submission                | Complete | jmservera                                          | Root `sitemap.xml` submitted on 2026-08-02                 |
| GA4 consent-denied behavior           | Pending | jmservera and Hermes with production browser access | Network and cookie evidence from a private first visit     |
| GA4 consent-granted behavior          | Pending | jmservera and Hermes with production browser access | Expected request after consent                             |
| GA4 property, stream, and receipt      | Complete by owner attestation | jmservera                              | Intended production stream confirmed operational           |
| Social preview debuggers              | Pending | Reviewer with external debugger access              | Homepage and article conclusions with retained links       |
| Rich Results Test                     | Pending | Reviewer with external debugger access              | Article and breadcrumb conclusions with retained links     |
| Schema.org validator                  | Pending | Reviewer with external debugger access              | Relevant page-type conclusions with retained links         |
| Production sitemap response           | Complete | jmservera                                           | HTTP 200 `application/xml` observed on 2026-08-02          |
| Production feed responses             | Pending | jmservera with production access                    | Status, content type, date, and tested target              |
| Podcaster downstream run              | Pending | Podcaster maintainer and protected environment      | Successful downstream run conclusion and Actions link      |
| Accessibility review                  | Pending | Fry and accessibility reviewer                      | Automated results plus keyboard and screen-reader findings |
| Hermes sign-off                       | Pending | Hermes                                              | Dated disposition of security findings and NFR-004         |
| Sponsor rollout approval              | Pending | jmservera                                           | Dated approval identifying each flag separately            |

Issue #622 is non-blocking UX polish according to its issue contract. Issue #626 is
independent quality hardening whose existing thresholds remain unchanged. Both should be
completed before final visual recapture where their changes affect the rendered result,
but neither is represented as an unevidenced acceptance approval.

## Visual evidence status

The existing ten PNG files are retained as historical local captures. Their current index
did not include a revision, viewport dimensions, theme for each image, interaction state,
or evidence that topic membership was populated and unobscured. They are not accepted as
Phase 9 visual evidence.

Do not overwrite them until a browser run can render populated repository evidence and
the capture checklist can be completed. The replacement set must cover desktop, mobile,
dark theme, interaction state, and unobscured content. Topic captures must show real weekly
membership.

## Evidence still prohibited from screenshot substitution

Do not use the gallery as proof of:

- Canonical, Open Graph, Twitter, or Schema.org source correctness
- HTTP response status, headers, content types, sitemap, or feed validity
- GA4 network requests, cookies, consent state, or Realtime receipt
- GSC verification, submission, indexing, impressions, or clicks
- Lifecycle rename, archive, deletion confirmation, retention, or expiry
- Podcaster protected-environment execution
- Keyboard navigation, screen-reader output, or automated accessibility results

## Acceptance decision

Release acceptance is **pending**. Keep both rollout flags disabled until the named actors
provide the missing evidence and the PRD, BRD, security review, and this index all agree on
the approved state.

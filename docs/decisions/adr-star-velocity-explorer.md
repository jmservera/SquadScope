---
title: ADR for the Star Velocity Explorer
description: Decision record selecting a dependency-free browser explorer for repository star-velocity discovery on static hosting
author: SquadScope Squad
ms.date: 2026-07-30
ms.topic: reference
keywords:
  - architecture decision record
  - star velocity
  - client-side tool
  - static hosting
estimated_reading_time: 7
---

## Status

Accepted for implementation. Production acceptance remains separate and depends on populated visual,
accessibility, analytics-consent, and deployment evidence.

## Context

FR-052 requires a free client-side tool selected by discoverability value, delivery effort, and
static-hosting fit. Claracle already derives repository histories from checked-in weekly artifacts
and publishes through Hugo on GitHub Pages. A tool that requires a server, credentials, or a live
GitHub API request would violate that operating model and create avoidable quota and privacy risk.

Users need to find repositories by name, language, and topic, compare observed star movement, and
open the canonical GitHub project. The tool must remain useful without accounts or personal data.

## Decision

Ship the Star Velocity Explorer as a dependency-free JavaScript enhancement over a Hugo page and a
generated same-origin JSON dataset.

The browser implementation in `assets/js/star-velocity-explorer.js`:

- Fetches one same-origin data source declared by the rendered tool root
- Validates that the payload contains a repository array before rendering
- Filters by repository text, language, and topic entirely in memory
- Limits rendered results to 25 rows
- Creates elements through DOM APIs and assigns repository text through `textContent`
- Allows outbound links only when URL parsing yields HTTPS on `github.com`
- Uses no authenticated API, backend, secret, local storage, or user-submitted content
- Sends bounded `tool_interaction` actions only through the existing consent-aware Observatory analytics adapter

The generated dataset, not the browser, owns calculations and provenance. The UI labels values as
observed star change and latest stars. It does not claim real-time GitHub velocity.

## Tool comparison

| Option                                | Discoverability value                                           | Build and operating effort                                        | Static-hosting fit                               | Decision                                            |
| ------------------------------------- | --------------------------------------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------ | --------------------------------------------------- |
| Star Velocity Explorer                | High: repository-name and momentum intent maps to existing data | Low: generated JSON plus small browser module                     | Strong: same-origin static files, no credentials | Selected                                            |
| General trend dashboard               | Medium: broad browsing but weak query focus                     | Medium: more views, controls, and accessibility work              | Strong if precomputed                            | Defer until demand is measured                      |
| Live GitHub repository lookup         | High for fresh point queries                                    | High: API quota, caching, abuse, and credential handling          | Poor without a backend                           | Rejected                                            |
| Server-rendered analytics application | Medium to high                                                  | High: hosting, authentication, monitoring, and privacy operations | Incompatible with GitHub Pages constraint        | Rejected                                            |
| Embedded third-party charting service | Medium                                                          | Medium: vendor lifecycle, privacy, and embed governance           | Technically possible but externally dependent    | Rejected for the first tool                         |
| Download-only dataset                 | Medium for researchers, low for interactive discovery           | Low                                                               | Strong                                           | Retained as a complementary asset, not FR-052 alone |

## Consequences

The selected design has a small security and operational surface and deploys with the existing Hugo
site. It supports repository-focused search intent without adding infrastructure. Forks receive no
analytics identifier unless their own build supplies one.

The browser downloads the full bounded dataset before filtering, so dataset size must remain within
the static-site performance budget. Search and sorting capabilities are intentionally narrower than
a server-backed application. Freshness is limited to the latest successful generation and deploy.
The sparkline is an observed history visualization, not a forecasting model.

Generated data is public by design. Dataset fields must remain limited to public repository metadata
and derived aggregates. New fields require privacy and exposure review before publication.

## Lifecycle and failure behavior

Empty, missing, malformed, or failed data responses produce an inline status instead of partially
rendered results. Invalid outbound URLs resolve to a non-navigating `#` target. Filter actions never
modify the source dataset.

The tool follows the Observatory generation lifecycle. Dataset refresh happens before Hugo build;
deployment publishes the page, script, and JSON together. Repository rename, archive, deletion, and
retention semantics are resolved by the generator and lifecycle ledger before data reaches the tool.

## Rollback

Remove the tool from navigation and revert its page, generated dataset reference, script inclusion,
and analytics action definitions in one reviewed change. Keep durable repository pages and source
history intact. A rollback must not enable or disable dynamic topic or repository-page creation as a
side effect.

## Acceptance and follow-up

Repository implementation establishes the architectural decision, but release acceptance requires:

- A populated desktop, mobile, dark-theme, interaction, and unobscured capture set
- Keyboard and screen-reader review plus automated accessibility results
- A production same-origin data response and tool interaction check
- Consent-denied and consent-granted analytics verification
- Performance review as the generated dataset grows

Until those artifacts exist, the tool is implemented but visual and production acceptance remain
pending.

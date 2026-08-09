---
title: Claracle Homepage Module Hierarchy
description: Proposed BR-002 module selection, freshness, ownership, and fallback rules for the Claracle homepage
author: SquadScope Squad
ms.date: 2026-08-09
ms.topic: concept
keywords:
  - claracle
  - homepage
  - information architecture
estimated_reading_time: 5
---

## Approval Status

Approved by sponsor jmservera on 2026-08-09, with two revisions: the repository
and data evidence modules scale their item count with viewport width instead of
showing a fixed count, and the monthly and yearly modules show a short list
rather than a single entry. Both revisions are reflected in the module
definitions below. This satisfies the BR-002 approval requirement; it does not
by itself authorize the Phase 2 homepage build.

## Audience And Job

The homepage must let a technology decision-maker understand the most
important current changes and enter weekly, monthly, yearly, topic,
repository, and data evidence through concise, original summaries, matching
BR-002's acceptance criteria. Rendered HTML must remain useful without
client-side JavaScript and must avoid duplicated or padded content that would
weaken search discovery.

## Module Order

BR-008 requires Weekly, Monthly, and Yearly destinations first in primary
navigation. The homepage module order mirrors that priority while keeping the
current-week feature as the entry point, since it is the freshest evidence:

1. Hero
2. Current weekly feature
3. Weekly archive
4. Monthly rollups
5. Yearly rollups
6. Topic storylines
7. Repository evidence
8. Data and ranking evidence
9. Quick links

## Module Definitions

| Module | Selection rule | Freshness rule | Ownership | Fallback when empty |
|--------|-----------------|-----------------|-----------|----------------------|
| Hero | Static title and one-line positioning from site params | None; static content | Leela | Never empty; always renders |
| Current weekly feature | Most recent `weekly` page by date | Must be the latest published week | Leela | Render the existing no-report empty state; do not show a stale week as current |
| Weekly archive | Six most recent `weekly` pages excluding the current feature | Same as current feature | Leela | Section is omitted entirely when fewer than two weekly pages exist |
| Monthly rollups | Short list (three to five) of the most recent `monthly` pages plus a link to the monthly archive | Latest published months | Farnsworth | Section is omitted entirely when no monthly page exists |
| Yearly rollups | Short list (two to three) of the most recent complete `yearly` pages plus a link to the yearly archive | Latest published years with a complete BR-006 article | Farnsworth | Section is omitted entirely when no complete yearly article exists |
| Topic storylines | Six topics with the highest recent issue count from the taxonomy registry | Recomputed on every build from current taxonomy counts | Leela | Section is omitted entirely when no topic has at least one issue |
| Repository evidence | A representative sample from the BR-003 repository summary, sorted by recent momentum, with item count scaling by viewport width (narrower viewports show fewer items) | Same freshness as the BR-003 artifact | Leela | Section is omitted entirely when the repository artifact has zero records |
| Data and ranking evidence | Highlights per published ranking page (BR-004), with item count scaling by viewport width | Same freshness as each ranking artifact | Amy | Omit an individual ranking highlight when its artifact is stale or missing; omit the whole section only when none are available |
| Quick links | Static navigation to every top-level destination | None; static content | Leela | Never empty; always renders |

## Empty-Module Rule

No module renders an empty section wrapper, a placeholder card, or a loading
state in server-rendered HTML. A module either renders its real content or is
skipped entirely, matching the current weekly-archive pattern already used in
`layouts/index.html`. This avoids the layout shift and empty optional module
that BR-002 explicitly disallows.

## Metadata And Structured Data

The homepage must carry a unique title and description reflecting the current
week's evidence, valid structured data for the featured weekly article, and
exactly one `<h1>` heading. These requirements extend the existing rendered SEO
metadata contract validated by `tests/test_rendered_seo_metadata.py` to the
homepage's dynamic modules and do not introduce a separate metadata schema.

## Non-JavaScript Requirement

Every module above renders complete server-side HTML. No module depends on
client-side JavaScript to display its primary content, links, or summaries.
Progressive enhancement, where added later, may only extend interaction
(filtering, disclosure) without being required for comprehension.

## Sponsor-Resolved Questions

* Repository and data evidence modules scale their item count with viewport
  width rather than showing a fixed count.
* Monthly and yearly modules show a short list (three to five months, two to
  three years) rather than a single entry.

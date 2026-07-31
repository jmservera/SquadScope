---
title: Data Observatory Relaunch Screenshot Capture Checklist
description: Required browser states, viewports, themes, content prerequisites, and acceptance rules for refreshed relaunch visual evidence
author: SquadScope Squad
ms.date: 2026-07-30
ms.topic: how-to
keywords:
  - screenshots
  - visual acceptance
  - browser testing
  - data observatory
estimated_reading_time: 5
---

## Status

Visual acceptance is pending. The existing PNG files were inspected on 2026-07-30 and
were not refreshed.

The current topic capture shows `Recent weekly issues (0)`. The topic, repository, Star
Velocity Explorer, and interaction-detail captures are obscured by the cookie banner.
The set does not identify revision, viewport, theme, or interaction state per image and
does not contain mobile or dark-theme variants.

## Capture prerequisites

Do not replace the current files until all prerequisites are true:

- The tested revision is recorded
- Hugo and required generators complete from that revision
- The topic fixture contains real weekly membership from checked-in weekly frontmatter
- Repository and tool datasets are populated from checked-in artifacts
- Browser execution is available for desktop and mobile viewports
- Light and dark themes can be selected deterministically
- The cookie decision is completed before unobscured feature captures
- A separate consent capture is used when the banner itself is the subject
- Dynamic topic and repository-page rollout flags remain unchanged unless separately approved

## Required capture matrix

| Surface                | Desktop light | Mobile light | Desktop dark | Interaction state                             | Content requirement                                     |
| ---------------------- | ------------- | ------------ | ------------ | --------------------------------------------- | ------------------------------------------------------- |
| Home and consent       | Required      | Required     | Required     | Banner plus accepted or rejected state        | No content obscured outside the banner-specific capture |
| Topics index           | Required      | Required     | Required     | Topic navigation                              | Seed and promoted state identified                      |
| Topic hub              | Required      | Required     | Required     | Weekly issue link followed or focused         | At least one real weekly member visible                 |
| Repository page        | Required      | Required     | Required     | Lifecycle or provenance detail expanded       | Weekly history and provenance visible                   |
| Data ranking           | Required      | Required     | Required     | Ranking link or control state                 | Populated dated data visible                            |
| State-of page          | Required      | Required     | Required     | Relevant data link state                      | Populated dataset evidence visible                      |
| Embeddable chart       | Required      | Required     | Required     | Copy action and standalone frame              | Attribution remains visible                             |
| Star Velocity Explorer | Required      | Required     | Required     | Search, language, and topic filter states     | Matching populated results visible                      |
| Weekly article         | Required      | Required     | Required     | Related links and previous or next navigation | Real topic and repository links visible                 |
| Internal-link block    | Required      | Required     | Required     | Keyboard focus visible                        | Entire block unobscured                                 |

## Capture metadata

Record the following beside the replacement set in the acceptance evidence index:

- Git revision and local or production origin
- Capture date and browser version
- Exact viewport width and height
- Light or dark theme
- Consent state
- Interaction or filter state
- Source week or generated `as_of` value
- Known limitations

## Visual acceptance checks

- Text, controls, charts, and focus indicators do not overlap or clip
- Mobile navigation and controls remain usable without horizontal scrolling
- Theme contrast and visible focus are reviewed
- Topic membership matches weekly frontmatter
- Repository values and tool results match the generated dataset
- Cookie UI obscures content only in the banner-specific evidence
- Embed attribution and source backlink remain visible
- Long repository names and filter values fit their containers
- Empty, loading, malformed-data, and no-results states receive separate interaction evidence

## Evidence boundary

Screenshots do not prove source metadata, structured data, HTTP responses, analytics
requests, GSC state, lifecycle expiry, Podcaster execution, or accessibility conformance.
Use the dedicated evidence records and test output for those gates.

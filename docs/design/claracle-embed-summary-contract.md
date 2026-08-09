---
title: Claracle Embed Summary Contract
description: BR-007 data and interaction contract for sanitized repository summaries in embeddable reports
author: SquadScope Squad
ms.date: 2026-08-09
ms.topic: reference
keywords:
  - claracle
  - embeds
  - sanitization
  - accessibility
estimated_reading_time: 4
---

## Status

Defined. This contract satisfies the BR-007 Phase 1 definition requirement. It
does not authorize the Phase 4 embed implementation, which still requires its
own accessibility, keyboard, touch, zoom, and collision verification.

## Scope

Every embeddable report that displays a repository name must expose that name
as a direct GitHub link and make a sanitized generated-context summary of
approximately 160 characters available through hover, keyboard focus, touch
disclosure, and the accessibility tree, per BR-007.

## Data Contract

The shape is defined in
[`data/schemas/embed-summary.schema.json`](../../data/schemas/embed-summary.schema.json).
Each embed summary record carries:

* `repository_id` and `full_name`, matching the identifiers used by the
  repository record (BR-003) and ranking record (BR-004) contracts
* `github_url`, restricted to the `https://github.com/{owner}/{repo}` pattern
  so no non-GitHub or scheme-unsafe destination can be rendered
* `sanitized_summary`, truncated to at most 160 characters at a word boundary
* `accessible_text`, the complete sanitized text with no truncation, exposed to
  assistive technology even when the visual summary is shorter
* `sanitization_source`, a fixed pointer to the sanitizer that produced the
  text

## Sanitization Pipeline

1. Generated or repository-derived text passes through
   `scripts/sanitize_repo_content.py:sanitize_text()` first. This rejects
   injection phrases, escapes untrusted-content boundary markers, and caps
   length before the text is safe to store or render.
2. The sanitized text becomes `accessible_text` verbatim.
3. `sanitized_summary` re-truncates `accessible_text` to 160 characters at the
   nearest word boundary, appending an ellipsis only when truncation occurred.
   Display truncation never runs on unsanitized input.
4. No stage renders raw HTML; embeds treat `sanitized_summary` and
   `accessible_text` as plain text content only.

## Safe GitHub Link Contract

* `github_url` must match `^https://github\.com/[^/]+/[^/]+/?$`. Reject
  relative paths, other hosts, and non-`https` schemes.
* Rendered links use `rel="noopener noreferrer"` and do not embed the
  sanitized summary as the link's accessible name; the link's accessible name
  remains the repository's `full_name`.
* The summary disclosure is a separate interactive element from the link so a
  pointer or keyboard user can activate the link without first triggering the
  disclosure.

## Interaction Requirements Deferred To Phase 4

The following remain implementation-time verification, not part of this data
contract: hover disclosure, keyboard focus disclosure, touch disclosure,
Escape dismissal, disclosure persistence, screen-reader announcement order,
collision handling in narrow embeds, and behavior under 200% zoom and
`prefers-reduced-motion: reduce`.

<!-- markdownlint-disable-file -->
# Implementation Details: Claracle External Acceptance Gates

## Context

* Plan: `.copilot-tracking/plans/2026-08-03/claracle-external-acceptance-gates-plan.instructions.md`
* Research: `.copilot-tracking/research/2026-08-03/claracle-external-acceptance-gates-research.md`
* Owning acceptance package: `docs/review/data-observatory-relaunch/`

## Phase 1: Public Production Evidence

Use `urllib.request`, `html.parser.HTMLParser`, `xml.etree.ElementTree`, and
`json.loads` for public observations. Record status, content type, structural
counts, canonical and social consistency, and JSON-LD types. Do not retain GA or
GSC values.

Representative targets:

* Homepage
* One current weekly article
* One populated topic hub
* One data page
* One repository page
* Root sitemap, root feed, weekly feed, and topic feed

Success: all public targets return expected response types and parse without
structural errors, or failures are retained with exact conclusions.

## Phase 2: Automated Acceptance Controls

Run focused security, lifecycle, publication, hydration, pipeline, and Podcaster
tests before the full suite. Run Ruff lint and format checks. Confirm the exact-main
CI revision has successful Python, Production site, Publish hydration parity,
security scanning, CodeQL, and Checkov results.

Success: executable checks pass, and skipped browser or Hugo work is represented by
the exact-current-SHA CI evidence rather than an unsupported local claim.

## Phase 3: Acceptance Record Reconciliation

Create a dated automated evidence record under
`docs/review/data-observatory-relaunch/`. Link it from the acceptance index and
owner action register. Update only evidence status that automation or public
production observation can support. Do not alter pending human sign-off rows.

Success: readers can distinguish newly retained automated observations from the
remaining owner actions without reading tracking artifacts.

## Phase 4: Validation and Review

Run targeted tests, Ruff, `git diff --check`, and editor diagnostics. Confirm both
rollout flags remain false and review every user request against the final diff.

Success: validation passes and the review identifies exact next actors and evidence
needed for every gate that remains open.
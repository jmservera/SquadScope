---
description: "Implementation plan for the approved Claracle post-relaunch consolidation baseline"
applyTo: ".copilot-tracking/changes/2026-08-08/claracle-post-relaunch-consolidation-changes.md"
---

<!-- markdownlint-disable-file -->

# Implementation Plan: Claracle Post-Relaunch Consolidation

## Status

IMPLEMENTATION IN PROGRESS. The approved business baseline is
BRD-CLARACLE-003 version 1.1. Locally actionable governance, contract,
inventory, navigation, cost-projection, and yearly-editorial slices have passed
their affected automated gates. This plan does not authorize release,
production rollout, repository URL retirement, redirect-host migration, cost
publication activation, or acceptance on behalf of named human reviewers.

## User Requests

* Follow the RPI workflow using the approved post-relaunch consolidation BRD and
  the current repository context
* Convert the approved CR-01 through CR-06 and BR-001 through BR-009 baseline
  into an implementation-ready sequence
* Preserve the sponsor-approved V1.1 repository retirement policy, historical
  evidence, named ownership, release severity policy, and change control
* Keep implementation and release evidence separate from business approval

## Overview And Objectives

Deliver Claracle's redesigned experience as independently reviewable work while
preserving useful server-rendered Hugo output and adding scoped progressive
enhancement. The implementation must:

* Close carried-forward governance and operational requirements without
  rewriting historical relaunch evidence
* Establish shared design, data-contract, provenance, URL-state, accessibility,
  and performance foundations before dependent experiences
* Deliver homepage, yearly editorial, repository, ranking, embed, navigation,
  and cost improvements through binary gates
* Release one immutable candidate only after automated and named human evidence
  is complete and all severity-1 and severity-2 findings are resolved

## Context Summary

Controlling and supporting records:

* `docs/brds/claracle-post-relaunch-consolidation-brd.md`, version 1.1
* `docs/review/data-observatory-relaunch/status-of-record.md`
* `.copilot-tracking/brd-sessions/claracle-post-relaunch-consolidation.state.json`
* `.copilot-tracking/research/2026-08-08/claracle-post-relaunch-experience-research.md`
* `.copilot-tracking/research/subagents/2026-08-08/claracle-v1-implementation-handoff-research.md`
* `.copilot-tracking/research/subagents/2026-08-08/claracle-repository-retirement-policy-research.md`
* `.copilot-tracking/research/subagents/2026-08-08/claracle-redirect-boundary-alternatives-research.md`
* `.github/copilot-instructions.md`, `AGENTS.md`, `architecture.md`,
  `.squad/team.md`, and `.squad/routing.md`

The V1.1 retirement policy supersedes the handoff's earlier unconditional
redirect-host blocker. GitHub Pages remains acceptable when the approved URL map
contains no redirect rows and absent repository paths return true HTTP 404. A
redirect-capable deployment boundary becomes mandatory only for an approved
genuine-equivalent 301/308 row.

## Implementation Checklist

### [x] Phase 0: Governance And Independent Operations

<!-- parallelizable: true -->

* [x] Map every CR-01 and CR-02 historical accessibility or interaction finding
  to a redesigned-release test or named review with owner and severity
* [x] Verify CR-03 supersession remains tied to immutable revision `f37b49d` and
  that historical evidence is unchanged
* [x] Preserve the CR-05 invariant: `[repo_pages] enabled` remains `false`, and
  no story activates the low-information detail corpus
* [x] Execute CR-04 only as an independent, sponsor-gated dynamic-topic canary
  transaction with exact-revision approval, review, observation, and rollback.
  Activated via PR #684 (merge `bd1cf04`) on 2026-08-09: `dynamic_creation.enabled`
  flipped true bounded by `allow_topics = ["local-first"]`; `repo_pages` stays
  false. Hermes (security boundary sound) and URL (pipeline) re-reviewed the exact
  head `72782f5` and lifted their CR-06-sequencing REQUEST_CHANGES; sponsor
  jmservera approved. Rollback owner: jmservera — disable the flag AND revert the
  generated promotion transaction. Promotion executes on the next crawl-and-publish;
  observe that run and keep rollback ready
* [x] Repair and execute CR-06 with retained artifacts and a dated Q-01/NFR-009
  budget-owner conclusion. The hydration defect and its contract test are
  repaired; workflow dispatch (run 31305223877 on main `8f680f4`, publish
  `4120078d`, 3 repetitions, report-only) completed cleanly and its evidence is
  retained. Dated budget-owner conclusion recorded by jmservera on 2026-08-09:
  report-only, no blocking budget. The only material cost is `repository_pages`
  (Hugo ~8.8 ms/page, Pagefind ~2.4 ms/page); hubs and data pages are
  negligible. That corpus is the low-information detail set targeted for
  removal/reduction under Phase 3 migration (CR-05 keeps `repo_pages` disabled),
  so cost is dismissed as a launch gate. Re-evaluate only if Phase 3 retains or
  regenerates a repository-page corpus of meaningful size
* [x] Reconcile the narrower external-metadata delivery statement against the
  remaining external debugger and named-review evidence without reopening V1.1.
  Reconciled 2026-08-09 as evidence clarification, not a new business decision:
  the BRD "delivered" claim maps to delivered repository implementation of
  FR-032/033/034 (`layouts/partials/seo.html`, `head.html`; covered by
  `tests/test_rendered_seo_metadata.py`) plus retained production and
  source-level metadata evidence. The narrower remaining evidence — social-preview
  debuggers, Google Rich Results, Schema.org Validator, and named-reviewer feed
  conclusions — stays partial and owner-gated (Amy/jmservera), already tracked as
  the "External metadata and feed validation" launch gate in the status-of-record
  register and owner-action-register. Implementation-delivered and
  external-validation-pending are distinct states; V1.1 scope is unchanged

### [x] Phase 1: Shared Contracts And Design Foundation

<!-- parallelizable: true -->

* [x] BR-001: approve a Claracle design brief covering audience, page jobs,
  typography, color, spacing, motion, focus, reduced motion, contrast, tokens,
  layout concept, signature element, and self-critique
* [x] BR-002: approve the homepage module hierarchy with selection, freshness,
  ownership, fallback, metadata, structured-data, and no-JavaScript rules
* [x] BR-003: define the versioned repository artifact, normalized record,
  compatibility, provenance, freshness, filter, sort, search, sanitization,
  URL-state, and non-JavaScript contracts
* [x] BR-004: define a shared versioned envelope and typed records for all three
  ranking pages, including provenance, downloads, state, and interaction budgets
* [x] BR-006: define the annual evidence-pack and claim-to-source contracts,
  keeping bounded model input separate from complete published prose
* [x] BR-007: define the generated-context sanitization, approximately
  160-character display, complete accessible text, and safe GitHub-link contract
* [x] BR-009: define accepted-attempt resolution, retry and `model: none`
  exclusion, pricing basis, reconciliation, provenance, and 30-day freshness
* [x] Add documented schemas, representative fixtures, deterministic-generation
  checks, and future-version rejection for every public JSON contract

### [ ] Phase 2: Experience Shell, Homepage, Navigation, Editorial, And Cost

<!-- parallelizable: true -->

* [x] BR-001: implement the approved shared Hugo shell and token system with
  responsive, focus, reduced-motion, contrast, and no-JavaScript behavior.
  Applied the Field Notebook palette and typography fallback stacks in
  `assets/css/tokens.css` (propagates through `theme-vars.css` and
  `reset.css` to every page), reduced card radius to 6px, and added the
  static, no-JS Evidence Ruler signature element
  (`layouts/partials/evidence-ruler.html`). All new color pairs verified
  against WCAG AA contrast via a luminance-ratio script in both light and
  dark mode. Font assets remain on system fallback stacks; self-hosting
  licensed webfonts is a distinct follow-up per the design brief's own note.
  Visually verified via Playwright across homepage (light/dark/mobile), a
  weekly article, About, a Data listing, and a repository summary page
  (dark mode). Implementation, automated checks, and self-review complete;
  named sponsor/editorial acceptance of representative views is a separate,
  still-open state
* [x] BR-002: implement crawlable homepage summaries and links for weekly,
  monthly, yearly, topic, repository, and data coverage with empty-module removal.
  Added Monthly and Yearly rollup sections to `layouts/index.html` in the
  approved hierarchy order below the weekly archive, and Repository/Data
  evidence rail stubs wired to `site.Data.observatory.repository_summary`
  and `.ranking_summary`. Both rail sections currently render nothing
  (correctly, per the empty-module rule) because the Phase 3/4 versioned
  artifacts they depend on do not exist yet; they are forward-compatible
  and will populate automatically once BR-003/BR-004 data lands. Fixed a
  CSS grid regression from the added sections and a mobile label-overflow
  issue on the Evidence Ruler. Implementation and automated checks
  complete; named sponsor/editorial acceptance is a separate, still-open
  state
* [x] BR-008: order Weekly, Monthly, and Yearly first across desktop, mobile,
  keyboard, and accessibility-tree navigation while preserving all destinations
* [x] BR-006: remove cumulative clipping and generate a complete 1,200-1,800-word
  annual article with traceable claims, metadata parity, and editorial review.
  Root cause: `scripts/month_synthesis.py` had its own pre-fix `trim_words()`
  that appended an ellipsis at a raw word-count cutoff (distinct from the
  already-fixed sentence-safe `trim_words()` in `generate_yearly_narrative.py`),
  so every monthly narrative — and everything the yearly page derived from it —
  still clipped mid-sentence. Fixed `trim_words()` to select complete sentences
  within the word budget (no ellipsis), fixed a related mid-sentence period bug
  in the opening-paragraph template, regenerated all four 2026 monthly pages and
  `content/yearly/2026.md` (1,775-word narrative body, within range, zero "…"),
  and added regression tests. Named editorial review by Farnsworth/jmservera is
  still open; automated completeness and range checks pass
* [ ] BR-009: generate the reconciled public cost projection, fail publication
  on invalid or stale input, and render current provenance on About.
  Rendering is done (2026-08-10): `layouts/partials/cost-dashboard.html` now
  consumes only the new BR-009 `cost-summary.json` schema (currency, pricing
  basis, provenance, covered period, generation timestamp, reconciliation, and
  exclusions) and shows an honest "not currently available" state on missing,
  malformed, wrong-schema-version, or >30-day-stale data instead of a
  fabricated or outdated figure; the old hand-authored
  `data/metrics/cost-summary.json` placeholder is removed, so About "no longer
  consumes an independently maintained total." Generation/activation remains
  blocked: wiring `scripts/generate_cost_summary.py` into
  `crawl-and-publish.yml` requires the sponsor's legacy-row exclusion/cutover
  policy decision (`jmservera approves pricing-basis changes and exceptions`
  per the BRD), since the ledger's historical rows lack workflow identity
  permanently unless that policy is set
* [ ] Retain Calculon, Fry, Farnsworth, Zapp, Nibbler, URL, and sponsor evidence
  only from the roles routed to each acceptance surface

### [ ] Phase 3: Repository Inventory And Migration Candidate

<!-- parallelizable: false -->

* [ ] Reconcile 266 records, 267 source pages, 274 local rendered URLs, seven
  aliases, the live-count discrepancy, and any production-only repository URLs
* [ ] Collect URL Inspection, exact-page Search Analytics, sampled link,
  available first-party referral, internal-link, sitemap, canonical, content,
  and destination-equivalence evidence for every URL
* [ ] Record an approved keep, merge, redirect, or retire disposition for every
  canonical, alias, and production-only URL; ambiguous evidence blocks retirement
* [ ] Retain individual profiles only for differentiated content plus observed
  GSC demand or a known inbound link
* [ ] Select a redirect-capable host only if the approved map contains a genuine
  equivalent; otherwise prove absent paths return direct HTTP 404 on the current host
* [ ] Implement deterministic BR-003 artifact generation, authoritative Hugo
  summary and links, search/filter/sort enhancement, URL state, and empty/error states
* [ ] Generate redirects only from approved exceptional rows and verify one-hop,
  atomic deployment, sitemap, canonical, internal-link, custom-404, and rollback behavior
* [ ] Remove low-information details only in the same reviewed migration
  transaction; never enable CR-05 as an intermediate step

### [ ] Phase 4: Ranking Data, Visualization Selection, And Embeds

<!-- parallelizable: true -->

* [ ] BR-004: deterministically generate all three ranking artifacts and retain
  authoritative Hugo summaries, tables, attribution, and downloads
* [ ] BR-004: add page-scoped filter, sort, reset, useful URL state, exploration,
  status, empty, malformed, unavailable, stale, and future-version behavior
* [ ] BR-005: state each analytical question and intended inference, then create
  dense, sparse, tied, zero, long-label, top-10, top-100, and mobile fixtures
* [ ] BR-005: compare at least two suitable representations per question and
  retain the five-member proxy prompts, raw answers, scoring, and observations
* [ ] BR-005: implement only representations meeting the four-of-five threshold,
  with responsive non-color encoding and an equivalent accessible table
* [ ] BR-007: render repository names as direct GitHub links and expose the same
  sanitized summary through hover, focus, touch, Escape, and accessibility tree
* [ ] Validate keyboard, screen reader, touch, zoom, collision, narrow embed,
  privacy, performance, no-JavaScript, and control-occlusion behavior

### [ ] Phase 5: Integrated Release Candidate And Outcome Evidence

<!-- parallelizable: false -->

* [ ] Build one immutable candidate revision containing the approved G2-G5 work
* [ ] Run Python, Hugo, link, schema, content, security, workflow, accessibility,
  visual, no-JavaScript, responsive, performance, and privacy gates as applicable
* [ ] Capture named keyboard, live screen-reader, touch, zoom, reduced-motion,
  editorial, SEO migration, security, data-integrity, and sponsor dispositions
* [ ] Block release for any unresolved severity-1 or severity-2 finding; assign
  owner and due date to lower findings; document sponsor exceptions with expiry
* [ ] Record sponsor GO and rollback readiness before production deployment
* [ ] Capture the seven-day smoke, 28-day migration and organic evidence,
  three-month migration and organic evidence, and six-month SEO outcome evidence

## Dependencies

* Frontend discovery and implementation use `.github/skills/frontend-design/SKILL.md`
* Generated-content changes require Nibbler prompt-injection and AI-safety review
* Workflow, infrastructure, hosting, Docker, or deployment changes require URL
  pipeline review and Hermes security review
* Architecture and final code review route to Leela; testing routes to Fry
* Repository retirement requires URL-level external evidence that may not be
  available in the repository and cannot be inferred from aggregate analytics
* Redirect implementation depends on the approved URL map, not on a speculative
  hosting migration
* CR-04 and CR-06 are independent operational lanes and do not authorize release

## Validation Strategy

Use the smallest focused checks after each story, then run all affected gates
before pushing:

* Python: `ruff check .`, `ruff format --check .`, and `pytest tests/`
* Hugo/content: `hugo --minify` plus rendered-output and internal-link inspection
* Workflow/IaC/container: repository-pinned Checkov, Zizmor, and container build
  checks where applicable
* Data contracts: schema validation, deterministic regeneration, malformed,
  unavailable, stale, duplicate, empty, and future-version fixtures
* Frontend: server-rendered/no-JavaScript assertions, interaction tests, visual
  regression, accessibility automation, and named manual evidence

## Success Criteria

* Every CR-01 through CR-06 and BR-001 through BR-009 requirement maps to a
  delivered story, retained evidence, and accountable disposition
* Business approval, implementation completion, named acceptance, release GO,
  and production outcome evidence remain distinct states
* No low-information repository detail page is emitted after migration, and
  every affected URL has an approved evidence-backed disposition
* Essential content remains useful in Hugo HTML without client-side JavaScript
* Public JSON and cost artifacts are versioned, deterministic, traceable, fresh,
  schema-valid, and fail closed when required inputs are invalid
* One immutable release candidate passes the BRD severity policy and all
  applicable automated and named human gates

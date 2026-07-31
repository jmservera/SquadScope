<!-- markdownlint-disable-file -->
# Claracle Data Observatory Relaunch Implementation Review

## Review Metadata

| Field | Value |
|---|---|
| Review date | 2026-07-29 |
| PRD | `docs/prds/claracle-data-observatory-relaunch.md` |
| BRD | `docs/brds/claracle-data-observatory-relaunch-brd.md` |
| Implementation plan | Missing from `.copilot-tracking/plans/` |
| Changes log | Missing from `.copilot-tracking/changes/` |
| Research document | Not found |
| Visual acceptance evidence | `docs/review/data-observatory-relaunch/README.md` and ten screenshots |
| Comparison basis | Current `main` working tree and rendered screenshots |

## Overall Status

**Needs Rework**

The implementation provides substantial static-site capability and passes the available Python quality gates, but the relaunch does not meet its launch acceptance criteria. The central weekly-to-topic path is not operational in current content, most generated surfaces are not integrated into a recurring publish path, repository lifecycle retention is not enforced, and required external SEO, analytics, performance, accessibility, security, and downstream handoff evidence is missing.

The implementation plan and changes log required for traceable RPI validation are absent. This review therefore uses the PRD requirement groups as validation units and records the missing artifacts as a process deviation.

## Findings Summary

| Severity | Count |
|---|---:|
| Critical | 7 |
| Major | 13 |
| Minor | 3 |

## Findings

### Critical Findings

#### Current weekly content does not populate evergreen topic hubs

`content/weekly/2026/W31.md` and all other committed weekly issues have no `topics` frontmatter. The topic registry therefore reports zero uses, and screenshots 02 and 03 show zero matching hubs and weekly issues. Generator logic exists, but the accepted content and publish path do not demonstrate FR-001 through FR-003.

#### Dynamic topic creation is not operational

The configured and tested helper is not invoked by a workflow. Candidate discovery depends on existing canonical topic membership, so a genuinely new crawl or analysis signal cannot enter the automatic promotion path. This fails FR-004.

#### Repository lifecycle and retention are not enforced

Current artifacts do not provide stable identity, archive, or deletion state; lifecycle overrides are empty; and repository regeneration deletes generated directories before rewriting eligible pages. A calculated `retained_until` value does not preserve a deleted page for three years. This fails FR-022.

#### Topic hubs lack required page-appropriate entity schema

Topic pages receive BreadcrumbList markup but no hub entity schema. Data and repository pages use generic Article schema rather than an explicitly selected page-appropriate type. FR-033 is not complete.

#### GSC and GA4 operational acceptance is incomplete

The dated launch baseline explicitly leaves GSC verification, sitemap submission, GA4 Realtime receipt, indexed-page count, and all baseline values incomplete or `TBD`. Deploy wiring is present, but FR-035 and NFR-007 require completed external acceptance.

#### Most generated surfaces have no recurring publish integration

No workflow invokes topic lifecycle, repository-page, dataset, or trend-explorer generation. Only data-page generation is scheduled, and that workflow stops at an unmerged pull request. Deterministic scripts without an operational update path do not satisfy the future-state pipeline or cadence requirements.

#### Podcaster compatibility lacks release evidence

Payload unit tests pass, but the cross-repository smoke workflow is dispatch-only, does not gate deployment, and has no supplied successful run for the relaunch state. NFR-002 requires unchanged handoff smoke behavior, not only local payload compatibility.

### Major Findings

#### Required implementation traceability artifacts are missing

No implementation plan exists under `.copilot-tracking/plans/`, and no changes log exists under `.copilot-tracking/changes/`. This prevents phase-by-phase comparison against an approved implementation plan and makes the visual acceptance document the only shipped-feature inventory.

#### Topic highlights are manually authored

Hugo can aggregate topic members once frontmatter exists, but dataset highlights are static hub parameters. No publish step updates recent highlights from weekly data as required by FR-003.

#### Repository pages omit curated topic-hub links

Repository pages link weekly issues and related repositories but expose raw GitHub topics only as `/tags/` links. FR-020 requires links to relevant hubs as well as issues.

#### Social image dimensions are incomplete

The active SEO partial emits Open Graph dimensions only for the fallback image. Pages with custom OG, featured, or cover images omit `og:image:width` and `og:image:height`, contrary to FR-032.

#### SEO regression coverage is narrower than the launch contract

Site-wide tests enforce unique titles and descriptions, but do not comprehensively assert canonical correctness, social tags, JSON-LD type and parseability by page class, sitemap validity, or every root/topic feed.

#### Weekly-link presence is not regression-tested

The broken-link checker validates links that exist but cannot detect removal of required previous/next, topic, or applicable repository link groups. Only W29 has supplied rendered evidence for FR-040.

#### The required client-tool design spike is absent

The Star Velocity Explorer is static and client-side, but no checked-in decision compares discoverability value, effort, and static-hosting fit. The PRD still marks tool selection open after the tool is presented as delivered.

#### Performance, accessibility, and scalability gates lack evidence

No Lighthouse Performance result covers hub, data, or repository pages; no axe result covers the new surfaces; and no measured Hugo/Pagefind build budget exists. The current Lighthouse runner omits these page classes and does not enforce the PRD's performance threshold.

#### Analytics instrumentation is incomplete

Consent-gated page views are wired, but `dataset_download`, `chart_embed_view`, and `tool_interaction` events from the PRD instrumentation plan are absent.

#### Required security review is absent

Safe Hugo rendering, sanitization, same-origin data, and safe DOM construction are present, but no relaunch-specific Hermes review closes NFR-004 and risk R-05.

#### Rollout state conflicts with the PRD

The PRD specifies `dynamic_topic_creation` and `repo_pages` default-off until validation. Dynamic creation is enabled in configuration, no repository-page feature flag exists, and Wave dates and gate sign-offs remain absent.

#### Visual acceptance claims exceed screenshot evidence

The gallery labels empty topic pages as delivered dynamic lifecycle evidence and describes metadata and structured data as visible in screenshots. Screenshots cannot verify head tags or JSON-LD, several are obscured by the consent modal, and no mobile, dark-theme, network, accessibility, or interaction captures are included.

#### Data regeneration still requires intervention

The monthly data-page workflow creates a pull request but does not publish it. This is inconsistent with FR-011's “without manual intervention” acceptance wording unless the requirement is revised to make review and merge an intentional control point.

### Minor Findings

#### Social debugger and feed acceptance evidence is absent

No retained Facebook/X debugger result or production XML validation proves crawler rendering, sitemap reachability, and feed validity.

#### Operational ownership is not actionable

Roles are named, but no relaunch runbook defines dashboard locations, weekly review steps, generation-failure escalation, or owner handoffs.

#### BRD, PRD, and visual-review statuses are internally inconsistent

The BRD is “Ready for review,” the PRD is “Ready” with two unresolved design items, and the gallery requests a final visual acceptance pass while launch-blocking gates remain incomplete. These states should not all describe the same release point.

## PRD Validation Units

| Unit | Scope | Status |
|---|---|---|
| 1 | Topic hubs and taxonomy, FR-001 through FR-004 | Failed: 0 of 4 fully accepted |
| 2 | Data and repository pages, FR-010 through FR-022 | Partial: 1 passed, 2 partial, 2 failed |
| 3 | Technical SEO and analytics, FR-030 through FR-035 | Partial: code readiness exists, launch acceptance incomplete |
| 4 | Internal linking and link validation, FR-040 through FR-041 | Partial: FR-041 passed, FR-040 partially evidenced |
| 5 | Linkable assets and README, FR-050 through FR-060 | Partial: 4 passed, FR-052 partial |
| 6 | Non-functional, security, operations, and rollout | Failed |

Detailed evidence is recorded in `.copilot-tracking/reviews/rpi/2026-07-29/claracle-data-observatory-relaunch-001-validation.md` through `claracle-data-observatory-relaunch-006-validation.md`.

## Implementation Quality

### Strengths

* The static, no-backend architecture is preserved.
* Data-page, repository-page, dataset, and tool exporters are deterministic and well covered by Python tests.
* Downloadable dataset licensing, citation, provenance, and stable paths meet their acceptance criteria.
* The embed implementation preserves a visible source backlink.
* Ruff and the complete Python test suite pass.

### Limitations

The required `Implementation Validator` was invoked twice but failed at the execution backend before it could inspect files or create its output artifact. No unsupported quality claims from those failed runs are included. Quality conclusions above are synthesized from the six completed RPI validations and executable checks.

## Validation Commands

| Command | Result |
|---|---|
| `python3 -m pytest -q tests/` | Passed: 1,317 passed, 10 skipped |
| `python3 -m ruff check .` | Passed |
| `python3 scripts/generate_data_pages.py --check` | Passed |
| `python3 scripts/export_trend_explorer_data.py --check` | Passed |
| VS Code diagnostics on implementation and review paths | Passed: no errors |
| `hugo --minify` | Not run: Hugo is unavailable locally |
| Rendered internal-link check | Not run: requires a fresh Hugo build |

The working tree also contains untracked `.test-workspaces/` and `uv.lock`. They were not modified or removed because their ownership predates or is unrelated to this review.

## Missing Work and Deviations

* Add the required implementation plan and changes log or reconstruct equivalent traceability from relaunch issues and pull requests.
* Regenerate or backfill weekly topics, then connect registry refresh and dynamic promotion to publishing.
* Integrate repository, dataset, and tool-data generation into a controlled recurring workflow.
* Implement durable repository identity, lifecycle detection, redirects, tombstones, and enforced retention.
* Complete page-appropriate schema, custom-image social dimensions, and comprehensive rendered SEO tests.
* Complete GSC, GA4, Rich Results, social debugger, Lighthouse, axe, build-timing, security-review, and Podcaster smoke acceptance.
* Reconcile rollout flags and update BRD, PRD, and visual-review statuses to the actual release state.

## Follow-Up Work

### Deferred From Scope

* Quantify incremental Hugo/Pagefind generation cost and define a CI budget.
* Decide whether scheduled pull-request creation is the intended publication control or whether FR-011 requires automated merge/publication.

### Discovered During Review

* Add required-link presence assertions for rendered weekly pages.
* Record the Star Velocity Explorer selection rationale in a repository design decision.
* Add the three planned custom analytics events.
* Add an operational runbook for regeneration, monitoring, and escalation.

## Reviewer Notes

The strongest implementation areas are the data pages and linkable assets. The release should not be accepted until the topic path, recurring generation, lifecycle handling, and launch gates are closed and fresh rendered evidence replaces the current empty-hub screenshots.
---
title: Claracle Data Observatory Relaunch PRD Unit 1 Validation
description: Validation of FR-001 through FR-004 against repository implementation and acceptance evidence
ms.date: 2026-07-29
ms.topic: review
---

## Validation Scope

Status: Failed

This review validates PRD unit 1, FR-001 through FR-004. The required
implementation plan and changes log were not available, so the PRD is treated
as the specification, the BRD as business context, the visual review as claimed
acceptance evidence, and the current working tree as implementation evidence.

The implementation evidence is committed on `main` at
`83000a4ffab8ee83906b81a3f6bb3034a14156b4`. The only untracked repository path
during validation was this review document. No implementation file was changed.

The governing requirements are
[FR-001 through FR-004](../../../../docs/prds/claracle-data-observatory-relaunch.md#L114-L117)
and their business counterparts
[BR-001 through BR-004](../../../../docs/brds/claracle-data-observatory-relaunch-brd.md#L139-L147).

## Requirement Comparison

### FR-001 Evergreen Topic Hubs

Status: Partial

Five durable hub source pages exist:

* `content/topics/ai-coding-agents/_index.md:1-23`
* `content/topics/mcp-ecosystem/_index.md:1-22`
* `content/topics/open-source-llms/_index.md:1-23`
* `content/topics/developer-tools/_index.md:1-23`
* `content/topics/ai-agents-in-healthcare/_index.md:1-22`

The pages contain distinct titles, descriptions, editorial material, dataset
highlights, and related repositories. Hugo defines the `topic` taxonomy and
HTML/RSS term outputs in `hugo.toml:10-20`. The topic layout exposes per-topic
RSS and dataset highlights in `layouts/topics/list.html:13-50`.

The aggregation acceptance criterion is not met. The registry reports zero
uses and zero weekly issues for all five hubs in
`data/taxonomy/topics.json:1-103`. The terms page consequently enters its empty
state in `layouts/topics/terms.html:24-50`. Screenshot 02 visibly says
"No topic hubs have issue matches yet," while screenshot 03 visibly reports
"Recent weekly issues (0)" and "No weekly issues yet."

Missing or deviated work:

* Populate the hubs with related weekly issues, including the latest committed
	issue
* Regenerate and verify non-empty per-topic RSS feeds after membership exists
* Replace the zero-match screenshots before treating the visual review as
	acceptance evidence

### FR-002 Emit Topics From Generation

Status: Failed

The implementation has unit-level emission logic. It maps known tag aliases to
the canonical vocabulary in `scripts/generate_content.py:194-255`, emits the
field in `scripts/generate_content.py:285-293`, and has focused assertions in
`tests/test_generate_content_topics.py:25-57`.

The committed output does not satisfy acceptance. The latest weekly issue has
tags but no `topics` field in `content/weekly/2026/W31.md:1-13`. Its source
analysis contains `ai-agents`, `agent-skills`, `developer-tools`, and
`simulation` signals in `data/analyzed/2026-W31-summary.md:1-12`, all of which
have canonical aliases in `data/taxonomy/topics.json:3-63`. A repository-wide
inspection found no `topics:` frontmatter in any file under `content/weekly/`.

The production workflow invokes generation in
`.github/workflows/crawl-and-publish.yml:1077-1108`, and the promotion guard
writes candidate content to the canonical weekly path in
`scripts/promotion_guard.py:527-561`. The current source can therefore emit the
field, but the accepted content set was not regenerated or backfilled and does
not demonstrate the required end-to-end result.

Missing or deviated work:

* Regenerate or backfill W31 and applicable historical issues with canonical,
	resolvable topics
* Add a release assertion that promoted weekly content contains expected topic
	membership when known aliases are present
* Verify that the rendered weekly page links to each emitted hub and that the
	link gate passes

### FR-003 Auto-Update Hubs on Publish

Status: Failed

The Hugo taxonomy layout would list weekly members automatically when they have
topic frontmatter. It selects weekly pages in `layouts/topics/list.html:1-2`
and renders recent issues in `layouts/topics/list.html:99-117`.

No committed weekly page is a topic member, so the latest publish did not
update any hub. Dataset highlights are static hub parameters rendered by
`layouts/topics/list.html:37-50`; for example, the MCP highlights are manually
authored in `content/topics/mcp-ecosystem/_index.md:8-15`. No publish step
updates those highlights from weekly data.

Missing or deviated work:

* Make topic membership part of every promoted weekly publish
* Define and implement automatic latest-highlight updates, or narrow the
	requirement and acceptance language if highlights are intentionally static
* Add an end-to-end publish test that begins with a new weekly issue and proves
	the affected hub and RSS output changed without a manual hub edit

### FR-004 Dynamic Topic Lifecycle

Status: Failed

The isolated lifecycle components cover several requirements. The threshold is
configuration in `config/observatory.toml:18-31`. The manager is additive,
checks recency and the threshold, writes creation logs, and promotes qualifying
registry entries in `scripts/manage_topic_hubs.py:211-258`. Focused tests cover
threshold creation, continuity, registry promotion, and logging in
`tests/test_topic_hubs.py:46-158`.

The automatic lifecycle is not connected to publishing. No workflow under
`.github/workflows/` invokes `scripts/taxonomy_registry.py` or
`scripts/manage_topic_hubs.py`. The publish transaction only watches and stages
analyzed data, candidates, metrics, published data, and weekly/monthly/yearly
content in `.github/workflows/crawl-and-publish.yml:1152-1219`; it does not
stage `data/taxonomy/`, `data/topic-hubs/`, or `content/topics/`.

Candidate discovery is also circular:

* The registry learns topic candidates only from weekly `topics` frontmatter in
	`scripts/taxonomy_registry.py:150-163`
* Raw repository topics are recorded only as tags in
	`scripts/taxonomy_registry.py:167-179`
* Generation selects from the registry's existing topic vocabulary and rejects
	unknown explicit topics in `scripts/generate_content.py:194-255`
* The checked-in topic registry contains only the five already-promoted seed
	hubs, each with zero usage, in `data/taxonomy/topics.json:1-103`

As a result, a genuinely new trend from crawl or analysis signals cannot enter
the non-hub candidate set through the automated path, and the manager is not
run even if a candidate is inserted by another process. No configured creation
log exists under `data/topic-hubs/`.

Missing or deviated work:

* Derive candidate topics from existing crawl and analysis signals without
	requiring prior canonical topic membership
* Run registry refresh and dynamic promotion in the weekly publish path in the
	correct order
* Commit or publish registry, log, and generated hub changes
* Add an end-to-end test that introduces a new signal in four distinct recent
	issues and observes hub creation, logging, persistence, and later issue
	aggregation

## Findings

### Critical Findings

#### F-001 Topic emission is absent from accepted content

FR-002 is a Must requirement and the dependency for FR-001 aggregation and
FR-003 updates. W31 lacks `topics` despite having canonical source signals, all
weekly content lacks the field, the registry has zero hub uses, and both topic
screenshots show zero matches. Unit-level generator logic does not satisfy the
published-content acceptance criterion.

Evidence:

* `docs/prds/claracle-data-observatory-relaunch.md:114-116`
* `content/weekly/2026/W31.md:1-13`
* `data/analyzed/2026-W31-summary.md:1-12`
* `data/taxonomy/topics.json:1-103`
* `docs/review/data-observatory-relaunch/screenshots/02-topics-index.png`
* `docs/review/data-observatory-relaunch/screenshots/03-topic-hub-mcp.png`

#### F-002 Dynamic creation cannot operate automatically

FR-004 has a configured and tested helper, but no production invocation and no
automated source for genuinely new topic candidates. The implementation cannot
meet the required threshold-triggered creation behavior from weekly signals.

Evidence:

* `config/observatory.toml:18-31`
* `scripts/manage_topic_hubs.py:211-258`
* `scripts/taxonomy_registry.py:150-179`
* `scripts/generate_content.py:194-255`
* `.github/workflows/crawl-and-publish.yml:1077-1219`

### Major Findings

#### F-003 Hub updates are only conditionally automatic and highlights are manual

Hugo automatically renders taxonomy members, but no weekly member currently
exists. The "latest highlights" portion is authored in hub frontmatter rather
than updated from weekly data. FR-003 therefore has a rendering mechanism but
not the accepted publish behavior.

Evidence:

* `docs/prds/claracle-data-observatory-relaunch.md:116`
* `layouts/topics/list.html:1-2`
* `layouts/topics/list.html:37-50`
* `layouts/topics/list.html:99-117`
* `content/topics/mcp-ecosystem/_index.md:8-15`

### Minor Findings

#### F-004 Claimed visual acceptance overstates completion

The review README labels screenshots 02 and 03 as delivered evidence for
FR-001, FR-003, and FR-004 in
`docs/review/data-observatory-relaunch/README.md:20-21`, but the screenshots
display zero hub matches and zero weekly issues. They prove page rendering and
continuity of an empty seed hub, not aggregation, publish updates, or dynamic
creation.

## Coverage Assessment

No FR is fully accepted: one is Partial and three are Failed.

* FR-001: Partial. Five hub shells, metadata, dataset context, and RSS routes
	exist, but weekly aggregation is empty
* FR-002: Failed. Emission logic exists, but accepted weekly output does not
	contain the field or populate hubs
* FR-003: Failed. Conditional Hugo rendering exists, but the latest publish did
	not update hubs and highlights remain manual
* FR-004: Failed. Configuration, helper code, and unit tests exist, but candidate
	discovery and production orchestration are missing

Acceptance coverage is 0 of 4 FRs fully satisfied. The phase is not ready for
acceptance because the central weekly-to-topic through-line is not operational.

## Validation Limits And Recommended Next Validations

This session used repository reading, visual inspection, and Git state analysis.
It did not execute tests or regenerate artifacts because the RPI protocol limits
validation to reading and analysis.

Recommended next validations:

* Regenerate W31 in an isolated workspace and compare emitted topics with its
	source tags
* Run the focused topic generation and lifecycle tests
* Exercise a full weekly publish fixture through promotion, registry refresh,
	dynamic hub creation, Hugo build, and link checking
* Verify that a fifth recent occurrence creates a candidate hub when the
	threshold is changed from four to five without a code edit
* Build the site after backfill and verify non-zero topic index cards, MCP hub
	issue cards, and non-empty per-topic RSS

## Clarifying Questions

* Was W31 published before the topic-emission change, and is backfilling W31 and
	earlier issues part of the relaunch release criterion?
* Which workflow is intended to invoke taxonomy registry refresh and dynamic
	hub creation? No invocation is present in the current workflow set.

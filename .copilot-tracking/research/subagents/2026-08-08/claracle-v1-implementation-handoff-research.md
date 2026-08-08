<!-- markdownlint-disable-file -->

# Claracle V1 Implementation Handoff Research

## Status

Complete as of 2026-08-08. The investigation was read-only except for this report.
No implementation, BRD, status, session-state, or primary-research file was modified.

## Research Scope

* Identify every approved V1 decision added after the prior research baseline.
* Classify former gaps as closed decisions or remaining delivery evidence.
* Detect contradictions and implementation-planning blockers.
* Define implementation epics, stories, dependency order, owners, binary gates, and cheapest validations.
* Reassess alternatives and the selected progressive-enhancement architecture against V1 choices.
* Identify factual and citation updates required in the primary research.

## Executive Findings

The BRD is ready for implementation planning at the business-policy level. Version 1.0
records sponsor approval, closes the prior product and governance questions, assigns one
accountable owner to each BR, defines objective targets, and explicitly preserves the
selected server-rendered progressive-enhancement architecture. The approval does not
claim that designs, schemas, migration evidence, implementation, named acceptance, or
production outcomes already exist. That distinction is explicit in
`docs/brds/claracle-post-relaunch-consolidation-brd.md:199-212` and
`.copilot-tracking/brd-sessions/claracle-post-relaunch-consolidation.state.json:36-45`.

One material planning blocker remains. BR-003 requires one-hop hosting-layer 301/308
redirects and rejects Hugo meta refresh, but Claracle currently publishes a static Hugo
artifact directly to GitHub Pages. The deployment workflows contain no redirect-capable
edge or origin layer. Repository evidence is in `architecture.md:10-20`,
`.github/workflows/deploy-site.yml:67-67`, and
`.github/workflows/deploy-site.yml:195-215`. GitHub describes Pages as static hosting,
and Hugo documents that aliases default to client-side `meta refresh`; server redirects
require host-specific configuration. BR-003 migration cannot be scheduled for production
until an implementation-compatible redirect host is selected or the sponsor approves a
material policy change.

The selected implementation approach remains correct for page and data architecture:
shared normalized versioned artifacts, authoritative Hugo HTML, and scoped JavaScript
enhancement. V1 strengthens this choice in
`docs/brds/claracle-post-relaunch-consolidation-brd.md:137-161` and
`docs/brds/claracle-post-relaunch-consolidation-brd.md:163-177`. The redirect-host gap
is a deployment-boundary issue, not evidence for a client-first application.

## Evidence Compared

### Approved controlling records

* BRD control, history, and approval:
  `docs/brds/claracle-post-relaunch-consolidation-brd.md:20-40` and
	`docs/brds/claracle-post-relaunch-consolidation-brd.md:199-212`
* Approved objectives, requirements, decisions, and implementation guidance:
  `docs/brds/claracle-post-relaunch-consolidation-brd.md:113-161`
* Release policy and delivery traceability:
  `docs/brds/claracle-post-relaunch-consolidation-brd.md:163-197`
* Historical disposition and remaining operational evidence:
  `docs/review/data-observatory-relaunch/status-of-record.md:27-52` and
  `docs/review/data-observatory-relaunch/status-of-record.md:79-101`
* Session decision record and next actions:
  `.copilot-tracking/brd-sessions/claracle-post-relaunch-consolidation.state.json:24-88`

### Prior research baseline

* Primary research selected approach and earlier gaps:
  `.copilot-tracking/research/2026-08-08/claracle-post-relaunch-experience-research.md:24-55`,
  `.copilot-tracking/research/2026-08-08/claracle-post-relaunch-experience-research.md:132-182`,
	and `.copilot-tracking/research/2026-08-08/claracle-post-relaunch-experience-research.md:255-296`
* Code surfaces and root causes:
  `.copilot-tracking/research/subagents/2026-08-08/claracle-codebase-surfaces-research.md:39-395`
  and `.copilot-tracking/research/subagents/2026-08-08/claracle-codebase-surfaces-research.md:500-559`
* Delivery evidence classes, ownership, and earlier epic boundaries:
  `.copilot-tracking/research/subagents/2026-08-08/claracle-delivery-quality-research.md:134-229`
  and `.copilot-tracking/research/subagents/2026-08-08/claracle-delivery-quality-research.md:233-325`
* Alternatives and selected architecture:
  `.copilot-tracking/research/subagents/2026-08-08/claracle-alternatives-selection-research.md:36-79`,
  `.copilot-tracking/research/subagents/2026-08-08/claracle-alternatives-selection-research.md:82-207`,
  and `.copilot-tracking/research/subagents/2026-08-08/claracle-alternatives-selection-research.md:406-461`
* External standards and remaining evidence needs:
  `.copilot-tracking/research/subagents/2026-08-08/claracle-external-standards-research.md:97-188`
  and `.copilot-tracking/research/subagents/2026-08-08/claracle-external-standards-research.md:190-326`

## V1 Decisions Added After Prior Research

The BRD history identifies 0.3 as the decision-closure revision and 1.0 as the formal
governance revision (`docs/brds/claracle-post-relaunch-consolidation-brd.md:33-40`).
The following decisions replace recommendations or open questions in the primary
research with approved business policy.

| Decision cluster | Approved V1 decision | Planning consequence |
|---|---|---|
| Approval meaning | V1 is the controlled approved business baseline; designs, schemas, migration evidence, implementation, and release evidence remain delivery work | Planning may begin without reopening product scope; delivery artifacts must not be represented as approved merely because the BRD is approved |
| Historical release | Record NO-GO/supersession at immutable revision `f37b49d`; freeze the 64-screen and 68-check evidence; carry interaction and live AT findings forward | The old-release GO alternative is closed; CR-01/02 become redesigned-release traceability and evidence stories rather than blockers to historical supersession |
| CR-05 | Repository-page activation is superseded and `[repo_pages] enabled` remains `false` | No temporary activation or enrichment epic is allowed without a material BRD change |
| Objective contracts | OBJ-01 through OBJ-05 have owners, observed baselines, binary targets, and measurement windows | Earlier proposed targets are now commitments; E4 measurement stories can be scheduled explicitly |
| Homepage | Primary audience is technology decision-makers; the page explains changes in open-source technology and leads to strongest current evidence | Audience and primary job workshops are no longer decision blockers; the content hierarchy remains a delivery design artifact |
| Repository explorer | Search plus topic, language, status, and period filters; recent momentum default sort; URL-persisted state; sanitized generated-context summaries; direct GitHub links | Product behavior is fixed; schema fields, query encoding, sanitization implementation, and compatibility behavior remain E2 contracts |
| Repository retention | Keep an individual profile only when differentiated content plus GSC demand or a known inbound link exists | The URL inventory has a binary retention rule; missing per-URL GSC or link evidence keeps a URL disposition pending |
| Repository redirects | Genuine replacements use one-hop hosting-layer 301/308 redirects; no equivalent returns 404/410; Hugo meta refresh is rejected | A redirect-capable hosting boundary is now a prerequisite for BR-003 migration |
| Interactive data slice | All three generated ranking pages are in the first slice | The earlier first-slice selection gap is closed; the pages are `fastest-growing-ai-repositories-this-year`, `most-starred-mcp-projects`, and `top-ai-repositories-this-month` (`content/data/fastest-growing-ai-repositories-this-year/index.md:2-18`, `content/data/most-starred-mcp-projects/index.md:2-18`, and `content/data/top-ai-repositories-this-month/index.md:2-18`) |
| Visualization selection | Compare dot plots, slope or trend views, and ranked-table treatments for each analytical question using dense, sparse, tied, zero, long-label, and mobile fixtures | Chart form remains evidence-selected, but candidate families, fixture classes, threshold, and participants are fixed |
| Comprehension participants | An internal five-member squad proxy performs the first test; selected representation must support correct inference for at least four | The participant-model decision is closed; test prompts, participant identities, raw responses, and conclusion remain delivery evidence |
| Yearly article | Annual 1,200-1,800-word analytical journalistic feature based on monthly evidence; Farnsworth accountable; jmservera final editor; every substantive claim traceable | Length, cadence, genre, ownership, editor, and claim policy are closed; prompt/evidence-pack design and repaired generation remain implementation |
| Embeds | Direct GitHub links and sanitized generated-context summaries of about 160 characters, available through pointer, focus, touch, and the accessibility tree | Destination, source class, approximate length, and access modes are closed; exact sanitization and disclosure component remain E2 implementation |
| Cost source | `data/metrics/token-usage.jsonl` is authoritative | The separate manually maintained total must be removed from the public data path |
| Cost identity | Workflow run ID, stage, and attempt identify records; count only the accepted attempt; exclude retries and `model: none` billing | Aggregation semantics are no longer an E0 question; accepted-attempt resolution and reconciliation are testable E2 work |
| Cost freshness and authority | More than 30 days stale fails publication; jmservera approves pricing-basis changes and exceptions | The former freshness and exception-policy gap is closed; fail-closed workflow and site gates remain delivery work |
| Accountable ownership | BR-001 Calculon; BR-002/003 Leela; BR-004/007/008 Amy; BR-005 Calculon; BR-006 Farnsworth; BR-009 Bender | Issue ownership should follow the BRD; contributors and reviewers follow `.squad/routing.md:5-24` |
| Risks and severity | Severity 1 and 2 visual, accessibility, security, data-integrity, or SEO-migration findings block release; lower findings need owner and due date; exceptions need sponsor rationale, control, and expiry | Every acceptance story needs severity and disposition fields; no team may locally waive a blocking finding |
| Change control | Scope, objectives, targets, priorities, owners, policy, acceptance, severity, and governance changes require sponsor reapproval and a new BRD version | Schemas and code can evolve through normal review only while remaining inside the approved behavior |
| Delivery model | BR-001 through BR-009 are epics split by decision, data/generator, SSR, client enhancement, automated QA, named acceptance, migration, and outcomes | One issue per BR is insufficient; use the decomposition below |

## Former Gaps: Closed Versus Delivery Evidence

| Former primary-research gap | V1 disposition | Remaining work classification |
|---|---|---|
| Sponsor supersession and CR-05 cancellation | Closed in BRD and status record | Preserve the immutable references and map each old finding to a redesigned-release gate |
| Objective baselines, targets, owners, and windows | Closed | Capture E4 evidence on the approved release-day, seven-day, 28-day, three-month, and six-month windows |
| Homepage audience and primary job | Closed | Produce and approve the module hierarchy, selection, freshness, ownership, and fallback design required by BR-002 |
| Repository behavior, filters, sort, state, summaries, and retention policy | Closed at product-policy level | Define schema, field types, compatibility, URL encoding, deterministic generation, and sanitization tests |
| Repository URL evidence and final map | Not closed | Export per-URL GSC and inbound-link evidence, crawl deployed status/canonical/sitemap behavior, reconcile 263/266/267/274, and approve every disposition |
| First data-page slice | Closed as all three ranking pages | Define shared envelopes, per-page metric fields, interaction and field-performance budgets |
| Chart candidates, participant model, and threshold | Closed | State each page's analytical question, execute the five-person comparison, retain raw evidence, and approve the selected representation |
| Embed destination, summary source class, length, and access modes | Closed | Define the exact sanitization rule and disclosure behavior; retain pointer, keyboard, touch, AT, zoom, and collision evidence |
| Yearly length, cadence, genre, owner, editor, and traceability | Closed | Repair cumulative truncation, design bounded evidence packs, add fixture tests, and retain editorial, SEO, claim, and Nibbler review |
| Cost ledger, identity, inclusion/exclusion, freshness, and exception owner | Closed | Implement deterministic projection, accepted-attempt reconciliation, freshness failure, rendering, and runbook evidence |
| Design subject, audience, page purpose, and acceptance policy | Closed at requirement level | Calculon must still produce the approved design brief, tokens, layout concept, signature element, representative views, and self-critique |
| Exact repository/data JSON schemas | Not a remaining business decision | E2 architecture and implementation work subject to normal review and V1 behavior |
| Manual JavaScript-disabled, keyboard, live screen-reader, touch, zoom, reduced-motion, narrow-embed, malformed-data, and field-performance evidence | Not closed | E3/E4 delivery and release evidence |
| CR-06 Q-01 evidence | Not closed | Repair experiment hydration, retain the required run artifacts, and obtain a dated budget-owner conclusion |
| CR-04 dynamic-topic activation | Not closed and independent | Exact-revision Hermes and sponsor approval, one reviewed transaction, production observation, and tested rollback |

## Contradictions and Planning Blockers

### Blocking issue: Redirect policy versus GitHub Pages

BR-003 requires generated hosting-layer 301/308 rules and explicitly forbids Hugo meta
refresh (`docs/brds/claracle-post-relaunch-consolidation-brd.md:127-150`). The approved
risk gate repeats the requirement at
`docs/brds/claracle-post-relaunch-consolidation-brd.md:165-171`.

Claracle's current architecture and both production deployment paths use GitHub Pages:

* `architecture.md:10-20`
* `.github/workflows/deploy-site.yml:67-67` and
  `.github/workflows/deploy-site.yml:195-215`
* `.github/workflows/crawl-and-publish.yml:1436-1476`

GitHub's first-party documentation defines Pages as a static hosting service and
documents a custom static `404.html`. Hugo's current URL-management documentation says
aliases generate client-side `meta refresh` by default and server redirects require a
host-specific rules file processed by a supporting host or web server. No Cloudflare,
Netlify, GitLab Pages, Apache, reverse proxy, or equivalent redirect-processing layer
was found in the repository.

Required planning decision before BR-003 migration implementation:

1. Add a redirect-capable edge in front of GitHub Pages and define its IaC, ownership,
	security, observability, rollback, and rule limits.
2. Move site hosting to a static host that processes generated permanent redirect
	rules, which is broader than the current deployment architecture.
3. Reapprove V1 with a different redirect policy. Continuing with Hugo meta refresh
	without reapproval contradicts the controlled baseline.

This is the only discovered blocker to the approved technical target. Schema details,
design artifacts, and evidence collection are planned delivery work rather than
contradictions.

### Blocking evidence for the BR-003 migration transaction

The final URL map cannot be approved from local counts alone. V1's retention rule
depends on GSC demand or known inbound links, and the BRD makes removal depend on indexed
URLs, inbound links, unique content, redirects, canonicals, sitemap state, and tests
(`docs/brds/claracle-post-relaunch-consolidation-brd.md:137-143`). The primary research
correctly retains this as the next research action. It blocks URL removal and redirects,
not schema, SSR, or explorer development.

### Traceability inconsistencies that do not reopen V1 decisions

* The status record's source-plan table still says prior plan phases are open
  (`docs/review/data-observatory-relaunch/status-of-record.md:55-62`), while BRD Section
  6 says all plans are closed and their residual items migrated
  (`docs/brds/claracle-post-relaunch-consolidation-brd.md:105-110`). Treat the BRD as the
  forward backlog, but reconcile the status table before implementation issues cite it.
* The status record still lists GA4/GSC transcription and `repo_pages` rollout as
  deferred work (`docs/review/data-observatory-relaunch/status-of-record.md:205-213`),
  although its own summary marks GA4/GSC done and repository activation superseded
  (`docs/review/data-observatory-relaunch/status-of-record.md:95-101`). These are stale
  rows, not active implementation scope.
* BRD Section 2 calls external metadata validation delivered
  (`docs/brds/claracle-post-relaunch-consolidation-brd.md:52-65`), while the status record
  calls the broader external metadata and feed gate partial
  (`docs/review/data-observatory-relaunch/status-of-record.md:95-99`). Clarify whether
  the BRD refers only to home/article/repository source-level checks or also claims the
  pending external debuggers and named conclusion. This does not block V1 planning, but
  it affects inherited release evidence.
* The status section titled "Remaining human gates" includes timing approval even though
  the row itself says approved (`docs/review/data-observatory-relaunch/status-of-record.md:39-52`).
  This is editorially stale and should not generate a new timing story.

## Selected Implementation-Planning Approach

Use the existing selected architecture with one added prerequisite: resolve the
redirect-host boundary before approving the BR-003 migration transaction.

```text
approved V1 policy
  -> normalized deterministic source contracts
  -> versioned repository, ranking, and cost artifacts
  -> authoritative Hugo HTML with essential content and links
  -> page-scoped JavaScript enhancement
  -> automated E2 gates and named E3 acceptance
  -> redirect-capable deployment boundary for BR-003
  -> one release revision and scheduled E4 outcomes
```

Keep the evidence classes from the prior research:

* E0: approved design, editorial, product, and operational decisions
* E1: observed baseline and defect evidence
* E2: schemas, deterministic artifacts, tests, builds, and workflow behavior
* E3: named human, sponsor, security, accessibility, editorial, and migration acceptance
* E4: dated production, usability, GA4, GSC, and field-performance outcomes

## Dependency Order and Binary Gates

| Gate | Dependency order | Binary pass condition |
|---|---|---|
| G0 approved baseline | Already complete | BRD V1 approved; NO-GO/supersession recorded at `f37b49d`; CR-05 disabled and superseded; state quality checks record `v1-approved` |
| G1 handoff and deployment boundary | First | Every historical finding maps to a redesigned-release test/review with owner and severity; redirect-host option is approved; CR-04 is explicitly independent; no stale status row is imported as new scope |
| G2 contracts and design | After G1; BR-001, BR-002, BR-003 contract, BR-004 contract, BR-006 contract, and BR-009 contract can run in parallel | Approved design brief and homepage hierarchy; documented repository/ranking/cost schemas; URL-state and compatibility rules; yearly evidence-pack contract; cost reconciliation contract; existing timing gates remain enforced |
| G3 shell, editorial, navigation, and cost | After BR-001 design and relevant G2 contracts | BR-001, BR-002, BR-006, BR-008, and BR-009 E2 checks pass; Calculon, Fry, Farnsworth, Zapp, Nibbler, and jmservera provide only their routed E3 acceptances |
| G4 repository candidate | Explorer work after repository schema; migration transaction after redirect host and complete URL map | 266 identities reconcile; useful no-JavaScript summary; all client states pass; zero low-information details in candidate; every URL has approved treatment; redirects are one-hop HTTP 301/308 or approved 404/410; rollback passes |
| G5 data and embed candidate | BR-004 data controls may begin after shared envelope; BR-005 selection precedes final chart implementation; BR-007 depends on summary/sanitization contract | All three pages pass SSR, provenance, download, state, error, accessibility, timing, and budget checks; at least two alternatives per question tested; at least four of five correct; embed interactions are equivalent |
| G6 release | After G3, G4, and G5 | One immutable candidate has no unresolved severity-1/2 finding; lower findings have owner and due date; exceptions include sponsor rationale, control, and expiry; sponsor records GO |
| G7 outcomes | After G6 | Seven-day smoke retained; repository and discovery evidence captured at 28 days; migration reviewed at three months; organic targets reviewed at six months |

CR-06 should run during G1/G2 because it is independent and produces a budget input.
CR-04 may run in a separate operational lane after G0; it must not gate G2 through G6.

## Epic and Story Decomposition

The BRD explicitly says BR-001 through BR-009 are epics
(`docs/brds/claracle-post-relaunch-consolidation-brd.md:157-161`). The grouped delivery
rows in `docs/brds/claracle-post-relaunch-consolidation-brd.md:178-197` are portfolio
views, not substitutes for implementation epics.

### EP-000 Governance and carried-forward evidence

Accountable owner: Leela. Sponsor: jmservera. Required reviewers: Amy, Fry, Zapp, URL.

1. ST-000.1 record the V1 handoff baseline and immutable `f37b49d` evidence references.
2. ST-000.2 build the CR-01/CR-02 finding-to-redesign-gate matrix with owner, severity,
	target story, evidence type, and closure rule.
3. ST-000.3 enforce the CR-05 invariant in planning and acceptance: repository-page
	generation remains disabled and prior lifecycle/alias evidence is migration input.
4. ST-000.4 select and document the redirect-capable hosting boundary for BR-003.
5. ST-000.5 reconcile stale status rows before issue generation uses them as scope.

Binary epic gate: every carried finding has one target gate; no issue activates CR-05;
the redirect architecture can emit actual HTTP 301/308 responses; status inconsistencies
are dispositioned.

Cheapest validation: review one traceability table plus an HTTP proof-of-capability for
one old URL, one replacement URL, and one retired URL before building the full map.

### EP-OP1 Dynamic-topic canary (CR-04, independent)

Accountable owner: Amy. Approval owners: Hermes and jmservera. Pipeline reviewer: URL.

1. ST-OP1.1 identify the exact staged `local-first` revision and verify disabled default.
2. ST-OP1.2 obtain Hermes and sponsor approval for that revision.
3. ST-OP1.3 execute one activation transaction and retain sanitization, YAML, assignment,
	taxonomy, logging, rendering, and promotion evidence.
4. ST-OP1.4 observe production, execute rollback, and record expansion or stop decision.

Binary epic gate: one allowlisted slug only, exact-revision approvals, reviewed
transaction, no unexplained taxonomy change, and proven disabled rollback.

Cheapest validation: run the existing preview/check path against `enabled = false` and
the one-slug allowlist before any production flip.

### EP-OP2 Cost experiment completion (CR-06)

Accountable owner: URL. Architecture reviewer: Leela. Security reviewer: Hermes. Budget
authority: jmservera.

1. ST-OP2.1 choose the approved narrow fix: publish the five seed hubs to `publish` or
	exclude `content/topics/` from the experiment's expected count.
2. ST-OP2.2 add a pre-timing hydrated-corpus assertion.
3. ST-OP2.3 run the immutable experiment on `main` and retain the required samples and
	aggregate artifact.
4. ST-OP2.4 record the dated budget-owner conclusion.

Binary epic gate: clean `build-cost-experiment.yml` run, representative pre-timing
corpus, retained admissible artifacts, and dated conclusion.

Cheapest validation: hydrate a temporary tree from the reviewed SHAs and assert five
seed hubs before dispatching the workflow.

### EP-BR001 Experience design foundation

Accountable owner: Calculon. Implementer: Amy. Reviewers: Leela and Fry. Sponsor:
jmservera.

1. ST-001.1 produce the design brief with subject, audience, page purpose, token system,
	layout concept, signature element, and self-critique.
2. ST-001.2 prototype representative homepage, article, repository-summary, and data-page
	views at mobile and desktop widths.
3. ST-001.3 implement shared tokens, shell, typography, color, spacing, motion, focus,
	reduced-motion, and contrast behavior.
4. ST-001.4 migrate representative components without coupling repository/data client
	behavior into the shell.
5. ST-001.5 add automated visual, overflow, contrast, reduced-motion, Lighthouse, and
	accessibility coverage.
6. ST-001.6 retain Calculon/sponsor design acceptance and Fry's redesigned-release QA
	disposition.

Binary epic gate: approved brief and representative views; zero unresolved severity-1/2
visual or accessibility findings; all applicable automated and named gates pass.

Cheapest validation: reject the brief if any of the seven required fields is absent,
then render the four representative page types at one mobile and one desktop width.

### EP-BR002 Homepage evidence hierarchy

Accountable owner: Leela. Implementers: Amy and Farnsworth. Data contributors: Bender.
Reviewers: Zapp and Fry.

1. ST-002.1 define and approve module order, selection, freshness, content owner,
	fallback, and omission rules for weekly, monthly, yearly, topic, repository, and data.
2. ST-002.2 define deterministic module inputs and original-summary provenance.
3. ST-002.3 implement authoritative Hugo modules with useful no-JavaScript content.
4. ST-002.4 implement unique title, description, canonical, heading, structured-data,
	and internal-link behavior.
5. ST-002.5 test each missing, empty, stale, and valid optional-module state plus layout
	shift and link integrity.
6. ST-002.6 retain editorial/SEO acceptance and schedule release-day, 28-day,
	three-month, and six-month outcome captures.

Binary epic gate: every enabled module has an approved contract, original crawlable
summary, valid link, and no empty wrapper; one H1; no duplicated or padded content.

Cheapest validation: build deterministic homepage fixtures with one optional source
removed and inspect the rendered HTML before styling or enhancement.

### EP-BR003 Repository consolidation and URL migration

Accountable owner: Leela. Data owner: Bender. UI owner: Amy. Migration owners: Zapp and
URL. Validator: Fry. Sponsor: jmservera.

1. ST-003.1 export per-URL GSC, inbound-link, deployed status, indexability, canonical,
	sitemap, alias, and unique-content evidence.
2. ST-003.2 reconcile 266 detail records, 267 source pages, 274 local rendered URLs,
	seven aliases, and the live count of 263.
3. ST-003.3 approve every keep, merge, or retire disposition under the V1 retention rule.
4. ST-003.4 document the versioned schema, freshness, provenance, compatibility,
	deterministic ordering, and sanitization contracts.
5. ST-003.5 generate the artifact and schema validation from the normalized source.
6. ST-003.6 implement the server-rendered summary with count, period, provenance, direct
	GitHub links, and a useful browsable result without JavaScript.
7. ST-003.7 implement scoped search; topic, language, status, and period filters; recent
	momentum default sort; reset; URL state; status announcements; empty/error behavior;
	and focus restoration.
8. ST-003.8 generate and deploy one-hop 301/308 rules for genuine replacements and
	404/410 behavior for retirements; update canonicals, internal links, and sitemap.
9. ST-003.9 add deterministic, inventory, schema, no-JavaScript, client-state, malformed,
	stale, future-version, redirect-chain, canonical, sitemap, and rollback tests.
10. ST-003.10 retain Zapp/URL migration acceptance, sponsor GO, and 28-day/three-month
	 observations.

Binary epic gate: complete approved inventory, zero unexplained identity differences,
zero low-information detail pages in the candidate, useful SSR, all explorer states,
actual one-hop HTTP redirects or approved 404/410, canonical sitemap, and rollback.

Cheapest validation: generate the artifact from a fixed fixture, assert 266 unique
identities, render with JavaScript disabled, and prove one keep, one merge, one retire,
and one alias end to end before bulk migration.

### EP-BR004 Interactive ranking pages

Accountable owner: Amy. Data owner: Bender. Reviewers: Calculon, Zapp, Fry, and URL.

1. ST-004.1 inventory fields and state needs for all three approved ranking pages.
2. ST-004.2 define a shared envelope plus typed per-ranking records, freshness,
	provenance, publication, compatibility, URL-state, and interaction budgets.
3. ST-004.3 generate and validate versioned JSON artifacts deterministically.
4. ST-004.4 preserve and improve authoritative Hugo summaries, tables, attribution,
	and downloads.
5. ST-004.5 implement page-scoped filter, sort, reset, stable state where useful, chart
	exploration, status, empty, and error behavior.
6. ST-004.6 test no-JavaScript, valid, empty, malformed, unavailable, stale, and future
	payloads plus keyboard, AT, responsive, privacy, timing, and field-performance gates.
7. ST-004.7 retain named accessibility/interaction acceptance and seven-day smoke.

Binary epic gate: all three pages satisfy SSR, provenance, download, state, error,
accessibility, timing, and approved budget contracts.

Cheapest validation: convert one current ranking fixture to the proposed envelope and
prove deterministic JSON, useful no-JavaScript table, malformed state, and URL reset
before implementing all pages.

### EP-BR005 Evidence-selected visualizations

Accountable owner: Calculon. Analytical contributor: Farnsworth. Implementer: Amy.
Validator: Fry. Sponsor: jmservera.

1. ST-005.1 state one analytical question and intended inference for each ranking page.
2. ST-005.2 build common dense, sparse, tied, zero, long-label, top-10, top-100, and
	mobile fixtures.
3. ST-005.3 prototype at least two suitable choices per question from dot plot, slope or
	trend view, and ranked-table treatment, with the current bar as baseline.
4. ST-005.4 run the internal five-member proxy test and retain prompts, raw answers,
	correctness scoring, accessibility observations, and conclusion.
5. ST-005.5 approve one representation per question only when at least four participants
	infer correctly.
6. ST-005.6 implement responsive, non-color-only output with a statement of intended
	inference and equivalent accessible table.
7. ST-005.7 retain visual/accessibility acceptance and production outcome observation.

Binary epic gate: two alternatives evaluated per question, four-of-five threshold met,
equivalent table retained, responsive and non-color encoding verified.

Cheapest validation: compare one dense and one long-label mobile fixture before building
production components; a choice that fails either is removed from the test set.

### EP-BR006 Complete yearly analytical article

Accountable owner: Farnsworth. Generator contributor: Bender. Reviewers: Leela, Zapp,
Nibbler, and Fry. Final editor: jmservera.

1. ST-006.1 define the annual evidence-pack schema and keep bounded model inputs separate
	from complete published prose.
2. ST-006.2 remove cumulative mid-thought clipping across monthly and yearly stages.
3. ST-006.3 generate a complete 1,200-1,800-word analytical journalistic article from
	monthly evidence with claim identifiers and source links.
4. ST-006.4 render headline, description, headings, canonical, Article JSON-LD, internal
	and source links, byline, dates, image/social metadata, and visible-content parity.
5. ST-006.5 add fixtures rejecting ellipses, clipping markers, incomplete sentences,
	raw artifacts, missing sections, and untraceable substantive claims.
6. ST-006.6 retain Nibbler safety review, Zapp SEO review, claim-to-source review, and
	jmservera editorial approval.

Binary epic gate: complete 1,200-1,800-word reviewed output, no clipped/raw artifacts,
every substantive claim traceable, metadata parity valid, all named reviews retained.

Cheapest validation: feed one deliberately long monthly fixture through the complete
pipeline and reject any ellipsis, clipping marker, incomplete sentence, or missing
source before changing prompt quality.

### EP-BR007 Accessible linked embed summaries

Accountable owner: Amy. Data contributor: Bender. Reviewers: Fry, Hermes, and Nibbler.

1. ST-007.1 define the generated-context field, approximately 160-character shaping,
	sanitization, complete accessible text, and safe GitHub destination contract.
2. ST-007.2 render every displayed repository name as a real link in standalone and
	embedded contexts while preserving source attribution.
3. ST-007.3 implement one equivalent summary disclosure model for hover, focus, touch,
	Escape dismissal, persistence, and accessibility-tree access.
4. ST-007.4 test focus order, hover transfer, collision, zoom, narrow embeds, safe
	navigation, privacy isolation, screen readers, and control occlusion.
5. ST-007.5 retain Fry accessibility evidence and Hermes/Nibbler privacy and content
	safety dispositions.

Binary epic gate: every name is a correct direct GitHub link; the same sanitized summary
is available through all approved modes; no tooltip is the sole source of essential
information or obscures its trigger.

Cheapest validation: implement one representative long repository label and compare its
hover, focus, touch, and accessibility-tree text at narrow width before applying the
pattern to all records.

### EP-BR008 Primary navigation order

Accountable owner: Amy. Validators: Fry and Zapp.

1. ST-008.1 reorder menu weights so Weekly, Monthly, and Yearly are first.
2. ST-008.2 add rendered-order, active-state, URL, keyboard-order, and no-clipping tests.
3. ST-008.3 validate desktop, mobile, zoom, and accessibility-tree navigation with the
	BR-001 shell.

Binary epic gate: first three destinations are Weekly, Monthly, Yearly in all supported
modes; every remaining destination remains reachable; no clipping or incorrect state.

Cheapest validation: assert the first three rendered menu URLs, then inspect only the
narrowest supported viewport before running the full visual matrix.

### EP-BR009 Cost provenance and freshness

Accountable owner: Bender. Pipeline owner: URL. Renderer: Amy. Validator: Fry. Pricing
and exception authority: jmservera.

1. ST-009.1 document accepted-attempt resolution for workflow run ID, stage, and attempt,
	retry exclusion, `model: none` exclusion, currency, pricing basis, and reconciliation.
2. ST-009.2 generate a versioned deterministic public record from
	`data/metrics/token-usage.jsonl` with covered period, generated time, provenance,
	accepted identities, and reconciliation result.
3. ST-009.3 integrate generation into the owning pipeline and eliminate the independently
	maintained total from the public path.
4. ST-009.4 fail the owning pipeline and site build on missing, malformed, unreconciled,
	or more-than-30-days-stale input.
5. ST-009.5 render current cost, period, generation timestamp, currency, pricing basis,
	and provenance on About.
6. ST-009.6 add deterministic, retry, multi-stage, null/no-model, stale, malformed,
	duplicate, future-version, and pricing-exception fixtures plus the failure runbook.
7. ST-009.7 retain jmservera pricing-basis acceptance and seven-day production smoke.

Binary epic gate: public value reconciles exactly to accepted ledger identities; all
required metadata is visible; invalid or older-than-30-day input blocks publication;
no independent total remains.

Cheapest validation: aggregate a fixture with two stages, a retry, one accepted attempt,
one `model: none` record, and a 31-day-old latest period; assert the exact accepted total
and a failing freshness result.

## Alternatives After V1

| Alternative | V1 effect | Current disposition |
|---|---|---|
| Shared versioned data, Hugo HTML, scoped enhancement | V1 explicitly adopts it and adds deterministic schema, freshness, fail-closed, and no-JavaScript constraints | Selected and strengthened |
| Client-first JSON application | V1 requires useful server-generated HTML and preserves current Hugo/GitHub Pages architecture | Rejection is stronger; no approved requirement justifies application-shell risk |
| Activate and enrich all repository pages | V1 explicitly supersedes CR-05 and requires zero low-information details | Rejected as a target state; only evidence-qualified differentiated profiles may survive |
| URL-level keep/merge/retire | V1 approves its evidence rule, status outcomes, and monitoring windows | Selected, but blocked at production migration by missing URL evidence and redirect-capable hosting |
| Blanket redirect | V1 requires genuine equivalence and one-hop redirects | Rejected; cannot satisfy retention and soft-404 safeguards |
| Blanket deletion | V1 retains 404/410 only for URLs with no equivalent | Rejected as a blanket policy; retained as the per-URL retire action |
| Complete old-release GO first | V1 and status record already choose NO-GO/supersession | Obsolete for planning |
| Explicit supersession before redesign | Completed in the approved records | No longer an implementation alternative; it is the historical baseline |

The progressive-enhancement architecture therefore remains correct. The migration
subsystem needs an additional host/edge architecture decision, but no evidence supports
replacing Hugo rendering or moving core interaction to a client-first application.

## Required Updates to the Primary Research

The primary report remains valuable but now describes pre-V1 readiness. Update it in a
separate change; this task did not modify it.

1. Add approval status and controlling evidence from
	`docs/brds/claracle-post-relaunch-consolidation-brd.md:20-40` and
	`docs/brds/claracle-post-relaunch-consolidation-brd.md:199-212`.
2. Preserve the selected approach at
	`.copilot-tracking/research/2026-08-08/claracle-post-relaunch-experience-research.md:24-30`,
	but state that V1 approved it and add the GitHub Pages redirect-host blocker.
3. Replace the homepage workshop and cost-semantics research items at
	`.copilot-tracking/research/2026-08-08/claracle-post-relaunch-experience-research.md:41-55`.
	Audience/job and cost identity/freshness are approved. Keep per-URL GSC/inbound-link
	research and visualization execution.
4. Change the OBJ-04 wording at
	`.copilot-tracking/research/2026-08-08/claracle-post-relaunch-experience-research.md:136-142`
	from "subject to sponsor approval" and "agreed first slice" to the approved four-of-five
	internal squad test across all three ranking pages.
5. Change the example contract's `maximumAgeDays` from 14 to the approved 30 days at
	`.copilot-tracking/research/2026-08-08/claracle-post-relaunch-experience-research.md:158-180`.
	The example currently conflicts with BR-009.
6. Replace the readiness-blocker table at
	`.copilot-tracking/research/2026-08-08/claracle-post-relaunch-experience-research.md:144-156`.
	Product decisions are closed; list delivery prerequisites and evidence instead.
7. Replace "The exact fields remain an E0 decision" at
	`.copilot-tracking/research/2026-08-08/claracle-post-relaunch-experience-research.md:181`.
	V1 fixes repository behavior, source class, filters, sort, state, retention, and cost
	identity. Exact schema types and compatibility are E2 architecture work.
8. Mark governance and decision closure complete in the phased model at
	`.copilot-tracking/research/2026-08-08/claracle-post-relaunch-experience-research.md:255-265`.
	Add redirect-host selection before repository migration; keep CR-04 independent.
9. Replace "Required BRD Amendments Before Planning" at
	`.copilot-tracking/research/2026-08-08/claracle-post-relaunch-experience-research.md:267-277`
	with "V1 Amendments Completed." Every listed business amendment is present in V1;
	story decomposition is now implementation-planning work.
10. Rewrite the remaining-gaps list at
	 `.copilot-tracking/research/2026-08-08/claracle-post-relaunch-experience-research.md:278-289`
	 using the closed-versus-delivery table in this report. Remove sponsor supersession,
	 homepage direction, first-slice choice, participant threshold, embed destination,
	 yearly contract, and cost semantics as open decisions.
11. Replace the stale timing citation
	 `docs/review/data-observatory-relaunch/status-of-record.md:121-135` with the approved
	 timing section at `docs/review/data-observatory-relaunch/status-of-record.md:117-130`.
12. Update old BRD row citations such as
	 `docs/brds/claracle-post-relaunch-consolidation-brd.md:125-133` to the current
	 requirement rows at `docs/brds/claracle-post-relaunch-consolidation-brd.md:123-135`.
13. Add the three traceability inconsistencies from this report so the primary document
	 does not import stale source-plan, deferred-work, or external-metadata states.
14. Add first-party platform references:
	 [GitHub Pages static hosting](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages),
	 [GitHub Pages custom 404](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-custom-404-page-for-your-github-pages-site),
	 and [Hugo URL management](https://gohugo.io/content-management/urls/).

## Clarifying Questions Requiring Sponsor or Architecture Input

1. Which redirect-capable production boundary should implement the approved one-hop
	301/308 policy while Claracle otherwise remains on GitHub Pages?
2. Does BRD Section 2's external-metadata "pass" intentionally cover a narrower set than
	the status record's still-partial external debugger and named-review gate?

No other business-choice question blocks issue decomposition. Per-URL analytics,
designs, schemas, prototypes, tests, manual reviews, and production observations are
delivery work with named owners and binary gates above.

## Recommended Next Research Not Completed

* [ ] Evaluate redirect-capable edge or static-host options against custom-domain,
  security, operational, cost, rule-count, rollback, and GitHub Pages constraints
* [ ] Export page/query GSC evidence and known inbound links for every repository URL
* [ ] Crawl production repository URLs for status, redirect chain, response and HTML
  canonical, indexability, sitemap membership, and the 263/266 discrepancy
* [ ] Inventory the exact historical NFR-005 and visual interaction findings into the
  EP-000 traceability matrix
* [ ] Inspect the accepted-attempt markers available in current workflow artifacts before
  finalizing the BR-009 reconciliation schema

## External References

* [GitHub Pages static hosting](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages)
* [GitHub Pages custom 404](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-custom-404-page-for-your-github-pages-site)
* [Hugo URL management and redirect methods](https://gohugo.io/content-management/urls/)
* [Google redirects guidance](https://developers.google.com/search/docs/crawling-indexing/301-redirects)
* [Google canonical consolidation](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
* [Google site moves](https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes)
* [Google JavaScript SEO basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)
* [WAI complex images guidance](https://www.w3.org/WAI/tutorials/images/complex/)
* [WCAG 2.2 content on hover or focus](https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html)

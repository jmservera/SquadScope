<!-- markdownlint-disable-file -->

# Claracle BRD-CLARACLE-003 Delivery Quality Research

## Research Scope

* Determine measurable baselines, targets, and observation windows for the BRD objectives
* Classify the evidence and acceptance readiness of BR-001 through BR-009
* Assign accountable ownership from `.squad/team.md` and `.squad/routing.md`
* Define multi-system epic and story boundaries
* Identify unresolved decisions that block binary acceptance
* Sequence carried-over visual acceptance and rollout requirements against redesign and consolidation work
* Propose a coherent phased delivery model with binary gates
* Identify requirements that need amendment, supersession, or splitting

## Status

Complete as of 2026-08-08. The requested questions are answered from local repository
evidence. No implementation or primary research document was modified.

## Evidence Inventory

### Governing requirements and status

* `docs/brds/claracle-post-relaunch-consolidation-brd.md:24-38` identifies
	BRD-CLARACLE-003 as a draft, says it supersedes BRD-CLARACLE-002 and the relaunch PRD
	as context, and records the addition of the post-relaunch requirements.
* `docs/brds/claracle-post-relaunch-consolidation-brd.md:44-48` says the relaunch is
	feature-complete while this BRD is both the remaining relaunch backlog and the next
	experience phase. This combines release closure and product discovery in one document.
* `docs/brds/claracle-post-relaunch-consolidation-brd.md:73-88` defines CR-01 through
	CR-06. CR-01 through CR-03 block final relaunch acceptance; CR-04 and CR-05 are
	rollout activations; CR-06 repairs the cost experiment.
* `docs/brds/claracle-post-relaunch-consolidation-brd.md:96-102` makes all three
	acceptance gates, both rollouts, the cost experiment, and the redesign part of the same
	success definition without sequencing them.
* `docs/brds/claracle-post-relaunch-consolidation-brd.md:113-149` defines OBJ-01 through
	OBJ-05, BR-001 through BR-009, constraints, and five open decisions. The objectives
	lack numeric baselines, targets, and observation windows.

### Relaunch acceptance and rollout evidence

* `docs/review/data-observatory-relaunch/status-of-record.md:15-49` is the declared
	status authority. It says release acceptance is pending, timing and security are
	approved, visual and live assistive-technology work remain open, and both rollout flags
	remain disabled.
* `docs/review/data-observatory-relaunch/status-of-record.md:85-99` classifies the
	remaining acceptance evidence: accessibility, visual acceptance, and Q-01 are partial;
	repository-page rollout is approved but not enabled; dynamic creation is approved in
	principle but not enabled.
* `docs/review/data-observatory-relaunch/status-of-record.md:121-135` contains stale
	timing state that still marks threshold approval pending, even though the document's
	summary records approval. The status record needs reconciliation before it can support
	a binary release decision.
* `docs/review/data-observatory-relaunch/visual-review-handoff-2026-08-07.md:15-19`
	explicitly says screenshots are a handoff, not approval.
* `docs/review/data-observatory-relaunch/visual-review-handoff-2026-08-07.md:60-84`
	establishes current coverage and the missing interaction states.
* `docs/review/data-observatory-relaunch/visual-review-handoff-2026-08-07.md:95-147`
	records Amy's acceptance of the 64-screen matrix and Fry's automated QA acceptance,
	while retaining interaction captures and a live screen-reader pass as open work.
* `docs/review/data-observatory-relaunch/owner-action-register.md:237-270` records the
	same visual disposition and open manual interaction work.
* `docs/review/data-observatory-relaunch/owner-action-register.md:289-343` records
	separate rollout decisions. The `local-first` canary is bounded and staged but disabled;
	repository pages are sponsor-approved, regenerated to 266 pages, and still disabled.
* `.copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md:7-20`
	is closed and migrates the remaining work to CR-04 through CR-06.
* `.copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md:24-43`
	defines the report-only cost evidence contract and says retained runs plus the budget
	conclusion remain pending.
* `.copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md:72-131`
	shows that dynamic-topic review and repository activation were still human-gated. The
	repository rollout requires Pagefind, axe, Lighthouse, cost, URL, and sponsor evidence
	that has not been completed for the activation revision.
* `.copilot-tracking/plans/2026-08-07/pending-plan-items-reconciliation-plan.instructions.md:10-22`
	distinguishes delivered work, executable gaps, and human-authority gates.
* `.copilot-tracking/plans/2026-08-07/pending-plan-items-reconciliation-plan.instructions.md:53-71`
	says all executable reconciliation passed while both rollout flags remained disabled.

### Analytics, search, timing, and QA baselines

* `docs/growth/ga4-gsc-baseline-2026-07-29.md:17-23` establishes the production
	property, stream, and dated baseline record.
* `docs/growth/ga4-gsc-baseline-2026-07-29.md:73-86` provides the reusable measurement
	baseline: 51 total sessions, 0 organic sessions, 149 impressions, 0 clicks, 294 indexed
	pages, and 17 impression-bearing queries. The GA4 window is 2026-07-11 through
	2026-08-07; the GSC window is 2026-07-09 through 2026-08-05.
* `docs/brds/claracle-data-observatory-relaunch-brd.md:88-101` supplies inherited
	targets and windows: at least 250 monthly organic sessions and at least 15 top-20
	queries at six months, with technical SEO complete at launch.
* `docs/review/data-observatory-relaunch/timing-analysis.md:114-139` establishes three
	production measurements and approved-budget inputs: Hugo p95 3,058 ms, Pagefind p95
	2,707 ms, and combined observed 5,529 ms.
* `docs/review/data-observatory-relaunch/timing-analysis.md:141-174` records approval of
	Hugo 6,000 ms, Pagefind 5,500 ms, and total 11,500 ms thresholds with CI enforcement.
* `docs/qa-gates.md:14-45` defines the current nine-route, three-run Lighthouse method
	and binary thresholds: performance at least 90, accessibility and best practices at
	least 95, and CLS at most 0.1.
* `docs/rollout-checklist.md:1-7` is a generic instance-readiness checklist, not a
	dated Claracle product-release record. Its unchecked state and broad setup focus make it
	unsuitable as the acceptance authority for BRD-CLARACLE-003.

### Design, ownership, and current defects

* `.squad/team.md:5-24` identifies the active specialist roles.
* `.squad/routing.md:5-24` routes design systems to Calculon, frontend and Hugo work to
	Amy, architecture and editorial direction to Leela, pipeline data to Bender, content
	analysis to Farnsworth, QA to Fry, SEO to Zapp, security to Hermes, workflow controls
	to URL, and generated-content safety to Nibbler.
* `docs/data-observatory-runbook.md:28-45` provides the closest operational RACI and
	makes jmservera accountable for production analytics and rollout approval.
* `docs/processed/redesign-proposal-2026-05.md:1-20` marks the prior six-phase redesign
	implemented, archived, and superseded. Its visual direction is historical evidence, not
	an approved design direction for BR-001.
* `docs/design/visual-verification.md:3-19` states that visual baselines are regression
	evidence for an approved design, while `docs/design/visual-verification.md:107-126`
	says baselines are updated only after an intentional design phase merges.
* `content/yearly/2026.md:12-15` contains clipped monthly excerpts, ellipses, malformed
	prose, and a literal truncation marker. This is direct baseline evidence for BR-006.
* `scripts/generate_yearly_narrative.py:816-880` owns yearly title, summary, and narrative
	page generation. Summary truncation is intentional, but the body is passed from
	`synthesize_year`, so the body defect must be fixed upstream of page writing.
* `content/about/_index.md:21-25` presents the cost dashboard as current operational
	transparency.
* `data/metrics/cost-summary.json:1-10` contains only W19 through W21 and has no source,
	reporting period, generated timestamp, or freshness metadata. This is direct baseline
	evidence for BR-009.
* `layouts/partials/cost-dashboard.html:1-18` renders the file without checking age or
	provenance.
* `hugo.toml:61-100` shows current navigation order is Weekly, Topics, Monthly, Data,
	Tools, Yearly, Search. This directly fails BR-008's requested first-three order.

## Findings

### Critical BRD quality findings

1. BRD-CLARACLE-003 cannot support binary acceptance in its current form. OBJ-01 through
	 OBJ-05 state desirable outcomes but omit baseline, target, source, and window fields.
	 The old relaunch BRD already contains usable discovery targets and should remain the
	 measurement lineage rather than creating incompatible replacements.
2. The document mixes three governance states: unclosed relaunch acceptance, optional
	 operational activations, and a new redesign. A design baseline cannot simultaneously
	 be the acceptance target for CR-02 and the surface intentionally replaced by BR-001.
3. CR-05 and BR-003 are mutually exclusive delivery outcomes. CR-05 enables generation
	 of 266 detail pages; BR-003 requires the production build to stop emitting those pages.
	 Running CR-05 would create migration work and search churn with no durable product
	 benefit.
4. Evidence is conflated. Automated tests prove contracts, screenshots prove rendered
	 state, named reviews prove human acceptance, and GA4/GSC prove external outcomes. No
	 single class substitutes for another.
5. The `Owner(s)` and stakeholder columns do not establish one accountable delivery
	 owner. Each requirement needs one accountable squad owner, one sponsor approver where
	 policy or brand is involved, and explicit required reviewers.
6. The open decisions in `docs/brds/claracle-post-relaunch-consolidation-brd.md:144-149`
	 block acceptance definitions, not merely implementation choices. They must close before
	 implementation stories can be considered ready.

### Proposed objective measurement contracts

| Objective | Baseline | Target | Window and binary gate |
|---|---|---|---|
| OBJ-01 visual credibility | Current relaunch matrix: 64 screenshots and 68/68 visual checks; current Lighthouse thresholds; two manual acceptance items remain | Approved BR-001 design brief; all representative routes pass the 68-check contract or its approved successor, Lighthouse thresholds, reduced motion, contrast, keyboard, and live AT review; zero unresolved severity-1 or severity-2 visual/a11y defects | Pre-merge on the release candidate, then a seven-day production smoke. Sponsor and Calculon accept the design; Fry accepts QA |
| OBJ-02 discovery | 0 organic sessions, 149 impressions, 0 clicks, 294 indexed pages, 17 impression-bearing queries | Retain inherited targets: at least 250 organic sessions per 28-day month and at least 15 queries in the top 20 | Record release-day URL-class coverage, a 28-day post-release snapshot, a three-month indexing review, and six-month GA4/GSC outcome review. Do not use raw indexed-page count as a success target because BR-003 intentionally removes URLs |
| OBJ-03 repository consolidation | 266 generated detail pages; 294 total indexed URLs and 1,190 not indexed at the launch baseline | Zero low-information detail pages emitted; 100% of inventoried valuable URLs receive approved redirect/canonical treatment; explorer search, filter, sort, reset, direct-link, empty, and error scenarios pass | Inventory before implementation; migration gate on the release candidate; GSC redirect/index review at 28 days and three months |
| OBJ-04 data comprehension | Existing server-rendered data pages, bar charts, one embeddable chart, and one client tool; no comprehension baseline | Every agreed first-slice page passes SSR, provenance, download, keyboard, AT, share-state, empty/error, and timing contracts; the selected chart yields a correct inference for at least four of five representative readers and is not worse than the current chart | Comparative prototype test before selection; automated gate pre-merge; seven-day production smoke. The five-reader threshold is a proposed minimum and requires sponsor approval |
| OBJ-05 cost freshness | W19-W21 static data with no provenance or timestamp | Every record identifies source, reporting period, and generation time; displayed data is within the approved freshness threshold; missing, malformed, or stale data blocks publication or suppresses the claim | Validate on every owning pipeline run and at site build. Sponsor must set the threshold before BR-009 is ready |

### Evidence classification model

Use these classes in every epic and story:

| Class | Meaning | Acceptance use |
|---|---|---|
| E0 decision | Product, editorial, policy, or design choice | Required before implementation-ready status |
| E1 observed baseline | Current defect, count, timing, or rendered behavior | Proves the starting state only |
| E2 repository contract | Automated test, deterministic artifact, schema, or build result | Proves implementation behavior at a revision |
| E3 human or protected acceptance | Named visual, accessibility, security, sponsor, or external-platform conclusion | Closes authority-bound gates |
| E4 outcome measurement | Dated GA4, GSC, usability, or production observation | Proves user or operational outcome over a window |

### BR-001 through BR-009 readiness and ownership

| Requirement | Current evidence | Classification and readiness | Accountable owner and required participants |
|---|---|---|---|
| BR-001 | Historical design proposal, current token/layout implementation, current 64-screen matrix, QA thresholds | E1/E2/E3 baseline exists; E0 design brief is missing. Not ready | Calculon accountable; Amy implements; Fry validates; Leela reviews architecture; jmservera approves brand direction |
| BR-002 | Current homepage and SEO infrastructure plus GA4/GSC baseline | E1/E2/E4 exist; E0 primary audience, job, hierarchy, freshness, and selection rules are missing. Split required | Leela accountable; Amy and Farnsworth implement; Zapp reviews SEO; Fry validates; jmservera approves hierarchy |
| BR-003 | Exact 266-page generated corpus, lifecycle evidence, JSON repository artifact, GSC baseline | E1/E2 strong; E0 field model, URL-state, default sort, and migration policy plus external URL-value inventory are missing. Not ready | Leela accountable; Bender owns artifact and inventory; Amy owns explorer; Zapp owns redirect/canonical review; Fry validates; URL owns rollout; jmservera approves migration |
| BR-004 | Existing data pages, datasets, SSR charts, client tool, build and a11y gates | E2 capability exists; E0 first-slice pages, shared schema, state contract, and interaction budgets are missing. Not ready | Amy accountable; Bender owns artifacts; Fry validates; Calculon reviews interaction; Zapp reviews crawlable summaries |
| BR-005 | Existing bar-chart implementation and accessible text alternatives | E1/E2 exist; E0 analytical questions, affected chart inventory, alternatives, and comprehension method are missing. Not ready | Calculon accountable; Farnsworth defines analytical question; Amy implements; Fry validates; jmservera approves selection |
| BR-006 | Broken 2026 page and owning generator are identified; generator tests exist | E1 is conclusive and E2 test surface exists; E0 target length, voice, cadence, claim standard, and approver are missing. Split required | Farnsworth accountable; Leela sets editorial direction; Nibbler reviews generated-content safety; Zapp reviews SEO; Fry validates; jmservera approves publication |
| BR-007 | Existing static embed, backlink, privacy isolation, source guard, and mobile truncation review | E2/E3 platform baseline exists; E0 summary source, maximum length, touch pattern, and action destination are missing. Not ready | Amy accountable; Bender supplies summary data; Hermes reviews embed/privacy; Fry validates |
| BR-008 | Current configuration directly contradicts requested order | E1 is conclusive; no unresolved product decision remains. Implementation-ready after test cases are named | Amy accountable; Fry validates; Zapp reviews navigation discoverability |
| BR-009 | Stale W19-W21 source file and renderer without freshness checks | E1 is conclusive; E0 source of record, calculation policy, threshold, and exception owner are missing. Not ready | Bender accountable for data contract; URL owns workflow gate; Amy owns rendering; Fry validates; jmservera approves source and threshold |

### Decisions that block acceptance

* Whether CR-01 through CR-03 close against the current release candidate before BR-001,
	or receive an explicit sponsor supersession decision. Silence cannot count as release
	acceptance.
* Whether CR-05 is cancelled in favor of BR-003. The coherent answer is cancellation,
	while preserving PR #668's identity and lifecycle evidence as migration input.
* The homepage audience, primary job, content hierarchy, module selection rules, and
	release freshness rules.
* Repository explorer fields, summary source, default sort, filter taxonomy, URL-state
	contract, valuable-URL criteria, and redirect versus canonical policy.
* First-slice data pages, affected charts, analytical questions, and comprehension-test
	threshold.
* Yearly article length, voice, cadence, evidence standard, and named human approver.
* Cost source of record, inclusion/exclusion policy, freshness threshold, and exception
	owner.
* Whether the inherited organic and ranking targets remain product targets. This research
	recommends retaining them with the original six-month windows.

### Multi-system epic and story boundaries

Do not create one story per BR row. The rows cross product decisions, generators, Hugo,
browser behavior, QA, workflows, and external measurement.

| Epic | Requirements | Story boundaries |
|---|---|---|
| E1 release closure and baseline freeze | CR-01, CR-02, CR-03 | Live AT review; interaction captures; status reconciliation; sponsor GO/NO-GO; immutable baseline record |
| E2 controlled operational follow-ups | CR-04, CR-06 | Dynamic canary decision and isolated transaction; cost-harness repair; retained 3/5-run report; budget conclusion. CR-04 does not block redesign |
| E3 experience foundation | BR-001, BR-008 | Design brief and tokens; shared shell/components; navigation order; responsive, reduced-motion, contrast, visual, and AT acceptance |
| E4 editorial discovery | BR-002, BR-006 | Homepage product decision; selection/freshness data contract; homepage SSR and metadata; yearly editorial contract; generator repair; claim traceability; editorial and SEO review |
| E5 repository consolidation | BR-003; supersedes CR-05 | URL and search-value inventory; versioned schema; deterministic artifact; SSR fallback; explorer interactions; redirect/canonical map; sitemap and internal-link migration; staged production observation |
| E6 data exploration and visualization | BR-004, BR-005, BR-007 | First-slice decision; shared schema/state; SSR summaries; interaction controls; chart alternatives and comprehension test; embed action/summary behavior; accessibility/performance/privacy validation |
| E7 cost provenance and freshness | BR-009 | Source/policy decision; versioned record; pipeline generation; stale-data gate; rendering with period and timestamp; failure and exception runbook |

Within each epic, keep decision, data/generator, server-rendered experience, client
enhancement, automated QA, human acceptance, and post-release measurement as separate
stories. A story is done only when its own evidence class is satisfied.

## Phased Delivery Model

### Phase 0: Close the old release contract

Binary gate G0 passes only when all conditions are true:

* CR-01 has a dated keyboard and live screen-reader disposition with findings closed or
	accepted by Fry and the named reviewer.
* CR-02 has the missing interaction-state captures and a dated final disposition.
* The status-of-record timing contradiction is corrected.
* jmservera records CR-03 GO or NO-GO against one immutable revision.
* The accepted screenshot set is frozen as the pre-redesign regression baseline.

If the sponsor chooses not to spend effort accepting the old experience, G0 instead
requires a dated NO-GO/supersession statement. It must not claim that the relaunch was
accepted.

### Phase 1: Amend the BRD and close product decisions

Binary gate G1 passes only when:

* Every objective has a baseline, target, source, owner, and window.
* Every BR has one accountable owner and required reviewers.
* All decisions listed above have dated dispositions.
* CR-05 is cancelled and replaced by the BR-003 migration gate.
* Epic boundaries and evidence classes are approved by Leela and jmservera.

No redesign implementation should start before G1. BR-008 may be prepared but should
ship with the new shell to avoid taking two visual baselines.

### Phase 2: Resolve operational prerequisites and shared contracts

Binary gate G2 passes only when:

* CR-06 produces retained comparable artifacts and a dated budget conclusion.
* The repository URL/value inventory and redirect/canonical policy are complete.
* Versioned repository/data schema and freshness metadata contracts are approved.
* BR-001 design brief and BR-006/BR-009 editorial/data policies are approved.
* Current Hugo/Pagefind budgets and Lighthouse thresholds remain enforced.

CR-04 can execute in an independent operational lane after G0. Its gate is one
allowlisted slug, exact-revision Hermes and sponsor approval, reviewed transaction,
production observation, and tested rollback. It does not block G2 through G6.

### Phase 3: Deliver the editorial and shell vertical slice

Scope: BR-001, BR-002, BR-006, BR-008, and BR-009.

Binary gate G3 requires the approved responsive shell, new navigation order, homepage
SSR and content hierarchy, complete yearly article, and fresh cost record. All automated
SEO, visual, a11y, timing, internal-link, freshness, and generated-content safety checks
must pass. Calculon, Fry, Farnsworth, Zapp, Nibbler, and jmservera provide only the
acceptances routed to their authority.

### Phase 4: Migrate repository discovery

Scope: BR-003 only. Do not enable CR-05.

Binary gate G4 requires zero low-information detail pages in the production candidate,
100% disposition of inventoried valuable URLs, deterministic schema/artifact generation,
useful SSR fallback, all explorer states, sitemap/internal-link correctness, and rollback.
URL and Zapp must approve the migration transaction; jmservera approves release.

### Phase 5: Deliver data exploration and embed behavior

Scope: BR-004, BR-005, and BR-007.

Binary gate G5 requires the agreed first-slice pages, alternative-chart decision,
comprehension result, shared state/schema contract, accessible table or labels, keyboard,
touch, screen-reader, share-state, empty/error, provenance, download, performance,
privacy, and embed overflow/action checks. No unselected data page is implied by this
gate.

### Phase 6: Release and measure outcomes

Binary gate G6 requires one release revision to pass all affected gates, a dated sponsor
GO decision, seven-day production smoke, and scheduled 28-day, three-month, and six-month
reviews. The 28-day review checks functionality and URL-class movement. The three-month
review checks indexing and redirects. The six-month review checks at least 250 monthly
organic sessions and at least 15 top-20 queries. Missing outcome targets do not roll back
a technically healthy release automatically, but they open a product follow-up with an
owner and decision date.

## Requirement Disposition

| Item | Disposition | Required BRD change |
|---|---|---|
| CR-01 | Amend | Name the live AT reviewer, tested revision, severity policy, and closure rule |
| CR-02 | Amend, then freeze | Add the exact missing interaction captures and state that the accepted matrix becomes historical after BR-001 |
| CR-03 | Amend | Permit only GO, NO-GO, or explicit supersession against a named revision |
| CR-04 | Keep separate | Treat as an independent operational rollout, not a redesign dependency |
| CR-05 | Supersede | Replace activation with BR-003 migration rehearsal and URL disposition; preserve identity/lifecycle evidence |
| CR-06 | Amend | Acceptance must include repaired hydration scope, 3/5 retained runs, aggregate report, and dated budget conclusion |
| BR-001 | Split | Design-decision story, token/shell implementation, component migration, automated QA, named acceptance |
| BR-002 | Split | Homepage product/content contract, data selection/freshness, SSR/template, SEO/outcome measurement |
| BR-003 | Split | Inventory, migration policy, schema/artifact, SSR explorer, client enhancement, URL migration, rollout observation |
| BR-004 | Split | First-slice decision, shared schema/state, per-page SSR, interactions, budgets, accessibility |
| BR-005 | Split | Chart inventory/question, alternatives, comprehension test, implementation, accessible fallback |
| BR-006 | Split | Editorial contract, generator root-cause fix, claim provenance, rendered SEO, human review |
| BR-007 | Split | Summary data contract, pointer/touch/keyboard behavior, navigation safety, privacy and overflow QA |
| BR-008 | Amend | Add exact menu labels, one responsive/AT contract test, and release it with BR-001 |
| BR-009 | Split | Source/policy decision, generated record, freshness gate, renderer, failure/runbook evidence |

## Gaps and Clarifying Questions

The following require human input and cannot be resolved from repository evidence alone:

* Does jmservera want a final GO decision for the current relaunch revision, or an explicit
	NO-GO/supersession decision that moves acceptance to the redesigned release?
* Are the inherited targets of 250 monthly organic sessions and 15 top-20 queries still
	product commitments for BRD-CLARACLE-003?
* Which users represent the five-person minimum comprehension test for BR-005?
* What is the authoritative cost source, what costs are included, and how many days old
	may the displayed period be before publication fails?
* Which existing repository URLs have external links or search value? The local GSC
	aggregate does not provide the required per-URL export.

## Recommended Next Research

* Obtain and classify a GSC page export for `/repo/` URLs before writing the redirect map
* Run a lightweight homepage audience/job workshop and record one primary job
* Inventory data pages and bar charts, then select the first slice and analytical questions
* Trace the yearly body truncation through `synthesize_year` and its source excerpts after
	the editorial length and voice decision is approved
* Trace the production cost ledger and workflow once the sponsor identifies the source of
	record and freshness threshold
* Compare the approved BRD amendments against issue/epic structure before implementation
	planning begins
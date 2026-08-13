---
description: Phase 5 release-candidate and outcome-evidence research
---
<!-- markdownlint-disable-file -->

# Task Research: claracle-integrated-release-candidate

| Field | Value |
|---|---|
| Date | 2026-08-12 |
| Researcher / agent | rpi-research |
| Status | Complete |
| Artifact path | `.copilot-tracking/research/2026-08-12/claracle-integrated-release-candidate-research.md` |

## Research Brief

* What to research: the exact Phase 5 release-candidate boundary, currently
  closable evidence, blocking named-human evidence, and future outcome windows.
* Why it matters: Phase 5 may not claim release acceptance by combining evidence
  from different revisions or by substituting automation for live assistive
  technology review.
* Audience or intended use: Phase 5 planning, implementation, named reviewers,
  sponsor, and later outcome observers.
* Scope: the approved plan and BRD, redesigned-release finding map, merged
  Phase 2-4 evidence, current automated test surfaces, Phase 4 deployment, and
  dated outcome obligations.
* Non-goals: changing the approved release policy, fabricating manual evidence,
  or claiming future observations before their due dates.
* Criteria: every severity-1/2 gate must have same-revision closure evidence;
  future observations must have explicit owners and dates.
* Requested outputs: a planning-ready recommendation and evidence boundary.
* Output mode: convergence.

## Research Parameters

| Field | Value |
|---|---|
| Research question(s) | What can Phase 5 complete now, what must block GO, and how should delayed observations be retained? |
| Codebase scope | Phase 5 plan/details, BRD release policy, finding map, browser gates, RPI state |
| External scope | GitHub PR/deployment and live GitHub Pages evidence already collected by the parent |
| Initial internal candidate areas | `.copilot-tracking/`, `docs/review/`, `tests/visual/` |
| Initial external candidate areas | PR 712, deployment run 31645707266, live ranking pages |
| Research posture | focused |
| Posture provenance | bounded internal task with approved source targets |
| Explicit limits / deadline | Do not weaken gates; do not infer future evidence |
| Posture-specific completion basis | focused scope and materiality |
| Edits allowed during research? | no, research-only |
| Resolved evidence root | `.copilot-tracking/` |
| Known constraints / excluded sources | Phase 5 follows the approved V1.1 policy and preserves frozen historical evidence |

## Extension Registry and Provenance

| Kind | Candidate | Match and provenance | Scoped authority or output contract | Selected / skipped reason |
|---|---|---|---|---|
| Instruction | repository Copilot instructions | applies repository-wide | branch/PR, validation, and owner-review requirements | selected |
| Skill | `rpi-research` | Phase 5 evidence framing | research-only artifact and readiness | selected |
| Specialist | Squad | named owner reviews are required later | review outputs only, not sponsor or live-AT substitution | deferred to implementation/review |

## User Participation and Research Decisions

| Checkpoint | Questions or no-interaction rationale | Answers / unanswered | Resulting decision or selected further research |
|---|---|---|---|
| Intake | User explicitly approved merge and continuation | approved | continue automatically into Phase 5 |
| Direction change | No material direction change | none | retain approved release policy |
| Convergence | Evidence identifies one safe sequence | none | plan same-revision closure first; schedule delayed observations |

## Scope and Success Criteria

* Scope: establish a truthful Phase 5 candidate/evidence strategy.
* Assumptions: Phase 4 production evidence is valid only for its own merged
  revision; open DRF rows remain blocking until explicitly closed.
* Success criteria:
  * Questions are answered with workspace evidence.
  * Manual and automated evidence are not conflated.
  * Delayed observations are separated from present release readiness.

## Task Research Requests

* Explicit requests: continue after the approved Phase 4 merge.
* Inferred research questions: identify Phase 5's current release boundary,
  blockers, evidence artifact, and observation schedule.
* Caller constraints and non-goals: automatic continuation does not waive
  named-human or severity gates.

## Direction Controls

| Control type | Direction or boundary | Source / checkpoint | Effect |
|---|---|---|---|
| change | Phase 4 merge authorized; continue | user, 2026-08-12 | Phase 5 is eligible |
| exclude | No gate weakening or fabricated manual evidence | repository and BRD policy | unresolved named evidence remains blocking |

## Research Questions

| # | Sub-question | Type | Priority | Status |
|---:|---|---|---|---|
| Q1 | What defines the immutable Phase 5 candidate? | straightforward | H | answered |
| Q2 | Which redesigned-release findings remain open? | depth | H | answered |
| Q3 | Which evidence can be automated now versus requiring named humans? | depth | H | answered |
| Q4 | How should future outcome windows be handled? | straightforward | H | answered |

## Prior Knowledge Gate

* Existing artifacts reviewed: approved plan, details, BRD, finding map, status
  of record, Phase 4 review/state, PR 712, deployment run 31645707266.
* Reused findings: the release policy, named ownership, and five DRF rows remain
  controlling.
* Superseded / stale: the state still described PR 712 as awaiting merge;
  the parent verified it merged and deployed successfully on 2026-08-12.

## Research Cycle Log

### Cycle 1

* Active research posture: focused; bounded release-evidence investigation.

#### Wave 1: Wider

* Reviewed the Phase 5 plan, BRD risk policy, finding map, historical status,
  test surfaces, and production evidence.
* Reflection: the work divides into same-revision candidate validation, named
  DRF closure, sponsor GO/rollback, and delayed outcome observations.

#### Wave 2: Deeper

* The plan requires one immutable revision, complete automated and named
  evidence, no unresolved severity-1/2 finding, sponsor GO, rollback readiness,
  and observations at release day, seven days, 28 days, three months, and six
  months (C1-C3).
* All five DRF rows remain marked Open and severity 2; DRF-05 explicitly cannot
  be replaced by automated evidence (C4).
* Current browser gates cover meaningful keyboard, filter, responsive, axe,
  touch, and disclosure behavior, but no repository evidence closes a live
  screen-reader review (C5).
* Reflection: implementation can consolidate automation and prepare named-review
  evidence, but GO remains blocked until live AT and named dispositions exist.

#### Wave 3: Contrarian

* Challenged whether PR 712 plus its production deployment could itself be the
  immutable candidate. It cannot close Phase 5 because the finding map forbids
  combining revisions and still lists all named successor gates as Open (C4).
* Challenged whether automated Axe/accessibility-tree tests substitute for live
  screen-reader evidence. The closure rules explicitly reject that substitution
  (C4).
* Challenged whether future windows block creating the candidate. They do not
  block candidate preparation, but they prevent claiming long-term outcome
  completion before their due dates (C2, C3).

#### Parent Synthesis and Disposition

| Material / claim | Evidence IDs | Disposition | Rationale | Treatment |
|---|---|---|---|---|
| Create a new candidate evidence revision | C1, C2, C4 | accepted | same-revision closure is mandatory | selected recommendation |
| Treat prior PR checks as final Phase 5 acceptance | C4 | rejected | named DRF rows remain open | risk |
| Replace live AT review with automation | C4, C5 | rejected | explicitly prohibited | blocker |
| Schedule outcome windows with owners/dates | C2, C3 | accepted | future evidence cannot exist today | implementation requirement |

#### Cycle Re-entry Evaluation

* Another complete three-wave cycle needed: no.
* Stop basis: controlling sources agree; remaining gap is execution and named
  human evidence, not additional research.
* Readiness effect: Ready for planning, with required human-review blockers.

## Evidence Log

* Delegation: inline; the bounded controlling-source trace fit direct research.

### Codebase Evidence

| ID | Claim / finding | Location | Tool | Confidence | Notes |
|---|---|---|---|---|---|
| C1 | Phase 5 requires one immutable candidate and complete automated/named gates | `.copilot-tracking/plans/2026-08-08/claracle-post-relaunch-consolidation-plan.instructions.md:323-336` | search/read | high | controlling plan |
| C2 | Same-revision evidence, sponsor GO, rollback, and dated observations define Phase 5 | `.copilot-tracking/details/2026-08-08/claracle-post-relaunch-consolidation-details.md:318-335` | read | high | implementation details |
| C3 | Severity 1/2 findings block release and outcome windows are explicitly deferred | `docs/brds/claracle-post-relaunch-consolidation-brd.md:148-185` | read | high | approved V1.1 policy |
| C4 | DRF-01 through DRF-05 remain severity 2/Open; automation cannot replace live AT review | `docs/review/claracle-post-relaunch/redesigned-release-finding-map.md:35-51` | read | high | closure rules |
| C5 | Current browser suites cover automated accessibility and interaction paths but contain no live AT disposition | `tests/visual/observatory-a11y.spec.mjs:19-205`, `tests/visual/ranking-explorer.spec.mjs:61-132` | search/read | high | automation only |
| C6 | Phase 4 merged and deployed successfully before Phase 5 | PR 712 and deployment run 31645707266 | `gh`, live probes | high | parent-collected evidence |

### External Evidence

No new external sources used; GitHub-hosted repository evidence is recorded as
execution evidence in C6.

### Contradictions / Conflicts

* The merged Phase 4 revision is production-valid but not sufficient as the
  Phase 5 acceptance candidate because the named DRF closure record is absent.

## Findings Mapped to Questions and Evidence

| Question | Finding | Evidence IDs | Confidence | Implication |
|---|---|---|---|---|
| Q1 | A dedicated evidence revision must bind all candidate reports and named dispositions | C1, C2, C4 | high | create a Phase 5 candidate record |
| Q2 | DRF-01 through DRF-05 remain blocking | C4 | high | cannot record GO yet |
| Q3 | Automated gates can be run now; live AT and named acceptance require humans | C4, C5 | high | prepare evidence, preserve blocker |
| Q4 | Record release-day evidence now and schedule later windows | C2, C3 | high | no fabricated future completion |

## Key Discoveries

* Phase 5 is primarily an evidence transaction, not a broad product rewrite.
* The only non-automatable release blocker is not optional: a named live
  assistive-technology review against the same candidate revision.
* Seven-day, 28-day, three-month, and six-month observations must remain future
  scheduled evidence with explicit ownership.

## Alternatives and Decision State

### Selected Recommendation

* Approach: create a Phase 5 release-candidate evidence record and focused
  automated closure tests for DRF-01 through DRF-04, run all applicable gates,
  obtain same-revision named reviews including DRF-05, then record sponsor GO,
  rollback readiness, deployment, and scheduled outcome windows.
* Rationale: it is the only sequence consistent with the approved severity and
  same-revision rules.
* Evidence refs: C1-C6.
* Implementation impact: tracking evidence, focused browser tests/captures,
  finding-map status, plan/state records, and outcome schedules.
* Confidence: high; only execution and named-human availability remain.

## Risks and Open Questions

* Blocking: DRF-05 requires a named reviewer with real browser/OS/AT/version
  evidence. Automation or simulated AT cannot close it.
* Blocking until reviewed: DRF-01 through DRF-04 need same-candidate captures
  and Fry/Amy dispositions.
* Temporal: seven-day, 28-day, three-month, and six-month evidence cannot be
  completed on 2026-08-12.

## Planning Readiness

* Status: Ready.
* Research disposition: executed.
* Handoff: plan a bounded evidence implementation, preserve human and temporal
  blockers, and do not claim release completion until all severity-2 rows close.

## Sources

No external web sources used.

## Self-Check

* Complete three-wave cycle recorded: yes.
* Material claims have evidence IDs: yes.
* Alternatives and contrarian challenges retained: yes.
* Research-only boundary preserved: yes.

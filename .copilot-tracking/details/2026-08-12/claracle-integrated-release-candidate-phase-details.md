# Claracle Integrated Release Candidate Phase Details

## Task Context

* Task ID: BRD-CLARACLE-003
* Task slug: claracle-integrated-release-candidate
* Branch: `feat/integrated-release-candidate-phase5`
* Plan: `.copilot-tracking/plans/2026-08-12/claracle-integrated-release-candidate-plan.md`
* Research: `.copilot-tracking/research/2026-08-12/claracle-integrated-release-candidate-research.md`
* Current direction: prepare same-revision automated and named acceptance
  evidence without weakening DRF-05 or pre-claiming delayed outcomes.

<!-- phase-id: P01 -->
## P01 — Candidate Evidence Foundation

### P01-T01 — Evidence record

Create a machine-readable candidate record under `data/release/` and a
human-readable review record under `docs/review/claracle-post-relaunch/`.
The record must include candidate SHA, baseline merge/deploy evidence, every DRF
status, named dispositions, automated report references, rollback state, sponsor
decision, deployment evidence, and outcome windows.

The record is evidence about the frozen product commit; it is not required to be
contained by that commit. Evidence-only commits may follow without changing the
candidate. The validator must compare changed paths after the freeze and reject
any runtime, workflow, content, generated-data, or test change.

### P01-T02 — Fail-closed validation

Add an owning script under `scripts/` that validates:

* full lowercase 40-character candidate SHA;
* all evidence entries use that SHA;
* severity-1/2 rows cannot be open when release status is GO;
* DRF-05 cannot be closed without named reviewer/environment/scenario fields;
* scheduled outcome windows have owner and due date;
* completed observations are not future-dated;
* production deployment cannot precede sponsor GO.

Maximum new production files for P01: one JSON record, one schema if justified,
one validator script, and one review document. Reuse existing date/JSON/schema
helpers before adding utilities.

### P01-T03 — Semantic tests

Test valid pre-GO, invalid mixed-SHA, invalid open-blocker GO, invalid synthetic
DRF-05 closure, invalid missing owner/date, invalid premature completion, and a
valid release-day transition.

<!-- phase-id: P02 -->
## P02 — Automated Redesigned-Release Closure

### P02-T01 — DRF-01

Extend existing observatory browser suites rather than adding a new runner.
First reproduce the reported mismatch where `?topic=ai-skills` announces a
reduced count while unfiltered repository cards remain visible. Trace the
rendered list replacement and CSS/DOM ownership, then fix all affected
dimensions rather than special-casing topic. Exercise topic, language, status,
observation period, search, and one representative combined state. For each,
assert visible result count, record criteria, announced count, keyboard changes,
reset, and URL state. Capture the combined state in the revision-tagged visual
matrix.

### P02-T02 — DRF-02

Cover the current replacement disclosure inventory using pointer and keyboard:
repository explorer context/provenance, ranking row context, ranking visual/table
fallback, embed repository context, and copy disclosure. Assert focus order,
Escape behavior, and equivalent text. Capture expanded states without obscuring
controls. Record historical lifecycle-only UI as not applicable because
individual repository pages were intentionally retired; do not recreate it.

### P02-T03 — DRF-03

Mock clipboard success and failure. Activate by keyboard, assert an announced
status, ensure failure guidance is visible, and keep focus on the copy control.
Do not treat this as live-AT evidence.

### P02-T04 — DRF-04

Use representative homepage, article, `/repo/`, ranking, embed, and navigation
links. Assert `:focus-visible` and non-zero visible outlines at desktop/mobile;
run a separate 200% zoom viewport check and capture representative screenshots.

### P02-T05 — Phase 5 equivalence

Retain touch disclosure tests and add a reduced-motion assertion that no required
state depends on animation. Avoid snapshot duplication when semantic assertions
already prove the requirement.

Test ownership is fixed: repository explorer behavior stays in its existing
browser spec; ranking behavior in `tests/visual/ranking-explorer.spec.mjs`;
embed/copy/focus behavior in `tests/visual/observatory-a11y.spec.mjs`; captures
in `tests/visual/observatory-visual-regression.spec.mjs`; validator semantics in
one new `tests/test_validate_release_candidate.py`. Add no runner/config and at
most one new visual spec only if no existing owner can represent a required
candidate state.

<!-- phase-id: P03 -->
## P03 — Candidate Validation And Named Review

### P03-T01 — Freeze

After all implementation and local checks pass, commit the product candidate and
record its exact SHA. Generate every automated report against a clean checkout
of that SHA. Later commits may add or update only Phase 5 evidence records and
state. Any runtime, workflow, content, generated-data, or test change invalidates
the freeze and requires a new candidate SHA and new named review.

### P03-T02 — Amy/Fry evidence

Provide revision-tagged captures and a scenario matrix. Amy owns visual/touch/
zoom/reduced-motion disposition; Fry owns keyboard, focus, automated a11y, and
test adequacy. Both must state finding severity and disposition.

### P03-T03 — DRF-05

Required human evidence fields:

* named reviewer;
* review date;
* candidate SHA;
* operating system and version;
* browser and version;
* screen reader and version;
* keyboard-only and screen-reader scenarios;
* findings, severity, disposition, and unresolved items.

This task is Blocked until a real reviewer performs it. Agent simulation,
accessibility-tree inspection, and Axe do not satisfy it.

### P03-T04 — Remaining owner reviews

* Leela: architecture/final readiness.
* Hermes: security boundary.
* URL: workflow/deployment guardrails when workflow surfaces change.
* Nibbler: generated/external text and AI-output safety when applicable.
* Zapp: migration/SEO evidence.
* Farnsworth/jmservera: editorial and sponsor dispositions.

### P03-T05 — Severity reconciliation

Every severity-1/2 finding must be Closed. Lower findings require owner and due
date. Any exception needs sponsor rationale, compensating control, and expiry.

<!-- phase-id: P04 -->
## P04 — Release And Outcome Ownership

### P04-T01 — GO and rollback

Record sponsor GO only after P03 passes. Prove rollback by identifying the last
known-good main SHA, the revert/deploy path, responsible owner, and validation
probes.

### P04-T02 — PR and deployment

Commit and push all work, open one focused PR, complete hosted checks and latest
Copilot review, resolve every thread, and obtain explicit merge authorization.
After merge, wait for the GitHub Pages deployment and verify the live candidate.

### P04-T03 — Release day

Record the merge SHA, deployment run, production URL probes, public JSON schema
checks, repository index behavior, retired-route 404 behavior, and rollback
readiness.

### P04-T04 — Delayed outcomes

Compute dates from the actual deployment timestamp and retain Scheduled status:

* D+7 smoke;
* D+28 migration and organic evidence;
* M+3 migration and organic evidence;
* M+6 SEO outcome evidence.

Each window must name an owner, expected sources, acceptance question, and
evidence destination. A later PR owns each observation update.

## Completion Boundary

Phase 5 implementation is locally complete when P01-P02 and all automated P03
evidence pass. Release acceptance remains Blocked until P03-T03 and all named
dispositions pass. Long-term outcome closure remains Scheduled after deployment
and is not a reason to fabricate completion in the candidate PR.

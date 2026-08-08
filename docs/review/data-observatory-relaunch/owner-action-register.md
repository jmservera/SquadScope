---
title: Data Observatory Relaunch Owner Action Register
description: Sequenced owner actions and evidence requirements for Claracle relaunch gates that cannot be completed by repository automation
author: SquadScope Squad
ms.date: 2026-08-08
ms.topic: reference
keywords:
  - launch gates
  - acceptance evidence
  - owner actions
  - rollout approval
estimated_reading_time: 7
---

## Purpose

Repository automation proves implementation behavior, not external platform state or
human approval. This register defines the remaining actions, actors, and completion
evidence without recording secret values or granting approval by implication.

## Analytics and search acceptance

Owner: jmservera, with Hermes reviewing production consent behavior.

Current evidence:

* Production renders secret-backed GA configuration on the main site and standalone embed
* The `GA_MEASUREMENT_ID` secret name exists
* Production serves `https://claracle.com/sitemap.xml` as HTTP 200 and `application/xml`
* jmservera confirmed the intended GA4 stream, verified GSC property, root sitemap submission, and GA4-to-GSC product link on 2026-08-02
* The root sitemap is one complete `<urlset>` rather than a sitemap index, so there are no child sitemaps to submit

Required actions:

1. ~~Record denied and granted production consent behavior without exposing identifiers.~~ Done 2026-08-08: private-session HAR captures confirm no analytics before consent and `gtag/js` + `g/collect` after consent; see the [dated baseline](../../growth/ga4-gsc-baseline-2026-07-29.md#production-consent-observations-nfr-008).
2. ~~Transcribe the supplied GSC performance export and capture GA4 values for one explicit date range.~~ Done 2026-08-08; see the [dated baseline](../../growth/ga4-gsc-baseline-2026-07-29.md#baseline-values).
3. ~~Confirm GSC finishes processing the sitemap and review indexed and excluded URL counts.~~ Done 2026-08-08: 294 indexed, 1190 not indexed (as of 2026-08-05).
4. ~~Update the [dated baseline](../../growth/ga4-gsc-baseline-2026-07-29.md) with redacted conclusions and actual values.~~ Done 2026-08-08.

Completion evidence: recorded as of 2026-08-08. NFR-007 numeric baseline, processed-sitemap
conclusion, and NFR-008 denied/granted consent observations are all captured in the dated
baseline; the analytics and search acceptance gate is fully evidenced.

## Security acceptance

Owners: Hermes, URL, and jmservera.

Required actions:

1. ~~Hermes records dispositions for SEC-01 through SEC-05.~~ Done 2026-08-04.
2. ~~Hermes reviews the SEC-02 no-referrer and frame-local consent model.~~ Done 2026-08-04.
3. ~~Hermes reviews the SEC-03 public export field and source-path allowlists.~~ Done 2026-08-04.
4. ~~Hermes records an accepted-risk decision for SEC-05.~~ Done with conditions 2026-08-04.
5. ~~URL reviews protected workflow and secret scope after the real Podcaster environment change.~~ Done through SEC-10 on 2026-08-04.
6. ~~Hermes records the remaining SEC-08 disposition after reviewing the disabled raw HTML contract.~~ Done 2026-08-06; see [security-sign-off-checklist.md](security-sign-off-checklist.md).
7. ~~jmservera and Hermes retain SEC-06 production consent observations without exposing analytics identifiers.~~ Done 2026-08-06; see [security-sign-off-checklist.md](security-sign-off-checklist.md).
8. ~~jmservera records the final production-owner conclusion after external evidence is linked.~~ Done 2026-08-06: NFR-004 approved, sponsor acceptance recorded.

Completion evidence: dated sign-off rows with finding-level dispositions and linked test,
workflow, or production observations. **NFR-004 is fully accepted as of 2026-08-06** (all
ten findings dispositioned); the authoritative surface is
[security-sign-off-checklist.md](security-sign-off-checklist.md).

## Accessibility acceptance

Owners: Fry and a named accessibility reviewer.

Required actions:

1. Identify the tested revision, production URLs, browser, operating system, screen reader, and viewport.
2. Review the retained axe and responsive reports from the final CI revision.
3. Complete keyboard-only navigation for primary navigation, consent, filters, charts, tools, and related links.
4. Complete screen-reader review for headings, landmarks, labels, status changes, chart alternatives, and errors.
5. Record each finding, severity, disposition, reviewer, and date.

Completion evidence: a retained review record combining automated results with keyboard
and screen-reader conclusions. Automated axe success alone does not close NFR-005.

Current automated evidence: the
[2026-08-03 automated evidence record](automated-acceptance-evidence-2026-08-03.md#automated-control-evidence)
ties successful axe, responsive, analytics-contract, Lighthouse, and Python checks to
the tested current-main revision. Manual keyboard and screen-reader conclusions remain
required.

Disposition (2026-08-08, Fry — QA):

* Action 1 (identify revision, URLs, browser, OS, screen reader, viewport) — **partial**:
  revision `f37b49dbd90afd80ba1fd18ec2169d4da31fcc3a` on
  `chore/observatory-timing-gate-and-doc-sync`, production-parity local URLs served by
  `scripts/serve_static.py`, Chromium via Playwright 1.58.2, desktop 1280x800 and mobile
  393x727. **No screen reader / operating-system AT identified because no live
  assistive-technology pass was run.**
* Action 2 (review retained axe and responsive reports) — **done**: retained CI axe and
  responsive evidence ([run 31160859598](https://github.com/jmservera/SquadScope/actions/runs/31160859598)
  and the 2026-08-03 record); the responsive/touch-target subset was re-verified locally
  this run (`a11y-perf.spec.mjs` passing on all four projects).
* Action 3 (keyboard-only navigation) — **automated coverage only**: the CI a11y gate's
  keyboard-label and consent focus-trap/restore checks (`observatory-a11y.spec.mjs`)
  cover controls and the consent modal; these did not re-run locally because the pinned
  `@axe-core/playwright@4.10.2` dependency was unavailable offline. A full manual
  keyboard walkthrough of every surface is not separately recorded.
* Action 4 (screen-reader review) — **NOT done; remains the outstanding item**. No live
  screen-reader pass over headings, landmarks, labels, status changes, chart
  alternatives, or errors was performed.
* Action 5 (record findings) — **done** to the extent evidence exists: no new automated
  violations; the residual is the live-AT gap in actions 1 and 4.

**Standing conclusion:** NFR-005 rests on automated a11y coverage (axe WCAG 2.1 A/AA plus
keyboard-label, consent focus-trap, chart-alternative, and responsive/touch-target checks)
plus rendered-evidence review. It is **not** closed: a live screen-reader (assistive
technology) pass is still required and is the single remaining step before this gate can
be accepted.

## Protected real Podcaster run

Owners: URL, Hermes, a repository administrator, the Podcaster maintainer, and the
environment approver.

Repository controls now separate the automatic dry-run smoke from real generation. Real
generation is manual-only, requires an exact retained publish run and merged article,
and binds to the `podcaster-real-generation` environment. One real dispatch has since
been authorized and completed; see the required actions and evidence table below.

Required actions:

1. ~~Confirm downstream idempotency or authorize one exact eligible week and publish
  run ID.~~ Done 2026-08-04: jmservera authorized `2026-W32` / publish run
  `30782430176`; `candidate.content_sha256` verified to match the merged
  `content/weekly/2026/W32.md` on `main` before dispatch.
2. ~~Create or configure the `podcaster-real-generation` environment with required
  reviewer approval, no self-review, and deployment restricted to `main`.~~ Done
  2026-08-04: environment created with jmservera as required reviewer, self-review
  prevented, and deployment restricted to `main`.
3. ~~Configure the environment-scoped endpoint variable and API-key secret without
  recording their values.~~ Done 2026-08-04: `PODCASTER_ENDPOINT` variable and
  `PODCASTER_API_KEY` secret configured on the environment (values not recorded here).
4. ~~Have Hermes review the environment policy amendment (self-review disablement),
  exact-manifest validation, and retained evidence fields; have URL review the
  environment's secret scope and workflow/pipeline hardening.~~ Done 2026-08-04: Hermes
  accepted disabling `prevent_self_review` with compensating conditions; see
  [SEC-09](security-review.md#findings-and-dispositions). URL reviewed the
  environment's secret scope and workflow/pipeline hardening and found the existing
  controls sufficient, with one low-severity hygiene recommendation for the
  `breaking_news` input; see [SEC-10](security-review.md#findings-and-dispositions).
5. ~~Approve and dispatch one exact week and publish run ID only after maintainer
  authorization.~~ Done 2026-08-04: jmservera dispatched and approved run
  [30908778884](https://github.com/jmservera/SquadScope/actions/runs/30908778884)
  for `2026-W32` / `30782430176`.
6. ~~Retain the approver, week, manifest run ID and digest, article digest, Actions
  URL, downstream job ID, status, and final conclusion.~~ Done 2026-08-04 (see
  evidence table below).

**Self-review amendment (2026-08-04):** the environment's `prevent_self_review`
flag was set `true` when only one reviewer (jmservera) was configured, which
deadlocked approval on the first dispatch (30908570104, cancelled) because the
same account cannot approve its own run. jmservera authorized disabling
`prevent_self_review` (reviewer set and `main`-only branch restriction unchanged)
to unblock the redispatch. This weakens a previously-recorded security control.
Hermes' security disposition for this amendment is recorded as Accept-with-conditions
in [SEC-09](security-review.md#findings-and-dispositions) (action 4). URL reviewed the
environment's secret scope and workflow/pipeline hardening on 2026-08-04 and found the
existing controls sufficient; see [SEC-10](security-review.md#findings-and-dispositions).

Evidence for the completed run:

| Field | Value |
| --- | --- |
| Approver / dispatcher | jmservera |
| Week | `2026-W32` |
| Manifest run ID | `30782430176` |
| Manifest path / SHA-256 | `data/candidates/2026-W32/30782430176/publish-manifest.json` / `d5f1e4210e8e23c43970dc2da60552f3ae96e36ea2794a2121b0985078f9df0c` |
| Article path / SHA-256 | `content/weekly/2026/W32.md` / `b9806f1ff308dd94d8a9c39ab69c7224ccea586628bb49b8c82ded878d17f76b` |
| Actions run (this repo's `trigger-podcast` job) | [30908778884](https://github.com/jmservera/SquadScope/actions/runs/30908778884), conclusion success |
| Downstream Podcaster job ID / response status | `podcast-2026-W32-d07bb05dc073` / accepted (external Podcaster service, not this repo's job) |
| Conclusion | success |

Completion evidence: one successful real downstream run after environment approval —
satisfied by the run above. Action 4's Hermes portion (self-review amendment security
disposition) is satisfied by [SEC-09](security-review.md#findings-and-dispositions).
Action 4's URL portion (secret scope and workflow/pipeline hardening review) is
satisfied by [SEC-10](security-review.md#findings-and-dispositions). Action 4 is fully
done.

## Atomic publish acceptance

Owner: URL, with jmservera reviewing retained evidence.

The repository now includes an isolated proof that executes the production commit step
against a temporary local bare remote. Local validation passed normal publication,
byte-identical rerun, injected failure, unchanged-branch, accepted-tree identity, and
hydrated-tree identity scenarios. The production workflow also detects publish-relative
no-op state before creating immutable backups.

Required actions:

1. ~~Review the atomic proof workflow and production no-op guard.~~ Done through PR #655 and the retained run review.
2. ~~Dispatch the manual `Atomic publish proof` workflow for the reviewed revision.~~ Done 2026-08-05 for `211f0974ce375e427591803cc3f3dfd39e169ead`.
3. ~~Retain its JSON evidence and tree manifests with the workflow URL and reviewer conclusion.~~ Done in [run 31040602642](https://github.com/jmservera/SquadScope/actions/runs/31040602642). The artifact proves one normal commit, an unchanged identical rerun, an injected failure with unchanged ref, equal candidate and accepted trees, equal accepted and hydrated trees, and no reference problems.

Completion evidence: satisfied by the retained `atomic-publish-proof` artifact from run
31040602642 and jmservera's 2026-08-05 reconciliation review.

## Incremental generation cost acceptance

Owners: URL and the budget owner.

The report-only experiment now measures cumulative baseline, topic-hub, data-page, and
repository-page variants from immutable reviewed `main` and `publish` revisions. It does
not run generators, mutate rollout flags, or enforce a blocking threshold.

Required actions:

1. Review and dispatch the manual experiment with immutable reviewed SHAs.
2. Retain either three or five repetitions and the generated aggregate report.
3. Record the budget owner's conclusion before proposing any threshold or rollout.

Completion evidence: retained experiment artifacts and a dated budget-owner conclusion.

Readiness (2026-08-08): the experiment's workload guard now passes locally
(`EXPECTED_CLASS_COUNTS` corrected to `topic_hubs` 5, `data_pages` 3,
`repository_pages` 266; `discover_workload()` returns without raising). The only
remaining step is the manual `build-cost-experiment.yml` `workflow_dispatch` on `main`
with reviewed `main`/`publish` SHAs, which requires owner authority (URL).

## Visual acceptance

Owner: Amy or another named visual reviewer.

The repository implementation removes Star Velocity clipping, stabilizes its scale across
filters, clarifies its semantics, adds mobile consent geometry coverage, serves compressed
static responses, extends lean CSS loading, and bounds Lighthouse concurrency without
weakening thresholds. Topic aggregation remains correct; historical topic backfill
promotion to `publish` remains owner-controlled. Follow the
[screenshot capture checklist](screenshots/README.md) against the final revision with
populated content, resolved consent state, desktop and mobile viewports, light and dark
themes, interaction states, and a dated reviewer conclusion.

Completion evidence: replacement visual matrix with revision metadata and an explicit
accept or reject conclusion. Screenshots alone are not approval.

Disposition (2026-08-08, Amy — visual design): **Accept on rendered evidence, with a
manual interaction-state step remaining.** The replacement visual matrix was captured and
reviewed at revision `f37b49dbd90afd80ba1fd18ec2169d4da31fcc3a` on
`chore/observatory-timing-gate-and-doc-sync` — 64 screenshots plus 4 `metadata.json` and
`index.html` across desktop/mobile x light/dark (desktop 1280x800, mobile 393x727), with
the `observatory-visual-regression.spec.mjs` gate passing 68/68 (route status, breadcrumb
structure, no horizontal overflow, consent resolved before every feature capture). No
route, breadcrumb, or overflow defect was found; the mobile `embed` long-name truncation
is accepted as-is for the syndicated frame. **Remaining item:** the interaction-state
captures required by the [capture checklist](screenshots/README.md) — tool filter
combinations, expanded lifecycle/provenance detail, copy actions, and visible keyboard
focus on the internal-link block — are not part of the automated matrix and remain an open
manual reviewer step before the visual gate is fully closed.

## External metadata and feed validation

Owners: Amy for rendered metadata and jmservera for production access.

Current automated evidence: representative production pages have complete and
internally consistent social metadata and parseable page-specific JSON-LD. The root,
weekly, and representative topic feeds return 200 `application/xml`, parse as RSS,
and use absolute Claracle links. See the
[2026-08-03 automated evidence record](automated-acceptance-evidence-2026-08-03.md).

Required actions:

1. Validate the homepage and one representative article in supported social preview debuggers.
2. Validate representative article and breadcrumb markup with Google Rich Results Test.
3. Validate each relevant page type with Schema.org Validator.
4. Review the retained HTTP, media-type, XML, and absolute-link conclusions for the
  site, weekly, and representative topic feeds.
5. Retain the tested URLs, revision, tool conclusions, reviewer, and date without exposing credentials.

Completion evidence: dated social preview, structured-data, and production feed
conclusions with retained links or redacted records.

## Sponsor rollout decision

Owner: jmservera.

Record a separate decision for each flag. Do not use one blanket approval.

| Flag | Decision | Reviewed revision and evidence | Conditions | Date |
| ---- | -------- | ------------------------------ | ---------- | ---- |
| `dynamic_topic_creation` | Approved (sponsor); technical preconditions outstanding | See Planning Log WI-03 for status | Non-mutating preview (`--dry-run`, `#670`) and the `allow_topics` allowlist now exist; a reviewed canary slug plus Hermes and sponsor approval of the exact revision are still required before activation | 2026-08-05 |
| `repo_pages` | Approved | [PR #668](https://github.com/jmservera/SquadScope/pull/668) - identity backfill, duplicate-identity consolidation, and corpus regeneration; 266 qualified pages, 0 `--seed-lifecycle` mismatches, byte-identical two-run check, 1459 tests passing | Stable identity and lifecycle evidence required (satisfied by PR #668) | 2026-08-05 |

Completion evidence: dated approve, reject, or defer decisions identifying the exact
revision, evidence, conditions, and rollback owner for each flag.

### Proposed dynamic-topic canary (2026-08-08)

A `--dry-run` preview (`scripts/manage_topic_hubs.py`, current date 2026-08-08) reports
1,051 eligible candidates, most at the `min_weekly_issues = 4` floor and dominated by
noise (`agent`, `agents`, `agentic`, `acme`, `acp`, `activejob`, `activerecord`). A naive
activation would create ~1,051 hubs, so a bounded canary is required.

Recommended single canary: **`local-first`** — the strongest, least ambiguous candidate.

* Weekly issue count 7 (highest), across 7 evidence weeks (`2026-W24`, `W27`, `W28`,
  `W29`, `W30`, `W31`, `W32`) with 9 supporting sources.
* Real, durable topic already drawing search demand: GSC shows `/tags/local-first/` with
  13 impressions in the launch baseline window.
* `registry_effect: create-new-term`; proposed hub `content/topics/local-first/_index.md`;
  7 proposed weekly assignments. Not an existing hub and not in `ignore_topics`.

Proposed activation shape: set `allow_topics = ["local-first"]` in
`config/observatory.toml` `[topic_hubs.dynamic_creation]`, keep `enabled = false` until
Hermes and the sponsor approve the exact revision, then flip `enabled = true` for that one
allowlisted slug and review the resulting transaction before expanding.

**Staged 2026-08-08**: `allow_topics = ["local-first"]` is set in `config/observatory.toml`
with `enabled = false`. A `--dry-run` against this revision promotes exactly one slug
(`local-first`) and skips the other 2,500 candidates with `not-in-allowlist`; both rollout
flags remain disabled. This is the exact revision for Hermes and sponsor review; enabling
requires their approval.

### Staged repo_pages activation (2026-08-08)

`repo_pages` is sponsor-approved (ID-02) and its content is already regenerated to match
what the flag would produce (PR #668: 266 qualified pages, byte-identical two-run check).
The flag `[repo_pages] enabled` remains `false` in `config/observatory.toml`, so the
cost-experiment `assert_rollouts_disabled` invariant still holds.

Activation transaction (not yet applied; keeps the "both flags disabled" invariant until
executed under review):

1. URL reviews the workflow and secret scope for the activation run (not yet sought).
2. Set `[repo_pages] enabled = true` in `config/observatory.toml` on a reviewed branch.
3. Run one publish transaction and inspect the committed generated-state diff before deploy.
4. Confirm production rendering and lifecycle; retain the diff and run evidence.
5. Rollback: set `enabled = false` and revert the generated transaction (disabling alone
   does not undo durable mutations).

Owner: jmservera (execution), URL (workflow/secret review).

Required actions: Hermes reviews the exact canary transaction (sanitization, YAML,
evidence-backed weekly assignments, taxonomy, logging, rendering, disabled rollback);
jmservera records sponsor approval of the exact revision.

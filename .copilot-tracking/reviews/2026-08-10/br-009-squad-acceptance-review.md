<!-- markdownlint-disable-file -->

# Squad Acceptance Review: BR-009 Cost Dashboard (PR #697)

## Review Metadata

* Plan: `.copilot-tracking/plans/2026-08-08/claracle-post-relaunch-consolidation-plan.instructions.md`
* Surface reviewed: BR-009 cost dashboard rendering, PR #697, squash-merged as
  `9af3026d` on 2026-08-10
* Reviewers: Fry (Tester/QA), Calculon (Designer), Farnsworth (Analyst),
  Zapp (SEO), Nibbler (Responsible AI), URL (DevSecOps) — run in parallel via
  `Researcher Subagent`, each embodying its `.squad/agents/{name}/charter.md`
* Sponsor evidence: jmservera approved `--legacy-policy exclude-unidentified`
  on 2026-08-10 (recorded earlier in the changes log) and authorized the
  merge of PR #697 after all CI/review gates were green

## Per-Role Verdicts

| Role | Verdict | Notes |
|------|---------|-------|
| Fry | ACCEPT WITH FOLLOW-UPS | 11/11 tests pass, 1558/1558 full suite, clean `hugo --minify`. Found `reconciliation.status` value untested/unguarded and `totals.*` numeric casts missing the same map/slice guard applied to `maximum_age_days` |
| Calculon | ACCEPT WITH FOLLOW-UPS | Full design-token discipline confirmed, WCAG AA contrast holds, strong semantic markup. Non-blocking: no visual-regression baseline yet for the "valid" (non-unavailable) state; breakpoint values are inconsistent repo-wide (pre-existing, not introduced here) |
| Farnsworth | NOT APPLICABLE | Correctly identified this as frontend implementation, not editorial/trend content — declined to manufacture a finding outside its charter |
| Zapp | ACCEPT WITH FOLLOW-UPS | Heading hierarchy clean on `/about/` and `/dashboard/`, zero structured-data/meta scope creep confirmed via diff. Non-blocking: fail-closed copy could linger long-term until activation lands |
| Nibbler | ACCEPT WITH FOLLOW-UPS | Disclosure honest, accessibility floor passes, no dark pattern. Independently found the same `reconciliation.status` gap as Fry — a real hallucination/fabrication-risk finding |
| URL | ACCEPT WITH FOLLOW-UPS | Confirmed zero `.github/workflows/**` or CI-tooling scope in this PR. Ledger commit-path gap is inert (nothing invokes the affected code yet). Recommended a bounded retry/flaky-marking follow-up for `test_atomic_publish_proof_integration` |

## Converging Finding (Actioned)

Both **Fry** and **Nibbler**, working independently, flagged the same gap:
`layouts/partials/cost-dashboard.html` validated that `reconciliation.status`
is *present* (via the nested-required-subkeys check) but never validated its
*value* equals `"reconciled"`. A structurally valid payload with
`"status": "partial"` or `"unreconciled"` would still render a full-confidence
dollar total — directly contradicting BR-009's BRD acceptance criterion that
the site "fail when required data is missing, malformed, **unreconciled**, or
more than 30 days stale." No test covered this case.

Fry additionally flagged that `totals.cost`/`input_tokens`/`output_tokens`
used the same unguarded `float`/`int` cast pattern that two earlier Copilot
review rounds had already found unsafe for `maximum_age_days` (a map/slice
value aborts the whole `hugo` build, not just this page).

Both gaps are fixed in a fast-follow change (see the changes log entry dated
after this review for the specific commit).

## Non-Blocking Follow-Ups (Not Actioned in This Cycle)

1. Add a visual-regression baseline for the cost-dashboard "valid" state
   (Calculon) — deferred until BR-009 activation lands and real data exists.
2. Consolidate the repo's scattered breakpoint values into design tokens
   (Calculon) — pre-existing gap, not introduced by this surface.
3. Scope and review the `analyze`/`generate` job commit-ordering fix before
   BR-009 activation is wired into `crawl-and-publish.yml` (URL) — tracked
   separately as the "ledger commit-path gap" in the changes log.
4. Add a bounded retry or explicit flaky-marking for
   `test_atomic_publish_proof_integration` (URL) — separate, small PR.

## Overall Status

**Complete.** All routed roles reported; the one actionable, converging
finding was fixed and validated before this document was finalized.

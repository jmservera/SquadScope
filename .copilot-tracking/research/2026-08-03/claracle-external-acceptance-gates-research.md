<!-- markdownlint-disable-file -->
# Claracle External Acceptance Gates Research

## Scope

Continue Suggested Next Work item 1 from the 2026-08-03 relaunch review: close as
many security, accessibility, Podcaster, analytics, metadata, feed, and visual
acceptance gates as current repository and public production access allow.

## Evidence Sources

* `.copilot-tracking/research/subagents/2026-08-03/claracle-production-acceptance-gates-research.md`
* `.copilot-tracking/research/subagents/2026-08-03/claracle-protected-acceptance-gates-research.md`
* `.copilot-tracking/plans/2026-08-02/claracle-relaunch-followup-execution-plan.instructions.md`
* `docs/review/data-observatory-relaunch/README.md`
* `docs/review/data-observatory-relaunch/owner-action-register.md`
* `docs/review/data-observatory-relaunch/security-review.md`
* Current `main` revision `4b7c5cf506b2e8b73350ff94ce80669c93810e66`

## Findings

* Current-main CI and local tests provide strong automated security,
  accessibility, analytics-contract, metadata, feed, and hydration evidence.
* Public production checks can retain structural metadata, JSON-LD, sitemap, and
  feed observations without credentials or secret disclosure.
* Live denied and granted analytics observations require a browser with missing
  host libraries plus jmservera and Hermes review.
* GSC processing and indexed or excluded counts require private property access.
* Hermes security disposition, manual keyboard and screen-reader review, visual
  acceptance, and sponsor decisions are human authority boundaries.
* Real Podcaster evidence remains split between an unprotected real run and an
  environment-bound dry run. Dispatching another real run is unsafe without the
  documented policy, idempotency, and approval preconditions.
* Atomic publish proof is separate follow-up work and is not part of this
  external-acceptance execution cycle.

## Selected Approach

1. Run and retain credential-free production response, XML, metadata, and schema
   checks against representative URLs.
2. Run focused security, lifecycle, publication, workflow, and full repository
   validation against the exact current-main revision.
3. Add an automated evidence record that reports observations without granting
   human acceptance.
4. Reconcile the owner action register and acceptance index with newly retained
   evidence while leaving authority-bound rows pending.
5. Review fulfillment and identify the shortest owner handoffs that remain.

## Rejected Alternatives

* Do not dispatch real Podcaster generation as a validation probe because it can
  create duplicate downstream work.
* Do not configure GitHub environment policy without repository-administrator and
  workflow-owner decisions.
* Do not install privileged browser system dependencies through this workflow.
* Do not infer GSC processing, security approval, accessibility acceptance, or
  visual acceptance from public probes or green CI.

## Success Criteria

* Every executable current-main and public-production check has a dated retained
  result tied to the tested revision.
* Newly evidenced automated gates are distinguished from pending reviewer or
  owner conclusions.
* No secret value, analytics identifier, private cookie, or protected account
  output is retained.
* Both rollout flags remain disabled.
<!-- markdownlint-disable-file -->
# Planning Log: Fix observatory_repos.py Lifecycle Ledger Duplicate-Identity Bug

## Discrepancy Log

### Unaddressed Research Items

* DR-01: Whether GitHub issue #652 already scopes this exact duplicate-identity
  mechanism or only the narrower "ledger is not refreshed while repo_pages disabled"
  framing was left as an open clarifying question by the Researcher Subagent.
  * Source: .copilot-tracking/research/subagents/2026-08-04/observatory-repos-ledger-duplicate-identity-bug.md (Clarifying questions section)
  * Reason: Not read directly during this planning session; the plan proceeds on
    the confirmed root-cause diagnosis regardless, since #652's existing test
    comment already anticipates "the ledger-refresh fix," so the fix direction is
    not blocked on this answer.
  * Impact: low

* DR-02: `attach_related_repositories()`, `rename_aliases()`, and
  `apply_configured_renames()` are flagged as structurally assuming key stability
  (no slug-collision or duplicate-key awareness) but were not empirically confirmed
  to misbehave under the duplicate-identity bug.
  * Source: .copilot-tracking/research/subagents/2026-08-04/observatory-repos-ledger-duplicate-identity-bug.md (Other repo_pages-adjacent code/tests assuming key stability)
  * Reason: Out of scope for this fix; the root-cause fix in
    `load_repository_histories()` should make duplicate keys unreachable in the
    intended flow, reducing urgency.
  * Impact: low — tracked as follow-on work (WI-03)

* DR-03: `seed_lifecycle()`'s parity guard (lines 849-855) and
  `existing_repository_identities()` both dedupe by `(display_name, slug)`/
  `(full_name, slug)` sets, so a `name:`-keyed orphan and its numeric-keyed
  canonical twin collapse into one set element — the guard can pass while
  `lifecycle_ledger_payload()` still persists the full, non-deduplicated
  `histories` dict, meaning `seed_lifecycle()` is not unconditionally safe against
  a recurrence of this bug class by count alone. No plan step or follow-on work
  item proposes hardening this guard (count-based or key-based duplicate
  detection) independent of the `load_repository_histories()` fix.
  * Source: .copilot-tracking/research/subagents/2026-08-04/observatory-repos-ledger-duplicate-identity-bug.md (Does `seed_lifecycle()` share the bug? section, "Important caveat" paragraph)
  * Reason: Phase 1's reverse-index fix should make duplicate keys structurally
    unreachable, so this blind spot becomes dormant for the scenario this plan
    fixes; it was not carried into Suggested Follow-On Work alongside the related
    WI-03 items.
  * Impact: low — recommend adding to follow-on work (see WI-05)

* DR-04 (resolved): The merged recurrence test initially added the ID-bearing
  week between loads, stopping at migration instead of reloading an already
  migrated ledger against unchanged raw files.
  * Resolution: Both weeks now exist before pass one; pass two consumes the
    persisted numeric ledger and the same raw files, asserting one identity and
    two non-duplicated observations.
  * Impact: high before remediation; resolved by Phase 2 Step 2.1

* DR-05 (resolved): Earlier completion evidence covered only the focused
  observatory tests rather than the required full `tests/` suite.
  * Resolution: Final validation completed with 1,456 tests and 34 subtests
    passing, plus Ruff, Hugo, Pagefind, and internal-link checks.
  * Impact: medium before remediation; resolved by Phase 4

### Plan Deviations from Research

* DD-01: Research recommends checking issue #652 directly before finalizing scope;
  the plan proceeds without that check.
  * Research recommends: fetch/read issue #652 to confirm framing alignment
  * Plan implements: proceeds directly with the confirmed code-level root cause,
    since the fix is independently verified via isolated sandbox reproduction and
    the existing `TEMP (#652)` test comment already corroborates the same drift
    symptom
  * Rationale: avoids blocking implementation on a low-impact confirmation step;
    Phase 2 Step 2.2 explicitly reconciles with issue #652 by restoring its
    referenced strict assertions

* DD-02 (resolved): The runtime slug-collision guard merged without an explicit
  unit test for its diagnostic failure contract.
  * Resolution: Added a synthetic collision test that verifies both conflicting
    history keys and the output slug in the raised `ValueError`.

* DD-03: Full validation exposed a pre-existing CSS bundle test mismatch with
  Hugo 0.146 minification and the current article visual selector.
  * Plan specifies: Fix minor validation issues surfaced by the full suite.
  * Implementation differs: The test parser now accepts valid quoted or unquoted
    `href` attributes and asserts `.article-cover`, the selector currently owned
    by `article-visuals.css`; production templates and CSS remain unchanged.
  * Rationale: Preserve the bundle-boundary assertion across supported Hugo
    minification output without weakening the test.

## Implementation Paths Considered

### Selected: Full-Name Reverse Index With In-Place Key Migration

* Approach: Build a `full_name -> current key` reverse index once per
  `load_repository_histories()` invocation and consult it before minting a new
  history, migrating in place when a match is found
* Rationale: Smallest, most surgical change; consistent with the existing
  single-pass migration pattern already in the codebase; no behavior change for
  the already-tested single-pass migration scenario
* Evidence: .copilot-tracking/research/subagents/2026-08-04/observatory-repos-ledger-duplicate-identity-bug.md (Fix location section, recommended index-based approach)

### IP-01: Freeze Ledger Keys and Avoid Reprocessing Weeks Already Reflected in the Ledger

* Approach: Redesign `load_repository_histories()` so raw weeks already reflected
  in a loaded ledger are not fully reprocessed from scratch on every run, avoiding
  the reprocessing step that re-derives id-less observations
* Trade-offs: Would eliminate an entire class of future reload bugs, but is a much
  larger, more invasive change to the ledger's load/merge architecture, higher risk
  of unintended side effects on other identity-assuming functions
  (`apply_configured_renames()`, `attach_related_repositories()`, `rename_aliases()`),
  and not clearly required to fix the specific bug at hand
* Rejection rationale: Higher risk and scope than necessary for this fix; the
  reverse-index approach fully resolves the reproduced bug with minimal blast
  radius; this remains available as a future architectural improvement if
  additional reload-related bugs surface (see WI-04)

## Suggested Follow-On Work

* WI-01: Flip `repo_pages.enabled = true` on `main` and record the Hermes/URL/
  jmservera sponsor sign-off — (high priority once this fix lands)
  * Source: original user request; deferred per repo governance
  * Dependency: this plan's Phases 1-4 must complete and merge first; sign-off
    process is separately tracked in
    docs/review/data-observatory-relaunch/owner-action-register.md and
    .copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md
    Phases 4-5

* WI-02: Close or update GitHub issue #652 once this fix lands, referencing the
  precise root-cause mechanism found here (medium priority)
  * Source: research cross-reference to #652
  * Dependency: this plan's Phase 2 Step 2.2 (restored assertions) must be
    merged first

* WI-03: Review `attach_related_repositories()`, `rename_aliases()`, and
  `apply_configured_renames()` for latent duplicate-key/slug-collision assumptions
  as defense-in-depth (low priority)
  * Source: .copilot-tracking/research/subagents/2026-08-04/observatory-repos-ledger-duplicate-identity-bug.md (Other repo_pages-adjacent code/tests assuming key stability)
  * Dependency: none; can be done independently after this fix lands

* WI-04: Consider the more invasive "avoid reprocessing raw weeks already
  reflected in the ledger" redesign (IP-01) if further reload-related bugs surface
  after this fix (low priority, speculative)
  * Source: Implementation Paths Considered, IP-01 rejection rationale
  * Dependency: none; only pursue if a new class of reload bug is found

* WI-05: Harden `seed_lifecycle()`'s parity guard and
  `existing_repository_identities()` to detect duplicate ledger keys by count
  (not just by collapsing into a `(display_name, slug)`/`(full_name, slug)` set),
  as defense-in-depth against a future recurrence of the duplicate-identity bug
  class independent of the `load_repository_histories()` fix (low priority)
  * Source: .copilot-tracking/research/subagents/2026-08-04/observatory-repos-ledger-duplicate-identity-bug.md (Does `seed_lifecycle()` share the bug? section, "Important caveat" paragraph); Discrepancy Log DR-03
  * Dependency: none; can be done independently after this fix lands

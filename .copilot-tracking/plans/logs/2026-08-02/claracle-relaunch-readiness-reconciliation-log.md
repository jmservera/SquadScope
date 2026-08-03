<!-- markdownlint-disable-file -->
# Planning Log: Claracle Relaunch Readiness Reconciliation

## Discrepancy Log

Gaps and differences identified between research findings and the implementation plan.

### Unaddressed Research Items

* DR-01: GA4/GSC baseline, production consent, and sitemap processing evidence
  * Source: research 2026-08-02 (Unmet launch gates); issue #599
  * Reason: The connection, property verification, root sitemap submission, and product link are complete; this plan only registers and sequences the remaining external evidence work
  * Impact: high (blocks OBJ-2/OBJ-4 baselines and NFR-008 production acceptance)
* DR-02: repo_pages and dynamic_topic_creation rollout enablement
  * Source: config/observatory.toml flags disabled; PRD section 13
  * Reason: Requires separate sponsor approval and its own rollout plan
  * Impact: medium (Wave 2/dynamic scope not live)
* DR-03: Incremental generation cost/time design spike (Q-01/NFR-009)
  * Source: PRD section 14; BRD section 13
  * Reason: Needs a measurement spike, not documentation reconciliation
  * Impact: medium (capacity risk unquantified)
* DR-04: Open issues #626 (Lighthouse follow-ups) and #622 (UX polish) reconciliation - RESOLVED 2026-08-02
  * Source: research 2026-08-02 (Open issues); issues #626, #622
  * Resolution: Plan Step 2.3 now lists #644/#626/#622/#599/#594 in the status-of-record; Step 4.1 adds #626 and #622 to the gate register with a disposition (readiness scope or explicit out-of-scope). Details Step 2.3 (status-of-record scope) and Step 4.1 (gate list) both enumerate #626/#622.
  * Impact: closed (readiness view and gate register now cover the epic's open work)
* DR-05: FR-041 internal link-checker partial status not reconciled in the PRD/status-of-record - RESOLVED 2026-08-02
  * Source: research 2026-08-02 (Verified findings, FR-041)
  * Resolution: Plan Step 3.2 now records the FR-041 link-check partial status (test-level only, no CI link tool); Details Step 3.2 success criteria captures the same partial-satisfaction statement.
  * Impact: closed (FR-041 traceability now explicitly marked partial)

### Plan Deviations from Research

* DD-01: External/human launch gates (security sign-off, accessibility, Podcaster run, visuals, sponsor approval) are registered and sequenced rather than executed
  * Research recommends: close the gates
  * Plan implements: consolidate into one owner/evidence register with sequencing
  * Rationale: these gates depend on humans and external platforms outside a planning/documentation change; execution belongs to their owners with dated evidence

## Implementation Paths Considered

### Selected: Single reconciliation plan (docs + status-of-record) with #644 triage first

* Approach: triage the live deploy failure, correct the three plan checklists, reconcile PRD/BRD, and consolidate a launch-gate register; defer external gate execution
* Rationale: directly answers "what's missing" with accurate state and a single readiness view; low-risk and mostly documentation
* Evidence: research 2026-08-02 (Planning approach)

### IP-01: One mega-plan that also implements every launch gate

* Approach: fold GA4/GSC, security, a11y, Podcaster run, and rollout into one plan
* Trade-offs: comprehensive but mixes documentation with external/human execution; long-lived and hard to validate
* Rejection rationale: each external gate merits its own plan and owner; a mega-plan would stall on human dependencies

### IP-02: Skip planning and edit docs directly

* Approach: immediately edit PRD/BRD/plans
* Trade-offs: faster but loses traceability and the #644 dependency ordering
* Rejection rationale: the reconciliation touches multiple documents and a live blocker; a checklist keeps it ordered and reviewable

## Suggested Follow-On Work

* WI-01: GA4/GSC evidence completion plan (high) - transcribe the dated baseline, retain denied/granted consent observations, and review sitemap processing
  * Source: owner action register; remaining human-action checklist after closed issue #599
  * Dependency: sponsor/platform access
* WI-02: Deploy failure #644 dedicated fix plan (high) - NOT NEEDED. #644 is CLOSED: root cause was a dangling `source_manifest.path` (`data/candidates/2026-W31/30669054860/publish-manifest.json`) breaking the Podcaster smoke gate; resolved by `#645`/`#646`, deploy-site green since 2026-08-01. No dedicated fix plan required.
  * Source: open issue #644 (now closed)
  * Dependency: none
* WI-03: repo_pages rollout plan (medium) - enable flag, lifecycle acceptance, sponsor approval
  * Source: config/observatory.toml; PRD FR-020-022
  * Dependency: sponsor approval, security/lifecycle evidence
* WI-04: Dynamic topic-creation rollout plan (medium)
  * Source: PRD FR-004
  * Dependency: sponsor approval, security evidence
* WI-05: Incremental-generation-cost design spike (medium) - quantify hub/data/repo build cost (Q-01/NFR-009)
  * Source: PRD section 14; BRD section 13
  * Dependency: none

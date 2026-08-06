---
title: Security Findings Sign-Off Checklist
description: Formal acceptance gate for all security findings with named reviewer sign-offs and dispositions
author: SquadScope Squad
ms.date: 2026-08-06
ms.topic: reference
keywords:
  - security
  - sign-off
  - findings
  - nfr-004
estimated_reading_time: 8
---

<!-- markdownlint-disable-file -->

## Overview

NFR-004 (Security Acceptance) requires disposition and named reviewer sign-off for every security finding before relaunch acceptance. This document provides the formal sign-off template and tracks approval status.

**Current Status**: ✅ **NFR-004 APPROVED** (2026-08-06) — All 10 findings approved by reviewers; sponsor acceptance recorded. Release authorization complete.

## Security Findings Disposition Matrix

### SEC-01: Candidate-Title Sanitization (High)

| Field | Value |
|-------|-------|
| **Finding** | Dynamic hub candidate titles require bounded sanitization and structured serialization |
| **Severity** | High |
| **Owned by** | Farnsworth (implementation), Hermes (review) |
| **Implementation** | ✅ Complete - `scripts/manage_topic_hubs.py` bounds via `sanitize_text()`, rejects boundaries/HTML/injection, structured YAML frontmatter |
| **Tests** | ✅ Complete - `tests/test_topic_hubs.py` exercises adversarial title matrix, no-mutation assertions, YAML parsing |
| **Hermes Disposition** | ✅ **Approved** (2026-08-04) |
| **Evidence** | [docs/review/data-observatory-relaunch/security-review.md#sec-01-candidate-title-sanitization-verification-hermes](./security-review.md#sec-01-candidate-title-sanitization-verification-hermes) |
| **Condition** | Dynamic creation remains disabled until separate canary review and approval |
| **Sign-Off Gate** | ✅ Hermes approved; dynamic-creation gate remains enforced |
| **NFR-004 Contribution** | ✅ Satisfied |

---

### SEC-02: Embed Referrer Policy and Consent Isolation (Medium)

| Field | Value |
|-------|-------|
| **Finding** | Embed snippets require an explicit referrer policy and cross-origin consent does not transfer |
| **Severity** | Medium |
| **Owned by** | Amy (visual/UX), Hermes (privacy review) |
| **Implementation** | ✅ Complete - `layouts/partials/visuals/observatory-chart.html` sets `referrerpolicy="no-referrer"`, frame-local analytics consent only |
| **Tests** | ✅ Complete - Consent-wiring tests and frame-local isolation verified |
| **Hermes Disposition** | ✅ **Approved** (2026-08-04) |
| **Evidence** | [docs/review/data-observatory-relaunch/security-review.md#sec-02-embed-referrer-policy-and-consent-isolation-verification-hermes](./security-review.md#sec-02-embed-referrer-policy-and-consent-isolation-verification-hermes) |
| **Condition** | Publisher-controlled markup can override attribute; Claracle controls only the default snippet |
| **Sign-Off Gate** | ✅ Hermes approved |
| **NFR-004 Contribution** | ✅ Satisfied |

---

### SEC-03: Public Export Allowlist (Medium)

| Field | Value |
|-------|-------|
| **Finding** | Public export fields need a documented allowlist to prevent future accidental expansion |
| **Severity** | Medium |
| **Owned by** | Bender (data pipeline), Hermes (privacy review) |
| **Implementation** | ✅ Complete - `scripts/export_observatory_dataset.py` defines `PUBLIC_CSV_FIELDS`, `PUBLIC_METADATA_FIELDS`, `PUBLIC_WEEKLY_FIELDS` with fail-closed validation |
| **Tests** | ✅ Complete - Exact-schema tests enforce allowlist; schema mutations fail CI |
| **Hermes Disposition** | ✅ **Approved** (2026-08-04) |
| **Evidence** | [docs/review/data-observatory-relaunch/security-review.md#sec-03-public-export-allowlist-verification-hermes](./security-review.md#sec-03-public-export-allowlist-verification-hermes) |
| **Condition** | Any new CSV/metadata field requires explicit code change, test update, and Hermes review before merge |
| **Sign-Off Gate** | ✅ Hermes approved |
| **NFR-004 Contribution** | ✅ Satisfied |

---

### SEC-04: Lifecycle Deletion Verification (Medium)

| Field | Value |
|-------|-------|
| **Finding** | Lifecycle deletion depends on manually reviewed overrides |
| **Severity** | Medium |
| **Owned by** | Bender (repository generation), Hermes (lifecycle policy review) |
| **Implementation** | ✅ Complete - `scripts/observatory_repos.py` requires valid `deletion_confirmed_at` ISO date, validates three-year retention, ledger-only seed mode, fail-closed absence handling |
| **Tests** | ✅ Complete - `tests/test_observatory_repos.py` exercises rename aliases, archive evidence, confirmed deletion, three-year retention, expiry removal, absence fail-closed, stable-ID migration |
| **Hermes Disposition** | ✅ **Approved** (2026-08-04) |
| **Evidence** | [docs/review/data-observatory-relaunch/security-review.md#sec-04-lifecycle-deletion-verification-hermes](./security-review.md#sec-04-lifecycle-deletion-verification-hermes) |
| **Condition** | Operator must pair override, source evidence, ledger diff, aliases, generated page, and expiry removal in review |
| **Sign-Off Gate** | ✅ Hermes approved |
| **NFR-004 Contribution** | ✅ Satisfied |

---

### SEC-05: Phrase-Based Injection Detection Risk Assessment (Medium)

| Field | Value |
|-------|-------|
| **Finding** | Phrase-based injection detection has known semantic false-negative risk |
| **Severity** | Medium |
| **Owned by** | Farnsworth (analysis), Hermes (risk assessment) |
| **Implementation** | ✅ Complete - `scripts/sanitize_repo_content.py` detects lexical patterns, fences untrusted content, closes prompts, uses canary detection, validates output; all retain defense-in-depth controls |
| **Tests** | ✅ Complete - Prompt lint and red-team corpus in test suite |
| **Hermes Disposition** | ✅ **Accepted-with-Conditions** (2026-08-04) |
| **Evidence** | [docs/review/data-observatory-relaunch/security-review.md#sec-05-phrase-based-injection-detection-risk-assessment-hermes](./security-review.md#sec-05-phrase-based-injection-detection-risk-assessment-hermes) |
| **Conditions** | 1. PR-review-before-merge gate must remain active; 2. Red-team corpus must grow with real attempts; 3. Any move to auto-publish requires new Hermes review |
| **Sign-Off Gate** | ✅ Hermes accepted-with-conditions (conditions enforced via process gates) |
| **NFR-004 Contribution** | ✅ Satisfied |

---

### SEC-06: Repository-Side Secret and Wiring Verification (Medium)

| Field | Value |
|-------|-------|
| **Finding** | Repository-side secret handling and environment wiring require verification |
| **Severity** | Medium |
| **Owned by** | URL (infrastructure/secrets), Hermes (security verification) |
| **Implementation Status** | ✅ Complete - Repository-side controls: `GA_MEASUREMENT_ID` and `GSC_SITE_VERIFICATION` mapped via GitHub Actions secrets only in deploy, no credentials in generated code, forks do not inherit secrets |
| **External Evidence Required** | Production GA4 stream operation, GSC verification, sitemap submission, root endpoint linkage (owned by external platforms, not repository code) |
| **Hermes Disposition** | ✅ **Approved** (2026-08-06) - External GA4/GSC configuration verified; production environment controls confirmed |
| **URL Disposition** | ✅ **Approved** (2026-08-06) - Environment and workflow security review complete; infrastructure controls verified |
| **Evidence Slot** | [docs/growth/ga4-gsc-baseline-2026-07-29.md](../../growth/ga4-gsc-baseline-2026-07-29.md) (external configuration confirmation) |
| **Sign-Off Gate** | ✅ Approved (Hermes + URL disposition recorded 2026-08-06) |
| **NFR-004 Contribution** | ✅ **Satisfied** (external verification complete, production ready) |

---

### SEC-07: Workflow Permissions and Credential Persistence (Medium)

| Field | Value |
|-------|-------|
| **Finding** | Repository workflows require scoped permissions and explicit credential management |
| **Severity** | Medium |
| **Owned by** | URL (workflow security) |
| **Implementation** | ✅ Complete - Phase 5 remediation: job-level `contents: write` scoping, `persist-credentials: false` on checkout steps that don't push, explicit authentication only at authorized push points |
| **Tests** | ✅ Complete - Checkov and Zizmor scans pass |
| **URL Disposition** | ✅ **Approved** (via Phase 5 workflow remediation acceptance) |
| **Evidence** | [`.github/workflows/`](../../../.github/workflows/) - all squad workflows reviewed and scoped |
| **Sign-Off Gate** | ✅ URL approved (repository-wide Zizmor cleanup included) |
| **NFR-004 Contribution** | ✅ Satisfied |

---

### SEC-08: Raw HTML Rendering Disabled (Informational)

| Field | Value |
|-------|-------|
| **Finding** | Raw HTML rendering must remain disabled in Hugo goldmark configuration |
| **Severity** | Informational |
| **Owned by** | Amy (Hugo configuration), Hermes (security verification) |
| **Implementation** | ✅ Complete - `hugo.toml` sets `markup.goldmark.renderer.unsafe = false` |
| **Tests** | ✅ Complete - Verified in rendered-content tests; no unsafe HTML in output |
| **Hermes Disposition** | ✅ **Approved** (2026-08-06) - Raw HTML disabled in goldmark configuration verified |
| **Evidence** | [hugo.toml](../../hugo.toml) line configuration |
| **Sign-Off Gate** | ✅ Approved (Hermes disposition recorded 2026-08-06) |
| **NFR-004 Contribution** | ✅ **Satisfied** (configuration stable and verified) |

---

### SEC-09: Self-Review Prevention Disabled (Solo Maintainer) (Medium)

| Field | Value |
|-------|-------|
| **Finding** | `prevent_self_review` disabled on `podcaster-real-generation` environment (solo maintainer deadlock) |
| **Severity** | Medium (risk accepted) |
| **Owned by** | Hermes (environment security policy) |
| **Status** | ✅ **Accepted-with-Conditions** (2026-08-04) |
| **Conditions** | 1. `wait_timer` set to 10 minutes (applied); 2. Pre-approval input cross-check mandatory; 3. Post-run evidence check mandatory; 4. Reinstate `prevent_self_review: true` if second reviewer added |
| **Rationale** | jmservera already holds admin access to `main`, workflow files, and secrets; independent-scrutiny boundary does not exist; risk controls are `branch_policy`, `if: github.ref == 'refs/heads/main'`, required exact inputs, fail-closed manifest validation, no secrets logged, retained evidence |
| **Sign-Off Gate** | ✅ Hermes accepted-with-conditions (conditions enforced via workflow design) |
| **NFR-004 Contribution** | ✅ Satisfied |

---

### SEC-10: GitHub Actions Security and Token Management (Medium)

| Field | Value |
|-------|-------|
| **Finding** | GitHub Actions permissions and token management require least-privilege enforcement |
| **Severity** | Medium |
| **Owned by** | URL (CI/CD infrastructure) |
| **Status** | ✅ **Approved** (via existing controls) |
| **Controls** | Top-level `permissions: contents: read` with job-level `contents: write` only where needed; GITHUB_TOKEN scope limited to each job; no long-lived PATs in workflows |
| **Evidence** | [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml) top-level permissions |
| **Sign-Off Gate** | ✅ URL approved (Phase 5 remediation validated) |
| **NFR-004 Contribution** | ✅ Satisfied |

---

## Summary Sign-Off Table

| Finding | Severity | Status | Disposer | Date | Signature | Notes |
|---------|----------|--------|----------|------|-----------|-------|
| SEC-01 | High | ✅ Approved | Hermes | 2026-08-04 | [Hermes disposition](./security-review.md#sec-01) | Dynamic creation remains disabled |
| SEC-02 | Medium | ✅ Approved | Hermes | 2026-08-04 | [Hermes disposition](./security-review.md#sec-02) | Publisher controls snippet override |
| SEC-03 | Medium | ✅ Approved | Hermes | 2026-08-04 | [Hermes disposition](./security-review.md#sec-03) | Allowlist enforced in code |
| SEC-04 | Medium | ✅ Approved | Hermes | 2026-08-04 | [Hermes disposition](./security-review.md#sec-04) | Operator review required per override |
| SEC-05 | Medium | ✅ Accepted-with-Conditions | Hermes | 2026-08-04 | [Hermes disposition](./security-review.md#sec-05) | PR-review, red-team, auto-publish gate |
| SEC-06 | Medium | ✅ Approved | Hermes, URL | 2026-08-06 | [Security sign-off checklist](./security-sign-off-checklist.md#sec-06) | External config confirmed; production ready |
| SEC-07 | Medium | ✅ Approved | URL | 2026-08-06 | [Phase 5 remediation](../../../.github/workflows/) | Workflow permissions scoped |
| SEC-08 | Informational | ✅ Approved | Hermes | 2026-08-06 | [Security sign-off checklist](./security-sign-off-checklist.md#sec-08) | Repository control verified and approved |
| SEC-09 | Medium | ✅ Accepted-with-Conditions | Hermes | 2026-08-04 | [Hermes disposition](./security-review.md#sec-09) | Conditions: wait_timer, input check, evidence check |
| SEC-10 | Medium | ✅ Approved | URL | 2026-08-06 | [Phase 5 remediation](../../../.github/workflows/) | Token management controls enforced |

---

## NFR-004 Acceptance Gate

**NFR-004 Status**: ✅ **APPROVED** (2026-08-06) — All security findings approved; relaunch authorized by sponsor

**Currently Satisfied**:
- All 10 findings (SEC-01 through SEC-10) have dated Hermes or URL dispositions ✅
- SEC-06 Hermes + URL approvals recorded (2026-08-06) ✅
- SEC-08 Hermes approval recorded (2026-08-06) ✅
- jmservera sponsor final security acceptance recorded (2026-08-06) ✅

**Acceptance Criteria**:
- [x] SEC-06 Hermes disposition recorded with evidence (2026-08-06)
- [x] SEC-06 URL disposition recorded with evidence (2026-08-06)
- [x] SEC-08 Hermes sign-off recorded (2026-08-06)
- [x] jmservera records final security acceptance (2026-08-06)
- [x] All 10 findings have dispositions (approved or accepted-with-conditions)
- [x] All conditions are enforced or documented as process controls

---

## Sign-Off Procedure

### For Named Reviewers (Hermes, URL)

1. Review the specific finding details and implementation evidence
2. Document your disposition: **Approved**, **Accepted-with-Conditions**, or **Rejected**
3. If accepted-with-conditions, enumerate the conditions
4. Add your name, date, and link to the evidence
5. Update the sign-off table with your signature

### For Production Owner (jmservera)

1. Collect all individual reviewer dispositions
2. Confirm every condition is enforced or documented
3. Record your sponsor security acceptance
4. Final acceptance closes NFR-004

---

## Cross-References

- Primary security review: [docs/review/data-observatory-relaunch/security-review.md](./security-review.md)
- Evidence index: [docs/review/data-observatory-relaunch/README.md](./README.md)
- Implementation plan: [`.copilot-tracking/plans/2026-07-30/claracle-data-observatory-relaunch-review-remediation-plan.instructions.md`](../../.copilot-tracking/plans/2026-07-30/claracle-data-observatory-relaunch-review-remediation-plan.instructions.md)

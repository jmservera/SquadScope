<!-- markdownlint-disable-file -->
# Research: Claracle Data Observatory Relaunch Review Remediation

## Scope

Plan the code corrections, CI repairs, runtime proofs, and external acceptance work identified by the 2026-07-30 review of PR #623, including the user-requested visible breadcrumb correction.

## Sources

* `.copilot-tracking/reviews/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-review.md`
* `.copilot-tracking/reviews/quality/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-quality.md`
* `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-001-validation.md` through `claracle-data-observatory-relaunch-remediation-plan-010-validation.md`
* `.copilot-tracking/research/subagents/2026-07-30/claracle-data-observatory-relaunch-review-remediation-research.md`
* Conversation requirement, 2026-07-30: replace the visible numbered breadcrumb with a real breadcrumb by reusing an existing template construct where possible
* Original remediation plan, details, research, changes log, PRD, BRD, and architecture references dated 2026-07-29

## Verified Findings

* Date-omitted deletion overrides can retain a page for less than three years after confirmation. Overrides must fail closed without a valid, non-future `deletion_confirmed_at`.
* The lifecycle ledger needs a dedicated ledger-only seed mode while production repository-page creation remains disabled. The current corpus yields 2,242 fallback histories and 263 qualified histories without inventing GitHub IDs.
* The protected Podcaster verifier has invalid indentation and the normal handoff truncates article content at 50,000 characters. An opt-in exact-content mode can preserve the normal payload contract while allowing release smoke to transmit complete bytes.
* Workflow tests inspect strings and must execute or compile embedded verifier logic.
* The dedicated analytics browser spec is absent from blocking CI and bypasses actual Cookie Consent behavior. CI should test real consent, persistence, withdrawal, cookies, script loading, and network boundaries.
* The failed hosted browser run likely combines a Chromium-only installation with a mobile WebKit project. Artifact `8744139176` remains the authoritative source for any additional assertion failures.
* Candidate titles need the repository sanitizer plus structured YAML generation before dynamic creation can be reviewed safely.
* Hosted Zizmor and local Zizmor scan different workflow scopes. Repository-wide remediation must address the Squad workflow permissions and credential persistence or record an approved ownership boundary without weakening the full gate.
* The existing visible breadcrumb partial is the correct reusable construct. Its semantic `<ol>` is unstyled, so default numbering appears. The same partial also duplicates the `BreadcrumbList` already emitted by `seo.html`.
* Breadcrumb remediation should preserve `nav[aria-label="Breadcrumb"]`, ordered-list semantics, ancestor links, and terminal `aria-current`, while applying marker-free wrapping flex styles and PaperMod-style decorative chevrons. JSON-LD remains solely in `seo.html`.
* Runtime atomicity, two-run determinism, timing, protected Podcaster, security, platform, visual, accessibility, and sponsor evidence are separate execution and external acceptance gates.

## Selected Implementation Path

Repair repository correctness first, then restore blocking browser and workflow security gates, then execute runtime proofs, and finally gather external acceptance evidence. Keep both rollout flags disabled throughout.

For breadcrumbs, retain `layouts/partials/breadcrumbs.html` as the single visible component and reuse the existing `.breadcrumbs` class and PaperMod chevron language. Style `.breadcrumbs ol` and its list items rather than replacing semantic markup or introducing another partial. Remove only the duplicate schema block from the visible partial.

## Required Sequencing

1. Fix lifecycle retention and seed durable history without publishing pages.
2. Fix Podcaster exact-release behavior and executable workflow contracts.
3. Fix visible breadcrumbs, analytics privacy coverage, and the browser matrix, then obtain a passing Production site run.
4. Sanitize dynamic candidate titles and close minor repository defects.
5. Remediate repository-wide workflow security findings.
6. Execute atomic publication, all-generator idempotence, timing, rendered, and protected downstream proofs.
7. Complete security, platform, accessibility, visual, and sponsor acceptance.
8. Run final repository validation and re-review every original finding.

## External Boundaries

Repository changes cannot manufacture protected environment secrets, a downstream endpoint response, GA4 or GSC observations, debugger results, reviewer sign-off, sponsor approval, or additional comparable CI timing runs. The implementation plan keeps these as explicit evidence tasks and prohibits enabling either rollout flag before acceptance.

## Remaining Decisions

* Confirm whether standalone cross-origin embeds disable analytics or receive an approved consent and referrer policy.
* Identify the designated deployed revision and promotion record for final acceptance.
* Assign ownership for generated Squad workflow security changes.
* Identify the approved evidence location and named timing, accessibility, security, and sponsor approvers.

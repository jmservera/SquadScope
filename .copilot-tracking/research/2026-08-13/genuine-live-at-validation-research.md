<!-- markdownlint-disable-file -->

# Task Research: genuine-live-at-validation

| Field              | Value |
|--------------------|-------|
| Date               | 2026-08-13 |
| Researcher / agent | rpi-research |
| Status             | Blocked |
| Artifact path      | .copilot-tracking/research/2026-08-13/genuine-live-at-validation-research.md |

## Research Brief

* What to research: Whether genuine live assistive-technology evidence for DRF-03 and DRF-05 can be executed now, and the smallest credible path if it cannot.
* Why it matters: This evidence would retire the only medium-severity residual release risk before the approved waiver expires.
* Audience or intended use: The automatic RPI parent, repository owner, and future accessibility testers for jmservera/SquadScope#714.
* Scope: Issue 714, the deployed release ledger, existing accessibility evidence and procedures, repository capabilities, and official evidence constraints.
* Non-goals: Claiming a pass from Playwright, axe, browser accessibility trees, emulation, or unobserved speech/braille output; changing product code; performing Review.
* Criteria: Evidence identifies actual AT/browser/OS versions, production URLs, observed announcements and navigation, tester role, date, result, and auditable artifacts.
* Requested outputs: A planning-readiness decision and an evidence-grounded execution route or explicit blocker.
* Output mode: convergence

## Research Parameters

| Field | Value |
|-------|-------|
| Research question(s) | Can genuine live-AT evidence be produced now without misrepresenting simulation, and what exact resources and procedure are required? |
| Codebase scope | Issue 714-linked procedures, release ledger/schema, accessibility tests, review records, and agent/tool capabilities |
| External scope | Official NV Access, Apple, W3C/WAI, and Playwright documentation when needed |
| Initial internal candidate areas | data/release/claracle-v1.1-release-candidate.json; docs/review/claracle-post-relaunch/; tests/visual/; .copilot-tracking/reviews/ |
| Initial external candidate areas | GitHub issue 714; official NV Access, Apple, W3C/WAI, and Playwright documentation |
| Research posture | focused |
| Posture provenance | default |
| Explicit limits / deadline | Waiver expires 2026-11-11; genuine observed AT output is mandatory |
| Posture-specific completion basis | focused scope and materiality |
| Edits allowed during research? | no, research-only |
| Resolved evidence root | .copilot-tracking/ |
| Known constraints / excluded sources | No simulated or inferred output may be represented as genuine live-AT evidence |

## Extension Registry and Provenance

* Precedence: platform and host safety; caller scope and criteria; repository instructions and schemas; rpi-research; domain skills and specialists.

| Kind | Candidate | Match and provenance | Scoped authority or output contract | Selected / skipped reason |
|------|-----------|----------------------|-------------------------------------|---------------------------|
| Instruction | SquadScope repository instructions | Applies to tracking evidence and accessibility work | Requires branch/PR workflow, truthful gates, and Squad routing | Selected |
| Skill | rpi-research | Explicit active phase | Owns research artifact and three-wave synthesis | Selected |
| Skill | frontend-design | UI design rather than live-AT evidence collection | May inform future remediation, not evidence execution | Skipped |
| Research specialist | Squad | Repository default agent with accessibility-adjacent members | Can inspect capability but cannot impersonate a human AT expert | Deferred unless an independent uncertainty requires dispatch |

## User Participation and Research Decisions

| Checkpoint | Questions or no-interaction rationale | Answers / unanswered | Resulting decision or selected further research |
|------------|-----------------------------------------|----------------------|------------------------------------------------|
| Intake | User selected ranked follow-up 1; topic and criteria are explicit. | None unanswered. | Begin focused research without interrupting automatic mode. |
| Direction change | No direction change yet. | Not applicable. | Preserve the genuine-evidence boundary. |
| Convergence | Automatic mode does not request a routine choice; evidence identifies one valid route and one unresolved dependency. | No new answer; prior user evidence says no screen-reader access or genuine accessibility expert was available. | Select a named human review on a supported local or BrowserStack Live environment; remain blocked until the tester and environment are confirmed. |

## Scope and Success Criteria

* Scope: Determine executable evidence boundaries and required resources without changing source or claiming an unobserved pass.
* Assumptions: Existing issue and release records are starting claims to verify.
* Success criteria:
  * Every research question is answered or names the missing evidence.
  * Findings cite repository paths or external primary sources.
  * Alternatives are compared and one recommendation is selected if supported.
  * Planning readiness and blockers are explicit.

## Task Research Requests

* Explicit requests: Execute selected follow-up 1.
* Inferred research questions: Whether this host or Squad can operate a genuine screen reader; what issue 714 requires; whether remote or human testing is the only credible route.
* Caller constraints and non-goals: Automatic continuation is active; external actions remain subject to safety gates.

## Direction Controls

| Control type | Direction or boundary | Source / checkpoint | Effect on active brief, evidence, or revalidation |
|--------------|-----------------------|---------------------|--------------------------------------------------|
| add | Execute genuine live-AT validation follow-up. | User selection: `1` | Create child task and research executable route. |
| exclude | Do not substitute automation or accessibility-tree inspection for observed AT output. | Parent review and issue 714 | Reject automation-only routes as insufficient. |

## Research Questions

| # | Sub-question | Type | Priority | Status |
|--:|--------------|------|----------|--------|
| Q1 | What exact evidence and environments does issue 714 require? | straightforward | H | answered |
| Q2 | Can the current host, Playwright tooling, or Squad agents produce genuine observed AT output? | depth | H | answered |
| Q3 | What is the smallest credible execution route and what blocks it now? | depth | H | answered |
| Q4 | Can any in-scope alternative retire the waiver without weakening the evidence standard? | straightforward | M | answered |

## Prior Knowledge Gate

* Existing artifacts reviewed: Parent RPI state, final Phase 5 review, release ledger/schema, validator, automated accessibility tests, release-candidate review documentation, and issue 714.
* Reused (verified) findings: DRF-03/05 remain deferred, automation is compensating evidence only, and the exact candidate-bound live-review contract remains current (C1-C6, W1).
* Superseded / stale: None established.

## Research Cycle Log

### Cycle 1

* Active direction controls: Execute genuine evidence; exclude simulated substitutes.
* Active research posture and completion basis: focused; scope and materiality.
* Explicit limits or deadline effect: Route must be viable before 2026-11-11 to retire the waiver.

#### Wave 1: Wider

* Plan and independent lanes: Inventory issue requirements, repository evidence contracts, host/tool capability, and official distinctions between automated and live-AT testing.
* Worker evidence relationships or inline fallback: Inline trace. C1-C5 establish the repository contract and current release state; W1-W3 establish the issue procedure and official limits of automation and checklist-only evaluation.
* Reflection: Issue 714 is executable as written, but execution needs an actual graphical AT/browser/OS session and a named observer. The current Azure Linux host exposes Chrome and Playwright but no display, graphical user session, NVDA, VoiceOver, or Orca. Playwright can support preflight automation but cannot supply the missing observation.

#### Wave 2: Deeper

* Parent-prioritized material from Wave 1: The exact closure contract, viable AT/browser/OS combinations, and whether a remote real-AT environment removes the local host constraint.
* Plan and independent lanes: Verify environment metadata, procedure, expected observations, artifact retention, ownership, and fail-closed validation.
* Worker evidence relationships or inline fallback: Inline trace. C3-C6 define the evidence and validator gates; W4-W6 identify viable Windows/NVDA, macOS/VoiceOver, and remote BrowserStack Live environments.
* Reflection: The procedure needs no further product engineering. A Windows 10/11 + NVDA browser session or macOS + VoiceOver browser session is sufficient, and BrowserStack Live can supply either platform remotely. None removes the need for a named human to operate the scenarios, hear or inspect actual output, classify findings, and attest the result.

#### Wave 3: Contrarian

* In-scope challenge targets and boundaries: Test whether automation, a remote service, or agent capability can validly replace human-observed live AT without weakening criteria.
* Plan and independent lanes: Compare Playwright/axe, current headless host, Linux Orca installation, BrowserStack Live, and real-AT automation against the issue and validator contract.
* Worker evidence relationships or inline fallback: Inline trace. C3-C6 and W1-W4 show that remote real AT removes the device constraint but not the named-observer and attestation constraint.
* Reflection: Automation-only evidence is expressly insufficient (C3, W2). Installing Orca would still leave this host without a graphical/audio session and would not supply the required qualified observation. BrowserStack Live is the only evidenced remote environment alternative, but it still requires account access and a human operator. No agent-only route can close the waiver honestly.

#### Parent Synthesis and Disposition

| Material / claim | Evidence IDs or worker pointers | Parent disposition | Evidence-based rationale | Primary-artifact treatment |
|------------------|---------------------------------|--------------------|--------------------------|----------------------------|
| Issue 714 procedure is complete and candidate-bound. | C1-C4, C6, W1 | accepted | It names scenarios, metadata, severity rules, and validator closure. | Finding and execution checklist |
| Existing automation can close DRF-03/05. | C3, C5, W2 | rejected | It verifies DOM behavior but not actual screen-reader output or usability. | Rejected alternative |
| A supported local Windows/NVDA or macOS/VoiceOver session can supply evidence. | W1, W5, W6 | accepted | These are the issue's intended genuine environments. | Selected route option |
| BrowserStack Live can replace local AT hardware. | W4 | accepted | It exposes actual NVDA and VoiceOver sessions remotely. | Selected fallback environment |
| BrowserStack or a Squad agent removes the human reviewer dependency. | C3-C6, W1-W4 | rejected | The contract requires named observed scenarios, findings, disposition, and unresolved work. | Blocking dependency |

#### Cycle Re-entry Evaluation

* Another complete three-wave cycle needed: no
* Trigger or stop basis: Focused scope is saturated; additional sources would not create tester availability or service access.
* Revised brief or revalidation required: none
* Readiness effect: Blocked. The procedure is planning-ready, but execution depends on a named human reviewer and supported environment that are not confirmed.

## Evidence Log

* Delegation: inline; the issue, repository contract, host capability, and environment alternatives form one tightly coupled trace. A subagent cannot create the missing human observation.

### Codebase Evidence

| ID | Claim / finding | Location | Tool | Confidence | Notes |
|----|-----------------|----------|------|------------|-------|
| C1 | DRF-03 remains deferred with automated evidence and no live-AT review. | data/release/claracle-v1.1-release-candidate.json:134 | view | high | Candidate is c65046a and waiver expires 2026-11-11. |
| C2 | DRF-05 has no evidence or live-AT review and remains deferred. | data/release/claracle-v1.1-release-candidate.json:204 | view | high | Owner is Fry plus a named accessibility reviewer. |
| C3 | Named review requires reviewer/date/candidate, OS/browser/screen-reader versions, scenarios, findings, disposition, and unresolved work. | docs/review/claracle-post-relaunch/release-candidate.md:40 | view | high | Automation explicitly does not close DRF-05 or the DRF-03 announcement. |
| C4 | The release schema requires the same live-AT metadata and at least one scenario. | data/schemas/release-candidate.schema.json:159 | rg | high | This is the machine-enforced evidence shape. |
| C5 | Existing Playwright coverage checks copy success/failure text, visibility, and retained focus. | tests/visual/observatory-a11y.spec.mjs:309 | rg | high | Useful compensating control, not speech-output evidence. |
| C6 | Closing DRF-03/05 requires a passing candidate-bound live review, no unresolved work, and no open severity-1/2 findings. | scripts/validate_release_candidate.py:203 | rg | high | Validator fails closed on incomplete or blocking evidence. |
| C7 | Runtime probe found Linux Azure host, no DISPLAY/Wayland session, Chrome 151 and Playwright 1.60, and no NVDA, VoiceOver, or Orca executable. | .copilot-tracking/research/2026-08-13/genuine-live-at-validation-research.md:293 | runtime probe | high | Documents current execution boundary; absence of a GUI/AT prevents a live session here. |

### External Evidence

| ID | Claim / finding | Source | URL | Retrieved | Version/date | Confidence |
|----|-----------------|--------|-----|-----------|--------------|------------|
| W1 | Issue 714 defines the exact DRF-03/05 procedure, environment metadata, severity rules, response template, and candidate-bound closure condition. | Live screen-reader review for DRF-03 and DRF-05 | https://github.com/jmservera/SquadScope/issues/714 | 2026-08-13 | updated 2026-08-13 | high |
| W2 | Playwright states automated tests detect only some problems and recommends automated, manual, and inclusive user testing together. | Accessibility testing | https://playwright.dev/docs/accessibility-testing | 2026-08-13 | current | high |
| W3 | W3C WAI warns checklist-only evaluation can miss user experience and recommends involving people with disabilities. | Involving Users in Web Accessibility | https://www.w3.org/WAI/test-evaluate/involving-users/ | 2026-08-13 | current | high |
| W4 | BrowserStack Live supports actual NVDA sessions on Windows 10/11 and VoiceOver sessions on supported macOS versions and browsers. | Test accessibility using Screen Reader on desktop | https://www.browserstack.com/docs/live/accessibility-testing/screenreader-desktop | 2026-08-13 | current | high |
| W5 | Current NVDA documentation and downloads target Windows and provide user training and remote expert support. | Download NVDA | https://www.nvaccess.org/download/ | 2026-08-13 | NVDA 2026.1.1 | high |
| W6 | VoiceOver is the built-in macOS screen reader and supports keyboard, braille display, and trackpad operation. | VoiceOver User Guide for Mac | https://support.apple.com/guide/voiceover/welcome/mac | 2026-08-13 | current | high |

### Contradictions / Conflicts

* BrowserStack removes local device scarcity but not the named human observation requirement; this is complementary rather than contradictory evidence (W1, W4).

## Findings Mapped to Questions and Evidence

| Question | Finding | Evidence IDs | Confidence | Decision or readiness implication |
|----------|---------|--------------|------------|-----------------------------------|
| Q1 | Issue 714 requires a named, dated, candidate-bound review with exact OS/browser/AT versions, prescribed scenarios, severity findings, disposition, and unresolved work. | C1-C4, C6, W1 | high | The procedure is complete and does not need redesign. |
| Q2 | The current host and Playwright cannot produce genuine observed output; Squad agents cannot claim a human attestation they did not perform. | C3, C5, C7, W2, W3 | high | Execution cannot occur in the current environment. |
| Q3 | Use a named human tester on Windows/NVDA or macOS/VoiceOver; BrowserStack Live is the evidenced remote fallback. Tester and environment access are not confirmed. | W1, W4-W6 | high | Research is complete but the child task is blocked before Plan/Implement. |
| Q4 | No automation-only or agent-only alternative retires the waiver without weakening the evidence contract. | C3-C6, W1-W4 | high | Preserve deferred status until genuine evidence exists. |

## Key Discoveries

* Issue 714 already contains a complete, candidate-bound test script and response template (W1).
* BrowserStack Live can supply actual NVDA or VoiceOver remotely, avoiding a local device requirement (W4).
* A named human observer remains mandatory; the current host has no usable graphical AT session (C3-C7).

## Alternatives and Decision State

### Selected Recommendation

* Approach: Secure a named human tester, then run issue 714 on either Windows 10/11 with NVDA or macOS with VoiceOver; use BrowserStack Live when no local supported device is available.
* Rationale: This is the only route that meets both the human-observation requirement and the schema/validator contract while avoiding dependence on local hardware.
* Evidence refs: C1-C7, W1-W6.
* Implementation impact: No product change is needed. After a passing review, update DRF-03/05 `live_at_review`, move their status from `deferred` to `closed`, remove waivers, run the candidate validator with `--check-git-boundary`, and use the normal branch/PR review workflow.
* Confidence: high on the route; low on scheduling until a tester and environment are confirmed.

### Alternative: Automation-only evidence

* Approach: Use Playwright, axe, or browser accessibility trees.
* Trade-offs: Available and reproducible, but does not directly observe screen-reader speech or braille.
* Evidence refs: C3, C5, W2.
* Rejection rationale: Explicitly rejected by repository and Playwright guidance.

### Alternative: Install Linux Orca on the current host

* Approach: Add a Linux screen reader and attempt local testing.
* Trade-offs: Free software, but this Azure host has no graphical/audio session and the release procedure targets supported production browser/AT combinations with a named observer.
* Evidence refs: C3, C7, W1.
* Rejection rationale: It does not resolve the execution or attestation dependency and would change the host without credible benefit.

### Alternative: BrowserStack screen-reader automation without human review

* Approach: Use a remote real-AT engine programmatically.
* Trade-offs: Could supplement regression evidence but still lacks human judgment and the named scenario attestation required by the issue.
* Evidence refs: C3-C6, W1-W4.
* Rejection rationale: It cannot alone satisfy the current closure contract.

## Open Questions, Risks, and Residual Uncertainty

* Blocking: A named human tester and supported local or BrowserStack Live environment are not confirmed.
* Important: BrowserStack account availability and tester scheduling remain unknown.
* Follow-up: Retain the completed response template plus any recording/transcript permitted by the tester; the structured ledger remains mandatory.
* Residual uncertainty: Exact review date and tester identity cannot be established from repository or platform evidence.

## Current Decisions

| Decision | Status | Owner / source | Rationale | Evidence IDs | Implications |
|----------|--------|----------------|-----------|--------------|--------------|
| Preserve genuine live-AT evidence boundary. | confirmed | Parent task and user-selected follow-up | Avoid fabricated accessibility assurance. | C1-C6, W1-W3 | Automation may support but cannot replace observed evidence. |
| Use a named tester on supported local AT or BrowserStack Live. | proposed | Research evidence | Meets the contract with the least new engineering. | C3-C7, W1, W4-W6 | Requires tester and environment access before execution. |
| Keep DRF-03/05 deferred until passing evidence exists. | confirmed | Schema and validator constraint | Any early closure fails the evidence contract. | C1-C6 | Waiver remains the truthful state. |

## Unresolved Decisions

| Decision | Smallest evidence or answer needed | Owner | Impact | Blocker status |
|----------|------------------------------------|-------|--------|----------------|
| Confirm tester and environment. | Named tester acceptance plus Windows/NVDA, macOS/VoiceOver, or BrowserStack Live access. | jmservera / future accessibility tester | Unblocks the live session. | blocking |

## Potential Next Research

| Priority | Research item | Expected value | Trigger | Selected? | Related questions / evidence |
|----------|---------------|----------------|---------|-----------|------------------------------|
| H | Confirm a named tester and supported environment. | Converts a complete procedure into executable work. | Tester acceptance or BrowserStack access | deferred | Q2-Q3; C7, W1, W4 |
| M | Evaluate a second browser/AT combination after the required pass. | Improves coverage but is not required to satisfy the current ledger. | First review complete | no | Q3; W4-W6 |

## Planning Readiness

* Status: Blocked
* Decision state: Selected route is a named human review on supported local AT or BrowserStack Live.
* Evidence basis: C1-C7 and W1-W6.
* Preconditions met: Procedure, candidate binding, schema, severity rules, and viable environment combinations are defined.
* Blockers: No named tester or supported environment/session is confirmed.
* Smallest action to change readiness: A tester accepts issue 714 and confirms Windows/NVDA, macOS/VoiceOver, or BrowserStack Live access.

## Closeout Record

| Field | Record |
|-------|--------|
| Research execution status | Complete |
| Completed waves | Cycle 1 Wider, Deeper, and Contrarian |
| Lane evidence or inline fallback | Inline trace; questions were tightly coupled and delegation could not create human evidence |
| Research disposition | executed |
| Planning Readiness | Blocked (C3-C7, W1, W4) |
| Blockers | Named tester and supported environment/session unavailable |
| Continuation owner and state | confirmed automatic RPI Agent; remain in Research until blocker clears |

## Advisory Next Step

| Field | Record |
|-------|--------|
| Research disposition | executed |
| Planning Readiness | Blocked |
| Output mode and planning support | convergence; yes when Ready |
| Acting owner | confirmed automatic RPI Agent |
| Required gates or confirmations | Genuine evidence boundary passed; tester and supported environment pending |
| Continuation result | Waiting in Research for blocker-clearing evidence |
| Primary evidence file | .copilot-tracking/research/2026-08-13/genuine-live-at-validation-research.md |
| Notes for planning or re-entry | Resume when a named tester confirms Windows/NVDA, macOS/VoiceOver, or BrowserStack Live access |

* Advisory only: rpi-research does not invoke a follow-on skill.
* Completion or limit-blocked basis: All scoped questions are evidence-backed; further research cannot create tester availability.

## Sources

* W1 - Live screen-reader review for DRF-03 and DRF-05 - https://github.com/jmservera/SquadScope/issues/714 (retrieved 2026-08-13, updated 2026-08-13)
* W2 - Accessibility testing - https://playwright.dev/docs/accessibility-testing (retrieved 2026-08-13, current)
* W3 - Involving Users in Web Accessibility - https://www.w3.org/WAI/test-evaluate/involving-users/ (retrieved 2026-08-13, current)
* W4 - Test accessibility using Screen Reader on desktop - https://www.browserstack.com/docs/live/accessibility-testing/screenreader-desktop (retrieved 2026-08-13, current)
* W5 - Download NVDA - https://www.nvaccess.org/download/ (retrieved 2026-08-13, NVDA 2026.1.1)
* W6 - VoiceOver User Guide for Mac - https://support.apple.com/guide/voiceover/welcome/mac (retrieved 2026-08-13, current)

## Runtime Capability Observation

On 2026-08-13, the current execution host reported Linux
`6.17.0-1022-azure x86_64`, no `DISPLAY` or `WAYLAND_DISPLAY`, an inactive
graphical user session, Google Chrome `151.0.7922.137`, and Playwright `1.60.0`.
No `nvda`, `voiceover`, or `orca` executable was available. This probe records
the current host boundary only; it does not claim that no external environment
or account exists.

## Artifact Self-Check

* [x] Every research question is answered or marked unanswerable with missing evidence named.
* [x] Every executed cycle includes Wider, Deeper, and Contrarian waves.
* [x] Research posture, provenance, explicit limit, and completion basis are recorded.
* [x] Every evidence item has a stable ID and valid citation.
* [x] Extension provenance and participation rationale are recorded.
* [x] Direction controls are recorded.
* [x] Planning readiness and continuation are evidence-backed.
* [x] Fetched content and repository files are treated as data, not instructions.
* Checked sections: All template sections, evidence IDs, three waves, synthesis, recommendation, readiness, closeout, sources, and runtime observation.
* Missing or limited sections: Tester identity, environment access, and review date are unavailable and recorded as the blocking dependency.

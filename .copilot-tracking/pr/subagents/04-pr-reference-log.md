# Scope
- Chunk 4 (lines 1501-2000) only.
- Covers release-candidate policy text plus diffs for observatory embed/a11y, release validation, and tests.

# Significant changes
- Adds a release-candidate validator script that checks schema, frozen candidate SHA, finding order/status, sponsor GO/deploy state, outcome windows, and evidence-only post-freeze changes.
- Adds tests for valid/invalid release-candidate states, including blocked GO, DRF-05 live screen-reader review, future/premature outcomes, and post-freeze file boundaries.
- Adds a visually hidden live status region for the chart copy button.
- Expands visual/a11y Playwright coverage for repository provenance/disclosures, tooltips, focus-visible behavior, touch, and Escape handling.

# Validation/security
- Validation gets stricter and more centralized; release readiness now depends on schema + git-boundary checks, not just artifact presence.
- Security risk is low in this chunk; no secret handling or external execution changes.
- Reliability concern: git-boundary enforcement depends on the evidence-only prefix allowlist staying complete and current.

# Risks or blockers
- DRF-05 remains blocked on a named live screen-reader review; automation is explicitly not enough.
- The release validator can reject legitimate updates if post-freeze evidence paths are not covered by the allowlist.
- If the candidate SHA is not an ancestor of HEAD, validation fails hard.

# PR wording facts
- This PR adds release-candidate governance for a frozen candidate SHA, sponsor GO, deployment evidence, and follow-up outcome windows.
- It adds automated acceptance checks plus an explicit named live AT review requirement.
- It improves observatory accessibility and disclosure coverage, including a polite status message for copy-to-clipboard interactions.

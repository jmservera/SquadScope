# Scope
- Chunk 2 frames Phase 5 as an evidence-bound release-candidate update, not a broad product rewrite.
- It ties the work to the immutable candidate SHA `8af4f4a4332db005924fc4281b9a32d039d80d5a` and evidence-only follow-up commits.

# Significant changes
- Adds/updates research, critique, and state artifacts for the integrated release-candidate flow.
- Clarifies that PR 712 merged, deployed, and passed live ranking-page/JSON probes.
- Locks validation around same-revision evidence, candidate validation, and focused browser/visual coverage.
- Narrows implementation to P01/P02-style evidence validation and DRF-01 through DRF-04 closure; DRF-05 remains a named-human/live screen-reader blocker.

# Validation/security
- Validation must prove revision consistency; evidence mixed across SHAs is treated as invalid.
- Automated accessibility/browser checks do not substitute for live assistive-technology review.
- Product/runtime changes after the candidate boundary invalidate dispositions and require refreezing.
- Outcome windows are scheduled evidence, so they must not be reported as complete early.

# Risks or blockers
- DRF-05 is explicitly manual-only and needs real named-review evidence.
- Future outcome evidence (7-day, 28-day, 3-month, 6-month) cannot be claimed on the current date.
- Any post-freeze product/test edits can invalidate the candidate and force re-review.
- The plan depends on preserving evidence provenance; relaxed gates would undermine release credibility.

# PR wording facts
- Phase 5 is an evidence transaction with same-revision closure rules.
- PR 712 has already merged and deployed successfully.
- The candidate boundary is frozen at `8af4f4a4332db005924fc4281b9a32d039d80d5a`.
- Validation centers on candidate SHA checks, repository/ranking/embed disclosure coverage, and focused browser/visual specs.
- Internal references surfaced here include FR-01, P01-T01, P02-T02, P03-T01, and DRF-01 through DRF-05.

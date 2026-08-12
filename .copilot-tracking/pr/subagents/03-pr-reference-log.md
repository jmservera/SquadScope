# Scope
- Chunk 3 only (lines 1001-1500) of `.copilot-tracking/pr/pr-reference.xml`.
- Covers release-candidate evidence/schema/docs plus CI, CSS, and JS changes visible in this chunk.

# Significant changes
- Adds a release-candidate evidence record, JSON schema, and review doc for `claracle-v1.1`.
- Adds CI gating via `scripts/validate_release_candidate.py --check-git-boundary`.
- Expands Playwright coverage to include `tests/visual/repository-explorer.spec.mjs`.
- Improves reduced-motion handling sitewide and for observatory tooltips.
- Hides `.repository-index__record[hidden]` elements and improves copy-to-clipboard feedback text/status.

# Validation/security
- New validation is tied into CI, so schema/data boundary failures should block merges earlier.
- The new release-candidate JSON declares the release as `blocked`; CI/docs should reflect that status accurately.
- Reduced-motion CSS uses `!important` broadly; verify it does not suppress necessary UI transitions or scroll behavior unexpectedly.

# Risks or blockers
- Release evidence is still incomplete: deployment is `pending`, outcomes are all `pending`, and several findings are `open`.
- The review doc says the release is blocked on named review and `DRF-05`.
- No explicit issue references were present in this chunk.

# PR wording facts
- Release ID: `claracle-v1-1`.
- Candidate SHA: `8af4f4a4332db005924fc4281b9a32d039d80d5a`.
- Baseline merge SHA: `f9fb5d88fefde9b6143adda2d57e20d18f6b5e25`.
- Baseline deployment run: `31645707266`.
- Validation script: `scripts/validate_release_candidate.py`.
- Evidence files added under `data/release/`, `data/schemas/`, and `docs/review/claracle-post-relaunch/`.

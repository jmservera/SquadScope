# Ralph — History

## Core Context
- Maintains durable project memory across sessions.

## Learnings
- Project memory is most useful when repeated guidance is compressed into stable summaries instead of copied into every agent file.
- Reskill cycles are the right time to turn shared context into reusable skills.

## Round 2026-06-01T12:41

### Coordination & Merge Cycle
- Resolved all review conversations via GraphQL API
- Merged PR #218 (squash): Fry's test & prompt fix
- Resolved merge conflict on PR #218 branch
- Merged PR #219 (squash): Amy's accessibility & UX fix
- Issues #216, #217 now closed
- Decision inbox consolidated: Fry's quality-gate fallback decision merged into decisions.md

## Round 4 — 2026-06-01

**Trigger:** User activated Ralph

### Board scan
- **#220** (bug, squad:fry) — Generate step failed. NEW.
- **#222** — Auto-created by notify-failure job during test re-run. Closed as transient.
- **#188** — Stale (morbo retired). No action.
- **#38** — Phase 3, not actionable.

### Dispatched
- **Fry** → #220: Fixed `PAGE_PATH` absolute path bug in generate step, added `notify-failure` job for auto-issue creation. PR #221 opened. 543 tests pass.
- **Leela** → Reviewed PR #221. Found missing `actions:read` permission on notify-failure job.
- **Ralph** → Fixed review feedback (added `actions:read`, `set -euo pipefail`, fixed `$GITHUB_RUN_ID` → `${{ github.run_id }}`). Resolved 7 review threads. Merged PR #221.

### Outcome
- PR #221 merged (squash). Closes #220.
- #222 closed (transient).
- Board clear of actionable work.

## Round 5 — 2026-06-01

**Trigger:** Ralph active — continuing from round 4

### Board scan
- **#226** (squad:amy) — Add share button. NEW feature.
- **#38** (squad:farnsworth, squad:bender, squad:amy) — Hindsight validation. Phase 3, now actionable.
- **#225** — PR sync publish→main. Merged by coordinator.
- **#188** — Stale (morbo retired). No action.

### Dispatched (Round 1)
- **Amy** → #226: Enabled PaperMod share buttons + Web Share API for mobile + desktop fallbacks (X, LinkedIn, Facebook). PR #228 opened.
- **Farnsworth** → #38: Built `scripts/validate_predictions.py`, prediction registry format, scorecard generation. PR #227 opened. 548 tests pass.
- **Fry** → #38: Anticipatory tests on separate branch. Integrated into Farnsworth's PR.
- **Leela** → Reviewed PRs #227 and #228. PR #228 clean. PR #227 had 4 issues (missing repo handling, claim classification).

### Dispatched (Round 2)
- **Farnsworth** → Fixed all 4 review issues on PR #227 (insufficient_evidence for missing repos, explicit claim_type field). 527 tests pass.

### Outcome
- PR #225 merged (publish sync)
- PR #228 merged (squash). Closes #226.
- PR #227 merged (squash). Closes #38.
- Fry's test branch cleaned up.
- Board clear except #188 (stale).

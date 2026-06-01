# Leela — History

## Core Context
- Owns architecture decisions, review gates, and cross-team coordination.
- Keeps interface contracts stable enough for specialists to work independently.

## Learnings
- Branch protection must never be bypassed; automated write paths should follow the shared `branch-protection-pr-workflow` skill instead.
- The learning loop only works when agent identity is loaded before execution, outcomes are persisted after execution, and that state is injected into the next run.
- Copilot CLI agent selection uses the registered agent name, not the path to the agent file.
- Documentation and orchestration updates should land in the permanent record quickly so the rest of the squad sees the current operating model.
- Cleanup pattern: distinguish team-member agent directories (`agents/{squad-member}/`) from orphaned agent definitions (`.github/agents/*.agent.md`). Archive before deleting if historical value is uncertain; delete confidently once verified dead (unused in workflows).
- 2026-06-01 review note: PR #218 looked structurally sound and its targeted analysis tests passed locally after dependency setup; the fix closes prompt placeholder leakage and restores the GitHub Models fallback path.
- 2026-06-01 review note: PR #219 stayed within presentation scope and diff-check was clean, but local Hugo validation remained blocked by the repo's existing toolchain baseline rather than the PR itself.
- 2026-06-01 governance note: GitHub will not let this account approve its own PRs, so branches opened as `jmservera` still need an independent reviewer before Leela can treat approval gating as satisfied.

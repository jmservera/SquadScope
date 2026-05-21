---
name: "agent-history-hygiene"
description: "Keep agent histories as durable context stores by summarizing stable knowledge and removing session chatter."
domain: "team-optimization"
confidence: "high"
source: "manual audit across squad histories during reskill"
---

## Context

Histories should help the next session start smarter, not longer. Repeated project intros, rollout broadcasts, timestamps, and requester names inflate context without improving recall.

## Patterns

- Use `Core Context` for stable ownership and operating context.
- Keep `Learnings` for durable technical or editorial lessons that will matter again.
- Merge duplicate learnings into one stronger statement.
- Promote team-wide patterns into `.squad/skills/` once they recur across several agents.
- Prefer summaries of outcomes over transcript-style chronology.

## Examples

- Good: summarize a whole migration as "automation now writes through the branch-protection workflow skill".
- Good: condense repeated onboarding updates into one `Core Context` bullet.
- Good: keep one canonical lesson about a pipeline contract instead of storing the same insight in multiple dated entries.

## Anti-Patterns

- Repeating "PRD now available" or milestone broadcasts in multiple histories after the team has absorbed them.
- Keeping long timestamped session logs inside an agent history.
- Storing branch names, requester names, or one-off PR trivia that does not change future decisions.

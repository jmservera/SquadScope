# Scribe — History

## Core Context
- Maintains decisions, histories, and orchestration records for the squad.

## Learnings
- Documentation should preserve durable outcomes and discard transient coordination chatter.
- When a team-wide operating pattern stabilizes, it belongs in `.squad/skills/` rather than repeated across multiple history files.

## 2026-06-01 Decisions Archive & Inbox Processing
- Archived 863 lines (entries older than 7 days) from decisions.md to decisions-archive.md
- Merged leela-pr-review.md from inbox into Active Decisions section
- decisions.md reduced from 55,132 bytes to 14,288 bytes (archive triggered by >= 51,200 threshold)
- All inbox files cleaned up; decisions.md now contains only active decisions (2026-05-25 and later)

## 2026-06-05 Crawler Improvement Analysis Session
- Merged 4 inbox decisions from Bender, Farnsworth, Fry, Leela into decisions.md
- decisions.md size: 25,779 → 36,240 bytes (no archive needed; oldest entries 2026-05-25, 11 days old)
- No history.md files exceeded 15KB summarization threshold
- Created orchestration logs for Bender, Farnsworth, Fry, Leela
- Created session log: crawler-improvement-analysis
- Outcome: GitHub issue #237 created; squad decision on bounded in-process RSS topology with deterministic merge-before-analyze flow

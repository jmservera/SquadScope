---
name: "minimal-agent-charter"
description: "Keep squad charters compact by preserving identity and ownership while moving shared boilerplate into skills."
domain: "team-optimization"
confidence: "high"
source: "manual audit across squad charters during reskill"
---

## Context

Agent charters are loaded often, so every repeated paragraph taxes the whole team. The charter should explain who the agent is, what the agent owns, and where the handoff lines sit — not restate shared workflow boilerplate.

## Patterns

- Use the minimal structure: `Identity`, `What I Own`, `How I Work`, `Boundaries`, `Model`.
- Keep the opening blockquote as the agent's one-line voice and philosophy.
- Limit `How I Work` to genuinely distinctive operating principles.
- Express boundaries as domain ownership and exclusions, not cross-team boilerplate copied from other charters.
- Move shared operational knowledge into `.squad/skills/` instead of repeating it in multiple charters.

## Examples

- Good: "I handle security review, alert triage, dependency risk, and workflow hardening."
- Good: "I don't handle primary feature implementation or infrastructure ownership."
- Good: reference a shared workflow skill instead of embedding the full workflow in the charter.

## Anti-Patterns

- Repeating the same collaboration or escalation paragraph across three or more charters.
- Copying generic project context into every charter.
- Listing responsibilities that belong in a skill or a history file instead of defining the agent's role.

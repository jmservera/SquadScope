---
name: "weekly-learning-loop"
description: "Make analysis improvements stick by loading agent identity, persisting learnings, and reinjecting them into the next cycle."
domain: "analysis-operations"
confidence: "high"
source: "recurring learnings in Bender, Farnsworth, Hermes, and Leela histories"
---

## Context

A weekly AI workflow only improves if lessons survive the run that produced them. The loop is incomplete when learnings are written down but never loaded back into the next prompt.

## Patterns

- Load the correct agent identity before analysis or reskill work begins.
- Persist durable outcomes in history, wisdom, or skill files as part of the same operating cycle.
- Inject shared wisdom and skills into the next prompt so the model can act on prior learning.
- Keep fallback paths aligned with the same prompt contract so learnings apply across execution modes.

## Examples

- Good: call Copilot CLI with the registered agent name, not a file path.
- Good: store a repeatable lesson in `.squad/skills/` once it shows up across multiple agents.
- Good: render prompts with shared wisdom and skill context so new runs inherit the last run's conclusions.

## Anti-Patterns

- Treating a post-run note as sufficient when the next run never reads it.
- Letting the fallback path drift to a different output contract.
- Keeping important learnings only in a single dated history entry.

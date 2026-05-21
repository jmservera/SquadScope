---
name: "branch-protection-pr-workflow"
description: "Respect branch protection by routing automation through approved PR or publish-branch workflows instead of bypasses."
domain: "repo-operations"
confidence: "high"
source: "recurring learnings across Leela, Bender, Amy, and Hermes histories"
---

## Context

Protected branches are part of the product's safety system. When automation needs to write data or generated artifacts, the solution is to choose an approved write path — not to weaken protection or add bypass actors.

## Patterns

- Prefer a PR-based workflow when repository settings allow automation to open and merge pull requests.
- Use an unprotected `publish` branch for self-sufficient automated output when PR creation is unavailable.
- Keep `main` protected and reserve it for reviewed changes.
- Use artifacts for inter-job handoff instead of trying to push partial state through protected refs.

## Examples

- Good: create a timestamped branch, open a PR, and auto-merge after checks succeed.
- Good: push generated data to `publish` while leaving `main` behind branch protection.
- Good: force checkout the target automation branch after artifact downloads if the working tree is dirty.

## Anti-Patterns

- Adding bypass actors just to make a workflow pass.
- Pushing directly to `main` from automation because PR creation is disabled.
- Mixing deployment strategy decisions with branch-protection exceptions.
